import sys
import importlib.util
import random

print("Checking for Tkinter availability...")
if importlib.util.find_spec("tkinter") is None:
    print("Warning: Tkinter is not installed or supported in this environment. Some features may not work.")
else:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    import cv2
    from PIL import Image, ImageTk
    import numpy as np

    class ImageEditor:
        def __init__(self, root):
            print("Initializing ImageEditor...")
            self.root = root
            self.root.title("SYD 13")

            self.image = None
            self.original_image = None
            self.selection = None
            self.quality_factor = 100
            self.history = []  # Stack for undo
            self.redo_stack = []  # Stack for redo
            self.usage_count = 0  # Track user interactions

            self.canvas = tk.Canvas(root, width=500, height=400, bg="gray")
            self.canvas.pack()

            self.canvas.bind("<ButtonPress-1>", self.start_selection)
            self.canvas.bind("<B1-Motion>", self.draw_selection)
            self.canvas.bind("<ButtonRelease-1>", self.apply_crop)
            
            self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
            self.load_button.pack()
            
            self.save_button = tk.Button(root, text="Save Image", command=self.save_image)
            self.save_button.pack()
            
            self.slider = tk.Scale(root, from_=100, to=10, orient="horizontal", label="Quality", command=self.degrade_quality)
            self.slider.pack()
            
            self.undo_button = tk.Button(root, text="Undo", command=self.undo)
            self.undo_button.pack()
            
            self.redo_button = tk.Button(root, text="Redo", command=self.redo)
            self.redo_button.pack()
            
            self.root.bind("<Control-L>", lambda event: self.save_image())  # Load image mapped to Ctrl+L
            self.root.bind("<Control-S>", lambda event: self.load_image())  # Save image mapped to Ctrl+S
            self.root.bind("<Control-Z>", lambda event: self.undo())
            self.root.bind("<Control-Y>", lambda event: self.redo())
    
        def save_state(self):
            if self.image is not None:
                self.history.append(self.image.copy())
                self.redo_stack.clear()
    
        def load_image(self):
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if file_path:
                self.image = cv2.imread(file_path)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.original_image = self.image.copy()
                self.history.clear()
                self.redo_stack.clear()
                self.save_state()
                self.display_image()
    
        def display_image(self):
            if self.image is not None:
                img = Image.fromarray(self.image)
                img.thumbnail((500, 400))
                self.tk_img = ImageTk.PhotoImage(img)
                self.canvas.create_image(250, 200, image=self.tk_img)
    
        def start_selection(self, event):
            self.selection = (event.x, event.y)
    
        def draw_selection(self, event):
            self.canvas.delete("rect")
            self.canvas.create_rectangle(self.selection[0], self.selection[1], event.x, event.y, outline="red", tags="rect")
    
        def apply_crop(self, event):
            if self.image is None:
                return
            self.save_state()
            x1, y1, x2, y2 = self.selection[0], self.selection[1], event.x, event.y
            self.image[y1:y2, x1:x2] = 255
            self.display_image()
    
        def degrade_quality(self, value):
            if self.image is not None:
                self.save_state()
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(value)]
                _, encoded_img = cv2.imencode('.jpg', cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR), encode_param)
                self.image = cv2.imdecode(encoded_img, 1)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.display_image()
    
        def save_image(self):
            if self.image is not None:
                file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
                if file_path:
                    cv2.imwrite(file_path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
                    messagebox.showinfo("Success", "Image saved successfully")
    
        def undo(self):
            if len(self.history) > 1:
                self.redo_stack.append(self.image.copy())
                self.image = self.history.pop()
                self.display_image()
    
        def redo(self):
            if self.redo_stack:
                self.history.append(self.image.copy())
                self.image = self.redo_stack.pop()
                self.display_image()
    
    if __name__ == "__main__":
        root = tk.Tk()
        app = ImageEditor(root)
        root.mainloop()
