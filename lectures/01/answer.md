# Lecture 01 Answers

## Exercises

- Model's answer to the course-specific question (the 3 homework levels; a summary is fine): with `gemini-3.5-flash-lite` (default settings), the first run produced a general explanation of LoRA for "What is LoRA?", which was broadly correct. For "What are the 3 homework levels in the AIE2026 course?", the answer changed between runs: sometimes "I do not have access to specific information about the AIE2026 course", and sometimes a confident list such as "Level 1: Core / Basics, Level 2: Intermediate / Application, Level 3: Advanced / Challenge".
- What you noticed when comparing it with the correct meaning in the glossary: the glossary (`homework-levels`) says the levels are Basic (review lecture content), Implementation (write your own code), and Advanced (research and experimentation), that completing any one level completes the homework, and that it is not graded as a rule. The invented lists look similar because "basic / intermediate / advanced" is a common pattern, but none of them said that one level is enough or that the homework is not graded. The model fills the gap with a plausible general pattern and presents it as a fact about this course.
- Token counts you displayed (input / output): "What is LoRA?" 6 / 657; "What are the 3 homework levels in the AIE2026 course?" 18 / 77–283 (depending on the run). I added the display in `app/ask.py` using `response.usage_metadata.prompt_token_count` and `candidates_token_count`.

## Homework

- Level attempted: Basic
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
