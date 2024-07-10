import pandas as pd

input_file = 'tranco_Q9Z84-1m.csv/top-1m.csv'
df = pd.read_csv(input_file, header=None, names=['Rank', 'Domain'])

# Split the Rank and Domain columns if they are in a single column
if df.shape[1] == 1:
    df[['Rank', 'Domain']] = df[0].str.split(',', 1, expand=True)
    df = df.drop(columns=[0])
df['Rank'] = df['Rank'].astype(int)

# Filter South Korea websites
south_korea_websites = df[df['Domain'].str.endswith('.kr')]

# Take the top 1200 South Korea websites
top_1200_south_korea_websites = south_korea_websites.head(1200).copy()

# Create the local rank format
top_1200_south_korea_websites.loc[:, 'Local Rank'] = range(1, len(top_1200_south_korea_websites) + 1)
top_1200_south_korea_websites.loc[:, 'Domain'] = 'https://' + top_1200_south_korea_websites['Domain']
top_1200_south_korea_websites = top_1200_south_korea_websites[['Local Rank', 'Domain']]

output_file = 'top_1200_south_korea_websites.csv'
top_1200_south_korea_websites.to_csv(output_file, index=False, header=False)
print(f"The top 1200 South Korea websites have been saved to {output_file}")
