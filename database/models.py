from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class User:
    user_id: Optional[int]
    username: str
    password_hash: str
    email: str
    age: int
    created_at: datetime = None

    @staticmethod
    def create_table_query() -> str:
        return """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

@dataclass
class Product:
    product_id: Optional[int]
    name: str
    description: Optional[str]
    category: str
    price: Decimal
    stock_quantity: int
    qr_code_path: Optional[str]
    supplier_id: Optional[int]

    @staticmethod
    def create_table_query() -> str:
        return """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock_quantity INTEGER NOT NULL,
            qr_code_path TEXT,
            supplier_id INTEGER,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        )
        """

@dataclass
class Supplier:
    supplier_id: Optional[int]
    name: str
    contact_person: Optional[str]
    email: str
    phone: Optional[str]
    address: Optional[str]

    @staticmethod
    def create_table_query() -> str:
        return """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT
        )
        """

@dataclass
class Order:
    order_id: Optional[int]
    user_id: int
    order_date: datetime
    status: str
    total_amount: Decimal

    @staticmethod
    def create_table_query() -> str:
        return """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """