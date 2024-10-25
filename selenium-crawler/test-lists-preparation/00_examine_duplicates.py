import pandas as pd
import os

# Checks the number of sites we picked from each websites_list
location_websites_folder = "selenium-crawler/test-lists-preparation/location_websites_list/"
random_50_tracking_tech_path = "selenium-crawler/test-lists-preparation/random_50_sites_by_tracking_tech.csv"

df_tracking_tech = pd.read_csv(random_50_tracking_tech_path)

for location_website in os.listdir(location_websites_folder):
    file_name = location_websites_folder + location_website
    df_location = pd.read_csv(file_name)
    
    common_columns = df_location.columns.intersection(df_tracking_tech.columns)
    duplicate_rows = pd.merge(df_location, df_tracking_tech, on=list(common_columns), how='inner')
    num_duplicates = len(duplicate_rows)

    print(f"{location_website}: {num_duplicates}")