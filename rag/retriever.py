
import csv
import re

from ranking import rank_study_spots


# Common words that don't provide useful information for searching
STOP_WORDS = [
    "i", "want", "a", "an", "the",
    "with", "and", "or", "to", "for",
    "need", "looking", "find", "me",
    "place", "spot", "study", "wi-fi"
]


def load_study_spots(csv_path):
    """
    Load study spots from a CSV file into a list of dictionaries.
    """

    # Create an empty list to store all study spots
    spots = []

    # Open the CSV file in read mode
    with open(csv_path, "r", newline="", encoding="utf-8") as file:

        # Read the CSV file as dictionaries
        reader = csv.DictReader(file)

        # Go through each row in the CSV file
        for row in reader:

            # Convert distance from a string to a decimal number
            row["distance_miles"] = float(row["distance_miles"])

            # Convert available seats from a string to a whole number
            row["seats_available"] = int(row["seats_available"])

            # Add the updated study spot to our list
            spots.append(row)

    # Return the complete list of study spots
    return spots


def has_enough_seats(spot, min_seats):
    """
    Check whether a study spot has enough available seats.
    """

    # Get the number of available seats
    seats_available = int(spot["seats_available"])

    # Return True if the available seats meet the minimum requirement
    return seats_available >= min_seats


def extract_min_seats(query):
    """
    Extract the minimum number of seats from a student's request.
    """

    # Look for phrases such as:
    # "at least 4 seats"
    # "minimum 6 seats"
    # "min 10 seats"
    match = re.search(
        r"(?:at least|minimum|min)\s+(\d+)\s+seats?",
        query.lower()
    )

    # If a seating requirement was found
    if match:

        # Convert the captured number from a string to an integer
        return int(match.group(1))

    # If no seating requirement was found, return None
    return None


def retrieve_study_spots(query, spots, min_seats=None):
    """
    Find study spots that match all keywords in the student's request.
    Optionally filter spots by a minimum number of available seats.
    """

    # Automatically extract the minimum seat requirement
    extracted_min_seats = extract_min_seats(query)

    # Use the extracted requirement if one exists
    if extracted_min_seats is not None:
        min_seats = extracted_min_seats

    # Convert the student's request to lowercase
    query = query.lower()

    # Remove the minimum seat requirement before keyword matching
    query_without_seats = re.sub(
        r"(?:at least|minimum|min)\s+\d+\s+seats?",
        "",
        query
    )

    # Split the remaining request into individual words
    words = query_without_seats.split()

    # Keep only words that are not in our stop words list
    keywords = []

    for word in words:
        if word not in STOP_WORDS:
            keywords.append(word)

    # Create an empty list to store matching study spots
    results = []

    # Go through every study spot
    for spot in spots:

        # If a minimum seat requirement exists, check available seats
        if min_seats is not None:

            # Skip this study spot if it does not have enough seats
            if not has_enough_seats(spot, min_seats):
                continue

        # Combine the study spot's information into one string
        spot_info = (
            spot["name"] + " " +
            spot["noise_level"] + " " +
            spot["wifi_quality"] + " " +
            str(spot["distance_miles"]) + " " +
            str(spot["seats_available"])
        )

        # Convert the study spot information to lowercase
        spot_info = spot_info.lower()

        # Assume the study spot matches all keywords
        matches_all = True

        # Check every keyword against the study spot information
        for keyword in keywords:

            # If even one keyword is missing, it is not a complete match
            if keyword not in spot_info:
                matches_all = False
                break

        # Only add the study spot if every keyword matches
        if matches_all:
            results.append(spot)

    # Return all matching study spots
    return results



def recommend_study_spots(query, profile, spots, k=3):
    """
    Retrieve relevant study spots, then rank them
    using the existing ranking algorithm.
    """

    # Step 1: Retrieve study spots that match the student's request
    # Also pass the minimum seat requirement from the student's profile
    relevant_spots = retrieve_study_spots(
        query,
        spots,
        min_seats=profile["min_seats"]
    )

    # Step 2: If no relevant study spots were found, return an empty list
    if not relevant_spots:
        return []

    # Step 3: Rank only the retrieved study spots
    ranked_spots = rank_study_spots(profile, relevant_spots, k)

    # Step 4: Return the highest-ranked study spots
    return ranked_spots
