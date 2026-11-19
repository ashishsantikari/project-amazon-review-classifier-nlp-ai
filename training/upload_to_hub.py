"""Publish the project's models to the Hugging Face Hub.

Usage (after `uv run hf auth login`):
    uv run python upload_to_hub.py            # uploads all three models
    uv run python upload_to_hub.py --dry-run  # only shows what would be uploaded

Each model gets its own public repo under your account, with a model card.
Training pickles (training_args.bin) and intermediate checkpoints are skipped.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
REPORTS = Path(__file__).resolve().parent / "reports"

LORA_CARD = """---
library_name: peft
base_model: FacebookAI/roberta-base
pipeline_tag: text-classification
language: en
tags: [sentiment-analysis, lora, product-reviews]
---

# Review sentiment - RoBERTa-base + LoRA

LoRA adapter on top of `FacebookAI/roberta-base` that classifies product reviews as
**negative / neutral / positive**.

| Metric (held-out test) | Value |
|---|---|
| Accuracy | {accuracy:.3f} |
| F1 macro | {f1_macro:.3f} |
| Precision (macro) | {precision:.3f} |
| Recall (macro) | {recall:.3f} |

**Training:** LoRA r={lora_r}, alpha={lora_alpha}, target modules {lora_target_modules},
lr {learning_rate}, max length {max_length}, up to {num_train_epochs} epochs with early stopping.

```python
from peft import AutoPeftModelForSequenceClassification
from transformers import AutoTokenizer

model = AutoPeftModelForSequenceClassification.from_pretrained("{repo_id}", num_labels=3)
tokenizer = AutoTokenizer.from_pretrained("{repo_id}")
```
"""

FULL_CARD = """---
library_name: transformers
base_model: FacebookAI/roberta-base
pipeline_tag: text-classification
language: en
tags: [sentiment-analysis, product-reviews]
---

# Review sentiment - RoBERTa-base fine-tuned

`FacebookAI/roberta-base` fully fine-tuned to classify product reviews as
**negative / neutral / positive**.

```python
from transformers import pipeline
clf = pipeline("text-classification", model="{repo_id}")
clf("The battery died after two days.")
```
"""

CATEGORY_CARD = """---
library_name: transformers
base_model: distilroberta-base
pipeline_tag: text-classification
language: en
datasets: [McAuley-Lab/Amazon-Reviews-2023]
tags: [text-classification, product-reviews, product-category]
---

# Review product category - DistilRoBERTa

Predicts the product category of an Amazon review out of {n_labels} classes:
{labels_md}.

| Metric (held-out test, n={n_test}) | Value |
|---|---|
| Accuracy | {test_accuracy:.3f} |
| F1 macro | {test_f1_macro:.3f} |

![Confusion matrix](confusion_matrix.png)

**Data:** {n_total} reviews from Amazon Reviews 2023, balanced across categories
(title + text, reviews with fewer than 8 words removed), split 80/10/10.
**Training:** `distilroberta-base`, {epochs} epochs, lr {learning_rate}, max length {max_length},
on {device} ({train_minutes} min).

```python
from transformers import pipeline
clf = pipeline("text-classification", model="{repo_id}")
clf("Comfortable couch, the cushions are firm and the fabric is easy to clean.")
```
"""


def stage(files: dict[str, Path], card: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="hub_"))
    for name, src in files.items():
        shutil.copy2(src, tmp / name)
    (tmp / "README.md").write_text(card, encoding="utf-8")
    return tmp


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=["lora", "full", "category"])
    args = ap.parse_args()

    api = HfApi()
    user = api.whoami()["name"]
    jobs = []

    lora = MODELS / "sentiment-lora"
    if lora.exists():
        repo = f"{user}/review-sentiment-roberta-lora"
        cfg = json.loads((lora / "experiment_config.json").read_text())
        res = json.loads((lora / "results.json").read_text())
        fm = lora / "final_model"
        files = {n: fm / n for n in ["adapter_config.json", "adapter_model.safetensors",
                                     "tokenizer.json", "tokenizer_config.json"]}
        files.update({"experiment_config.json": lora / "experiment_config.json",
                      "results.json": lora / "results.json"})
        jobs.append(("lora", repo, files, LORA_CARD.format(repo_id=repo, **res, **cfg)))

    full = MODELS / "roberta-base-sentiment-finetuned"
    if full.exists():
        repo = f"{user}/review-sentiment-roberta-base"
        files = {p.name: p for p in full.iterdir() if p.is_file()}
        jobs.append(("full", repo, files, FULL_CARD.format(repo_id=repo)))

    cat = MODELS / "category-distilroberta"
    if cat.exists():
        repo = f"{user}/review-category-distilroberta"
        m = json.loads((REPORTS / "metrics.json").read_text())
        files = {p.name: p for p in cat.iterdir() if p.is_file() and p.suffix != ".bin"}
        files["confusion_matrix.png"] = REPORTS / "confusion_matrix.png"
        files["metrics.json"] = REPORTS / "metrics.json"
        card = CATEGORY_CARD.format(
            repo_id=repo, n_labels=len(m["labels"]),
            labels_md=", ".join(f"`{l}`" for l in m["labels"]),
            n_total=m["n_train"] + m["n_val"] + m["n_test"], **m)
        jobs.append(("category", repo, files, card))

    for key, repo, files, card in jobs:
        if args.only and key != args.only:
            continue
        size = sum(p.stat().st_size for p in files.values()) / 1e6
        print(f"{repo}: {len(files)} files, {size:.0f} MB")
        if args.dry_run:
            continue
        folder = stage(files, card)
        api.create_repo(repo, repo_type="model", exist_ok=True)
        api.upload_folder(repo_id=repo, folder_path=str(folder),
                          commit_message="Upload model from review-intelligence project")
        shutil.rmtree(folder, ignore_errors=True)
        print(f"  -> https://huggingface.co/{repo}")


if __name__ == "__main__":
    main()
