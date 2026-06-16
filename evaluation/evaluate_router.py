import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.graph.agent import route_question


def load_dataset(dataset_path: Path) -> list[dict]:
    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_router(dataset: list[dict]) -> dict:
    total = len(dataset)
    correct = 0
    failed_cases = []

    for item in dataset:
        question = item["question"]
        expected_route = item["expected_route"]

        state = {
            "question": question,
            "standalone_question": question,
            "chat_history": [],
            "route": "",
            "answer": "",
            "sources": [],
            "timings": {},
        }

        result_state = route_question(state)

        predicted_route = result_state["route"]
        timings = result_state.get("timings", {})
        router_method = timings.get("router_method", "unknown")

        is_correct = predicted_route == expected_route

        if is_correct:
            correct += 1
        else:
            failed_cases.append(
                {
                    "question": question,
                    "expected_route": expected_route,
                    "predicted_route": predicted_route,
                    "router_method": router_method,
                }
            )

        print("\n========================================")
        print(f"Question: {question}")
        print(f"Expected: {expected_route}")
        print(f"Predicted: {predicted_route}")
        print(f"Router method: {router_method}")
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
    dataset_path = PROJECT_ROOT / "evaluation" / "router_dataset.json"
    output_path = PROJECT_ROOT / "evaluation" / "router_results.json"

    dataset = load_dataset(dataset_path)

    results = evaluate_router(dataset)

    save_results(
        results=results,
        output_path=output_path,
    )

    print("\n\n========================================")
    print("FINAL ROUTER EVALUATION")
    print("========================================")
    print(f"Total Questions: {results['total_questions']}")
    print(f"Correct: {results['correct']}")
    print(f"Accuracy: {results['accuracy']}")

    if results["failed_cases"]:
        print("\nFailed Cases:")
        for case in results["failed_cases"]:
            print(
                f"- {case['question']} "
                f"| expected: {case['expected_route']} "
                f"| predicted: {case['predicted_route']} "
                f"| method: {case['router_method']}"
            )
    else:
        print("\nNo failed cases 🎉")