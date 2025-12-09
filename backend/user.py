# backend/user.py
"""
user.py
"""
import re
import sqlite3
from flask import Blueprint, request, jsonify
from db import get_db_connection


user_routes = Blueprint('user_routes', __name__)

def is_valid_email(e):
    """
    Verifies that the email used for login is a valid email.
    """
    # https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.match(regex, e)

def is_valid_password(p):
    """
    Verifies that the password used for login is a valid password.
    """
    return (len(p) >= 8 and len(p) <= 127)

@user_routes.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
            role:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM User WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        return jsonify({
            "token": "fake-jwt-token",
            "user": {
                "id": user["user_id"],
                "email": user["email"],
                "role": user["role"]
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401

@user_routes.route('/register', methods=['POST'])
def register():
    """
    User registration
    ---
    parameters:
      - in: body
        name: email
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
            role:
              type: string
              example: adopter
    responses:
      201:
        description: User registered
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
          "INSERT INTO User (email, password, role) VALUES (?, ?, ?)",
          (email, password, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return jsonify({"id": user_id, **data}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    finally:
        conn.close()
