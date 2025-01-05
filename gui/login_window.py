import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from database.database import DatabaseManager
from database.queries import UserQueries
from gui.base_window import BaseWindow, ScrollableFrame
from .register_window import RegisterWindow

class LoginWindow(tk.Tk, BaseWindow):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.setup_window_base("Inventory Management System - Login", 500, 600)
        self.configure(bg="#f0f0f0")

    def create_widgets(self):
        # Create scrollable frame
        self.scroll_container = ScrollableFrame(self)
        self.scroll_container.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create main frame inside scrollable frame
        self.main_frame = ttk.Frame(self.scroll_container.scrollable_frame)
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Style configuration
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12))

        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Login to System",
            font=('Helvetica', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Username
        ttk.Label(self.main_frame, text="Username:").pack(anchor='w')
        self.username_entry = ttk.Entry(self.main_frame, width=30)
        self.username_entry.pack(pady=(5, 15), ipady=5)

        # Password
        ttk.Label(self.main_frame, text="Password:").pack(anchor='w')
        self.password_entry = ttk.Entry(self.main_frame, width=30, show="*")
        self.password_entry.pack(pady=(5, 20), ipady=5)

        # Login Button
        self.login_button = ttk.Button(
            self.main_frame,
            text="Login",
            command=self.handle_login,
            style='Accent.TButton'
        )
        self.login_button.pack(pady=(0, 10), ipady=5, fill='x')

        # Register Button
        self.register_button = ttk.Button(
            self.main_frame,
            text="Register New User",
            command=self.show_register_dialog
        )
        self.register_button.pack(ipady=5, fill='x')

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            conn = self.db.get_connection()
            user = UserQueries.get_user_by_username(conn, username)

            if user:
                stored_password = user['password_hash']
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    self.handle_successful_login(dict(user))
                else:
                    messagebox.showerror("Error", "Invalid credentials")
            else:
                messagebox.showerror("Error", "User not found")

        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def handle_successful_login(self, user_data):
        self.withdraw()  # Hide login window
        self.clear_inputs()
        # Launch main application window
        from gui.main_window import MainWindow
        main_window = MainWindow(user_data, self)
        main_window.protocol("WM_DELETE_WINDOW", lambda: self.handle_main_window_close(main_window))

    def handle_main_window_close(self, main_window):
        main_window.destroy()
        self.deiconify()  # Show login window again

    def show_register_dialog(self):
        register_window = RegisterWindow(self)
        self.wait_window(register_window)

    def clear_inputs(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def on_closing(self):
        self.db.close()
        self.destroy()