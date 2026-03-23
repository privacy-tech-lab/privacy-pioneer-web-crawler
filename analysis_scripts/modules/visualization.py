import numpy as np
import pandas as pd
import json
import warnings

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

import seaborn as sns

# from modules.inspect_crawl import *
from modules.config import typs, countries
from modules.utils import clean_url, get_multiplier_for_normalization
    
# Temp, remove this import later
from modules.data_preperation import _check_data, _subset_urls

def errors_pie(err_log_data, title, total=1050, save=False):
    """Generates a pie chart of error counts

    """
    plt.style.use('_mpl-gallery-nogrid')

    x = [len(value) for value in err_log_data.values()]
    x = x + [1050 - sum(x)]
    
    labels = list(err_log_data.keys()) + ['No Error']

    colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(x)))

    fig, ax = plt.subplots(figsize=(8, 8))
    
    wedges, texts, autotexts = ax.pie(
        x, colors=colors, radius=3, center=(4, 4),
        wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=False,
        labels=labels, autopct='%1.1f%%',
        textprops={'color': 'black', 'fontsize': 12}  # Adjust fontsize here
    )-748512
    
    for text in texts:
        text.set_fontsize(16)  

    ax.set(xlim=(0, 8), ylim=(0, 8))

    plt.title(title, fontsize=24)
    plt.show()
    
    if save:
        fig.savefig(r"output\error_log\{title}.png", dpi=300, bbox_inches='tight')
        
def _collect_error_types(country_data_dict):
    """returns a list of error types with input of the error logs for 10 countries

    Args:
        country_data_dict (dict): {country: error_log_data}
        
    Returns:
        list: list of error types
    """
    error_types = set()
    for country_data in country_data_dict.values():
        error_types.update(country_data.keys())

    error_types.add("No Error")
      
    return list(error_types)

def _collect_error_files(folder_path, crawl_id):
    """collects the error files for 10 countries
    
    Args:
        folder_path (str): path to the folder containing the error logs
        crawl_id (str): id of the crawl
    
    Returns:
        dict: {country: error_log_data}
    """
    country_errors = {}
    for country in countries:
        file_path = f"{folder_path}\\error-logging_{country}_{crawl_id}.json"
        with open(file_path, "r") as f:
            data = json.load(f)
            country_errors[country] = data
    return country_errors

def _subset_US_top_525(country_data_dict, reverse=False):
    """subsets the error log data for a country to only include the top 525 US sites or only include the top 525 country sites (excluding US)

    Args:
        country_data_dict (dict): error_log_data_dict
        reverse (bool): indicates whether to subset to US sites or to non-US sites

    Returns:
        dict: error_log_data_dict
    """
    US_sites = pd.read_csv(r"data_other\unitedstates-top-525.csv")
    US_sites = US_sites['Site URL'].apply(clean_url)
    
    for country, error_log in country_data_dict.items():
        if country == "unitedstates":
            continue
        for category, sites in error_log.items():
            for site in sites:
                if reverse:
                    cond = clean_url(site) in US_sites
                else:
                    cond = clean_url(site) not in US_sites
                    
                if cond:
                    country_data_dict[country][category].remove(site)
                    
    return country_data_dict

def _get_total_site_num(countries, subset_us):
    totals = []
    for country in countries:
        if country != "unitedstates":
            if subset_us:
                totals.append(525)
            else:
                totals.append(1050)
        else:
            totals.append(525)
            
    return totals

def errors_visualization(crawl_id, subset_us=False, reverse=False):
    """visualizes the errors in scraping for 10 countries
    
    Properties of interest:
    - number of errors for 10 countries 
    - types of errors for 10 countries
    - number of errors per type for 10 countries
    
    Args:
        crawl_id (str): id of the crawl
        subset_us (bool): whether to subset to US sites
        reverse (bool): defaults to False. If changed to True, it will instead exclude US sites (for country 525 analysis) 

    """
    folder_path = f"data/crawl_{crawl_id}"
    country_errors = _collect_error_files(folder_path, crawl_id) 
    if subset_us:
        country_errors = _subset_US_top_525(country_errors, reverse=reverse)   
    error_types = _collect_error_types(country_errors)
    
    totals = _get_total_site_num(countries, subset_us)
    
    fig, axes = plt.subplots(nrows=len(countries), ncols=1, figsize=(5, 30))

    # Generate a color palette using a colormap
    cmap = cm.get_cmap("tab10", len(error_types))  # "tab10" is a good categorical colormap
    colors = {label: cmap(i) for i, label in enumerate(error_types)}  # Map labels to colors

    for ax, country in zip(axes, countries):
        errors = country_errors[country]
        labels = list(errors.keys())
        labels.append("No Error")
        
        sizes = [len(v) for v in list(errors.values())]
        sizes.append(totals.pop(0) - sum(sizes))
        
        pie_colors = [colors[label] for label in labels]
        
        # Plot the pie chart for the current country
        # ax.pie(
        #     sizes, labels=labels, colors=pie_colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8}
        # )
        ax.pie(
            sizes, colors=pie_colors, startangle=90, textprops={'fontsize': 8}
        )
        ax.set_title(f"Errors in {country}", fontsize=10)

    # Adjust layout
    plt.tight_layout()
    plt.show()
    
