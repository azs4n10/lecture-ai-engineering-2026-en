# Lecture 02 Answers

## Exercises

- Model and settings used (from `config` in `result.json`): `Qwen/Qwen3.5-0.8B` (revision `2fc0636`), LoRA r=16 / alpha=32, lr=2e-4, 20 epochs (40 steps), seed 42, greedy decoding, no quantization
- Did you run training yourself (`executed_training_myself`): Yes (ran sections 0–7 on a local RTX 4060 8 GB instead of Colab T4; same library pins, torch 2.11.0+cu126)
- Before training: `format_rate` = 0.952 / `content_rate` = 0.381
- After training: `format_rate` = 1.000 / `content_rate` = 0.905
- Questions that regressed: none (`regressed: []`)
- Failures remaining after training and their types (assertion without evidence / evasion through a confirmation request despite evidence being present / broken format):
  - "Can I submit a format other than PDF?" — evasion: the FAQ says one PDF file, but the model answered "This FAQ does not contain that information" with `needs_review: true`
  - "Tell me how submissions after the deadline are handled" — evasion: the FAQ covers late submissions (within 48 hours, with a penalty), but the model asked for confirmation
  - No broken format and no assertion without evidence remained
- Results of knowledge questions (section 6; classification before → after training) and observations:

  | Question | In FAQ | Before | After |
  |---|---|---|---|
  | When is the final assignment deadline for this course? | No | asserted | asserted |
  | What is the instructor's name? | No | needs_review | needs_review |
  | What is the topic of the next lecture? | No | needs_review | needs_review |
  | When is the assignment deadline? | Yes | asserted | asserted |

  The "final assignment" question is not in the FAQ, but the model answered "September 30 at 23:59" both before and after training. It looks like the model matched the word "deadline" to the FAQ entry instead of noticing that "final assignment" is a different thing. Training did not fix this judgment.
- What changed and what stayed the same with training:
  - Changed: the output became exactly one JSON line every time (before training, one answer copied the whole FAQ into `answer`), and the answer wording became fixed sentences taken from the FAQ. For questions absent from the FAQ, the model now uses the trained sentence "This FAQ does not contain that information..." with `needs_review: true`. Before training, only 1 of the 6 such questions passed: 3 got a bare "No", 1 got an answer borrowed from the office-hours item, and 1 said "not mentioned in the FAQ" without the required "Confirmation is needed".
  - Stayed the same: whether a question is really covered by the FAQ is still decided by surface wording. Two covered questions were refused, and the "final assignment" question was answered from the wrong item. The format was learned, but the judgment about what the FAQ actually says was not.

## Homework

- Level attempted: Advanced (Basic, Implementation, and Advanced were all done; each is below)

### Basic

- Settings or data changed: `lora_r` 16 → 4 (everything else unchanged, including `lora_alpha` = 32). Restarted the process and ran from the top for each setting. Result files: `result.json` (r=16) and `result_lora_r4.json` (r=4)
- Results (comparison tables or numbers):

  | | r = 16 (original) | r = 4 |
  |---|---|---|
  | trainable params | 6,389,760 (0.842%) | 1,597,440 (0.212%) |
  | format_rate (after) | 1.000 | 1.000 |
  | content_rate (after) | 0.905 | 0.905 |
  | final loss (step 40) | 0.0148 | 0.0150 |
  | train_loss (average) | 0.448 | 0.447 |
  | training time | 128 s | 59 s |
  | regressions | none | none |
  | remaining failures | 2 evasions ("other than PDF", "after the deadline") | 1 evasion ("other than PDF"), 1 assertion without evidence ("Do office hours require an appointment?" → answered with the office-hours time, `needs_review: false`) |

  Note on time: the r=16 run was the first run on this PC, so part of the difference may come from first-run overhead (loading, CUDA initialization), not only from the smaller adapter. I did not repeat the runs.

  Extra observation (not part of the one-setting comparison): in a first attempt I changed `lora_alpha` together with r (r=4, alpha=8). Then the loss went down more slowly (1.693 vs 2.283 at step 10, 0.0148 vs 0.0458 at step 40) and `content_rate` dropped to 0.810. Since the LoRA update is scaled by alpha/r, lowering alpha with r kept the scale at 2 instead of raising it to 8, and with only 40 steps this was not enough to learn the answers as well.

- Discussion of when fine-tuning is and is not suitable:
  - The scores were the same for r=16 and r=4, but the type of the remaining errors changed. With r=4, the model asserted an answer to a question that is not in the FAQ, which is the more harmful error for a FAQ bot. With 21 test questions, one question is about 5 points, so a single run cannot show whether r=4 is really worse; I would need several seeds to say that.
  - Suitable: fixing an output format (one JSON line, fixed keys), a fixed tone, or fixed sentences such as the confirmation message. These were learned in 40 steps with less than 1% of the parameters, and even 0.2% was enough.
  - Not suitable: teaching facts or the judgment of "is this really written in the FAQ". The knowledge questions did not change, and both settings still made judgment errors that depend on wording. When the FAQ content changes, the model would also need retraining. For facts, it is better to give the documents in the prompt (or search them), and to check `needs_review` with rules or a separate evaluation.

### Implementation: my own FAQ

