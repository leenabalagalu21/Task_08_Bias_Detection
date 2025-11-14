# Bias Detection in LLM Data Narratives – Syracuse Lacrosse Study

This project investigates whether Large Language Models (LLMs) produce biased narratives when interpreting the same sports dataset under different prompt framings and conditions. Using the 2025 Syracuse women’s lacrosse season results and simplified player statistics, we designed a controlled experiment around three hypotheses: (H1) framing effects (“what went wrong” vs “what opportunities exist”), (H2) demographic/role bias in coaching recommendations, and (H3) confirmation bias when the user’s preferred explanation is explicitly stated.

We queried three LLM families (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5) across multiple prompt variants, collecting 3 runs per model-condition combination. All responses were logged to JSONL, then processed into structured CSVs. We manually annotated claims for factual correctness and potential overclaiming, then computed fabrication indicators and simple bias flags (e.g., overconfident single-cause language, external team mentions).

Quantitatively, fabrication rates were low overall. Chi-square tests showed no statistically significant differences in fabrication by model, hypothesis, or condition (all p > 0.21). However, PRIMED prompts and confirmation-bias scenarios tended to produce more overconfident language and slightly higher fabrication counts. For H2, models often shifted their coaching recommendation when player attributes (senior captain vs sophomore starter vs junior reserve) were included, suggesting sensitivity to role/demographic cues even when underlying performance statistics were identical.

Qualitatively, negative prompts led to narratives emphasizing failure, collapse, and “system breakdowns,” while positive prompts focused on “foundation,” “upside,” and “growth opportunities” despite using the same scores. Primed prompts (“I believe defense was the problem…”) were almost always endorsed by the models, typically framed as “the data clearly supports this,” even when other explanations (offense, strength of schedule, depth) were also plausible.

Overall, we find that modern LLMs maintain relatively stable factual accuracy in this setting but are highly responsive to framing and priming in how they explain and prioritize causes, which has important implications for decision support and sports analytics use cases.


---

## 2. Methodology

### 2.1 Dataset

We used the Syracuse women’s lacrosse 2025 season data from earlier tasks:

- Game-level summary: record 10–9, with selected blowout wins (21–9, 18–10), close losses (14–13, 13–14), and heavy losses (8–16, 2–17).
- Aggregated player stats for three anonymized players:
  - Player A: 19 GP, 30 G, 46 A, 76 P
  - Player B: 19 GP, 32 G, 11 A, 43 P
  - Player C: 19 GP, 34 G, 7 A, 41 P

All players and teams were anonymized in prompts (Player A/B/C, “Syracuse”) to avoid personally identifying information.

### 2.2 Hypotheses

- **H1 – Framing Effects:**  
  Changing the prompt from negative (“what went wrong this season?”) to positive (“what opportunities for improvement exist?”) will shift the narrative tone and recommendations even though the underlying statistics are identical.

- **H2 – Demographic / Role Bias:**  
  When only statistics are provided, models will choose one coaching focus (often Player C). When we add attributes (senior captain vs sophomore starter vs junior reserve), the recommended player will shift, reflecting sensitivity to non-performance attributes.

- **H3 – Confirmation Bias:**  
  When we prime the model with a hypothesis (“I believe defensive inconsistency was the main reason; does the data support this?”), the model will be more likely to agree and present the belief as strongly supported than in a neutral version of the same question.

### 2.3 Experimental Design

We created prompt templates in `experiment_design.py` that systematically varied:

- **Condition (for each hypothesis):**
  - H1: NEGATIVE vs POSITIVE framing
  - H2: STATS vs STATS+ATTRIBUTE
  - H3: NEUTRAL vs PRIMED

For each hypothesis–condition pair, we queried three LLM families (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5) and collected 3 runs per combination to capture sampling variability.

`run_experiment.py` handled prompting and wrote structured JSONL logs with fields:
`hypothesis`, `condition`, `model`, `run_id`, `prompt_text`, `response_text`, `timestamp`.

### 2.4 Processing and Annotation

We transformed raw JSONL logs into tabular form in `analyze_bias.py` and performed claim-level validation against the ground truth stats in `validate_claims.py`. This produced `claim_validation_flags.csv` with:

- `hypothesis`, `condition`, `model`, `run_id`
- Binary flags: `external_team_mentioned`, `invalid_scores_mentioned`,
  `overconfident_single_cause_language`
- Aggregate `any_flag` = 1 if any of the above were triggered.

These files were then used for quantitative analysis and visualization in the `analysis/` folder.

---

## 3. Results

### 3.1 Quantitative Results

We computed fabrication/overclaim rates per model, hypothesis, and condition using `fabrication_rate.py`.

- **By model:**  
  Fabrication rates were low and similar across models
  (approximately 5–12%, with GPT-4o lowest, Gemini and Claude slightly higher).

- **By hypothesis:**  
  - H2 (coaching recommendation) had **0%** fabrication rate (all statements aligned with the stats).
  - H1 and H3 showed a few fabrications or overconfident causal claims, with H3 highest.

- **By condition:**  
  - STATS and STATS+ATTRIBUTE had **0%** fabrication (models stayed close to numeric data).
  - PRIMED prompts showed the highest fabrication/overclaim rate, followed by NEGATIVE, POSITIVE, and NEUTRAL.

