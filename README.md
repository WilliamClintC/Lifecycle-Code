# Project Overview

This data scraping project was completed for Professor Ron Yang at the UBC Sauder School of Business. The objective was to extract and process retail datasets from JD Power publications, primarily in PDF format.

## Project Workflow

### 1. Link Collection

PDF links were scraped using multiple methods:

- **Official Website Scraper**  
  `official_website_scrape_links.py`  
  *(Path: `C:\Users\clint\Desktop\Lifecycle Code\scripts\Link Scraper`)*

- **Dorking-Based Scraper**  
  `dorking_scrape_links.py`  
  *(Path: same as above)*

- **Historical Link Scraper (JD Power)**  
  `jdpower_history_scrape_links.py`

### 2. Link Cleaning and Validation

- Manually removed irrelevant links (e.g., related to used cars).
- Corrected intermediary links, ensuring date consistency.  
  *(CSV path: `data\pdf_links\individual\jdpower_commercial_truck_guidelines.csv`)*

### 3. PDF Downloading

- All valid PDF links were downloaded using `download_pdf_links.py`.

### 4. Error Handling

- Identified and reprocessed problematic or failed downloads.  
  *(Log path: `data\raw_pdfs\logs\error_links_20250411_085608.csv`)*

### 5. File Management

- Renamed PDFs for clarity and consistency using `pdf_renamer.py`.
- Manually removed false positives and duplicate files.  
  *(Folder: `data\raw_pdfs`)*

### 6. Data Extraction

- Extracted tables from the PDFs for analysis.
- Tested various extraction approaches.
  - *Note: Title-based identification methods proved ineffective due to inconsistent or unreadable text in some charts.*  
    *(Notebook path: `archived_attempts\Chart Extraction\chart_extractor (title_identification).ipynb`)*
