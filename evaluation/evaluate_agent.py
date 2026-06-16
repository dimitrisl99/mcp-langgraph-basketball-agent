import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.graph.agent import run_agent


def load_dataset(dataset_path: Path):
    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def evaluate_agent(dataset):
    total = len(dataset)

    route_correct = 0
    source_correct = 0
    answer_correct = 0

    failed_cases = []

    for item in dataset:

        question = item["question"]

        result = run_agent(
            question=question,
            chat_history=[],
        )

        predicted_route = result["route"]

        expected_route = item["expected_route"]

        route_ok = (
            predicted_route == expected_route
        )

        if route_ok:
            route_correct += 1

        source_ok = True

        expected_source = item.get(
            "expected_source"
        )

        if expected_source:

            retrieved_sources = [
                source["file"]
                for source in result["sources"]
            ]

            source_ok = (
                expected_source
                in retrieved_sources
            )

            if source_ok:
                source_correct += 1

        expected_keywords = item.get(
            "expected_answer_contains",
            [],
        )

        answer_text = result["answer"].lower()

        answer_ok = all(
            keyword.lower() in answer_text
            for keyword in expected_keywords
        )

        if answer_ok:
            answer_correct += 1

        if not (
            route_ok
            and source_ok
            and answer_ok
        ):
            failed_cases.append(
                {
                    "question": question,
                    "route_ok": route_ok,
                    "source_ok": source_ok,
                    "answer_ok": answer_ok,
                }
            )

        print("\n========================================")
        print("Question:", question)
        print("Expected:", expected_route)
        print("Predicted:", predicted_route)
        print("Route Correct:", route_ok)
        print("Source Correct:", source_ok)
        print("Answer Correct:", answer_ok)

    return {
        "total_questions": total,
        "route_accuracy":
            round(route_correct / total, 3),
        "source_accuracy":
            round(source_correct / total, 3),
        "answer_accuracy":
            round(answer_correct / total, 3),
        "failed_cases":
            failed_cases,
    }


if __name__ == "__main__":

    dataset = load_dataset(
        PROJECT_ROOT
        / "evaluation"
        / "end_to_end_dataset.json"
    )

    results = evaluate_agent(dataset)

    print("\n========================================")
    print("FINAL END-TO-END EVALUATION")
    print("========================================")
    print(
        "Route Accuracy:",
        results["route_accuracy"]
    )
    print(
        "Source Accuracy:",
        results["source_accuracy"]
    )
    print(
        "Answer Accuracy:",
        results["answer_accuracy"]
    )

    if results["failed_cases"]:
        print("\nFailed Cases:")

        for case in results["failed_cases"]:
            print(case)

    else:
        print("\nNo failed cases 🎉")