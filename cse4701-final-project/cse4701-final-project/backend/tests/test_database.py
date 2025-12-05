# backend/tests/test_database.py
"""
Test cases for database functionality.
"""
import os
import sys
import main
import tempfile
import sqlite3
import pytest
import db
from main import app

@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """
    patch
    """
    fd, path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr(db, 'DB_PATH', path)
    db.init_db()
    yield
    os.remove(path)

@pytest.fixture
def client_ep():
    """
    Provides a test client for making requests to the API.
    """
    return app.test_client()

def test_register_and_login(client_ep):
    """
    Test the register and login
    """
    # Register
    resp = client_ep.post('/users/register', json={"email": "u@example.com", "password": "p"})
    assert resp.status_code == 201
    # Login
    resp = client_ep.post('/users/login', json={"email": "u@example.com", "password": "p"})
    assert resp.status_code == 200

def test_pet_crud_and_application(client_ep):
    """
    Insert pet, Get pet, and register user than apply 
    """
    # Insert a pet directly into the temp DB
    conn = sqlite3.connect(db.DB_PATH)
    conn.execute("INSERT INTO pets (name, species, breed) VALUES (?, ?, ?)",
                 ("Max", "Dog", "Beagle"))
    conn.commit()
    conn.close()

    # GET /pets
    resp = client_ep.get('/pets/')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(p["name"] == "Max" for p in data["pets"])

    # Register user then apply
    client_ep.post('/users/register', json={"email": "x", "password": "y"})
    resp = client_ep.post('/pets/apply', json={"user_id": 1, "pet_id": 1})
    assert resp.status_code == 201