def errors_visualization_bar(crawl_id, title, subset_us=False, reverse=False, save=False):
    
    folder_path = f"data/crawl_{crawl_id}"
    country_errors = _collect_error_files(folder_path, crawl_id) 
    if subset_us:
        country_errors = _subset_US_top_525(country_errors, reverse=reverse)   
    error_types = _collect_error_types(country_errors)
        
    df_plot = pd.DataFrame(data=None, columns=["country", "type", "counts"])
    for country, error_log in country_errors.items():
        for error in error_types:
            if error == "No Error":
                continue
            try: 
                count = len(error_log[error])
            except KeyError:
                count = 0 
            rows = [{"country": country, "type": error, "counts": count}]
            df_plot = pd.concat([df_plot, pd.DataFrame(rows)], ignore_index=True)
            

    # Visualization
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=df_plot,
        x="type",
        y="counts",
        hue="country",
        ci=None
    )
    
    # Add vertical lines to separate error types    
    error_types_unique = df_plot["type"].unique()
    for i in range(len(error_types_unique) - 1):
        plt.axvline(x=i + 0.5, color="gray", linestyle="--", linewidth=1)
    
    plt.title(title, fontsize=16)
    plt.xlabel("Error Type", fontsize=14)
    plt.ylabel("Number of errors", fontsize=14)
    plt.xticks(rotation=30, fontsize=10)
    plt.legend(title="Country", fontsize=10)
    plt.tight_layout()
    
    if save:
        plt.savefig(f"output/error_log/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
        
def website_distribution_plot_1(ax, site_url_indices, title, color_site="green"):
    total_sites = 525
    grid_width = 21  # Number of columns
    grid_height = 25  # Number of rows

    x_coords = np.array([i % grid_width for i in range(total_sites)])
    y_coords = np.array([i // grid_width for i in range(total_sites)])
    
    colors = np.array(['white'] * total_sites)
    for idx in site_url_indices:
        colors[idx] = color_site
    
    ax.scatter(
        x_coords, 
        y_coords, 
        c=colors, 
        s=100,  # Size of the squares
        marker='s',  # Square markers
        edgecolor='black'  # Boundary color for squares
    )

    # Add labels for the first column
    for y in range(grid_height):
        label_index = y * grid_width
        ax.text(
            -0.8,  # Offset slightly to the left of the first column
            y, 
            str(label_index+1), 
            fontsize=8, 
            verticalalignment='center',
            horizontalalignment='right'
        )

    ax.set_aspect('equal')  # Ensure equal spacing

    # Remove axis labels
    ax.axis('off')

    # Add title
    ax.set_title(f"{title}", fontsize=14)
    
def scrape_distribution_plot_10(plot_lst):
    site_url_indices_lst = [plot[0] for plot in plot_lst]
    title_lst = [plot[1] for plot in plot_lst]
    
    fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(30, 12))
    for ax, site_url_indices, title in zip(axes.flat, site_url_indices_lst, title_lst):
        website_distribution_plot_1(ax, site_url_indices, title)
        
    legend_elements = [
        mpatches.Patch(color='green', label='Site with data'),
        mpatches.Patch(color='white', edgecolor='black', label='Site without data')
    ]
    fig.legend(
        handles=legend_elements, 
        loc='upper center',  # Position below the subplots
        fontsize=20, 
        ncol=2,  # Arrange legend items in a single row
        frameon=False  # Remove box around the legend
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for the legend at the bottom
    plt.show()    
    
def scrape_distribution_plot_20(plot_lst):

    site_url_indices_lst = [plot[0] for plot in plot_lst]
    title_lst = [plot[1] for plot in plot_lst]

    fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(30, 24))
    for ax, site_url_indices, title in zip(axes.flat, site_url_indices_lst, title_lst):
        website_distribution_plot_1(ax, site_url_indices, title)
        
    legend_elements = [
        mpatches.Patch(color='green', label='Site with data'),
        mpatches.Patch(color='white', edgecolor='black', label='Site without data')
    ]
    fig.legend(
        handles=legend_elements, 
        loc='upper center',  # Position below the subplots
        fontsize=20, 
        ncol=2,  # Arrange legend items in a single row
        frameon=False  # Remove box around the legend
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for the legend at the bottom
    plt.show()    

def scrape_distribution_plot_customize(plot_lst, color_pixel="green"):

    site_url_indices_lst = [plot[0] for plot in plot_lst]
    title_lst = [plot[1] for plot in plot_lst]
    
    n_col = int(len(plot_lst)/2)

    fig, axes = plt.subplots(nrows=2, ncols=n_col, figsize=(n_col*6, 12))
    for ax, site_url_indices, title in zip(axes.flat, site_url_indices_lst, title_lst):
        website_distribution_plot_1(ax, site_url_indices, title, color_pixel)

    legend_elements = [
        mpatches.Patch(color=color_pixel, label='Site with data'),
        mpatches.Patch(color='white', edgecolor='black', label='Site without data')
    ]
    fig.legend(
        handles=legend_elements, 
        loc='upper center',  # Position below the subplots
        fontsize=20, 
        ncol=2,  # Arrange legend items in a single row
        frameon=False  # Remove box around the legend
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for the legend at the bottom
    plt.show()        

def error_distribution_plot_10(plot_lst):
    site_url_indices_lst = [plot[0] for plot in plot_lst]
    title_lst = [plot[1] for plot in plot_lst]
    
    fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(30, 12))
    for ax, site_url_indices, title in zip(axes.flat, site_url_indices_lst, title_lst):
        website_distribution_plot_1(ax, site_url_indices, title, 'red')
        
    legend_elements = [
        mpatches.Patch(color='red', label='Site with error'),
        mpatches.Patch(color='white', edgecolor='black', label='Site without error')
    ]
    fig.legend(
        handles=legend_elements, 
        loc='upper center',  # Position below the subplots
        fontsize=20, 
        ncol=2,  # Arrange legend items in a single row
        frameon=False  # Remove box around the legend
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for the legend at the bottom
    plt.show()    

def error_distribution_plot_20(plot_lst):
    site_url_indices_lst = [plot[0] for plot in plot_lst]
    title_lst = [plot[1] for plot in plot_lst]
    
    fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(30, 24))
    for ax, site_url_indices, title in zip(axes.flat, site_url_indices_lst, title_lst):
        website_distribution_plot_1(ax, site_url_indices, title, 'red')
        
    legend_elements = [
        mpatches.Patch(color='red', label='Site with error'),
        mpatches.Patch(color='white', edgecolor='black', label='Site without error')
    ]
    fig.legend(
        handles=legend_elements, 
        loc='upper center',  # Position below the subplots
        fontsize=20, 
        ncol=2,  # Arrange legend items in a single row
        frameon=False  # Remove box around the legend
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for the legend at the bottom
    plt.show()    

def privacy_collection_general_boxplot(df, title, y_max=20, save=False):
    """
    Creates a box plot to visualize data distribution across types.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data.
    - title (str): The title of the chart.
    - y_max (int, optional): The maximum y-axis value. Defaults to 20.
    - save (bool, optional): If True, saves the chart as a PNG file. Defaults to False.

    Returns:
    - None
    """
    
    data_dict = count_collection_num(df)
    
    labels = typs
            
    labels_visualize = [label for label in labels]
    values_raw = list(data_dict.values())
    D = []
    for idx in range(len(values_raw[0])):
        element = []
        for label in labels:
            try:
                element.append(data_dict[label][idx])
            except KeyError:
                element.append(0)
        D.append(element)
        
    D = np.array(D)
    
    plt.style.use('default')
    
    fig, ax = plt.subplots(figsize=(20, 6))
    VP = ax.boxplot(D, positions=np.linspace(2, 2 + len(labels) * 3, len(labels)), 
                    widths=1.5, patch_artist=True,
                    showmeans=False, showfliers=False,
                    medianprops={"color": "white", "linewidth": 0.5},
                    boxprops={"facecolor": "C0", "edgecolor": "white", "linewidth": 0.5},
                    labels=labels_visualize,
                    whiskerprops={"color": "C0", "linewidth": 1.5},
                    capprops={"color": "C0", "linewidth": 1.5})

    ax.set(xlim=(0, 6 + len(labels) * 3), ylim=(0, y_max))
    plt.title(title)
    
    if save:
        fig.savefig(r"output\entries\{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
        
def privacy_collection_general_violinplot(df):
    """
    Generates a violin plot to visualize the distribution of data across types.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data.

    Returns:
    - None
    """
    
    data_dict = count_collection_num(df)
    
    labels = typs
    
    labels = labels[:4]
    
    labels_visualize = [label for label in labels]
    values_raw = list(data_dict.values())
    D = []
    for idx in range(len(values_raw[0])):
        element = []
        for label in labels:
            element.append(data_dict[label][idx])
        # for key, value in data_dict.items():
        #     element.append(value[idx])
        D.append(element)
        
    D = np.array(D)
    
    plt.style.use('default')
    # plt.style.use('_mpl-gallery')
    
    fig, ax = plt.subplots()
    vp = ax.violinplot(D, np.linspace(2, 2 + len(labels) * 3, len(labels)), widths=2, showmeans=False, showmedians=False, showextrema=False)
    
    ax.set_xticks(np.linspace(2, 2 + len(labels_visualize) * 3, len(labels_visualize)))
    ax.set_xticklabels(labels_visualize)
    # styling:
    for body in vp['bodies']:
        body.set_alpha(0.9)
        
    ax.set(xlim=(0, 6 + len(labels) * 3), ylim=(0, 30))

    plt.show()
    
def privacy_collection_general_barplot(df, title, subset_url_lst=None, save=False):
    """
    Generates a bar plot for the frequency of each type, optionally filtering by URLs.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data with 'typ' and 'rootUrl' columns.
    - title (str): The title of the chart.
    - subset_url_lst (list, optional): A list of URLs to filter the data. Defaults to None.
    - save (bool, optional): If True, saves the chart as a PNG file. Defaults to False.

    Returns:
    - None
    """
    
    if subset_url_lst is not None:
        subset_url_lst = [clean_url(url) for url in subset_url_lst]
        df.rootUrl = df.rootUrl.apply(clean_url)
        
        df = df[df.rootUrl.isin(subset_url_lst)]
    
    value_counts = df.typ.value_counts()
    # align the order of the typs according to the list typs
    value_counts = value_counts.reindex(typs)

    # Create the plot
    plt.figure(figsize=(20, 6))
    value_counts.plot(kind='bar', color='skyblue', edgecolor='black')

    # Add labels and title
    plt.title(title, fontsize=16)
    plt.xlabel('Type', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.xticks(rotation=45, fontsize=12)

    # Show the plot
    plt.tight_layout()
    if save:
        plt.savefig(r"output\entries\{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
    
def privacy_collection_general_barplot_proportion(dfs, countries, title, subset_url_lst=None, normalize=True, mask_columns=None, subset_columns=None, y_max=1, save=False):
    
    if (not isinstance(dfs, list)) or (not isinstance(dfs[0], pd.DataFrame)):
        raise ValueError("dfs should be a list of dataframes")
    
    if subset_url_lst is not None:
        # subset_url_lst
        subset_url_lst = [clean_url(url) for url in subset_url_lst]
        dfs = [df[df.rootUrl.apply(clean_url).isin(subset_url_lst)] for df in dfs]
        
    if mask_columns is not None:
        assert isinstance(mask_columns, list), "mask_columns should be a list of column names"

        # Drop the rows with value in column "typ in mask_columns
        dfs = [df[~df.typ.isin(mask_columns)] for df in dfs]
        
    if subset_columns is not None:
        assert isinstance(subset_columns, list), "mask_columns should be a list of column names"
        
        dfs = [df[df.typ.isin(mask_columns)] for df in dfs]
        
    
    total_counts = [df.shape[0] for df in dfs]
    value_counts = [df.typ.value_counts(normalize=normalize).reindex(typs) for df in dfs]
    n_figures = len(dfs)

    assert len(value_counts) == len(countries), "value_counts should have the same length as countries"

    
    fig, axes = plt.subplots(nrows=n_figures, ncols=1, figsize=(8, 3 * n_figures), sharex=True)
    if n_figures == 1:
        axes = [axes]  # Wrap a single axis object in a list to make it iterable
            
    for i, (vc, ax, country_name, total_count) in enumerate(zip(value_counts, axes, countries, total_counts)):
        vc.plot(kind='bar', color='skyblue', edgecolor='black', ax=ax)  # Plot normalized value counts
        ax.set_title(f"{title} - {country_name} - # rows {total_count}", fontsize=8)  # Add title for each subplot
        ax.set_xlabel('Type', fontsize=12)
        ax.set_ylabel('Proportion', fontsize=12)
        ax.set_ylim(0, 1)  # Set y-axis limit (convert percentage to proportion)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=10)
    
    # Set overall layout
    plt.tight_layout()
    
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
        
# def privacy_collection_distribution_plot_10(
#     dfs, countries, title, subset_url_lst=None, normalize=True, mask_columns=None, subset_columns=None, count_site_once=False, save=False
# ):
#     if (not isinstance(dfs, list)) or (not isinstance(dfs[0], pd.DataFrame)):
#         raise ValueError("dfs should be a list of dataframes")

#     if subset_url_lst is not None:
#         # Subset by URL list
#         subset_url_lst = [clean_url(url) for url in subset_url_lst]
#         dfs = [df[df.rootUrl.apply(clean_url).isin(subset_url_lst)] for df in dfs]

#     if mask_columns is not None:
#         assert isinstance(mask_columns, list), "mask_columns should be a list of column names"
#         # Drop rows with specified values in column `typ`
#         dfs = [df[~df.typ.isin(mask_columns)] for df in dfs]
#         typs_label = typs
#         for c in mask_columns:        
#             typs_label.remove(c)

#     if subset_columns is not None:
#         assert isinstance(subset_columns, list), "subset_columns should be a list of column names"
#         # Keep only rows with specified values in column `typ`
#         dfs = [df[df.typ.isin(subset_columns)] for df in dfs]
#         typs_label = subset_columns


#     # Prepare data for plotting
#     all_data = []
#     for df, country in zip(dfs, countries):
#         if count_site_once:
#             df = df.drop_duplicates(subset=['typ', 'rootUrl'])  
            
#         counts = df["typ"].value_counts(normalize=normalize).reindex(typs_label)
#         counts = counts.reset_index()
#         counts.columns = ["type", "proportion"]
#         counts["country"] = country
#         all_data.append(counts)

#     df_plot = pd.concat(all_data, ignore_index=True)

#     # Visualization
#     plt.figure(figsize=(12, 8))
#     sns.barplot(
#         data=df_plot,
#         x="type",
#         y="proportion",
#         hue="country",
#         ci=None,
#         edgecolor="black"
#     )

#     # Add vertical lines to separate types
#     error_types_unique = df_plot["type"].unique()
#     for i in range(len(error_types_unique) - 1):
#         plt.axvline(x=i + 0.5, color="gray", linestyle="--", linewidth=1)

#     # Style and labels
#     plt.title(title, fontsize=16)
#     plt.xlabel("Type", fontsize=14)
#     plt.ylabel("Proportion", fontsize=14)
#     if normalize:
#         plt.ylim(0, 1)
#     plt.xticks(rotation=30, fontsize=10)
#     plt.legend(title="Country", fontsize=10)
#     plt.tight_layout()

#     # Save or display the plot
#     if save:
#         plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches="tight")
#     else:
#         plt.show()
        
def privacy_collection_distribution_plot_10(
    dfs, countries, title, y_axis_label, subset_url_lst=None, proportion=True, normalize=False, mask_columns=None, subset_columns=None, reverse_subset=False, count_site_once=False, crawl_idx="00", save=False
):
    """
    Generates a line plot showing the proportion of entries by type across countries.

    Parameters:
    - dfs (list): A list of DataFrames with 'typ' columns.
    - countries (list): A list of country names corresponding to the DataFrames.
    - title (str): The title of the chart.
    - subset_url_lst (list, optional): A list of specific URLs to analyze. Defaults to None.
    - mask_columns (list, optional): Columns to exclude. Defaults to None.
    - subset_columns (list, optional): Columns to include. Defaults to None.
    - normalize (bool, optional): Whether to normalize the data. Defaults to True.
    - save (bool, optional): If True, saves the chart as a PNG file. Defaults to False.
    """
    _check_data(dfs, countries)

    if subset_url_lst is not None:
        dfs = _subset_urls(dfs, subset_url_lst, reverse_subset)

    if mask_columns is not None:
        dfs = [df[~df.typ.isin(mask_columns)] for df in dfs]

    if subset_columns is not None:
        dfs = [df[df.typ.isin(subset_columns)] for df in dfs]

    # Prepare data for plotting
    all_data = []
    
    for df, country in zip(dfs, countries):
        
        normalize_coef = 1
        if normalize: 
            normalize_coef = get_multiplier_for_normalization(country, crawl_idx)
            print(f"normalize_coef for country {country}: {normalize_coef}")
            
        if count_site_once:
            df = df.drop_duplicates(subset=['typ', 'rootUrl'])  # Count each type only once per site
            
        counts = df["typ"].value_counts(normalize=proportion).reindex(typs).reset_index()
        counts.columns = ["type", "proportion"]
        # Multiple each proportion by the normalization coefficient
        
        counts["proportion"] = counts["proportion"] * normalize_coef
        counts["country"] = country
        all_data.append(counts)

    df_plot = pd.concat(all_data, ignore_index=True)

    # Unique types (x-axis categories)
    classifications = df_plot["type"].unique()
    x = range(len(classifications))
    
    cmap = cm.get_cmap("tab10", len(countries)) 
    colors = {country: cmap(i) for i, country in enumerate(countries)}  


    fig, ax = plt.subplots(figsize=(20, 6))
    for country in countries:
        country_data = df_plot[df_plot["country"] == country]
        y_data = [
            country_data[country_data["type"] == c]["proportion"].values[0]
            if c in country_data["type"].values else 0
            for c in classifications
        ]
        marker_sizes = [60 for y in y_data]
        
        ax.scatter(x, y_data, s=marker_sizes, color=colors[country], label=country, edgecolors="none", alpha=0.7, marker='o')
        
        if proportion:
            y_displacement = 0
        else:
            y_displacement = -5
        
        for i, y in enumerate(y_data):
            if y > 0:  # Only label points with non-zero proportion
                ax.text(
                    x[i]+0.3, y+y_displacement, country, fontsize=8, ha='center', va='bottom', alpha=0.8
                )

    # Style the plot
    legend_handles = []
    for country in countries:
        legend_handles.append(Line2D([0], [0], marker='o', color='none', markerfacecolor=colors[country], markersize=16, alpha=0.7))

    # Custom legend with uniform-sized markers
    ax.legend(legend_handles, countries, title='Countries', loc='upper right', fontsize=12)

    
    ax.set_xticks(x)  # Set tick locations
    ax.set_xticklabels(classifications, rotation=0, fontsize=10)  # Set tick labels

    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Classification', fontsize=14)
    ax.set_ylabel(y_axis_label, fontsize=14)

    # Display or save the plot
    plt.tight_layout()
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()

def scatterPlot_privacyCategory_y_10Countreis(
    df_plot, colors, title, y_axis_name, y_displacement=0, save=False
):
    """
    Generates and displays or saves a scatter plot showing the proportion of entries by type across countries.
    
    Parameters:
    - df_plot (DataFrame): Consolidated DataFrame ready for plotting.
    - classifications (list): Unique types/categories present in the data.
    - colors (dict): Mapping of countries to their respective colors.
    - title (str): The title of the chart.
    - normalize (bool, optional): Whether the data was normalized. Defaults to True.
    - save (bool, optional): If True, saves the chart as a PNG file. Defaults to False.
    """
    x = range(len(typs))
    
    fig, ax = plt.subplots(figsize=(20, 6))
    
    for country in countries:
        country_data = df_plot[df_plot["country"] == country]
        y_data = [
            country_data[country_data["type"] == c]["y"].values[0]
            if c in country_data["type"].values else 0
            for c in typs
        ]
        marker_sizes = [60 for _ in y_data]
        
        ax.scatter(
            x, y_data, s=marker_sizes, color=colors[country], label=country, 
            edgecolors="none", alpha=0.7, marker='o'
        )
        
        for i, y in enumerate(y_data):
            if y > 0:  # Only label points with non-zero proportion
                ax.text(
                    x[i]+0.3, y+y_displacement, country, fontsize=8, 
                    ha='center', va='bottom', alpha=0.8
                )
    
    # Style the plot
    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor=colors[country], 
               markersize=16, alpha=0.7) for country in countries
    ]
    
    # Custom legend with uniform-sized markers
    ax.legend(legend_handles, countries, title='Countries', loc='upper right', fontsize=12)
    
    ax.set_xticks(x)  # Set tick locations
    ax.set_xticklabels(typs, rotation=0, fontsize=10)  # Set tick labels
    
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Classification', fontsize=14)
    ax.set_ylabel(y_axis_name, fontsize=14)
    
    # Display or save the plot
    plt.tight_layout()
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()

def scatterPlot_x_y_10Countries(df_plot, colors, title, x_axis_name, y_axis_name, save=False):
    fig, ax = plt.subplots(figsize=(10, 5))
    for country in countries:
        country_data = df_plot[df_plot['country'] == country]
        x, y = country_data['x'], country_data['y']
        
        ax.scatter(
            country_data['x'], country_data['y'], s=80, color=colors[country], edgecolors="none", label=country, alpha=0.7, marker='o'
        )
        
        ax.text(
            x+0.3, y, country, fontsize=10, 
            ha='center', va='bottom', alpha=0.8
        )
    
    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor=colors[country], 
               markersize=16, alpha=0.7) for country in countries
    ]
    
    # Custom legend with uniform-sized markers
    # ax.legend(legend_handles, countries, title='Countries', loc='upper left', fontsize=12)
    ax.legend(legend_handles, countries, title='Countries', bbox_to_anchor=(1.2, 1), fontsize=12)
    
    # ax.set_xticks()  # Set tick locations
    # ax.set_xticklabels(typs, rotation=0, fontsize=10)  # Set tick labels
    
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(x_axis_name, fontsize=14)
    ax.set_ylabel(y_axis_name, fontsize=14)

    ax.set_xlim(left=0)  # Set x-axis to start from 0
    ax.set_ylim(bottom=0)  # Set y-axis to start from 0
    
    # Display or save the plot
    # plt.tight_layout()
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
        
def scatterPlot_x_y_10Countries_1Instance(ax, df_plot, title, colors, x_axis_name, y_axis_name, normalize=False, save=False):
    for country in countries:
        country_data = df_plot[df_plot['country'] == country]
        x, y = country_data['x'], country_data['y']
    
        normalizing_coef = 1    
        if normalize:
            normalizing_coef = get_multiplier_for_normalization(country, "a0") # TODO make this a variable
        
        y = y * normalizing_coef
        
        ax.scatter(
            country_data['x'], country_data['y'], s=80, color=colors[country], edgecolors="none", label=country, alpha=0.7, marker='o'
        )
        
        ax.text(
            x+0.3, y, country, fontsize=10, 
            ha='center', va='bottom', alpha=0.8
        )
    
    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor=colors[country], 
               markersize=12, alpha=0.7) for country in countries
    ]
    
    # Custom legend with uniform-sized markers
    ax.legend(legend_handles, countries, title='Countries', loc='lower right', fontsize=8)
    # ax.legend(legend_handles, countries, title='Countries', bbox_to_anchor=(1.2, 1), fontsize=12)
    
    # ax.set_xticks()  # Set tick locations
    # ax.set_xticklabels(typs, rotation=0, fontsize=10)  # Set tick labels
    ax.set_title(title, fontsize=14)
    
    ax.set_xlabel(x_axis_name, fontsize=14)
    ax.set_ylabel(y_axis_name, fontsize=14)

    ax.set_xlim(left=0)  # Set x-axis to start from 0
    ax.set_ylim(bottom=0)  # Set y-axis to start from 0
    
def plot_4(df_plts, colorss, subtitles, x_axis_name, y_axis_name, save=False):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(30, 10))
    axes = axes.ravel()
    
    for (ax, df_plt, colors, subtitle) in zip(axes, df_plts, colorss, subtitles):
        scatterPlot_x_y_10Countries_1Instance(ax, df_plt, subtitle, colors, x_axis_name, y_axis_name, save=False)
        
    # plt.subplots_adjust(hspace=0.5, wspace=0.3)
    plt.subplots_adjust(hspace=0.5)
    plt.subplots_adjust(wspace=0.5)
    
    
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()

