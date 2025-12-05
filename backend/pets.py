# backend/pets.py
"""
pets.py
"""
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from db import get_db_connection

pet_routes = Blueprint('pet_routes', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@pet_routes.route('/', methods=['GET'])
def get_pets():
    """
    Get all pets
    ---
    responses:
      200:
        description: List of pets
        schema:
          type: object
          properties:
            pets:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  species:
                    type: string
                  breed:
                    type: string
    """
    conn = get_db_connection()
    pets = conn.execute("SELECT * FROM pets").fetchall()
    conn.close()
    pets_list = []
    for pet in pets:
        pet_dict = dict(pet)
        pet_dict["image"] = f"http://localhost:5000/uploads/{pet_dict['image']}"
        pets_list.append(pet_dict)
    return jsonify({"pets": [dict(p) for p in pets]})

@pet_routes.route('/apply', methods=['POST'])
def apply_pet():
    """
    Submit adoption application
    ---
    parameters:
      - in: body
        name: application
        required: true
        schema:
          type: object
          required:
            - user_id
            - pet_id
          properties:
            user_id:
              type: integer
            pet_id:
              type: integer
    responses:
      201:
        description: Application created
    """
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO applications (user_id, pet_id) VALUES (?, ?)",
        (data["user_id"], data["pet_id"])
    )
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return jsonify({"application_id": app_id}), 201

@pet_routes.route('/add', methods=['POST'])
def add_pet():
    """
    Adds a new pet.
    Accepts form-data with 'name', 'species', 'breed', and an image file.
    """
    name = request.form.get('name')
    species = request.form.get('species')
    breed = request.form.get('breed')
    image = request.files.get('image')

    if image:
        filename = secure_filename(image.filename)
        full_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(full_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pets (name, species, breed, image) VALUES (?, ?, ?, ?)",
        (name, species, breed, filename)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Pet added successfully'}), 201
