import tkinter as tk
from tkinter import ttk, messagebox
import re
import bcrypt
from database.database import DatabaseManager
from database.models import User
from database.queries import UserQueries
from gui.base_window import BaseWindow, ScrollableFrame

class RegisterWindow(tk.Toplevel, BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = DatabaseManager()
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.setup_window_base("Register New User", 500, 700)
        self.configure(bg="#f0f0f0")
        
        # Make it modal
        self.transient(self.parent)
        self.grab_set()

    def create_widgets(self):
        # Create scrollable frame
        self.scroll_container = ScrollableFrame(self)
        self.scroll_container.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create main frame inside scrollable frame
        self.main_frame = ttk.Frame(self.scroll_container.scrollable_frame)
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Register New User",
            font=('Helvetica', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Username
        ttk.Label(self.main_frame, text="Username:").pack(anchor='w')
        self.username_entry = ttk.Entry(self.main_frame, width=30)
        self.username_entry.pack(pady=(5, 15), ipady=5)

        # Email
        ttk.Label(self.main_frame, text="Email:").pack(anchor='w')
        self.email_entry = ttk.Entry(self.main_frame, width=30)
        self.email_entry.pack(pady=(5, 15), ipady=5)

        # Age
        ttk.Label(self.main_frame, text="Age:").pack(anchor='w')
        self.age_entry = ttk.Entry(self.main_frame, width=30)
        self.age_entry.pack(pady=(5, 15), ipady=5)

        # Password
        ttk.Label(self.main_frame, text="Password:").pack(anchor='w')
        self.password_entry = ttk.Entry(self.main_frame, width=30, show="*")
        self.password_entry.pack(pady=(5, 15), ipady=5)

        # Confirm Password
        ttk.Label(self.main_frame, text="Confirm Password:").pack(anchor='w')
        self.confirm_password_entry = ttk.Entry(self.main_frame, width=30, show="*")
        self.confirm_password_entry.pack(pady=(5, 20), ipady=5)

        # Register Button
        self.register_button = ttk.Button(
            self.main_frame,
            text="Register",
            command=self.handle_registration,
            style='Accent.TButton'
        )
        self.register_button.pack(pady=(0, 10), ipady=5, fill='x')

        # Cancel Button
        self.cancel_button = ttk.Button(
            self.main_frame,
            text="Cancel",
            command=self.destroy
        )
        self.cancel_button.pack(ipady=5, fill='x')

    def validate_inputs(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        age = self.age_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Check if all fields are filled
        if not all([username, email, age, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return False

        # Validate username (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messagebox.showerror(
                "Error", 
                "Username can only contain letters, numbers, and underscores"
            )
            return False

        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return False

        # Validate age
        try:
            age_num = int(age)
            if age_num < 18:
                messagebox.showerror(
                    "Error", 
                    "You must be 18 or older to register"
                )
                return False
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid age")
            return False

        # Check password match
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return False

        # Check password strength
        if len(password) < 8:
            messagebox.showerror(
                "Error", 
                "Password must be at least 8 characters long"
            )
            return False

        if not re.search(r'[A-Z]', password):
            messagebox.showerror(
                "Error", 
                "Password must contain at least one uppercase letter"
            )
            return False

        if not re.search(r'[a-z]', password):
            messagebox.showerror(
                "Error", 
                "Password must contain at least one lowercase letter"
            )
            return False

        if not re.search(r'\d', password):
            messagebox.showerror(
                "Error", 
                "Password must contain at least one number"
            )
            return False

        return True

    def handle_registration(self):
        if not self.validate_inputs():
            return

        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        age = int(self.age_entry.get().strip())
        password = self.password_entry.get()

        try:
            conn = self.db.get_connection()

            # Check if username already exists
            if UserQueries.get_user_by_username(conn, username):
                messagebox.showerror("Error", "Username already exists")
                return

            # Check if email already exists
            if UserQueries.check_email_exists(conn, email):
                messagebox.showerror("Error", "Email already exists")
                return

            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Create new user
            new_user = User(
                user_id=None,
                username=username,
                email=email,
                age=age,
                password_hash=password_hash,
                created_at=None
            )

            UserQueries.create_user(conn, new_user)
            
            messagebox.showinfo(
                "Success", 
                "Registration successful! You can now login."
            )
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")