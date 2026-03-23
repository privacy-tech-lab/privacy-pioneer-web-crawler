import pandas as pd
import numpy as np

import json
import os
import re
import csv

import shutil
from collections import defaultdict

from modules.config import countries
from modules.utils import clean_url, load_err_log

def merge_err_logs(crawl_id):
    """crawls that are interrupted will have multiple error-log files, this function merges them into one file.
    e.g. 
    "error-logging_{country}_{crawl_id}_0.json" &
    "error-logging_{country}_{crawl_id}_1.json" &
    "error-logging_{country}_{crawl_id}_2.json" will be merged into one file named 
    "error-logging_{country}_{crawl_id}.json"

    Args:
        crawl_id (str): ID of the crawl
    """
    folder_path = f"..\data\crawl_{crawl_id}"
    for country in countries:
        expected_json_file = os.path.join(folder_path, f"error-logging_{country}_{crawl_id}.json")
        if not os.path.exists(expected_json_file):
            # Collect all the error-logging files
            pattern = re.compile(rf"error-logging_{country}_{crawl_id}_\d\.json$")
            matching_files = [
                file for file in os.listdir(folder_path)
                if pattern.match(file)
            ]    
            
            if len(matching_files) == 0:
                print(f"No error logs found for {country}")
                continue
            
            print(matching_files)
            # put them together
            data = {}
            for file in matching_files:
                with open(os.path.join(folder_path, file), "r") as f:
                    data.update(json.load(f))
            
            # write the merged file
            with open(expected_json_file, "w") as f:
                json.dump(data, f)
            
            print(f"merged error logs for {country} to file {expected_json_file}")

def rename_crawl_files(crawl_id):
    """
    Creates a backup of crawl files and renames them for easier analysis.

    This function is designed to operate after the merge_error_log step and after 
    crawl files have been exported to the desired folder for analysis. It performs 
    the following steps:
    
    1. Creates a backup folder named "crawl_a{x}_backup" (where 'x' is the provided folder_id).
       All crawl files are copied into this backup folder without any modifications.
    
    2. Renames the original crawl files in the folder for improved clarity and organization 
       during analysis. The new file names are derived by removing the last two characters 
       of the original file name (before the extension) and appending the folder_id.
    
    Parameters:
        folder_id (str): An identifier for the folder containing the crawl files.
    """
    
    data_folder_path = f"../data/crawl_{crawl_id}"
    data_raw_folder_path = f"../data/crawl_{crawl_id}_raw"    
    
    # remove all content in data_folder_path
    if os.path.exists(data_folder_path):
        shutil.rmtree(data_folder_path)
    
    for file_name in os.listdir(data_raw_folder_path):
        shutil.copy(f"{data_raw_folder_path}/{file_name}", f"{data_folder_path}/{file_name}")
    
    # 2. The file names will be changed for the ease of analysis
    for file_name in os.listdir(data_folder_path):
        new_file_name = file_name.split(".")[0][:-2] + crawl_id + "." + file_name.split(".")[1]
        shutil.move(f"{data_folder_path}/{file_name}", f"{data_folder_path}/{new_file_name}")
    
def collect_all_error_logs(crawl_id):
    """
    Collects all error URLs from the error log files in a specified folder,
    and compares them with URLs in the unitedstates-top-525.csv file.
    Outputs a combined CSV file of matching error URLs.

    Args:
        folder_id (str): Identifier for the folder containing error log files.

    Returns:
        None: Outputs a combined CSV file named "combined_US_error_sites.csv".
    """
    folder_path = f"../data/crawl_{crawl_id}"
    output_csv_path = os.path.join(folder_path, "combined_US_error_sites.csv")
    
    # Collect all error log files
    error_logs = []
    for file_name in os.listdir(folder_path):
        if file_name.startswith("error-logging"):
            with open(os.path.join(folder_path, file_name), "r") as file:
                try:
                    error_logs.append(json.load(file))
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse {file_name}")

    # Flatten error logs into a single list of URLs
    error_urls = set()
    for log in error_logs:
        for url_list in log.values():
            error_urls.update(url_list)

    # Clean the error URLs
    cleaned_error_urls = {clean_url(url) for url in error_urls}

    # Load the unitedstates-top-525.csv file
    sites_US_crawl_path = r"../data_other/unitedstates-top-525.csv"
    df_sites = pd.read_csv(sites_US_crawl_path)
    site_urls = df_sites['Site URL'].apply(clean_url).values

    # Find matching URLs
    matching_urls = [url for url in cleaned_error_urls if url in site_urls]

    # Create a DataFrame and save to CSV
    df_matching_urls = pd.DataFrame(matching_urls, columns=['Error URL'])
    df_matching_urls.to_csv(output_csv_path, index=False)
    print(f"Combined error URLs saved to: {output_csv_path}")
    
def filter_entries_by_error_sites(crawl_id):
    """
    Removes entries containing error sites from entry files.

    Args:
        crawl_id (str): Identifier for the crawl process.

    Returns:
        None: Updates and renames the entry files in place.
    """
    folder_path = f"../data/crawl_{crawl_id}"

    # Load Error Sites
    error_sites_path = os.path.join(folder_path, "combined_US_error_sites.csv")
    error_sites = set(pd.read_csv(error_sites_path)["Error URL"].values)
    
    # Load Entries
    for country in countries:
        entries_path = os.path.join(folder_path, f"entries_{country}_{crawl_id}.csv")
        if not os.path.exists(entries_path):
            print(f"Entries file for {country} not found. Skipping...")
            continue
        df_entries = pd.read_csv(entries_path)
        original_len = len(df_entries)
        # Filter Entries
        filtered_entries = df_entries[~df_entries["rootUrl"].apply(clean_url).isin(error_sites)]
        
        filtered_len = len(filtered_entries)
        print(f"Filtered error {country} entries: {original_len - filtered_len}")
        # Save Filtered Entries
        filtered_entries.to_csv(entries_path, index=False)
        print(f"Filtered entries saved to: {entries_path}")
        

