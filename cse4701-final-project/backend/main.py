# backend/main.py
"""
main.py
"""

from flask import Flask, jsonify, send_from_directory
from flasgger import Swagger
from flask_cors import CORS
from user import user_routes
from pets import pet_routes
from questionnaire import questionnaire_routes
import db  # your database initializer

app = Flask(__name__)
Swagger(app)  # enables /apidocs

# Initialize the SQLite database (creates file and tables on first run)
db.init_db()
# Register blueprints
app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(pet_routes, url_prefix='/pets')
app.register_blueprint(questionnaire_routes, url_prefix='/api')

CORS(app, supports_credentials=True)

@app.route('/')
def home():
    """
    Home endpoint
    ---
    responses:
      200:
        description: API is up and running
        schema:
          properties:
            message:
              type: string
              example: Pet Adoption API is running.
    """
    return jsonify({"message": "Pet Adoption API is running."})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Uploads the image file for the given pet.
    """
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
