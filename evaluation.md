# StudySync AI - Evaluation Report

## 1. Testing Overview

StudySync AI was evaluated in two ways:

1. **Automated tests** using pytest, covering the study-spot retrieval system, Gemini explanation generation, error handling, and the original scoring functionality.
2. **Manual end-to-end runs** in the Streamlit app, used to check each guardrail and review Gemini's real explanations.

## 2. Test Results

The complete test suite was executed using:

```bash
pytest -v
```

Results:

- Total tests: 18
- Passed: 18
- Failed: 0

The tests pass with or without a `.env` file, because all Gemini calls in the tests are mocked.

### Test Breakdown

| Component | Tests Passed |
|---|---:|
| Gemini Generator | 5 |
| Study-Spot Retriever | 11 |
| Original Scoring System | 2 |
| Total | 18 |

## 3. Retrieval Evaluation

The retrieval system was tested with different student requests.

| Test Scenario | Expected Result | Outcome |
|---|---|---|
| Quiet study spot | Only quiet locations | Passed |
| Loud study spot | Only loud locations | Passed |
| Excellent Wi-Fi | All matching locations | Passed |
| Quiet + excellent Wi-Fi | Innovation Commons | Passed |
| Minimum seat requirement | Only locations meeting the requirement | Passed |
| No matching results | Empty result list | Passed |
| Conflicting requirements | Empty result list | Passed |

## 4. Gemini Reliability Evaluation

The Gemini generator was tested using mocked API responses.

Tests verified that:

- A successful response is returned correctly.
- Empty recommendations produce a helpful message.
- A missing API key raises an error.
- A temporary 503 error triggers a retry.
- Repeated API failures raise an error after three attempts.

All five generator tests passed.

## 5. Guardrail Examples

These examples were run manually in the **AI Study Spot Advisor** tab with `streamlit run app.py`. Preference settings: noise = `quiet`, distance = `1.0`, seats = `4`.

### Guardrail 1: Empty Request Validation

**Input:**

```text
(text box left empty, then "Find study spots" clicked)
```

**Behavior:** `rag/ui.py` checks `if not query.strip()` before loading data or calling Gemini.

**Result:**

```text
Please describe the study spot you need.
```

No retrieval, ranking, or Gemini call was made, so no API usage was wasted on an empty request.

---

### Guardrail 2: No Matching Results

**Input:**

```text
I need a quiet study spot with at least 100 seats
```

**Behavior:** `extract_min_seats()` pulled out `100` as the minimum seat requirement. No spot in the dataset has 100 seats, so retrieval returned an empty list. The UI stopped before calling Gemini.

**Result:**

```text
No study spots matched your request. Try changing your search.
```

Because Gemini never received an empty list, it had no chance to invent a study spot that does not exist.

---

### Guardrail 3: Missing API Key

**Input:**

```text
I need a quiet study spot
```

(Run with the `.env` file temporarily renamed to `.env.bak`.)

**Behavior:** Retrieval and ranking ran normally, because they do not need the API. `generate_study_spot_explanation()` then detected the missing key and raised a `ValueError`, which the UI caught and displayed.

**Result:**

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
Something went wrong: Gemini API key not found. Check your .env file.
```

The app **degraded gracefully**: the student still received the ranked recommendations, and only the AI explanation was unavailable. The app did not crash.

---

### Guardrail 4: Retry After a Real Gemini 503 Error

**Input:**

```text
I need a study spot with excellent Wi-Fi
```

**Behavior:** During this real run, Gemini returned a `503 Service Unavailable` error because of high demand. The generator logged the error, waited 2 seconds, and retried. The second attempt succeeded.

**Result (from `logs/studysync.log`):**

```text
2026-11-17 00:22:37,986 - INFO - Starting Gemini explanation generation.
2026-11-17 00:22:42,665 - INFO - HTTP Request: POST https://generativelanguage.googleapis.com/v1/models/gemini-3.8-flash:generateContent "HTTP/1.1 503 Service Unavailable"
2026-11-17 00:22:42,666 - ERROR - Gemini API error: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
2026-11-17 00:22:44,667 - INFO - AFC is enabled with max remote calls: 10.
2026-11-17 00:23:08,945 - INFO - HTTP Request: POST https://generativelanguage.googleapis.com/v1/models/gemini-3.8-flash:generateContent "HTTP/1.1 200 OK"
2026-11-17 00:23:08,947 - INFO - Gemini successfully generated an explanation.
```

The student saw a normal AI explanation and never saw the 503 error. Without the retry logic, this request would have failed. The retry is limited to 3 attempts so the app never retries forever (verified by `test_generate_explanation_fails_after_three_attempts`).

---

### Guardrail 5: Grounded Prompt (Output Guardrail)

**Input:**

```text
I need a quiet study spot with at least 10 seats
```

**Behavior:** The prompt in `rag/generator.py` sends Gemini only the retrieved and ranked spots and instructs it to "use only the information provided" and "not invent features, amenities, or details."

**Result:** Gemini's explanation mentioned only noise level, distance, Wi-Fi quality, seats, and ranking reasons, all taken from the dataset. It did not invent outlets, food, opening hours, or other amenities. (Full output in the README's [Sample Interactions](README.md#sample-interactions).)

### Guardrail Summary

| Guardrail | Input | Result | Improves Reliability By |
|---|---|---|---|
| Empty request validation | Empty text box | Warning shown, no processing | Preventing wasted API calls |
| No matching results | "at least 100 seats" | Friendly "no matches" message | Preventing Gemini from explaining spots that don't exist |
| Missing API key | Any request, no `.env` | Rankings shown + clear error | Graceful degradation instead of a crash |
| 503 retry | Real request during high demand | Retried after 2s, succeeded | Recovering from temporary outages automatically |
| Grounded prompt | Any request | Only dataset facts used | Reducing hallucinated details |

## 6. Human Review of Gemini Output

Three real requests were reviewed manually (see the README's Sample Interactions):

| Request | Invented details? | Notes |
|---|---|---|
| Quiet spot with at least 10 seats | None found | All details matched the dataset |
| Excellent Wi-Fi | None found | Correctly explained why moderate-noise spots scored lower |
| Loud study spot | One small overclaim | Correctly pointed out the "too loud" ranking conflict, but ended with "seats available right now," which the non-real-time dataset cannot confirm |

**Finding:** The grounded prompt prevented invented amenities in all three runs, but Gemini can still add small time-related claims. Human review is still needed.

## 7. Limitations

The retrieval system uses keyword-based matching rather than semantic embeddings. This means it may not understand different phrases that express the same preference.

The automated tests verify retrieval behavior against the current dataset. They do not establish that every recommendation is useful for every student.

Gemini explanations are instructed to use only the retrieved study-spot information, but generated explanations still require review for accuracy, as shown by the "right now" overclaim above.

## 8. Conclusion

StudySync AI passed all 18 automated tests and five manually verified guardrail checks, including a real Gemini 503 error that the retry logic recovered from.

The results demonstrate that the retrieval system handles the tested preferences, the generator handles common API failure scenarios, the app degrades gracefully without an API key, and the original scoring functionality remains intact.

Further evaluation with real student requests and human review would help identify additional improvements.