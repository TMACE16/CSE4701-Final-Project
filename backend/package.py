# backend/package.py
"""
package.py - Package creation and management routes
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from db import get_db_connection
from datetime import datetime

package_routes = Blueprint('package_routes', __name__)

def login_required(f):
    """
    Decorator to require authentication for routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            user_id = int(token)
            request.user_id = user_id
        except (IndexError, ValueError):
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function


@package_routes.route('/services', methods=['GET'])
def get_services():
    """
    Get all available shipping services.
    ---
    responses:
      200:
        description: List of available services
    """
    conn = get_db_connection()
    
    try:
        services = conn.execute(
            "SELECT * FROM ServiceType ORDER BY delivery_speed, base_price"
        ).fetchall()
        
        return jsonify({
            'services': [
                {
                    'service_id': s['service_id'],
                    'name': s['name'],
                    'max_weight_lb': s['max_weight_lb'],
                    'base_price': s['base_price'],
                    'delivery_speed': s['delivery_speed']
                }
                for s in services
            ]
        }), 200
    finally:
        conn.close()


@package_routes.route('/ship', methods=['POST'])
@login_required
def create_shipment():
    """
    Create a new package shipment.
    ---
    parameters:
      - in: body
        name: shipment
        required: true
        schema:
          type: object
          required:
            - sender_name
            - sender_addr1
            - sender_city
            - sender_state
            - sender_zip
            - recipient_name
            - recipient_addr1
            - recipient_city
            - recipient_state
            - recipient_zip
            - service_id
            - weight_lb
            - payment_type
          properties:
            sender_name:
              type: string
            sender_addr1:
              type: string
            sender_addr2:
              type: string
            sender_city:
              type: string
            sender_state:
              type: string
            sender_zip:
              type: string
            recipient_name:
              type: string
            recipient_addr1:
              type: string
            recipient_addr2:
              type: string
            recipient_city:
              type: string
            recipient_state:
              type: string
            recipient_zip:
              type: string
            service_id:
              type: integer
            weight_lb:
              type: number
            is_hazardous:
              type: boolean
            is_international:
              type: boolean
            declared_value:
              type: number
            customs_desc:
              type: string
            payment_type:
              type: string
              enum: [account, credit_card, prepaid]
    responses:
      201:
        description: Package created successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        # Get customer_id for the user
        customer = conn.execute(
            "SELECT customer_id FROM Customer WHERE user_id = ?",
            (request.user_id,)
        ).fetchone()
        
        if not customer:
            return jsonify({'error': 'Customer profile not found. Please complete your profile.'}), 400
        
        customer_id = customer['customer_id']
        
        # Validate service and weight
        service = conn.execute(
            "SELECT * FROM ServiceType WHERE service_id = ?",
            (data['service_id'],)
        ).fetchone()
        
        if not service:
            return jsonify({'error': 'Invalid service type'}), 400
        
        if data['weight_lb'] > service['max_weight_lb']:
            return jsonify({
                'error': f'Package weight exceeds maximum for this service ({service["max_weight_lb"]} lb)'
            }), 400
        
        # Validate payment type
        if data['payment_type'] == 'account':
            # Check if customer has a contract
            has_contract = conn.execute(
                "SELECT has_contract FROM Customer WHERE customer_id = ?",
                (customer_id,)
            ).fetchone()['has_contract']
            
            if not has_contract:
                return jsonify({'error': 'Account billing requires a contract. Please use credit card.'}), 400
        
        # Insert package
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Package (
                customer_id, sender_name, sender_addr1, sender_addr2,
                sender_city, sender_state, sender_zip,
                recipient_name, recipient_addr1, recipient_addr2,
                recipient_city, recipient_state, recipient_zip,
                service_id, weight_lb, is_hazardous, is_international,
                declared_value, customs_desc, payment_type, date_shipped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            data['sender_name'],
            data['sender_addr1'],
            data.get('sender_addr2', ''),
            data['sender_city'],
            data['sender_state'],
            data['sender_zip'],
            data['recipient_name'],
            data['recipient_addr1'],
            data.get('recipient_addr2', ''),
            data['recipient_city'],
            data['recipient_state'],
            data['recipient_zip'],
            data['service_id'],
            data['weight_lb'],
            1 if data.get('is_hazardous', False) else 0,
            1 if data.get('is_international', False) else 0,
            data.get('declared_value'),
            data.get('customs_desc'),
            data['payment_type'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        package_id = cursor.lastrowid
        
        # Create initial tracking event
        # Get a default location (first warehouse)
        location = conn.execute(
            "SELECT location_id FROM Location WHERE type = 'warehouse' LIMIT 1"
        ).fetchone()
        
        if location:
            cursor.execute("""
                INSERT INTO TrackingEvent (package_id, location_id, timestamp, status, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                package_id,
                location['location_id'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'processing',
                'Package received and being processed'
            ))
        
        conn.commit()
        
        return jsonify({
            'message': 'Package created successfully',
            'tracking_number': package_id,
            'estimated_cost': service['base_price']
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@package_routes.route('/customer/profile', methods=['GET', 'POST'])
@login_required
def customer_profile():
    """
    Get or create customer profile for the logged-in user.
    ---
    responses:
      200:
        description: Customer profile
    """
    conn = get_db_connection()
    
    try:
        if request.method == 'GET':
            customer = conn.execute(
                "SELECT * FROM Customer WHERE user_id = ?",
                (request.user_id,)
            ).fetchone()
            
            if not customer:
                return jsonify({'exists': False}), 200
            
            return jsonify({
                'exists': True,
                'customer': {
                    'customer_id': customer['customer_id'],
                    'name': customer['name'],
                    'phone': customer['phone'],
                    'address_line1': customer['address_line1'],
                    'address_line2': customer['address_line2'],
                    'city': customer['city'],
                    'state': customer['state'],
                    'zip': customer['zip'],
                    'has_contract': bool(customer['has_contract']),
                    'account_number': customer['account_number']
                }
            }), 200
        
        # POST - Create/Update customer profile
        data = request.get_json()
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO Customer (user_id, name, phone, address_line1, address_line2, city, state, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.user_id,
            data['name'],
            data.get('phone', ''),
            data.get('address_line1', ''),
            data.get('address_line2', ''),
            data.get('city', ''),
            data.get('state', ''),
            data.get('zip', '')
        ))
        
        conn.commit()
        
        return jsonify({'message': 'Profile created/updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
