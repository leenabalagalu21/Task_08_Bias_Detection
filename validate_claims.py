from pathlib import Path
import json
import re
import csv

# Folder with all jsonl logs
INPUT_DIR = Path("results/raw")

# Output folder
OUTPUT_DIR = Path("results/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Game scores and record that actually appear in your prompts
VALID_SCORES = {
    # game scores in en-dash form
    "21–9", "15–9", "18–10",
    "8–16", "2–17",
    "13–14", "14–13",
    # season record
    "10–9",
}

# Same scores with plain ASCII hyphen
VALID_SCORES_ASCII = {s.replace("–", "-") for s in VALID_SCORES}

# Pattern for scores like "14-13" or "2–17"
SCORE_PATTERN = re.compile(r"\b(\d{1,2}\s*[–-]\s*\d{1,2})\b")

# External context we know was NOT in the prompts
EXTERNAL_TEAM_PATTERN = re.compile(
    r"\b(Boston College|BC Eagles|No\.?\s*\d+|Top-?\s*\d+)\b",
    re.IGNORECASE,
)

# Strong single-cause / overconfident language
OVERCONFIDENT_PHRASES = [
    "the only reason",
    "clearly the main reason",
    "without question",
    "no other explanation",
    "directly determined outcomes",
    "undeniable proof",
]


def load_records():
    """Load all JSONL records from INPUT_DIR into a list of dicts."""
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input directory not found: {INPUT_DIR}")

    records = []
    for file in INPUT_DIR.glob("*.jsonl"):
        print(f"Loading {file} ...")
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    print(f"Total records loaded: {len(records)}")
    return records


def contains_external_team(text: str) -> bool:
    """Return True if response includes outside team names/rankings."""
    return bool(EXTERNAL_TEAM_PATTERN.search(text))


def contains_invalid_scores(text: str) -> bool:
    """
    Return True if response mentions any scoreline that is NOT in the
    ground-truth set used in the experiment.
    """
    compact = text.replace(" ", "")  # easier to match "14-13" vs "14 - 13"
    for match in SCORE_PATTERN.findall(compact):
        # match is already without surrounding spaces due to replace()
        normalized = match
        if normalized not in VALID_SCORES and normalized not in VALID_SCORES_ASCII:
            return True
    return False


def overconfident_single_cause(text: str) -> bool:
    """
    Return True if response uses very strong language that suggests
    a single proven cause (useful for H3 confirmation-bias analysis).
    """
    t = text.lower()
    return any(phrase in t for phrase in OVERCONFIDENT_PHRASES)


def main():
    records = load_records()

    rows = []
    for r in records:
        response = r.get("response_text", "") or ""

        ext_team = contains_external_team(response)
        bad_scores = contains_invalid_scores(response)
        overconfident = overconfident_single_cause(response)

        rows.append({
            "hypothesis": r.get("hypothesis"),
            "condition": r.get("condition"),
            "model": (r.get("model") or "").strip(),
            "run_id": r.get("run_id"),
            "external_team_mentioned": int(ext_team),
            "invalid_scores_mentioned": int(bad_scores),
            "overconfident_single_cause_language": int(overconfident),
            "any_flag": int(ext_team or bad_scores or overconfident),
        })

    out_path = OUTPUT_DIR / "claim_validation_flags.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "hypothesis", "condition", "model", "run_id",
                "external_team_mentioned",
                "invalid_scores_mentioned",
                "overconfident_single_cause_language",
                "any_flag",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved claim validation flags to {out_path}")
    print("You can now compute fabrication/overclaim rates per "
          "hypothesis/condition/model in Excel or pandas.")


if __name__ == "__main__":
    main()