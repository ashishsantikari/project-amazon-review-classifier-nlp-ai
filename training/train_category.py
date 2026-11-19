"""Fine-tune distilroberta-base to classify a review into a product category.

Input : data/reviews.csv  (from prepare_data.py)
Output: ../models/category-distilroberta/   model the app picks up automatically
        reports/                            metrics.json, classification report,
                                            confusion matrix
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from datasets import ClassLabel, Dataset
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             classification_report, confusion_matrix, f1_score)
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          DataCollatorWithPadding, Trainer, TrainingArguments,
                          set_seed)

BASE_MODEL = "distilroberta-base"
MAX_LENGTH = 128
EPOCHS = 3
LR = 3e-5
BATCH = 32
SEED = 42

HERE = Path(__file__).parent
DATA = HERE / "data" / "reviews.csv"
OUT_MODEL = HERE.parent / "models" / "category-distilroberta"
REPORTS = HERE / "reports"
CKPT = HERE / "checkpoints"


def main() -> None:
    set_seed(SEED)
    use_gpu = torch.cuda.is_available()
    print(f"torch {torch.__version__} | device: "
          f"{torch.cuda.get_device_name(0) if use_gpu else 'CPU'}")

    df = pd.read_csv(DATA)
    labels = sorted(df["label"].unique())
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}
    df["label"] = df["label"].map(label2id)

    ds = Dataset.from_pandas(df, preserve_index=False)
    ds = ds.cast_column("label", ClassLabel(names=labels))
    # 80 / 10 / 10 stratified split
    tmp = ds.train_test_split(test_size=0.2, stratify_by_column="label", seed=SEED)
    val_test = tmp["test"].train_test_split(test_size=0.5, stratify_by_column="label", seed=SEED)
    splits = {"train": tmp["train"], "val": val_test["train"], "test": val_test["test"]}
    print({k: len(v) for k, v in splits.items()})

    tok = AutoTokenizer.from_pretrained(BASE_MODEL)
    enc = {k: v.map(lambda b: tok(b["text"], truncation=True, max_length=MAX_LENGTH),
                    batched=True, remove_columns=["text"])
           for k, v in splits.items()}

    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=len(labels), id2label=id2label, label2id=label2id)

    def compute_metrics(p):
        preds = np.argmax(p.predictions, axis=-1)
        return {"accuracy": accuracy_score(p.label_ids, preds),
                "f1_macro": f1_score(p.label_ids, preds, average="macro")}

    args = TrainingArguments(
        output_dir=str(CKPT),
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        per_device_train_batch_size=BATCH,
        per_device_eval_batch_size=BATCH * 2,
        warmup_ratio=0.06,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        fp16=use_gpu,
        logging_steps=100,
        report_to="none",
        seed=SEED,
        dataloader_num_workers=0,  # Windows-friendly
    )
    trainer = Trainer(model=model, args=args, train_dataset=enc["train"],
                      eval_dataset=enc["val"], tokenizer=tok,
                      data_collator=DataCollatorWithPadding(tok),
                      compute_metrics=compute_metrics)

    t0 = time.time()
    trainer.train()
    train_minutes = (time.time() - t0) / 60

    # Final evaluation on the held-out test set
    pred = trainer.predict(enc["test"])
    y_true, y_pred = pred.label_ids, np.argmax(pred.predictions, axis=-1)
    metrics = {
        "base_model": BASE_MODEL,
        "test_accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "test_f1_macro": round(float(f1_score(y_true, y_pred, average="macro")), 4),
        "n_train": len(splits["train"]), "n_val": len(splits["val"]), "n_test": len(splits["test"]),
        "epochs": EPOCHS, "learning_rate": LR, "max_length": MAX_LENGTH,
        "train_minutes": round(train_minutes, 1),
        "device": torch.cuda.get_device_name(0) if use_gpu else "cpu",
        "labels": labels,
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "metrics.json").write_text(json.dumps(metrics, indent=2))
    report = classification_report(y_true, y_pred, target_names=labels, digits=3)
    (REPORTS / "classification_report.txt").write_text(report)

    cm = confusion_matrix(y_true, y_pred, normalize="true")
    fig, ax = plt.subplots(figsize=(10, 9))
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(
        ax=ax, cmap="Blues", values_format=".2f", xticks_rotation=45, colorbar=False)
    ax.set_title(f"Category classifier - test accuracy {metrics['test_accuracy']:.1%}")
    fig.tight_layout()
    fig.savefig(REPORTS / "confusion_matrix.png", dpi=130)

    OUT_MODEL.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(OUT_MODEL))
    tok.save_pretrained(str(OUT_MODEL))

    print(report)
    print(json.dumps(metrics, indent=2))
    print(f"Model saved to {OUT_MODEL}")


if __name__ == "__main__":
    main()
