# Secure Inventory Management Application with Graphical User Interface using SQLite and QR Code

## Scenario
You have been tasked with developing a **secure inventory management application** with a graphical user interface (GUI) using SQLite and QR code functionality. This application is designed for businesses such as retail stores to implement **product tracking, stock management,** and **order handling**.

---

## Overview
The goal is to create a user-friendly, secure application that combines the following features:
- A **Graphical User Interface (GUI)** for interaction.
- **Secure user authentication** for system access.
- **QR code generation and scanning** for efficient product management.
- A robust **SQLite database** for data storage and CRUD operations.
- **SQL injection prevention** to ensure system security.

---

## Software Requirements

### 1. **Graphical User Interface** (12 Marks)
- Develop the GUI using **Python**.
- Ensure it is **user-friendly** and **visually appealing**.
- Must include:
  - A **search bar**.
  - **Product categories**.
  - A **QR code scanner**.

### 2. **User Authentication** (5 Marks)
- Implement a secure login system requiring **user credentials**.
- Passwords must be **hashed** and securely stored in the SQLite database.

### 3. **QR Code Generator and Scanner** (8 Marks)
- Include functionality to **generate** and **scan QR codes**.
- QR codes should provide **product details** when scanned.
- Generated QR codes must be saved in the **local directory** of the application.

### 4. **Minimum Software Requirements** (12 Marks)
- Create an **SQLite database** to store key information:
  - **User registration**.
  - **Products**.
  - **Suppliers**.
  - **Orders**.
- The database must be **linked to the GUI**.
- Full marks require implementation of **CRUD (Create, Read, Update, Delete)** operations for all tables.

### 5. **SQL Injection Prevention** (3 Marks)
- Sanitize and validate **all user inputs** before passing them to the database.
- Reject and do not store any user details where the **age is under 18** (considered an attack).

---

## Key Considerations
- Ensure **consistency** across all application components.
- The application can have **one or more windows**, linked seamlessly for a smooth user experience.
- Monitor stock levels for all products.​
- Reduce stock when a sale is recorded.​
- Alert for low stock to reorder products.​
- Update stock when new shipments arrive.​
- Use QR codes for product identification and tracking.
