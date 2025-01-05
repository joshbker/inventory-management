import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Initialize storage for bound widgets
        self._bound_widgets = set()
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure the canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Bind canvas configuration
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Pack the widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configure the canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mouse wheel scrolling
        self.bind_mouse_scroll()

    def bind_mouse_scroll(self):
        def _on_mousewheel(event):
            if self.canvas.winfo_exists():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind to the canvas and scrollable frame
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel, add="+")
        self._bound_widgets.add(self.canvas)

    def unbind_mouse_scroll(self):
        # Unbind from all widgets
        self.canvas.unbind_all("<MouseWheel>")
        self._bound_widgets.clear()

    def on_frame_configure(self, event=None):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the width of the inner frame to fill the canvas
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def destroy(self):
        # Clean up bindings before destroying
        self.unbind_mouse_scroll()
        super().destroy()

class BaseWindow:
    """Mixin class for window setup and sizing"""
    
    def setup_window_base(self, title, width=800, height=600):
        self.title(title)
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate minimum dimensions (80% of screen size if larger than base size)
        min_width = min(int(screen_width * 0.8), max(width, int(screen_width * 0.4)))
        min_height = min(int(screen_height * 0.8), max(height, int(screen_height * 0.4)))
        
        # Set minimum size
        self.minsize(min_width, min_height)
        
        # Calculate position for center of screen
        center_x = int((screen_width - min_width) / 2)
        center_y = int((screen_height - min_height) / 2)
        
        # Set window size and position
        self.geometry(f"{min_width}x{min_height}+{center_x}+{center_y}")
        
        # Make the window resizable
        self.resizable(True, True)
        
        # Bind the closing event
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
    def on_window_close(self):
        """Handle window closing"""
        # Clean up any ScrollableFrames
        for widget in self.winfo_children():
            if isinstance(widget, ScrollableFrame):
                widget.unbind_mouse_scroll()
        self.destroy()