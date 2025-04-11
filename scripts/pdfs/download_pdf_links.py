# Script to download PDF links from csv 
# Script to download PDF links from csv

import os
import requests
import pandas as pd
from urllib.parse import urlparse
from tqdm import tqdm
import time
import csv
from datetime import datetime

def main():
    # Load your data - you need to specify your data source
    file_path = r"C:\Users\clint\Desktop\Lifecycle Code\data\pdf_links\combined\combined_pdf_links.csv"
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Define the output directory
    output_dir = r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs"
    # Create logs directory
    logs_dir = r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\logs"

    # Create the directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # Create log files with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    non_pdf_log = os.path.join(logs_dir, f"non_pdf_links_{timestamp}.csv")
    duplicate_log = os.path.join(logs_dir, f"duplicate_links_{timestamp}.csv")
    error_log = os.path.join(logs_dir, f"error_links_{timestamp}.csv")

    # Initialize log files with headers
    with open(non_pdf_log, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Content-Type'])

    with open(duplicate_log, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL'])

    with open(error_log, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Error'])

    # Track downloaded URLs to avoid duplicates
    downloaded_urls = set()
    successful_downloads = 0
    skipped_duplicates = 0
    non_pdf_links = 0
    error_links = 0

    # Verify data is loaded before starting the loop
    if len(data) == 0:
        raise ValueError("No data available. Please ensure the CSV file contains data before running this code.")

    # Define a maximum runtime to prevent infinite loops (e.g., 1 hour)
    max_runtime = 3600  # in seconds
    start_time = time.time()

    # Download PDFs from the DataFrame
    for index, row in tqdm(data.iterrows(), total=len(data), desc="Downloading PDFs"):
        # Check if we've exceeded the maximum runtime
        if time.time() - start_time > max_runtime:
            print(f"Maximum runtime of {max_runtime/60:.1f} minutes reached. Stopping.")
            break
            
        if pd.notna(row['link']):
            url = row['link']
            
            # Skip if this URL has already been downloaded
            if url in downloaded_urls:
                skipped_duplicates += 1
                # Log duplicate link
                with open(duplicate_log, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([url])
                continue
            
            # Generate a filename from the URL or use the index
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # If filename is empty or doesn't end with .pdf, create a default name
            if not filename or not filename.lower().endswith('.pdf'):
                filename = f"document_{index}.pdf"
            
            # Check for filename collisions and add a suffix if needed
            base_name, extension = os.path.splitext(filename)
            counter = 1
            output_path = os.path.join(output_dir, filename)
            
            while os.path.exists(output_path):
                filename = f"{base_name}_{counter}{extension}"
                output_path = os.path.join(output_dir, filename)
                counter += 1
            
            # Download the PDF
            success = download_pdf(url, output_path, non_pdf_log, error_log)
            if success:
                downloaded_urls.add(url)
                successful_downloads += 1
            else:
                # Remove the file if it was created but is not a PDF
                if os.path.exists(output_path):
                    os.remove(output_path)
                non_pdf_links += 1

    # Create a summary log file
    summary_log = os.path.join(logs_dir, f"download_summary_{timestamp}.csv")
    with open(summary_log, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Successful Downloads', successful_downloads])
        writer.writerow(['Skipped Duplicates', skipped_duplicates])
        writer.writerow(['Non-PDF Links', non_pdf_links])
        writer.writerow(['Runtime (minutes)', f"{(time.time() - start_time)/60:.1f}"])

    print(f"Downloaded {successful_downloads} PDFs.")
    print(f"Skipped {skipped_duplicates} duplicate links.")
    print(f"Disregarded {non_pdf_links} non-PDF links.")
    print(f"Total runtime: {(time.time() - start_time)/60:.1f} minutes")
    print(f"\nLog files created in {logs_dir}:")
    print(f"- Non-PDF links: {os.path.basename(non_pdf_log)}")
    print(f"- Duplicate links: {os.path.basename(duplicate_log)}")
    print(f"- Error links: {os.path.basename(error_log)}")
    print(f"- Summary: {os.path.basename(summary_log)}")

# Function to download a PDF file
def download_pdf(url, output_path, non_pdf_log, error_log, timeout=30):
    try:
        # Send a GET request to the URL with timeout
        response = requests.get(url, stream=True, timeout=timeout, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if the content is a PDF
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"Link is not a PDF: {url} (Content-Type: {content_type})")
            # Log non-PDF link
            with open(non_pdf_log, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([url, content_type])
            return False
        
        # Write the content to a file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except requests.Timeout:
        error_msg = f"Timeout: Request took longer than {timeout} seconds"
        print(f"Timeout downloading {url}: {error_msg}")
        # Log error
        with open(error_log, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([url, error_msg])
        return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        # Log error
        with open(error_log, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([url, str(e)])
        return False

if __name__ == "__main__":
    main()