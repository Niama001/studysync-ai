# StudySync AI

**An AI-powered study-spot recommendation system built with Python, Streamlit, and Gemini.**

StudySync AI helps students find study environments that match their preferences. Students can describe what they need in natural language, and the application retrieves relevant study spots, ranks them using the existing recommendation algorithm, and uses Google's Gemini API to generate explanations for the recommendations.

## Original Project

### Base Project: StudySync — "Find a Study Spot" (CodePath AI110, Tinker 3B)

StudySync AI extends the **StudySync** app from CodePath AI110, specifically the **"Find a Study Spot"** feature built in Tinker 3B (`ranking.py`).

**Original goal:** Help a student choose a campus study spot that fits their basic needs.

**Original capabilities:**

- Loaded 10 sample study spots from `data/study_spots.csv`.
- Let the student set preferences using form controls only: maximum noise level (dropdown), maximum distance (slider), and minimum seats (number input).
- Scored **every** spot with a fixed rule-based algorithm:
  - Noise within the limit: **+2** ("quiet enough"), otherwise **−1** ("too loud")
  - Distance within the limit: **+2** ("close enough"), otherwise **−1** ("too far")
  - Enough seats: **+1** ("enough seats"), otherwise **−1** ("not enough seats")
- Displayed the top 3 spots with their score and short reason labels.

**What the original system could not do:**

- It could not understand a typed, natural-language request.
- It did not search or filter spots based on what the student asked for (it always scored all 10).
- It did not consider Wi-Fi quality.
- It did not explain its recommendations beyond short labels like "quiet enough, close enough."
- It had no AI component, no logging, and no error handling for external services.

### What StudySync AI Adds

| | Original (Tinker 3B) | StudySync AI (Project 4) |
|---|---|---|
| **Input** | Dropdown, slider, number input | Natural-language request + preferences |
| **Search** | None — scores all 10 spots | Keyword retrieval + automatic seat-requirement extraction |
| **Ranking** | Rule-based scoring | Same scoring algorithm, applied only to retrieved spots |
| **Wi-Fi** | Not used | Searchable (e.g., "excellent Wi-Fi") |
| **Explanation** | Short reason labels | Gemini-generated explanation grounded in retrieved data |
| **Reliability** | None | API key check, empty-input check, 503 retry logic, logging, error display |
| **Testing** | None for ranking | 18 automated tests + an evaluation harness with 16 predefined cases |

The original ranking algorithm in `ranking.py` was kept and reused. The new AI Study Spot Advisor adds retrieval before ranking and AI generation after it, which turns the original ranker into a Retrieval-Augmented Generation (RAG) system.

> **Note:** The **Session Scorer** and **Session Log** tabs come from earlier StudySync tinker activities and are kept for completeness. The Project 4 extension is the **AI Study Spot Advisor** tab.

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
| `eval_harness.py` | Evaluation script that runs 16 predefined requests and prints a pass/fail summary |
| `test_retriever.py` | Tests retrieval and recommendation behavior |
| `test_generator.py` | Tests Gemini response handling and error recovery |
| `test_scoring.py` | Tests the original scoring functionality |
| `evaluation.md` | Evaluation scenarios, guardrail examples, and test results |
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
- **Python CSV module** — Study-spot data loading and management
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

## Sample Interactions

The following examples were run end-to-end in the **AI Study Spot Advisor** tab using:

```bash
streamlit run app.py
```

All three examples used the same preference settings:

```text
Maximum noise level:  quiet
Maximum distance:     1.0 miles
Minimum seats needed: 4
```

### Example 1: Quiet spot with a seat requirement

**Input:**

```text
I need a quiet study spot with at least 10 seats
```

**What happened:** The retriever extracted `10` as the minimum seat requirement, kept only quiet spots with 10+ seats, and the ranker sorted the top 3.

**Output:**

```text
Your Top Recommendations

Innovation Commons
Ranking Score: 5.0
Noise Level: quiet
Distance: 0.3 miles
Available Seats: 12
Wi-Fi Quality: excellent
Ranking Reasons: quiet enough, close enough, enough seats

Grand Reading Room
Ranking Score: 5.0
Noise Level: quiet
Distance: 0.5 miles
Available Seats: 20
Wi-Fi Quality: good
Ranking Reasons: quiet enough, close enough, enough seats

Basement Carrels
Ranking Score: 5.0
Noise Level: quiet
Distance: 0.9 miles
Available Seats: 10
Wi-Fi Quality: basic
Ranking Reasons: quiet enough, close enough, enough seats

AI Explanation

Hello! I'm StudySync, and I found three great study spots that match your
request for a quiet space with at least 10 seats.

All three spots received a top ranking score of 5.0 because they are quiet
enough, close enough, and have enough seats to fit your needs.

* Innovation Commons
  * Noise Level: Quiet
  * Available Seats: 12 (meets your 10-seat requirement)
  * Distance: 0.3 miles away (the closest option)
  * Wi-Fi Quality: Excellent
  * Why it fits: It provides the quiet environment and seat count you need,
    with the added benefit of being very close by and having excellent Wi-Fi.

* Grand Reading Room
  * Noise Level: Quiet
  * Available Seats: 20 (plenty of seating)
  * Distance: 0.5 miles away
  * Wi-Fi Quality: Good
  * Why it fits: It is quiet, has the most available seating of all the
    options, is only half a mile away, and offers good Wi-Fi.

* Basement Carrels
  * Noise Level: Quiet
  * Available Seats: 10 (meets your minimum requirement)
  * Distance: 0.9 miles away
  * Wi-Fi Quality: Basic
  * Why it fits: It gives you the quiet space you asked for with exactly
    10 seats available, located under a mile away with basic Wi-Fi.
```

