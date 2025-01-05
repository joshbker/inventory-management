import sqlite3
from pathlib import Path
from typing import Optional
import logging
from .models import User, Product, Supplier, Order

class DatabaseManager:
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.setup_logging()
        self.initialize_database()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='database.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_connection(self) -> sqlite3.Connection:
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                self.logger.error(f"Database connection error: {e}")
                raise
        return self.conn

    def initialize_database(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create tables using model definitions
            cursor.execute(User.create_table_query())
            cursor.execute(Product.create_table_query())
            cursor.execute(Supplier.create_table_query())
            cursor.execute(Order.create_table_query())

            conn.commit()
            self.logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None