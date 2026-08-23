"""
Core RAG pipeline.
- Chunk tài liệu (PDF/txt)
- Embed bằng sentence-transformers (chạy local, miễn phí, không cần API key)
- Lưu / truy vấn vector store bằng ChromaDB (persist ra disk)
- Sinh câu trả lời bằng LLM (OpenAI) dựa trên context truy xuất được
"""

import os
import uuid
from typing import List, Dict

import chromadb
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
        text_parts.append(page.extract_text() or "")
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


# ---------- 2. Lưu vào vector store ----------

def index_document(document_id: str, file_path: str, filename: str) -> int:
    """
    Đọc PDF -> chunk -> embed -> lưu vào Chroma.
    Trả về số lượng chunk đã lưu.
    """
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    if not chunks:
        return 0

    ids = [f"{document_id}-{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    _collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


# ---------- 3. Truy xuất (retrieve) ----------

def retrieve_context(query: str, top_k: int = 4) -> List[Dict]:
    results = _collection.query(query_texts=[query], n_results=top_k)

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