### Example 2: Excellent Wi-Fi

**Input:**

```text
I need a study spot with excellent Wi-Fi
```

**What happened:** The retriever found all 3 spots with excellent Wi-Fi. The ranker scored the two moderate-noise spots lower because the noise preference was set to `quiet`.

**Output:**

```text
Your Top Recommendations

Innovation Commons
Ranking Score: 5.0
Noise Level: quiet
Distance: 0.3 miles
Available Seats: 12
Wi-Fi Quality: excellent
Ranking Reasons: quiet enough, close enough, enough seats

Engineering Lounge
Ranking Score: 2.0
Noise Level: moderate
Distance: 0.8 miles
Available Seats: 15
Wi-Fi Quality: excellent
Ranking Reasons: too loud, close enough, enough seats

Group Project Room B
Ranking Score: 2.0
Noise Level: moderate
Distance: 0.4 miles
Available Seats: 6
Wi-Fi Quality: excellent
Ranking Reasons: too loud, close enough, enough seats

AI Explanation

Hi there! Here are the study spots that match your need for excellent Wi-Fi,
along with the details and rankings for each:

1. Innovation Commons (Top Pick – Ranking Score: 5.0)
   * Wi-Fi Quality: Excellent
   * Distance: 0.3 miles
   * Noise Level: Quiet
   * Available Seats: 12
   * Why it fits: This is your best option because it meets your need for
     excellent Wi-Fi while being quiet enough, close enough, and having
     plenty of available seats.

2. Engineering Lounge (Ranking Score: 2.0)
   * Wi-Fi Quality: Excellent
   * Distance: 0.8 miles
   * Noise Level: Moderate
   * Available Seats: 15
   * Why it fits: It has the excellent Wi-Fi you need, is close enough, and
     offers plenty of seating. However, it received a lower score of 2.0
     because it is considered too loud.

3. Group Project Room B (Ranking Score: 2.0)
   * Wi-Fi Quality: Excellent
   * Distance: 0.4 miles
   * Noise Level: Moderate
   * Available Seats: 6
   * Why it fits: It provides excellent Wi-Fi, is close by, and has enough
     open seats. Like the Engineering Lounge, it scored a 2.0 because it is
     considered too loud.
```

### Example 3: Loud spot (request conflicts with preference setting)

**Input:**

```text
I want a loud study spot
```

**What happened:** The retriever found the 2 loud spots in the dataset. Because the noise preference was still set to `quiet`, the ranker labeled both as "too loud." Gemini noticed this conflict and explained it to the student.

**Output:**

```text
Your Top Recommendations

Courtyard Cafe
Ranking Score: 2.0
Noise Level: loud
Distance: 0.2 miles
Available Seats: 8
Wi-Fi Quality: basic
Ranking Reasons: too loud, close enough, enough seats

Student Union Tables
Ranking Score: 2.0
Noise Level: loud
Distance: 0.1 miles
Available Seats: 25
Wi-Fi Quality: good
Ranking Reasons: too loud, close enough, enough seats

AI Explanation

Hi! I'm StudySync, and here are two study spots that match your request for
a loud environment:

1. Student Union Tables
   * Noise Level: Loud (matches your request)
   * Distance: 0.1 miles
   * Wi-Fi Quality: Good
   * Available Seats: 25
   * Why it fits: This spot directly fits your preference for a loud study
     area. It received a ranking score of 2.0 because the system considered
     it "too loud" (even though that's what you are looking for!), but noted
     it is close enough and has plenty of available seats.

2. Courtyard Cafe
   * Noise Level: Loud (matches your request)
   * Distance: 0.2 miles
   * Wi-Fi Quality: Basic
   * Available Seats: 8
   * Why it fits: Like your first option, this cafe offers the loud
     atmosphere you requested. It also received a ranking score of 2.0 with
     the ranking reasons of being "too loud," close enough, and having
     enough seats.

Both locations fit your noise preference, are very close by, and have seats
available right now!
```

### Observations from the Sample Runs

