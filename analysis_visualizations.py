import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(r"C:\Users\leena\Downloads\results\processed\claim_validation_flags.csv")

sns.set(style="whitegrid")


# ==============================
# 1. Fabrication Rate by Model
# ==============================
def plot_fabrication_by_model():
    summary = df.groupby("model")['any_flag'].mean()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=summary.index, y=summary.values)
    plt.title("Fabrication Rate by Model", fontsize=14, pad=20)
    plt.ylabel("Fabrication Rate")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # FIX
    plt.savefig("fabrication_rate_by_model.png", dpi=300)
    plt.close()


# ==============================
# 2. Fabrication Rate by Condition
# ==============================
def plot_fabrication_by_condition():
    summary = df.groupby("condition")['any_flag'].mean()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=summary.index, y=summary.values, palette="viridis")
    plt.title("Fabrication Rate by Condition", fontsize=14, pad=20)
    plt.ylabel("Fabrication Rate")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # FIX
    plt.savefig("fabrication_rate_by_condition.png", dpi=300)
    plt.close()


# ==============================
# 3. Heatmap (Model × Condition)
# ==============================
def plot_heatmap_model_condition():
    table = pd.crosstab(df["model"], df["condition"], df["any_flag"], aggfunc='mean').fillna(0)

    plt.figure(figsize=(12, 7))
    sns.heatmap(table, annot=True, cmap="Blues", fmt=".2f")
    plt.title("Fabrication Heatmap (Model × Condition)", fontsize=16, pad=20)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # FIX
    plt.savefig("fabrication_heatmap.png", dpi=300)
    plt.close()


# ==============================
# Run all visualizations
# ==============================
plot_fabrication_by_model()
plot_fabrication_by_condition()
plot_heatmap_model_condition()

print("All plots saved successfully.")
