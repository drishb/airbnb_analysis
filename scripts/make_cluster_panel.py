"""One-off figure: combine the four per-market map_clusters.png outputs
into a single 2x2 panel for the report's neighbourhood-segmentation section.
Reads existing pipeline figures only; no re-computation."""
import matplotlib.pyplot as plt
from matplotlib.image import imread

PANELS = [
    ("outputs-cali", "California", 5),
    ("outputs-amsterdam", "Amsterdam", 5),
    ("outputs-antwerp", "Antwerp", 3),
    ("outputs-rio", "Rio de Janeiro", 5),
]

fig, axes = plt.subplots(2, 2, figsize=(12, 12), dpi=150)

for ax, (folder, city, k) in zip(axes.flat, PANELS):
    img = imread(f"{folder}/figures/map_clusters.png")
    ax.imshow(img)
    ax.axis("off")
    ax.set_title(f"{city} (k = {k} clusters)", fontsize=13, fontweight="bold", pad=8)

fig.suptitle("Neighbourhood clusters by market", fontsize=16, fontweight="bold", y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig("outputs/figures/map_clusters_by_market.png", bbox_inches="tight")
print("wrote outputs/figures/map_clusters_by_market.png")
