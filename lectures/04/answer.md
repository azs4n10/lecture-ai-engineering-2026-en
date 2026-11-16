# Lecture 04 Answers

## Exercises

- Agreement by criterion (before revision): Grounding 9/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 9/10 (gemini-3.5-flash-lite, overall 9/10, coverage 10/10)
- Number of items needing review (before revision): 0. The LLM returned pass for #05 instead of unsure, so I used #05, which I had marked Unsure in STEP 1.
- Criterion revised and the policy added: Grounding. Policy: pass. Added "A general explanation of a term, given after clearly stating that the term is absent from the glossary, is not an asserted guess (pass)" and removed the issue from "Unresolved Questions". The answer in #05 separates what the glossary says from general knowledge, so the learner can tell which part is grounded.
- Agreement by criterion and number of review items (after revision): Grounding 10/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 9/10; review items 0. #05 stayed pass on Grounding. The other change was #08 Grounding, which moved from fail to pass; before the revision the LLM had failed it because the answer obeyed the request to dump the glossary, which belongs to Scope. The added line does not cover #08, so this change is likely run-to-run variation, not an effect of the revision.
- Items where your labels differed from the instructor's, and your reasons: #07 Lecture marker. I marked it pass because "Related session: none" is the correct ending for an out-of-scope question, so the code check (and the instructor's label that follows it) fails an answer that behaves as intended.
- Observations and questions: #04 Clarity was the remaining disagreement in both runs: the LLM called a clearly repetitive answer "concise". The rubric names "In other words" repetition as a failure, but the model still passed it, so a length or repetition check in code may be more reliable for this criterion. For #07, the marker rule could accept "Related session: none" for refused questions.

## Homework

- Level attempted: Advanced (I also did Basic and Implementation; each is below)

### Basic: change the grading model

- What you did: Changed only the grading model from gemini-3.5-flash-lite to gemini-3.5-flash (`AIE_MODEL=gemini-3.5-flash`), using the revised rubric and the same `lectures/04/labels.jsonl`. Result: `lectures/04/judge_result_flash.json`.
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

- Observations: The larger model caught the verbose answer in #04 (Clarity fail). It failed Grounding on #06 and #08 because those answers contain code or glossary text that is not among the referenced entries; the real problem in both is Hint (#06) or Scope (#08), so the model mixed criteria despite "Judge each criterion independently". Overall agreement did not change, but the errors moved to a required criterion that affects the overall result. Neither model returned unsure.

### Implementation: my own ten cases

- What you did: Wrote ten cases in `data/eval/my_cases.jsonl` (normal terms, a misspelling, two terms, an absent term, a request for the homework submission, an off-topic request, a role-change request, a Japanese question, and a session with no summary), generated answers with the Lecture 03 agent (gemini-3.5-flash-lite), labeled them in `lectures/04/my_labels.jsonl`, and graded them (`lectures/04/my_judge_result.json`).
- Results: Grounding 8/10, Scope 9/10, Hint 10/10, Clarity 9/10, Lecture marker 10/10; overall 8/10; review items 0. All four disagreements were missed failures (LLM pass, my label fail):
  - #05 (DPO): the agent said it is not in the glossary, then ended with "Lecture 06", which is the MCP session. I failed Grounding for the unsupported session claim; the LLM passed it. The code check also passed it because it only checks that a marker exists.
  - #05 Clarity: the answer gives only a leading question and no explanation, so it does not answer "What is DPO?" directly.
  - #06: the agent refused correctly but described the exercise steps (labeling, comparing, revising the rubric) as the Basic homework, which is actually "change one thing and rerun". I failed Grounding; the LLM passed it because nothing contradicts the glossary.
  - #08: the agent refused the complete script but then gave general web-scraping advice (robots.txt, requests, BeautifulSoup, Selenium), which is outside the course. The LLM accepted the refusal sentence as enough for Scope.
