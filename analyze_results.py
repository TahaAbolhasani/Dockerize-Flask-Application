"""
analyze_results.py

Reads the latency CSV files produced by each of the 4 deployment stages
(Host, Docker, Compose, Swarm) and produces:
  1. A summary table of latency statistics (mean, median, std, min, max) per stage.
  2. A bar chart comparing average latency across the 4 methods.
  3. A bar chart comparing CPU%, Memory%, and Network I/O across the 4 methods,
     using values YOU manually noted down from `docker stats` while each test ran
     (these are not in the CSV files, so you must fill them in below).

Run this on your own machine (inside the venv), from the homeworks/one folder:
    python analyze_results.py

Requires: pandas, matplotlib (install with: pip install pandas matplotlib)
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------------
# 1. CONFIGURATION - adjust these paths/values to match your setup
# ---------------------------------------------------------------------------

RESULTS_DIR = os.path.expanduser("~/CloudComputing/results")

# Latency CSV files for each stage.
# For Swarm with 3 replicas, we combine the 3 per-container files into one,
# since together they represent the full set of 160 queries for that stage.
LATENCY_FILES = {
    "Host": os.path.join(RESULTS_DIR, "system_inference_metrics.csv"),
    "Docker": os.path.join(RESULTS_DIR, "docker_system_inference_metrics.csv"),
    "Compose": os.path.join(RESULTS_DIR, "compose_inference_metrics.csv"),
    "Swarm (1 replica)": os.path.join(RESULTS_DIR, "swarm_1replica_inference_metrics.csv"),
}

SWARM_3REPLICA_FILES = [
    os.path.join(RESULTS_DIR, "swarm_3replica_container1.csv"),
    os.path.join(RESULTS_DIR, "swarm_3replica_container2.csv"),
    os.path.join(RESULTS_DIR, "swarm_3replica_container3.csv"),
]

# Some of our CSVs are missing a header row (e.g. compose_inference_metrics.csv,
# because of the `touch` workaround we used for the volume mount bug).
# We define the expected column names here so we can apply them when needed.
COLUMN_NAMES = ["Inference Latency (ms)", "Prediction", "Input Text", "Timestamp"]

# ---------------------------------------------------------------------------
# NOTE: CPU %, Memory %, and Network I/O are NOT included in this analysis.
# Those metrics come from `docker stats` (observed live, not written to the CSV
# files), and were not systematically captured during this run. The final
# report should explicitly note this as a limitation: only inference latency
# (which is fully logged in the CSV files) is compared here.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 2. LOAD AND CLEAN LATENCY DATA
# ---------------------------------------------------------------------------

def load_latency_csv(path):
    """Load a latency CSV, handling the case where the header row is missing."""
    # Peek at the first line to see if it looks like a header or like data.
    with open(path, "r") as f:
        first_line = f.readline().strip()

    has_header = first_line.startswith("Inference Latency")

    if has_header:
        df = pd.read_csv(path)
    else:
        df = pd.read_csv(path, header=None, names=COLUMN_NAMES)

    # Make sure the latency column is numeric.
    df["Inference Latency (ms)"] = pd.to_numeric(df["Inference Latency (ms)"], errors="coerce")
    df = df.dropna(subset=["Inference Latency (ms)"])
    return df


def load_swarm_3replica():
    """Combine the 3 per-container CSVs from the 3-replica Swarm test into one DataFrame."""
    frames = []
    for path in SWARM_3REPLICA_FILES:
        if os.path.exists(path):
            frames.append(load_latency_csv(path))
        else:
            print(f"  Warning: {path} not found, skipping.")
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


print("Loading latency data...")
data = {}
for label, path in LATENCY_FILES.items():
    if os.path.exists(path):
        data[label] = load_latency_csv(path)
        print(f"  {label}: {len(data[label])} rows loaded from {path}")
    else:
        print(f"  Warning: {path} not found, skipping {label}.")

swarm_3 = load_swarm_3replica()
if swarm_3 is not None:
    data["Swarm (3 replicas)"] = swarm_3
    print(f"  Swarm (3 replicas): {len(swarm_3)} rows loaded (combined from 3 containers)")

if not data:
    raise SystemExit("No latency data found. Check RESULTS_DIR and file names at the top of this script.")

# ---------------------------------------------------------------------------
# 4. SUMMARY STATISTICS TABLE
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("LATENCY SUMMARY STATISTICS (ms)")
print("=" * 70)

summary_rows = []
for label, df in data.items():
    lat = df["Inference Latency (ms)"]
    summary_rows.append({
        "Method": label,
        "Count": len(lat),
        "Mean": round(lat.mean(), 2),
        "Median": round(lat.median(), 2),
        "Std Dev": round(lat.std(), 2),
        "Min": round(lat.min(), 2),
        "Max": round(lat.max(), 2),
    })

summary_df = pd.DataFrame(summary_rows)
print(summary_df.to_string(index=False))

# Save the summary table as a CSV too, useful to paste into your report.
summary_path = os.path.join(RESULTS_DIR, "latency_summary.csv")
summary_df.to_csv(summary_path, index=False)
print(f"\nSummary table saved to: {summary_path}")

# ---------------------------------------------------------------------------
# 5. PLOT 1: AVERAGE LATENCY COMPARISON (bar chart)
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))
methods = summary_df["Method"]
means = summary_df["Mean"]
stds = summary_df["Std Dev"]

bars = ax.bar(methods, means, yerr=stds, capsize=5, color="#4C72B0")
ax.set_ylabel("Average Inference Latency (ms)")
ax.set_title("Average Inference Latency by Deployment Method")
ax.set_xticks(range(len(methods)))
ax.set_xticklabels(methods, rotation=20, ha="right")

# Add value labels on top of each bar
for bar, mean in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(stds) * 0.05,
             f"{mean:.1f}", ha="center", va="bottom")

plt.tight_layout()
latency_plot_path = os.path.join(RESULTS_DIR, "latency_comparison.png")
plt.savefig(latency_plot_path, dpi=150)
print(f"Latency comparison plot saved to: {latency_plot_path}")
plt.close()

# ---------------------------------------------------------------------------
# 6. PLOT 2: LATENCY DISTRIBUTION (box plot) - shows spread/variability too
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))
box_data = [df["Inference Latency (ms)"].values for df in data.values()]
try:
    # Newer matplotlib (>=3.9) renamed this parameter to tick_labels
    ax.boxplot(box_data, tick_labels=list(data.keys()))
except TypeError:
    # Older matplotlib versions use "labels"
    ax.boxplot(box_data, labels=list(data.keys()))
ax.set_ylabel("Inference Latency (ms)")
ax.set_title("Latency Distribution by Deployment Method")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
boxplot_path = os.path.join(RESULTS_DIR, "latency_distribution.png")
plt.savefig(boxplot_path, dpi=150)
print(f"Latency distribution plot saved to: {boxplot_path}")
plt.close()

print("\nDone! Check the 'results' folder for the PNG plots and the summary CSV.")
print("NOTE: CPU%, Memory%, and Network I/O were not captured in this run and")
print("are therefore not plotted. Mention this explicitly as a limitation in your report.")