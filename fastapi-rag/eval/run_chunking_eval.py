"""
So sánh 2 chiến lược chunking (fixed-size vs semantic) trên cùng 1 bộ tài liệu mẫu
và 1 bộ câu hỏi kỳ vọng (eval/questions.json).

Cách chạy (từ thư mục fastapi-rag, đã activate venv):
    python -m eval.run_chunking_eval

Dùng collection Chroma tạm thời (in-memory), không đụng tới dữ liệu thật đã index
qua API (chroma_data/). Kết quả in ra console và ghi vào eval/eval_report.md.
"""

import glob
import json
import os
import time

import chromadb

from app.rag_pipeline import (
    _embedding_fn,
    chunk_text,
    semantic_chunk_text,
    index_chunks,
    retrieve_context,
)

SAMPLE_DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "questions.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "eval_report.md")
TOP_K = 3

STRATEGIES = {
    "fixed": lambda text: chunk_text(text, chunk_size=120, overlap=20),
    "semantic": lambda text: semantic_chunk_text(text, similarity_threshold=0.6),
}


def load_sample_docs():
    docs = {}
    for path in sorted(glob.glob(os.path.join(SAMPLE_DOCS_DIR, "*.txt"))):
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            docs[filename] = f.read()
    return docs


def build_collection(client, name, chunk_fn, docs):
    collection = client.create_collection(name=name, embedding_function=_embedding_fn)
    total_chunks = 0
    chunk_lengths = []
    t0 = time.perf_counter()
    for i, (filename, text) in enumerate(docs.items()):
        chunks = chunk_fn(text)
        index_chunks(document_id=f"doc-{i}", filename=filename, chunks=chunks, collection=collection)
        total_chunks += len(chunks)
        chunk_lengths.extend(len(c.split()) for c in chunks)
    index_time = time.perf_counter() - t0
    avg_len = sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0
    return collection, {
        "total_chunks": total_chunks,
        "avg_chunk_words": round(avg_len, 1),
        "index_time_sec": round(index_time, 2),
    }


def evaluate(collection, questions):
    hit_at_1 = 0
    hit_at_k = 0
    correct_scores = []
    rows = []

    for q in questions:
        hits = retrieve_context(q["query"], top_k=TOP_K, collection=collection)
        filenames = [h["filename"] for h in hits]
        is_hit_1 = len(filenames) > 0 and filenames[0] == q["expected_filename"]
        is_hit_k = q["expected_filename"] in filenames

        if is_hit_1:
            hit_at_1 += 1
        if is_hit_k:
            hit_at_k += 1
            idx = filenames.index(q["expected_filename"])
            correct_scores.append(hits[idx]["score"])

        rows.append({
            "query": q["query"],
            "expected": q["expected_filename"],
            "retrieved_top1": filenames[0] if filenames else None,
            "hit@1": is_hit_1,
            f"hit@{TOP_K}": is_hit_k,
        })

    n = len(questions)
    metrics = {
        "hit@1": round(hit_at_1 / n, 2),
        f"hit@{TOP_K}": round(hit_at_k / n, 2),
        "avg_distance_when_hit": round(sum(correct_scores) / len(correct_scores), 4) if correct_scores else None,
    }
    return metrics, rows


def main():
    docs = load_sample_docs()
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    client = chromadb.EphemeralClient()

    report_lines = [
        "# So sánh Fixed-size chunking vs Semantic chunking",
        "",
        f"- Số tài liệu mẫu: {len(docs)}",
        f"- Số câu hỏi eval: {len(questions)}",
        f"- top_k dùng để truy xuất: {TOP_K}",
        "",
    ]

    all_results = {}
    for strategy_name, chunk_fn in STRATEGIES.items():
        collection, index_stats = build_collection(client, f"eval_{strategy_name}", chunk_fn, docs)
        metrics, rows = evaluate(collection, questions)
        all_results[strategy_name] = {"index_stats": index_stats, "metrics": metrics, "rows": rows}

        print(f"\n=== Chiến lược: {strategy_name} ===")
        print("Index stats:", index_stats)
        print("Metrics:", metrics)

        report_lines.append(f"## Chiến lược: `{strategy_name}`")
        report_lines.append("")
        report_lines.append("| Chỉ số | Giá trị |")
        report_lines.append("|---|---|")
        for k, v in {**index_stats, **metrics}.items():
            report_lines.append(f"| {k} | {v} |")
        report_lines.append("")
        report_lines.append("| Câu hỏi | Nguồn kỳ vọng | Top-1 truy xuất | hit@1 | hit@" + str(TOP_K) + " |")
        report_lines.append("|---|---|---|---|---|")
        for r in rows:
            report_lines.append(
                f"| {r['query']} | {r['expected']} | {r['retrieved_top1']} | "
                f"{'✅' if r['hit@1'] else '❌'} | {'✅' if r[f'hit@{TOP_K}'] else '❌'} |"
            )
        report_lines.append("")

    report_lines.append("## Tổng kết")
    report_lines.append("")
    report_lines.append("| Chiến lược | Số chunk | Độ dài chunk TB (từ) | hit@1 | hit@" + str(TOP_K) + " | avg distance khi đúng |")
    report_lines.append("|---|---|---|---|---|---|")
    for strategy_name, res in all_results.items():
        s = res["index_stats"]
        m = res["metrics"]
        report_lines.append(
            f"| {strategy_name} | {s['total_chunks']} | {s['avg_chunk_words']} | "
            f"{m['hit@1']} | {m[f'hit@{TOP_K}']} | {m['avg_distance_when_hit']} |"
        )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\nĐã ghi báo cáo chi tiết vào {REPORT_PATH}")


if __name__ == "__main__":
    main()
