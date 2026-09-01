"""
Core RAG pipeline.
- Chunk tài liệu (PDF/txt)
- Embed bằng sentence-transformers (chạy local, miễn phí, không cần API key)
- Lưu / truy vấn vector store bằng ChromaDB (persist ra disk)
- Sinh câu trả lời bằng LLM (OpenAI) dựa trên context truy xuất được
"""

import os
import re
import uuid
from typing import List, Dict

import chromadb
import numpy as np
from chromadb.utils import embedding_functions
from pypdf import PdfReader

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- Khởi tạo Chroma client (persist local) ---
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_embedding_fn,
)


# ---------- 1. Đọc & chunk tài liệu ----------

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text(extraction_mode="layout") or "")
    return "\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Fixed-size chunking với overlap. Đơn giản, dễ giải thích trong báo cáo.
    (Có thể mở rộng thêm semantic chunking sau để so sánh 2 chiến lược.)
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
    return chunks


def _split_sentences(text: str) -> List[str]:
    """Tách câu bằng regex đơn giản (đủ dùng để so sánh 2 chiến lược chunking,
    không cần thư viện NLP nặng)."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def semantic_chunk_text(
    text: str,
    similarity_threshold: float = 0.6,
    max_chunk_sentences: int = 8,
    min_chunk_sentences: int = 2,
) -> List[str]:
    """
    Semantic chunking: gộp các câu liên tiếp có embedding tương đồng cao (cosine
    similarity) vào cùng 1 chunk, mở chunk mới khi độ tương đồng giữa 2 câu liền kề
    tụt dưới ngưỡng hoặc chunk đã đủ dài. Dùng để so sánh với chunk_text()
    (fixed-size) trong phần đánh giá của báo cáo.
    """
    sentences = _split_sentences(text)
    if len(sentences) <= 1:
        return sentences

    embeddings = np.array(_embedding_fn(sentences))
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-8
    normalized = embeddings / norms

    def flush(buf: List[str]):
        if len(buf) < min_chunk_sentences and chunks:
            chunks[-1] = chunks[-1] + " " + " ".join(buf)
        else:
            chunks.append(" ".join(buf))

    chunks: List[str] = []
    current = [sentences[0]]
    for i in range(1, len(sentences)):
        sim = float(np.dot(normalized[i], normalized[i - 1]))
        if sim < similarity_threshold or len(current) >= max_chunk_sentences:
            flush(current)
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    flush(current)
    return chunks


# ---------- 2. Lưu vào vector store ----------

def index_chunks(document_id: str, filename: str, chunks: List[str], collection=None) -> int:
    """Embed + lưu 1 danh sách chunk đã cắt sẵn vào 1 collection (mặc định là
    collection chính của app; eval script truyền collection riêng để không đụng
    dữ liệu thật)."""
    if not chunks:
        return 0

    coll = collection if collection is not None else _collection
    ids = [f"{document_id}-{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    coll.add(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def index_document(document_id: str, file_path: str, filename: str) -> int:
    """
    Đọc PDF -> chunk (fixed-size) -> embed -> lưu vào Chroma.
    Trả về số lượng chunk đã lưu.
    """
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    return index_chunks(document_id, filename, chunks)


# ---------- 3. Truy xuất (retrieve) ----------

def retrieve_context(query: str, top_k: int = 4, collection=None) -> List[Dict]:
    coll = collection if collection is not None else _collection
    results = coll.query(query_texts=[query], n_results=top_k)

    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        hits.append({
            "text": doc,
            "filename": meta.get("filename"),
            "chunk_index": meta.get("chunk_index"),
            "score": dist,
        })
    return hits


# ---------- 4. Sinh câu trả lời (generation) ----------

def build_prompt(query: str, context_chunks: List[Dict]) -> str:
    context_str = "\n\n---\n\n".join(
        f"[Nguồn: {c['filename']} - đoạn {c['chunk_index']}]\n{c['text']}"
        for c in context_chunks
    )
    return f"""Bạn là trợ lý AI trả lời câu hỏi dựa trên tài liệu được cung cấp.
Chỉ trả lời dựa trên ngữ cảnh bên dưới. Nếu không tìm thấy thông tin liên quan, hãy nói rõ là không có đủ thông tin.
Luôn trích dẫn nguồn (tên file + số đoạn) cho mỗi ý trả lời.

Ngữ cảnh:
{context_str}

Câu hỏi: {query}

Trả lời:"""


def generate_answer(query: str, context_chunks: List[Dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = build_prompt(query, context_chunks)

    if not api_key:
        # Fallback khi chưa cấu hình LLM API key - vẫn demo được phần retrieval
        preview = "\n\n".join(f"- ({c['filename']} #{c['chunk_index']}) {c['text'][:200]}..." for c in context_chunks)
        return (
            "[Chưa cấu hình OPENAI_API_KEY - chỉ hiển thị context truy xuất được]\n\n"
            f"{preview}"
        )

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


def new_document_id() -> str:
    return str(uuid.uuid4())


def delete_document(document_id: str) -> None:
    _collection.delete(where={"document_id": document_id})


def generate_answer_stream(query: str, context_chunks: List[Dict]):
    """
    Giống generate_answer(), nhưng yield từng mẩu chữ thay vì trả 1 cục.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = build_prompt(query, context_chunks)

    if not api_key:
        yield "[Chưa cấu hình OPENAI_API_KEY - không thể streaming]"
        return

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    stream = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta