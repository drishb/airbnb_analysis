"""One-off figure: mean silhouette score per market vs. this project's own
0.25 acceptance bar, in the same visual style as the report's existing
"Price-demand relationship strength" bar chart. Source values are the
selected-k rows already in each outputs-*/cluster_summary.md."""
import matplotlib.pyplot as plt

MARKETS = ["California", "Antwerp", "Amsterdam", "Rio de Janeiro"]
SILHOUETTE = [0.19, 0.17, 0.33, 0.17]
COLORS = ["#D9622B", "#1F3864", "#E8A33D", "#2E8B57"]
THRESHOLD = 0.25

fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)

bars = ax.bar(MARKETS, SILHOUETTE, color=COLORS, width=0.6, zorder=3)

for bar, val in zip(bars, SILHOUETTE):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val - 0.02 if val > THRESHOLD else val + 0.012,
        f"{val:.2f}",
        ha="center",
        va="top" if val > THRESHOLD else "bottom",
        fontsize=12,
        fontweight="bold",
        color="white" if val > THRESHOLD else "black",
    )

ax.axhline(THRESHOLD, color="black", linestyle="--", linewidth=1.2, zorder=2)
ax.text(
    len(MARKETS) - 0.42,
    THRESHOLD + 0.008,
    "project acceptance threshold (0.25)",
    ha="right",
    va="bottom",
    fontsize=9.5,
    style="italic",
)

ax.set_title("Segmentation quality by market", fontsize=14, fontweight="bold", pad=14)
ax.set_ylabel("Mean silhouette score (k-means, selected k)")
ax.set_ylim(0, 0.40)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.25, zorder=0)

fig.tight_layout()
fig.savefig("outputs/figures/silhouette_by_market.png", bbox_inches="tight")
print("wrote outputs/figures/silhouette_by_market.png")