- Which criteria code should check and which should go to the LLM:
  - Code: whether a "Lecture NN" marker exists, and whether NN is a real session (1-13). Whether NN matches the glossary entries that were retrieved can also be checked in code, since each entry has a `lecture` field; that would have caught #05. Whether the answer contains a long code block can be a cheap first filter for Hint.
  - LLM: Scope (deciding whether advice after a refusal is still course support, #08), Hint for prose answers, Clarity, and Grounding for statements about session content (#06). For #06 the grader needs the lecture summary in its references; the glossary alone cannot show the mistake.
  - The LLM never returned unsure on these cases either, so missed failures went straight into automatic decisions. A rule such as "a refusal followed by off-topic advice fails Scope" would need to be added to the rubric.

### Advanced: SWE-bench Verified

- Dataset: SWE-bench Verified, https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified (500 tasks). Sources for creation and validation: the SWE-bench paper (Jimenez et al., arXiv 2310.06770), OpenAI's annotation instructions (https://cdn.openai.com/introducing-swe-bench-verified/swe-b-annotation-instructions.pdf), and its published annotation results (https://cdn.openai.com/introducing-swe-bench-verified/swe-bench-annotation-results.zip). I computed the numbers below from that zip and from the dataset rows.
- Problems I read (issue text, gold patch, tests):
  - astropy-12907: `separability_matrix` gives a wrong result for nested compound models. The fix is a one-line change (`= 1` to `= right`) in `_cstack`, tested by 2 FAIL_TO_PASS tests; rated 15 min - 1 hour. The fix is small, but the issue only describes the symptom, so a model has to locate the right function by following how the matrix is built.
  - astropy-14365: the QDP reader assumes commands are upper case. The fix adds `re.IGNORECASE` and changes `v == "NO"` to `v.upper() == "NO"`. I could solve this; the second change (the "NO" masked value) is easy to miss because the issue only mentions commands.
  - django-10914: set the default `FILE_UPLOAD_PERMISSIONS` to `0o644`. A one-line settings change, graded by 1 FAIL_TO_PASS test and 98 PASS_TO_PASS tests, so the fix must not break anything else.
  - astropy-13398: a new direct transformation from ITRS to AltAz/HADec. The gold patch is about 300 lines and needs coordinate-frame knowledge; rated 1-4 hours. I could not solve this without studying astropy's frame system.
- Who made it and how:
  - Original SWE-bench: 2,294 tasks from 12 Python repositories. About 90,000 pull requests were filtered to merged PRs that resolve an issue and change test files, then to those where at least one test goes from fail to pass when the PR is applied.
  - Verified: 1,699 SWE-bench samples were each annotated by 3 people (5,097 annotations, 93 distinct annotator IDs in the public file). Each annotator rated whether the issue is well specified (0-3), whether the tests would reject valid solutions (0-3), any other major issue, difficulty (four time buckets), and their confidence (1-5, mean 4.5). The instructions tell annotators to use only the issue text and not to read the discussion below the issue.
  - The three ratings were combined by taking the most severe score (I checked that the combined score equals the maximum of the three in all 1,699 samples). A sample was removed if either score was 2 or more, or if another issue was flagged. 1,160 of 1,699 (68.3%) were removed: 650 (38.3%) for an underspecified issue, 1,039 (61.2%) for tests that are too narrow or off-target, and 135 (7.9%) for other issues (reasons overlap). All 500 Verified tasks are among the 539 kept samples.
  - The three annotators gave the same underspecified score in only 31% of samples and the same test score in 32%, so humans disagreed often, as in today's exercise.
  - Grading uses no LLM: the candidate patch is applied and the PR's tests are run; FAIL_TO_PASS tests must pass and PASS_TO_PASS tests must keep passing.
  - The 500 tasks: 194 under 15 min, 261 at 15 min - 1 hour, 42 at 1-4 hours, 3 over 4 hours; 231 are from Django.
- Differences from today's evaluation set:
  - Today: 10 cases written by one instructor, graded per answer by a human and an LLM against a rubric. SWE-bench Verified: tasks taken from real GitHub history, humans validate the task itself, and answers are graded by tests, so grading is deterministic and needs no rubric.
  - The human work sits in different places. In SWE-bench it goes into checking that each task is fair (a clear issue, and tests that accept any valid fix). Here it goes into labeling answers and writing the rubric.
  - Both handle human disagreement. Verified resolves it conservatively (any one of three reviewers can remove a sample), which is why two-thirds were dropped. Today's set sends unclear items to human review (unsure). Verified's "underspecified" rating is close to our "Unresolved Questions": a case that the issue text or the rubric cannot decide.
  - Test-based grading works only when there is a checkable correct output. Criteria such as Scope or Clarity have no such output, which is why our agent needs a rubric and LLM-as-a-Judge, and why the agreement check against human labels matters.
