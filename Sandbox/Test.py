import fitz  # PyMuPDF
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import cv2
import shutil

def analyze_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        print(f"\n--- Page {page_num + 1} ---")

        # Extract and count images
        image_list = page.get_images(full=True)
        if image_list:
            print(f"🖼️ Found {len(image_list)} embedded image(s)")
        else:
            print("🖼️ No embedded images")

        # Extract and count vector drawings
        drawings = page.get_drawings()
        if drawings:
            print(f"📈 Found {len(drawings)} vector drawing object(s)")
            print("Vector Drawing Details:")
            for i, draw in enumerate(drawings):
                print(f"  Drawing {i+1}:")
                print(f"    Type: {draw['type']}")
                if draw['type'] == "l":  # Line
                    print(f"    Line from {draw['items'][0][:2]} to {draw['items'][0][2:4]}")
                elif draw['type'] == "c":  # Curve
                    print(f"    Curve with {len(draw['items'])} control points")
                elif draw['type'] == "r":  # Rectangle
                    print(f"    Rectangle at {draw['rect']}")
                print(f"    Color: {draw.get('color', 'N/A')}")
                print(f"    Stroke width: {draw.get('width', 'N/A')}")
                if i >= 9:  # Limit to first 10 drawings to avoid overwhelming output
                    print(f"    ... {len(drawings) - 10} more drawings (showing first 10 only)")
                    break
        else:
            print("📈 No vector drawings")

        # Detect potential tables: rectangles + text blocks
        blocks = page.get_text("dict")["blocks"]
        table_like = False
        for b in blocks:
            if b["type"] == 0 and len(b.get("lines", [])) > 1:
                # multiple lines of text, possibly a table
                table_like = True
        if table_like:
            print("📋 Possible table detected (text + structure)")
        else:
            print("📋 No table-like structures detected")
    
    doc.close()

# Helper function to make objects JSON serializable
def make_serializable(obj):
    """Convert non-serializable objects to serializable ones"""
    if isinstance(obj, (tuple, list)):
        return [make_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):  # Handle custom objects
        return {key: make_serializable(val) for key, val in obj.__dict__.items()}
    elif hasattr(obj, 'x') and hasattr(obj, 'y'):  # Handle Point-like objects
        return {'x': obj.x, 'y': obj.y}
    else:
        # Try to convert to a basic type
        try:
            return float(obj)
        except (TypeError, ValueError):
            try:
                return str(obj)
            except:
                return "UNSERIALIZABLE"

