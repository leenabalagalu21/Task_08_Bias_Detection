import pandas as pd
import numpy as np
import os

from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest

# -----------------------------------------------------------
# Load dataset
# -----------------------------------------------------------
df = pd.read_csv(r"C:\Users\leena\Downloads\results\processed\claim_validation_flags.csv")
df["fabrication"] = df["any_flag"].astype(int)

# -----------------------------------------------------------
# Ensure analysis folder exists
# -----------------------------------------------------------
OUTPUT_DIR = "analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

text_output = []
csv_records = []

def add_result(title, content):
    """Store results in text file & machine-readable CSV."""
    text_output.append("\n" + "="*70)
    text_output.append(title)
    text_output.append("="*70)
    text_output.append(content)

    # Store also in CSV-friendly rows
    csv_records.append({"test": title, "result": content})


# -----------------------------------------------------------
# 1. Chi-Square Tests
# -----------------------------------------------------------
def chi_square_test(name, table):
    chi2, p, dof, expected = chi2_contingency(table)
    result_text = (
        f"\nChi-square: {chi2}"
        f"\np-value: {p}"
        f"\nDegrees of freedom: {dof}"
        f"\nContingency Table:\n{table.to_string()}"
    )
    add_result(f"Chi-Square Test: {name}", result_text)


# MODEL
model_table = pd.crosstab(df["model"], df["fabrication"])
chi_square_test("Fabrication ~ MODEL", model_table)

# HYPOTHESIS
hypothesis_table = pd.crosstab(df["hypothesis"], df["fabrication"])
chi_square_test("Fabrication ~ HYPOTHESIS", hypothesis_table)

# CONDITION
condition_table = pd.crosstab(df["condition"], df["fabrication"])
chi_square_test("Fabrication ~ CONDITION", condition_table)


# -----------------------------------------------------------
# 2. Z-Tests (Proportion Tests)
# -----------------------------------------------------------
def ztest_groups(group1, group2, col):
    g1 = df[df[col] == group1]["fabrication"]
    g2 = df[df[col] == group2]["fabrication"]

    count = [g1.sum(), g2.sum()]
    nobs = [len(g1), len(g2)]

    stat, pval = proportions_ztest(count, nobs)

    result_text = (
        f"\nComparing {group1} vs {group2} (Column: {col})"
        f"\nZ-statistic: {stat}"
        f"\np-value: {pval}"
        f"\nCounts: {count}"
        f"\nNobs: {nobs}"
    )
    add_result(f"Z-Test: {group1} vs {group2} ({col})", result_text)


# Run z-tests
ztest_groups("claude-3.5", "gemini-1.5", "model")
ztest_groups("gemini-1.5", "gpt-4o", "model")
ztest_groups("POSITIVE", "NEGATIVE", "condition")


# -----------------------------------------------------------
# Save output files
# -----------------------------------------------------------

# Save human-readable text
with open(os.path.join(OUTPUT_DIR, "stat_tests.txt"), "w") as f:
    f.write("\n".join(text_output))

# Save CSV summary
csv_df = pd.DataFrame(csv_records)
csv_df.to_csv(os.path.join(OUTPUT_DIR, "stat_tests.csv"), index=False)

print("\nAll statistical test outputs saved in /analysis folder:")
print(" - analysis/stat_tests.txt")
print(" - analysis/stat_tests.csv")
