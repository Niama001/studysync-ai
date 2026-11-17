"""
StudySync AI -- Evaluation Harness

Runs the retrieval + ranking pipeline on a set of predefined student
requests, compares the results to the expected study spots, and prints
a pass/fail summary.

This script does NOT call Gemini, so it runs without an API key and
always gives the same results.

Run with:
    python eval_harness.py
"""

import sys
from pathlib import Path

from rag.retriever import (
    load_study_spots,
    extract_min_seats,
    retrieve_study_spots,
    recommend_study_spots
)


# Find the CSV file relative to this script
CSV_PATH = Path(__file__).parent / "data" / "study_spots.csv"


# The default preferences used by the AI Study Spot Advisor tab
DEFAULT_PROFILE = {
    "max_noise": "quiet",
    "max_distance": 1.0,
    "min_seats": 4
}


# ------------------------------------------------------------------
# Test cases
# ------------------------------------------------------------------

# Retrieval cases: check that the retriever returns exactly these spots
RETRIEVAL_CASES = [
    {
        "name": "Quiet spots",
        "query": "I need a quiet study spot",
        "expected": [
            "Innovation Commons",
            "Grand Reading Room",
            "North Stacks Nook",
            "Basement Carrels",
            "24-Hour Annex"
        ]
    },
    {
        "name": "Loud spots",
        "query": "I want a loud study spot",
        "expected": [
            "Courtyard Cafe",
            "Student Union Tables"
        ]
    },
    {
        "name": "Moderate noise",
        "query": "I want a moderate study spot",
        "expected": [
            "Engineering Lounge",
            "Rooftop Study Deck",
            "Group Project Room B"
        ]
    },
    {
        "name": "Excellent Wi-Fi",
        "query": "I need a study spot with excellent Wi-Fi",
        "expected": [
            "Innovation Commons",
            "Engineering Lounge",
            "Group Project Room B"
        ]
    },
    {
        "name": "Basic Wi-Fi",
        "query": "I need a study spot with basic Wi-Fi",
        "expected": [
            "Courtyard Cafe",
            "Rooftop Study Deck",
            "Basement Carrels"
        ]
    },
    {
        "name": "Quiet + excellent Wi-Fi",
        "query": "I need a quiet study spot with excellent Wi-Fi",
        "expected": [
            "Innovation Commons"
        ]
    },
    {
        "name": "Quiet + at least 10 seats",
        "query": "I need a quiet study spot with at least 10 seats",
        "expected": [
            "Innovation Commons",
            "Grand Reading Room",
            "Basement Carrels",
            "24-Hour Annex"
        ]
    },
    {
        "name": "Minimum 15 seats",
        "query": "Find a spot with minimum 15 seats",
        "expected": [
            "Grand Reading Room",
            "Engineering Lounge",
            "Student Union Tables",
            "24-Hour Annex"
        ]
    },
    {
        "name": "Impossible seat count",
        "query": "I need a quiet study spot with at least 100 seats",
        "expected": []
    },
    {
        "name": "No spot meets every requirement",
        "query": "I need a quiet study spot with excellent Wi-Fi and at least 20 seats",
        "expected": []
    }
]


# Recommendation cases: check the full retrieve + rank pipeline
RECOMMENDATION_CASES = [
    {
        "name": "Top 3 quiet spots within 1 mile",
        "query": "I need a quiet study spot",
        "profile": DEFAULT_PROFILE,
        "expected_order": [
            "Innovation Commons",
            "Grand Reading Room",
            "Basement Carrels"
        ],
        "expected_top_score": 5.0
    },
    {
        "name": "Profile seat requirement is respected",
        "query": "I need a quiet study spot",
        "profile": {
            "max_noise": "quiet",
            "max_distance": 3.0,
            "min_seats": 15
        },
        "expected_order": [
            "Grand Reading Room",
            "24-Hour Annex"
        ],
        "expected_top_score": 5.0
    }
]


# Seat extraction cases: check the regex that reads seat requirements
SEAT_EXTRACTION_CASES = [
    {"query": "I need a quiet spot with at least 10 seats", "expected": 10},
    {"query": "Find a place with minimum 6 seats", "expected": 6},
    {"query": "I need min 4 seats", "expected": 4},
    {"query": "I need a quiet study spot", "expected": None}
]


# Known limitations: these are NOT counted in the score.
# They document cases the keyword retriever does not handle yet.
LIMITATION_CASES = [
    {
        "name": "Punctuation after a keyword",
        "query": "quiet.",
        "would_expect": "5 quiet spots"
    },
    {
        "name": "'wifi' spelled without a hyphen",
        "query": "excellent wifi",
        "would_expect": "3 spots with excellent Wi-Fi"
    },
    {
        "name": "Synonym for quiet",
        "query": "I need a peaceful study spot",
        "would_expect": "5 quiet spots"
    }
]


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def get_names(spots):
    """
    Return a list of study-spot names from a list of spot dictionaries.
    """
    names = []

    for spot in spots:
        names.append(spot["name"])

    return names


