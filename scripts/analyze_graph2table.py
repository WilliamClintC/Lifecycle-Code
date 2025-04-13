from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import shutil
import glob
import re
from pathlib import Path
import csv
from datetime import datetime

def get_image_files(directory):
    """Get all image files from the specified directory"""
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
    
    return image_files

def log_error_to_csv(image_path, error_type, error_message):
    """Log an error to the CSV file"""
    error_log_path = r"C:\Users\clint\Desktop\Lifecycle Code\data\csv_data\graph2table\processing_errors.csv"
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(error_log_path)
    
    # Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare row data
    row_data = {
        'Timestamp': timestamp,
        'Image_Name': os.path.basename(image_path),
        'Image_Path': image_path,
        'Error_Type': error_type,
        'Error_Message': error_message
    }
    
    # Open file in append mode
    with open(error_log_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=row_data.keys())
        
        # Write header if file is being created
        if not file_exists:
            writer.writeheader()
        
        # Write the error data
        writer.writerow(row_data)
    
    print(f"Error logged to {error_log_path}")

def automate_graph2table_upload(file_path):
    # Setup Chrome WebDriver
    driver = None
    
    try:
        driver = webdriver.Chrome()
        
        # Maximize the browser window to ensure all elements are visible
        driver.maximize_window()
        
        # Navigate to the website
        driver.get("https://graph2table.com/")
        print(f"\nProcessing image: {os.path.basename(file_path)}")
        print("Navigating to Graph2Table...")
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 20)  # Increased timeout for better reliability
        
        # Find the hidden file input element
        file_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        
        # Sometimes file inputs are hidden - make it visible with JavaScript if needed
        driver.execute_script("arguments[0].style.display = 'block';", file_input)
        
        # Send the file path to the input
        print(f"Uploading file: {file_path}")
        file_input.send_keys(file_path)
        
        # Wait for the file to be processed
        print("File uploaded, waiting for processing...")
        
        # Try to find the download button with a more robust approach
        try:
            # Wait for the download button to be present in the DOM
            download_button = wait.until(
                EC.presence_of_element_located((By.ID, "downloadBtn"))
            )
            
            # Scroll to the button to ensure it's in view
            driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
            time.sleep(1)  # Short pause to allow scrolling to complete
            
            # Now wait for it to be clickable
            download_button = wait.until(
                EC.element_to_be_clickable((By.ID, "downloadBtn"))
            )
            
            print("Processing complete, clicking download button...")
            # Try direct click first
            try:
                download_button.click()
            except:
                # If direct click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", download_button)
                
        except Exception as e:
            print(f"Error with download button: {e}")
            print("Trying alternative approach...")
            
            # Try finding by XPath or other selectors if ID fails
            try:
                download_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Download') or contains(@class, 'download')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                driver.execute_script("arguments[0].click();", download_button)
            except Exception as inner_e:
                print(f"Alternative approach also failed: {inner_e}")
                raise
        
        # Give time for the download to start
        print("Download initiated, waiting for download to complete...")
        time.sleep(5)
        
        print("Download should be complete")
        
        # Process the downloaded file
        try:
            process_downloaded_file(file_path)
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing downloaded file: {error_msg}")
            log_error_to_csv(file_path, "CSV Processing Error", error_msg)
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"An error occurred: {error_msg}")
        print("Try checking if the file path exists and is accessible.")
        log_error_to_csv(file_path, "Browser Automation Error", error_msg)
        return False
    finally:
        # Properly close the browser with error handling
        if driver:
            try:
                driver.quit()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {e}")
                # If normal quit fails, try more aggressive termination
                try:
                    driver.close()
                    print("Browser tab closed")
                except:
                    print("Could not close browser normally")
    
    return True  # If we reach here, processing was successful

def process_downloaded_file(image_path):
    """Process the downloaded CSV file by moving and renaming it"""
    try:
        # Create target directory if it doesn't exist
        target_dir = r"C:\Users\clint\Desktop\Lifecycle Code\data\csv_data\graph2table"
        os.makedirs(target_dir, exist_ok=True)
        
        # Get the download directory (specific Downloads folder)
        downloads_dir = r"C:\Users\clint\Downloads"
        
        # Find the most recently downloaded CSV file
        csv_files = glob.glob(os.path.join(downloads_dir, "*.csv"))
        if not csv_files:
            print("No CSV files found in the Downloads directory.")
            return
        
        # Get the most recent file
        latest_file = max(csv_files, key=os.path.getmtime)
        print(f"Found downloaded CSV: {latest_file}")
        
        # Extract the base name from the image path
        image_name = os.path.basename(image_path)
        
        # Use regex to extract XX_YYYY pattern from the filename
        match = re.search(r'(\d+_\d+)', image_name)
        if match:
            base_name = match.group(1)
        else:
            # Fallback if the pattern isn't found
            base_name = os.path.splitext(image_name)[0]
            print(f"Warning: Could not extract pattern from filename. Using {base_name} instead.")
        
        # Check if file with this name already exists and add counter if needed
        counter = 1
        new_filename = f"{base_name}.csv"
        full_path = os.path.join(target_dir, new_filename)
        
        while os.path.exists(full_path):
            counter += 1
            new_filename = f"{base_name}_{counter}.csv"
            full_path = os.path.join(target_dir, new_filename)
        
        # Copy the file to the new location with the new name
        shutil.copy2(latest_file, full_path)
        print(f"File renamed and moved to: {full_path}")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

def process_all_images(image_paths=None):
    """Process specified images or all images in the extracted_images directory (top level only)"""
    if image_paths is None:
        # Get only top level files from extracted_images directory, not from subdirectories
        image_directory = r"C:\Users\clint\Desktop\Lifecycle Code\data\extracted_images"
        
        # Get all files with image extensions directly in the top folder (not recursive)
        image_files = []
        for item in os.listdir(image_directory):
            item_path = os.path.join(image_directory, item)
            # Only include if it's a file (not directory) and has an image extension
            if os.path.isfile(item_path) and any(item_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                image_files.append(item_path)
        images = image_files
    else:
        images = image_paths

    if not images:
        print("No image files found to process.")
        return

    print(f"Found {len(images)} images to process")

    # Keep track of success and failure
    success_count = 0
    failure_count = 0

    # Process each image
    for image_path in images:
        try:
            result = automate_graph2table_upload(image_path)
            if result:
                print(f"Successfully processed: {os.path.basename(image_path)}")
                success_count += 1
            else:
                print(f"Failed to fully process: {os.path.basename(image_path)}")
                failure_count += 1
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to process {os.path.basename(image_path)}: {error_msg}")
            log_error_to_csv(image_path, "Unexpected Error", error_msg)
            failure_count += 1
            continue

    # Print summary
    print("\n=== Processing Complete ===")
    print(f"Total images: {len(images)}")
    print(f"Successfully processed: {success_count}")
    print(f"Failed to process: {failure_count}")

    if failure_count > 0:
        print(f"Check the error log at: C:\\Users\\clint\\Desktop\\Lifecycle Code\\data\\csv_data\\graph2table\\processing_errors.csv")

if __name__ == "__main__":
    # Process all images in the top-level extracted_images directory
    process_all_images()