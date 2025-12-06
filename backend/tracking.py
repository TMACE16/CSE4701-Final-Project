# backend/tracking.py
"""
tracking.py - Package tracking routes
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from db import get_db_connection

tracking_routes = Blueprint('tracking_routes', __name__)

def login_required(f):
    """
    Decorator to require authentication for routes.
    Expects Authorization header with format: "Bearer <user_id>"
    In production, this would validate a JWT token.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            # Extract user_id from token
            # In production: decode and validate JWT token here
            token = auth_header.split(' ')[1]
            user_id = int(token)  # For now, token is just the user_id
            request.user_id = user_id
        except (IndexError, ValueError):
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function


@tracking_routes.route('/tracking/<int:tracking_number>', methods=['GET'])
@login_required
def get_package_tracking(tracking_number):
    """
    Get package details and tracking history for a given tracking number.
    Only returns packages belonging to the authenticated user.
    ---
    parameters:
      - in: path
        name: tracking_number
        required: true
        schema:
          type: integer
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
          example: Bearer 1
    responses:
      200:
        description: Package tracking information
      403:
        description: Unauthorized to view this package
      404:
        description: Package not found
    """
    conn = get_db_connection()
    
    try:
        # Get package details
        package_query = """
            SELECT 
                p.package_id,
                p.recipient_name,
                p.recipient_addr1,
                p.recipient_addr2,
                p.recipient_city,
                p.recipient_state,
                p.recipient_zip,
                p.sender_name,
                p.sender_addr1,
                p.sender_addr2,
                p.sender_city,
                p.sender_state,
                p.sender_zip,
                p.weight_lb,
                p.date_shipped,
                p.date_delivered,
                p.delivered_signature,
                p.is_hazardous,
                p.is_international,
                st.name as service_name,
                st.delivery_speed,
                c.customer_id
            FROM Package p
            JOIN ServiceType st ON p.service_id = st.service_id
            JOIN Customer c ON p.customer_id = c.customer_id
            WHERE p.package_id = ?
        """
        
        package = conn.execute(package_query, (tracking_number,)).fetchone()
        
        if not package:
            return jsonify({'error': 'Package not found'}), 404
        
        # Verify the package belongs to the authenticated user
        user_check = """
            SELECT c.customer_id 
            FROM Customer c
            WHERE c.user_id = ? AND c.customer_id = ?
        """
        user_package = conn.execute(
            user_check, 
            (request.user_id, package['customer_id'])
        ).fetchone()
        
        if not user_package:
            return jsonify({'error': 'Unauthorized to view this package'}), 403
        
        # Get tracking events (history)
        tracking_query = """
            SELECT 
                te.timestamp,
                te.status,
                te.notes,
                l.type as location_type,
                l.name as location_name,
                l.city as location_city,
                l.state as location_state
            FROM TrackingEvent te
            JOIN Location l ON te.location_id = l.location_id
            WHERE te.package_id = ?
            ORDER BY te.timestamp DESC
        """
        
        tracking_events = conn.execute(tracking_query, (tracking_number,)).fetchall()
        
        # Get current status (most recent event)
        current_status = tracking_events[0] if tracking_events else None
        
        # Format response
        response = {
            'package': {
                'tracking_number': package['package_id'],
                'service': package['service_name'],
                'delivery_speed': package['delivery_speed'],
                'weight': package['weight_lb'],
                'date_shipped': package['date_shipped'],
                'date_delivered': package['date_delivered'],
                'delivered_signature': package['delivered_signature'],
                'is_hazardous': bool(package['is_hazardous']),
                'is_international': bool(package['is_international']),
                'sender': {
                    'name': package['sender_name'],
                    'address': package['sender_addr1'],
                    'address2': package['sender_addr2'],
                    'city': package['sender_city'],
                    'state': package['sender_state'],
                    'zip': package['sender_zip']
                },
                'recipient': {
                    'name': package['recipient_name'],
                    'address': f"{package['recipient_addr1']}{' ' + package['recipient_addr2'] if package['recipient_addr2'] else ''}",
                    'city': package['recipient_city'],
                    'state': package['recipient_state'],
                    'zip': package['recipient_zip']
                }
            },
            'current_status': {
                'status': current_status['status'] if current_status else 'Unknown',
                'location': current_status['location_name'] if current_status else 'Unknown',
                'city': current_status['location_city'] if current_status else None,
                'state': current_status['location_state'] if current_status else None,
                'timestamp': current_status['timestamp'] if current_status else None
            } if current_status else None,
            'tracking_history': [
                {
                    'timestamp': event['timestamp'],
                    'status': event['status'],
                    'location': event['location_name'],
                    'location_type': event['location_type'],
                    'city': event['location_city'],
                    'state': event['location_state'],
                    'notes': event['notes']
                }
                for event in tracking_events
            ]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@tracking_routes.route('/user/packages', methods=['GET'])
@login_required
def get_user_packages():
    """
    Get all packages for the authenticated user.
    ---
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
          example: Bearer 1
    responses:
      200:
        description: List of user's packages
    """
    conn = get_db_connection()
    
    try:
        query = """
            SELECT 
                p.package_id,
                p.recipient_name,
                p.recipient_city,
                p.recipient_state,
                p.date_shipped,
                p.date_delivered,
                st.name as service_name,
                (
                    SELECT te.status 
                    FROM TrackingEvent te 
                    WHERE te.package_id = p.package_id 
                    ORDER BY te.timestamp DESC 
                    LIMIT 1
                ) as current_status
            FROM Package p
            JOIN ServiceType st ON p.service_id = st.service_id
            JOIN Customer c ON p.customer_id = c.customer_id
            WHERE c.user_id = ?
            ORDER BY p.date_shipped DESC
        """
        
        packages = conn.execute(query, (request.user_id,)).fetchall()
        
        return jsonify({
            'packages': [
                {
                    'tracking_number': pkg['package_id'],
                    'recipient_name': pkg['recipient_name'],
                    'recipient_location': f"{pkg['recipient_city']}, {pkg['recipient_state']}",
                    'service': pkg['service_name'],
                    'date_shipped': pkg['date_shipped'],
                    'date_delivered': pkg['date_delivered'],
                    'current_status': pkg['current_status'] or 'Processing'
                }
                for pkg in packages
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
