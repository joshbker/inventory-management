from gui.login_window import LoginWindow
from database.database import DatabaseManager

def main():
    # Initialize database
    try:
        db = DatabaseManager()
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return

    # Create and run the application
    app = LoginWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()