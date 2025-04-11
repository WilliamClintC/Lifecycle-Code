# Project Overview

This is a data scraping project done for Professor. Ron Yang at UBC Sauder School of Business
The project extracts retail datasets from JD Power. 

The project does the following.

1. Collect all available PDF links through the following website
    1. Official Website (C:\Users\clint\Desktop\Lifecycle Code\scripts\Link Scraper\official_website_scrape_links.py)
    2. Dorking (C:\Users\clint\Desktop\Lifecycle Code\scripts\Link Scraper\dorking_scrape_links.py)
    3. Official Website History Link (C:\Users\clint\Desktop\Lifecycle Code\scripts\Link Scraper\jdpower_history_scrape_links.py)
        1. Manually remove "used car" links
        2. Change the intermediary links to correct link (if intermediary link error exist the date is also wrong) (C:\Users\clint\Desktop\Lifecycle Code\data\pdf_links\individual\jdpower_commercial_truck_guidelines.csv)
2. Download all the PDF links (C:\Users\clint\Desktop\Lifecycle Code\scripts\download_pdf_links.py)
    1. redownload/analyze manually error links (C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\logs\error_links_20250411_085608.csv) (C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\logs\error_links_20250411_085608.csv)
    2. Rename PDFs (C:\Users\clint\Desktop\Lifecycle Code\scripts\pdfs\pdf_renamer.py)
    3. Manually Delete False Positive PDFs (C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs)
    4. Manually Delete Duplicated PDFs
3. Extract PDF tables
    1. Tested different methodologies 
        1. Title Identification (does not work: Some charts have unreadable text) (C:\Users\clint\Desktop\Lifecycle Code\archived_attempts\Chart Extraction\chart_extractor (title_identification).ipynb)