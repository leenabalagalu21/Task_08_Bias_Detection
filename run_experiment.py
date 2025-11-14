import json
from pathlib import Path
from datetime import datetime, timezone

PROMPTS_PATH = Path("prompts/prompts.jsonl")
OUTPUT_PATH = Path("results/raw/llm_responses.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def iter_prompts():
    with PROMPTS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    print("=== LLM Bias Experiment Runner (manual logging) ===\n")
    print(f"Reading prompts from: {PROMPTS_PATH}")
    print(f"Appending responses to: {OUTPUT_PATH}\n")

    prompts = list(iter_prompts())

    for i, p in enumerate(prompts, start=1):
        print("=" * 60)
        print(f"Prompt #{i}")
        print(f"Hypothesis: {p['hypothesis']} | Condition: {p['condition']}\n")
        print("PROMPT:")
        print(p["prompt_text"])
        print("=" * 60)

        model = input("Model name (e.g., gpt-4o, claude-3.5, gemini-1.5): ").strip()
        run_id_str = input("Run id (e.g., 1, 2, 3): ").strip()
        try:
            run_id = int(run_id_str)
        except ValueError:
            run_id = 1

        print("\nPaste the LLM's response below. End with a blank line:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        response_text = "\n".join(lines).strip()

        if not response_text:
            print("No response entered, skipping this run.\n")
            continue

        record = {
            "hypothesis": p["hypothesis"],
            "condition": p["condition"],
            "model": model,
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_text": p["prompt_text"],
            "response_text": response_text,
        }

        with OUTPUT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print("Saved response.\n")

    print("All prompts processed. You can re-run this script for more runs or models.")


if __name__ == "__main__":
    main()