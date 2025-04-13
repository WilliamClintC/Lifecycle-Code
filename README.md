# JD Power Data Extraction Project

## Project Overview

This data extraction project was completed for Professor Ron Yang at the UBC Sauder School of Business. The objective was to extract and process retail price datasets from JD Power automotive publications, primarily available in PDF format, and convert them into structured, analyzable data.

The project involved developing an end-to-end pipeline that began with scraping PDFs from the internet using various web scraping techniques (Google dorking, BeautifulSoup for HTML parsing, and Selenium for automated browser interactions). These PDFs were then processed to extract charts, which were subsequently digitized into data points, followed by validation of the extraction accuracy.

The final datasets are available in two formats:

- `data/final_dataset/AI.csv`: Data generated using Graph2Table AI extraction methods
- `data/final_dataset/Webplot_Digitizer.csv`: Data generated using WebPlotDigitizer for validation and comparison purposes

The methodology combines automated extraction techniques with manual verification to ensure data quality and consistency.

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
- Manually fixed date inconsistencies 
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

- Extracted charts from PDFs for analysis using `scripts/pdfs/extract_pdf_content.py`
- Tested various extraction approaches:
  - Title-based identification methods proved ineffective due to inconsistent or unreadable text in some charts
  - Embedded image detection showed limited success
  - **Contour detection** ultimately provided the best results
- Manual corrections implemented according to error logs at `data/extracted_images/logs/extraction_errors.csv`

### 6. Image-to-CSV Conversion

- Utilized Graph2Table AI for converting chart images to structured CSV datasets
- Output files stored in `data/csv_data/graph2table/`
- Manually identified and removed problematic conversions (e.g., the 03_2025 dataset)

### 7. Manual Verification Process

- Created reference datasets using WebPlotDigitizer for validation purposes `data/csv_data/webplotdigitizer/combined_digitizer_data.csv`
- Manually digitized selected benchmark images (earliest, latest, middle timepoints, plus one 2YO truck dataset) 
- Combined outputs stored at `data\csv_data\graph2table\combined_data.csv`

### 8. Data Analysis & Validation

- Developed Jupyter notebooks to analyze and compare AI-generated vs. manually digitized data
- Conducted quality assurance and validation tests across the dataset
- Analysis files available in the `notebooks/` directory

### 9. Utility Tools

Several utility scripts were developed to support the workflow:

- `scripts/utils/image_viewer.py` - Visual inspection tool for extracted images
- `scripts/utils/pdf_image_curator.py` - Manual correction utility for extracted images
- `scripts/utils/img_sorter.py` - Organization tool for image datasets
- `scripts/utils/img_errors_fix_img_to_csv.py` - Error correction tool for problematic image-to-CSV conversions

## Repository Structure

```
├── README.md
├── column_processor.ipynb        # Notebook for processing column data
├── archived_attempts/            # Previous methodologies and approaches
│   └── Chart Extraction/         # Early attempts at chart extraction
├── data/
│   ├── csv_data/                 # CSV outputs from image processing
│   │   ├── graph2table/          # AI-generated CSV data
│   │   └── webplotdigitizer/     # Manually verified CSV data
│   ├── extracted_images/         # Charts extracted from PDFs
│   │   └── logs/                 # Error logs from extraction process
│   ├── pdf_links/                # Scraped PDF links
│   │   ├── combined/             # Aggregated link collections
│   │   └── individual/           # Source-specific link collections
│   └── raw_pdfs/                 # Downloaded PDF source files
│       └── logs/                 # Download error logs
├── notebooks/                    # Analysis and verification notebooks
│   └── CSV_explorer*.ipynb       # Various data exploration notebooks
├── outputs/                      # Output visualizations and reports
└── scripts/
    ├── graph2table AI/           # Scripts for AI-based chart digitization
    ├── pdfs/                     # PDF processing utilities
    └── utils/                    # Helper scripts and utilities
```
