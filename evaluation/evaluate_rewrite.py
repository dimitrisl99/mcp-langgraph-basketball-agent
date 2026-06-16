import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.graph.agent import rewrite_question


def load_dataset(dataset_path: Path) -> list[dict]:
    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def contains_expected_text(
    rewritten_question: str,
    expected_contains: list[str],
) -> bool:
    rewritten_lower = rewritten_question.lower()

    return all(
        expected.lower() in rewritten_lower
        for expected in expected_contains
    )


def evaluate_rewrite(dataset: list[dict]) -> dict:
    total = len(dataset)
    correct = 0
    failed_cases = []

    for item in dataset:
        chat_history = item["chat_history"]
        question = item["question"]
        expected_contains = item["expected_contains"]

        state = {
            "question": question,
            "standalone_question": "",
            "chat_history": chat_history,
            "route": "",
            "answer": "",
            "sources": [],
            "timings": {},
        }

        result_state = rewrite_question(state)

        rewritten_question = result_state["standalone_question"]

        is_correct = contains_expected_text(
            rewritten_question=rewritten_question,
            expected_contains=expected_contains,
        )

        if is_correct:
            correct += 1
        else:
            failed_cases.append(
                {
                    "question": question,
                    "rewritten_question": rewritten_question,
                    "expected_contains": expected_contains,
                }
            )

        print("\n========================================")
        print(f"Question: {question}")
        print(f"Rewritten: {rewritten_question}")
        print(f"Expected contains: {expected_contains}")
        print(f"Correct: {is_correct}")

    accuracy = correct / total if total else 0

    return {
        "total_questions": total,
        "correct": correct,
        "accuracy": round(accuracy, 3),
        "failed_cases": failed_cases,
    }


def save_results(results: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    dataset_path = PROJECT_ROOT / "evaluation" / "rewrite_dataset.json"
    output_path = PROJECT_ROOT / "evaluation" / "rewrite_results.json"

    dataset = load_dataset(dataset_path)

    results = evaluate_rewrite(dataset)

    save_results(
        results=results,
        output_path=output_path,
    )

    print("\n\n========================================")
    print("FINAL REWRITE EVALUATION")
    print("========================================")
    print(f"Total Questions: {results['total_questions']}")
    print(f"Correct: {results['correct']}")
    print(f"Accuracy: {results['accuracy']}")

    if results["failed_cases"]:
        print("\nFailed Cases:")
        for case in results["failed_cases"]:
            print(
                f"- {case['question']} "
                f"| rewritten: {case['rewritten_question']} "
                f"| expected contains: {case['expected_contains']}"
            )
    else:
        print("\nNo failed cases 🎉")