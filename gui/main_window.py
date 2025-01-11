import tkinter as tk
from tkinter import ttk, messagebox
from database.database import DatabaseManager
from database.models import Product, Supplier
from database.queries import OrderQueries, ProductQueries, SupplierQueries
from gui.base_window import BaseWindow
from gui.order_dialog import OrderDialog
from gui.product_dialog import ProductDialog
from gui.supplier_dialog import SupplierDialog
from utils.qr_code.scanner import QRScannerDialog
from utils.qr_code.viewer import QRCodeViewer

class MainWindow(tk.Toplevel, BaseWindow):
    def __init__(self, user_data, parent):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.db = DatabaseManager()
        self.active_scanner = None  # Track active scanner window
        self.setup_window()
        self.create_menu()
        self.create_widgets()

    def setup_window(self):
        self.setup_window_base("Inventory Management System", 1024, 768)
        self.configure(bg="#f0f0f0")

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self.handle_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Inventory Menu
        inventory_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Inventory", menu=inventory_menu)
        inventory_menu.add_command(label="Products", command=self.show_products)
        inventory_menu.add_command(label="Suppliers", command=self.show_suppliers)
        inventory_menu.add_command(label="Orders", command=self.show_orders)

        # Scan QR Code Button
        menubar.add_cascade(label="Scan QR Code", command=self.scan_qr_code)

    def create_widgets(self):
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(padx=20, pady=20, fill='both', expand=True)

        # Header frame for welcome message and status
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill='x', padx=5, pady=(0, 20))

        # Welcome message
        self.welcome_label = ttk.Label(
            self.header_frame,
            text=f"Welcome, {self.user_data['username']}!",
            font=('Helvetica', 16, 'bold')
        )
        self.welcome_label.pack(side='left')

        # Status label
        self.status_label = ttk.Label(
            self.header_frame,
            text="",
            font=('Helvetica', 11)
        )
        self.status_label.pack(side='right')

        # Create search frame
        search_frame = ttk.LabelFrame(self.main_container, text="Search Products")
        search_frame.pack(fill='x', padx=5, pady=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=5, pady=5, expand=True, fill='x')

        search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.handle_search
        )
        search_button.pack(side='right', padx=5, pady=5)

        # Create main notebook for different sections
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Products tab
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text='Products')

        # Suppliers tab
        self.suppliers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.suppliers_frame, text='Suppliers')

        # Create products treeview
        self.products_tree = ttk.Treeview(
            self.products_frame,
            columns=('ID', 'Name', 'Category', 'Price', 'Stock'),
            show='headings'
        )

        # Configure treeview columns
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Name', text='Name')
        self.products_tree.heading('Category', text='Category')
        self.products_tree.heading('Price', text='Price')
        self.products_tree.heading('Stock', text='Stock')

        # Configure column widths
        self.products_tree.column('ID', width=50)
        self.products_tree.column('Name', width=200)
        self.products_tree.column('Category', width=150)
        self.products_tree.column('Price', width=100)
        self.products_tree.column('Stock', width=100)

        # Add scrollbar for products
        scrollbar = ttk.Scrollbar(
            self.products_frame,
            orient='vertical',
            command=self.products_tree.yview
        )
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        # Create products frame for the treeview and buttons
        content_frame = ttk.Frame(self.products_frame)
        content_frame.pack(fill='both', expand=True)

        # Pack the products treeview and scrollbar in a frame
        tree_frame = ttk.Frame(content_frame)
        tree_frame.pack(side='left', fill='both', expand=True)

        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Products buttons frame
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(side='right', fill='y', padx=10, pady=5)

        # Add product button
        add_button = ttk.Button(
            buttons_frame,
            text="Add Product",
            command=self.show_add_product_dialog
        )
        add_button.pack(fill='x', pady=(0, 5))

        # Edit product button
        edit_button = ttk.Button(
            buttons_frame,
            text="Edit Product",
            command=self.show_edit_product_dialog
        )
        edit_button.pack(fill='x', pady=5)

        # Delete product button
        delete_button = ttk.Button(
            buttons_frame,
            text="Delete Product",
            command=self.delete_product
        )
        delete_button.pack(fill='x', pady=5)

        # View QR code button
        view_qr_button = ttk.Button(
            buttons_frame,
            text="View QR Code",
            command=self.show_qr_code
        )
        view_qr_button.pack(fill='x', pady=5)

        # Create suppliers treeview
        self.suppliers_tree = ttk.Treeview(
            self.suppliers_frame,
            columns=('ID', 'Name', 'Contact', 'Email', 'Phone'),
            show='headings'
        )

        # Configure suppliers treeview columns
        self.suppliers_tree.heading('ID', text='ID')
        self.suppliers_tree.heading('Name', text='Name')
        self.suppliers_tree.heading('Contact', text='Contact Person')
        self.suppliers_tree.heading('Email', text='Email')
        self.suppliers_tree.heading('Phone', text='Phone')

        # Configure column widths
        self.suppliers_tree.column('ID', width=50)
        self.suppliers_tree.column('Name', width=150)
        self.suppliers_tree.column('Contact', width=150)
        self.suppliers_tree.column('Email', width=200)
        self.suppliers_tree.column('Phone', width=100)

        # Add scrollbar for suppliers
        suppliers_scrollbar = ttk.Scrollbar(
            self.suppliers_frame,
            orient='vertical',
            command=self.suppliers_tree.yview
        )
        self.suppliers_tree.configure(yscrollcommand=suppliers_scrollbar.set)

        # Create suppliers frame for the treeview and buttons
        suppliers_content_frame = ttk.Frame(self.suppliers_frame)
        suppliers_content_frame.pack(fill='both', expand=True)

        # Pack the suppliers treeview and scrollbar in a frame
        suppliers_tree_frame = ttk.Frame(suppliers_content_frame)
        suppliers_tree_frame.pack(side='left', fill='both', expand=True)

        self.suppliers_tree.pack(side='left', fill='both', expand=True)
        suppliers_scrollbar.pack(side='right', fill='y')

        # Suppliers buttons frame
        suppliers_buttons_frame = ttk.Frame(suppliers_content_frame)
        suppliers_buttons_frame.pack(side='right', fill='y', padx=10, pady=5)

        # Add supplier button
        add_supplier_button = ttk.Button(
            suppliers_buttons_frame,
            text="Add Supplier",
            command=self.show_add_supplier_dialog
        )
        add_supplier_button.pack(fill='x', pady=(0, 5))

        # Edit supplier button
        edit_supplier_button = ttk.Button(
            suppliers_buttons_frame,
            text="Edit Supplier",
            command=self.show_edit_supplier_dialog
        )
        edit_supplier_button.pack(fill='x', pady=5)

        # Delete supplier button
        delete_supplier_button = ttk.Button(
            suppliers_buttons_frame,
            text="Delete Supplier",
            command=self.delete_supplier
        )
        delete_supplier_button.pack(fill='x', pady=5)

        # Orders tab
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text='Orders')

        # Create orders treeview
        self.orders_tree = ttk.Treeview(
            self.orders_frame,
            columns=('ID', 'Date', 'Status', 'Total'),
            show='headings'
        )

        # Configure orders treeview columns
        self.orders_tree.heading('ID', text='Order ID')
        self.orders_tree.heading('Date', text='Date')
        self.orders_tree.heading('Status', text='Status')
        self.orders_tree.heading('Total', text='Total Amount')

        # Configure column widths
        self.orders_tree.column('ID', width=80)
        self.orders_tree.column('Date', width=150)
        self.orders_tree.column('Status', width=100)
        self.orders_tree.column('Total', width=120)

        # Add scrollbar for orders
        orders_scrollbar = ttk.Scrollbar(
            self.orders_frame,
            orient='vertical',
            command=self.orders_tree.yview
        )
        self.orders_tree.configure(yscrollcommand=orders_scrollbar.set)

        # Create orders frame for the treeview and buttons
        orders_content_frame = ttk.Frame(self.orders_frame)
        orders_content_frame.pack(fill='both', expand=True)

        # Pack the orders treeview and scrollbar in a frame
        orders_tree_frame = ttk.Frame(orders_content_frame)
        orders_tree_frame.pack(side='left', fill='both', expand=True)

        self.orders_tree.pack(side='left', fill='both', expand=True)
        orders_scrollbar.pack(side='right', fill='y')

        # Orders buttons frame
        orders_buttons_frame = ttk.Frame(orders_content_frame)
        orders_buttons_frame.pack(side='right', fill='y', padx=10, pady=5)

        # Add order button
        ttk.Button(
            orders_buttons_frame,
            text="New Order",
            command=self.show_new_order_dialog
        ).pack(fill='x', pady=(0, 5))

        # Update status button
        ttk.Button(
            orders_buttons_frame,
            text="Update Status",
            command=self.update_order_status
        ).pack(fill='x', pady=5)

        # Delete order button
        ttk.Button(
            orders_buttons_frame,
            text="Delete Order",
            command=self.delete_order
        ).pack(fill='x', pady=5)

        # Load initial data
        self.load_products()
        self.load_suppliers()
        self.load_orders()

    def load_products(self):
        try:
            conn = self.db.get_connection()
            products = ProductQueries.get_all_products(conn)
            
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Insert products
            for product in products:
                self.products_tree.insert('', 'end', values=(
                    product['product_id'],
                    product['name'],
                    product['category'],
                    f"${product['price']:.2f}",
                    product['stock_quantity']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def handle_search(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_products()
            return

        try:
            conn = self.db.get_connection()
            products = ProductQueries.search_products(conn, search_term)
            
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Insert filtered products
            for product in products:
                self.products_tree.insert('', 'end', values=(
                    product['product_id'],
                    product['name'],
                    product['category'],
                    f"${product['price']:.2f}",
                    product['stock_quantity']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def show_products(self):
        self.notebook.select(0)  # Select the products tab
        self.load_products()

    def show_suppliers(self):
        self.notebook.select(1)  # Select the suppliers tab
        self.load_suppliers()

    def show_orders(self):
        self.notebook.select(2)  # Select the orders tab
        self.load_orders()

    def show_new_order_dialog(self):
        dialog = OrderDialog(self, self.db.get_connection(), self.user_data['user_id'])
        self.wait_window(dialog)
        if dialog.result:
            self.load_orders()

    def load_orders(self):
        try:
            conn = self.db.get_connection()
            orders = OrderQueries.get_all_orders(conn)
            
            # Clear existing items
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            
            # Insert orders
            for order in orders:
                self.orders_tree.insert('', 'end', values=(
                    order['order_id'],
                    order['order_date'],
                    order['status'],
                    f"${order['total_amount']:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def update_order_status(self):
        selected_items = self.orders_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an order to update")
            return
        
        order_id = self.orders_tree.item(selected_items[0])['values'][0]
        
        # Create status selection dialog
        status_dialog = tk.Toplevel(self)
        status_dialog.title("Update Order Status")
        status_dialog.geometry("300x170")
        status_dialog.transient(self)
        status_dialog.grab_set()
        
        # Status options
        statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        status_var = tk.StringVar(value=statuses[0])
        
        # Create and pack widgets
        ttk.Label(
            status_dialog,
            text="Select New Status:",
            font=('Helvetica', 12)
        ).pack(pady=(20, 10))
        
        status_combo = ttk.Combobox(
            status_dialog,
            textvariable=status_var,
            values=statuses,
            state='readonly'
        )
        status_combo.pack(pady=10, padx=20, fill='x')
        
        def update_status():
            try:
                conn = self.db.get_connection()
                OrderQueries.update_order_status(
                    conn,
                    order_id,
                    status_var.get()
                )
                status_dialog.destroy()
                self.load_orders()
                messagebox.showinfo(
                    "Success",
                    "Order status updated successfully!"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to update order status: {str(e)}"
                )
        
        # Buttons frame
        buttons_frame = ttk.Frame(status_dialog)
        buttons_frame.pack(side='bottom', pady=20, fill='x', padx=20)
        
        ttk.Button(
            buttons_frame,
            text="Update",
            command=update_status,
            style='Accent.TButton'
        ).pack(side='left', expand=True, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=status_dialog.destroy
        ).pack(side='left', expand=True, padx=5)

    def delete_order(self):
        selected_items = self.orders_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an order to delete")
            return
        
        order_id = self.orders_tree.item(selected_items[0])['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this order?"):
            try:
                conn = self.db.get_connection()
                OrderQueries.delete_order(conn, order_id)
                self.load_orders()
                messagebox.showinfo("Success", "Order deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete order: {str(e)}")

    def scan_qr_code(self):
        # Check if scanner is already open
        if self.active_scanner is not None and self.active_scanner.winfo_exists():
            self.active_scanner.lift()  # Bring existing scanner to front
            return
        
        # Show loading indicator
        self.status_label.configure(text="Opening scanner...")
        self.update_idletasks()
        
        try:
            # Create scanner window
            self.active_scanner = QRScannerDialog(self)
            
            # Update status when scanner closes
            def on_scanner_close():
                if self.active_scanner is not None:
                    self.active_scanner = None
                self.status_label.configure(text="")
            
            # Safely close scanner
            self.active_scanner.protocol(
                "WM_DELETE_WINDOW", 
                lambda: (self.active_scanner.on_closing() if self.active_scanner else None, on_scanner_close())
            )
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open scanner: {str(e)}")
            self.active_scanner = None
            self.status_label.configure(text="")

    def show_add_product_dialog(self):
        dialog = ProductDialog(self, self.db.get_connection())
        self.wait_window(dialog)
        if dialog.result:
            self.load_products()

    def show_edit_product_dialog(self):
        selected_items = self.products_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
        
        product_id = self.products_tree.item(selected_items[0])['values'][0]
        
        try:
            conn = self.db.get_connection()
            product_data = ProductQueries.get_product_by_id(conn, product_id)
            
            if product_data:
                product = Product(
                    product_id=product_data['product_id'],
                    name=product_data['name'],
                    description=product_data['description'],
                    category=product_data['category'],
                    price=product_data['price'],
                    stock_quantity=product_data['stock_quantity'],
                    supplier_id=product_data['supplier_id'],
                    qr_code_path=product_data['qr_code_path']
                )
                
                dialog = ProductDialog(self, conn, product)
                self.wait_window(dialog)
                if dialog.result:
                    self.load_products()
            else:
                messagebox.showerror("Error", "Product not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit product: {str(e)}")

    def show_qr_code(self):
        selected_items = self.products_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a product to view its QR code")
            return
        
        product_id = self.products_tree.item(selected_items[0])['values'][0]
        
        try:
            conn = self.db.get_connection()
            product_data = ProductQueries.get_product_by_id(conn, product_id)
            
            if product_data:
                product = Product(
                    product_id=product_data['product_id'],
                    name=product_data['name'],
                    description=product_data['description'],
                    category=product_data['category'],
                    price=product_data['price'],
                    stock_quantity=product_data['stock_quantity'],
                    supplier_id=product_data['supplier_id'],
                    qr_code_path=product_data['qr_code_path']
                )
                
                viewer = QRCodeViewer(self, product)
                self.wait_window(viewer)
            else:
                messagebox.showerror("Error", "Product not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view QR code: {str(e)}")

    def delete_product(self):
        selected_items = self.products_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
        
        product_id = self.products_tree.item(selected_items[0])['values'][0]
        
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this product?"):
            try:
                conn = self.db.get_connection()
                ProductQueries.delete_product(conn, product_id)
                self.load_products()
                messagebox.showinfo("Success", "Product deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")

    def load_suppliers(self):
        try:
            conn = self.db.get_connection()
            suppliers = SupplierQueries.get_all_suppliers(conn)
            
            # Clear existing items
            for item in self.suppliers_tree.get_children():
                self.suppliers_tree.delete(item)
            
            # Insert suppliers
            for supplier in suppliers:
                self.suppliers_tree.insert('', 'end', values=(
                    supplier['supplier_id'],
                    supplier['name'],
                    supplier['contact_person'] or '',
                    supplier['email'],
                    supplier['phone'] or ''
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def show_add_supplier_dialog(self):
        dialog = SupplierDialog(self, self.db.get_connection())
        self.wait_window(dialog)
        if dialog.result:
            self.load_suppliers()

    def show_edit_supplier_dialog(self):
        selected_items = self.suppliers_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a supplier to edit")
            return
        
        supplier_id = self.suppliers_tree.item(selected_items[0])['values'][0]
        
        try:
            conn = self.db.get_connection()
            supplier_data = SupplierQueries.get_supplier_by_id(conn, supplier_id)
            
            if supplier_data:
                supplier = Supplier(
                    supplier_id=supplier_data['supplier_id'],
                    name=supplier_data['name'],
                    contact_person=supplier_data['contact_person'],
                    email=supplier_data['email'],
                    phone=supplier_data['phone'],
                    address=supplier_data['address']
                )
                
                dialog = SupplierDialog(self, conn, supplier)
                self.wait_window(dialog)
                if dialog.result:
                    self.load_suppliers()
            else:
                messagebox.showerror("Error", "Supplier not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit supplier: {str(e)}")

    def delete_supplier(self):
        selected_items = self.suppliers_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a supplier to delete")
            return
        
        supplier_id = self.suppliers_tree.item(selected_items[0])['values'][0]
        
        # Check if supplier has associated products
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id = ?", (supplier_id,))
            product_count = cursor.fetchone()[0]
            
            if product_count > 0:
                messagebox.showerror(
                    "Error",
                    "Cannot delete supplier with associated products. Please reassign or delete the products first."
                )
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check supplier products: {str(e)}")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this supplier?"):
            try:
                SupplierQueries.delete_supplier(conn, supplier_id)
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")

    def handle_logout(self):
        self.db.close()
        self.destroy()  # Close main window
        self.parent.deiconify()  # Show login window again

    def on_closing(self):
        self.db.close()
        self.destroy()