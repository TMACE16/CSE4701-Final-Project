# backend/tests/test_api.py

"""
Test cases for the API endpoints.

This module contains the test functions to ensure the correct behavior
of the API defined in backend.main.
"""

import pytest
from main import app

@pytest.fixture
def client():
    """
    Provides a test client for making requests to the API.
    """
    with app.test_client() as client:
        yield client

def test_home(client):
    """
    Test the home route of the Pet Adoption API.
    """
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert "Pet Adoption API is running." in data["message"]

def test_login_success(client):

    """
    Test successful login for a user.
    """
    client.post('/users/register', json={"email": "test@example.com", "password": "testpass"})
    resp = client.post('/users/login', json={"email": "test@example.com", "password": "testpass"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data

def test_login_failure(client):
    """
    Test login failure due to incorrect credentials.
    """
    resp = client.post('/users/login', json={"email": "wrong@example.com", "password": "bad"})
    assert resp.status_code == 401

def test_get_pets(client):
    """
    Test retrieving the list of pets.
    """
    resp = client.get('/pets/')
    assert resp.status_code == 200
    data = resp.get_json()
    assert "pets" in data

def test_apply_pet(client):
    """
    Test applying for a pet.
    """
    sample = {"user_id": 1, "pet_id": 1}
    resp = client.post('/pets/apply', json=sample)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["application_id"] > 0