def scatterPlot_x_y_10Countries_plot_2(df_plts, colorss, title, subtitles, x_axis_name, y_axis_name, save=False):
    fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
    axes = axes.ravel()
    
    for (ax, df_plt, colors, subtitle) in zip(axes, df_plts, colorss, subtitles):
        scatterPlot_x_y_10Countries_1Instance(ax, df_plt, subtitle, colors, x_axis_name, y_axis_name, save=False)
        
    # plt.subplots_adjust(hspace=0.5, wspace=0.3)
    # plt.subplots_adjust(hspace=0.5)
    # plt.subplots_adjust(wspace=0.5)
    
    
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()

def plot_2(func1, df_plts, colorss, title, subtitles, x_axis_name, y_axis_name, normalize=[], save=False):
    fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
    axes = axes.ravel()
    
    for (ax, df_plt, colors, subtitle, _normalize) in zip(axes, df_plts, colorss, subtitles, normalize):
        func1(ax, df_plt, subtitle, colors, x_axis_name, y_axis_name, normalize=_normalize, save=False)
        
    # plt.subplots_adjust(hspace=0.5, wspace=0.3)
    # plt.subplots_adjust(hspace=0.5)
    # plt.subplots_adjust(wspace=0.5)
    
    
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
        
def privacy_collection_barplot_site_num(
    dfs, countries, title, subset_url_lst=None, normalize=True, mask_columns=None, subset_columns=None, save=False
):
    
    _check_data(dfs, countries)
    
    if subset_url_lst is not None:
        subset_url_lst = [clean_url(url) for url in subset_url_lst]
        dfs = [df[df.rootUrl.apply(clean_url).isin(subset_url_lst)] for df in dfs]

    if mask_columns is not None:
        dfs = [df[~df.typ.isin(mask_columns)] for df in dfs]

    if subset_columns is not None:
        dfs = [df[df.typ.isin(subset_columns)] for df in dfs]

    # Prepare data for plotting
    all_data = []
    totals = {}
    for df, country in zip(dfs, countries):
        # for each typ, only count once for each rootUrl
        df = df.drop_duplicates(subset=['typ', 'rootUrl'])  

        counts = df["typ"].value_counts(normalize=normalize).reset_index()
        counts.columns = ["type", "proportion"]
        counts["country"] = country
        all_data.append(counts)
        totals[country] = len(df)

    df_plot = pd.concat(all_data, ignore_index=True)
    
    # Unique types (x-axis categories)
    classifications = df_plot["type"].unique()
    x = range(len(classifications))
    
    cmap = cm.get_cmap("tab10", len(countries)) 
    colors = {country: cmap(i) for i, country in enumerate(countries)}  

    # Visualization
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=df_plot,
        x="type",
        y="proportion",
        hue="country",
        ci=None,
        edgecolor="black"
    )

    # Add vertical lines to separate types
    error_types_unique = df_plot["type"].unique()
    for i in range(len(error_types_unique) - 1):
        plt.axvline(x=i + 0.5, color="gray", linestyle="--", linewidth=1)

    # Style and labels
    plt.title(title, fontsize=16)
    plt.xlabel("Type", fontsize=14)
    plt.ylabel("Proportion", fontsize=14)
    if normalize:
        plt.ylim(0, 1)
    plt.xticks(rotation=30, fontsize=10)
    plt.legend(title="Country", fontsize=10)
    plt.tight_layout()

    # Save or display the plot
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches="tight")
    else:
        plt.show()
        
