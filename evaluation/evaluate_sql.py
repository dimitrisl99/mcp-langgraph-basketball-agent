import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.sql.text_to_sql import answer_sql_question


def load_dataset(dataset_path: Path) -> list[dict]:
    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def contains_expected_text(
    answer: str,
    expected_contains: list[str],
) -> bool:
    if not expected_contains:
        return True

    answer_lower = answer.lower()

    return all(
        expected.lower() in answer_lower
        for expected in expected_contains
    )


def evaluate_sql(dataset: list[dict]) -> dict:
    total = len(dataset)
    correct = 0
    failed_cases = []

    for item in dataset:
        question = item["question"]
        expected_contains = item.get("expected_contains", [])

        answer = answer_sql_question(question)

        is_correct = contains_expected_text(
            answer=answer,
            expected_contains=expected_contains,
        )

        if is_correct:
            correct += 1
        else:
            failed_cases.append(
                {
                    "question": question,
                    "answer": answer,
                    "expected_contains": expected_contains,
                }
            )

        print("\n========================================")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
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
    dataset_path = PROJECT_ROOT / "evaluation" / "sql_dataset.json"
    output_path = PROJECT_ROOT / "evaluation" / "sql_results.json"

    dataset = load_dataset(dataset_path)

    results = evaluate_sql(dataset)

    save_results(results=results, output_path=output_path)

    print("\n\n========================================")
    print("FINAL SQL EVALUATION")
    print("========================================")
    print(f"Total Questions: {results['total_questions']}")
    print(f"Correct: {results['correct']}")
    print(f"Accuracy: {results['accuracy']}")

    if results["failed_cases"]:
        print("\nFailed Cases:")
        for case in results["failed_cases"]:
            print(
                f"- {case['question']} "
                f"| answer: {case['answer'][:100]} "
                f"| expected: {case['expected_contains']}"
            )
    else:
        print("\nNo failed cases 🎉")