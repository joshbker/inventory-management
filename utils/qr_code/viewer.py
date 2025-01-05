import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from gui.base_window import BaseWindow

class QRCodeViewer(tk.Toplevel, BaseWindow):
    def __init__(self, parent, product):
        super().__init__(parent)
        self.parent = parent
        self.product = product
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.setup_window_base(f"QR Code - {self.product.name}", 400, 500)
        self.configure(bg="#f0f0f0")
        
        # Make it modal
        self.transient(self.parent)
        self.grab_set()

    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"QR Code for {self.product.name}",
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Check if QR code exists
        if not self.product.qr_code_path or not os.path.exists(self.product.qr_code_path):
            error_label = ttk.Label(
                main_frame,
                text="QR code not found.",
                font=('Helvetica', 12)
            )
            error_label.pack(pady=20)
            return

        try:
            # Load and display QR code image
            image = Image.open(self.product.qr_code_path)
            # Resize if needed while maintaining aspect ratio
            if image.size[0] > 300 or image.size[1] > 300:
                image.thumbnail((300, 300))
            
            photo = ImageTk.PhotoImage(image)
            
            # Create label to display image
            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo  # Keep a reference to prevent garbage collection
            image_label.pack(pady=20)

            # Product details
            details_frame = ttk.LabelFrame(main_frame, text="Product Details")
            details_frame.pack(fill='x', padx=10, pady=10)

            # Add product details
            ttk.Label(details_frame, text=f"ID: {self.product.product_id}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(details_frame, text=f"Name: {self.product.name}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(details_frame, text=f"Category: {self.product.category}").pack(anchor='w', padx=5, pady=2)
            ttk.Label(details_frame, text=f"Price: ${self.product.price}").pack(anchor='w', padx=5, pady=2)
            
            # Save location
            path_label = ttk.Label(
                main_frame,
                text=f"QR Code location:\n{self.product.qr_code_path}",
                font=('Helvetica', 9),
                wraplength=350
            )
            path_label.pack(pady=(20, 0))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load QR code: {str(e)}")#