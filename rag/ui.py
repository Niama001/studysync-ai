
import streamlit as st

from rag.retriever import load_study_spots, recommend_study_spots
from rag.generator import generate_study_spot_explanation


def render_ai_study_spot_tab():
    """
    Display the AI-powered StudySync study spot advisor.
    """

    # Display the title and introduction
    st.subheader("AI Study Spot Advisor")

    st.write(
        "Tell StudySync what kind of study environment you need, "
        "and AI will help explain your recommendations."
    )

    # Get the student's request in natural language
    query = st.text_input(
        "What kind of study spot are you looking for?",
        placeholder="Example: I need a quiet study spot with at least 10 seats"
    )

    # Collect the student's preferences for the ranking algorithm
    max_noise = st.selectbox(
        "Maximum noise level",
        ["quiet", "moderate", "loud"],
        index=0
    )

    max_distance = st.slider(
        "Maximum distance (miles)",
        0.0,
        3.0,
        1.0
    )

    min_seats = st.number_input(
        "Minimum seats needed",
        min_value=1,
        value=4,
        step=1
    )

    # Run the recommendation system when the button is clicked
    if st.button("Find study spots"):

        # Make sure the student entered a request
        if not query.strip():
            st.warning("Please describe the study spot you need.")

        else:
            try:
                # Load the study spots from the CSV file
                spots = load_study_spots("data/study_spots.csv")

                # Create the student's ranking profile
                profile = {
                    "max_noise": max_noise,
                    "max_distance": max_distance,
                    "min_seats": min_seats
                }

                # Retrieve relevant spots and rank them
                ranked_spots = recommend_study_spots(
                    query,
                    profile,
                    spots,
                    k=3
                )

                # Check whether any study spots matched
                if not ranked_spots:
                    st.info(
                        "No study spots matched your request. "
                        "Try changing your search."
                    )

                else:
                    # Display the ranking results
                    st.subheader("Your Top Recommendations")

                    for spot, score, reasons in ranked_spots:

                        # Display the study spot's name
                        st.markdown(f"### {spot['name']}")

                        # Display its ranking score
                        st.write(f"**Ranking Score:** {score:.1f}")

                        # Display its noise level
                        st.write(
                            f"**Noise Level:** {spot['noise_level']}"
                        )

                        # Display its distance
                        st.write(
                            f"**Distance:** {spot['distance_miles']} miles"
                        )

                        # Display its available seats
                        st.write(
                            f"**Available Seats:** {spot['seats_available']}"
                        )

                        # Display its Wi-Fi quality
                        st.write(
                            f"**Wi-Fi Quality:** {spot['wifi_quality']}"
                        )

                        # Display the reasons behind its ranking score
                        st.write(
                            f"**Ranking Reasons:** {', '.join(reasons)}"
                        )

                    # Display the AI explanation section
                    st.subheader("AI Explanation")

                    # Show a loading message while Gemini generates its response
                    with st.spinner(
                        "StudySync AI is generating your explanation..."
                    ):

                        # Ask Gemini to explain the recommendations
                        explanation = generate_study_spot_explanation(
                            query,
                            ranked_spots
                        )

                    # Display Gemini's generated explanation
                    st.markdown(explanation)

            except Exception as error:

                # Display an error if something goes wrong
                st.error(f"Something went wrong: {error}")
