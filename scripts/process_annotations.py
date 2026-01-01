#!/usr/bin/env -S uv run
# scripts/process_annotations.py

"""
PoC Quality Validator & Output Generator for intent classification annotations.

Applies:
  1) Confidence threshold filtering
  2) Inter-annotator agreement check

Logs disagreements and exports agreed samples to JSONL.

Run from project root:
    uv run scripts/process_annotations.py
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

# -----------------------------------------------------------------------------
# Constants & paths
# -----------------------------------------------------------------------------
CONF_THRESHOLD: float = 0.8
FILE_RAW: Path = Path("data/raw/raw_annotations.csv")
FILE_OUT: Path = Path("data/processed/clean_training_dataset.jsonl")
DIR_LOGS: Path = Path("logs")

FILE_OUT.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Logging setup (daily file)
# -----------------------------------------------------------------------------
today: str = datetime.today().strftime("%Y-%m-%d")
today_str: str = datetime.today().strftime("%Y%m%d")
file_log: Path = DIR_LOGS / today / f"disagreements_{today_str}.log"
file_log.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=file_log,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
console = logging.getLogger("console")
console.addHandler(logging.StreamHandler())
console.setLevel(logging.INFO)


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def load_annotations(path: Path) -> pd.DataFrame:
    """Load annotation CSV."""
    return pd.read_csv(path)


def filter_by_confidence(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Keep annotations with confidence ≥ threshold."""
    return df[df["confidence_score"] >= threshold].copy()


def detect_disagreements(df: pd.DataFrame) -> List[Dict[str, List]]:
    """
    Find texts with multiple labels (disagreement).
    Returns structured disagreement records.
    """
    label_sets = df.groupby("text")["label"].agg(set)
    disagreed = label_sets[label_sets.apply(len) > 1]

    records: List[Dict[str, List]] = []
    for text, labels in disagreed.items():
        sub = df[df["text"] == text]
        records.append(
            {
                "text": text,
                "labels": list(labels),
                "annotators": sub["annotator_id"].tolist(),
                "confidence_scores": sub["confidence_score"].tolist(),
            }
        )
    return records


def extract_agreed(df: pd.DataFrame) -> pd.DataFrame:
    """Return one (text, label) per text where annotators fully agreed."""
    label_sets = df.groupby("text")["label"].agg(set)
    agreed_texts = label_sets[label_sets.apply(len) == 1].index
    return df[df["text"].isin(agreed_texts)][["text", "label"]].drop_duplicates()


def export_jsonl(df: pd.DataFrame, path: Path) -> None:
    """Write clean dataset to JSONL."""
    with path.open("w", encoding="utf-8") as f:
        for text, label in df.itertuples(index=False):
            f.write(
                json.dumps({"text": text, "label": label}, ensure_ascii=False) + "\n"
            )


def main() -> None:
    """Run validation pipeline."""
    console.info("Reading raw annotations…")
    df_raw = load_annotations(FILE_RAW)

    console.info("Filtering by confidence…")
    df_conf = filter_by_confidence(df_raw, CONF_THRESHOLD)
    console.info(f"After confidence filter: {len(df_conf)} rows")

    console.info("Checking agreement…")
    disagreements = detect_disagreements(df_conf)
    if disagreements:
        logging.info("Disagreed samples:")
        for rec in disagreements:
            logging.info(json.dumps(rec, ensure_ascii=False))
    else:
        logging.info("Disagreed samples: 0")

    df_clean = extract_agreed(df_conf)
    console.info(f"Agreed samples: {len(df_clean)}")

    console.info("Exporting JSONL…")
    export_jsonl(df_clean, FILE_OUT)
    console.info("Done.")


if __name__ == "__main__":
    main()
