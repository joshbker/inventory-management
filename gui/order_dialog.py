import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from database.models import Order, Product
from database.queries import OrderQueries, ProductQueries
from gui.base_window import BaseWindow, ScrollableFrame
from datetime import datetime

class OrderDialog(tk.Toplevel, BaseWindow):
    def __init__(self, parent, db_connection, user_id):
        super().__init__(parent)
        self.parent = parent
        self.db = db_connection
        self.user_id = user_id
        self.result = None
        self.order_items = []  # List to store selected products and quantities
        
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.setup_window_base("Create New Order", 600, 800)
        self.configure(bg="#f0f0f0")
        
        # Make it modal
        self.transient(self.parent)
        self.grab_set()

    def create_widgets(self):
        # Create scrollable frame
        self.scroll_container = ScrollableFrame(self)
        self.scroll_container.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.scroll_container.scrollable_frame)
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Create New Order",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Product selection frame
        product_frame = ttk.LabelFrame(self.main_frame, text="Add Products")
        product_frame.pack(fill='x', padx=5, pady=5)

        # Product dropdown
        self.products = self.load_available_products()
        self.product_var = tk.StringVar()
        self.product_combobox = ttk.Combobox(
            product_frame,
            textvariable=self.product_var,
            values=list(self.products.keys()),
            state='readonly',
            width=40
        )
        self.product_combobox.pack(padx=5, pady=5)

        # Quantity frame
        quantity_frame = ttk.Frame(product_frame)
        quantity_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(quantity_frame, text="Quantity:").pack(side='left', padx=5)
        vcmd = (self.register(self.validate_integer), '%P')
        self.quantity_entry = ttk.Entry(
            quantity_frame,
            width=10,
            validate='key',
            validatecommand=vcmd
        )
        self.quantity_entry.pack(side='left', padx=5)
        self.quantity_entry.insert(0, "1")

        # Add product button
        ttk.Button(
            product_frame,
            text="Add to Order",
            command=self.add_product_to_order
        ).pack(pady=5)

        # Order items frame
        self.items_frame = ttk.LabelFrame(self.main_frame, text="Order Items")
        self.items_frame.pack(fill='both', expand=True, padx=5, pady=10)

        # Order items treeview
        self.items_tree = ttk.Treeview(
            self.items_frame,
            columns=('Product', 'Quantity', 'Price', 'Total'),
            show='headings'
        )
        
        self.items_tree.heading('Product', text='Product')
        self.items_tree.heading('Quantity', text='Quantity')
        self.items_tree.heading('Price', text='Price')
        self.items_tree.heading('Total', text='Total')

        self.items_tree.column('Product', width=200)
        self.items_tree.column('Quantity', width=100)
        self.items_tree.column('Price', width=100)
        self.items_tree.column('Total', width=100)

        self.items_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Total amount frame
        total_frame = ttk.Frame(self.main_frame)
        total_frame.pack(fill='x', padx=5, pady=10)

        ttk.Label(
            total_frame,
            text="Total Amount:",
            font=('Helvetica', 12, 'bold')
        ).pack(side='left', padx=5)

        self.total_label = ttk.Label(
            total_frame,
            text="$0.00",
            font=('Helvetica', 12, 'bold')
        )
        self.total_label.pack(side='right', padx=5)

        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))

        # Place Order button
        ttk.Button(
            buttons_frame,
            text="Place Order",
            command=self.place_order,
            style='Accent.TButton'
        ).pack(side='left', expand=True, padx=5)

        # Cancel button
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side='left', expand=True, padx=5)

    def load_available_products(self):
        try:
            products = ProductQueries.get_all_products(self.db)
            return {f"{p['name']} (${p['price']})": p for p in products}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")
            return {}

    def validate_integer(self, value):
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False

    def add_product_to_order(self):
        selected = self.product_var.get()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return

        quantity = self.quantity_entry.get().strip()
        if not quantity:
            messagebox.showwarning("Warning", "Please enter quantity")
            return

        quantity = int(quantity)
        if quantity <= 0:
            messagebox.showwarning("Warning", "Quantity must be positive")
            return

        product = self.products[selected]
        if quantity > product['stock_quantity']:
            messagebox.showwarning(
                "Warning", 
                f"Not enough stock. Available: {product['stock_quantity']}"
            )
            return

        # Calculate item total
        price = Decimal(str(product['price']))
        total = price * Decimal(quantity)

        # Add to treeview
        self.items_tree.insert('', 'end', values=(
            product['name'],
            quantity,
            f"${price:.2f}",
            f"${total:.2f}"
        ))

        # Store order item
        self.order_items.append({
            'product_id': product['product_id'],
            'quantity': quantity,
            'price': price,
            'total': total
        })

        # Update total amount
        self.update_total_amount()

        # Clear quantity
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")

    def update_total_amount(self):
        total = sum(item['total'] for item in self.order_items)
        self.total_label.config(text=f"${total:.2f}")

    def place_order(self):
        if not self.order_items:
            messagebox.showwarning("Warning", "Please add items to the order")
            return

        try:
            # Calculate total amount
            total_amount = sum(item['total'] for item in self.order_items)

            # Create order
            order = Order(
                order_id=None,
                user_id=self.user_id,
                order_date=datetime.now(),
                status="Pending",
                total_amount=total_amount
            )

            # Save order
            order_id = OrderQueries.create_order(self.db, order)

            # Update product stock quantities
            for item in self.order_items:
                ProductQueries.update_stock_quantity(
                    self.db,
                    item['product_id'],
                    item['quantity']
                )

            messagebox.showinfo(
                "Success",
                f"Order placed successfully! Order ID: {order_id}"
            )
            
            self.result = order
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")