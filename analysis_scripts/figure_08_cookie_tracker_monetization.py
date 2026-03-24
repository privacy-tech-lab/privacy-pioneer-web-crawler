"""
04_cookie_tracker_monetization.py
----------------------------------
Visualises how consent banners affect monetization tracker activity across
Germany, Spain, and the United States.

Background
----------
Each site was crawled twice:
  1. "Consent" crawl  — the user clicked "Accept" on any cookie banner.
  2. "No-action" crawl — the user ignored the banner (or no banner appeared).

This script compares the number of monetization-related tracking requests
(advertising, analytics, social) recorded in each scenario, for the top N
parent companies in each country.

A higher no-action / consent ratio means the banner reduced tracker activity.

Data source
-----------
Raw (unfiltered) cookie crawl data from analysis/Cookie_Analysis/data_unfiltered/.
First-party requests (where the tracker domain matches the site domain) are
excluded. Sites that errored during the crawl are also excluded.

Run from the project root:
    python analysis/PaperAnalysis/04_cookie_tracker_monetization.py
"""

import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tldextract
from matplotlib.patches import Patch


# ---------------------------------------------------------------------------
# Constants — adjust these to change the analysis scope
# ---------------------------------------------------------------------------

# How many top parent companies to show per country.
N_TOP_COMPANIES = 30

# The three sub-categories within the "monetization" permission.
TRACKER_TYPES = ['advertising', 'social', 'analytics']

# Colours for the "consent" bars (darker = user accepted the banner).
CONSENT_COLORS = {
    'advertising': '#0072B2',   # deep blue
    'social':      '#009E73',   # deep green
    'analytics':   '#D55E00',   # deep orange
}

# Colours for the "no-action" bars (lighter = banner was ignored).
NO_ACTION_COLORS = {
    'advertising': '#66b3ff',   # light blue
    'social':      '#66cc99',   # light green
    'analytics':   '#FF8C66',   # light orange
}


# ---------------------------------------------------------------------------
# Data-loading helpers
# ---------------------------------------------------------------------------

