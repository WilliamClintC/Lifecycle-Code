import os
import cv2
import numpy as np
from tkinter import Tk, messagebox

class ImageCropper:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.output_folder = os.path.join(os.path.dirname(os.path.dirname(folder_path)), "cropped_sorted")
        self._ensure_output_folder_exists()
        self.image_files = self._get_image_files()
        self.current_index = 0
        self.current_image = None
        self.original_image = None
        self.display_image = None
        self.cropping = False
        self.x_start, self.y_start = -1, -1
        self.x_end, self.y_end = -1, -1
        self.crop_roi = None
        self.scale_factor = 1.0
        self.window_name = "Image Cropping Tool"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        # Display command instructions at startup
        self._print_instructions()
    
    def _ensure_output_folder_exists(self):
        """Create the output folder if it doesn't exist"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"Created output folder: {self.output_folder}")
        else:
            print(f"Output folder already exists: {self.output_folder}")
            
    def _get_image_files(self):
        """Get all image files from the specified folder."""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        return [f for f in os.listdir(self.folder_path) 
                if os.path.splitext(f)[1].lower() in valid_extensions]
    
    def _resize_image_for_display(self, image, max_width=1280, max_height=720):
        """Resize image to fit screen while maintaining aspect ratio."""
        height, width = image.shape[:2]
        
        # Calculate scale factor to fit within max dimensions
        width_scale = max_width / width if width > max_width else 1.0
        height_scale = max_height / height if height > max_height else 1.0
        
        # Use the smaller scale to ensure image fits within bounds
        self.scale_factor = min(width_scale, height_scale)
        
        if self.scale_factor < 1.0:
            # Only resize if necessary
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized
        
        self.scale_factor = 1.0
        return image.copy()
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for cropping."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.cropping = True
            self.x_start, self.y_start = x, y
            self.x_end, self.y_end = x, y
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.cropping:
                self.x_end, self.y_end = x, y
                # Create a copy of the display image to draw on
                self.current_image = self.display_image.copy()
                cv2.rectangle(self.current_image, (self.x_start, self.y_start), 
                              (self.x_end, self.y_end), (0, 255, 0), 2)
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.cropping = False
            self.x_end, self.y_end = x, y
            # Ensure coordinates are ordered correctly (top-left to bottom-right)
            x1, y1 = min(self.x_start, self.x_end), min(self.y_start, self.y_end)
            x2, y2 = max(self.x_start, self.x_end), max(self.y_start, self.y_end)
            
            # Save crop region and convert to original image coordinates
            if self.scale_factor != 1.0:
                # Convert display coordinates to original image coordinates
                x1_orig = int(x1 / self.scale_factor)
                y1_orig = int(y1 / self.scale_factor)
                x2_orig = int(x2 / self.scale_factor)
                y2_orig = int(y2 / self.scale_factor)
                self.crop_roi = (x1_orig, y1_orig, x2_orig, y2_orig)
            else:
                self.crop_roi = (x1, y1, x2, y2)
            
            # Draw final rectangle
            self.current_image = self.display_image.copy()
            cv2.rectangle(self.current_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    def _print_instructions(self):
        """Print command instructions to the console"""
        print("\n" + "="*50)
        print("IMAGE CROPPING TOOL - COMMANDS")
        print("="*50)
        print("c: Crop the selected region and save")
        print("n: Skip to next image without cropping")
        print("r: Reset crop selection for current image")
        print("q: Quit the application")
        print("Click and drag with mouse to select crop region")
        print("="*50 + "\n")
    
    def run(self):
        """Main loop to process all images."""
        if not self.image_files:
            print("No images found in the specified directory.")
            return
        
        while self.current_index < len(self.image_files):
            image_path = os.path.join(self.folder_path, self.image_files[self.current_index])
            print(f"\nProcessing: {image_path} ({self.current_index + 1}/{len(self.image_files)})")
            
            # Load the image
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                print(f"Error loading image: {image_path}")
                self.current_index += 1
                continue
            
            # Resize for display
            self.display_image = self._resize_image_for_display(self.original_image)
            self.current_image = self.display_image.copy()
            self.crop_roi = None
            
            # Print information about the image and scaling
            orig_h, orig_w = self.original_image.shape[:2]
            disp_h, disp_w = self.display_image.shape[:2]
            print(f"Original size: {orig_w}x{orig_h}, Display size: {disp_w}x{disp_h}, Scale: {self.scale_factor:.2f}")
            
            # Set window title to include current image info
            window_title = f"{self.window_name} - {self.image_files[self.current_index]} ({self.current_index + 1}/{len(self.image_files)})"
            cv2.setWindowTitle(self.window_name, window_title)
            
            # Resize window to fit the image
            cv2.resizeWindow(self.window_name, disp_w, disp_h)
            
            while True:
                # Display the image without any overlays
                cv2.imshow(self.window_name, self.current_image)
                
                # Wait for key press
                key = cv2.waitKey(1) & 0xFF
                
                # 'n' - Next image without cropping
                if key == ord('n'):
                    print("Skipping to next image")
                    self.current_index += 1
                    break
                
                # 'c' - Crop the image if a region is selected
                elif key == ord('c') and self.crop_roi is not None:
                    x1, y1, x2, y2 = self.crop_roi
                    cropped_img = self.original_image[y1:y2, x1:x2]
                    
                    # Generate output path in the dedicated folder
                    filename, ext = os.path.splitext(self.image_files[self.current_index])
                    output_path = os.path.join(self.output_folder, f"{filename}_cropped{ext}")
                    
                    # Save the cropped image
                    cv2.imwrite(output_path, cropped_img)
                    print(f"Saved cropped image to: {output_path}")
                    
                    self.current_index += 1
                    break
                
                # 'r' - Reset cropping for current image
                elif key == ord('r'):
                    print("Resetting crop selection")
                    self.current_image = self.display_image.copy()
                    self.crop_roi = None
                
                # 'i' - Show instructions again
                elif key == ord('i'):
                    self._print_instructions()
                
                # 'q' - Quit the application
                elif key == ord('q'):
                    print("Quitting application")
                    return
        
        print("Finished processing all images.")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Path to the folder containing images
    image_folder = r"C:\Users\clint\Desktop\Lifecycle_RA\Data\Processed\Sorted_Images"
    
    # Check if the folder exists
    if not os.path.exists(image_folder):
        root = Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", f"Folder not found: {image_folder}")
        root.destroy()
    else:
        cropper = ImageCropper(image_folder)
        cropper.run()