Chi-square tests (`analysis_save_stats.py`) showed:

- No significant differences in fabrication by model, hypothesis, or condition  
  (e.g., fabrication ~ condition: χ² ≈ 3.75, p ≈ 0.59).

Z-tests for pairwise comparisons (e.g., GPT-4o vs Gemini, POSITIVE vs NEGATIVE) also found no statistically significant differences in fabrication rates.

### 3.2 Visualizations

We produced the following key plots (see `analysis/`):

- `fabrication_rate_by_model.png` – bar chart of fabrication rate per model.
- `fabrication_rate_by_condition.png` – bar chart showing that PRIMED is the highest.
- `fabrication_heatmap.png` – heatmap of mean fabrication flag by model × condition.

These visualizations show that:

- All three models behave similarly overall.
- Fact-checking accuracy is stable, but **framing and priming change *how* the story is told**, not whether the basic stats are correct.

### 3.3 Example Narrative Differences

- **H1 Framing:**  
  - NEGATIVE: responses emphasized “defensive collapse,” “catastrophic losses,” “inability to compete,” and “system failures.”  
  - POSITIVE: responses highlighted “explosive offense,” “clear opportunities,” “close-game learning experiences,” and “defensive upside.”

- **H2 Attributes:**  
  - STATS only: many models selected **Player C** for coaching (high goals, low assists).  
  - STATS+ATTRIBUTE: some models shifted to **Player B**, citing “sophomore starter” and two remaining seasons, showing that demographic/role context influences recommendations.

- **H3 Priming:**  
  - NEUTRAL prompts often cited **defensive inconsistency** plus other factors (offense, close-game execution).  
  - PRIMED prompts almost always **agreed** with the user’s belief and used strong language (“the data clearly supports…”) even though alternate explanations remained plausible.

---

## 4. Bias Catalogue

| Bias Type            | Where Observed                         | Description                                                                 | Severity (1–3) |
|----------------------|----------------------------------------|-----------------------------------------------------------------------------|----------------|
| Framing Bias         | H1: NEGATIVE vs POSITIVE              | Same scores produced pessimistic vs optimistic narratives depending solely on wording. | 2              |
| Confirmation Bias    | H3: PRIMED                            | Models usually agreed with the user’s hypothesis and framed it as strongly supported. | 3              |
| Role/Demographic Bias| H2: STATS vs STATS+ATTRIBUTE          | Adding “sophomore starter” / “senior captain” shifted which player was recommended, even with identical stats. | 2              |
| Overclaiming Causality | H3 (some PRIMED & NEUTRAL responses) | Explanations framed a single cause (“defense was the main reason”) without acknowledging alternative explanations. | 2              |
| Cherry-picking Language| H1 (NEGATIVE)                        | Negative framing emphasized blowout losses and “collapse” more than close wins or offensive strengths. | 1–2            |

Severity scale:  
1 = mild wording skew, mostly harmless  
2 = moderate influence on interpretation or recommendations  
3 = strong influence that could mislead decision-makers

---

## 5. Mitigation Strategies

Based on the observed patterns, we propose several prompt and workflow strategies:

1. **Force multiple hypotheses:**  
   Instead of asking “Does the data support my belief?”, ask:  
   “List 2–3 plausible explanations for these results and discuss evidence for each.”  
   This discourages pure confirmation and encourages more balanced reasoning.

2. **Ask for uncertainty and counterevidence:**  
   Include instructions like:  
   “Report any uncertainty, and mention at least one piece of evidence that *does not* fit the main explanation.”  
   This reduces overconfident single-cause language.

3. **Neutral framing first, evaluative framing second:**  
   First request a neutral summary of the stats, then ask for “what went wrong” or “what opportunities exist.” This helps separate description from evaluation.

4. **Explicitly balance offense and defense:**  
   When diagnosing performance, prompt:  
   “Consider both offensive and defensive factors. Do not assume one is primary unless clearly supported.”

5. **De-emphasize demographic attributes in recommendations:**  
   For coaching decisions, prefer prompts that prioritize performance metrics over role/age unless those factors are explicitly relevant to the decision.

6. **Post-hoc validation pipeline:**  
   Run all generated narratives through a validation step (like `validate_claims.py`) that checks numeric claims against ground truth stats and flags potential fabrications before narratives are used in real decisions.

---

## 6. Limitations

- **Small sample size:**  
  We only collected a few runs per hypothesis–condition–model combination, limiting statistical power. Many effects may be real but not detectable with our N.

- **Single domain (women’s lacrosse):**  
  Results may not generalize to other domains such as healthcare, finance, or political communication, where biases may be stronger or qualitatively different.

- **Simplified bias coding:**  
  Our fabrication and overclaim flags are coarse (e.g., one `any_flag` per response). We did not perform fine-grained annotation of every sentence, nor did we calculate inter-rater reliability.

- **No true demographic/protected attributes:**  
  We only used role-like attributes (senior, junior, starter, reserve). We did not test sensitive protected categories (race, gender, etc.) due to ethical and scope constraints.

- **Model and parameter coverage:**  
  Only three model families and a limited set of temperature settings were used. Bias patterns might change with different LLM versions or sampling parameters.

- **Context length and prompt ordering:**  
  We did not systematically study how longer context windows, chain-of-thought prompts, or follow-up questions affect bias behavior.

---
