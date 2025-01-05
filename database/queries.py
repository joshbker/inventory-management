from typing import Optional, List, Dict, Any
import sqlite3
from .models import User, Product, Supplier, Order

class UserQueries:
    @staticmethod
    def create_user(conn: sqlite3.Connection, user: User) -> int:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, age, password_hash)
            VALUES (?, ?, ?, ?)
        """, (user.username, user.email, user.age, user.password_hash))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

    @staticmethod
    def check_email_exists(conn: sqlite3.Connection, email: str) -> bool:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return cursor.fetchone() is not None

class ProductQueries:
    @staticmethod
    def create_product(conn: sqlite3.Connection, product: Product) -> int:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, description, category, price, 
                                stock_quantity, qr_code_path, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product.name, product.description, product.category, 
              float(product.price), product.stock_quantity, product.qr_code_path, 
              product.supplier_id))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all_products(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_id, name, category, price, stock_quantity 
            FROM products
        """)
        return cursor.fetchall()

    @staticmethod
    def update_product(conn: sqlite3.Connection, product: Product) -> None:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET name = ?, description = ?, category = ?, 
                price = ?, stock_quantity = ?, supplier_id = ?
            WHERE product_id = ?
        """, (product.name, product.description, product.category,
              float(product.price), product.stock_quantity, product.supplier_id,
              product.product_id))
        conn.commit()

    @staticmethod
    def delete_product(conn: sqlite3.Connection, product_id: int) -> None:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()

    @staticmethod
    def get_product_by_id(conn: sqlite3.Connection, product_id: int) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        return cursor.fetchone()

    @staticmethod
    def search_products(conn: sqlite3.Connection, search_term: str) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_id, name, category, price, stock_quantity 
            FROM products 
            WHERE name LIKE ? OR category LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        return cursor.fetchall()

    @staticmethod
    def update_product_qr_code(conn: sqlite3.Connection, product_id: int, qr_code_path: str) -> None:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET qr_code_path = ? 
            WHERE product_id = ?
        """, (qr_code_path, product_id))
        conn.commit()

class SupplierQueries:
    @staticmethod
    def create_supplier(conn: sqlite3.Connection, supplier: Supplier) -> int:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers (name, contact_person, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (supplier.name, supplier.contact_person, supplier.email, 
              supplier.phone, supplier.address))
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_all_suppliers(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        return cursor.fetchall()

    @staticmethod
    def update_supplier(conn: sqlite3.Connection, supplier: Supplier) -> None:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE suppliers 
            SET name = ?, contact_person = ?, email = ?, 
                phone = ?, address = ?
            WHERE supplier_id = ?
        """, (supplier.name, supplier.contact_person, supplier.email,
              supplier.phone, supplier.address, supplier.supplier_id))
        conn.commit()

    @staticmethod
    def delete_supplier(conn: sqlite3.Connection, supplier_id: int) -> None:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))
        conn.commit()

    @staticmethod
    def get_supplier_by_id(conn: sqlite3.Connection, supplier_id: int) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = ?", (supplier_id,))
        return cursor.fetchone()

    @staticmethod
    def get_all_suppliers(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        return cursor.fetchall()

class OrderQueries:
    @staticmethod
    def create_order(conn: sqlite3.Connection, order: Order) -> int:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, status, total_amount)
            VALUES (?, ?, ?)
        """, (order.user_id, order.status, order.total_amount))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_orders(conn: sqlite3.Connection, user_id: int) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders WHERE user_id = ? 
            ORDER BY order_date DESC
        """, (user_id,))
        return cursor.fetchall()