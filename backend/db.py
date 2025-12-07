# backend/db.py
"""
db.py
"""

import os
import sqlite3

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'shipping.db')

# SQL schema to create tables
SCHEMA = """
PRAGMA foreign_keys = ON;

----------------------------------------------------------------------
-- Users on the website/app
----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS User (
    user_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email            TEXT UNIQUE NOT NULL,
    password         TEXT NOT NULL,
    role             TEXT NOT NULL CHECK (role IN ('customer', 'staff', 'admin')),
    
    CHECK (email LIKE '%@%')
);

----------------------------------------------------------------------
-- CUSTOMERS & BILLING
----------------------------------------------------------------------

-- Customers: both contract and non-contract
CREATE TABLE IF NOT EXISTS Customer (
    customer_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER UNIQUE,
    name             TEXT NOT NULL,
    phone            TEXT,
    address_line1    TEXT,
    address_line2    TEXT,
    city             TEXT,
    state            TEXT,
    zip              TEXT,

    -- billing method flags
    has_contract     INTEGER DEFAULT 0 CHECK (has_contract IN (0, 1)),
    account_number   INTEGER UNIQUE,
    credit_card_last4 TEXT,

    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

-- Monthly statements for contract customers
CREATE TABLE IF NOT EXISTS BillingStatement (
    statement_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    statement_month  TEXT NOT NULL,
    total_amount     REAL DEFAULT 0.00,
    status           TEXT DEFAULT 'unpaid' CHECK (status IN ('unpaid', 'paid')),
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Payments (credit card, ACH, etc.)
CREATE TABLE IF NOT EXISTS Payment (
    payment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    package_id       INTEGER,
    date_paid        TEXT NOT NULL,
    amount           REAL NOT NULL,
    method           TEXT NOT NULL CHECK (method IN ('account', 'credit_card', 'prepaid')),
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (package_id) REFERENCES Package(package_id)
);

----------------------------------------------------------------------
-- SHIPPING SERVICES & RATES
----------------------------------------------------------------------

-- Defines service type (envelope, box, overnight, etc.)
CREATE TABLE IF NOT EXISTS ServiceType (
    service_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    max_weight_lb    REAL NOT NULL,
    base_price       REAL NOT NULL,
    delivery_speed   TEXT NOT NULL CHECK (delivery_speed IN ('overnight', '2-day', 'ground'))
);

----------------------------------------------------------------------
-- PACKAGES
----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Package (
    package_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    
    sender_name      TEXT NOT NULL,
    sender_addr1     TEXT NOT NULL,
    sender_addr2     TEXT,
    sender_city      TEXT NOT NULL,
    sender_state     TEXT NOT NULL,
    sender_zip       TEXT NOT NULL,

    recipient_name   TEXT NOT NULL,
    recipient_addr1  TEXT NOT NULL,
    recipient_addr2  TEXT,
    recipient_city   TEXT NOT NULL,
    recipient_state  TEXT NOT NULL,
    recipient_zip    TEXT NOT NULL,

    service_id       INTEGER NOT NULL,
    weight_lb        REAL NOT NULL,

    is_hazardous     INTEGER DEFAULT 0 CHECK (is_hazardous IN (0, 1)),
    is_international INTEGER DEFAULT 0 CHECK (is_international IN (0, 1)),
    declared_value   REAL,
    customs_desc     TEXT,

    payment_type     TEXT NOT NULL CHECK (payment_type IN ('account', 'credit_card', 'prepaid')),
    date_shipped     TEXT NOT NULL,
    date_delivered   TEXT,
    delivered_signature TEXT,

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (service_id) REFERENCES ServiceType(service_id)
);

----------------------------------------------------------------------
-- LOCATIONS (Hubs, Trucks, Planes)
----------------------------------------------------------------------

-- Everything that can hold a package temporarily
CREATE TABLE IF NOT EXISTS Location (
    location_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    type             TEXT NOT NULL CHECK (type IN ('warehouse', 'truck', 'plane')),
    name             TEXT NOT NULL,
    city             TEXT,
    state            TEXT
);

----------------------------------------------------------------------
-- PACKAGE TRACKING (event history)
----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS TrackingEvent (
    event_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id       INTEGER NOT NULL,
    location_id      INTEGER NOT NULL,
    timestamp        TEXT NOT NULL,
    status           TEXT NOT NULL CHECK (status IN ('arrived', 'departed', 'loaded', 'out for delivery', 'delivered', 'processing')),
    notes            TEXT,

    FOREIGN KEY (package_id) REFERENCES Package(package_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

----------------------------------------------------------------------
-- Relationship of package to its monthly billing statement
----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS StatementPackage (
    statement_id     INTEGER NOT NULL,
    package_id       INTEGER NOT NULL,
    PRIMARY KEY (statement_id, package_id),
    FOREIGN KEY (statement_id) REFERENCES BillingStatement(statement_id),
    FOREIGN KEY (package_id) REFERENCES Package(package_id)
);

----------------------------------------------------------------------
-- Staff
----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Staff (
    staff_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER UNIQUE NOT NULL,
    employee_number  TEXT UNIQUE NOT NULL,
    hire_date        TEXT NOT NULL,
    department       TEXT,
    
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);
"""

