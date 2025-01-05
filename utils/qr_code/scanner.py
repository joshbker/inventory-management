import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import json
from PIL import Image, ImageTk
from gui.base_window import BaseWindow, ScrollableFrame
import threading
import logging
import os

# Suppress OpenCV warnings
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

class QRScannerDialog(tk.Toplevel, BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Setup logging
        self.setup_logging()

        # Initialize variables
        self.cap = None
        self.is_running = False
        self.failed_frames = 0
        self.last_detected_data = None  # To store the last detected QR data
        self.current_frame = None

        self.setup_window()
        self.create_widgets()
        self.start_scanning()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='qr_scanner.log'
        )
        self.logger = logging.getLogger(__name__)

    def setup_window(self):
        self.setup_window_base("QR Code Scanner", 1024, 768)
        self.configure(bg="#f0f0f0")

        # Allow interactions with other windows
        self.grab_release()

    def create_widgets(self):
        # Main frame
        self.main_frame = ScrollableFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Title and instructions
        ttk.Label(
            self.main_frame.scrollable_frame,
            text="QR Code Scanner",
            font=('Helvetica', 16, 'bold')
        ).pack(pady=(0, 10))

        ttk.Label(
            self.main_frame.scrollable_frame,
            text="Hold a QR code up to the camera to scan",
            font=('Helvetica', 12)
        ).pack(pady=(0, 10))

        # Frame for video feed
        self.video_frame = ttk.Frame(self.main_frame.scrollable_frame)
        self.video_frame.pack(pady=10)

        # Label for video feed
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()

        # Status label
        self.status_label = ttk.Label(
            self.main_frame.scrollable_frame,
            text="⏳ Initializing camera...",
            font=('Helvetica', 11, 'bold')
        )
        self.status_label.pack(pady=10)

        # Results frame
        self.results_frame = ttk.LabelFrame(
            self.main_frame.scrollable_frame, 
            text="Scanned Product Details"
        )
        self.results_frame.pack(fill='x', padx=10, pady=10)
        self.results_frame.pack_forget()

        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame.scrollable_frame)
        buttons_frame.pack(fill='x', pady=10)

        # Restart camera button
        self.restart_button = ttk.Button(
            buttons_frame,
            text="Restart Camera",
            command=self.restart_camera
        )
        self.restart_button.pack(side='left', padx=5, expand=True)

        # Close button
        ttk.Button(
            buttons_frame,
            text="Close Scanner",
            command=self.on_closing
        ).pack(side='left', padx=5, expand=True)

    def start_scanning(self):
        try:
            # Try different camera indices
            for camera_index in range(2):
                self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 16:9 resolution
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    break

            if not self.cap.isOpened():
                raise Exception("No working camera found")

            self.is_running = True
            self.failed_frames = 0
            self.logger.info("Camera initialized successfully")

            threading.Thread(target=self.update_camera, daemon=True).start()
            self.update_gui()

            self.status_label.configure(text="🔍 Scanning for QR codes...")

        except Exception as e:
            self.logger.error(f"Failed to start scanner: {str(e)}")
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            self.destroy()

    def restart_camera(self):
        if self.cap is not None:
            self.cap.release()
        self.start_scanning()
        self.status_label.configure(text="🔄 Restarting camera...")

    def update_camera(self):
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                continue

            try:
                ret, frame = self.cap.read()
                if ret:
                    self.failed_frames = 0
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Highlight detected QR codes
                    decoded_objects = decode(frame_rgb, symbols=[ZBarSymbol.QRCODE])
                    for obj in decoded_objects:
                        (x, y, w, h) = obj.rect
                        cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Decode QR code data
                        qr_data = obj.data.decode("utf-8")
                        if qr_data != self.last_detected_data:
                            self.last_detected_data = qr_data
                            try:
                                product_data = json.loads(qr_data)
                                self.after(0, lambda: self.show_results(product_data))
                            except json.JSONDecodeError:
                                self.logger.error(f"Invalid QR code data: {qr_data}")

                    self.current_frame = frame_rgb
                else:
                    self.failed_frames += 1
                    if self.failed_frames >= 30:
                        self.restart_camera()
                        break

            except Exception as e:
                self.logger.error(f"Camera update error: {str(e)}")
                self.failed_frames += 1
                if self.failed_frames >= 30:
                    self.restart_camera()
                    break

    def show_results(self, data):
        try:
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            self.results_frame.pack(fill='x', padx=10, pady=10)
            self.status_label.configure(text="✅ QR Code detected!")

            ttk.Label(
                self.results_frame,
                text="Found Product:",
                font=('Helvetica', 11, 'bold')
            ).pack(anchor='w', padx=5, pady=(5, 10))

            details = [
                ("ID", data.get('product_id', 'N/A')),
                ("Name", data.get('name', 'N/A')),
                ("Category", data.get('category', 'N/A')),
                ("Price", f"${data.get('price', '0.00')}")
            ]

            if data.get('description'):
                details.append(("Description", data['description']))

            for label, value in details:
                frame = ttk.Frame(self.results_frame)
                frame.pack(fill='x', padx=5, pady=2)
                ttk.Label(frame, text=f"{label}:", width=15).pack(side='left')
                ttk.Label(frame, text=str(value)).pack(side='left')

        except Exception as e:
            self.logger.error(f"Error showing results: {str(e)}")
            messagebox.showerror("Error", "Failed to display product details")

    def update_gui(self):
        if not self.is_running:
            return

        try:
            if self.current_frame is not None:
                image = Image.fromarray(self.current_frame)
                image = image.resize((426, 240))  # Slightly larger display size (2/3 of 640x360)
                photo = ImageTk.PhotoImage(image=image)

                self.video_label.configure(image=photo)
                self.video_label.image = photo
        except Exception as e:
            self.logger.error(f"GUI update error: {str(e)}")

        finally:
            self.after(67, self.update_gui)  # ~15 FPS

    def on_closing(self):
        self.logger.info("Shutting down scanner")
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
        self.destroy()
