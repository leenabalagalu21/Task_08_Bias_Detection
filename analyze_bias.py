from pathlib import Path
import json
import re
import csv
from collections import Counter

# Folder that contains all your jsonl logs
INPUT_DIR = Path("results/raw")

# Folder where we write analysis outputs
OUTPUT_DIR = Path("results/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Simple word lists to approximate sentiment / framing
POSITIVE_WORDS = {
    "opportunity", "opportunities", "potential", "strength", "strengths",
    "foundation", "upside", "growth", "improvement", "improve",
    "competitive", "build", "leverage", "breakthrough", "positive"
}

NEGATIVE_WORDS = {
    "collapse", "collapsed", "catastrophic", "failure", "failed",
    "struggle", "struggled", "weakness", "weaknesses", "problem",
    "problems", "poor", "inconsistent", "inconsistency", "breakdown",
    "breakdowns", "vulnerable", "mediocre", "underperformed", "issues"
}

# To detect which player (A/B/C) is recommended
PLAYER_PATTERN = re.compile(r"\bPlayer\s+([ABC])\b", re.IGNORECASE)


def load_records():
    """Load all JSONL files from INPUT_DIR into a single list of dicts."""
    records = []
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input directory not found: {INPUT_DIR}")

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


def sentiment_score(text: str) -> float:
    """
    Very simple sentiment score:
    (positive_count - negative_count) / (positive_count + negative_count)
    """
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    if pos == 0 and neg == 0:
        return 0.0
    return (pos - neg) / (pos + neg)


def main():
    records = load_records()

    # ---------------------- H2: player recommendations ----------------------
    h2_counts = Counter()

    for r in records:
        if r.get("hypothesis") != "H2":
            continue

        txt = r.get("response_text", "") or ""
        m = PLAYER_PATTERN.search(txt)
        player = m.group(1).upper() if m else "UNKNOWN"
        condition = r.get("condition", "").strip()
        model = r.get("model", "").strip()

        key = (condition, model, player)
        h2_counts[key] += 1

    h2_out = OUTPUT_DIR / "h2_player_recommendations.csv"
    with h2_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["condition", "model", "player", "count"])
        for (cond, model, player), cnt in sorted(h2_counts.items()):
            writer.writerow([cond, model, player, cnt])

    print(f"Saved H2 player recommendation counts to {h2_out}")

    # ---------------------- H1 & H3: sentiment + focus ----------------------
    sentiment_rows = []

    for r in records:
        if r.get("hypothesis") not in ("H1", "H3"):
            continue

        text = r.get("response_text", "") or ""
        s = sentiment_score(text)

        tl = text.lower()
        mentions_def = any(w in tl for w in ("defense", "defensive"))
        mentions_off = any(w in tl for w in ("offense", "offensive"))
        mentions_close = any(
            phrase in tl
            for phrase in ("close game", "close games", "one-goal", "tight game", "tight games")
        )
        mentions_team = "team" in tl
        mentions_individual = "player" in tl or "players" in tl

        sentiment_rows.append({
            "hypothesis": r.get("hypothesis"),
            "condition": r.get("condition"),
            "model": r.get("model", "").strip(),
            "run_id": r.get("run_id"),
            "sentiment_score": s,
            "mentions_defense": int(mentions_def),
            "mentions_offense": int(mentions_off),
            "mentions_close_games": int(mentions_close),
            "mentions_team_level": int(mentions_team),
            "mentions_individual_level": int(mentions_individual),
        })

    sent_out = OUTPUT_DIR / "h1_h3_sentiment_focus.csv"
    with sent_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "hypothesis", "condition", "model", "run_id",
                "sentiment_score",
                "mentions_defense", "mentions_offense",
                "mentions_close_games", "mentions_team_level",
                "mentions_individual_level",
            ],
        )
        writer.writeheader()
        writer.writerows(sentiment_rows)

    print(f"Saved H1/H3 sentiment & focus analysis to {sent_out}")
    print("Done. You can now open these CSVs in Excel or pandas for charts and stats.")


if __name__ == "__main__":
    main()