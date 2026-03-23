import pandas as pd
import numpy as np
from datetime import datetime
import os

import matplotlib.pyplot as plt

from modules.utils import clean_url, load_entries, load_err_log
from modules.config import countries
from modules.visualization import scrape_distribution_plot_20, error_distribution_plot_20, scrape_distribution_plot_customize

def count_sites_scraped(df):
    n_sites = df['rootUrl'].nunique()
    print(f"number of unique sites with data collection: {n_sites}")
    return n_sites

def count_errs(err_log, total=1050):
    """Counts the number of err sites

    Args:
        err_log (json): the error log file.
        total (int, optional): number of total sites (to compute proportion). Defaults to 1050.
    """
    
    total_err = 0
    for key, value in err_log.items():
        total_err += len(value)
    print(f"Total error count: {total_err}, which is {total_err/total*100:.2f}% of the total entries")
    return total_err

def inspect_1_site(dfs, site_url):
    """Inspect the entries for a specific site URL.

    Args:
        dfs (pd.DataFrame list): list of entries dataframes.
        site_url (str): the site URL to inspect.
    """
    for df in dfs:
        df.rootUrl_cleaned = df.rootUrl.apply(clean_url)
        site_df = df[df.rootUrl_cleaned == site_url]
        print(site_df)
        print("------")

def count_collection_num(df):
    """Count the number of data collection types for each site

    Args:
        df (pd.DataFrame): entries dataframe.

    Returns:
        dict: dictionary with data collection type as key and list number of occurences of such type for each rootUrl as value.
    """
    unique_typ = list(df.typ.unique())
    data_dict = {typ: [] for typ in unique_typ}
    for site in df.rootUrl.unique():
        site_df = df[df.rootUrl == site]
        for typ in unique_typ:
            data_dict[typ].append(site_df[site_df.typ == typ].shape[0])
            
    return data_dict

def check_scrape_distribution(df, country_url_df, inspect_num=30):
    """
    Checks the distribution of scraped URLs by matching cleaned root URLs in the entries dataframe against the list of site URLs to scrape (e.g. canada-top-525.csv).

    Args:
        df (pd.DataFrame): entries.csv in dataframe.
        country_url_df (pd.DataFrame): {country}-top-525.csv in dataframe.

    Returns:
        None: Prints the indices of matching URLs from the `site_urls` (country-top-525.csv) list.

    Notes:
        - This function uses the `clean_url` function to clean both the 'rootUrl' and 'Site URL' columns for comparison.
    """
    site_urls = country_url_df['Site URL'].values
    
    cleaned_site_urls = [clean_url(url) for url in site_urls]

    # Clean the root URLs in your DataFrame
    df['cleaned_rootUrl'] = df['rootUrl'].apply(clean_url)

    # Match the index of the cleaned site URLs with the cleaned root URLs
    matching_indices = [
        idx for idx, cleaned_url in enumerate(df['cleaned_rootUrl']) if cleaned_url in cleaned_site_urls
    ]

    # To match the indices from the `site_urls` list, we need to know the corresponding index from the cleaned site list
    site_url_indices = sorted(list(set([cleaned_site_urls.index(df['cleaned_rootUrl'].iloc[idx]) for idx in matching_indices])))
    
    if len(site_url_indices) < inspect_num:
        print("Matching Indices from site_urls:", site_url_indices)
    else:
        print_indices = np.linspace(0, len(site_url_indices)-1, 30).astype(int)
        print("Matching Indices from site_urls:", [site_url_indices[i] for i in print_indices])
        
