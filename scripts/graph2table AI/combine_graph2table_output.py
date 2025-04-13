import pandas as pd
import os
import glob
import re
from datetime import datetime

def combine_csv_files():
    # Define the directory path containing the CSV files
    csv_dir = r"C:\Users\clint\Desktop\Lifecycle Code\data\csv_data\graph2table\Raw"
    
    # Use glob to get all CSV files in the directory
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {csv_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files")
    
    # Create a list to store processed DataFrames
    processed_dfs = []
    
    # Read and process each CSV file
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        print(f"Reading {filename}")
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Rename the first column to "Date" regardless of its original name
        first_col_name = df.columns[0]
        df = df.rename(columns={first_col_name: "Date"})
        
        # Process dates with special handling for this format
        print(f"Processing dates in {filename}")
        df = process_dates(df)
        
        # Add source file information
        df['Source_File'] = filename
        
        # Ensure "Date" is the first column
        cols = df.columns.tolist()
        cols.remove("Date")
        df = df[["Date"] + cols]
        
        processed_dfs.append(df)
    
    # Combine all DataFrames with vertical concatenation
    print("Combining files with vertical concatenation based on Date column")
    combined_df = pd.concat(processed_dfs, ignore_index=True)
    
    # Sort the combined DataFrame by Date for better organization
    combined_df = combined_df.sort_values('Date')
    
    # Save the combined DataFrame
    output_dir = r"C:\Users\clint\Desktop\Lifecycle Code\data\csv_data\graph2table"
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "combined_data.csv")
    combined_df.to_csv(output_path, index=False)
    
    print(f"Combined data saved to {output_path}")
    print(f"Combined data shape: {combined_df.shape}")
    print(f"Date range: {combined_df['Date'].min()} to {combined_df['Date'].max()}")
    
    return combined_df

def process_dates(df):
    """
    Process date column with special handling for formats like 'Jan-16' and 'Feb' (without year)
    """
    current_year = None
    processed_dates = []
    
    for date_str in df['Date']:
        # Convert to string to ensure consistent handling
        date_str = str(date_str).strip()
        
        # Handle special case like "Dec (est.)"
        if '(' in date_str:
            # Remove any parenthetical annotations
            date_str = date_str.split('(')[0].strip()
        
        # Handle cases like 'Jan-16'
        if '-' in date_str:
            parts = date_str.split('-')
            month = parts[0]
            year_suffix = parts[1]
            
            # Clean the year suffix to handle any non-numeric characters
            year_suffix = ''.join(c for c in year_suffix if c.isdigit())
            
            # Convert year suffix to full year (e.g., '16' -> '2016')
            if len(year_suffix) == 2:
                full_year = int("20" + year_suffix)
            else:
                full_year = int(year_suffix)
            
            current_year = full_year
            formatted_date = f"{month} {full_year}"
            
        # Handle cases like 'Feb' (month only, need to infer year)
        else:
            month = date_str
            if current_year is None:
                # If we haven't seen a year yet, default to 2016 (based on your example)
                current_year = 2016
            
            formatted_date = f"{month} {current_year}"
            
            # If month is December, increment year for next entry
            if month.lower() == 'dec':
                current_year += 1
        
        processed_dates.append(formatted_date)
    
    # Replace the Date column with processed dates
    df['Date'] = processed_dates
    
    # Convert to datetime objects
    df['Date'] = pd.to_datetime(df['Date'], format='%b %Y', errors='coerce')
    
    # Check for parsing errors
    if df['Date'].isna().any():
        print(f"Warning: Some dates could not be parsed. First few problematic values: {df.loc[df['Date'].isna(), 'Date'].head().tolist()}")
    
    return df

# Execute the function
if __name__ == "__main__":
    combine_csv_files()