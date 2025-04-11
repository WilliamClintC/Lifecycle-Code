import os
import re

# Directory containing the PDF files
pdf_directory = r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs"

# Helper function to convert month name to number
def month_to_number(month_name):
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    return months.get(month_name.lower(), "00")

# Get all files in the directory
files = os.listdir(pdf_directory)

for filename in files:
    if filename.lower().endswith('.pdf'):
        full_path = os.path.join(pdf_directory, filename)
        new_filename = None
        
        # Try to match decimal format like "04.2019_Commercial Truck Guidelines_1.pdf"
        match = re.match(r"(\d+)\.(\d{4})_.*\.pdf", filename)
        if match:
            month, year = match.groups()
            new_filename = f"{month}_{year}.pdf"
        
        # Try to match month name format like "August_2022_Guidelines.pdf"
        if not new_filename:
            match = re.match(r"([A-Za-z]+)_(\d{4})_.*\.pdf", filename)
            if match:
                month_name, year = match.groups()
                month_num = month_to_number(month_name)
                new_filename = f"{month_num}_{year}.pdf"
        
        # If a new filename was generated
        if new_filename:
            new_full_path = os.path.join(pdf_directory, new_filename)
            
            # Check if destination file already exists
            if os.path.exists(new_full_path) and full_path != new_full_path:
                print(f"Skipping {filename} - target file {new_filename} already exists")
                continue
                
            # Rename the file
            try:
                os.rename(full_path, new_full_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename}: {e}")
        else:
            print(f"Skipping {filename} - doesn't match any expected pattern")

print("Renaming completed.")