def check_scrape_distribution_visualized(CRAWL_ID):
    
    plot_lst = []

    for us_bool in [False, True]:
        for country in countries:
            sites_crawl_path = f"../data_other/{country}-top-525.csv"
            sites_US_crawl_path = r"../data_other/unitedstates-top-525.csv"
            entries_path = f"../data/crawl_{CRAWL_ID}/entries_{country}_{CRAWL_ID}.csv"
            
            if us_bool:
                df_sites = pd.read_csv(sites_crawl_path)
            else:
                df_sites = pd.read_csv(sites_US_crawl_path)
                
            try:
                df = load_entries(entries_path)
            except FileNotFoundError:
                plot_lst.append(([], "none"))
                continue
            
            site_urls = df_sites['Site URL'].values
            cleaned_site_urls = [clean_url(url) for url in site_urls]

            # Clean the root URLs in your DataFrame
            df['cleaned_rootUrl'] = df['rootUrl'].apply(clean_url)

            # Match the index of the cleaned site URLs with the cleaned root URLs
            matching_indices = [
                idx for idx, cleaned_url in enumerate(df['cleaned_rootUrl']) if cleaned_url in cleaned_site_urls
            ]
            
            site_url_indices = sorted(list(set([cleaned_site_urls.index(df['cleaned_rootUrl'].iloc[idx]) for idx in matching_indices])))
            
            title = f"crawl {CRAWL_ID} in {country}"
            
            plot_lst.append((site_url_indices, title))

    scrape_distribution_plot_20(plot_lst)
    
def check_error_distribution_visualized(CRAWL_ID):
    
    plot_lst = []

    for us_bool in [False, True]:
        for country in countries:
            sites_crawl_path = f"../data_other/{country}-top-525.csv"
            sites_US_crawl_path = r"../data_other/unitedstates-top-525.csv"

            error_log_path = f"../data/crawl_{CRAWL_ID}/error-logging_{country}_{CRAWL_ID}.json"
            
            if us_bool:
                df_sites = pd.read_csv(sites_crawl_path)
            else:
                df_sites = pd.read_csv(sites_US_crawl_path)
            
            try:
                error_log = load_err_log(error_log_path)
            except FileNotFoundError:
                plot_lst.append(([], "none"))
                continue
            
            error_sites = []
            for key, value in error_log.items():
                for site in value:
                    error_sites.append(clean_url(site))
            
            site_urls = df_sites['Site URL'].values
            cleaned_site_urls = [clean_url(url) for url in site_urls]

            matching_indices = [
                idx for idx, cleaned_url in enumerate(error_sites) if cleaned_url in cleaned_site_urls
            ]
            
            site_url_indices = sorted(
                list(
                    set(
                        [cleaned_site_urls.index(clean_url(error_sites[idx])) for idx in matching_indices]
                    )
                )
            )
                    
            if us_bool:
                title = f"crawl {CRAWL_ID} in {country} on US sites"
            else:
                title = f"crawl {CRAWL_ID} in {country} on country sites"
            
            plot_lst.append((site_url_indices, title))

    error_distribution_plot_20(plot_lst)
    
def inspect_country_scrape(country, CRAWL_IDs):
    
    plot_lst = []
    
    for us_bool in [False, True]:
        for CRAWL_ID in CRAWL_IDs:
            sites_crawl_path = f"../data_other/{country}-top-525.csv"
            sites_US_crawl_path = r"../data_other/unitedstates-top-525.csv"

            entries_path = f"../data/crawl_{CRAWL_ID}/entries_{country}_{CRAWL_ID}.csv"
            
            if not us_bool:
                    df_sites = pd.read_csv(sites_crawl_path)
            else:
                df_sites = pd.read_csv(sites_US_crawl_path)
                
            try:
                df = load_entries(entries_path)
            except FileNotFoundError:
                plot_lst.append(([], "none"))
                continue
            
            site_urls = df_sites['Site URL'].values
            cleaned_site_urls = [clean_url(url) for url in site_urls]

            # Clean the root URLs in your DataFrame
            df['cleaned_rootUrl'] = df['rootUrl'].apply(clean_url)

            # Match the index of the cleaned site URLs with the cleaned root URLs
            matching_indices = [
                idx for idx, cleaned_url in enumerate(df['cleaned_rootUrl']) if cleaned_url in cleaned_site_urls
            ]
            
            site_url_indices = sorted(list(set([cleaned_site_urls.index(df['cleaned_rootUrl'].iloc[idx]) for idx in matching_indices])))
            
            if us_bool:
                title = f"crawl {CRAWL_ID} in {country} on US sites"
            else:
                title = f"crawl {CRAWL_ID} in {country} on country sites"
            
            plot_lst.append((site_url_indices, title))
            
    scrape_distribution_plot_customize(plot_lst, "green")

