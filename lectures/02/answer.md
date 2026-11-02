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

- Level attempted: Basic
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
