import pandas as pd
import json

def load_entries(filename):
    return pd.read_csv(filename)

def load_err_log(filename):
    with open(filename, 'r') as f:
        return json.load(f)
    
def clean_url(url):
    """Cleans the url, keeping only the essential part.

    Args:
        url (str): the url to clean.

    Returns:
        str: the cleaned url.
    """
    url = url.replace('www.', '')
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    components = url.split('/')
    return components[0]

def get_multiplier_for_normalization(country, CRAWL_ID):
    """Normalization is only needed for the counry-specific crawls, since any error in US sites for any country will be resulted in the removal of data for such site for all countries. 
    
    coefficient for normalization: total number of sites / number of sites without errors

    Args:
        TODO
    """
    
    total_site_num = 525
    
    sites_crawl_path = f"../data_other/{country}-top-525.csv"
    error_log_path = f"../data/crawl_{CRAWL_ID}/error-logging_{country}_{CRAWL_ID}.json"
    
    df_sites = pd.read_csv(sites_crawl_path)

    try:
        error_log = load_err_log(error_log_path)
    except FileNotFoundError:
        print("Missing data for {country}")
        return
    
    error_sites = []
    for key, value in error_log.items():
        for site in value:
            error_sites.append(clean_url(site))
            
    site_urls = df_sites['Site URL'].values
    cleaned_site_urls = [clean_url(url) for url in site_urls]

    matching_indices = [
        idx for idx, cleaned_url in enumerate(error_sites) if cleaned_url in cleaned_site_urls
    ]
    
    country_error_num = len(
        set(
            [cleaned_site_urls.index(clean_url(error_sites[idx])) for idx in matching_indices]
        )
    )
        
    coefficient = total_site_num / (total_site_num - country_error_num)
    
    return coefficient