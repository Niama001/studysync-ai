import pytest
from unittest.mock import Mock, patch

from google.genai import errors

from rag.generator import generate_study_spot_explanation


def test_generate_study_spot_explanation():
    """
    Test whether Gemini generates an explanation
    using the ranked study spots.
    """

    # Create a pretend response from Gemini
    mock_response = Mock()
    mock_response.text = "Innovation Commons is a good match!"

    # Create sample ranked study spots
    ranked_spots = [
        (
            {
                "name": "Innovation Commons",
                "noise_level": "quiet",
                "distance_miles": 0.3,
                "wifi_quality": "excellent",
                "seats_available": 12
            },
            5.0,
            ["quiet enough", "close enough", "enough seats"]
        )
    ]

    # Temporarily replace the real Gemini API key and client
    with patch("rag.generator.GEMINI_API_KEY", "test-key"), \
         patch("rag.generator.client") as mock_client:

        # Tell our pretend Gemini client what to return
        mock_client.models.generate_content.return_value = mock_response

        # Call the function we want to test
        explanation = generate_study_spot_explanation(
            "I need a quiet study spot with at least 10 seats",
            ranked_spots
        )

    # Check that the function returned Gemini's pretend response
    assert explanation == "Innovation Commons is a good match!"

    # Check that the Gemini client was called once
    mock_client.models.generate_content.assert_called_once()


def test_generate_explanation_with_no_ranked_spots():
    """
    Test whether the generator returns a helpful message
    when no study spots are found.
    """

    explanation = generate_study_spot_explanation(
        "I need a quiet study spot",
        []
    )

    # Check that the function returns a helpful message
    assert "couldn't find" in explanation.lower()


def test_generate_explanation_without_api_key():
    """
    Test whether the generator raises an error
    when the Gemini API key is missing.
    """

    # Create sample ranked study spots
    ranked_spots = [
        (
            {
                "name": "Innovation Commons",
                "noise_level": "quiet",
                "distance_miles": 0.3,
                "wifi_quality": "excellent",
                "seats_available": 12
            },
            5.0,
            ["quiet enough", "close enough", "enough seats"]
        )
    ]

    # Temporarily pretend the API key is missing
    with patch("rag.generator.GEMINI_API_KEY", None):

        # Check that the function raises the expected error
        with pytest.raises(
            ValueError,
            match="Gemini API key not found"
        ):
            generate_study_spot_explanation(
                "I need a quiet study spot",
                ranked_spots
            )


def test_generate_explanation_retries_after_503_error():
    """
    Test whether the generator retries when Gemini
    temporarily becomes unavailable.
    """

    # Create a pretend successful response from Gemini
    mock_response = Mock()
    mock_response.text = "Innovation Commons is a good match!"

    # Create a pretend Gemini API 503 error
    mock_error = errors.APIError(
        503,
        {
            "message": "Gemini is temporarily unavailable.",
            "status": "UNAVAILABLE"
        },
        None
    )

    # Temporarily replace the real Gemini API key and client
    with patch("rag.generator.GEMINI_API_KEY", "test-key"), \
         patch("rag.generator.client") as mock_client, \
         patch("rag.generator.time.sleep") as mock_sleep:

        # Make the first API call fail and the second call succeed
        mock_client.models.generate_content.side_effect = [
            mock_error,
            mock_response
        ]

        # Ask the generator to explain the recommendation
        explanation = generate_study_spot_explanation(
            "I need a quiet study spot",
            [
                (
                    {
                        "name": "Innovation Commons",
                        "noise_level": "quiet",
                        "distance_miles": 0.3,
                        "wifi_quality": "excellent",
                        "seats_available": 12
                    },
                    5.0,
                    ["quiet enough", "close enough", "enough seats"]
                )
            ]
        )

    # Check that the generator eventually returned an explanation
    assert explanation == "Innovation Commons is a good match!"

    # Check that Gemini was called twice
    assert mock_client.models.generate_content.call_count == 2

    # Check that the generator waited before retrying
    mock_sleep.assert_called_once_with(2)


def test_generate_explanation_fails_after_three_attempts():
    """
    Test whether the generator raises an error
    after all three Gemini attempts fail.
    """

    # Create a pretend Gemini API 503 error
    mock_error = errors.APIError(
        503,
        {
            "message": "Gemini is temporarily unavailable.",
            "status": "UNAVAILABLE"
        },
        None
    )

    # Temporarily replace the real API key, client, and sleep function
    with patch("rag.generator.GEMINI_API_KEY", "test-key"), \
         patch("rag.generator.client") as mock_client, \
         patch("rag.generator.time.sleep") as mock_sleep:

        # Make all three API attempts fail
        mock_client.models.generate_content.side_effect = [
            mock_error,
            mock_error,
            mock_error
        ]

        # Check that the API error is raised after three attempts
        with pytest.raises(errors.APIError):
            generate_study_spot_explanation(
                "I need a quiet study spot",
                [
                    (
                        {
                            "name": "Innovation Commons",
                            "noise_level": "quiet",
                            "distance_miles": 0.3,
                            "wifi_quality": "excellent",
                            "seats_available": 12
                        },
                        5.0,
                        ["quiet enough", "close enough", "enough seats"]
                    )
                ]
            )

    # Check that Gemini was called exactly three times
    assert mock_client.models.generate_content.call_count == 3

    # Check that StudySync waited twice before giving up
    assert mock_sleep.call_count == 2

