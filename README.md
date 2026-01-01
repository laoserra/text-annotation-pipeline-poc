# Text Annotation Pipeline – PoC
###  Quality Validator & Output Generator

![Proof of Concept](https://img.shields.io/badge/Stage-Proof%20of%20Concept-blue?style=flat)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-306998?style=flat)
![UV Astral](https://img.shields.io/badge/UV-Astral-FFC107?style=flat)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white&style=flat)
![MIT License](https://img.shields.io/badge/License-MIT-green?style=flat)


## 🏛️ Project Overview

This repository implements **Part 2 (PoC)** of a text annotation pipeline for intent classification.
It validates human annotations for quality and exports a model-ready dataset.

**Quality validations:**
- a confidence score threshold (≥ 0.8)
- an inter-annotator agreement check

**Agreed samples** are exported as JSONL for ML training, while **disagreements** are logged for inspection.


## ⚙️ Prerequisites

- [Astral UV](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.12+ runner & package manager)

## 🚀 Quick Start

Clone the repository and run the script from project root:
```bash
git clone https://github.com/laoserra/text-annotation-pipeline-poc.git
cd text-annotation-pipeline-poc
uv run scripts/process_annotations.py
```
> [!NOTE]
> The script must be executed from the project root so that input/output paths resolve correctly.

**Expected behaviour:**
  - Prints number of disagreed and agreed samples to stdout
  - Saves logs to `logs/<YYYY-MM-DD>/disagreements.log` (if any exist)
  - Exports `data/processed/clean_training_dataset.jsonl` only when samples pass confidence and agreement checks


## 📊 Key Findings & Results

The log file stores rich context per disagreement, for example:
```json
{"text": "I need to reset my password", "labels": ["login_issue","password_reset"], "annotators": [1, 6], "confidence_scores": [0.92, 0.87]}
```

The JSONL output is intentionally minimal and ML-friendly:
```json
{"text": "Reset my password please", "label": "password_reset"}
{"text": "My parcel is missing", "label": "shipping_issue"}
```
This keeps a clean contract for downstream model training while preserving debugging detail in logs.


## 🧪 Log & Output Behaviour

| Condition                        | Console Output                                   | Files Generated                                      |
| -------------------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| All samples fail confidence      | `All samples failed the confidence score check.` | ❌ none                                               |
| Pass confidence but all disagree | `All samples failed the agreement test.`         | `disagreements.log` only                             |
| Some pass confidence and agree   | Prints counts + exports agreed                   | `disagreements.log` + `clean_training_dataset.jsonl` |


## 📂 Project Structure

```text
text-annotation-pipeline-poc/
├── data/
│   ├── raw/
│   │   └── raw_annotations.csv
│   └── processed/
│       └── clean_training_dataset.jsonl
├── logs/
│   └── <date>/
│       └── disagreements.log
├── scripts/
│   └── process_annotations.py
├── design_document.md
└── README.md
```


## 🔗 How PoC Fits Part 1 (High-Level Architecture)

This script fits into the Model-Ready layer of the larger system designed in [Part 1](./design_document.md):
- Runs after human annotation collection
- Acts as a quality gate before ML training data export
- Simulates a minimal but realistic pipeline boundary contract
- Uses simple log files only (assessment requirement), while the full system design proposes structured event logs and richer observability for future stages


## 📜 License
This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.
