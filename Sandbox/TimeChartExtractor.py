import fitz  # PyMuPDF
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import cv2
import shutil
import re
import csv
from datetime import datetime

def extract_retail_price_plots(pdf_path, output_dir=None, relaxed_detection=True, error_log_path=None):
    """
    Extract retail price charts from a PDF specifically focusing on 
    Average Retail Selling Price plots.

    Parameters:
        pdf_path (str): Path to the PDF file
        output_dir (str, optional): Output directory for extracted plots
        relaxed_detection (bool): If True, use relaxed criteria for finding charts
        error_log_path (str, optional): Path to save error logs
    """
    if output_dir is None:
        output_dir = os.path.join(r"C:\Users\clint\Desktop\Lifecycle Code\Sandbox", "retail_price_plots")

    os.makedirs(output_dir, exist_ok=True)
    print(f"Creating output directory: {output_dir}")

    doc = fitz.open(pdf_path)
    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")

    # Dictionary to store results
    retail_price_results = {
        "pdf_name": pdf_name,
        "total_pages": doc.page_count,
        "plots_found": []
    }
    
    # Focus specifically on retail price indicators
    retail_price_indicators = [
        "Average Retail Selling Price",
        "Avg. Retail Selling Price", 
        "Retail Selling Price",
        "Retail Price",
        "Average Price"
    ]

    # Track if we've found a plot in this PDF
    found_plot = False
    error_details = {
        "pdf_name": pdf_name,
        "pdf_path": pdf_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": "No retail price chart found",
        "pages_checked": doc.page_count,
        "detected_keywords": []
    }

    for page_num, page in enumerate(doc):
        page_index = page_num + 1
        print(f"\nAnalyzing page {page_index} for Retail Selling Price charts...")
        
        # Look for retail price indicators in text blocks
        text_dict = page.get_text("dict")
        text_blocks = text_dict["blocks"]
        price_related_text = []
        
        # First pass - find retail price text indicators
        for block in text_blocks:
            if block["type"] == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        
                        # Check if the text matches any of our retail price indicators
                        if any(indicator.lower() in text.lower() for indicator in retail_price_indicators):
                            price_related_text.append({
                                'text': text,
                                'rect': span["bbox"],
                                'confidence': 10  # High confidence for exact matches
                            })
                            print(f"Found indicator: '{text}' on page {page_index}")
                            
                            # Add to error details in case we can't find a full chart
                            if text not in error_details["detected_keywords"]:
                                error_details["detected_keywords"].append(text)

        # If we found retail price indicators, extract the chart
        if price_related_text:
            try:
                # Convert plot area to pixels
                zoom = 3.0  # High resolution
                mat = fitz.Matrix(zoom, zoom)
                
                # Find the most relevant text indicator
                main_indicator = price_related_text[0]
                for indicator in price_related_text:
                    if indicator['confidence'] > main_indicator['confidence']:
                        main_indicator = indicator
                
                # Create rectangle around the text with room for the chart
                # (typically charts appear below their titles/labels)
                text_rect = fitz.Rect(main_indicator['rect'])
                
                # Create a capture rectangle extending below the text to capture the chart
                capture_rect = fitz.Rect(
                    0,  # Start from left edge of page
                    max(0, text_rect.y0 - 20),  # Extend slightly above the text
                    page.rect.width,  # Full page width
                    min(page.rect.height, text_rect.y0 + 350)  # Extend below the text
                )
                
                # Extract that specific area
                pix = page.get_pixmap(matrix=mat, clip=capture_rect)

                # Save the image
                plot_img_path = os.path.join(output_dir, f"{pdf_name}_retail_price_plot.png")
                pix.save(plot_img_path)
                print(f"Saved Retail Selling Price chart to {plot_img_path}")

                # Record results
                retail_price_results["plots_found"].append({
                    "page": page_index,
                    "image_path": plot_img_path,
                    "indicator_text": main_indicator['text']
                })
                
                # Mark that we found a plot in this PDF
                found_plot = True
                
                # We found what we needed, no need to check other pages
                break
                
            except Exception as e:
                error_msg = f"Error extracting plot: {str(e)}"
                print(error_msg)
                error_details["error"] = error_msg
        else:
            print(f"Page {page_index}: No Retail Selling Price chart detected")

    # If we couldn't find any retail price plot, try harder with fallback method
    if not found_plot:
        # Try a fallback method - get any page with text mentions of price
        for page_num, page in enumerate(doc):
            page_index = page_num + 1
            
            # Look for price-related text in the page
            text = page.get_text().lower()
            if any(indicator.lower() in text for indicator in retail_price_indicators):
                try:
                    print(f"Fallback: Found price-related text on page {page_index}, capturing entire page")
                    
                    # Capture the entire page as a last resort
                    zoom = 2.0  # Still decent resolution
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Save the image
                    plot_img_path = os.path.join(output_dir, f"{pdf_name}_retail_price_plot_fallback.png")
                    pix.save(plot_img_path)
                    print(f"Saved fallback capture to {plot_img_path}")
                    
                    # Record results
                    retail_price_results["plots_found"].append({
                        "page": page_index,
                        "image_path": plot_img_path,
                        "indicator_text": "Fallback capture - Price mention found",
                        "is_fallback": True
                    })
                    
                    # Mark that we found a plot (though it's a fallback)
                    found_plot = True
                    break
                except Exception as e:
                    error_msg = f"Error in fallback capture: {str(e)}"
                    print(error_msg)
                    error_details["error"] = error_msg

    # Check if we need to write to error log
    if not found_plot and error_log_path:
        # Ensure the directory for the error log exists
        os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
        
        # Check if the file exists to determine if we need to write headers
        file_exists = os.path.isfile(error_log_path)
        
        with open(error_log_path, 'a', newline='') as csvfile:
            fieldnames = ['pdf_name', 'pdf_path', 'timestamp', 'error', 'pages_checked', 'detected_keywords']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            # Convert list to string for CSV
            error_details['detected_keywords'] = ';'.join(error_details['detected_keywords'])
            writer.writerow(error_details)
        
        print(f"Error details logged to {error_log_path}")

    if not retail_price_results["plots_found"]:
        print(f"\nWARNING: No Retail Selling Price charts found in {pdf_name}.")
    else:
        # Generate HTML report
        html_path = os.path.join(output_dir, f"{pdf_name}_retail_price_report.html")
        generate_html_report(retail_price_results, html_path)
        print(f"\nAnalysis complete! Found {len(retail_price_results['plots_found'])} retail price plots.")
        print(f"Results saved to {output_dir}")
        print(f"HTML report saved to {html_path}")

    doc.close()
    return retail_price_results, found_plot