def remove_duplicate_entries(crawl_id, time_limit=600_000):
    """
    Removes entries where the timestamp difference between each entry and the last entry
    for a site exceeds the specified time limit (default: 600 seconds).

    Args:
        crawl_id (str): Identifier for the crawl process.
        time_limit (int): Time limit in seconds to consider entries as valid.

    Returns:
        None: Updates and renames the entry files in place.
    """
    folder_path = f"../data/crawl_{crawl_id}"

    # Load Entries
    for country in countries:
        entries_path = os.path.join(folder_path, f"entries_{country}_{crawl_id}.csv")
        if not os.path.exists(entries_path):
            print(f"Entries file for {country} not found. Skipping...")
            continue

        df_entries = pd.read_csv(entries_path)
        original_len = len(df_entries)

        # Group by rootUrl and filter entries
        filtered_entries = []
        for site_url, group in df_entries.groupby("rootUrl"):
            group = group.sort_values("timestp")
            last_timestp = group["timestp"].iloc[-1]

            # Keep only entries where the timestamp difference to the last entry is less than the time limit
            group_filtered = group[group["timestp"].apply(lambda x: (last_timestp - x) <= (time_limit))]

            if not group_filtered.empty:
                filtered_entries.append(group_filtered)

        # Combine filtered groups into a single DataFrame
        filtered_entries = pd.concat(filtered_entries, ignore_index=True) if filtered_entries else pd.DataFrame()
        filtered_len = len(filtered_entries)

        print(f"Filtered duplicate {country} entries: {original_len - filtered_len}")

        # Save Filtered Entries
        if not filtered_entries.empty:
            filtered_entries.to_csv(entries_path, index=False)
            print(f"Filtered entries saved to: {entries_path}")
        else:
            print(f"No valid entries for {country}. File not updated.")
            
def merge_all_dataframes(crawl_id):
    df_lst = []
    
    folder_path = f"../data/crawl_{crawl_id}"
    
    error_sites_path = os.path.join(folder_path, "combined_US_error_sites.csv")
    error_sites = set(pd.read_csv(error_sites_path)["Error URL"].values)

    for country in countries:
        entries_path = os.path.join(folder_path, f"entries_{country}_{crawl_id}.csv")
        error_log_path = os.path.join(folder_path, f"error-logging_{country}_{crawl_id}.json")

        if (not os.path.exists(entries_path)) or (not os.path.exists(error_log_path)):
            print(f"Entries file {os.path.exists(entries_path)}; error-log file {os.path.exists(error_log_path)} for {country}. Skipping...")
            continue
        
        # Load the entries and errors
        df_entries = pd.read_csv(entries_path)
        error_log = load_err_log(error_log_path)
        
        # Add column named "error_instance"
        # The data would the type of the error in the site
        # If the site is not in the error log, the value would be "None"
        # If the error site is not in entries, create a new entry with the url and the error type
        for error_type, error_sites in error_log.items():
            error_sites = [clean_url(site) for site in error_sites]
            for err_site in error_sites:
                if err_site not in df_entries["rootUrl"].apply(clean_url).values:
                    new_entry = {
                        "rootUrl": err_site,
                        "error_instance": error_type,
                        "country": country
                    }
                    df_entries = pd.concat([df_entries, pd.DataFrame([new_entry])], ignore_index=True)
                else:
                    df_entries.loc[df_entries["rootUrl"].apply(clean_url).isin(error_sites), "error_instance"] = error_type
        
        df_entries["error_instance"] = df_entries["error_instance"].fillna("None")

        # Add column named "error_other_instance"
        df_entries["error_other_instance"] = df_entries["rootUrl"].apply(clean_url).isin(error_sites)
        
        # Add column named "duplicates"
        # Criterion for duplicates: the timespan between this entry and the next entry is greater than 10 minutes
        df_entries["duplicates"] = False
        df_entries["timestp"] = pd.to_datetime(df_entries["timestp"])
        df_entries = df_entries.sort_values(["rootUrl", "timestp"])
        threshold = 600_000
        # If the timestamp difference between the firstentry and the last entry for one rootUrl exceeds the threshold, then the data points for this rootUrl is considered to be potential duplicates
        df_entries["duplicates"] = False  # Initialize duplicates column
        grouped = df_entries.groupby("rootUrl")

        # Calculate the timestamp difference for each group
        for root_url, group in grouped:
            if len(group) > 1:  # Only process if there are multiple entries for the same rootUrl
                first_entry_time = group["timestp"].min()
                last_entry_time = group["timestp"].max()
                time_diff = (last_entry_time - first_entry_time).total_seconds() * 1000  # Convert to milliseconds
                
                if time_diff > threshold:
                    # Mark all entries in this group as potential duplicates
                    df_entries.loc[group.index, "duplicates"] = True
        
        df_lst.append(df_entries)
        
        # TODO: Add column named "http / recrawl"
        
        # TODO: 
            
    # Merge all entries, add a column "country"
    df_all_entries = pd.DataFrame()
    for df, country in zip(df_lst, countries):
        df["country"] = country
        df_all_entries = pd.concat([df_all_entries, df])
            
    # Save the merged dataframe to a new file
    df_all_entries.to_csv(f"../data/crawl_{crawl_id}/all_entries.csv", index=False)
    
    return df_all_entries