# JD Power Data Extraction Project

## Project Overview

This data scraping project was completed for Professor Ron Yang at the UBC Sauder School of Business. The objective was to extract and process retail datasets from JD Power publications, primarily in PDF format.

## Project Workflow

### 1. Link Collection

PDF links were scraped using multiple methods:

- **Official Website Scraper**  
  `scripts/Link Scraper/official_website_scrape_links.py`

- **Dorking-Based Scraper**  
  `scripts/Link Scraper/dorking_scrape_links.py`

- **Historical Link Scraper (JD Power)**  
  `scripts/Link Scraper/jdpower_history_scrape_links.py`

### 2. Link Cleaning and Validation

- Manually removed irrelevant links (e.g., related to used cars)
- Manually corrected intermediary links
- Manually fixed date Inconsistencies 
  *(CSV location: `data/pdf_links/individual/jdpower_commercial_truck_guidelines.csv`)*

### 3. PDF Downloading

- All valid PDF links were downloaded using `scripts/pdfs/download_pdf_links.py`
- Manually identified and reprocessed problematic or failed downloads
- Error logs stored in `data/raw_pdfs/logs/`

### 4. File Management

- Renamed PDFs for clarity and consistency using `scripts/pdfs/pdf_renamer.py`
- Manually removed false positives and duplicate files
- All processed PDFs stored in `data/raw_pdfs/`

### 5. Data Extraction

- Extracted tables from PDFs for analysis using `scripts/pdfs/extract_pdf_content.py`
- Tested various extraction approaches:
  - Title-based identification methods proved ineffective due to inconsistent or unreadable text in some charts
  - Embedded image detection showed limited success
  - **Contour detection** ultimately provided the best results
-Manual Correction imlemented according to error log data\extracted_images\logs\extraction_errors.csv

6. graph2table AI conversion
converts the images to csv datasets 
placed the outputs here data\csv_data\graph2table
7. WebPlotDigitizer Output  
manually collected webplot digitzer output from 3 images (earliest, latest, middle, and one plot with 2YO truck data) C:\Users\clint\Desktop\Lifecycle Code\data\csv_data\webplotdigitizer\combined_digitizer_data.csv

8. used ntoebook to analyze AI vs Manual collection C:\Users\clint\Desktop\Lifecycle Code\notebooks


also used util scripts\utils\image_viewer.py to hlep view the images to check for errors
utilities for manual fixes C:\Users\clint\Desktop\Lifecycle Code\scripts\utils\pdf_image_curator.py
C:\Users\clint\Desktop\Lifecycle Code\scripts\utils\img_sorter.py  

C:\Users\clint\Desktop\Lifecycle Code\scripts\utils\img_errors_fix_img_to_csv.py


## Repository Structure

```
├── README.md
├── archived_attempts/
│   └── Chart Extraction/
├── data/
│   ├── corrected_images/
│   ├── digitized_data/
│   ├── edited_pdfs/
│   ├── extracted_images/
│   ├── final_dataset/
│   ├── pdf_links/
│   └── raw_pdfs/
├── notebooks/
├── Sandbox/
└── scripts/
    ├── analyze_graph2table.py
    ├── analyze_webplot.py
    ├── compare_outputs.py
    ├── pdfs/
    └── utils/