def generate_html_report(results, html_path):
    """Generate an HTML report for the retail price plots"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Retail Price Chart Extraction Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .plot-section {{ margin-bottom: 40px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }}
            .plot-image {{ margin-bottom: 20px; }}
            .plot-image img {{ max-width: 100%; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>Retail Price Chart Extraction Report</h1>
        <h2>PDF: {results["pdf_name"]}</h2>
        <p>Plots found: {len(results["plots_found"])}</p>
        
        <div id="plots">
    """
    
    # Add each plot to the report
    for i, plot in enumerate(results["plots_found"]):
        img_filename = os.path.basename(plot["image_path"])
        
        html += f"""
        <div class="plot-section">
            <h3>Retail Price Chart - Page {plot["page"]}</h3>
            <p>Indicator text: <strong>{plot.get("indicator_text", "Unknown")}</strong></p>
            
            <div class="plot-image">
                <img src="{img_filename}" alt="Retail Price Chart">
            </div>
        </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    with open(html_path, "w") as f:
        f.write(html)

def generate_combined_html_report(output_dir, pdf_paths):
    """Generate a combined HTML report showing all successfully extracted charts"""
    
    # Collect all the extracted charts
    chart_images = []
    for pdf_path in pdf_paths:
        pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
        
        # Check for regular and fallback images
        regular_img = os.path.join(output_dir, f"{pdf_name}_retail_price_plot.png")
        fallback_img = os.path.join(output_dir, f"{pdf_name}_retail_price_plot_fallback.png")
        
        if os.path.exists(regular_img):
            chart_images.append({
                'pdf_name': pdf_name,
                'image_path': regular_img,
                'is_fallback': False
            })
        elif os.path.exists(fallback_img):
            chart_images.append({
                'pdf_name': pdf_name,
                'image_path': fallback_img,
                'is_fallback': True
            })
    
    # Generate the HTML
    html_path = os.path.join(output_dir, "all_charts_report.html")
    
    with open(html_path, 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>All Retail Price Charts</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2, h3 { color: #333; }
                .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }
                .chart-card { border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
                .chart-card img { width: 100%; height: auto; border: 1px solid #eee; }
                .chart-card h3 { margin-top: 0; }
                .fallback { background-color: #fff3cd; }
                .chart-info { margin-bottom: 10px; }
                header { margin-bottom: 30px; }
            </style>
        </head>
        <body>
            <header>
                <h1>Combined Retail Price Charts Report</h1>
                <p>Generated on """ + datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + """</p>
            </header>
            
            <h2>Charts Extracted: """ + str(len(chart_images)) + """ out of """ + str(len(pdf_paths)) + """</h2>
            
            <div class="chart-grid">
        """)
        
        # Add each chart
        for chart in chart_images:
            card_class = "chart-card fallback" if chart['is_fallback'] else "chart-card"
            tag = " (Fallback)" if chart['is_fallback'] else ""
            
            f.write(f"""
            <div class="{card_class}">
                <h3>{chart['pdf_name']}{tag}</h3>
                <div class="chart-info">
                    <p>PDF: {chart['pdf_name']}</p>
                </div>
                <img src="{os.path.basename(chart['image_path'])}" alt="Chart from {chart['pdf_name']}">
            </div>
            """)
        
        f.write("""
            </div>
        </body>
        </html>
        """)

