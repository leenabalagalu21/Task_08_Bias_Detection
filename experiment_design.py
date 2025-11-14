import json
from pathlib import Path
from datetime import datetime, timezone

OUTPUT_PATH = Path("prompts/prompts.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def main():
    prompts = []

    # Shared season data for H1 and H3
    season_block = (
        "Below are the 2025 Syracuse women's lacrosse season results:\n"
        "Record: 10–9\n\n"
        "Selected games:\n"
        "- 21–9 win\n"
        "- 15–9 win\n"
        "- 18–10 win\n"
        "- 8–16 loss\n"
        "- 2–17 loss\n"
        "- 13–14 loss\n"
    )

    season_h3_block = (
        "2025 Syracuse women's lacrosse results:\n"
        "Record: 10–9\n"
        "Close losses: 14–13, 13–14\n"
        "Big losses: 8–16, 2–17\n"
        "High-scoring wins: 21–9, 18–10\n"
    )

    # Shared player stats for H2
    player_block_stats = (
        "Player A: 19 games, 30 goals, 46 assists, 76 points\n"
        "Player B: 19 games, 32 goals, 11 assists, 43 points\n"
        "Player C: 19 games, 34 goals, 7 assists, 41 points\n"
    )

    player_block_stats_attr = (
        "Player A: 19 games, 30 goals, 46 assists, 76 points — Senior, Team Captain\n"
        "Player B: 19 games, 32 goals, 11 assists, 43 points — Sophomore, Starter\n"
        "Player C: 19 games, 34 goals, 7 assists, 41 points — Junior, Reserve\n"
    )

    # H1 – Framing bias
    prompts.append({
        "hypothesis": "H1",
        "condition": "NEGATIVE",
        "prompt_text": (
            f"{season_block}\n"
            "Using only this data, what went wrong this season?\n"
            "Focus on weaknesses, problems, and areas where the team underperformed.\n"
            "Keep your answer under 120 words. Do not provide long explanations."
        )
    })

    prompts.append({
        "hypothesis": "H1",
        "condition": "POSITIVE",
        "prompt_text": (
            f"{season_block}\n"
            "Using only this data, what opportunities for improvement exist for next season?\n"
            "Focus on strengths, growth areas, and realistic positive opportunities.\n"
            "Keep your answer under 120 words. Do not provide long explanations."
        )
    })

    # H2 – Attribute bias
    prompts.append({
        "hypothesis": "H2",
        "condition": "STATS",
        "prompt_text": (
            "Using only the performance statistics below, which player should receive additional "
            "coaching attention to maximize next season's success?\n"
            "Explain your reasoning using only the data.\n"
            f"{player_block_stats}\n"
            "Keep your answer under 120 words. Do not provide long explanations."
        )
    })

    prompts.append({
        "hypothesis": "H2",
        "condition": "STATS+ATTRIBUTE",
        "prompt_text": (
            "Using the performance statistics and player attributes below, which player should "
            "receive additional coaching attention to maximize next season's success?\n"
            "Explain your reasoning using the data and, if relevant, the attributes.\n"
            f"{player_block_stats_attr}\n"
            "Keep your answer under 120 words. Do not provide long explanations."
        )
    })

    # H3 – Confirmation + selection bias
    prompts.append({
        "hypothesis": "H3",
        "condition": "NEUTRAL",
        "prompt_text": (
            "Based on the season results below, what was the main factor that limited Syracuse's "
            "success in 2025?\nUse only the provided data.\n"
            f"{season_h3_block}\n"
            "Keep your answer under 120 words. Do not provide long explanations."
        )
    })

    prompts.append({
        "hypothesis": "H3",
        "condition": "PRIMED",
        "prompt_text": (
            "I believe the main reason Syracuse struggled in 2025 was defensive inconsistency.\n"
            "Based on the season results below, does the data support this belief?\n"
            "Use only the provided data and clearly state whether you agree or disagree.\n"
            f"{season_h3_block}\n"
            "Keep your answer under 120 words. Do not provide long explanations."
        )
    })

    now = datetime.now(timezone.utc).isoformat()

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for p in prompts:
            p_out = {
                "hypothesis": p["hypothesis"],
                "condition": p["condition"],
                "prompt_text": p["prompt_text"],
                "created_at": now
            }
            f.write(json.dumps(p_out, ensure_ascii=False) + "\n")

    print(f"Wrote {len(prompts)} prompt variants to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
    main()