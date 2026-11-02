import json, os, re, time, torch, sys
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

WORK = Path(sys.argv[3]); WORK.mkdir(parents=True, exist_ok=True)
CONFIG = {"base_model": "Qwen/Qwen3.5-0.8B", "revision": "2fc06364715b967f1860aea9cf38778875588b17", "seed": 42,
          "num_train_epochs": 5, "warmup_steps": 6, "lr": 2e-4, "lora_r": 16, "lora_alpha": 32, "max_seq_len": 512, "max_new_tokens": 120}
terms = json.load(open(sys.argv[1], encoding="utf-8"))["terms"]
records = [json.loads(l) for l in open(sys.argv[2], encoding="utf-8")]

EVAL = [
    ("glossary", "What is lecNN-start tag?", [r"tag", r"branch"]),
    ("glossary", "What is 3 homework levels?", [r"Basic", r"Implementation", r"Advanced"]),
    ("glossary", "What is answer.md?", [r"lectures/", r"PR|pull request"]),
    ("glossary", "What is Default model?", [r"gemini-3\.5-flash-lite"]),
    ("glossary", "What is TestModel?", [r"Pydantic AI"]),
    ("glossary", "What is Pi?", [r"coding agent", r"terminal"]),
    ("paraphrase", "Which tag should I branch from if I have not finished the previous lecture's exercises?", [r"lec\w*-start"]),
    ("paraphrase", "In AIE2026, how many homework levels do I have to complete for each lecture?", [r"\b(one|1)\b"]),
    ("paraphrase", "Where do I write my exercise and homework results in this course?", [r"answer\.md"]),
    ("paraphrase", "Which model does this course use by default for exercises?", [r"flash-lite"]),
    ("paraphrase", "How can I test a Pydantic AI agent without an API key?", [r"TestModel"]),
    ("paraphrase", "Which terminal coding agent has only four built-in tools?", [r"\bPi\b"]),
    ("absent", "What is lec99-final tag?", None),
    ("absent", "What is the bonus homework level in AIE2026?", None),
    ("absent", "What is glossary_fetch_all?", None),
    ("absent", "What is the AIE2026 midterm exam?", None),
]
DECLINE = r"not (in|found|listed|defined|included|part of)|no (information|entry|such)|does not (contain|include|appear|exist)|don't know|do not know|not sure|cannot find|isn't (in|listed)|is not (a |an )?(term|defined|mentioned)"

def score(cat, ans, kws):
    if cat == "absent":
        return bool(re.search(DECLINE, ans, re.I))
    return all(re.search(k, ans, re.I) for k in kws)

STOP = set("what is the a an of in for to do does i my this course which how can should if have not be use by default with only are and or from each lecture".split())
def words(s): return {w for w in re.findall(r"[a-z0-9_.\-/]+", s.lower()) if w not in STOP and len(w) > 1}
def search(q):
    qw = words(q); best, bs = None, 0
    for t in terms:
        name = words(t["term"] + " " + " ".join(t.get("aliases", [])))
        s = 3 * len(qw & name) + len(qw & words(t["definition"]))
        if s > bs: best, bs = t, s
    return best if bs >= 3 else None

DEVICE = "cuda"
tok = AutoTokenizer.from_pretrained(CONFIG["base_model"], revision=CONFIG["revision"])
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(CONFIG["base_model"], revision=CONFIG["revision"], dtype=torch.float32).to(DEVICE)

def gen(m, messages):
    p = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    x = tok(p, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        o = m.generate(**x, max_new_tokens=CONFIG["max_new_tokens"], do_sample=False, pad_token_id=tok.pad_token_id)
    return tok.decode(o[0][x["input_ids"].shape[1]:], skip_special_tokens=True).strip()

SEARCH_SYS = "You answer questions about the AIE2026 course glossary. Use only the glossary entry given. If no entry is given or the entry does not answer the question, say that it is not in the glossary."
def run_search(m, q):
    t = search(q)
    entry = f"Glossary entry: {t['term']}: {t['definition']}" if t else "Glossary entry: (none found)"
    return gen(m, [{"role": "system", "content": SEARCH_SYS}, {"role": "user", "content": f"{entry}\n\nQuestion: {q}"}]), (t["id"] if t else None)

def evaluate(m, label, with_search=False):
    rows = []
    for cat, q, kws in EVAL:
        if with_search: a, hit = run_search(m, q)
        else: a, hit = gen(m, [{"role": "user", "content": q}]), None
        rows.append({"cond": label, "cat": cat, "q": q, "ok": score(cat, a, kws), "retrieved": hit, "answer": a})
    return rows

t0 = time.time(); before = evaluate(model, "before"); search_rows = evaluate(model, "search", True)
print("eval time", round(time.time() - t0, 1))

ds = Dataset.from_list(records)
lora = LoraConfig(r=CONFIG["lora_r"], lora_alpha=CONFIG["lora_alpha"], lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
sft = SFTConfig(output_dir=str(WORK / "ckpt"), num_train_epochs=CONFIG["num_train_epochs"], per_device_train_batch_size=4, gradient_accumulation_steps=2,
                learning_rate=CONFIG["lr"], lr_scheduler_type="cosine", warmup_steps=CONFIG["warmup_steps"], logging_steps=15, save_strategy="no",
                fp16=True, max_length=CONFIG["max_seq_len"], packing=False, report_to="none", seed=CONFIG["seed"])
trainer = SFTTrainer(model=model, args=sft, train_dataset=ds, processing_class=tok, peft_config=lora)
trainer.model.print_trainable_parameters()
t0 = time.time(); trainer.train(); train_sec = round(time.time() - t0)
tuned = trainer.model; tuned.eval()
after = evaluate(tuned, "after")
after_search = evaluate(tuned, "after+search", True)
allrows = before + search_rows + after + after_search
summary = {}
for r in allrows:
    summary.setdefault(r["cond"], {}).setdefault(r["cat"], []).append(r["ok"])
summary = {c: {k: f"{sum(v)}/{len(v)}" for k, v in d.items()} for c, d in summary.items()}
json.dump({"config": CONFIG, "train_examples": len(records), "train_seconds": train_sec,
           "final_loss": [h for h in trainer.state.log_history if "loss" in h][-1]["loss"], "summary": summary, "rows": allrows},
          open(WORK / "result_glossary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("train_seconds", train_sec); print(json.dumps(summary, indent=1))
for r in allrows: print(r["cond"], r["cat"], r["ok"], r["retrieved"], "|", r["q"], "|", r["answer"][:160].replace("\n", " "))
