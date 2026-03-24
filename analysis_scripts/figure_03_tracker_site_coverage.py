"""
figure_03_tracker_site_coverage.py
------------------------------------
Analyses how many sites in the top-525 crawl collected *no* privacy-related
data at all (or no monetization/tracker data specifically).

Two crawl datasets are compared side-by-side for each of the 10 countries:
  - Common Top 525:  the same 525 US-popular sites crawled from every country.
  - Country Top 525: each country's own locally-popular top-525 sites.

The main output is a pair of horizontal stacked bar charts — one per dataset —
showing what percentage of sites had data collected vs. did not.

Run from the project root:
    python analysis/PaperAnalysis/figure_03_tracker_site_coverage.py
"""

import os
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tldextract
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

from modules.config import countries, country_mapping


# ---------------------------------------------------------------------------
# URL utility
# ---------------------------------------------------------------------------

def get_main_domain(url):
    """Return only the registrable domain name from a URL.

    Example: 'https://news.bbc.co.uk/article' -> 'bbc'
    """
    return tldextract.extract(url).domain


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

# Load the full combined dataset once at module level so it can be reused
# by multiple functions without re-reading from disk each time.
_ALL_ENTRIES_PATH = r"analysis_data\entries\combined_all_countries.csv"
_raw_df = pd.read_csv(_ALL_ENTRIES_PATH)

# Common Top 525: entries from the shared US-popular site list,
# keeping only rows where the crawl succeeded across all countries.
df_common_525 = _raw_df[
    (_raw_df['countrySpecificEntries'] == False) &
    (_raw_df['CountriesCrawlFailed'] == False)
]

# Country Top 525: entries from each country's own top-525 list
# (plus US entries, since the US list is the same in both datasets),
# keeping only rows where that country's crawl succeeded.
df_country_525 = _raw_df[
    ((_raw_df['countrySpecificEntries'] == True) | (_raw_df['country'] == "unitedstates")) &
    (_raw_df['CrawlFailed'] == False)
]


def get_errors():
    """Load crawl error logs and classify each errored URL as belonging to the
    common crawl list (US top-525) or the country-specific crawl list.

    The error logs record sites that could not be loaded during the crawl.
    We need to subtract these from the total 525 sites when computing the
    proportion that collected no data (to avoid counting errors as 'no data').

    Returns
    -------
    country_525_errors : dict[str, list[str]]
        Errored URLs per country for the country-specific crawl.
    common_525_errors : dict[str, list[str]]
        Errored URLs per country for the common (US-popular) crawl.
    """
    error_log_folder = r"analysis_data\error-logging"
    crawl_list_folder = r"analysis_data\crawl_list"

    # Build a dict of {country: [site_url, ...]} from the crawl list CSVs.
    crawl_lists = {}
    for country in countries:
        crawl_list_path = os.path.join(crawl_list_folder, f"{country}-top-525.csv")
        df_sites = pd.read_csv(crawl_list_path)
        crawl_lists[country] = df_sites["Site URL"].tolist()

    country_525_errors = {}
    common_525_errors = {}

    for filename in os.listdir(error_log_folder):
        if not filename.startswith("error-logging"):
            continue

        country = filename.split("_")[1]
        error_log_path = os.path.join(error_log_folder, filename)

        with open(error_log_path, "r") as f:
            error_log = json.load(f)

        # Each error log maps error_type -> [list of failed URLs].
        # Classify each failed URL as country-specific or common (US list).
        country_errors = []
        common_errors = []
        for error_type, failed_urls in error_log.items():
            for url in failed_urls:
                if url in crawl_lists[country]:
                    country_errors.append(url)
                if url in crawl_lists["unitedstates"]:
                    common_errors.append(url)

        country_525_errors[country] = country_errors
        common_525_errors[country] = common_errors

    return country_525_errors, common_525_errors