- **Consistent results:** Retrieval and ranking are deterministic, so the same request always returns the same spots and scores. Only Gemini's wording varies between runs.
- **Grounded explanations:** In all three examples, Gemini only used details from the dataset (noise, distance, Wi-Fi, seats, and ranking reasons). It did not invent amenities such as outlets, food, or opening hours.
- **Transparency about conflicts:** In Example 3, Gemini pointed out that the ranking said "too loud" even though the student asked for a loud spot, instead of hiding the mismatch.
- **One overclaim found during review:** Example 3 ends with "have seats available right now!" The dataset is not real-time, so this phrase goes slightly beyond the provided data. This shows why AI explanations still need human review (see [Limitations](#limitations)).

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

## Evaluation Harness

In addition to the pytest suite, `eval_harness.py` evaluates the full retrieval and ranking pipeline on **16 predefined student requests** and prints a pass/fail summary.

The harness does not call Gemini, so it runs without an API key and always gives the same results.

### What It Checks

| Section | Cases | What Is Checked |
|---|---:|---|
| Retrieval | 10 | The retriever returns exactly the expected spots for noise, Wi-Fi, seat, combined, and impossible requests |
| Retrieval + Ranking | 2 | The top 3 order, the top score, and that every result meets the seat requirement |
| Seat Extraction | 4 | Seat requirements are read correctly from "at least," "minimum," "min," and requests with no number |
| Known Limitations | 3 | Reported but **not scored** — documents requests the keyword retriever cannot handle yet |

### Run It

```bash
python eval_harness.py
```

### Latest Output

```text
============================================================
StudySync AI - Evaluation Harness
============================================================
Loaded 10 study spots from study_spots.csv

Retrieval
------------------------------------------------------------
  [PASS] Quiet spots  ->  5 spot(s)
  [PASS] Loud spots  ->  2 spot(s)
  [PASS] Moderate noise  ->  3 spot(s)
  [PASS] Excellent Wi-Fi  ->  3 spot(s)
  [PASS] Basic Wi-Fi  ->  3 spot(s)
  [PASS] Quiet + excellent Wi-Fi  ->  1 spot(s)
  [PASS] Quiet + at least 10 seats  ->  4 spot(s)
  [PASS] Minimum 15 seats  ->  4 spot(s)
  [PASS] Impossible seat count  ->  0 spot(s)
  [PASS] No spot meets every requirement  ->  0 spot(s)

Retrieval + Ranking
------------------------------------------------------------
  [PASS] Top 3 quiet spots within 1 mile  ->  top score 5.0
  [PASS] Profile seat requirement is respected  ->  top score 5.0

Seat Requirement Extraction
------------------------------------------------------------
  [PASS] "I need a quiet spot with at least 10 seats"  ->  10
  [PASS] "Find a place with minimum 6 seats"  ->  6
  [PASS] "I need min 4 seats"  ->  4
  [PASS] "I need a quiet study spot"  ->  None

Known Limitations (not scored)
------------------------------------------------------------
  [INFO] Punctuation after a keyword: "quiet." returned 0 spot(s) (ideal: 5 quiet spots)
  [INFO] 'wifi' spelled without a hyphen: "excellent wifi" returned 0 spot(s) (ideal: 3 spots with excellent Wi-Fi)
  [INFO] Synonym for quiet: "I need a peaceful study spot" returned 0 spot(s) (ideal: 5 quiet spots)

============================================================
Summary
============================================================
  Retrieval              10/10 passed
  Retrieval + Ranking    2/2 passed
  Seat Extraction        4/4 passed
------------------------------------------------------------
  TOTAL                  16/16 passed (100.0%)
============================================================
```

### What the Results Show

- All 16 scored cases passed, so retrieval, ranking, and seat extraction behave as expected on the current dataset.
- The **Known Limitations** section shows three real weaknesses of keyword matching: punctuation after a keyword, "wifi" spelled without a hyphen, and synonyms like "peaceful." These are reported honestly instead of being hidden, and they point to future improvements.
- If any scored case fails, the script exits with an error code, so it could also be used in an automated check before deploying changes.

## Logging

StudySync records application events and errors in:

```text
logs/studysync.log
```

The logging system tracks Gemini explanation generation, successful responses, and API errors. The `logs/` directory is generated when the application runs.

## Limitations

- The study-spot dataset contains only 10 sample locations.
- Retrieval uses keyword matching, so it may not recognize every variation of a student's request. The evaluation harness confirms that punctuation (e.g., "quiet."), the spelling "wifi," and synonyms like "peaceful" return no results.
- Study-spot information is not updated in real time.
- Gemini-generated explanations depend on the retrieved information and may still require human review. For example, Gemini once described seats as available "right now," even though the data is not real-time.
- If the typed request and the noise-level setting disagree (for example, typing "loud" while the setting is "quiet"), the ranking scores reflect the setting, not the typed request.

See [model_card.md](model_card.md) for additional information about limitations, potential misuse, reliability, and ethical considerations.

## Project Documentation

- [Model Card](model_card.md)
- [Evaluation Report](evaluation.md)
- [Architecture Diagram](diagrams/architecture.mmd)
- [Evaluation Harness](eval_harness.py)

## Future Improvements

Potential future improvements include:

- Expanding the study-spot dataset with additional locations and information sources.
- Improving retrieval to understand different ways students express similar preferences.
- Removing punctuation and normalizing spellings such as "wifi" before keyword matching.
- Adding real-time study-space availability information.
- Expanding evaluation with additional student requests and feedback.
- Detecting the noise level in the typed request so it can override or warn about a conflicting noise setting.

---

**Built as part of CodePath AI110: Foundations to AI Engineering - Project 4, Applied AI System.**