# Đánh giá chất lượng RAG

Script `eval_rag.py` đo chất lượng retrieval + generation bằng cách gửi một bộ
câu hỏi mẫu tới endpoint `POST /chat` của service đang chạy, rồi báo cáo:

- **avg_retrieval_score**: trung bình cosine distance của các chunk truy xuất
  được (càng thấp càng tốt, đây chính là field `score` trả về trong `/chat`).
- **keyword_hit_rate**: tỉ lệ từ khóa mong đợi (`expected_keywords`) xuất hiện
  trong câu trả lời — proxy đơn giản cho độ chính xác khi chưa có LLM giám khảo.
- Cảnh báo khi một câu hỏi không truy xuất được nguồn nào (thường do chưa
  upload tài liệu, hoặc câu hỏi không liên quan tới tài liệu đã index).

## Chạy

```bash
# 1. Ở thư mục fastapi-rag, chạy server
uvicorn app.main:app --reload

# 2. Upload tài liệu cần đánh giá
curl -F "file=@duong_dan_toi_file.pdf" http://localhost:8000/documents/upload

# 3. Sửa eval_questions.json: viết câu hỏi + từ khóa mong đợi khớp với tài liệu vừa upload

# 4. Chạy eval
python eval/eval_rag.py

# Tuỳ chọn: đổi base URL / top_k, ghi kết quả chi tiết ra file
python eval/eval_rag.py --base-url http://localhost:8000 --top-k 5 --output eval/results.json
```

## Định dạng `eval_questions.json`

```json
[
  {
    "query": "Câu hỏi cần đánh giá",
    "expected_keywords": ["từ khóa 1", "từ khóa 2"]
  }
]
```

Để lại `expected_keywords: []` nếu chỉ muốn xem retrieval score mà chưa có
tiêu chí chấm đúng/sai cho câu trả lời.

## So sánh chiến lược chunking (gợi ý cho phần báo cáo)

Muốn so sánh fixed-size chunking (hiện tại) với một chiến lược khác (VD:
semantic chunking): chạy `eval_rag.py` với cùng bộ câu hỏi trên 2 lần index
khác nhau (đổi `chunk_text()` giữa 2 lần, xoá collection Chroma cũ, index lại,
rồi eval), so sánh `avg_retrieval_score` và `keyword_hit_rate` giữa 2 lần chạy.