def print_result(passed, label, details=""):
    """
    Print one PASS or FAIL line.
    """
    status = "PASS" if passed else "FAIL"
    line = f"  [{status}] {label}"

    if details:
        line += f"  ->  {details}"

    print(line)


# ------------------------------------------------------------------
# Evaluation sections
# ------------------------------------------------------------------

def run_retrieval_cases(spots):
    """
    Check that retrieval returns exactly the expected spots.
    """
    print("\nRetrieval")
    print("-" * 60)

    passed_count = 0

    for case in RETRIEVAL_CASES:
        results = retrieve_study_spots(case["query"], spots)
        actual = get_names(results)

        # Order does not matter for retrieval, so compare as sets
        passed = set(actual) == set(case["expected"])

        if passed:
            passed_count += 1
            print_result(True, case["name"], f"{len(actual)} spot(s)")
        else:
            print_result(
                False,
                case["name"],
                f"expected {case['expected']}, got {actual}"
            )

    return passed_count, len(RETRIEVAL_CASES)


def run_recommendation_cases(spots):
    """
    Check the full retrieve + rank pipeline: order and top score.
    """
    print("\nRetrieval + Ranking")
    print("-" * 60)

    passed_count = 0

    for case in RECOMMENDATION_CASES:
        ranked = recommend_study_spots(
            case["query"],
            case["profile"],
            spots,
            k=3
        )

        actual_order = []
        for spot, score, reasons in ranked:
            actual_order.append(spot["name"])

        top_score = ranked[0][1] if ranked else None

        # Every recommended spot must meet the profile's seat requirement
        seats_ok = True
        for spot, score, reasons in ranked:
            if spot["seats_available"] < case["profile"]["min_seats"]:
                seats_ok = False

        passed = (
            actual_order == case["expected_order"]
            and top_score == case["expected_top_score"]
            and seats_ok
        )

        if passed:
            passed_count += 1
            print_result(True, case["name"], f"top score {top_score}")
        else:
            print_result(
                False,
                case["name"],
                f"expected {case['expected_order']} (top {case['expected_top_score']}), "
                f"got {actual_order} (top {top_score}), seats ok: {seats_ok}"
            )

    return passed_count, len(RECOMMENDATION_CASES)


def run_seat_extraction_cases():
    """
    Check that seat requirements are read correctly from requests.
    """
    print("\nSeat Requirement Extraction")
    print("-" * 60)

    passed_count = 0

    for case in SEAT_EXTRACTION_CASES:
        actual = extract_min_seats(case["query"])
        passed = actual == case["expected"]

        label = f"\"{case['query']}\""

        if passed:
            passed_count += 1
            print_result(True, label, f"{actual}")
        else:
            print_result(False, label, f"expected {case['expected']}, got {actual}")

    return passed_count, len(SEAT_EXTRACTION_CASES)


def run_limitation_cases(spots):
    """
    Show known limitations. These are reported but not scored.
    """
    print("\nKnown Limitations (not scored)")
    print("-" * 60)

    for case in LIMITATION_CASES:
        results = retrieve_study_spots(case["query"], spots)

        print(
            f"  [INFO] {case['name']}: \"{case['query']}\" "
            f"returned {len(results)} spot(s) "
            f"(ideal: {case['would_expect']})"
        )


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    print("=" * 60)
    print("StudySync AI - Evaluation Harness")
    print("=" * 60)

    spots = load_study_spots(CSV_PATH)
    print(f"Loaded {len(spots)} study spots from {CSV_PATH.name}")

    sections = [
        ("Retrieval", run_retrieval_cases(spots)),
        ("Retrieval + Ranking", run_recommendation_cases(spots)),
        ("Seat Extraction", run_seat_extraction_cases())
    ]

    run_limitation_cases(spots)

    # Print the summary
    total_passed = 0
    total_cases = 0

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for section_name, (passed, total) in sections:
        print(f"  {section_name:<22} {passed}/{total} passed")
        total_passed += passed
        total_cases += total

    score = (total_passed / total_cases) * 100

    print("-" * 60)
    print(f"  {'TOTAL':<22} {total_passed}/{total_cases} passed ({score:.1f}%)")
    print("=" * 60)

    # Exit with an error code if any case failed
    if total_passed < total_cases:
        sys.exit(1)


if __name__ == "__main__":
    main()