def get_sites_w_0_collection():
    """Count sites that loaded successfully but collected no privacy data at all.

    For each country, we know:
      total sites = 525
      errored sites = sites that failed to load (excluded from analysis)
      sites with data = unique rootUrls that appear in the entries dataset

    sites with NO data = 525 - errored - sites_with_data

    Returns
    -------
    dict[str, dict]
        Keys per country: 'common_no_data', 'country_no_data',
        'common_no_data_prop', 'country_no_data_prop'.
    """
    country_525_errors, common_525_errors = get_errors()
    results = {}

    print("Computing zero-collection site counts...")
    for country in countries:
        print(f"  {country}")

        # --- Common Top 525 ---
        sites_with_data_common = df_common_525[df_common_525['country'] == country]['rootUrl'].nunique()
        errors_common = len(common_525_errors.get(country, []))
        no_data_common = 525 - errors_common - sites_with_data_common
        print(f"    common:  {no_data_common} = 525 - {errors_common} errors - {sites_with_data_common} with data")

        # --- Country Top 525 ---
        sites_with_data_country = df_country_525[df_country_525['country'] == country]['rootUrl'].nunique()
        errors_country = len(country_525_errors.get(country, []))
        no_data_country = 525 - errors_country - sites_with_data_country
        print(f"    country: {no_data_country} = 525 - {errors_country} errors - {sites_with_data_country} with data")

        valid_common = 525 - errors_common
        valid_country = 525 - errors_country
        results[country] = {
            "common_no_data":       no_data_common,
            "country_no_data":      no_data_country,
            "common_no_data_prop":  no_data_common  / valid_common,
            "country_no_data_prop": no_data_country / valid_country,
        }

    return results


def get_sites_w_0_monetization_collection():
    """Same as get_sites_w_0_collection(), but only counts sites that collected
    no *monetization* (advertising/tracking) data specifically.

    Returns
    -------
    dict[str, dict]
        Same structure as get_sites_w_0_collection().
    """
    country_525_errors, common_525_errors = get_errors()
    results = {}

    print("Computing zero-monetization site counts...")
    for country in countries:
        print(f"  {country}")

        # Filter to monetization rows only before counting unique sites.
        monetization_common = df_common_525[
            (df_common_525['country'] == country) &
            (df_common_525['permission'] == "monetization")
        ]
        monetization_country = df_country_525[
            (df_country_525['country'] == country) &
            (df_country_525['permission'] == "monetization")
        ]

        sites_with_data_common  = monetization_common['rootUrl'].nunique()
        sites_with_data_country = monetization_country['rootUrl'].nunique()

        errors_common  = len(common_525_errors.get(country, []))
        errors_country = len(country_525_errors.get(country, []))

        no_data_common  = 525 - errors_common  - sites_with_data_common
        no_data_country = 525 - errors_country - sites_with_data_country
        print(f"    common:  {no_data_common} = 525 - {errors_common} - {sites_with_data_common}")
        print(f"    country: {no_data_country} = 525 - {errors_country} - {sites_with_data_country}")

        valid_common  = 525 - errors_common
        valid_country = 525 - errors_country
        results[country] = {
            "common_no_data":       no_data_common,
            "country_no_data":      no_data_country,
            "common_no_data_prop":  no_data_common  / valid_common,
            "country_no_data_prop": no_data_country / valid_country,
        }

    print(results)
    return results


# ---------------------------------------------------------------------------
# Chart style helper
# ---------------------------------------------------------------------------

def set_paper_style():
    """Apply a clean, publication-ready matplotlib style."""
    plt.style.use('seaborn-v0_8-paper')
    sns.set_palette("husl")
    plt.rcParams.update({
        'font.family':    'serif',
        'font.size':      11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.dpi':     100,
        'figure.figsize': (8, 6),
    })


# ---------------------------------------------------------------------------
# Paper figure: horizontal stacked bar charts
# ---------------------------------------------------------------------------

