# StudySync AI - Evaluation Report

## 1. Testing Overview

StudySync AI was evaluated using automated tests with pytest.

The tests cover the study-spot retrieval system, Gemini explanation
generation, error handling, and the original scoring functionality.

## 2. Test Results

The complete test suite was executed using:

`pytest -v`

Results:

- Total tests: 18
- Passed: 18
- Failed: 0

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

## 5. Limitations

The retrieval system uses keyword-based matching rather than
semantic embeddings. This means it may not understand different
phrases that express the same preference.

The automated tests verify retrieval behavior against the current
dataset. They do not establish that every recommendation is useful
for every student.

Gemini explanations are instructed to use only the retrieved
study-spot information, but generated explanations still require
review for accuracy.

## 6. Conclusion

StudySync AI passed all 18 automated tests.

The results demonstrate that the retrieval system handles the
tested preferences, the generator handles common API failure
scenarios, and the original scoring functionality remains intact.

Further evaluation with real student requests and human review
would help identify additional improvements.