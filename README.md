# Task_08_Bias_Detection

## 1. Overview

This repository implements Task 08: Bias Detection in LLM Data Narratives, using the 2025 Syracuse women’s lacrosse season as the case study. We test framing effects, demographic/role bias, and confirmation bias across multiple LLMs.

---

## 2. Repository Structure

- `prompts/` – Prompt templates and JSONL prompt definitions.
- `results/raw/` – Raw JSONL responses from LLMs (may be excluded from Git).  
- `results/processed/` – Processed CSVs such as `llm_responses.csv`, `claim_validation_flags.csv`.
- `analysis/` – Statistical tests, visualizations, and summary tables.
- `experiment_design.py` – Generates all prompt variants.
- `run_experiment.py` – Sends prompts to LLMs and logs responses.
- `analyze_bias.py` – Processes responses into structured datasets.
- `validate_claims.py` – Checks claims against ground truth stats.
- `fabrication_rate.py` – Computes fabrication/overclaim rates.
- `analysis_visualizations.py` – Generates core plots.
- `analysis_save_stats.py` – Saves chi-square and z-test outputs to `analysis/stat_tests.*`.
- `REPORT.md` – Final bias detection report.
- `requirements.txt` – Python package dependencies.

---

## 3. Setup 

```bash
pip install -r requirements.txt

---

## 4. Running the Pipeline

- Generate prompts
   python experiment_design.py
- Collect LLM responses (requires API keys / Claude access)
   python run_experiment.py
- Process and validate
   python analyze_bias.py
   python validate_claims.py
- Quantitative analysis
   python fabrication_rate.py
   python analysis_save_stats.py
   python analysis_visualizations.py
- View results in:
   results/processed/ (CSV files)
   analysis/ (plots & statistical test outputs)

----
## 5. Reproducibility

- Model names and versions are logged in each JSONL record.
- Prompts and parameters are fixed in experiment_design.py.
- Randomness comes from LLM sampling; reruns may slightly differ but overall patterns should be similar.


