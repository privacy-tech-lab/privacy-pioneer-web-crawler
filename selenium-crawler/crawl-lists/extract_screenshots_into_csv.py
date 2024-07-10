import os
import csv

#This script takes the screenshots names of each sites and put them into a csv file.

folder_path = 'screenshots'  
def extract_url(file_name):
    base_url = file_name.split('___')[1].replace('.png', '').replace('_', '.')
    return f"https://{base_url}"
file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
urls = [extract_url(file) for file in file_names]
csv_file_path = 'south-korea-top-525.csv'  
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Site URL"])
    for url in urls:
        writer.writerow([url])

print(f"URLs have been saved to {csv_file_path}")
