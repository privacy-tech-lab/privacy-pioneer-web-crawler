import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import json
import csv
from collections import defaultdict

from modules.utils import clean_url, load_entries
from modules.config import countries, typs

def _check_data(dfs, countries):
    if (not isinstance(dfs, list)) or (not isinstance(dfs[0], pd.DataFrame)):
        raise ValueError("dfs should be a list of dataframes")

    if not isinstance(countries, list) or len(countries) != len(dfs):
        raise ValueError("Length of countries must match the number of DataFrames in dfs")
    
def _subset_urls(dfs, subset_url_lst, reverse_subset):
    subset_url_lst = [clean_url(url) for url in subset_url_lst]
    dfs_out = []
    for index, country in enumerate(countries):
        if country == "unitedstates":
            dfs_out.append(dfs[index])
        else:
            if not reverse_subset:        
                dfs_out.append(dfs[index][dfs[index].rootUrl.apply(clean_url).isin(subset_url_lst)])
            else:
                dfs_out.append(dfs[index][~dfs[index].rootUrl.apply(clean_url).isin(subset_url_lst)])
                
    return dfs_out

def collect_entries(crawl_idx):
    dfs = []
    for country_ in countries:
        FILE_PATH = f"../data/crawl_{crawl_idx}/entries_{country_}_{crawl_idx}.csv"
        dfs.append(load_entries(FILE_PATH))
    country_labels = countries
        
    return dfs, country_labels

def _prepare_sites_US():
    US_SITES_PATH = f"../data_other/unitedstates-top-525.csv"
    df_us = pd.read_csv(US_SITES_PATH)
    sites_us = df_us['Site URL'].values
    
    return sites_us

def prepare_collectionNumberOrProportion_data(
    dfs, subset_url_lst=None, reverse_subset=False, mask_columns=None, subset_columns=None, 
    normalize=True, count_site_once=False
):
    """
    Prepares data for generating a privacy collection distribution plot.
    
    Parameters:
    - dfs (list): A list of DataFrames with 'typ' and 'rootUrl' columns.
    - countries (list): A list of country names corresponding to the DataFrames.
    - subset_url_lst (list, optional): A list of specific URLs to analyze. Defaults to None.
    - mask_columns (list, optional): Types to exclude. Defaults to None.
    - subset_columns (list, optional): Types to include. Defaults to None.
    - normalize (bool, optional): Whether to normalize the data. Defaults to True.
    - count_site_once (bool, optional): If True, counts each type only once per site. Defaults to False.
    
    Returns:
    - df_plot (DataFrame): Consolidated DataFrame ready for plotting.
    - classifications (list): Unique types/categories present in the data.
    - colors (dict): Mapping of countries to their respective colors.
    """
    _check_data(dfs, countries)
    
    # Clean and filter URLs if subset_url_lst is provided
    if subset_url_lst is not None:
        dfs = _subset_urls(dfs, subset_url_lst, reverse_subset)
    
    # Exclude specified types
    if mask_columns is not None:
        dfs = [df[~df.typ.isin(mask_columns)] for df in dfs]
    
    # Include only specified types
    if subset_columns is not None:
        dfs = [df[df.typ.isin(subset_columns)] for df in dfs]
    
    # Prepare data for plotting
    all_data = []
    totals = {}
    for df, country in zip(dfs, countries):
        if count_site_once:
            df = df.drop_duplicates(subset=['typ', 'rootUrl'])  # Count each type only once per site
            
        counts = df["typ"].value_counts(normalize=normalize).reindex(typs).reset_index()
        counts.columns = ["type", "y"]
        counts["country"] = country
        all_data.append(counts)
        totals[country] = len(df)
    
    df_plot = pd.concat(all_data, ignore_index=True)
    
    # Assign colors to countries
    cmap = plt.cm.get_cmap("tab10", len(countries)) 
    colors = {country: cmap(i) for i, country in enumerate(countries)}
    
    return df_plot, colors

def prepare_numberOfCollectionPerSite_data(
    dfs, subset_url_lst=None, reverse_subset=False, mask_columns=None, subset_columns=None
):
    # Clean and filter URLs if subset_url_lst is provided
    if subset_url_lst is not None:
        dfs = _subset_urls(dfs, subset_url_lst, reverse_subset)
            
    # Exclude specified types
    if mask_columns is not None:
        dfs = [df[~df.typ.isin(mask_columns)] for df in dfs]
    
    # Include only specified types
    if subset_columns is not None:
        dfs = [df[df.typ.isin(subset_columns)] for df in dfs]
    
    # Prepare data for plotting
    all_data = []
    for df, country in zip(dfs, countries):
        df_nSites = df.drop_duplicates(subset=['typ', 'rootUrl'])
        
        counts = df["typ"].value_counts().reindex(typs).reset_index()
        counts.columns = ["type", "y"]
        
        counts["country"] = country
        for typ in typs:
            if typ not in df.typ.unique():
                counts.loc[counts.type == typ, "y"] = 0
                continue
                
            site_count = df_nSites[df_nSites.typ == typ].shape[0]
            collection_num = df.loc[df.typ == typ].shape[0]
            # modify the y with country, typ specified
            counts.loc[counts.type == typ, "y"] = collection_num/site_count
                            
        all_data.append(counts)
    
    df_plot = pd.concat(all_data, ignore_index=True)
    
    # Assign colors to countries
    cmap = plt.cm.get_cmap("tab10", len(countries)) 
    colors = {country: cmap(i) for i, country in enumerate(countries)}
    
    return df_plot, colors

def perpare_categorySpecific_CollectionNumVSCollectionPerSite_data(dfs, category, subset_url_lst=None, reverse_subset=False):
    # Clean and filter URLs if subset_url_lst is provided
    if subset_url_lst is not None:
        dfs = _subset_urls(dfs, subset_url_lst, reverse_subset)
    
    all_data = []
    for df, country in zip(dfs, countries):
        df_todo = df[df['typ'] == category]
        df_nSites = df_todo.drop_duplicates(subset=['rootUrl'])
        # x - Total number of collections, y - Avg number of collections per site
        
        x = df_todo.shape[0]
        if df_nSites.shape[0] == 0:
            y = 0
        else:
            y = x / df_nSites.shape[0]
        
        counts = pd.DataFrame({'country': [country], 'y': [y], 'x': [x]}, index=[len(all_data)])
        all_data.append(counts)
        
    df_plot = pd.concat(all_data, ignore_index=True)
        
    cmap = plt.cm.get_cmap("tab10", len(countries)) 
    colors = {country: cmap(i) for i, country in enumerate(countries)}
            
    return df_plot, colors

def perpare_categorySpecific_CollectionNumVsSiteNum_data(dfs, category, subset_url_lst=None, reverse_subset=False):
    # Clean and filter URLs if subset_url_lst is provided
    if subset_url_lst is not None:
        dfs = _subset_urls(dfs, subset_url_lst, reverse_subset)
    
    all_data = []
    for df, country in zip(dfs, countries):
        df_todo = df[df['typ'] == category]
        df_nSites = df_todo.drop_duplicates(subset=['rootUrl'])
        # x - Total number of collections, y - Avg number of collections per site
        
        x = df_todo.shape[0]
        y = df_nSites.shape[0]
        
        counts = pd.DataFrame({'country': [country], 'y': [y], 'x': [x]}, index=[len(all_data)])
        all_data.append(counts)
        
    df_plot = pd.concat(all_data, ignore_index=True)
        
    cmap = plt.cm.get_cmap("tab10", len(countries)) 
    colors = {country: cmap(i) for i, country in enumerate(countries)}
            
    return df_plot, colors