def process_all_pdfs_for_retail_price_charts(pdf_folder, output_dir=None, error_log_path=None):
    """Process all PDFs in a folder to extract retail price charts"""
    if output_dir is None:
        output_dir = os.path.join(r"C:\Users\clint\Desktop\Lifecycle Code\Sandbox", "all_retail_price_charts")
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files in {pdf_folder}")
    
    successful = 0
    failed = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        
        print(f"\n\nProcessing {pdf_file}...")
        results, found_plot = extract_retail_price_plots(
            pdf_path, 
            output_dir=output_dir, 
            relaxed_detection=True, 
            error_log_path=error_log_path
        )
        
        if found_plot:
            successful += 1
        else:
            failed.append(pdf_name)
    
    # Create summary report
    summary_path = os.path.join(output_dir, "extraction_summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"Retail Price Chart Extraction Summary\n")
        f.write(f"===================================\n\n")
        f.write(f"Total PDFs processed: {len(pdf_files)}\n")
        f.write(f"Successfully extracted charts: {successful}\n")
        f.write(f"Failed extractions: {len(failed)}\n\n")
        
        if failed:
            f.write("Failed PDFs:\n")
            for pdf in failed:
                f.write(f"- {pdf}\n")
    
    print(f"\nAll PDFs processed.")
    print(f"Successfully extracted retail price charts from {successful} out of {len(pdf_files)} PDFs.")
    
    if failed:
        print(f"Failed to extract charts from {len(failed)} PDFs.")
        if error_log_path:
            print(f"See {error_log_path} for detailed error information.")
    
    return successful, failed

# If run directly, process one PDF or all PDFs in the folder
if __name__ == "__main__":
    # Process specific May PDFs as requested
    pdf_files = [
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\05_2018.pdf",
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\05_2019.pdf",
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\05_2020.pdf",
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\05_2021.pdf",
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\05_2022.pdf",
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\05_2023.pdf",
        r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\5_2024.pdf",
    ]
    
    # Create a specific output directory for these files
    may_output_dir = os.path.join(r"C:\Users\clint\Desktop\Lifecycle Code\Sandbox", "may_retail_price_charts")
    os.makedirs(may_output_dir, exist_ok=True)
    
    # Create error log CSV file
    error_log_path = os.path.join(may_output_dir, "extraction_errors.csv")
    
    # Ensure error log directory exists
    os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
    
    # Initialize error log if it doesn't exist
    if not os.path.isfile(error_log_path):
        with open(error_log_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['pdf_name', 'pdf_path', 'timestamp', 'error', 'pages_checked', 'detected_keywords'])
            writer.writeheader()
    
    print(f"Processing {len(pdf_files)} PDFs...")
    
    successful = 0
    failed = []
    
    for pdf_path in pdf_files:
        pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
        print(f"\nProcessing {pdf_name}...")
        
        # Check if the file exists before attempting to process it
        if not os.path.exists(pdf_path):
            print(f"ERROR: File {pdf_path} does not exist")
            
            # Log the error
            with open(error_log_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['pdf_name', 'pdf_path', 'timestamp', 'error', 'pages_checked', 'detected_keywords'])
                writer.writerow({
                    'pdf_name': pdf_name,
                    'pdf_path': pdf_path,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'error': 'File does not exist',
                    'pages_checked': 0,
                    'detected_keywords': ''
                })
            
            failed.append(pdf_name)
            continue
        
        try:
            # Pass the error log path
            results, found_plot = extract_retail_price_plots(
                pdf_path, 
                output_dir=may_output_dir,
                error_log_path=error_log_path
            )
            
            if found_plot:
                successful += 1
            else:
                failed.append(pdf_name)
                
        except Exception as e:
            print(f"ERROR: Failed to process {pdf_name}: {str(e)}")
            
            # Log the error
            with open(error_log_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['pdf_name', 'pdf_path', 'timestamp', 'error', 'pages_checked', 'detected_keywords'])
                writer.writerow({
                    'pdf_name': pdf_name,
                    'pdf_path': pdf_path,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'error': f'Exception: {str(e)}',
                    'pages_checked': 0,
                    'detected_keywords': ''
                })
            
            failed.append(pdf_name)
    
    # Create summary report
    summary_path = os.path.join(may_output_dir, "may_extraction_summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"May Retail Price Chart Extraction Summary\n")
        f.write(f"=====================================\n\n")
        f.write(f"Total PDFs processed: {len(pdf_files)}\n")
        f.write(f"Successfully extracted charts: {successful}\n")
        f.write(f"Failed extractions: {len(failed)}\n\n")
        
        if failed:
            f.write("Failed PDFs:\n")
            for pdf in failed:
                f.write(f"- {pdf}\n")
    
    print(f"\nAll PDFs processed.")
    print(f"Successfully extracted retail price charts from {successful} out of {len(pdf_files)} PDFs.")
    
    if failed:
        print(f"Failed to extract charts from {len(failed)} PDFs.")
        print(f"See {error_log_path} for detailed error information.")
    
    print(f"Summary report created at {summary_path}")
    
    # Also generate a combined HTML report showing all charts
    generate_combined_html_report(may_output_dir, pdf_files)
    print(f"Combined HTML report created at {os.path.join(may_output_dir, 'all_charts_report.html')}")