def _load_json(path):
    """Read and return the contents of a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def get_errored_sites():
    """Return the set of site URLs that errored during the cookie crawl.

    Error logs are per-country, per-condition (consent / no-action). We pool
    all errored URLs into one set so they can be excluded from all dataframes.

    Returns
    -------
    set[str]
        Site URLs that should be excluded from analysis.
    """
    error_log_paths = {
        'Germany accept':    r"analysis_data\cookie_analysis\error-logging_Germany_accept.json",
        'Germany crawler':   r"analysis_data\cookie_analysis\error-logging_Germany_crawler.json",
        'Spain accept':      r"analysis_data\cookie_analysis\error-logging_Spain_accept.json",
        'Spain crawler':     r"analysis_data\cookie_analysis\error-logging_Spain_crawler.json",
        'US accept':         r"analysis_data\cookie_analysis\error-logging_UnitedStates_accept.json",
        'US crawler':        r"analysis_data\cookie_analysis\error-logging_UnitedStates_crawler.json",
    }

    errored_urls = set()
    for label, path in error_log_paths.items():
        error_log = _load_json(path)
        for failed_urls in error_log.values():
            errored_urls.update(failed_urls)

    print(f"Total unique errored sites across all logs: {len(errored_urls)}")
    return errored_urls


def _get_main_domain(url):
    """Return only the registrable domain name (e.g. 'bbc' from 'news.bbc.co.uk')."""
    return tldextract.extract(url).domain


def _is_third_party(request_url, root_url):
    """Return True if the network request goes to a different domain than the page."""
    request_domain = tldextract.extract(request_url).registered_domain
    page_domain    = tldextract.extract(root_url).registered_domain
    return request_domain != page_domain


def load_cookie_data_third_party_only():
    """Load all six raw cookie-crawl CSV files (Germany, Spain, US × consent/no-action)
    and add an 'is_third_party' column to each.

    Only third-party requests are relevant for parent-company analysis — first-party
    requests (where the tracker is the site itself) are not external data collectors.

    Returns
    -------
    Six DataFrames in the order:
        de_consent, de_no_action, sp_consent, sp_no_action, us_consent, us_no_action
    """
    data_paths = {
        'de_consent':   r"analysis_data\cookie_analysis\entries_Germany_accept.csv",
        'de_no_action': r"analysis_data\cookie_analysis\entries_Germany_crawler.csv",
        'sp_consent':   r"analysis_data\cookie_analysis\entries_Spain_accept.csv",
        'sp_no_action': r"analysis_data\cookie_analysis\entries_Spain_crawler.csv",
        'us_consent':   r"analysis_data\cookie_analysis\entries_UnitedStates_accept.csv",
        'us_no_action': r"analysis_data\cookie_analysis\entries_UnitedStates_crawler.csv",
    }

    dataframes = {}
    for key, path in data_paths.items():
        df = pd.read_csv(path)
        df['is_third_party'] = df.apply(
            lambda row: _is_third_party(row['requestUrl'], row['rootUrl']), axis=1
        )
        dataframes[key] = df

    return (
        dataframes['de_consent'], dataframes['de_no_action'],
        dataframes['sp_consent'], dataframes['sp_no_action'],
        dataframes['us_consent'], dataframes['us_no_action'],
    )


def exclude_errored_sites(dataframes, errored_urls):
    """Remove rows belonging to errored sites from a list of DataFrames.

    Parameters
    ----------
    dataframes : list[pd.DataFrame]
        Each DataFrame must have a 'rootUrl' column.
    errored_urls : set[str]
        URLs to exclude (matched by main domain to handle http/https variants).

    Returns
    -------
    list[pd.DataFrame]   Same order as input, with errored rows removed.
    """
    errored_domains = {_get_main_domain(url) for url in errored_urls}
    cleaned = []
    for df in dataframes:
        df = df.copy()
        df['_root_domain'] = df['rootUrl'].apply(_get_main_domain)
        df = df[~df['_root_domain'].isin(errored_domains)].drop(columns='_root_domain')
        cleaned.append(df)

    for original, filtered in zip(dataframes, cleaned):
        print(f"  {len(original):>6} rows → {len(filtered):>6} rows after removing errored sites")

    return cleaned


def load_clean_cookie_data():
    """Load cookie data with first-party requests and errored sites removed.

    This is the main data-loading entry point called by the plotting function.

    Returns
    -------
    Six cleaned DataFrames:
        de_consent, de_no_action, sp_consent, sp_no_action, us_consent, us_no_action
    """
    errored_urls = get_errored_sites()

    (de_consent, de_no_action,
     sp_consent, sp_no_action,
     us_consent, us_no_action) = load_cookie_data_third_party_only()

    all_dfs = [de_consent, de_no_action, sp_consent, sp_no_action, us_consent, us_no_action]
    cleaned = exclude_errored_sites(all_dfs, errored_urls)

    return tuple(cleaned)


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _build_tracker_type_table(df, top_companies, tracker_types):
    """Count entries per (parent company, tracker type) for the given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Already filtered to a single permission type (e.g. 'monetization').
    top_companies : pd.Index
        The parent companies to include (others are dropped).
    tracker_types : list[str]
        Columns to include in the output (e.g. ['advertising', 'social', 'analytics']).

    Returns
    -------
    pd.DataFrame
        Rows = companies, columns = tracker types, values = entry counts.
    """
    filtered = df[df['parentCompany'].isin(top_companies)]
    table = (
        filtered
        .groupby(['parentCompany', 'typ'])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=tracker_types, fill_value=0)
        .reindex(top_companies)
    )
    return table


def _sort_companies_by_total(consent_table, no_action_table):
    """Return company names sorted by their combined entry count (ascending).

    Ascending order is used so that the most active company appears at the
    top of a horizontal bar chart (matplotlib draws from bottom to top).
    """
    total_per_company = consent_table.sum(axis=1) + no_action_table.sum(axis=1)
    return total_per_company.sort_values(ascending=True).index


def _print_ratio_summary(consent_df, no_action_df, country_label):
    """Print a table showing how much the consent banner reduced tracker counts
    per site and per tracker type.

    The ratio is: no_action_count / consent_count.
    A ratio > 1 means more trackers fired when the banner was ignored,
    so the banner did reduce tracking. A ratio < 1 means fewer trackers
    fired even without banner interaction.

    Parameters
    ----------
    consent_df, no_action_df : pd.DataFrame
        Both filtered to monetization rows only.
    country_label : str
        Used in the printed header (e.g. "Germany").

    Returns
    -------
    site_table : pd.DataFrame
    total_ratio : float
    """
    # Count total tracker events per site for each condition.
    consent_per_site   = consent_df.groupby('rootUrl').size().rename('consent')
    no_action_per_site = no_action_df.groupby('rootUrl').size().rename('no_action')

    site_table = pd.concat([consent_per_site, no_action_per_site], axis=1).fillna(0)
    site_table['ratio'] = site_table.apply(
        lambda row: row['no_action'] / row['consent'] if row['consent'] else float('nan'),
        axis=1,
    )

    # Also break down by tracker type.
    for typ in TRACKER_TYPES:
        consent_typ   = consent_df[consent_df['typ'] == typ].groupby('rootUrl').size().rename(f'{typ}_consent')
        no_action_typ = no_action_df[no_action_df['typ'] == typ].groupby('rootUrl').size().rename(f'{typ}_no_action')
        site_table = site_table.join(consent_typ, how='left').join(no_action_typ, how='left').fillna(0)
        site_table[f'{typ}_ratio'] = site_table.apply(
            lambda row, t=typ: (
                row[f'{t}_no_action'] / row[f'{t}_consent']
                if row[f'{t}_consent'] else float('nan')
            ),
            axis=1,
        )

    site_table = site_table.sort_values('ratio', ascending=False)

    total_consent   = site_table['consent'].sum()
    total_no_action = site_table['no_action'].sum()
    total_ratio     = total_no_action / total_consent if total_consent else float('nan')

    print(f"\n{'='*70}")
    print(f"  {country_label} — Consent Banner Impact Summary")
    print(f"{'='*70}")
    print(f"  TOTAL : {total_no_action:.0f} (no action) / {total_consent:.0f} (consent) = {total_ratio:.2f}x")
    print(f"\n  {'Type':<14} {'Consent':>9} {'No-Action':>10} {'Ratio':>7}")
    print(f"  {'-'*44}")
    for typ in TRACKER_TYPES:
        tc = site_table[f'{typ}_consent'].sum()
        tn = site_table[f'{typ}_no_action'].sum()
        tr = tn / tc if tc else float('nan')
        print(f"  {typ.capitalize():<14} {tc:>9.0f} {tn:>10.0f} {tr:>7.2f}x")

    col_w = 42
    print(f"\n  Per-site breakdown (sorted by overall ratio, descending):")
    header = (
        f"  {'Site':<{col_w}} {'Consent':>8} {'NoAct':>7} {'Ratio':>6}  "
        + "  ".join(f"{t[:3].capitalize()}C {t[:3].capitalize()}N {t[:3].capitalize()}R" for t in TRACKER_TYPES)
    )
    print(f"\n{header}")
    print(f"  {'-' * (len(header) - 2)}")
    for site, row in site_table.iterrows():
        typ_parts = "  ".join(
            f"{row[f'{t}_consent']:>4.0f} {row[f'{t}_no_action']:>4.0f} "
            + (f"{row[f'{t}_ratio']:>4.1f}x" if not pd.isna(row[f'{t}_ratio']) else "   N/A")
            for t in TRACKER_TYPES
        )
        ratio_str = f"{row['ratio']:>5.2f}x" if not pd.isna(row['ratio']) else "   N/A"
        print(f"  {site:<{col_w}} {row['consent']:>8.0f} {row['no_action']:>7.0f} {ratio_str}  {typ_parts}")

    return site_table, total_ratio


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def _draw_country_chart(ax, consent_table, no_action_table,
                        country_title, subtitle, show_y_label=False):
    """Draw one horizontal grouped-stacked bar chart for a single country.

    Each company gets two paired bars:
      - Top bar    (consent)   = trackers fired after the user accepted the banner.
      - Bottom bar (no-action) = trackers fired when the banner was ignored.

    Both bars are stacked by tracker type (advertising / analytics / social).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    consent_table, no_action_table : pd.DataFrame
        Rows = companies (sorted), columns = tracker types, values = counts.
    country_title : str    e.g. 'Trackers - Germany'
    subtitle : str         e.g. 'Entries by Parent Company (Top 30)'
    show_y_label : bool    If True, show the 'Parent Company' y-axis label.
    """
    companies = consent_table.index
    y = np.arange(len(companies))
    bar_height = 0.35   # height of each individual bar

    # Draw consent bars (top of each pair), stacked by tracker type.
    left_offsets = np.zeros(len(companies))
    for tracker_type in TRACKER_TYPES:
        widths = consent_table[tracker_type].values
        ax.barh(y + bar_height / 2, widths, bar_height,
                left=left_offsets, color=CONSENT_COLORS[tracker_type])
        left_offsets += widths

    # Draw no-action bars (bottom of each pair), stacked by tracker type.
    left_offsets = np.zeros(len(companies))
    for tracker_type in TRACKER_TYPES:
        widths = no_action_table[tracker_type].values
        ax.barh(y - bar_height / 2, widths, bar_height,
                left=left_offsets, color=NO_ACTION_COLORS[tracker_type])
        left_offsets += widths

    ax.set_title(country_title, pad=25)
    ax.set_yticks(y)
    ax.set_yticklabels(companies)
    if show_y_label:
        ax.set_ylabel('Parent Company')
    ax.set_xlabel('Number of Entries')
    ax.set_xlim(0, 90)

    # Subtitle sits just above the title.
    ax.text(0.5, 1.012, subtitle, transform=ax.transAxes,
            ha='center', va='bottom', fontsize=14, fontweight='bold')

    # Legend: dark shade = consent, light shade = no-action.
    legend_handles = [
        Patch(facecolor=CONSENT_COLORS['advertising'],   label='Advertising — Consent'),
        Patch(facecolor=NO_ACTION_COLORS['advertising'], label='Advertising — No Action'),
        Patch(facecolor=CONSENT_COLORS['analytics'],     label='Analytics — Consent'),
        Patch(facecolor=NO_ACTION_COLORS['analytics'],   label='Analytics — No Action'),
        Patch(facecolor=CONSENT_COLORS['social'],        label='Social — Consent'),
        Patch(facecolor=NO_ACTION_COLORS['social'],      label='Social — No Action'),
    ]
    ax.legend(handles=legend_handles, loc='lower right', frameon=True,
              ncol=1, labelspacing=0.5)


def plot():
    """Run the full analysis and display the chart.

    Steps
    -----
    1. Load and clean the cookie crawl data.
    2. Filter to monetization rows only.
    3. Identify the top N parent companies per country.
    4. Print consent-banner impact ratio tables to the console.
    5. Display a 1×3 figure of horizontal stacked bar charts.
    """
    # --- Load data ---
    (de_consent, de_no_action,
     sp_consent, sp_no_action,
     us_consent, us_no_action) = load_clean_cookie_data()

    # --- Filter to monetization permission only ---
    de_consent   = de_consent[de_consent['permission']   == 'monetization']
    de_no_action = de_no_action[de_no_action['permission'] == 'monetization']
    sp_consent   = sp_consent[sp_consent['permission']   == 'monetization']
    sp_no_action = sp_no_action[sp_no_action['permission'] == 'monetization']
    us_consent   = us_consent[us_consent['permission']   == 'monetization']
    us_no_action = us_no_action[us_no_action['permission'] == 'monetization']

    # --- Identify top N parent companies per country (by combined entry count) ---
    top_de = pd.concat([de_consent, de_no_action])['parentCompany'].value_counts().head(N_TOP_COMPANIES).index
    top_sp = pd.concat([sp_consent, sp_no_action])['parentCompany'].value_counts().head(N_TOP_COMPANIES).index
    top_us = pd.concat([us_consent, us_no_action])['parentCompany'].value_counts().head(N_TOP_COMPANIES).index

    # --- Build per-company, per-tracker-type count tables ---
    de_consent_table   = _build_tracker_type_table(de_consent,   top_de, TRACKER_TYPES)
    de_no_action_table = _build_tracker_type_table(de_no_action, top_de, TRACKER_TYPES)
    sp_consent_table   = _build_tracker_type_table(sp_consent,   top_sp, TRACKER_TYPES)
    sp_no_action_table = _build_tracker_type_table(sp_no_action, top_sp, TRACKER_TYPES)
    us_consent_table   = _build_tracker_type_table(us_consent,   top_us, TRACKER_TYPES)
    us_no_action_table = _build_tracker_type_table(us_no_action, top_us, TRACKER_TYPES)

    # Sort companies so the most active appears at the top of the chart.
    de_order = _sort_companies_by_total(de_consent_table, de_no_action_table)
    sp_order = _sort_companies_by_total(sp_consent_table, sp_no_action_table)
    us_order = _sort_companies_by_total(us_consent_table, us_no_action_table)

    de_consent_table,   de_no_action_table = de_consent_table.loc[de_order],   de_no_action_table.loc[de_order]
    sp_consent_table,   sp_no_action_table = sp_consent_table.loc[sp_order],   sp_no_action_table.loc[sp_order]
    us_consent_table,   us_no_action_table = us_consent_table.loc[us_order],   us_no_action_table.loc[us_order]

    # --- Print composition tables ---
    print("Germany Monetization — Consent Tracker Composition:")
    print(de_consent_table)
    print("\nGermany Monetization — No-Action Tracker Composition:")
    print(de_no_action_table)
    print("\nSpain Monetization — Consent Tracker Composition:")
    print(sp_consent_table)
    print("\nSpain Monetization — No-Action Tracker Composition:")
    print(sp_no_action_table)
    print("\nUS Monetization — Consent Tracker Composition:")
    print(us_consent_table)
    print("\nUS Monetization — No-Action Tracker Composition:")
    print(us_no_action_table)

    # --- Print consent-banner impact ratios ---
    # We pass the monetization-filtered DataFrames (not the tables) because
    # _print_ratio_summary also needs the rootUrl column for per-site analysis.
    de_monet_consent   = de_consent[de_consent['parentCompany'].isin(top_de)]
    de_monet_no_action = de_no_action[de_no_action['parentCompany'].isin(top_de)]
    sp_monet_consent   = sp_consent[sp_consent['parentCompany'].isin(top_sp)]
    sp_monet_no_action = sp_no_action[sp_no_action['parentCompany'].isin(top_sp)]
    us_monet_consent   = us_consent[us_consent['parentCompany'].isin(top_us)]
    us_monet_no_action = us_no_action[us_no_action['parentCompany'].isin(top_us)]

    _, de_ratio = _print_ratio_summary(de_monet_consent, de_monet_no_action, "Germany")
    _, sp_ratio = _print_ratio_summary(sp_monet_consent, sp_monet_no_action, "Spain")
    _, us_ratio = _print_ratio_summary(us_monet_consent, us_monet_no_action, "United States")

    print(f"\n{'='*70}")
    print("  Cross-country banner impact comparison")
    print(f"{'='*70}")
    print(f"  Germany : {de_ratio:.2f}x")
    print(f"  Spain   : {sp_ratio:.2f}x")
    print(f"  US      : {us_ratio:.2f}x")
    print(f"  DE/US ratio: {de_ratio/us_ratio:.2f}x  |  SP/US ratio: {sp_ratio/us_ratio:.2f}x")

    # --- Draw charts ---
    plt.style.use('default')
    plt.rcParams.update({
        'font.family':      'serif',
        'font.size':        12,
        'axes.labelsize':   14,
        'axes.titlesize':   16,
        'axes.titleweight': 'bold',
        'axes.grid':        True,
        'grid.linestyle':   '--',
        'grid.linewidth':   0.6,
        'grid.alpha':       0.7,
        'figure.facecolor': 'white',
        'axes.facecolor':   'white',
        'figure.dpi':       300,
    })

    fig, axes = plt.subplots(ncols=3, figsize=(20, 8))

    subtitle = f'Entries by Parent Company (Top {N_TOP_COMPANIES})'
    _draw_country_chart(axes[0], de_consent_table, de_no_action_table,
                        'Trackers — Germany', subtitle, show_y_label=True)
    _draw_country_chart(axes[1], sp_consent_table, sp_no_action_table,
                        'Trackers — Spain', subtitle)
    _draw_country_chart(axes[2], us_consent_table, us_no_action_table,
                        'Trackers — United States', subtitle)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.4)
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    plot()
