import logging
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from database.models import Product
from database.queries import ProductQueries, SupplierQueries
from gui.base_window import BaseWindow, ScrollableFrame
from utils.qr_code.generator import QRCodeGenerator

class ProductDialog(tk.Toplevel, BaseWindow):
    def __init__(self, parent, db_connection, product=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db_connection
        self.product = product
        self.result = None
        self.qr_generator = QRCodeGenerator()
        self.setup_logging()
        
        self.setup_window()
        self.create_widgets()
        if self.product:
            self.load_product_data()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='product.log'
        )
        self.logger = logging.getLogger(__name__)

    def setup_window(self):
        title = "Edit Product" if self.product else "Add Product"
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
        title_text = "Edit Product" if self.product else "Add New Product"
        title_label = ttk.Label(
            self.main_frame,
            text=title_text,
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Product Name
        ttk.Label(self.main_frame, text="Product Name:").pack(anchor='w')
        self.name_entry = ttk.Entry(self.main_frame, width=40)
        self.name_entry.pack(pady=(5, 15), ipady=3)

        # Category
        ttk.Label(self.main_frame, text="Category:").pack(anchor='w')
        self.category_entry = ttk.Entry(self.main_frame, width=40)
        self.category_entry.pack(pady=(5, 15), ipady=3)

        # Description
        ttk.Label(self.main_frame, text="Description:").pack(anchor='w')
        self.description_text = tk.Text(self.main_frame, width=40, height=4)
        self.description_text.pack(pady=(5, 15))

        # Price
        ttk.Label(self.main_frame, text="Price ($):").pack(anchor='w')
        vcmd = (self.register(self.validate_decimal), '%P')
        self.price_entry = ttk.Entry(
            self.main_frame, 
            width=40, 
            validate='key', 
            validatecommand=vcmd
        )
        self.price_entry.pack(pady=(5, 15), ipady=3)

        # Stock Quantity
        ttk.Label(self.main_frame, text="Stock Quantity:").pack(anchor='w')
        vcmd2 = (self.register(self.validate_integer), '%P')
        self.stock_entry = ttk.Entry(
            self.main_frame, 
            width=40,
            validate='key', 
            validatecommand=vcmd2
        )
        self.stock_entry.pack(pady=(5, 15), ipady=3)

        # Supplier
        ttk.Label(self.main_frame, text="Supplier:").pack(anchor='w')
        self.supplier_combobox = ttk.Combobox(
            self.main_frame,
            width=37,
            state='readonly'
        )
        self.load_suppliers()
        self.supplier_combobox.pack(pady=(5, 20), ipady=3)

        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))

        # Save button
        save_button = ttk.Button(
            buttons_frame,
            text="Save",
            command=self.save_product,
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

    def save_product(self):
        if not self.validate_inputs():
            return

        try:
            name = self.name_entry.get().strip()
            category = self.category_entry.get().strip()
            description = self.description_text.get('1.0', 'end-1c').strip()
            price = Decimal(self.price_entry.get().strip())
            stock = int(self.stock_entry.get().strip())
            
            supplier_display = self.supplier_combobox.get()
            supplier_id = self.suppliers.get(supplier_display)

            # Create product object
            product = Product(
                product_id=getattr(self.product, 'product_id', None),
                name=name,
                category=category,
                description=description if description else None,
                price=price,
                stock_quantity=stock,
                supplier_id=supplier_id,
                qr_code_path=None
            )

            # Save product to database
            if self.product:  # Update existing product
                ProductQueries.update_product(self.db, product)
                self.logger.info(f"Updated product {product.product_id}")
            else:  # Create new product
                product.product_id = ProductQueries.create_product(self.db, product)
                self.logger.info(f"Created new product with ID {product.product_id}")

            # Generate QR code
            if product.product_id:  # Make sure we have a product ID
                try:
                    qr_code_path = self.qr_generator.generate_product_qr(product)
                    self.logger.info(f"Generated QR code at {qr_code_path}")
                    
                    # Update product with QR code path
                    ProductQueries.update_product_qr_code(self.db, product.product_id, qr_code_path)
                    self.logger.info(f"Updated product {product.product_id} with QR code path")
                    
                    messagebox.showinfo("Success", 
                        f"Product {'updated' if self.product else 'added'} successfully!\n"
                        f"QR code saved to: {qr_code_path}")
                except Exception as qr_error:
                    self.logger.error(f"QR code generation failed: {str(qr_error)}")
                    messagebox.showwarning("Warning", 
                        f"Product saved but QR code generation failed: {str(qr_error)}")
            
            self.result = product
            self.destroy()

        except Exception as e:
            self.logger.error(f"Failed to save product: {str(e)}")
            messagebox.showerror("Error", f"Failed to save product: {str(e)}")

    def load_suppliers(self):
        try:
            suppliers = SupplierQueries.get_all_suppliers(self.db)
            self.suppliers = {f"{s['name']} ({s['email']})": s['supplier_id'] 
                            for s in suppliers}
            self.supplier_combobox['values'] = list(self.suppliers.keys())
            if self.suppliers:
                self.supplier_combobox.set(list(self.suppliers.keys())[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def load_product_data(self):
        self.name_entry.insert(0, self.product.name)
        self.category_entry.insert(0, self.product.category)
        if self.product.description:
            self.description_text.insert('1.0', self.product.description)
        self.price_entry.insert(0, str(self.product.price))
        self.stock_entry.insert(0, str(self.product.stock_quantity))
        
        # Set supplier if exists
        if self.product.supplier_id:
            for display_name, supplier_id in self.suppliers.items():
                if supplier_id == self.product.supplier_id:
                    self.supplier_combobox.set(display_name)
                    break

    def validate_decimal(self, value):
        if value == "":
            return True
        try:
            if value.count('.') <= 1:
                float(value)
                return True
        except ValueError:
            return False
        return True

    def validate_integer(self, value):
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
        return True

    def validate_inputs(self):
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        price = self.price_entry.get().strip()
        stock = self.stock_entry.get().strip()

        if not all([name, category, price, stock]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return False

        try:
            float(price)
            int(stock)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock quantity")
            return False

        if float(price) < 0:
            messagebox.showerror("Error", "Price cannot be negative")
            return False

        if int(stock) < 0:
            messagebox.showerror("Error", "Stock quantity cannot be negative")
            return False

        return True