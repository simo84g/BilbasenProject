import pandas as pd
import os

def merge_csv_files(folder_path, output_file):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    dataframes = [] #Make empty dataframe
    
    # Loop csv files
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        df = pd.read_csv(file_path)
        dataframes.append(df)
    
    # Concatenate dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Save to a new CSV file
    merged_df.to_csv(os.path.join(folder_path, output_file), index=False)
    print(f'Merged file saved as: {output_file}')

folder_path = 'scraped_links'
output_file = 'merged_car_links.csv'
merge_csv_files(folder_path, output_file)
