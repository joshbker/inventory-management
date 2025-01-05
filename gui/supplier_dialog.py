import tkinter as tk
from tkinter import ttk, messagebox
from database.models import Supplier
from database.queries import SupplierQueries
from gui.base_window import BaseWindow, ScrollableFrame

class SupplierDialog(tk.Toplevel, BaseWindow):
    def __init__(self, parent, db_connection, supplier=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db_connection
        self.supplier = supplier  # None for add, Supplier instance for edit
        self.result = None
        
        self.setup_window()
        self.create_widgets()
        if self.supplier:
            self.load_supplier_data()

    def setup_window(self):
        title = "Edit Supplier" if self.supplier else "Add Supplier"
        self.setup_window_base(title, 500, 700)
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
        title_text = "Edit Supplier" if self.supplier else "Add New Supplier"
        title_label = ttk.Label(
            self.main_frame,
            text=title_text,
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Supplier Name
        ttk.Label(self.main_frame, text="Supplier Name:*").pack(anchor='w')
        self.name_entry = ttk.Entry(self.main_frame, width=40)
        self.name_entry.pack(pady=(5, 15), ipady=3)

        # Contact Person
        ttk.Label(self.main_frame, text="Contact Person:").pack(anchor='w')
        self.contact_entry = ttk.Entry(self.main_frame, width=40)
        self.contact_entry.pack(pady=(5, 15), ipady=3)

        # Email
        ttk.Label(self.main_frame, text="Email:*").pack(anchor='w')
        self.email_entry = ttk.Entry(self.main_frame, width=40)
        self.email_entry.pack(pady=(5, 15), ipady=3)

        # Phone
        ttk.Label(self.main_frame, text="Phone:").pack(anchor='w')
        self.phone_entry = ttk.Entry(self.main_frame, width=40)
        self.phone_entry.pack(pady=(5, 15), ipady=3)

        # Address
        ttk.Label(self.main_frame, text="Address:").pack(anchor='w')
        self.address_text = tk.Text(self.main_frame, width=40, height=4)
        self.address_text.pack(pady=(5, 15))

        # Required fields note
        ttk.Label(
            self.main_frame,
            text="* Required fields",
            font=('Helvetica', 10, 'italic')
        ).pack(pady=(0, 15))

        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))

        # Save button
        save_button = ttk.Button(
            buttons_frame,
            text="Save",
            command=self.save_supplier,
            style='Accent.TButton'
        )
        save_button.pack(side='left', expand=True, padx=5)

        # Cancel button
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_button.pack(side='left', expand=True, padx=5)

    def load_supplier_data(self):
        self.name_entry.insert(0, self.supplier.name)
        if self.supplier.contact_person:
            self.contact_entry.insert(0, self.supplier.contact_person)
        self.email_entry.insert(0, self.supplier.email)
        if self.supplier.phone:
            self.phone_entry.insert(0, self.supplier.phone)
        if self.supplier.address:
            self.address_text.insert('1.0', self.supplier.address)

    def validate_inputs(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not email:
            messagebox.showerror("Error", "Please fill in all required fields")
            return False

        # Validate email format
        if '@' not in email or '.' not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return False

        return True

    def save_supplier(self):
        if not self.validate_inputs():
            return

        name = self.name_entry.get().strip()
        contact_person = self.contact_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_text.get('1.0', 'end-1c').strip()

        try:
            supplier = Supplier(
                supplier_id=self.supplier.supplier_id if self.supplier else None,
                name=name,
                contact_person=contact_person if contact_person else None,
                email=email,
                phone=phone if phone else None,
                address=address if address else None
            )

            if self.supplier:  # Update existing supplier
                # Add update method to SupplierQueries class
                SupplierQueries.update_supplier(self.db, supplier)
                messagebox.showinfo("Success", "Supplier updated successfully!")
            else:  # Create new supplier
                SupplierQueries.create_supplier(self.db, supplier)
                messagebox.showinfo("Success", "Supplier added successfully!")

            self.result = supplier
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save supplier: {str(e)}")