def plot_tracker_site_coverage(monetization=False):
    """Create two horizontal stacked bar charts for the paper.

    Each chart shows, per country, what percentage of sites had data collected
    vs. did not. One chart covers the Common Top 525 sites, the other the
    Country-specific Top 525 sites.

    Parameters
    ----------
    monetization : bool
        If True, count only sites with *no monetization data* (trackers).
        If False, count sites with *no data collection at all*.

    Returns
    -------
    fig_common, fig_country : matplotlib.figure.Figure
        Two separate figure objects (one per crawl dataset).
    """
    set_paper_style()
    plt.style.use('default')
    plt.rcParams.update({
        'font.family':      'serif',
        'font.size':        11,
        'axes.labelsize':   14,
        'axes.titlesize':   16,
        'axes.titleweight': 'bold',
        'axes.grid':        False,
        'figure.facecolor': 'white',
        'axes.facecolor':   'white',
        'figure.dpi':       300,
    })

    # Two shades of blue: darker = sites with data, lighter = sites without.
    cmap = plt.get_cmap('Blues')
    color_with_data    = cmap(0.35)
    color_without_data = cmap(0.15)

    # Retrieve per-country proportions.
    if monetization:
        results = get_sites_w_0_monetization_collection()
    else:
        results = get_sites_w_0_collection()

    display_labels = [country_mapping.get(c, c) for c in countries]

    # Convert proportions to percentages for both crawl types.
    common_with_data_pct    = [100 - results[c]["common_no_data_prop"]  * 100 for c in countries]
    common_without_data_pct = [      results[c]["common_no_data_prop"]  * 100 for c in countries]
    country_with_data_pct   = [100 - results[c]["country_no_data_prop"] * 100 for c in countries]
    country_without_data_pct = [     results[c]["country_no_data_prop"] * 100 for c in countries]

    # Y positions: one row per country.
    y_pos = np.arange(len(countries))

    # Legend labels depend on whether we are analysing all data or monetization only.
    if monetization:
        label_with    = 'Sites with Trackers'
        label_without = 'Sites without Trackers'
    else:
        label_with    = 'Sites with Data Collection'
        label_without = 'Sites without Data Collection'

    legend_handles = [
        Patch(facecolor=color_with_data,    edgecolor='black', label=label_with),
        Patch(facecolor=color_without_data, edgecolor='black', label=label_without),
    ]

    def _build_chart(ax, with_data_pct, without_data_pct, title):
        """Draw one horizontal stacked bar chart onto the given axes."""
        bars_with = ax.barh(y_pos, with_data_pct,
                            color=color_with_data, edgecolor='black',
                            label=label_with)
        bars_without = ax.barh(y_pos, without_data_pct,
                                left=with_data_pct,
                                color=color_without_data, edgecolor='black',
                                label=label_without)

        # Annotate each segment with its percentage value.
        for bar, pct in zip(bars_with, with_data_pct):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{pct:.1f}%", ha="center", va="center", color="black", fontsize=12)

        for bar, pct in zip(bars_without, without_data_pct):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{pct:.1f}%", ha="center", va="center", color="black", fontsize=12)

        ax.invert_yaxis()   # first country at top
        ax.set_yticks(y_pos)
        ax.set_yticklabels(display_labels)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage (%)')
        ax.set_title(title, fontsize=16, pad=35)
        ax.xaxis.grid(True, linestyle='-', alpha=0.3, color=color_without_data)
        ax.legend(handles=legend_handles, loc='upper center',
                  bbox_to_anchor=(0.5, 1.175), ncol=2, frameon=True)

    # Build Figure 1: Common Top 525
    fig_common, ax_common = plt.subplots(figsize=(10, 7))
    _build_chart(
        ax_common,
        common_with_data_pct,
        common_without_data_pct,
        ('Proportion of Sites with / without Trackers\n(Common Top 525)'
         if monetization else
         'Proportion of Sites with / without Data Collection\n(Common Top 525)'),
    )
    plt.tight_layout()
    plt.subplots_adjust(left=0.2, bottom=0.20, top=0.75)

    # Build Figure 2: Country Top 525
    fig_country, ax_country = plt.subplots(figsize=(10, 7))
    _build_chart(
        ax_country,
        country_with_data_pct,
        country_without_data_pct,
        ('Proportion of Sites with / without Trackers\n(Country-specific Top 525)'
         if monetization else
         'Proportion of Sites with / without Data Collection\n(Country-specific Top 525)'),
    )
    plt.tight_layout()
    plt.subplots_adjust(left=0.2, bottom=0.20, top=0.75)

    return fig_common, fig_country


if __name__ == "__main__":
    fig_common, fig_country = plot_tracker_site_coverage(monetization=True)
    plt.show()
    # fig_common.savefig(
    #     "analysis/Paper_figs/4_2_ProportionPlot_DataVsNoData_common_top_525_monetization.png",
    #     dpi=300, bbox_inches="tight",
    # )
    # fig_country.savefig(
    #     "analysis/Paper_figs/4_2_ProportionPlot_DataVsNoData_country_top_525_monetization.png",
    #     dpi=300, bbox_inches="tight",
    # )