def get_db_connection():
    """
    Establish and return a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database by creating tables and adding sample data.
    """
    conn = get_db_connection()
    conn.executescript(SCHEMA)
    cursor = conn.cursor()
    
    # Create admin user
    cursor.execute(
        """
        INSERT OR IGNORE INTO User (email, password, role)
        VALUES (?, ?, ?)
        """, ("admin@shipping.com", "admin123", "admin")
    )
    
    # Create sample staff user
    cursor.execute(
        """
        INSERT OR IGNORE INTO User (email, password, role)
        VALUES (?, ?, ?)
        """, ("staff@shipping.com", "staff123", "staff")
    )
    
    # Create sample customer user
    cursor.execute(
        """
        INSERT OR IGNORE INTO User (email, password, role)
        VALUES (?, ?, ?)
        """, ("customer@example.com", "password123", "customer")
    )
    
    # Create sample service types
    cursor.executemany(
        """
        INSERT OR IGNORE INTO ServiceType (name, max_weight_lb, base_price, delivery_speed)
        VALUES (?, ?, ?, ?)
        """,
        [
            ('Overnight Letter', 1.0, 25.99, 'overnight'),
            ('Overnight Package', 50.0, 45.99, 'overnight'),
            ('2-Day Express', 70.0, 19.99, '2-day'),
            ('Ground Shipping', 150.0, 9.99, 'ground')
        ]
    )
    
    # Create sample locations
    cursor.executemany(
        """
        INSERT OR IGNORE INTO Location (type, name, city, state)
        VALUES (?, ?, ?, ?)
        """,
        [
            ('warehouse', 'Distribution Center East', 'Newark', 'NJ'),
            ('warehouse', 'Distribution Center West', 'Los Angeles', 'CA'),
            ('truck', 'Delivery Truck 101', 'New York', 'NY'),
            ('plane', 'Cargo Flight 202', None, None)
        ]
    )
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

    # First, get the user_id
    user_result = cursor.execute("""
        SELECT user_id FROM User WHERE email = ?
    """, ("customer@example.com",)).fetchone()

    if user_result:
        user_id = user_result['user_id']
    
        # Create customer profile
        cursor.execute("""
            INSERT OR IGNORE INTO Customer (user_id, name, phone, address_line1, city, state, zip, has_contract, account_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, "John Customer", "555-1234", "123 Main St", "New York", "NY", "10001", 0, None))


    # Add a test package
    cursor.execute("""
        INSERT OR IGNORE INTO Package (
            customer_id, sender_name, sender_addr1, sender_city, sender_state, sender_zip,
            recipient_name, recipient_addr1, recipient_city, recipient_state, recipient_zip,
            service_id, weight_lb, is_hazardous, is_international, payment_type, date_shipped
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,  # customer_id (adjust as needed)
        "John Sender", "123 Main St", "New York", "NY", "10001",
        "Jane Recipient", "456 Oak Ave", "Los Angeles", "CA", "90001",
        1,  # service_id (overnight)
        5.5,  # weight
        0,  # not hazardous
        0,  # not international
        "credit_card",
        "2025-12-01 10:00:00"
    ))

    package_id = cursor.lastrowid

    # Add tracking event for the package
    cursor.execute("""
        INSERT INTO TrackingEvent (package_id, location_id, timestamp, status, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (
        package_id,
        1,  # location_id (warehouse)
        "2025-12-01 10:30:00",
        "processing",
        "Package received at distribution center"
    ))

if __name__ == '__main__':
    # Run this file directly to initialize the database
    init_db()
