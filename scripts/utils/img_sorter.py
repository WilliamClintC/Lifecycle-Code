import os
import shutil
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Define source and destination directories
source_dir = r"C:\Users\clint\Desktop\Lifecycle_RA\Images"
dest_dir = r"C:\Users\clint\Desktop\Lifecycle_RA\Sorted_Images"

# Create destination directory if it doesn't exist
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Get list of image files
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
image_files = []

for file in os.listdir(source_dir):
    if any(file.lower().endswith(ext) for ext in image_extensions):
        image_files.append(file)

if not image_files:
    print("No image files found in the source directory.")
    exit()

# Create GUI
class ImageSorterApp:
    def __init__(self, root, image_files):
        self.root = root
        self.root.title("Image Sorter")
        self.image_files = image_files
        self.current_index = 0
        
        # Set up the GUI components
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(pady=10)
        
        self.keep_button = tk.Button(self.button_frame, text="Keep (Y)", command=self.keep_image)
        self.keep_button.pack(side=tk.LEFT, padx=5)
        
        self.discard_button = tk.Button(self.button_frame, text="Discard (N)", command=self.next_image)
        self.discard_button.pack(side=tk.LEFT, padx=5)
        
        self.filename_label = tk.Label(self.frame, text="")
        self.filename_label.pack(pady=2)
        
        self.progress_label = tk.Label(self.frame, text=f"Image 1 of {len(image_files)}")
        self.progress_label.pack(pady=5)
        
        # Bind keyboard shortcuts
        self.root.bind('<y>', lambda e: self.keep_image())
        self.root.bind('<n>', lambda e: self.next_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<Left>', lambda e: self.prev_image())
        
        # Set window size
        self.root.geometry("900x700")
        
        # Display the first image
        self.display_current_image()
    
    def display_current_image(self):
        if 0 <= self.current_index < len(self.image_files):
            # Get current image file
            img_path = os.path.join(source_dir, self.image_files[self.current_index])
            self.filename_label.config(text=self.image_files[self.current_index])
            
            try:
                # Open and resize image to fit the canvas
                img = Image.open(img_path)
                
                # Resize while maintaining aspect ratio
                max_width = 800
                max_height = 600
                width, height = img.size
                
                # Calculate new dimensions
                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Update canvas size
                self.canvas.config(width=img.width, height=img.height)
                
                # Display image
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                
                # Update progress label
                self.progress_label.config(text=f"Image {self.current_index + 1} of {len(self.image_files)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {self.image_files[self.current_index]}\nError: {str(e)}")
                self.next_image()
        else:
            self.show_completion()
    
    def keep_image(self):
        if 0 <= self.current_index < len(self.image_files):
            # Get source and destination paths
            source_path = os.path.join(source_dir, self.image_files[self.current_index])
            dest_path = os.path.join(dest_dir, self.image_files[self.current_index])
            
            # Copy file to destination directory
            try:
                shutil.copy2(source_path, dest_path)
                print(f"Kept: {self.image_files[self.current_index]}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy file: {str(e)}")
            
            # Move to next image
            self.next_image()
    
    def next_image(self):
        self.current_index += 1
        if self.current_index < len(self.image_files):
            self.display_current_image()
        else:
            self.show_completion()
    
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
    
    def show_completion(self):
        messagebox.showinfo("Sorting Complete", "All images have been processed!")
        self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSorterApp(root, image_files)
    root.mainloop()