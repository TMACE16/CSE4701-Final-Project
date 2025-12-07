# backend/main.py
"""
main.py
"""

from flask import Flask, jsonify, send_from_directory
from flasgger import Swagger
from flask_cors import CORS
from user import user_routes
from tracking import tracking_routes
from package import package_routes
from billing import billing_routes
from admin import admin_routes
import db

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Register all blueprints
app.register_blueprint(user_routes, url_prefix='/api')
app.register_blueprint(tracking_routes, url_prefix='/api')
app.register_blueprint(package_routes, url_prefix='/api')
app.register_blueprint(billing_routes, url_prefix='/api')
app.register_blueprint(admin_routes, url_prefix='/api')


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
              example: Package Delivery API is running.
    """
    return jsonify({"message": "Package Delivery API is running."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
