import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag_pipeline import index_document, retrieve_context, generate_answer, new_document_id

app = FastAPI(title="RAG Assistant Service")

# Cho phép gọi từ Spring Boot / React trong lúc dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    top_k: int = 4


class ChatResponse(BaseModel):
    answer: str
    sources: list


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hiện chỉ hỗ trợ file PDF")

    document_id = new_document_id()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        num_chunks = index_document(document_id, tmp_path, file.filename)
    finally:
        os.remove(tmp_path)

    if num_chunks == 0:
        raise HTTPException(status_code=422, detail="Không trích xuất được nội dung từ file (có thể là PDF scan ảnh)")

    return {
        "document_id": document_id,
        "filename": file.filename,
        "chunks_indexed": num_chunks,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query rỗng")

    context_chunks = retrieve_context(req.query, top_k=req.top_k)

    if not context_chunks:
        return ChatResponse(
            answer="Chưa có tài liệu nào được index, hoặc không tìm thấy nội dung liên quan.",
            sources=[],
        )

    answer = generate_answer(req.query, context_chunks)

    return ChatResponse(
        answer=answer,
        sources=[
            {"filename": c["filename"], "chunk_index": c["chunk_index"], "score": c["score"]}
            for c in context_chunks
        ],
    )
