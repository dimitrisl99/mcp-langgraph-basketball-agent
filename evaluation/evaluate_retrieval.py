import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.rag.retriever import search_playbooks


def load_dataset(dataset_path: Path) -> list[dict]:
    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def source_hit(
    retrieved_results: list[dict],
    expected_sources: list[str],
) -> bool:
    retrieved_sources = [
        result["source"]
        for result in retrieved_results
    ]

    return any(
        expected_source in retrieved_sources
        for expected_source in expected_sources
    )


def reciprocal_rank(
    retrieved_results: list[dict],
    expected_sources: list[str],
) -> float:
    for index, result in enumerate(retrieved_results, start=1):
        if result["source"] in expected_sources:
            return 1 / index

    return 0.0


def text_contains_hit(
    retrieved_results: list[dict],
    expected_text_contains: list[str],
) -> bool:
    if not expected_text_contains:
        return True

    combined_text = " ".join(
        result["text"].lower()
        for result in retrieved_results
    )

    return any(
        expected_text.lower() in combined_text
        for expected_text in expected_text_contains
    )


def evaluate_retrieval(
    dataset: list[dict],
    top_k: int = 5,
) -> dict:
    total_questions = len(dataset)

    source_hits = 0
    text_hits = 0
    reciprocal_ranks = []

    failed_cases = []

    for item in dataset:
        question = item["question"]
        expected_sources = item.get("expected_sources", [])
        expected_text_contains = item.get("expected_text_contains", [])

        retrieved_results = search_playbooks(
            query=question,
            top_k=top_k,
        )

        has_source_hit = source_hit(
            retrieved_results=retrieved_results,
            expected_sources=expected_sources,
        )

        has_text_hit = text_contains_hit(
            retrieved_results=retrieved_results,
            expected_text_contains=expected_text_contains,
        )

        rr = reciprocal_rank(
            retrieved_results=retrieved_results,
            expected_sources=expected_sources,
        )

        if has_source_hit:
            source_hits += 1

        if has_text_hit:
            text_hits += 1

        reciprocal_ranks.append(rr)

        if not has_source_hit or not has_text_hit:
            failed_cases.append(
                {
                    "question": question,
                    "expected_sources": expected_sources,
                    "expected_text_contains": expected_text_contains,
                    "retrieved_sources": [
                        result["source"]
                        for result in retrieved_results
                    ],
                    "top_result_preview": (
                        retrieved_results[0]["text"][:300]
                        if retrieved_results
                        else ""
                    ),
                }
            )

        print("\n========================================")
        print(f"Question: {question}")
        print("----------------------------------------")

        for index, result in enumerate(retrieved_results, start=1):
            print(
                f"{index}. {result['source']} "
                f"| page {result['page']} "
                f"| distance {result['distance']:.4f}"
            )

        print(f"Source Hit: {has_source_hit}")
        print(f"Text Hit: {has_text_hit}")
        print(f"Reciprocal Rank: {rr:.3f}")

    hit_at_k = source_hits / total_questions
    text_hit_at_k = text_hits / total_questions
    mrr = sum(reciprocal_ranks) / total_questions

    return {
        "total_questions": total_questions,
        "top_k": top_k,
        "hit_at_k": round(hit_at_k, 3),
        "text_hit_at_k": round(text_hit_at_k, 3),
        "mrr": round(mrr, 3),
        "failed_cases": failed_cases,
    }


def save_results(results: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    dataset_path = PROJECT_ROOT / "evaluation" / "retrieval_dataset.json"
    output_path = PROJECT_ROOT / "evaluation" / "retrieval_results.json"

    dataset = load_dataset(dataset_path)

    results = evaluate_retrieval(
        dataset=dataset,
        top_k=5,
    )

    save_results(
        results=results,
        output_path=output_path,
    )

    print("\n\n========================================")
    print("FINAL RETRIEVAL EVALUATION")
    print("========================================")
    print(f"Total Questions: {results['total_questions']}")
    print(f"Top K: {results['top_k']}")
    print(f"Hit@K: {results['hit_at_k']}")
    print(f"Text Hit@K: {results['text_hit_at_k']}")
    print(f"MRR: {results['mrr']}")

    if results["failed_cases"]:
        print("\nFailed Cases:")
        for case in results["failed_cases"]:
            print(f"- {case['question']}")
    else:
        print("\nNo failed cases 🎉")