def inspect_country_error(country, CRAWL_IDs):
    
    plot_lst = []
    
    for us_bool in [False, True]:
        for CRAWL_ID in CRAWL_IDs:
            sites_crawl_path = f"../data_other/{country}-top-525.csv"
            sites_US_crawl_path = r"../data_other/unitedstates-top-525.csv"

            error_log_path = f"../data/crawl_{CRAWL_ID}/error-logging_{country}_{CRAWL_ID}.json"
            
            if not us_bool:
                df_sites = pd.read_csv(sites_crawl_path)
            else:
                df_sites = pd.read_csv(sites_US_crawl_path)
                
            try:
                error_log = load_err_log(error_log_path)
            except FileNotFoundError:
                plot_lst.append(([], "none"))
                continue
            
            error_sites = []
            for key, value in error_log.items():
                for site in value:
                    error_sites.append(clean_url(site))
            
            site_urls = df_sites['Site URL'].values
            cleaned_site_urls = [clean_url(url) for url in site_urls]

            matching_indices = [
                idx for idx, cleaned_url in enumerate(error_sites) if cleaned_url in cleaned_site_urls
            ]
            
            site_url_indices = sorted(
                list(
                    set(
                        [cleaned_site_urls.index(clean_url(error_sites[idx])) for idx in matching_indices]
                    )
                )
            )
                    
            if us_bool:
                title = f"crawl {CRAWL_ID} in {country} on US sites"
            else:
                title = f"crawl {CRAWL_ID} in {country} on country sites"
            
            plot_lst.append((site_url_indices, title))
            
    scrape_distribution_plot_customize(plot_lst, "red")
    
def inspect_country_scrape_monetization(country, CRAWL_IDs):
    plot_lst = []
    
    for us_bool in [False, True]:
        for CRAWL_ID in CRAWL_IDs:
            sites_crawl_path = f"../data_other/{country}-top-525.csv"
            sites_US_crawl_path = r"../data_other/unitedstates-top-525.csv"

            entries_path = f"../data/crawl_{CRAWL_ID}/entries_{country}_{CRAWL_ID}.csv"
            
            if us_bool:
                df_sites = pd.read_csv(sites_crawl_path)
            else:
                df_sites = pd.read_csv(sites_US_crawl_path)
                
            try:
                df = load_entries(entries_path)
            except FileNotFoundError:
                plot_lst.append(([], "none"))
                continue
            
            site_urls = df_sites['Site URL'].values
            cleaned_site_urls = [clean_url(url) for url in site_urls]

            # Clean the root URLs in your DataFrame
            df['cleaned_rootUrl'] = df['rootUrl'].apply(clean_url)

            # Filter rows with "monetization" in the `permission` column
            monetization_df = df[df['permission'].str.contains("monetization", na=False)]
            
            # Match the index of the cleaned site URLs with the cleaned root URLs
            matching_indices = [
                idx for idx, cleaned_url in enumerate(monetization_df['cleaned_rootUrl']) 
                if cleaned_url in cleaned_site_urls
            ]
            
            site_url_indices = sorted(list(set([cleaned_site_urls.index(monetization_df['cleaned_rootUrl'].iloc[idx]) for idx in matching_indices])))
            
            if us_bool:
                title = f"crawl {CRAWL_ID} in {country} on US sites"
            else:
                title = f"crawl {CRAWL_ID} in {country} on country sites"
            
            plot_lst.append((site_url_indices, title))
            
    scrape_distribution_plot_customize(plot_lst, "blue")
        
