# This script creates the 50 random sites that includes  
# 5 sites from each of the 8 countries' top 525 lists and 10 sites from US' top 525 list
# 8 countries are: (australia, brazil, canada, germany, india, singapore, south africa, spain)

import pandas as pd
import random
import re

def clean_url(url):
    """
    Clean the URL by removing 'https://', 'http://', and 'www.'
    """
    url = re.sub(r'https?://(www\.)?', '', url)
    return url.rstrip('/')


countries = ['australia', 'brazil', 'canada', 'germany', 'india', 'singapore', 'southafrica', 'spain']
input_paths = {country: f'../crawl-lists/{country}-top-525.csv' for country in countries}
input_paths['us'] = '../crawl-lists/unitedstates-top-525.csv'
deduplication_path = 'current_list_for_deduplication.csv'
current_list = pd.read_csv(deduplication_path)
current_list['cleaned_url'] = current_list['Site URL'].apply(clean_url)

# Select non-duplicate random sites from a given list
def select_sites(country, num_sites):
    df = pd.read_csv(input_paths[country])
    df['cleaned_url'] = df['Site URL'].apply(clean_url)
    
    selected_sites = []
    while len(selected_sites) < num_sites:
        potential_site = df.sample(n=1).iloc[0]
        if potential_site['cleaned_url'] not in current_list['cleaned_url'].values and potential_site['cleaned_url'] not in [site['cleaned_url'] for site in selected_sites]:
            selected_sites.append(potential_site)
    
    return selected_sites

# Select 5 random sites from each of the specified countries and 10 from the US
selected_sites = []
for country in countries:
    selected_sites.extend(select_sites(country, 5))

selected_sites.extend(select_sites('us', 10))

# Create a DataFrame for the final selected sites and drop the 'cleaned_url' column
final_sites_df = pd.DataFrame(selected_sites).drop(columns=['cleaned_url'])

# Output the final list
output_path = 'random_50_sites_by_countries.csv'
final_sites_df[['Site URL']].to_csv(output_path, index=False)
print(f"Selected sites saved to {output_path}")
