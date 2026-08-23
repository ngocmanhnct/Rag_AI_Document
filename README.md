# Personal Knowledge RAG Assistant

Trợ lý AI hỏi-đáp tài liệu cá nhân — proof-of-concept cho hướng đề tài RAG + nền tảng cho project fullstack portfolio.

## Kiến trúc hiện tại (giai đoạn 1 - đã code xong)

```
┌────────────┐      upload PDF / chat      ┌──────────────────┐
│  (React -  │ ───────────────────────────▶│   FastAPI RAG     │
│  sắp làm)  │◀─────────────────────────── │   Service :8000   │
└────────────┘        answer + sources      └─────────┬─────────┘
                                                        │
                                              ┌─────────▼─────────┐
                                              │  ChromaDB (local  │
                                              │  persistent store)│
                                              └────────────────────┘
```

Giai đoạn sau sẽ thêm Spring Boot đứng giữa React và FastAPI để quản lý auth/user/document metadata (MySQL), gọi sang FastAPI qua REST.

## Đã có gì

- `fastapi-rag/app/rag_pipeline.py`:
  - Trích xuất text từ PDF (`pypdf`)
  - Chunking (fixed-size + overlap, dễ đổi sang semantic chunking sau để so sánh)
  - Embedding bằng `sentence-transformers` (chạy local, **miễn phí, không cần API key**)
  - Lưu/truy vấn vector store bằng **ChromaDB** (persist ra disk, không cần container riêng)
  - Sinh câu trả lời bằng OpenAI API (nếu chưa set `OPENAI_API_KEY` thì fallback hiển thị context thô — vẫn demo được phần retrieval)
- `fastapi-rag/app/main.py`: 2 endpoint chính
  - `POST /documents/upload` — upload PDF, index vào vector store
  - `POST /chat` — hỏi đáp, trả về answer + sources (tên file, số đoạn, score)
- `docker-compose.yml`: chạy FastAPI + MySQL (MySQL chuẩn bị sẵn cho Spring Boot sau)

## Cách chạy thử ngay (không cần Docker)

```bash
cd fastapi-rag
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# (tùy chọn) set API key để có câu trả lời thật từ LLM
export OPENAI_API_KEY=sk-xxxx   # Windows: set OPENAI_API_KEY=sk-xxxx

uvicorn app.main:app --reload
```

Mở http://localhost:8000/docs để test bằng Swagger UI:
1. Gọi `POST /documents/upload`, chọn 1 file PDF (VD: 1 chương giáo trình)
2. Gọi `POST /chat` với `{"query": "nội dung tài liệu nói về gì?"}`

## Hoặc chạy bằng Docker

```bash
cp .env.example .env   # rồi điền OPENAI_API_KEY thật vào
docker compose up --build
```

## Việc tiếp theo (theo đúng roadmap 4 tuần đã bàn)

- [ ] **Tuần 2 (đang làm)**: test thử với tài liệu thật, tinh chỉnh chunk_size/overlap
- [ ] **Tuần 3**: dựng Spring Boot skeleton (auth JWT, entity Document/User, gọi sang FastAPI qua RestTemplate/WebClient), dựng React UI cơ bản (upload + chat box)
- [ ] **Tuần 4**: polish, thêm streaming response, viết README + demo video

## Ghi chú cho phần tiểu luận

- Có thể đưa `chunk_text()` thành điểm so sánh: thử thêm 1 hàm `semantic_chunk_text()` (dùng embedding similarity để cắt đoạn theo ngữ nghĩa) rồi so sánh độ chính xác trả lời giữa 2 cách — đây là phần "đánh giá" hay để đưa vào báo cáo.
- Trường `score` trong response `/chat` chính là cosine distance — dùng để lập luận về độ tin cậy của retrieval trong phần đánh giá hệ thống.
