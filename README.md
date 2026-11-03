# StudySync AI

**An AI-powered study-spot recommendation system built with Python, Streamlit, and Gemini.**

StudySync AI helps students find study environments that match their preferences. Students can describe what they need in natural language, and the application retrieves relevant study spots, ranks them using the existing recommendation algorithm, and uses Google's Gemini API to generate explanations for the recommendations.

## Features

### 1. Session Scorer
- Evaluates session ratings.
- Provides feedback based on the submitted score.

### 2. Session Log
- Supports the existing study-session logging functionality.

### 3. AI Study Spot Advisor
- Accepts natural-language study-spot requests.
- Retrieves matching locations from a CSV dataset using keyword-based matching.
- Supports preferences such as noise level, Wi-Fi quality, and minimum available seats.
- Ranks retrieved locations using the existing StudySync scoring algorithm.
- Uses Gemini to explain why the recommended locations match the student's request.
- Includes error handling and retry logic for temporary Gemini API failures.

## How It Works

StudySync AI combines retrieval, ranking, and AI-generated explanations.

1. **User Request:** A student describes their preferred study environment.
2. **Retrieval:** The retriever searches the study-spot dataset for matching keywords and filters locations based on minimum seat requirements.
3. **Ranking:** The existing ranking algorithm scores and sorts the retrieved locations.
4. **AI Explanation:** Gemini receives the student's request and the retrieved study-spot information to generate a grounded explanation.
5. **Results:** Streamlit displays the recommendations, ranking scores, relevant details, and AI-generated explanation.

The retrieval system currently uses keyword-based matching rather than vector embeddings or a vector database.

## Project Architecture

The project separates the retrieval, generation, user interface, and logging responsibilities into different modules.

| File | Description |
|---|---|
| `app.py` | Main Streamlit application and tab navigation |
| `ranking.py` | Existing study-spot scoring and ranking algorithm |
| `rag/retriever.py` | Loads study-spot data and retrieves matching locations |
| `rag/generator.py` | Sends retrieved information to Gemini and generates explanations |
| `rag/ui.py` | Streamlit interface for the AI Study Spot Advisor |
| `logging_config.py` | Configures application logging |
| `data/study_spots.csv` | Study-spot dataset |
| `diagrams/architecture.mmd` | Mermaid architecture diagram |
| `test_retriever.py` | Tests retrieval and recommendation behavior |
| `test_generator.py` | Tests Gemini response handling and error recovery |
| `test_scoring.py` | Tests the original scoring functionality |
| `evaluation.md` | Evaluation scenarios and automated test results |
| `model_card.md` | Model documentation, limitations, ethics, and AI collaboration |

## Dataset

StudySync uses `data/study_spots.csv` as its study-spot knowledge source.

The dataset contains 10 sample study locations and includes:

- `id` — Unique study-spot identifier
- `name` — Study-spot name
- `noise_level` — Quiet, moderate, or loud
- `distance_miles` — Distance in miles
- `wifi_quality` — Basic, good, or excellent
- `seats_available` — Number of available seats in the sample dataset

Recommendations are limited to the information available in this dataset. Seat availability and other conditions are not verified in real time.

## Technologies Used

- **Python** — Application logic and data processing
- **Streamlit** — Interactive web application
- **Google Gemini API** — AI-generated recommendation explanations
- - **Python CSV module** — Study-spot data loading and management
- **Pytest** — Automated testing
- **python-dotenv** — Environment variable management
- **Logging** — Application activity and error tracking

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Niama001/studysync-ai.git
cd studysync-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace `your_gemini_api_key` with your own Gemini API key.

**Important:** Never commit your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL where you can open StudySync AI in your browser.

## Running Tests

Run the complete automated test suite:

```bash
pytest -v
```

The project currently includes 18 automated tests covering:

- Study-spot retrieval and filtering
- Minimum seat requirements
- Recommendation behavior
- Gemini explanation generation
- Missing API key handling
- Retry behavior after temporary API failures
- Original scoring functionality

**Latest evaluation:** 18 tests passed, 0 failed.

See [evaluation.md](evaluation.md) for the evaluation details.

## Logging

StudySync records application events and errors in:

```text
logs/studysync.log
```

The logging system tracks Gemini explanation generation, successful responses, and API errors. The `logs/` directory is generated when the application runs.

## Limitations

- The study-spot dataset contains only 10 sample locations.
- Retrieval uses keyword matching, so it may not recognize every variation of a student's request.
- Study-spot information is not updated in real time.
- Gemini-generated explanations depend on the retrieved information and may still require human review.

See [model_card.md](model_card.md) for additional information about limitations, potential misuse, reliability, and ethical considerations.

## Project Documentation

- [Model Card](model_card.md)
- [Evaluation Report](evaluation.md)
- [Architecture Diagram](diagrams/architecture.mmd)

## Future Improvements

Potential future improvements include:

- Expanding the study-spot dataset with additional locations and information sources.
- Improving retrieval to understand different ways students express similar preferences.
- Adding real-time study-space availability information.
- Expanding evaluation with additional student requests and feedback.

---

**Built as part of CodePath AI110: Foundations to AI Engineering - Project 4, Applied AI System.**