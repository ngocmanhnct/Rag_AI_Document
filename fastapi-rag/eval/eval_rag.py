"""
Đánh giá chất lượng RAG: gửi một bộ câu hỏi mẫu tới FastAPI service đang chạy,
kiểm tra câu trả lời có chứa từ khóa mong đợi không, và báo cáo retrieval score
(cosine distance - càng thấp càng tốt) cho từng câu hỏi.

Cách dùng:
    1. Chạy server (trong thư mục fastapi-rag):
           uvicorn app.main:app --reload
    2. Upload tài liệu qua POST /documents/upload (Swagger UI http://localhost:8000/docs
       hoặc curl -F "file=@ten_file.pdf" http://localhost:8000/documents/upload)
    3. Sửa eval/eval_questions.json cho khớp nội dung tài liệu vừa upload
    4. Chạy:
           python eval/eval_rag.py
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

import httpx

DEFAULT_QUESTIONS_FILE = Path(__file__).parent / "eval_questions.json"


def load_questions(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_eval(base_url: str, questions_file: Path, top_k: int):
    questions = load_questions(questions_file)
    if not questions:
        print(f"Không có câu hỏi nào trong {questions_file}")
        return []

    results = []
    with httpx.Client(timeout=60) as client:
        for case in questions:
            query = case["query"]
            expected_keywords = [k.lower() for k in case.get("expected_keywords", [])]

            resp = client.post(f"{base_url}/chat", json={"query": query, "top_k": top_k})
            resp.raise_for_status()
            data = resp.json()

            answer = data.get("answer", "")
            sources = data.get("sources", [])
            scores = [s["score"] for s in sources if s.get("score") is not None]

            answer_lower = answer.lower()
            matched_keywords = [k for k in expected_keywords if k in answer_lower]
            keyword_hit_rate = (
                len(matched_keywords) / len(expected_keywords) if expected_keywords else None
            )

            results.append({
                "query": query,
                "answer": answer,
                "num_sources": len(sources),
                "avg_retrieval_score": statistics.mean(scores) if scores else None,
                "expected_keywords": expected_keywords,
                "matched_keywords": matched_keywords,
                "keyword_hit_rate": keyword_hit_rate,
            })

    print_report(results)
    return results


def print_report(results):
    print("\n" + "=" * 80)
    print(f"{'Query':<40} {'Sources':>8} {'AvgScore':>10} {'KeywordHit':>12}")
    print("-" * 80)
    for r in results:
        avg_score = f"{r['avg_retrieval_score']:.4f}" if r["avg_retrieval_score"] is not None else "N/A"
        hit_rate = f"{r['keyword_hit_rate'] * 100:.0f}%" if r["keyword_hit_rate"] is not None else "N/A"
        print(f"{r['query'][:38]:<40} {r['num_sources']:>8} {avg_score:>10} {hit_rate:>12}")
    print("=" * 80)

    rates = [r["keyword_hit_rate"] for r in results if r["keyword_hit_rate"] is not None]
    scores = [r["avg_retrieval_score"] for r in results if r["avg_retrieval_score"] is not None]
    if rates:
        print(f"Trung bình keyword-hit-rate: {statistics.mean(rates) * 100:.1f}%")
    if scores:
        print(f"Trung bình retrieval score (cosine distance, càng thấp càng tốt): {statistics.mean(scores):.4f}")
    zero_source = sum(1 for r in results if r["num_sources"] == 0)
    if zero_source:
        print(f"CẢNH BÁO: {zero_source}/{len(results)} câu hỏi không tìm thấy nguồn nào (chưa upload tài liệu?).")


def main():
    parser = argparse.ArgumentParser(description="Đánh giá chất lượng RAG qua endpoint /chat")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_FILE)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--output", type=Path, default=None, help="Ghi kết quả chi tiết ra file JSON")
    args = parser.parse_args()

    try:
        results = run_eval(args.base_url, args.questions, args.top_k)
    except httpx.ConnectError:
        print(
            f"Không kết nối được tới {args.base_url}. Bạn đã chạy `uvicorn app.main:app --reload` chưa?",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.output and results:
        args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nĐã ghi kết quả chi tiết vào {args.output}")


if __name__ == "__main__":
    main()
