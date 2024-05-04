import pandas as pd
import os

def merge_csv_files(folder_path, output_file):
    # Get a list of all CSV files in the specified folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    # Initialize an empty list to store the dataframes
    dataframes = []
    
    # Loop over the list of csv files
    for csv_file in csv_files:
        # Construct the full path to the file
        file_path = os.path.join(folder_path, csv_file)
        # Read the CSV file and append it to the list of dataframes
        df = pd.read_csv(file_path)
        dataframes.append(df)
    
    # Concatenate all dataframes in the list
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Save the concatenated dataframe to a new CSV file
    merged_df.to_csv(os.path.join(folder_path, output_file), index=False)
    print(f'Merged file saved as: {output_file}')

# Example usage
folder_path = 'scraped_links'
output_file = 'merged_car_links.csv'
merge_csv_files(folder_path, output_file)
