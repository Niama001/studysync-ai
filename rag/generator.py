
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from logging_config import logger



# Load environment variables from the .env file
load_dotenv()


# Read the Gemini API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Create a Gemini client only if the API key exists
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def generate_study_spot_explanation(query, ranked_spots):
    """
    Ask Gemini to explain why the recommended study spots
    match the student's request.

    Retry the request if Gemini is temporarily unavailable.
    """

    # Check whether the Gemini API key was loaded
    if not GEMINI_API_KEY:
        raise ValueError(
            "Gemini API key not found. Check your .env file."
        )

    # Check whether we have any study spots to explain
    if not ranked_spots:
        return "I couldn't find any study spots matching your request."


    # Record that StudySync is starting AI explanation generation
    logger.info("Starting Gemini explanation generation.")

    # Create an empty string to store information about the spots
    context = ""

    # Go through each ranked study spot
    for spot, score, reasons in ranked_spots:

        # Add the spot's information to the context
        context += (
            f"\nStudy Spot: {spot['name']}\n"
            f"Noise Level: {spot['noise_level']}\n"
            f"Distance: {spot['distance_miles']} miles\n"
            f"Wi-Fi Quality: {spot['wifi_quality']}\n"
            f"Available Seats: {spot['seats_available']}\n"
            f"Ranking Score: {score}\n"
            f"Ranking Reasons: {', '.join(reasons)}\n"
        )

    # Create instructions for Gemini
    prompt = f"""
    You are StudySync, a helpful study-spot recommendation assistant.

    A student submitted this request:
    "{query}"

    Here are the study spots retrieved and ranked by StudySync:
    {context}

    Your task:
    1. Explain why each recommended spot may fit the student's request.
    2. Use only the information provided above.
    3. Do not invent features, amenities, or details.
    4. Mention relevant details such as noise, distance, Wi-Fi, and seats.
    5. Explain the ranking reasons in simple, friendly language.
    6. If a detail is not provided, do not make assumptions about it.

    Give the student a clear and concise explanation.
    """

    # Try sending the request to Gemini up to 3 times
    for attempt in range(3):

        try:
            # Send the prompt to Gemini
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            # Check whether Gemini returned readable text
            if not response.text:
                return (
                    "Gemini did not return an explanation. "
                    "Please try again."
                )


            # Record that Gemini successfully generated an explanation
            logger.info("Gemini successfully generated an explanation.")

            # Return Gemini's explanation
            return response.text

        except errors.APIError as error:

            # Record the Gemini API error
            logger.error(f"Gemini API error: {error}")

            # Retry only if Gemini reports temporary unavailability
            if error.code == 503 and attempt < 2:

                # Wait 2 seconds before trying again
                time.sleep(2)

            else:
                # Raise the error if all attempts fail
                raise
