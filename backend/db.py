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
Users on the website/app
----------------------------------------------------------------------

CREATE TABLE User (
    user_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email            TEXT UNIQUE NOT NULL,
    password         TEXT NOT NULL,
    role             TEXT NOT NULL CHECK (role IN ('customer', 'staff', 'admin')),
    
    CHECK (email LIKE '%@%')  -- basic email validation
);

----------------------------------------------------------------------
-- CUSTOMERS & BILLING
----------------------------------------------------------------------

-- Customers: both contract and non-contract
CREATE TABLE Customer (
    customer_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER UNIQUE,
    name             TEXT NOT NULL,
    email            TEXT,
    password         TEXT,
    phone            TEXT,
    address_line1    TEXT,
    address_line2    TEXT,
    city             TEXT,
    state            TEXT,
    zip              TEXT,

    -- billing method flags
    has_contract     INTEGER DEFAULT 0 CHECK (has_contract IN (0, 1)),   -- 1 = contract customer
    account_number   INTEGER UNIQUE,        -- contract customers only
    credit_card_last4 TEXT                  -- non-contract convenience

    CHECK (((email IS NULL AND password IS NULL) OR 
           (email IS NOT NULL AND password IS NOT NULL)) AND
           (email LIKE '%@%')),

    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

-- Monthly statements for contract customers
CREATE TABLE BillingStatement (
    statement_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    statement_month  TEXT NOT NULL,  -- e.g., '2025-01'
    total_amount     REAL DEFAULT 0.00,
    status           TEXT DEFAULT 'unpaid' CHECK (status IN ('unpaid', 'paid)),
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Payments (credit card, ACH, etc.)
CREATE TABLE Payment (
    payment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,
    date_paid        DATE NOT NULL,
    amount           REAL NOT NULL,
    method           TEXT NOT NULLCHECK (method IN ('account', 'credit_card', 'prepaid')),
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
    delivery_speed   TEXT NOT NULL CHECK (delivery_speed IN ('overnight', '2-day', 'ground')),
);

----------------------------------------------------------------------
-- PACKAGES
----------------------------------------------------------------------

CREATE TABLE Package (
    package_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id      INTEGER NOT NULL,       -- sender
    sender_name      TEXT NOT NULL,
    sender_add1      TEXT NOT NULL,
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

    is_hazardous     INTEGER DEFAULT 0,
    is_international INTEGER DEFAULT 0,
    declared_value   REAL,                  -- for customs
    customs_desc     TEXT,                  -- description if international

    payment_type     TEXT NOT NULL CHECK (payment_type IN ('account', 'credit_card', 'prepaid')),
    date_shipped     DATE NOT NULL,
    date_delivered   DATE,                  -- NULL until delivered
    delivered_signature TEXT,               -- who signed

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (service_id) REFERENCES ServiceType(service_id)
);

ALTER TABLE Payment ADD COLUMN package_id INTEGER REFERENCES Package(package_id);

----------------------------------------------------------------------
-- LOCATIONS (Hubs, Trucks, Planes)
----------------------------------------------------------------------

-- Everything that can hold a package temporarily
CREATE TABLE Location (
    location_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    type             TEXT CHECK (type IN ('warehouse', 'truck', 'plane')),
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
    timestamp        TIMESTAMP NOT NULL,
    status           TEXT CHECK (status IN ('arrived', 'departed', , -- e.g., 'arrived', 'departed', 'loaded', 'out for delivery'
    notes            TEXT,

    FOREIGN KEY (package_id) REFERENCES Package(package_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

----------------------------------------------------------------------
Relationship of package to its monthly billing statement
----------------------------------------------------------------------

CREATE TABLE StatementPackage (
    statement_id     INTEGER NOT NULL,
    package_id       INTEGER NOT NULL,
    PRIMARY KEY (statement_id, package_id),
    FOREIGN KEY (statement_id) REFERENCES BillingStatement(statement_id),
    FOREIGN KEY (package_id) REFERENCES Package(package_id)
);

----------------------------------------------------------------------
Staff
----------------------------------------------------------------------

CREATE TABLE Staff (
    staff_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER UNIQUE NOT NULL,
    role             TEXT CHECK (role IN ('staff', 'admin))
    
    FOREIGN KEY (user_id) REFERENCES User(user_id)
    FOREIGN KEY (role) REFERENCES User(role)
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
