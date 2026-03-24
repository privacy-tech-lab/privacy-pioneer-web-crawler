"""
05_parentComp_pie_country.py
----------------------------
Generates a 2×5 grid of pie charts showing which parent companies (data
collectors) appear most frequently across each country's own top-525 sites.

Dataset used:
  - Country-specific Top 525: each country's locally-popular sites, plus the
    US entries (since the US list is the same in both crawl types).
  - Duplicate entries are excluded.

Each pie chart shows the top companies for one country, with slices smaller
than THRESHOLD% merged into an "Other" category. A legend beside each chart
lists company names with their percentages. All companies that appear in any
country share a consistent colour so the same company looks the same across
all 10 charts.

Run from the project root:
    python analysis/PaperAnalysis/05_parentComp_pie_country.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Slices that represent less than THRESHOLD % of a country's total are merged
# into a single "Other" wedge.
THRESHOLD = 3

# Radius of each pie (values > 1 make the pie larger than the subplot area,
# which is needed here to leave room for the side legends).
PIE_SIZE = 1.2

# All pies start at the 12 o'clock position.
START_ANGLE = 90

COUNTRIES = [
    'australia', 'brazil', 'canada', 'germany', 'india',
    'singapore', 'southafrica', 'southkorea', 'spain', 'unitedstates',
]

COUNTRY_LABELS = {
    'germany':      'Germany',
    'spain':        'Spain',
    'brazil':       'Brazil',
    'unitedstates': 'United States',
    'canada':       'Canada',
    'southkorea':   'South Korea',
    'singapore':    'Singapore',
    'southafrica':  'South Africa',
    'australia':    'Australia',
    'india':        'India',
}

# Number of sites that had crawl errors per country (used to report the
# correct sample size "n = X sites" in each chart's legend title).
ERROR_SITE_COUNTS = {
    'australia': 21, 'brazil': 17, 'canada': 5,  'germany': 26, 'india': 36,
    'singapore': 42, 'southkorea': 22, 'spain': 26, 'southafrica': 22, 'unitedstates': 49,
}


# ---------------------------------------------------------------------------
# Colour palette helpers
# ---------------------------------------------------------------------------

def _lighten_color(hex_color, factor=0.2):
    """Blend a hex colour toward white by the given factor (0 = unchanged, 1 = white)."""
    rgb = np.array(mcolors.to_rgb(hex_color))
    blended = np.ones(3) * factor + rgb * (1 - factor)
    return mcolors.to_hex(blended)


def _build_palette(base_hex, n_colors):
    """Return a list of n_colors hex strings ranging from dark (base_hex) to light.

    The palette is used so the most-common company always gets the darkest shade.
    """
    base_rgb = mcolors.to_rgb(base_hex)
    shades = []
    for i in range(n_colors):
        t = i / (n_colors - 1) if n_colors > 1 else 1.0
        rgb = tuple(1 - t * (1 - comp) for comp in base_rgb)
        shades.append(mcolors.to_hex(rgb))
    return shades[::-1]   # reverse so index 0 = darkest


# Build the base sequential palette (9 shades of navy → light blue).
_base_palette = _build_palette("#0A3D62", n_colors=10)[:-1]   # drop lightest shade
SEQUENTIAL_PALETTE = [_lighten_color(h, factor=0.2) for h in _base_palette]


# ---------------------------------------------------------------------------
# Aggregation helper
# ---------------------------------------------------------------------------

def aggregate_small_slices(counts, labels, threshold):
    """Merge any slice whose share is below `threshold` % into "Other".

    Parameters
    ----------
    counts : list[int]
    labels : list[str]
    threshold : float   e.g. 3 means slices < 3% are merged

    Returns
    -------
    new_counts : list[int]
    new_labels : list[str]
    """
    total = sum(counts)
    new_counts, new_labels, other_total = [], [], 0
    for cnt, lbl in zip(counts, labels):
        if (cnt / total) * 100 >= threshold:
            new_counts.append(cnt)
            new_labels.append(lbl)
        else:
            other_total += cnt
    if other_total:
        new_counts.append(other_total)
        new_labels.append("Other")
    return new_counts, new_labels


# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

def main():
    # -----------------------------------------------------------------------
    # Load and filter data
    # -----------------------------------------------------------------------
    all_entries_path = r"analysis_data\entries\combined_all_countries.csv"
    all_entries = pd.read_csv(all_entries_path)

    # Keep country-specific entries plus US entries (which appear in both lists),
    # and drop any rows flagged as potential duplicates.
    entries_for_analysis = all_entries[
        (
            (all_entries['countrySpecificEntries'] == True) |
            (
                (all_entries['country'] == 'unitedstates') &
                (all_entries['countrySpecificEntries'] == False)
            )
        ) &
        (all_entries['potentialDuplicates'] == 0)
    ]

    # Count how many times each parent company appears per country.
    # Each row represents one data-collection event on one site.
    company_counts_by_country = (
        entries_for_analysis
        .groupby(['parentCompany', 'country'])
        .size()
        .reset_index(name='count')
    )

    # -----------------------------------------------------------------------
    # Build a consistent colour map so each company has the same colour in
    # every country's pie chart.
    # -----------------------------------------------------------------------

    # Collect every company that appears above the threshold in at least one
    # country — these get individual colours. The rest become "Other".
    nominees = set()
    for country in COUNTRIES:
        country_data = company_counts_by_country[company_counts_by_country['country'] == country]
        _, agg_labels = aggregate_small_slices(
            country_data['count'].tolist(),
            country_data['parentCompany'].tolist(),
            threshold=THRESHOLD,
        )
        nominees.update(lbl for lbl in agg_labels if lbl != "Other")

    nominees = sorted(nominees)
    print("Companies that appear above threshold in at least one country:")
    print(nominees)

    # Assign each nominee a colour from the Set3 categorical colour map.
    n_companies = len(nominees)
    cmap = plt.get_cmap('Set3', n_companies)
    company_colors = {
        company: mcolors.to_hex(cmap(i))
        for i, company in enumerate(nominees)
    }
    print("\nColour assignments:", company_colors)

    # Override specific company colours for visual clarity.
    company_colors['Other']      = SEQUENTIAL_PALETTE[-1]   # light grey-blue
    company_colors['nurago']     = '#80b1d3'
    company_colors['Adobe']      = '#d9d9d9'
    company_colors['Facebook']   = '#ccebc5'
    company_colors['cXense']     = '#8dd3c7'
    company_colors['Optimizely'] = '#ffed6f'

    # -----------------------------------------------------------------------
    # Draw pie charts
    # -----------------------------------------------------------------------
    plt.rcParams.update({
        'font.family':      'serif',
        'font.size':        12,
        'axes.labelsize':   14,
        'axes.titlesize':   16,
        'axes.titleweight': 'bold',
        'axes.grid':        True,
        'grid.linestyle':   '--',
        'grid.linewidth':   0.3,
        'grid.alpha':       0.7,
        'figure.facecolor': 'white',
        'axes.facecolor':   'white',
        'figure.dpi':       200,
    })

    fig, axes = plt.subplots(2, 5, figsize=(25, 8))
    axes = axes.flatten()

    for ax, country in zip(axes, COUNTRIES):
        country_data = company_counts_by_country[company_counts_by_country['country'] == country]
        counts = country_data['count'].tolist()
        labels = country_data['parentCompany'].tolist()

        # Merge small slices into "Other".
        agg_counts, agg_labels = aggregate_small_slices(counts, labels, threshold=THRESHOLD)

        # Sort companies by count (descending), but always put "Other" last.
        regular = sorted(
            [(cnt, lbl) for cnt, lbl in zip(agg_counts, agg_labels) if lbl != "Other"],
            key=lambda x: x[0], reverse=True,
        )
        other = [(cnt, lbl) for cnt, lbl in zip(agg_counts, agg_labels) if lbl == "Other"]
        sorted_pairs = regular + other

        sorted_counts, sorted_labels = zip(*sorted_pairs)
        slice_colors = [company_colors[lbl] for lbl in sorted_labels]

        wedges, _ = ax.pie(
            sorted_counts,
            labels=None,          # labels are in the legend, not on the slices
            colors=slice_colors,
            startangle=START_ANGLE,
            wedgeprops={'edgecolor': 'black', 'linewidth': 1.2},
            radius=PIE_SIZE,
        )

        # Build legend entries: "Company — XX.X%"
        total = sum(sorted_counts)
        legend_labels = [
            f"{lbl} — {cnt / total * 100:.1f}%"
            for lbl, cnt in zip(sorted_labels, sorted_counts)
        ]
        legend_title = (
            "Parent Companies\n"
            f"(n = {525 - ERROR_SITE_COUNTS[country]} Sites)"
        )
        leg = ax.legend(
            wedges, legend_labels,
            title=legend_title,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
        )
        leg.get_title().set_multialignment("center")
        leg.get_title().set_ha("center")
        for text in leg.get_texts():
            text.set_fontsize(11)

        ax.set_title(COUNTRY_LABELS[country], fontsize=16, fontweight='bold', pad=10)

    plt.subplots_adjust(wspace=1.1, hspace=-0.1)
    plt.suptitle(
        "Distribution of Parent Companies (Country-specific Top 525)",
        fontsize=20, fontweight='bold', y=0.925, x=0.55, ha='center',
    )
    plt.show()


if __name__ == "__main__":
    main()
