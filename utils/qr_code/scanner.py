import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from pyzbar.pyzbar import decode
import json
from PIL import Image, ImageTk
import numpy as np
from gui.base_window import BaseWindow
import threading
import queue
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
        self.frame_queue = queue.Queue(maxsize=1)
        self.result_queue = queue.Queue()
        self.last_scan_time = 0
        self.failed_frames = 0  # Counter for consecutive failed frames
        self.MAX_FAILED_FRAMES = 30  # Maximum number of consecutive failures before error
        
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
        self.setup_window_base("QR Code Scanner", 800, 800)
        self.configure(bg="#f0f0f0")

    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Title and instructions
        ttk.Label(
            self.main_frame,
            text="QR Code Scanner",
            font=('Helvetica', 16, 'bold')
        ).pack(pady=(0, 10))

        ttk.Label(
            self.main_frame,
            text="Hold a QR code up to the camera to scan",
            font=('Helvetica', 12)
        ).pack(pady=(0, 10))

        # Frame for video feed
        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(pady=10)

        # Label for video feed
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()

        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="⏳ Initializing camera...",
            font=('Helvetica', 11, 'bold')
        )
        self.status_label.pack(pady=10)

        # Results frame
        self.results_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Scanned Product Details"
        )
        self.results_frame.pack(fill='x', padx=10, pady=10)
        self.results_frame.pack_forget()

        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
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
            # Try different camera indices if the first one fails
            for camera_index in range(2):
                self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Use DirectShow
                if self.cap.isOpened():
                    # Set properties for better performance
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    break
            
            if not self.cap.isOpened():
                raise Exception("No working camera found")

            self.is_running = True
            self.failed_frames = 0
            self.logger.info("Camera initialized successfully")
            
            # Start threads
            threading.Thread(target=self.update_camera, daemon=True).start()
            threading.Thread(target=self.process_frames, daemon=True).start()
            self.update_gui()
            
            self.status_label.configure(text="🔍 Scanning for QR codes...")

        except Exception as e:
            self.logger.error(f"Failed to start scanner: {str(e)}")
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            self.destroy()

    def restart_camera(self):
        """Restart the camera if it's having issues"""
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
                    self.failed_frames = 0  # Reset counter on successful frame
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Add scanning overlay
                    height, width = frame_rgb.shape[:2]
                    cv2.rectangle(
                        frame_rgb, 
                        (width//4, height//4),
                        (3*width//4, 3*height//4),
                        (0, 255, 0), 
                        2
                    )
                    
                    if self.frame_queue.full():
                        self.frame_queue.get()
                    self.frame_queue.put(frame_rgb)
                else:
                    self.failed_frames += 1
                    if self.failed_frames >= self.MAX_FAILED_FRAMES:
                        self.logger.warning("Too many failed frames, attempting camera restart")
                        self.after(0, self.restart_camera)
                        break

            except Exception as e:
                self.logger.error(f"Camera update error: {str(e)}")
                self.failed_frames += 1
                if self.failed_frames >= self.MAX_FAILED_FRAMES:
                    self.after(0, self.restart_camera)
                    break

            self.after(10)  # Small delay to reduce CPU usage

    def process_frames(self):
        while self.is_running:
            try:
                frame = self.frame_queue.get(timeout=1)
                decoded_objects = decode(frame)
                
                for obj in decoded_objects:
                    try:
                        data = json.loads(obj.data.decode('utf-8'))
                        self.logger.info(f"Successfully decoded QR code: {data}")
                        self.result_queue.put(data)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to decode QR data: {str(e)}")
                        continue
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Frame processing error: {str(e)}")
                continue

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
            ).pack(anchor='w', padx=5, pady=(5,10))

            details = [
                ("ID", data['product_id']),
                ("Name", data['name']),
                ("Category", data['category']),
                ("Price", f"${data['price']}")
            ]

            if data.get('description'):
                details.append(("Description", data['description']))

            for label, value in details:
                frame = ttk.Frame(self.results_frame)
                frame.pack(fill='x', padx=5, pady=2)
                ttk.Label(frame, text=f"{label}:", width=15).pack(side='left')
                ttk.Label(frame, text=str(value)).pack(side='left')

            ttk.Button(
                self.results_frame,
                text="Scan Another Code",
                command=self.reset_scan
            ).pack(pady=10)

        except Exception as e:
            self.logger.error(f"Error showing results: {str(e)}")
            messagebox.showerror("Error", "Failed to display product details")

    def reset_scan(self):
        self.results_frame.pack_forget()
        self.status_label.configure(text="🔍 Scanning for QR codes...")

    def update_gui(self):
        if not self.is_running:
            return

        try:
            # Check for results
            try:
                result = self.result_queue.get_nowait()
                self.show_results(result)
            except queue.Empty:
                pass

            # Update video feed
            try:
                frame = self.frame_queue.get_nowait()
                image = Image.fromarray(frame)
                image = image.resize((640, 480))
                photo = ImageTk.PhotoImage(image=image)
                
                self.video_label.configure(image=photo)
                self.video_label.image = photo
            except queue.Empty:
                pass

        except Exception as e:
            self.logger.error(f"GUI update error: {str(e)}")

        finally:
            self.after(10, self.update_gui)

    def on_closing(self):
        self.logger.info("Shutting down scanner")
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
        self.destroy()