# New function to visualize and save vector drawings as images - with better visualization
def visualize_vector_drawings(pdf_path, output_dir=None):
    """Extract vector drawings from PDF pages and save as images"""
    # Use the Sandbox directory
    if output_dir is None:
        output_dir = os.path.join(r"C:\Users\clint\Desktop\Lifecycle Code\Sandbox", "vector_drawings_images")
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"Creating output directory: {output_dir}")
    
    doc = fitz.open(pdf_path)
    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
    
    for page_num, page in enumerate(doc):
        page_index = page_num + 1
        
        # Get the page dimensions
        page_rect = page.rect
        width, height = int(page_rect.width), int(page_rect.height)
        
        # Extract full page as image with high zoom factor 
        zoom_factor = 3.0  # Higher zoom for better quality
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        
        # ------- EXTRACT VECTOR DRAWINGS VISUALLY -------
        # Method 1: Save full page (with text and images)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        full_img_path = os.path.join(output_dir, f"{pdf_name}_page_{page_index}_full.png")
        pix.save(full_img_path)
        
        # Method 2: Create a version of the page with only vectors visible (no text)
        # We'll create this by manipulating the rendered page
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_np = np.array(img)
        
        # Create directory for vector visualizations
        vectors_dir = os.path.join(output_dir, f"{pdf_name}_page_{page_index}_vectors")
        os.makedirs(vectors_dir, exist_ok=True)
        
        # Save full page for reference
        cv2.imwrite(os.path.join(vectors_dir, "full_page.png"), cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
        
        # Extract drawings for analysis
        drawings = page.get_drawings()
        
        if drawings:
            # Create separate images for different drawing types with real visual representation
            strokes_img = img_np.copy()
            fills_img = img_np.copy()
            all_vectors_img = img_np.copy()
            
            # Create a mask that will isolate vector elements
            # We'll use this for edge detection to visualize vector content
            stroke_mask = np.zeros(img_np.shape[:2], dtype=np.uint8)
            
            # Track drawings by type
            stroke_widths = []
            colors = []
            drawing_types = []
            
            # Process each vector drawing element
            for i, drawing in enumerate(drawings):
                draw_type = drawing['type']
                drawing_types.append(draw_type)
                
                # Extract color and width data for analysis
                if 'width' in drawing and drawing['width'] is not None:
                    stroke_widths.append(drawing['width'])
                if 'color' in drawing and drawing['color'] is not None:
                    colors.append(drawing['color'])
                
                # Extract bounding rectangle for region of interest if available
                bbox = None
                if 'rect' in drawing:
                    r = drawing['rect']
                    # Scale rectangle by zoom factor
                    x0, y0, x1, y1 = int(r[0] * zoom_factor), int(r[1] * zoom_factor), int(r[2] * zoom_factor), int(r[3] * zoom_factor)
                    bbox = (x0, y0, x1, y1)
                    
                    # Add the drawing area to our mask
                    cv2.rectangle(stroke_mask, (x0, y0), (x1, y1), 255, -1)  # Fill the area
                
                # Extract drawing based on type for individual display
                if draw_type == 's' and 'items' in drawing and drawing['items']:
                    # For strokes, create an image showing just this stroke
                    try:
                        if bbox:
                            # Extract just this region plus some padding
                            padding = 10
                            x0, y0, x1, y1 = bbox
                            # Ensure boundaries are within image
                            x0 = max(0, x0 - padding)
                            y0 = max(0, y0 - padding)
                            x1 = min(img_np.shape[1], x1 + padding)
                            y1 = min(img_np.shape[0], y1 + padding)
                            
                            # Extract stroke ROI from image
                            stroke_roi = img_np[y0:y1, x0:x1].copy()
                            
                            # Save the individual stroke image
                            stroke_img_path = os.path.join(vectors_dir, f"stroke_{i+1}.png")
                            cv2.imwrite(stroke_img_path, cv2.cvtColor(stroke_roi, cv2.COLOR_RGB2BGR))
                            
                            # Draw a highlight box on the strokes image to show where it is
                            color = (0, 0, 255)  # Red in BGR
                            if 'color' in drawing and drawing['color']:
                                # Use the drawing's color (RGB to BGR)
                                r, g, b = [int(c * 255) for c in drawing['color']]
                                color = (b, g, r)  # BGR for OpenCV
                                
                            cv2.rectangle(strokes_img, (x0, y0), (x1, y1), color, 2)
                    except Exception as e:
                        print(f"Error processing stroke {i+1}: {str(e)}")
                
                elif draw_type == 'f' and bbox:
                    # For fill areas, highlight and extract the region
                    try:
                        # Extract ROI with padding
                        padding = 10
                        x0, y0, x1, y1 = bbox
                        # Ensure boundaries are within image
                        x0 = max(0, x0 - padding)
                        y0 = max(0, y0 - padding)
                        x1 = min(img_np.shape[1], x1 + padding)
                        y1 = min(img_np.shape[0], y1 + padding)
                        
                        fill_roi = img_np[y0:y1, x0:x1].copy()
                        
                        # Save the individual fill image
                        fill_img_path = os.path.join(vectors_dir, f"fill_{i+1}.png")
                        cv2.imwrite(fill_img_path, cv2.cvtColor(fill_roi, cv2.COLOR_RGB2BGR))
                        
                        # Highlight the fill area in the fills image
                        cv2.rectangle(fills_img, (x0, y0), (x1, y1), (0, 255, 0), 2)  # Green in BGR
                    except Exception as e:
                        print(f"Error processing fill {i+1}: {str(e)}")
            
            # Save the main vector visualization images
            cv2.imwrite(os.path.join(vectors_dir, "strokes_highlighted.png"), cv2.cvtColor(strokes_img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(os.path.join(vectors_dir, "fills_highlighted.png"), cv2.cvtColor(fills_img, cv2.COLOR_RGB2BGR))
            
            # Apply edge detection to the image to highlight vector elements
            # Mask the image to focus on areas with vectors
            masked_img = img_np.copy()
            for c in range(3):  # Apply to each color channel
                masked_img[:,:,c] = cv2.bitwise_and(masked_img[:,:,c], stroke_mask)
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(masked_img, cv2.COLOR_RGB2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges for better visibility
            kernel = np.ones((2, 2), np.uint8)
            edges_dilated = cv2.dilate(edges, kernel, iterations=1)
            
            # Create colored edges on black background
            edges_color = np.zeros_like(img_np)
            edges_color[edges_dilated > 0] = [0, 255, 0]  # Green edges
            
            # Save edge-detected vector image
            cv2.imwrite(os.path.join(vectors_dir, "vector_edges.png"), edges_color)
            
            # Create a composite image showing vectors on original
            alpha = 0.7
            composite = cv2.addWeighted(img_np, 1, edges_color, alpha, 0)
            cv2.imwrite(os.path.join(vectors_dir, "vector_overlay.png"), cv2.cvtColor(composite, cv2.COLOR_RGB2BGR))
            
            # Create a statistics visualization for types of drawings
            try:
                plt.figure(figsize=(12, 6))
                
                plt.subplot(1, 2, 1)
                type_counts = {}
                for t in drawing_types:
                    if t not in type_counts:
                        type_counts[t] = 0
                    type_counts[t] += 1
                plt.bar(type_counts.keys(), type_counts.values())
                plt.title(f"Drawing Types (Page {page_index})")
                plt.xlabel("Type")
                plt.ylabel("Count")
                
                if stroke_widths:
                    plt.subplot(1, 2, 2)
                    plt.hist(stroke_widths, bins=10)
                    plt.title(f"Stroke Widths (Page {page_index})")
                    plt.xlabel("Width")
                    plt.ylabel("Frequency")
                
                stats_path = os.path.join(vectors_dir, "statistics.png")
                plt.tight_layout()
                plt.savefig(stats_path)
                plt.close()
            except Exception as e:
                print(f"Error creating statistics: {str(e)}")
            
            # Create an HTML report for better visualization
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Vector Drawings - {pdf_name} Page {page_index}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .image-container {{ margin: 20px 0; }}
                    .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
                    .gallery {{ display: flex; flex-wrap: wrap; gap: 10px; }}
                    .gallery img {{ max-width: 200px; max-height: 200px; object-fit: contain; }}
                    .description {{ margin-bottom: 10px; color: #666; }}
                </style>
            </head>
            <body>
                <h1>Vector Drawings Analysis - {pdf_name}</h1>
                <h2>Page {page_index}</h2>
                
                <div class="image-container">
                    <h3>Full Page</h3>
                    <img src="full_page.png" alt="Full Page">
                </div>
                
                <div class="image-container">
                    <h3>Vector Elements (Edge Detection)</h3>
                    <p class="description">Green highlights show detected vector elements</p>
                    <img src="vector_overlay.png" alt="Vector Overlay">
                </div>
                
                <div class="image-container">
                    <h3>Vector Edges Only</h3>
                    <img src="vector_edges.png" alt="Vector Edges">
                </div>
                
                <div class="image-container">
                    <h3>Strokes Highlighted</h3>
                    <img src="strokes_highlighted.png" alt="Strokes Highlighted">
                </div>
                
                <div class="image-container">
                    <h3>Fills Highlighted</h3>
                    <img src="fills_highlighted.png" alt="Fills Highlighted">
                </div>
                
                <div class="image-container">
                    <h3>Statistics</h3>
                    <img src="statistics.png" alt="Statistics">
                </div>
                
                <h3>Individual Stroke Elements</h3>
                <div class="gallery">
            """
            
            # Add individual stroke images to the gallery
            stroke_files = [f for f in os.listdir(vectors_dir) if f.startswith("stroke_")]
            for stroke_file in stroke_files:
                html_content += f'    <img src="{stroke_file}" alt="{stroke_file}">\n'
            
            html_content += """
                </div>
                
                <h3>Individual Fill Elements</h3>
                <div class="gallery">
            """
            
            # Add individual fill images to the gallery
            fill_files = [f for f in os.listdir(vectors_dir) if f.startswith("fill_")]
            for fill_file in fill_files:
                html_content += f'    <img src="{fill_file}" alt="{fill_file}">\n'
            
            html_content += """
                </div>
            </body>
            </html>
            """
            
            # Save the HTML report
            html_path = os.path.join(vectors_dir, "report.html")
            with open(html_path, "w") as f:
                f.write(html_content)
            
            # Create a simpler HTML file in the main directory for easy navigation
            index_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Vector Drawings - {pdf_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    ul {{ list-style-type: none; padding: 0; }}
                    li {{ margin: 10px 0; }}
                    a {{ color: #0066cc; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>Vector Drawings - {pdf_name}</h1>
                <p>Click on a page to view its vector drawings:</p>
                <ul>
            """
            
    # Create main index HTML in the output directory
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Vector Drawings</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>PDF Vector Drawings</h1>
        <p>Click on a page to view its vector drawings:</p>
        <ul>
    """
    
    for page_num in range(doc.page_count):
        page_index = page_num + 1
        vectors_dir = os.path.join(output_dir, f"{pdf_name}_page_{page_index}_vectors")
        if os.path.exists(vectors_dir) and os.path.exists(os.path.join(vectors_dir, "report.html")):
            index_html += f'    <li><a href="{pdf_name}_page_{page_index}_vectors/report.html">Page {page_index}</a></li>\n'
    
    index_html += """
        </ul>
    </body>
    </html>
    """
    
    # Save the index HTML file
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w") as f:
        f.write(index_html)
    
    print(f"Created HTML reports for vector drawings. Open {index_path} to view.")
    
    doc.close()
    return output_dir

# Function to process vector drawings in batch for multiple PDFs
def process_pdfs_batch(pdf_folder, output_dir=None):
    """Process multiple PDFs for vector drawings visualization"""
    if output_dir is None:
        output_dir = os.path.join(r"C:\Users\clint\Desktop\Lifecycle Code\Sandbox", "vector_drawings_batch")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files in the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files in {pdf_folder}")
    
    # Create main index HTML
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vector Drawings - Batch Processing</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Vector Drawings - Batch Processing</h1>
        <p>Select a PDF to view its vector drawings:</p>
        <ul>
    """
    
    # Process each PDF and add to index
    for pdf_file in pdf_files[:5]:  # Limit to 5 files during development
        pdf_path = os.path.join(pdf_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        
        # Create a directory for this PDF
        pdf_output_dir = os.path.join(output_dir, pdf_name)
        os.makedirs(pdf_output_dir, exist_ok=True)
        
        # Process the PDF
        visualize_vector_drawings(pdf_path, output_dir=pdf_output_dir)
        
        # Add to index
        index_html += f'    <li><a href="{pdf_name}/index.html">{pdf_name}</a></li>\n'
    
    index_html += """
        </ul>
    </body>
    </html>
    """
    
    # Save the main index HTML
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(index_html)
    
    return output_dir

# 🔧 Run the functions
pdf_path = r"C:\Users\clint\Desktop\Lifecycle Code\data\raw_pdfs\01_2019.pdf"  # Specified PDF path

# Extract and save vector drawings with better visualization
output_dir = visualize_vector_drawings(pdf_path)

print(f"\nAll extracted vector drawings are saved in: {output_dir}")
print(f"Open {os.path.join(output_dir, 'index.html')} in a web browser to view the reports.")