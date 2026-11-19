# Lecture 01 Answers

## Exercises

- Model's answer to the course-specific question (the 3 homework levels; a summary is fine): with `gemini-3.5-flash-lite` (default settings), the first run produced a general explanation of LoRA for "What is LoRA?", which was broadly correct. For "What are the 3 homework levels in the AIE2026 course?", the answer changed between runs: sometimes "I do not have access to specific information about the AIE2026 course", and sometimes a confident list such as "Level 1: Core / Basics, Level 2: Intermediate / Application, Level 3: Advanced / Challenge".
- What you noticed when comparing it with the correct meaning in the glossary: the glossary (`homework-levels`) says the levels are Basic (review lecture content), Implementation (write your own code), and Advanced (research and experimentation), that completing any one level completes the homework, and that it is not graded as a rule. The invented lists look similar because "basic / intermediate / advanced" is a common pattern, but none of them said that one level is enough or that the homework is not graded. The model fills the gap with a plausible general pattern and presents it as a fact about this course.
- Token counts you displayed (input / output): "What is LoRA?" 6 / 657; "What are the 3 homework levels in the AIE2026 course?" 18 / 77–283 (depending on the run). I added the display in `app/ask.py` using `response.usage_metadata.prompt_token_count` and `candidates_token_count`.

## Homework

- Level attempted: Advanced (Basic was done first; both are below)

### Basic

- What you did:
  - Added an `AIE_TEMPERATURE` environment variable to `app/ask.py` (passed as `config={"temperature": ...}` to `generate_content`; unset means the model default)
  - Asked 2 questions, 3 times each, under 3 conditions (18 calls in total, 5 seconds apart):
    - `gemini-3.5-flash-lite`, temperature 0
    - `gemini-3.5-flash-lite`, temperature 2.0
    - `gemini-3.5-flash`, model default temperature
  - Questions: "What are the 3 homework levels in the AIE2026 course?" (course-specific) and "What is LoRA?" (general term)
  - Ran on a local PC (Windows, Python 3.13, `google-genai` 2.31.0 as in `uv.lock`) instead of Codespaces
- Results:

  Course-specific question (correct answer: `homework-levels` in `data/glossary.json`)

  | Condition | Run 1 | Run 2 | Run 3 | Output tokens |
  |---|---|---|---|---|
  | flash-lite, temperature 0 | "I do not have access" | "I do not have access" | invented 3 levels | 77 / 83 / 225 |
  | flash-lite, temperature 2.0 | "I do not have access" | invented 3 levels | "I do not have access" | 79 / 283 / 95 |
  | flash, default | invented 3 levels | asks for the institution, then gives "typical" 3 levels | invented 3 levels, attributed to "AI Vietnam and similar programs" | 275 / 257 / 332 |

  General question ("What is LoRA?")

  | Condition | Output tokens (3 runs) | Content |
  |---|---|---|
  | flash-lite, temperature 0 | 755 / 687 / 767 | all 3 explain Low-Rank Adaptation correctly; headings and examples differ |
  | flash-lite, temperature 2.0 | 657 / 627 / 736 | all 3 correct; no visible drop in quality |
  | flash, default | 865 / 821 / 924 | all 3 correct and longer; one run also noted that "LoRa" in networking means Long Range |

- Observations and questions:
  - Even with temperature 0, the 3 answers were not identical. For the course-specific question, 2 runs said "I do not know" and 1 run invented an answer. So temperature 0 does not make the output reproducible here, and it does not stop the model from making things up.
  - Temperature 2.0 did not make the general answer worse in an obvious way. The difference between conditions was much smaller than the difference between questions: for the general term all 9 answers were correct, while for the course-specific question no answer gave the correct content (the "I do not know" answers were honest, but not useful).
  - The larger model (`gemini-3.5-flash`) never said "I do not know". It gave longer, more confident answers, and once named a source that has nothing to do with this course. A more capable model was not safer for questions outside its knowledge.
  - Question: why does temperature 0 still give different answers? I guess it comes from the serving side (for example, batching or non-deterministic GPU computation), but I have not checked this.

