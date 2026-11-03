
from pathlib import Path

from rag.retriever import (
    load_study_spots,
    has_enough_seats,
    extract_min_seats,
    retrieve_study_spots,
    recommend_study_spots
)


# Find the CSV file relative to this test file
CSV_PATH = Path(__file__).parent / "data" / "study_spots.csv"


def test_load_study_spots():
    """
    Test whether study spots are loaded correctly from the CSV file.
    """

    # Load the study spots
    spots = load_study_spots(CSV_PATH)

    # Check that the CSV contains 10 study spots
    assert len(spots) == 10

    # Check that the first study spot has the correct name
    assert spots[0]["name"] == "Innovation Commons"

    # Check that distance was converted into a float
    assert isinstance(spots[0]["distance_miles"], float)

    # Check that available seats were converted into an integer
    assert isinstance(spots[0]["seats_available"], int)


def test_has_enough_seats():
    """
    Test whether a study spot meets a minimum seat requirement.
    """

    # Create an example study spot with 12 available seats
    spot = {
        "name": "Innovation Commons",
        "seats_available": 12
    }

    # 12 seats should meet a requirement of 10
    assert has_enough_seats(spot, 10) == True

    # 12 seats should not meet a requirement of 15
    assert has_enough_seats(spot, 15) == False


def test_extract_min_seats():
    """
    Test whether the minimum number of seats is extracted
    from a student's natural-language request.
    """

    # Test a request using "at least"
    assert extract_min_seats(
        "I need a quiet spot with at least 10 seats"
    ) == 10

    # Test a request using "minimum"
    assert extract_min_seats(
        "Find a place with minimum 6 seats"
    ) == 6

    # Test a request using "min"
    assert extract_min_seats(
        "I need min 4 seats"
    ) == 4

    # Return None when no seat requirement is mentioned
    assert extract_min_seats(
        "I need a quiet study spot"
    ) is None


def test_retrieve_quiet_study_spots():
    """
    Test whether retrieval finds only quiet study spots.
    """

    # Load the study spots
    spots = load_study_spots(CSV_PATH)

    # Search for quiet study spots
    results = retrieve_study_spots("quiet", spots)

    # Check that at least one result was found
    assert len(results) > 0

    # Check that every result is quiet
    for spot in results:
        assert spot["noise_level"] == "quiet"


def test_retrieve_spots_with_minimum_seats():
    """
    Test whether retrieval respects the seat requirement
    written in the student's request.
    """

    # Load the study spots
    spots = load_study_spots(CSV_PATH)

    # Search for quiet study spots with at least 10 seats
    results = retrieve_study_spots(
        "quiet study spot with at least 10 seats",
        spots
    )

    # Check that results were found
    assert len(results) > 0

    # Check that every result is quiet
    # and has at least 10 available seats
    for spot in results:
        assert spot["noise_level"] == "quiet"
        assert spot["seats_available"] >= 10



def test_retrieve_no_matching_spots():
    """
    Test whether retrieval returns an empty list
    when no study spots match the request.
    """

    # Load the study spots
    spots = load_study_spots(CSV_PATH)

    # Request a quiet study spot with at least 100 seats
    results = retrieve_study_spots(
        "quiet study spot with at least 100 seats",
        spots
    )

    # Check that no study spots were returned
    assert results == []



def test_recommend_spots_respects_profile_min_seats():
    """
    Test whether recommendations respect the minimum
    seat requirement provided through the student's profile.
    """

    # Load the study spots
    spots = load_study_spots(CSV_PATH)

    # Create a student's preferences
    profile = {
        "max_noise": "quiet",
        "max_distance": 3.0,
        "min_seats": 15
    }

    # The student asks for a quiet study spot
    # Notice that the request does not mention seats
    results = recommend_study_spots(
        "I need a quiet study spot",
        profile,
        spots,
        k=3
    )

    # Make sure recommendations were found
    assert len(results) > 0

    # Check that every recommended spot has at least 15 seats
    for spot, score, reasons in results:
        assert spot["seats_available"] >= 15

def test_retrieve_loud_study_spots():
    """
    Test whether retrieval finds only loud study spots
    when a student requests a loud environment.
    """

    # Load the study spots from our dataset
    spots = load_study_spots(CSV_PATH)

    # Search for loud study spots
    results = retrieve_study_spots(
        "I want a loud study spot",
        spots
    )

    # Get the names of the returned study spots
    result_names = []

    for spot in results:
        result_names.append(spot["name"])

    # These are the loud spots in our dataset
    expected_names = [
        "Courtyard Cafe",
        "Student Union Tables"
    ]

    # Check that retrieval found exactly the expected spots
    assert set(result_names) == set(expected_names)


def test_retrieve_spots_with_excellent_wifi():
    """
    Test whether retrieval finds all study spots
    with excellent Wi-Fi.
    """

    # Load the study spots from our dataset
    spots = load_study_spots(CSV_PATH)

    # Search for study spots with excellent Wi-Fi
    results = retrieve_study_spots(
        "I need a study spot with excellent Wi-Fi",
        spots
    )

    # Get the names of the returned study spots
    result_names = []

    for spot in results:
        result_names.append(spot["name"])

    # These are the spots with excellent Wi-Fi
    expected_names = [
        "Innovation Commons",
        "Engineering Lounge",
        "Group Project Room B"
    ]

    # Check that retrieval found exactly the expected spots
    assert set(result_names) == set(expected_names)


def test_retrieve_quiet_spots_with_excellent_wifi():
    """
    Test whether retrieval finds a study spot
    matching both quiet noise and excellent Wi-Fi.
    """

    # Load the study spots from our dataset
    spots = load_study_spots(CSV_PATH)

    # Search using two requirements
    results = retrieve_study_spots(
        "I need a quiet study spot with excellent Wi-Fi",
        spots
    )

    # Check that exactly one matching spot was found
    assert len(results) == 1

    # Check that the matching spot is Innovation Commons
    assert results[0]["name"] == "Innovation Commons"

    # Check both requested requirements
    assert results[0]["noise_level"] == "quiet"
    assert results[0]["wifi_quality"] == "excellent"

def test_retrieve_no_spot_matches_all_requirements():
    """
    Test whether retrieval returns no results
    when no study spot meets every requirement.
    """

    # Load the study spots from our dataset
    spots = load_study_spots(CSV_PATH)

    # Search for a quiet spot with excellent Wi-Fi and 20 seats
    results = retrieve_study_spots(
        "I need a quiet study spot with excellent Wi-Fi and at least 20 seats",
        spots
    )

    # Check that no study spots match all requirements
    assert results == []