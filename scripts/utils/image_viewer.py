import os
import re
import tkinter as tk
from tkinter import Button, Label, Entry, Frame, Scrollbar
from PIL import Image, ImageTk

def extract_date(filename):
    # Extract month and year from filename pattern
    match = re.search(r'(\d+)_(\d{4})', filename)
    if match:
        month, year = match.groups()
        # Ensure month is two digits for proper sorting
        month = month.zfill(2)
        return f"{year}_{month}"
    return filename

def view_images():
    folder_path = r"C:\Users\clint\Desktop\Lifecycle Code\data\extracted_images"
    
    # Get all image files and sort them chronologically
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=extract_date)
    
    if not image_files:
        print("No images found in the folder.")
        return
    
    # Grid dimensions
    grid_rows, grid_cols = 2, 4
    grid_size = grid_rows * grid_cols
    
    # Page control
    current_page = [0]  # Using list to make it mutable in nested functions
    total_pages = (len(image_files) + grid_size - 1) // grid_size  # Ceiling division
    
    root = tk.Tk()
    root.title("Chronological Image Grid Viewer")
    root.geometry("1600x800")  # Adjusted for 2x4 layout
    
    # Main frame with scrollbar
    main_frame = Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Canvas for scrolling
    canvas = tk.Canvas(main_frame)
    scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Add search frame for year and month entry
    search_frame = Frame(root)
    search_frame.pack(pady=5)
    
    # Year entry
    Label(search_frame, text="Year:").pack(side=tk.LEFT, padx=5)
    year_entry = Entry(search_frame, width=6)
    year_entry.pack(side=tk.LEFT, padx=5)
    
    # Month entry
    Label(search_frame, text="Month:").pack(side=tk.LEFT, padx=5)
    month_entry = Entry(search_frame, width=4)
    month_entry.pack(side=tk.LEFT, padx=5)
    
    # Search button
    def search_by_date():
        year = year_entry.get().strip()
        month = month_entry.get().strip()
        
        if not year and not month:
            return
        
        # Find matching index
        for i, filename in enumerate(image_files):
            search_pattern = f"{month}_" if month else ""
            search_pattern += f"{year}" if year else ""
            
            if search_pattern in filename:
                page = i // grid_size
                show_page(page)
                break
    
    Button(search_frame, text="Search", command=search_by_date).pack(side=tk.LEFT, padx=10)
    
    # Image grid frames (2x4)
    image_frames = []
    image_labels = []
    filename_labels = []
    
    for r in range(grid_rows):
        row_frame = Frame(scrollable_frame)
        row_frame.pack(pady=10)  # Increased padding
        
        for c in range(grid_cols):
            frame = Frame(row_frame, borderwidth=1, relief="solid")
            frame.pack(side=tk.LEFT, padx=10)  # Increased padding
            
            # Image label with larger size
            img_label = Label(frame)
            img_label.pack(padx=10, pady=10)  # Increased padding
            image_labels.append(img_label)
            
            # Filename label with larger wraplength
            name_label = Label(frame, text="", wraplength=300, font=("Arial", 10))
            name_label.pack(padx=10, pady=10)
            filename_labels.append(name_label)
            
            image_frames.append(frame)
    
    # Navigation frame
    nav_frame = Frame(root)
    nav_frame.pack(pady=10)
    
    # Page counter label
    page_label = Label(nav_frame, text="")
    
    def show_page(page_num):
        if 0 <= page_num < total_pages:
            current_page[0] = page_num
            
            # Calculate start and end indices for the current page
            start_idx = page_num * grid_size
            end_idx = min(start_idx + grid_size, len(image_files))
            
            # Clear all image labels first
            for img_label in image_labels:
                img_label.config(image='')
                img_label.image = None
            
            for name_label in filename_labels:
                name_label.config(text='')
            
            # Load images for the current page
            for i in range(start_idx, end_idx):
                grid_idx = i - start_idx
                img_path = os.path.join(folder_path, image_files[i])
                
                try:
                    # Display the image
                    img = Image.open(img_path)
                    # Adjusted thumbnail size for 2x4 grid
                    img.thumbnail((350, 350))  # Slightly smaller to fit 4 columns
                    
                    photo = ImageTk.PhotoImage(img)
                    image_labels[grid_idx].config(image=photo)
                    image_labels[grid_idx].image = photo  # Keep a reference
                    
                    # Update filename display
                    filename_labels[grid_idx].config(text=image_files[i])
                except Exception as e:
                    filename_labels[grid_idx].config(text=f"Error: {e}")
            
            # Update page label
            page_label.config(text=f"Page {page_num + 1} of {total_pages}")
    
    def next_page():
        show_page(current_page[0] + 1)
    
    def prev_page():
        show_page(current_page[0] - 1)
    
    # Navigation buttons
    prev_btn = Button(nav_frame, text="Previous Page", command=prev_page)
    prev_btn.pack(side=tk.LEFT, padx=10)
    
    page_label.pack(side=tk.LEFT, padx=10)
    
    next_btn = Button(nav_frame, text="Next Page", command=next_page)
    next_btn.pack(side=tk.LEFT, padx=10)
    
    # Full image preview functionality
    preview_window = None
    
    def show_full_image(idx):
        nonlocal preview_window
        
        if preview_window is not None:
            preview_window.destroy()
        
        img_path = os.path.join(folder_path, image_files[idx])
        
        # Create new window
        preview_window = tk.Toplevel(root)
        preview_window.title(image_files[idx])
        
        # Display full image
        img = Image.open(img_path)
        
        # Resize if needed while maintaining aspect ratio
        screen_width = root.winfo_screenwidth() * 0.8
        screen_height = root.winfo_screenheight() * 0.8
        
        img_width, img_height = img.size
        scale = min(screen_width/img_width, screen_height/img_height)
        
        if scale < 1:  # Only resize if the image is larger than the screen
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        photo = ImageTk.PhotoImage(img)
        
        img_label = Label(preview_window, image=photo)
        img_label.image = photo  # Keep a reference
        img_label.pack(padx=10, pady=10)
        
        # Add close button
        Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
    
    # Bind click events to image labels
    for i in range(grid_size):
        image_labels[i].bind("<Button-1>", lambda e, idx=i: show_full_image(current_page[0] * grid_size + idx))
        # Make the cursor change to indicate it's clickable
        image_labels[i].config(cursor="hand2")
    
    # Show first page
    show_page(0)
    
    root.mainloop()

if __name__ == "__main__":
    view_images()