### Advanced: response time, token counts, and the free-tier limits

- What I did:
  - `app/ask.py` now also prints the response time (`time.perf_counter()` around `generate_content`) and the thinking tokens (`usage_metadata.thoughts_token_count`)
  - 2 models × 3 questions × 3 runs, 4–5 seconds apart, model default temperature. I ran the whole set twice (the first set did not record thinking tokens yet), so most cells have 6 runs
  - Questions: "What does LoRA stand for? Answer in five words or fewer." (very short answer), the course-specific homework-levels question (medium), and "What is LoRA?" (long)

- Results (time is the wall-clock time of the `generate_content` call)

  | Model | Question | Runs | Time (s), min–max (mean) | Output tokens | Thinking tokens |
  |---|---|---|---|---|---|
  | gemini-3.5-flash-lite | short | 6 | 0.72–1.72 (1.08) | 4–5 | 0 |
  | gemini-3.5-flash-lite | homework levels | 6 | 0.81–1.68 (1.31) | 34–333 | 0 |
  | gemini-3.5-flash-lite | What is LoRA? | 6 | 3.07–3.70 (3.27) | 681–802 | 0 |
  | gemini-3.5-flash | short | 6 | 2.08–2.38 (2.26) | 4–5 | 244, 247, 318 |
  | gemini-3.5-flash | homework levels | 6 | 6.27–8.63 (7.17) | 291–467 | 819, 1026, 906 |
  | gemini-3.5-flash | What is LoRA? | 4 | 9.40–10.81 (9.99) | 825–915 | 991 |

  Input tokens were 6–18 for every question, so input size did not matter here.

- Rate limit I actually hit: after about 20 requests to `gemini-3.5-flash` today (including the Basic runs), every call returned 429 `RESOURCE_EXHAUSTED`. The error said: "Generate content requests per day limit exceeded on Free Tier", `limit: 20`, `model: gemini-3.6-flash`, quota id `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, "retry in 1h21m" (about 17:00 JST, which matches the documented reset at midnight Pacific time). One probe request about 75 seconds later went through, so the counting does not seem to be exact. `gemini-3.5-flash-lite` did not return 429 in about 45 requests today. The official page (ai.google.dev/gemini-api/docs/rate-limits) does not list free-tier numbers; it points to AI Studio and says limits are per project, not per API key, and are counted as RPM, input TPM, and RPD.

- Discussion:
  - Response time follows the number of generated tokens, not the question. For flash-lite, the "What is LoRA?" answers took about 3.3 s for about 740 tokens (about 220 tokens/s), while a 4-token answer still took about 0.7–1 s. So there is a fixed cost of under 1 s per request plus a per-token cost.
  - `gemini-3.5-flash` is a thinking model. Even for a 4-word answer, it spent 244–318 hidden thinking tokens and took about 2.3 s. If I count output + thinking tokens, its speed is about 160–185 tokens/s, close to flash-lite. Most of the extra time comes from thinking tokens that are not visible in the answer. The token count shown in the answer underestimates the real work, so `candidates_token_count` alone is not enough to estimate cost or time.
  - The limit I hit was requests per day, not tokens. A request with 6 input tokens counts the same as a long one. With 20 requests per day, `gemini-3.5-flash` on the free tier could not serve even one class of students asking one question each. For a Q&A bot I would use flash-lite on the free tier, send several questions in one request when possible, cache answers to repeated questions, and handle 429 with a wait and retry. When the answer quality of flash is really needed, a paid tier is necessary.
  - For this homework itself, the limit was the main constraint: repeating the experiment for more runs or more questions with `gemini-3.5-flash` was not possible today, so the flash "What is LoRA?" cell has only 4 runs and 1 thinking-token value.
