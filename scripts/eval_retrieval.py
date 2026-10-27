"""Measure retrieval quality on your own documents.

Usage (from the repo root, with .streamlit/secrets.toml in place and your
PDFs already uploaded through the app):

    python scripts/eval_retrieval.py scripts/eval_questions.csv

eval_questions.csv columns: question,filename,page
  - filename/page = where the answer really is.
  - Leave filename and page empty for a question your documents can NOT
    answer. Those show whether the min_score cutoff rejects junk.

Reports hit@1, hit@5 and MRR, plus the similarity scores of correct vs.
wrong matches, so you can choose DEFAULT_MIN_SCORE in rag_service.py from
data instead of guessing.
"""
import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from services.search_service import SearchService  # noqa: E402

TOP_K = 5


def main(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    search = SearchService()
    answerable = 0
    hits_at_1 = hits_at_k = 0
    reciprocal_ranks = []
    correct_scores, wrong_top_scores, unanswerable_top_scores = [], [], []

    for row in rows:
        question = row["question"].strip()
        filename = (row.get("filename") or "").strip()
        page = (row.get("page") or "").strip()
        results = search.search(question, top_k=TOP_K)
        top_score = results[0]["score"] if results else 0.0

        if not filename:
            unanswerable_top_scores.append(top_score)
            print(f"[no answer] top score {top_score:.3f}  {question}")
            continue

        answerable += 1
        rank = None
        for i, r in enumerate(results, start=1):
            if r["filename"] == filename and str(r["page_number"]) == page:
                rank = i
                correct_scores.append(r["score"])
                break

        if rank is None:
            wrong_top_scores.append(top_score)
        hits_at_1 += rank == 1
        hits_at_k += rank is not None
        reciprocal_ranks.append(1 / rank if rank else 0.0)
        print(f"[rank {rank or '-'}] top score {top_score:.3f}  {question}")

    def describe(name, scores):
        if scores:
            print(f"  {name:<28} n={len(scores):<3} min={min(scores):.3f} "
                  f"median={statistics.median(scores):.3f} max={max(scores):.3f}")

    print()
    if answerable:
        print(f"hit@1 = {hits_at_1 / answerable:.0%}   hit@{TOP_K} = {hits_at_k / answerable:.0%}   "
              f"MRR = {statistics.mean(reciprocal_ranks):.3f}   ({answerable} answerable questions)")
    print("Similarity scores:")
    describe("correct chunk", correct_scores)
    describe("top hit when answer missed", wrong_top_scores)
    describe("top hit, unanswerable", unanswerable_top_scores)
    print("Pick a min_score below most 'correct chunk' scores and above most "
          "'unanswerable' ones. If they overlap, a threshold alone can't separate them.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