def check_potential_duplicate_scrape(country, CRAWL_IDs, timespan=600_000):
    """ 
    For each site in the provided country and CRAWL_IDs, check if the timestamp between the 
    first entry and the last entry is within 10 minutes of each other and visualize in a table.
    Only sites with issues will be displayed.
    """
    # Prepare data structure for visualization
    site_data = {}

    for CRAWL_ID in CRAWL_IDs:
        # Define the path for the entries file based on the country and CRAWL_ID
        entries_path = f"../data/crawl_{CRAWL_ID}/entries_{country}_{CRAWL_ID}.csv"

        try:
            # Load the entries data
            df = load_entries(entries_path)
        except FileNotFoundError:
            print(f"Entries file not found for country: {country}, CRAWL_ID: {CRAWL_ID}")
            continue

        for site_url in df.rootUrl.unique():
            site_df = df[df.rootUrl == site_url]
            site_df = site_df.sort_values('timestp')

            first_entry = site_df.iloc[0]
            last_entry = site_df.iloc[-1]

            # Convert timestamps to readable format
            first_entry_readable = datetime.fromtimestamp(first_entry.timestp / 1000).strftime('%Y-%m-%d %H:%M:%S')
            last_entry_readable = datetime.fromtimestamp(last_entry.timestp / 1000).strftime('%Y-%m-%d %H:%M:%S')

            # Check if the difference between first and last timestamp is greater than 10 minutes (600 seconds)
            if last_entry.timestp - first_entry.timestp > timespan:  # 600000 milliseconds = 10 minutes
                issue_info = f"{first_entry_readable} - {last_entry_readable}"

                if site_url not in site_data:
                    site_data[site_url] = {}
                site_data[site_url][CRAWL_ID] = issue_info

    # Filter to only include sites with issues
    if not site_data:
        print("No sites with issues found.")
        return

    rows = list(site_data.keys())
    columns = CRAWL_IDs
    table_data = []

    for site in rows:
        row = []
        for crawl_id in columns:
            row.append(site_data.get(site, {}).get(crawl_id, ""))
        table_data.append(row)

    # Create table visualization
    fig, ax = plt.subplots(figsize=(10, len(rows) * 0.5))
    ax.axis('tight')
    ax.axis('off')

    table = ax.table(
        cellText=table_data,
        rowLabels=rows,
        colLabels=columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(columns))))

    plt.title(f"Sites with Timestamp Issues for {country} with threshold {timespan}")
    plt.show()


def check_scrape_time_span(df):
    """
    Checks the time span of data collection by sampling evenly spaced entries from the DataFrame and calculating the time difference between these sampled entries.

    Args:
        df (pd.DataFrame): entries.csv in dataframe

    Returns:
        None: Prints the timestamp of sampled entries in a human-readable format along with the time difference (in hours) between consecutive entries.

    Notes:
        - The function samples 10 evenly spaced indices from the DataFrame.
        - Timestamps are converted to a readable datetime format.
        - The time difference is calculated in milliseconds and converted to hours.
    """
    
    index_to_check = np.linspace(0, len(df)-1, 10)
    index_to_check = index_to_check.astype(int)
    
    for i in range(len(index_to_check[:-1])):
        index_0 = index_to_check[i]
        index_1 = index_to_check[i+1]
        
        entry = df.iloc[index_0]
        readable = datetime.fromtimestamp(entry.timestp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        next_readable = datetime.fromtimestamp(df.iloc[index_1].timestp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        diff = df.iloc[index_1].timestp - entry.timestp
        print(f"Entry {index_0} was collected at {readable}, Difference: {diff / 3_600_000}")
    
def check_scrape_percentage(df_entries, df_site):
    df_entries['cleaned_rootUrl'] = df_entries['rootUrl'].apply(clean_url)
    df_site['cleaned_rootUrl'] = df_site['Site URL'].apply(clean_url)
    
    sites_crawled = df_entries.cleaned_rootUrl.unique()
    sites_total = df_site.cleaned_rootUrl.unique()
    
    crawled_percentage = (len(sites_crawled) / len(sites_total)) * 100
    
    print(f"Percentage of sites scraped = {len(sites_crawled)} / {len(sites_total)} = {crawled_percentage}")
    


