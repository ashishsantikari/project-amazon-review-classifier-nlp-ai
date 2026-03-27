from __future__ import annotations

import importlib.util
import json
import logging
import os
import sys
import time
import yaml
from pathlib import Path
from threading import Lock
from typing import Any, cast


def _load_clean_text(model_dir: Path):
    """Import clean_text from the pipeline.py co-located with the model."""
    pipeline_file = model_dir / "pipeline.py"
    if not pipeline_file.exists():
        # Fallback: basic whitespace normalisation
        def clean_text(text: str) -> str:
            return " ".join(str(text).lower().split())
        return clean_text
    spec = importlib.util.spec_from_file_location("_model_pipeline", pipeline_file)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.clean_text


def _load_id2label(model_dir: Path) -> dict[int, str]:
    """Read id2label from experiment_config.json or fall back to defaults."""
    cfg_path = model_dir / "experiment_config.json"
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
            raw = cfg.get("id2label", {})
            return {int(k): v for k, v in raw.items()}
        except Exception:
            pass
    return {0: "negative", 1: "neutral", 2: "positive"}


class ModelManager:
    def __init__(self, model_root: str = "/models", idle_seconds: int = 180) -> None:
        self.logger = logging.getLogger(__name__)
        self.model_root = Path(model_root)
        self.idle_seconds = idle_seconds
        self._loaded: dict[str, Any] = {}
        self._last_used: dict[str, float] = {}
        self._model_names: dict[str, str] = {}
        self._lock = Lock()
        self.verbose = os.getenv("MODEL_MANAGER_VERBOSE", "false").lower() in {"1", "true", "yes", "on"}

        yaml_path = Path(__file__).parent / "models.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r") as f:
                self.models_config = yaml.safe_load(f).get("models", {})
        else:
            self.models_config = {}

        if self.verbose:
            self.logger.setLevel(logging.INFO)
            self.logger.info(
                "ModelManager initialized | model_root=%s idle_seconds=%s",
                str(self.model_root),
                self.idle_seconds,
            )

    def _vdebug(self, msg: str, *args: Any) -> None:
        if self.verbose:
            self.logger.info(msg, *args)

    def _load_transformer_pipeline(self, task_name: str, model_dir_path: Path) -> Any:
        self._vdebug("Loading local transformer pipeline | task=%s model_dir=%s", task_name, str(model_dir_path))
        try:
            from transformers import pipeline as hf_pipeline
        except Exception as exc:
            self.logger.exception("Failed importing transformers pipeline for local model: %s", exc)
            return None

        if not model_dir_path.exists():
            self.logger.warning("Local model path does not exist: %s", str(model_dir_path))
            return None

        try:
            return hf_pipeline(cast(Any, task_name), model=str(model_dir_path), tokenizer=str(model_dir_path))
        except Exception as exc:
            self.logger.exception("Failed loading local transformer pipeline from %s: %s", str(model_dir_path), exc)
            return None

    def _load_transformer_pipeline_by_id(self, task_name: str, model_id: str) -> Any:
        self._vdebug("Loading hub transformer pipeline | task=%s model_id=%s", task_name, model_id)
        try:
            from transformers import pipeline as hf_pipeline
        except Exception as exc:
            self.logger.exception("Failed importing transformers pipeline for hub model: %s", exc)
            return None

        try:
            return hf_pipeline(cast(Any, task_name), model=model_id, tokenizer=model_id)
        except Exception as exc:
            self.logger.exception("Failed loading hub transformer pipeline for model_id=%s: %s", model_id, exc)
            return None

    def _load_local_sentiment_bundle(self, model_dir_path: Path) -> Any:
        """Load a LoRA adapter from final_model/ inside model_dir_path.

        The adapter is applied on top of the base model declared in
        adapter_config.json (base_model_name_or_path).  The tokenizer is
        loaded from the same final_model/ directory.
        """
        adapter_dir = model_dir_path / "final_model"
        self._vdebug("Loading LoRA sentiment bundle | adapter_dir=%s", str(adapter_dir))
        try:
            import torch
            from peft import AutoPeftModelForSequenceClassification
            from transformers import AutoTokenizer
        except Exception as exc:
            self.logger.exception("Failed importing peft/transformers/torch: %s", exc)
            return None

        if not adapter_dir.exists():
            self.logger.warning("LoRA adapter directory not found: %s", str(adapter_dir))
            return None

        try:
            id2label = _load_id2label(model_dir_path)
            label2id = {v: k for k, v in id2label.items()}
            num_labels = len(id2label)

            tokenizer = AutoTokenizer.from_pretrained(str(adapter_dir))
            model = AutoPeftModelForSequenceClassification.from_pretrained(
                str(adapter_dir),
                num_labels=num_labels,
                id2label=id2label,
                label2id=label2id,
            )
            model.eval()
            clean_text_fn = _load_clean_text(model_dir_path)
            self._vdebug(
                "LoRA bundle loaded | num_labels=%d id2label=%s tokenizer=%s",
                num_labels,
                id2label,
                tokenizer.__class__.__name__,
            )
            return {
                "tokenizer": tokenizer,
                "model": model,
                "torch": torch,
                "clean_text": clean_text_fn,
                "id2label": id2label,
            }
        except Exception as exc:
            self.logger.exception("Failed loading LoRA sentiment bundle from %s: %s", str(adapter_dir), exc)
            return None

    def _load_local_sentiment_full(self, model_dir_path: Path) -> Any:
        self._vdebug("Loading full sentiment bundle | model_dir=%s", str(model_dir_path))
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except Exception as exc:
            self.logger.exception("Failed importing transformers/torch: %s", exc)
            return None

        if not model_dir_path.exists():
            self.logger.warning("Sentiment model directory not found: %s", str(model_dir_path))
            return None

        try:
            id2label = _load_id2label(model_dir_path)
            label2id = {v: k for k, v in id2label.items()}
            num_labels = len(id2label)

            tokenizer = AutoTokenizer.from_pretrained(str(model_dir_path))
            model = AutoModelForSequenceClassification.from_pretrained(
                str(model_dir_path),
                num_labels=num_labels,
                id2label=id2label,
                label2id=label2id,
            )
            model.eval()
            clean_text_fn = _load_clean_text(model_dir_path)
            self._vdebug(
                "Full sentiment bundle loaded | num_labels=%d id2label=%s tokenizer=%s",
                num_labels,
                id2label,
                tokenizer.__class__.__name__,
            )
            return {
                "tokenizer": tokenizer,
                "model": model,
                "torch": torch,
                "clean_text": clean_text_fn,
                "id2label": id2label,
            }
        except Exception as exc:
            self.logger.exception("Failed loading full sentiment bundle from %s: %s", str(model_dir_path), exc)
            return None

    def _iter_model_dirs(self) -> list[Path]:
        """Discover model directories.

        Accepts both:
        - Merged checkpoints: directory with config.json + tokenizer.json at root.
        - LoRA adapters: directory with a final_model/adapter_config.json inside.
        """
        if not self.model_root.exists() or not self.model_root.is_dir():
            self.logger.warning("Model root is missing or not a directory: %s", str(self.model_root))
            return []

        out: list[Path] = []
        for p in self.model_root.iterdir():
            if not p.is_dir():
                continue
            is_merged = (p / "config.json").exists() and (p / "tokenizer.json").exists()
            is_lora = (p / "final_model" / "adapter_config.json").exists()
            if is_merged or is_lora:
                out.append(p)
        self._vdebug("Discovered %s candidate model directories under %s", len(out), str(self.model_root))
        return out

    def _resolve_model_dir(self, env_var: str, keyword: str) -> Path | None:
        configured = os.getenv(env_var)
        if configured:
            candidate = self.model_root / configured
            if candidate.exists() and candidate.is_dir():
                self._vdebug("Using configured model directory | env=%s dir=%s", env_var, str(candidate))
                return candidate
            self.logger.warning(
                "Configured model directory not found | env=%s value=%s root=%s",
                env_var,
                configured,
                str(self.model_root),
            )

        all_dirs = self._iter_model_dirs()
        matches = [p for p in all_dirs if keyword in p.name.lower()]

        # If no name-match, fall back to any LoRA SEQ_CLS adapter (for sentiment)
        if not matches and keyword == "sentiment":
            lora_sentiment = []
            for p in all_dirs:
                adapter_cfg = p / "final_model" / "adapter_config.json"
                if adapter_cfg.exists():
                    try:
                        cfg = json.loads(adapter_cfg.read_text())
                        if cfg.get("task_type") == "SEQ_CLS":
                            lora_sentiment.append(p)
                    except Exception:
                        pass
            if lora_sentiment:
                matches = lora_sentiment
                self._vdebug(
                    "No name-match for '%s'; using LoRA SEQ_CLS fallback: %s",
                    keyword,
                    [p.name for p in matches],
                )

        if not matches:
            self.logger.warning("No model directory matches keyword '%s' under %s", keyword, str(self.model_root))
            return None

        # Prefer the most recently modified matching model.
        selected = sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        self._vdebug("Auto-selected model directory | keyword=%s dir=%s", keyword, str(selected))
        return selected

    def _normalize_sentiment_label(self, raw_label: str) -> str:
        label = raw_label.lower().strip()
        if label in {"label_0", "0"}:
            return "negative"
        if label in {"label_1", "1"}:
            return "neutral"
        if label in {"label_2", "2"}:
            return "positive"
        if "pos" in label:
            return "positive"
        if "neg" in label:
            return "negative"
        if "neu" in label:
            return "neutral"
        return "neutral"

    def get_sentiment_model(self, model_option: str):
        cache_key = model_option
        with self._lock:
            model = self._loaded.get(cache_key)
            if model is None:
                self._vdebug("Sentiment model cache miss | option=%s cache_key=%s", model_option, cache_key)
                cfg = self.models_config.get(model_option, {})
                if not cfg:
                    self.logger.error("Model option '%s' not found in models.yaml", model_option)
                    return None
                    
                model_type = cfg.get("type")
                if model_type == "hub":
                    model_name = os.getenv(cfg.get("env_var", ""), cfg.get("hub_id"))
                    model = self._load_transformer_pipeline_by_id(
                        task_name="text-classification",
                        model_id=model_name,
                    )
                    self._model_names[cache_key] = model_name if model is not None else cfg.get("fallback_name", "unknown")
                elif model_type in ("full", "lora"):
                    model_dir = self._resolve_model_dir(cfg.get("env_var", ""), cfg.get("keyword", ""))
                    if model_type == "full":
                        model = self._load_local_sentiment_full(model_dir) if model_dir is not None else None
                    else:
                        model = self._load_local_sentiment_bundle(model_dir) if model_dir is not None else None
                    self._model_names[cache_key] = model_dir.name if model_dir is not None else cfg.get("fallback_name", "unknown")
                else:
                    self.logger.error("Unknown model type '%s' for option '%s'", model_type, model_option)
                    return None

                self._loaded[cache_key] = model
                self.logger.info(
                    "Sentiment model loaded | option=%s model_name=%s loaded=%s",
                    model_option,
                    self._model_names.get(cache_key, "unknown"),
                    model is not None,
                )
            else:
                self._vdebug("Sentiment model cache hit | option=%s cache_key=%s", model_option, cache_key)
            self._last_used[cache_key] = time.time()
            return model

    def get_category_model(self):
        with self._lock:
            model = self._loaded.get("category")
            if model is None:
                self._vdebug("Category model cache miss")
                cfg = self.models_config.get("category", {})
                model_dir = self._resolve_model_dir(cfg.get("env_var", "CATEGORY_MODEL_DIR"), cfg.get("keyword", "category"))
                model = self._load_transformer_pipeline(
                    task_name="text-classification",
                    model_dir_path=model_dir,
                ) if model_dir is not None else None
                self._loaded["category"] = model
                self._model_names["category"] = model_dir.name if model_dir is not None else cfg.get("fallback_name", "category-heuristic-v1")
                self.logger.info(
                    "Category model loaded | model_name=%s loaded=%s",
                    self._model_names.get("category", "unknown"),
                    model is not None,
                )
            else:
                self._vdebug("Category model cache hit")
            self._last_used["category"] = time.time()
            return model

    def unload_idle_models(self) -> list[str]:
        now = time.time()
        unloaded: list[str] = []
        with self._lock:
            for key, last in list(self._last_used.items()):
                if now - last >= self.idle_seconds:
                    self._loaded.pop(key, None)
                    self._last_used.pop(key, None)
                    unloaded.append(key)
        if unloaded:
            self.logger.info("Unloaded idle models: %s", ", ".join(unloaded))
        else:
            self._vdebug("No idle models to unload")
        return unloaded

    def sentiment_predict(self, text: str, model_option: str = "custom") -> tuple[str, float, str]:
        self._vdebug("Starting sentiment prediction | option=%s text_length=%s", model_option, len(text))
        cache_key = model_option
        model = self.get_sentiment_model(model_option=model_option)
        cfg = self.models_config.get(model_option, {})

        if model is None:
            self.logger.error(
                "Sentiment model unavailable | option=%s model_name=%s",
                model_option,
                self._model_names.get(cache_key, "unknown"),
            )
            raise RuntimeError(f"Sentiment model '{model_option}' is not available.")

        model_name = self._model_names.get(cache_key, cfg.get("fallback_name", "unknown"))
        model_type = cfg.get("type")

        if model_type in ("lora", "full"):
            bundle = cast(dict[str, Any], model)
            tokenizer = bundle["tokenizer"]
            sentiment_model = bundle["model"]
            torch = bundle["torch"]
            clean_text_fn = bundle["clean_text"]
            id2label: dict[int, str] = bundle["id2label"]

            # 1) Clean input using the same pipeline used during training.
            cleaned_text = clean_text_fn(text)
            self._vdebug("%s | raw=%r cleaned=%r", model_option, text, cleaned_text)

            # 2) Tokenize.
            inputs = tokenizer(
                cleaned_text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True,
            )

            # 3) Forward pass.
            with torch.no_grad():
                logits = sentiment_model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                score, idx = torch.max(probs, dim=-1)

            predicted_id = int(idx.item())
            score_value = float(score.item())

            # 4) Map predicted id -> label using config-derived id2label.
            sentiment = id2label.get(predicted_id, "neutral")
            self._vdebug(
                "%s | predicted_id=%d label=%s score=%.4f model=%s",
                model_option, predicted_id, sentiment, score_value, model_name,
            )
            return sentiment, score_value, model_name

        # Reference Roberta pipeline path.
        out = model(text, truncation=True, max_length=512)[0]
        label = str(out.get("label", "neutral"))
        score = float(out.get("score", 0.5))
        sentiment = self._normalize_sentiment_label(label)
        self._vdebug(
            "reference | raw_label=%s mapped=%s score=%.4f model=%s",
            label, sentiment, score, model_name,
        )
        return sentiment, score, model_name

    def category_predict(self, text: str) -> tuple[str, float, str]:
        model = self.get_category_model()
        if model is None:
            self.logger.warning("Category model unavailable; using heuristic fallback")
            t = text.lower()
            if any(w in t for w in ["battery", "camera", "screen", "laptop", "phone"]):
                return "electronics", 0.84, "category-heuristic-v1"
            if any(w in t for w in ["taste", "restaurant", "food", "meal", "dish"]):
                return "food", 0.82, "category-heuristic-v1"
            if any(w in t for w in ["fabric", "shirt", "dress", "shoe", "style"]):
                return "fashion", 0.79, "category-heuristic-v1"
            return "general", 0.65, "category-heuristic-v1"

        out = model(text, truncation=True, max_length=512)[0]
        label = str(out.get("label", "general")).lower().replace("label_", "")
        score = float(out.get("score", 0.5))
        model_name = self._model_names.get("category", "category-transformer-v1")
        self._vdebug(
            "Category prediction complete | raw_label=%s mapped=%s score=%.4f model=%s",
            str(out.get("label", "general")),
            label,
            score,
            model_name,
        )
        return label, score, model_name
