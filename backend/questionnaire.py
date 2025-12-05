# backend/questionnaire.py
"""
questionnaire.py
"""
import sqlite3
from flask import Blueprint, request, jsonify
from db import get_db_connection

questionnaire_routes = Blueprint('questionnaire', __name__)

@questionnaire_routes.route('/questionnaire', methods=['POST'])
def submit_questionnaire():
    """
    Submits the user's questionnaire to the database for review by admins.
    """
    data = request.get_json()
    print(f"Received data: {data}")  # Log the data received on the backend for debugging

    # Validate required fields
    pets = data.get("pets")
    children = data.get("children")
    home_type = data.get("homeType")
    outdoor_space = data.get("outdoorSpace")
    hours_alone = data.get("hoursAlone")
    pet_id = data.get("pet_id")
    user_email = data.get("userEmail")

    if not all([pets, children, home_type, outdoor_space, hours_alone, pet_id, user_email]):
        return jsonify({"error": "Missing required fields"}), 400

    # Get user_id from email
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = ?", (user_email,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id = user["id"]

    # Insert application
    try:
        cur.execute("""
            INSERT INTO applications (
                user_id, pet_id, pets_owned, children,
                home_type, outdoor_space, hours_alone
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            pet_id,
            pets,
            children,
            home_type,
            outdoor_space,
            hours_alone
        ))
        conn.commit()
        return jsonify({"message": "Application submitted successfully"}), 200
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
        return jsonify({"error": "Error processing your request. Please try again later."}), 500
    finally:
        conn.close()

@questionnaire_routes.route('/my-applications', methods=['GET'])
def get_user_applications():
    """
    Retrieves all questionnaires submitted by the logged-in user.
    """
    user_email = request.args.get("email")

    if not user_email:
        return jsonify({"error": "Missing user email"}), 400

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Fetch applications for the user
    cur.execute("""
        SELECT applications.id, applications.pet_id, applications.pets_owned, applications.children,
               applications.home_type, applications.outdoor_space, applications.hours_alone,
               applications.submitted_at, applications.status, pets.name AS pet_name
        FROM applications
        JOIN pets ON applications.pet_id = pets.id
        WHERE applications.user_id = (SELECT id FROM users WHERE email = ?)
    """, (user_email,))
    applications = cur.fetchall()

    conn.close()

    if not applications:
        return jsonify({"message": "No applications found"}), 404

    # Return the applications with relevant details
    result = [{
        "id": app["id"],
        "pet_name": app["pet_name"],
        "pets_owned": app["pets_owned"],
        "children": app["children"],
        "home_type": app["home_type"],
        "outdoor_space": app["outdoor_space"],
        "hours_alone": app["hours_alone"],
        "submitted_at": app["submitted_at"],
        "status": app["status"]
    } for app in applications]

    return jsonify(result), 200


@questionnaire_routes.route('/questionnaires', methods=['GET'])  # No need for '/api'
def get_all_questionnaires():
    """
    Retrieves all questionnaires submitted by users for review by admins.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.*, u.email as user_email, p.name as pet_name
        FROM applications a
        JOIN users u ON a.user_id = u.id
        JOIN pets p ON a.pet_id = p.id
        ORDER BY a.submitted_at DESC
    """)

    applications = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in applications])

@questionnaire_routes.route('/questionnaire/status/<q_id>', methods=['PUT'])
def update_questionnaire_status(q_id):
    """
    Update questionnaire status
    """
    data = request.get_json()
    status = data.get('status')

    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status'}), 400

    try:
        db = get_db_connection()

        cursor = db.cursor()

        cursor.execute(
            """
            UPDATE applications
            SET status = ?
            WHERE id = ?
            """,
            (status, q_id))

        db.commit()
        return jsonify({'message': 'Status updated successfully'}), 200

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
