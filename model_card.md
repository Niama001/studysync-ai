## Limitations and Potential Biases

StudySync AI has several limitations. First, its recommendations are based on a dataset containing only 10 study spots. If a location is missing from the dataset, the system cannot recommend it.

Second, the retrieval system uses keyword-based matching instead of semantic search. This means it may not recognize different phrases that communicate the same preference. For example, a student might describe a place as "peaceful" instead of "quiet," and the system may not identify the intended match.

The recommendation results are also influenced by the existing scoring algorithm and the information available in the dataset. If the dataset is outdated or incomplete, recommendations may not reflect actual study conditions.

## Potential Misuse and Prevention

Students could rely on StudySync's recommendations as if they were guaranteed to be accurate. However, available seats, Wi-Fi quality, and noise levels may change over time.

Another potential risk is that Gemini could generate an explanation containing information that was not included in the retrieved study-spot data.

To reduce these risks, StudySync provides Gemini with only the retrieved and ranked study-spot information and explicitly instructs it not to invent features or details. The system also displays the original study-spot information and ranking reasons so students can review the information behind each recommendation.

The system should also communicate that recommendations are based on the available dataset and are not guaranteed to reflect real-time conditions.

## Reliability Testing Reflection

One thing that surprised me during testing was that Gemini could return a 503 error even when my API key and application code were configured correctly.

Initially, I thought something was wrong with my implementation. After investigating the error, I learned that the issue was temporary service unavailability rather than a problem with my code.

I added retry logic so StudySync could attempt the request again instead of immediately failing. I also tested both successful retries and situations where all three attempts failed. This helped me understand why testing AI applications requires checking not only successful responses but also how the system behaves when an external AI service is unavailable.

## Collaboration with AI

I used AI as a development assistant throughout this project to understand errors, review implementation decisions, and improve the reliability of StudySync.

One suggestion I accepted was adding retry logic to Gemini API requests. When Gemini returned a temporary 503 error, I used AI assistance to understand the error and implement a retry mechanism. I kept the retry limit to three attempts so the application would not retry indefinitely.

One approach I chose not to implement was a more complex semantic retrieval system using embeddings and a vector database. Although that could support more flexible searches, I kept the keyword-based retrieval approach because the project uses a small CSV dataset and I wanted the retrieval process to remain understandable, testable, and within the project's scope.

This experience taught me that AI suggestions should not automatically be treated as the best solution. I still need to evaluate whether a suggestion fits the project's requirements, complexity, and goals.