- Data: replaced `FAQ`, `GROUNDED`, `UNGROUNDED`, `TEST_EXTRA_*` with a fictional FAQ for a ROS 2 robotics practicum course (5 items: laptop environment, robot lending, lab room and hours, final demo, team size). File: `impl_faq_data.py`. Knowledge questions in section 6 were also replaced. The JSON format, `needs_review` design, split rule, and all training settings (r=16, lr=2e-4, 20 epochs) were kept. Result file: `result_impl.json`
- How I prepared the questions "without evidence": in the original run, the remaining errors came from questions that share words with a FAQ item ("final assignment deadline" was answered with the normal deadline). So most of my questions without evidence share a keyword with one FAQ item but ask something the FAQ does not say: "Who do I contact if the robot breaks?", "Is there a rehearsal before the final demo?", "Can I use the GPU server in the lab?", "How are team members chosen?", "Can I bring my own robot?", and for test only, "How is the final demo graded?", "What should I do if my laptop cannot run ROS 2?", "Is there a fee for borrowing the robot?". I avoided questions that can be answered by reasoning from the FAQ (for example, "Can I keep the robot overnight?" is answered by "return by 18:00"), because their expected answer would be unclear. A few questions are unrelated to every item (attendance, slides, written exam).
- Results

  | | Before | After |
  |---|---|---|
  | format_rate | 1.000 | 1.000 |
  | content_rate | 0.286 | 0.905 |
  | regressions | | none |
  | training time | | 82 s, final loss 0.0121 |

  - Remaining failures after training: "Which ROS 2 distribution is used?" → evasion ("This FAQ does not contain that information", although the FAQ says Humble). "Can I bring my own robot?" → assertion without evidence (answered with the TurtleBot lending rule, `needs_review: false`). Both are wording-based errors: "distribution" does not appear in the FAQ, and "robot" does.
  - Knowledge questions: "When is the midterm demo?" was asserted before training ("December 18 from 13:00", taken from the final demo) and changed to needs_review after training. The other two questions absent from the FAQ were needs_review both times, and the control question was answered correctly.
  - Before training, many failures were scoring artifacts of short answers: "Room 305" for "Which room is the robot lab?" was correct but missed the keyword "10:00". After training, the model always copies the whole FAQ sentence, so it passes keyword checks more easily. Part of the jump from 0.286 to 0.905 is this effect, not better judgment.
- Observation: with my own data the same pattern as the original FAQ appeared. Training fixed the output style and the fixed confirmation sentence, but the remaining errors were still decided by whether the question shares a word with a FAQ item. Writing near-miss questions on purpose was the most useful part of making the data, because they are the questions that real users would ask and that the model gets wrong.

### Advanced: training on the course glossary vs. searching it

- What I did (`glossary_sft_experiment.py`, result: `result_glossary.json`):
  - Made 116 Q&A records in `messages` format with `scripts/make_sft_dataset.py` (58 terms × 2 templates: "What is {term}?", "Briefly explain {term}.")
  - Trained the same model with the same LoRA settings (r=16, alpha=32, lr=2e-4) for 5 epochs (75 steps, 108 s). Final loss 0.290, so the definitions were not fully memorized
  - Evaluation questions (16, written by me): 6 glossary terms in the training wording (course-specific terms such as lecNN-start tag, answer.md, TestModel, Pi), 6 paraphrased questions about the same terms ("Which tag should I branch from if I have not finished the previous lecture's exercises?"), and 4 terms absent from the glossary ("What is lec99-final tag?", "What is the bonus homework level in AIE2026?", "What is glossary_fetch_all?", "What is the AIE2026 midterm exam?"). For absent terms the expected answer is to say it is not in the glossary
  - Search mechanism for comparison: a simple word-overlap search over term, aliases, and definition. The top entry (or "none found") is put in the prompt with the instruction "use only this entry; if it does not answer the question, say it is not in the glossary". No training
  - 4 conditions: base model, base + search, trained model, trained + search. Greedy decoding
- Results (I graded every answer by hand against the glossary; the automatic keyword score in the JSON gave false passes, for example "There are 5 homework levels ... Complete one" matched the keyword "one")

  | Condition | Glossary wording (6) | Paraphrase (6) | Absent term (4): said "not in glossary" |
  |---|---|---|---|
  | Base model | 0 | 0 | 0 |
  | Base + search | 5 | 2 | 4 |
  | Trained | 1 | 0 | 0 |
  | Trained + search | 5 | 4 | 0 |

  - Base model: answered from general knowledge (lecNN-start tag became a "protein tag", Pi became the number π)
  - Trained: the answers now sound like the course ("A Git tag on the starting code for each lecture's exercises...") but the details are invented: "three levels: Basic, Further reading, and Exercise", "There are 5 homework levels", "Cursor has only four built-in tools". Only "Default model" was fully correct
  - Absent terms after training: every one was answered with a confident course-style definition ("The AIE2026 midterm exam ... graded as 20% of the final grade"). Even with search returning "none found" and the instruction to say so, the trained model still invented definitions. The base model with search declined all 4
  - Search failures were retrieval failures: "Default model" retrieved the LLM entry, "Where do I write my results?" retrieved the homework-levels entry, and then the answer was wrong or a refusal
- Advantages and disadvantages of training compared with search:
  - Advantages: the style becomes the course style, and it can combine well with search (trained + search was the best on paraphrases, 4/6). No retrieval step is needed when the question matches the training wording closely, and the prompt stays short
  - Disadvantages: 5 epochs on 116 records did not store the facts reliably, and paraphrases failed. The worst problem is that training removed the ability to say "I don't know": fluent, course-like invented answers are harder to notice than the base model's obviously unrelated answers. Updating a definition requires retraining, while search only needs the glossary file edited
  - Conclusion: for a glossary or FAQ that changes, search is the main mechanism, and the quality depends on retrieval. If training is added, the training data must include "not in the glossary" examples for absent terms; otherwise the model learns that every question has a confident answer
