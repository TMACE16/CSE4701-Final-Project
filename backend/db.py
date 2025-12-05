# backend/db.py
"""
db.py
"""

import os
import sqlite3

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'petadoption.db')

# SQL schema to create tables
SCHEMA = """
PRAGMA foreign_keys = ON;

----------------------------------------------------------------------
-- CUSTOMERS & BILLING
----------------------------------------------------------------------

-- Customers: both contract and non-contract
CREATE TABLE Customer (
    customer_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    email            TEXT,
    phone            TEXT,
    address_line1    TEXT,
    address_line2    TEXT,
    city             TEXT,
    state            TEXT,
    zip              TEXT,

    -- billing method flags
    has_contract     INTEGER DEFAULT 0,     -- 1 = contract customer
    account_number   INTEGER UNIQUE,        -- contract customers only
    credit_card_last4 TEXT                  -- non-contract convenience
);

-- Monthly statements for contract customers
CREATE TABLE BillingStatement (
    statement_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    statement_month  TEXT NOT NULL,  -- e.g., '2025-01'
    total_amount     NUMERIC(12,2) DEFAULT 0.00,
    status           TEXT DEFAULT 'unpaid',
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Payments (credit card, ACH, etc.)
CREATE TABLE Payment (
    payment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    date_paid        TEXT NOT NULL,
    amount           REAL NOT NULL,
    method           TEXT NOT NULL,   -- 'credit_card', 'account', 'prepaid'
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

----------------------------------------------------------------------
-- SHIPPING SERVICES & RATES
----------------------------------------------------------------------

-- Defines service type (envelope, box, overnight, etc.)
CREATE TABLE ServiceType (
    service_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,       -- e.g., 'Overnight Letter'
    max_weight_lb    REAL NOT NULL,
    base_price       REAL NOT NULL,
    delivery_speed   TEXT NOT NULL        -- 'overnight', '2-day', 'ground'
);

----------------------------------------------------------------------
-- PACKAGES
----------------------------------------------------------------------

CREATE TABLE Package (
    package_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,       -- sender
    recipient_name   TEXT NOT NULL,
    recipient_addr1  TEXT NOT NULL,
    recipient_addr2  TEXT,
    recipient_city   TEXT NOT NULL,
    recipient_state  TEXT NOT NULL,
    recipient_zip    TEXT NOT NULL,

    service_id       INTEGER NOT NULL,
    weight_lb        REAL NOT NULL,

    is_hazardous     INTEGER DEFAULT 0,
    is_international INTEGER DEFAULT 0,
    declared_value   REAL,                  -- for customs
    customs_desc     TEXT,                  -- description if international

    payment_type     TEXT NOT NULL,         -- 'account', 'credit_card', 'prepaid'
    date_shipped     TEXT NOT NULL,
    date_delivered   TEXT,                  -- NULL until delivered
    delivered_signature TEXT,               -- who signed

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (service_id) REFERENCES ServiceType(service_id)
);

----------------------------------------------------------------------
-- LOCATIONS (Hubs, Trucks, Planes)
----------------------------------------------------------------------

-- Everything that can hold a package temporarily
CREATE TABLE Location (
    location_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    type             TEXT NOT NULL,    -- 'warehouse', 'truck', 'plane'
    name             TEXT NOT NULL,
    city             TEXT,
    state            TEXT
);

----------------------------------------------------------------------
-- PACKAGE TRACKING (event history)
----------------------------------------------------------------------

CREATE TABLE TrackingEvent (
    event_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id       INTEGER NOT NULL,
    location_id      INTEGER NOT NULL,
    timestamp        TEXT NOT NULL,
    status           TEXT NOT NULL, -- e.g., 'arrived', 'departed', 'loaded', 'out for delivery'
    notes            TEXT,

    FOREIGN KEY (package_id) REFERENCES Package(package_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

----------------------------------------------------------------------
-- OPTIONAL: Relationship of package to its monthly billing statement
----------------------------------------------------------------------

CREATE TABLE StatementPackage (
    statement_id     INTEGER NOT NULL,
    package_id       INTEGER NOT NULL,
    PRIMARY KEY (statement_id, package_id),
    FOREIGN KEY (statement_id) REFERENCES BillingStatement(statement_id),
    FOREIGN KEY (package_id) REFERENCES Package(package_id)
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
    # Only initialize if DB file does not exist
    """
    Initialize the database by creating tables if the DB file doesn't already exist.
    """
    conn = get_db_connection()
    conn.executescript(SCHEMA)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (email, password, role)
        VALUEs (?, ?, "admin")
        """, ("admin123@gmail.com", "password")
    )
    cursor.executemany(
        """
        INSERT OR IGNORE INTO pets (name, species, breed, image)
        VALUES (?, ?, ?, ?)

        """,
        [
            ('Ted', 'Dog', 'Husky', 'ted.jpg'),
            ('George', 'Cat', 'Domestic Short Hair', 'george.jpg')
        ]
    )
    conn.commit()
    conn.close()
