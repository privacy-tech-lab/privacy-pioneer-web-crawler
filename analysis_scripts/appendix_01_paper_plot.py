"""
01_paper_plot.py
----------------
Produces a cumulative histogram of network traffic observation durations.

For each (site, country) pair in the dataset, we compute how long (in seconds)
the crawler observed network traffic — from the first to the last recorded
request. The chart shows what percentage of sites were fully observed within
a given number of seconds, with a vertical line marking the 60th percentile.

Run from the project root:
    python analysis/PaperAnalysis/01_paper_plot.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Chart style
# ---------------------------------------------------------------------------
plt.style.use('default')
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.linewidth': 0.4,
    'grid.alpha': 0.7,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'figure.dpi': 300,
})


def main():
    # -----------------------------------------------------------------------
    # Load data
    # -----------------------------------------------------------------------
    all_entries_path = r"analysis_data\entries\combined_all_countries.csv"
    all_entries = pd.read_csv(all_entries_path)

    # Remove duplicate entries flagged during preprocessing.
    all_entries = all_entries[all_entries['potentialDuplicates'] == 0]

    # -----------------------------------------------------------------------
    # Compute observation duration per (site, country) pair
    # Each row in all_entries is one network request with a timestamp (timestp,
    # in milliseconds). We find the earliest and latest request per site and
    # country, then compute the span in seconds.
    # -----------------------------------------------------------------------
    time_span_df = (
        all_entries
        .groupby(['rootUrl', 'country'])
        .agg(min_time=('timestp', 'min'), max_time=('timestp', 'max'))
        .reset_index()
    )
    time_span_df['time_span_seconds'] = (
        (time_span_df['max_time'] - time_span_df['min_time']) / 1_000
    )

    durations = time_span_df['time_span_seconds']
    x_max = 60  # cap the x-axis at 60 seconds for readability
    percentile_60 = np.percentile(durations, 60)

    # -----------------------------------------------------------------------
    # Plot cumulative histogram
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.hist(
        durations,
        bins=40,
        range=(durations.min(), x_max),
        cumulative=True,
        density=True,           # normalise so y-axis shows proportion (0–1)
        color='#2197D9',
        edgecolor='black',
        linewidth=0.7,
    )

    # Vertical dashed line at the 60th percentile
    ax.axvline(x=percentile_60, linestyle='--', linewidth=1.1, color='red')

    ax.set_title("Network Traffic Collection")
    ax.set_xlabel("Observation Duration (Seconds)")
    ax.set_ylabel("Percentage of Sites")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
