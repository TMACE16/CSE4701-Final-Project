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

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    species TEXT NOT NULL,
    breed TEXT,
    image TEXT,
    UNIQUE(name, species, breed)
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pet_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pets_owned TEXT,
    children TEXT,
    home_type TEXT,
    outdoor_space TEXT,
    hours_alone TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(pet_id) REFERENCES pets(id)
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
        """, ("admin123@gmail.com", "pass")
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
