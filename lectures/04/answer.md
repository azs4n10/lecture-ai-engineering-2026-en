# Lecture 04 Answers

## Exercises

- Agreement by criterion (before revision): Grounding 9/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 9/10 (gemini-3.5-flash-lite, overall 9/10, coverage 10/10)
- Number of items needing review (before revision): 0. The LLM returned pass for #05 instead of unsure, so I used #05, which I had marked Unsure in STEP 1.
- Criterion revised and the policy added: Grounding. Policy: pass. Added "A general explanation of a term, given after clearly stating that the term is absent from the glossary, is not an asserted guess (pass)" and removed the issue from "Unresolved Questions". The answer in #05 separates what the glossary says from general knowledge, so the learner can tell which part is grounded.
- Agreement by criterion and number of review items (after revision): Grounding 10/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 9/10; review items 0. #05 stayed pass on Grounding. The other change was #08 Grounding, which moved from fail to pass; before the revision the LLM had failed it because the answer obeyed the request to dump the glossary, which belongs to Scope. The added line does not cover #08, so this change is likely run-to-run variation, not an effect of the revision.
- Items where your labels differed from the instructor's, and your reasons: #07 Lecture marker. I marked it pass because "Related session: none" is the correct ending for an out-of-scope question, so the code check (and the instructor's label that follows it) fails an answer that behaves as intended.
- Observations and questions: #04 Clarity was the remaining disagreement in both runs: the LLM called a clearly repetitive answer "concise". The rubric names "In other words" repetition as a failure, but the model still passed it, so a length or repetition check in code may be more reliable for this criterion. For #07, the marker rule could accept "Related session: none" for refused questions.

## Homework

- Level attempted: Basic
- What you did: Changed only the grading model from gemini-3.5-flash-lite to gemini-3.5-flash (`AIE_MODEL=gemini-3.5-flash`), using the revised rubric and the same `lectures/04/labels.jsonl`. Result saved in `lectures/04/judge_result_flash.json`.
- Results:

  | Criterion | flash-lite | flash |
  |---|---|---|
  | Grounding | 10/10 | 8/10 |
  | Scope | 10/10 | 10/10 |
  | Hint | 10/10 | 10/10 |
  | Clarity | 9/10 | 10/10 |
  | Lecture marker (code) | 9/10 | 9/10 |
  | Overall | 9/10 | 9/10 |
  | Review items | 0 | 0 |

- Observations and questions: The larger model caught the verbose answer in #04 (Clarity fail), matching my label. However, it failed Grounding on #06 and #08 because those answers contain code or glossary text that is not among the referenced entries. In both cases the real problem is Hint (#06) or Scope (#08), so the model mixed criteria despite "Judge each criterion independently". The overall agreement did not change, but the errors moved from a subjective criterion to a required one, which matters more because Grounding affects the overall pass/fail. Neither model returned unsure for any item, so coverage alone does not show whether a model is being careful.