def us525_site_specific_frequency_plot(dfs, countries, title, subset_url_lst, save=False):
    """
    Generates a line plot showing the frequency of entries for specific URLs across countries.

    Parameters:
    - dfs (list): A list of DataFrames with 'rootUrl' columns.
    - countries (list): A list of country names corresponding to the DataFrames.
    - title (str): The title of the chart.
    - subset_url_lst (list): A list of specific URLs to analyze.
    - save (bool, optional): If True, saves the chart as a PNG file. Defaults to False.

    Returns:
    - None
    """
    
    if (not isinstance(dfs, list)) or (not isinstance(dfs[0], pd.DataFrame)):
        raise ValueError("dfs should be a list of dataframes")

    if not isinstance(countries, list) or len(countries) != len(dfs):
        raise ValueError("Length of countries must match the number of DataFrames in dfs")

    subset_url_lst = [clean_url(url) for url in subset_url_lst]
    
    for df in dfs:
        df.rootUrl = df.rootUrl.apply(clean_url)
    
    filtered_dfs = [df[df['rootUrl'].isin(subset_url_lst)] for df in dfs]
    
    df_plot = pd.DataFrame(0, index=subset_url_lst, columns=countries)
    
    for i, df in enumerate(filtered_dfs):
        country = countries[i]
        for url in subset_url_lst:
            url_count = df[df['rootUrl'] == url].shape[0]
            df_plot.at[url, country] = url_count
            # print(url_count)
    
    x = list(range(len(subset_url_lst)))
    
    fig, ax = plt.subplots(figsize=(20, 6))
    for country in countries:
        y_data = list(df_plot[country].values)
        ax.plot(x, y_data, 'x-', label=country, markeredgewidth=2, linewidth=2) 
        
    ax.legend(title='Countries', loc='upper right', fontsize=12)
    
    ax.set_xticks(x)  # Set tick locations
    ax.set_xticklabels(subset_url_lst, rotation=45, fontsize=10)  # Set tick labels

    # Set plot labels and title
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('URL', fontsize=14)
    ax.set_ylabel('Count', fontsize=14)

    # Display or save the plot
    plt.tight_layout()
    if save:
        plt.savefig(f"output/entries/{title}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()

    

