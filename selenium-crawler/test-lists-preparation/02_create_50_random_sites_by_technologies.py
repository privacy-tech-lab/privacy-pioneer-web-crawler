import pandas as pd
import random
import re
import os

def clean_url(url):
    """
    Clean the URL by removing 'https://', 'http://', and 'www.'
    """
    url = re.sub(r'https?://(www\.)?', '', url)
    return url.rstrip('/')

fingerprint_folder = 'fingerprint_websites_list'
location_folder = 'location_websites_list'
deduplication_path = 'current_list_for_deduplication.csv'
current_list = pd.read_csv(deduplication_path)
current_list['cleaned_url'] = current_list['Site URL'].apply(clean_url)

def select_sites(folder, num_sites_per_file):
    selected_sites = []
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    for file in files:
        df = pd.read_csv(os.path.join(folder, file))
        df['cleaned_url'] = df['Site URL'].apply(clean_url)
        
        while len(selected_sites) < num_sites_per_file * len(files):
            potential_site = df.sample(n=1).iloc[0]
            if potential_site['cleaned_url'] not in current_list['cleaned_url'].values and potential_site['cleaned_url'] not in [site['cleaned_url'] for site in selected_sites]:
                selected_sites.append(potential_site)
                if len([site for site in selected_sites if site['cleaned_url'] == potential_site['cleaned_url']]) > 1:
                    selected_sites.pop()
    
    return selected_sites

# Select sites from each folder
fingerprint_sites = select_sites(fingerprint_folder, 4)
location_sites = select_sites(location_folder, 6)

selected_sites = fingerprint_sites + location_sites
final_sites_df = pd.DataFrame(selected_sites).drop(columns=['cleaned_url'])

# Output the final list
output_path = 'random_50_sites_by_tracking_tech.csv'
final_sites_df[['Site URL']].to_csv(output_path, index=False)

print(f"Selected sites saved to {output_path}")
