# backend/admin.py
"""
admin.py - Admin and staff management routes
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from db import get_db_connection
from datetime import datetime
import sqlite3

admin_routes = Blueprint('admin_routes', __name__)

def staff_required(f):
    """
    Decorator to require staff or admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            user_id = int(token)
            
            # Check if user is staff or admin
            conn = get_db_connection()
            user = conn.execute(
                "SELECT role FROM User WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            conn.close()
            
            if not user or user['role'] not in ['staff', 'admin']:
                return jsonify({'error': 'Staff access required'}), 403
            
            request.user_id = user_id
            request.user_role = user['role']
        except (IndexError, ValueError):
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin role only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            user_id = int(token)
            
            # Check if user is admin
            conn = get_db_connection()
            user = conn.execute(
                "SELECT role FROM User WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            conn.close()
            
            if not user or user['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            request.user_id = user_id
            request.user_role = user['role']
        except (IndexError, ValueError):
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function


@admin_routes.route('/admin/packages', methods=['GET'])
@staff_required
def get_all_packages():
    """
    Get all packages in the system with filtering options.
    ---
    parameters:
      - in: query
        name: status
        schema:
          type: string
      - in: query
        name: date_from
        schema:
          type: string
      - in: query
        name: date_to
        schema:
          type: string
    responses:
      200:
        description: List of packages
    """
    conn = get_db_connection()
    
    try:
        query = """
            SELECT 
                p.package_id,
                p.sender_name,
                p.recipient_name,
                p.recipient_city,
                p.recipient_state,
                p.date_shipped,
                p.date_delivered,
                c.name as customer_name,
                st.name as service_name,
                (
                    SELECT te.status 
                    FROM TrackingEvent te 
                    WHERE te.package_id = p.package_id 
                    ORDER BY te.timestamp DESC 
                    LIMIT 1
                ) as current_status,
                (
                    SELECT l.name
                    FROM TrackingEvent te
                    JOIN Location l ON te.location_id = l.location_id
                    WHERE te.package_id = p.package_id
                    ORDER BY te.timestamp DESC
                    LIMIT 1
                ) as current_location
            FROM Package p
            JOIN Customer c ON p.customer_id = c.customer_id
            JOIN ServiceType st ON p.service_id = st.service_id
            ORDER BY p.date_shipped DESC
            LIMIT 100
        """
        
        packages = conn.execute(query).fetchall()
        
        return jsonify({
            'packages': [
                {
                    'tracking_number': pkg['package_id'],
                    'sender': pkg['sender_name'],
                    'recipient': pkg['recipient_name'],
                    'destination': f"{pkg['recipient_city']}, {pkg['recipient_state']}",
                    'customer': pkg['customer_name'],
                    'service': pkg['service_name'],
                    'date_shipped': pkg['date_shipped'],
                    'date_delivered': pkg['date_delivered'],
                    'current_status': pkg['current_status'] or 'Unknown',
                    'current_location': pkg['current_location'] or 'Unknown'
                }
                for pkg in packages
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/packages/<int:package_id>/update-status', methods=['POST'])
@staff_required
def update_package_status(package_id):
    """
    Add a new tracking event for a package.
    ---
    parameters:
      - in: path
        name: package_id
        required: true
        schema:
          type: integer
      - in: body
        name: tracking_event
        required: true
        schema:
          type: object
          required:
            - location_id
            - status
          properties:
            location_id:
              type: integer
            status:
              type: string
            notes:
              type: string
    responses:
      201:
        description: Tracking event added
    """
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        # Verify package exists
        package = conn.execute(
            "SELECT package_id FROM Package WHERE package_id = ?",
            (package_id,)
        ).fetchone()
        
        if not package:
            return jsonify({'error': 'Package not found'}), 404
        
        # Add tracking event
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TrackingEvent (package_id, location_id, timestamp, status, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            package_id,
            data['location_id'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data['status'],
            data.get('notes', '')
        ))
        
        # If status is delivered, update package
        if data['status'] == 'delivered':
            cursor.execute("""
                UPDATE Package
                SET date_delivered = ?,
                    delivered_signature = ?
                WHERE package_id = ?
            """, (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('signature', 'Staff'),
                package_id
            ))
        
        conn.commit()
        
        return jsonify({
            'message': 'Package status updated successfully',
            'event_id': cursor.lastrowid
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/locations', methods=['GET', 'POST'])
@staff_required
def manage_locations():
    """
    Get all locations or create a new one.
    ---
    responses:
      200:
        description: List of locations
      201:
        description: Location created
    """
    conn = get_db_connection()
    
    try:
        if request.method == 'GET':
            locations = conn.execute(
                "SELECT * FROM Location ORDER BY type, name"
            ).fetchall()
            
            return jsonify({
                'locations': [
                    {
                        'location_id': loc['location_id'],
                        'type': loc['type'],
                        'name': loc['name'],
                        'city': loc['city'],
                        'state': loc['state']
                    }
                    for loc in locations
                ]
            }), 200
        
        # POST - Create new location
        data = request.get_json()
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Location (type, name, city, state)
            VALUES (?, ?, ?, ?)
        """, (
            data['type'],
            data['name'],
            data.get('city'),
            data.get('state')
        ))
        
        conn.commit()
        
        return jsonify({
            'message': 'Location created successfully',
            'location_id': cursor.lastrowid
        }), 201
        
    except Exception as e:
        if request.method == 'POST':
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/stats', methods=['GET'])
@staff_required
def get_stats():
    """
    Get dashboard statistics.
    ---
    responses:
      200:
        description: Statistics data
    """
    conn = get_db_connection()
    
    try:
        # Total packages
        total_packages = conn.execute(
            "SELECT COUNT(*) as count FROM Package"
        ).fetchone()['count']
        
        # In transit packages
        in_transit = conn.execute("""
            SELECT COUNT(*) as count FROM Package
            WHERE date_delivered IS NULL
        """).fetchone()['count']
        
        # Delivered today
        delivered_today = conn.execute("""
            SELECT COUNT(*) as count FROM Package
            WHERE date(date_delivered) = date('now')
        """).fetchone()['count']
        
        # Total customers
        total_customers = conn.execute(
            "SELECT COUNT(*) as count FROM Customer"
        ).fetchone()['count']
        
        # Recent activity
        recent_events = conn.execute("""
            SELECT 
                te.timestamp,
                te.status,
                p.package_id,
                l.name as location_name
            FROM TrackingEvent te
            JOIN Package p ON te.package_id = p.package_id
            JOIN Location l ON te.location_id = l.location_id
            ORDER BY te.timestamp DESC
            LIMIT 10
        """).fetchall()
        
        return jsonify({
            'stats': {
                'total_packages': total_packages,
                'in_transit': in_transit,
                'delivered_today': delivered_today,
                'total_customers': total_customers
            },
            'recent_activity': [
                {
                    'timestamp': event['timestamp'],
                    'status': event['status'],
                    'tracking_number': event['package_id'],
                    'location': event['location_name']
                }
                for event in recent_events
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/packages/<int:package_id>/location', methods=['GET'])
@staff_required
def get_package_location(package_id):
    """
    Get current location of a package.
    ---
    parameters:
      - in: path
        name: package_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Package location information
    """
    conn = get_db_connection()
    
    try:
        location_info = conn.execute("""
            SELECT 
                l.location_id,
                l.type,
                l.name,
                l.city,
                l.state,
                te.timestamp,
                te.status
            FROM TrackingEvent te
            JOIN Location l ON te.location_id = l.location_id
            WHERE te.package_id = ?
            ORDER BY te.timestamp DESC
            LIMIT 1
        """, (package_id,)).fetchone()
        
        if not location_info:
            return jsonify({'error': 'Package not found or no location data'}), 404
        
        return jsonify({
            'location': {
                'location_id': location_info['location_id'],
                'type': location_info['type'],
                'name': location_info['name'],
                'city': location_info['city'],
                'state': location_info['state'],
                'last_update': location_info['timestamp'],
                'status': location_info['status']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """
    Get all staff and admin users.
    ---
    responses:
      200:
        description: List of users
    """
    conn = get_db_connection()
    
    try:
        users = conn.execute("""
            SELECT user_id, email, role
            FROM User
            WHERE role IN ('staff', 'admin')
            ORDER BY role, email
        """).fetchall()
        
        return jsonify({
            'users': [
                {
                    'user_id': u['user_id'],
                    'email': u['email'],
                    'role': u['role']
                }
                for u in users
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/users/create', methods=['POST'])
@admin_required
def create_staff_user():
    """
    Create a new staff or admin user.
    ---
    parameters:
      - in: body
        name: user
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - role
          properties:
            email:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [staff, admin]
            employee_number:
              type: string
            department:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid input or email already exists
    """
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        # Validate role
        if data['role'] not in ['staff', 'admin']:
            return jsonify({'error': 'Role must be staff or admin'}), 400
        
        # Check if email already exists
        existing = conn.execute(
            "SELECT user_id FROM User WHERE email = ?",
            (data['email'],)
        ).fetchone()
        
        if existing:
            return jsonify({'error': 'Email already exists'}), 400
        
        cursor = conn.cursor()
        
        # Create user account
        cursor.execute("""
            INSERT INTO User (email, password, role)
            VALUES (?, ?, ?)
        """, (
            data['email'],
            data['password'],  # In production, hash this!
            data['role']
        ))
        
        user_id = cursor.lastrowid
        
        # Create staff record if provided
        if 'employee_number' in data or 'department' in data:
            cursor.execute("""
                INSERT INTO Staff (user_id, employee_number, hire_date, department)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                data.get('employee_number', f'EMP{user_id:05d}'),
                datetime.now().strftime('%Y-%m-%d'),
                data.get('department', 'General')
            ))
        
        conn.commit()
        
        return jsonify({
            'message': f'{data["role"].capitalize()} user created successfully',
            'user_id': user_id,
            'email': data['email'],
            'role': data['role']
        }), 201
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Delete a staff or admin user (cannot delete yourself).
    ---
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: User deleted successfully
      400:
        description: Cannot delete yourself
      403:
        description: Cannot delete customer accounts
      404:
        description: User not found
    """
    conn = get_db_connection()
    
    try:
        # Prevent self-deletion
        if user_id == request.user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Check user exists and is staff/admin
        user = conn.execute(
            "SELECT role FROM User WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['role'] == 'customer':
            return jsonify({'error': 'Cannot delete customer accounts from this interface'}), 403
        
        cursor = conn.cursor()
        
        # Delete staff record if exists
        cursor.execute("DELETE FROM Staff WHERE user_id = ?", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM User WHERE user_id = ?", (user_id,))
        
        conn.commit()
        
        return jsonify({
            'message': 'User deleted successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/users/<int:user_id>/update-role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """
    Update a user's role (staff <-> admin).
    ---
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
      - in: body
        name: role
        required: true
        schema:
          type: object
          required:
            - role
          properties:
            role:
              type: string
              enum: [staff, admin]
    responses:
      200:
        description: Role updated successfully
      400:
        description: Invalid role or cannot modify yourself
    """
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        # Prevent self-modification
        if user_id == request.user_id:
            return jsonify({'error': 'Cannot modify your own role'}), 400
        
        # Validate role
        if data['role'] not in ['staff', 'admin']:
            return jsonify({'error': 'Role must be staff or admin'}), 400
        
        # Update role
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE User
            SET role = ?
            WHERE user_id = ? AND role IN ('staff', 'admin')
        """, (data['role'], user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found or not a staff/admin'}), 404
        
        conn.commit()
        
        return jsonify({
            'message': 'Role updated successfully',
            'user_id': user_id,
            'new_role': data['role']
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/customers', methods=['GET'])
@staff_required
def get_all_customers():
    """
    Get all customer accounts.
    ---
    responses:
      200:
        description: List of customers
    """
    conn = get_db_connection()
    
    try:
        customers = conn.execute("""
            SELECT 
                c.customer_id,
                c.user_id,
                c.name,
                c.phone,
                c.has_contract,
                c.account_number,
                u.email,
                u.role,
                COUNT(p.package_id) as total_packages
            FROM Customer c
            LEFT JOIN User u ON c.user_id = u.user_id
            LEFT JOIN Package p ON c.customer_id = p.customer_id
            GROUP BY c.customer_id
            ORDER BY c.customer_id DESC
        """).fetchall()
        
        return jsonify({
            'customers': [
                {
                    'customer_id': c['customer_id'],
                    'user_id': c['user_id'],
                    'name': c['name'],
                    'email': c['email'],
                    'phone': c['phone'],
                    'has_contract': bool(c['has_contract']),
                    'account_number': c['account_number'],
                    'total_packages': c['total_packages']
                }
                for c in customers
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@admin_routes.route('/admin/customers/<int:customer_id>/contract', methods=['POST'])
@admin_required
def toggle_contract_status(customer_id):
    """
    Convert a customer to/from contract status.
    ---
    parameters:
      - in: path
        name: customer_id
        required: true
        schema:
          type: integer
      - in: body
        name: contract_info
        schema:
          type: object
          properties:
            has_contract:
              type: boolean
    responses:
      200:
        description: Contract status updated
    """
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        # Get customer info
        customer = conn.execute(
            "SELECT * FROM Customer WHERE customer_id = ?",
            (customer_id,)
        ).fetchone()
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        if data.get('has_contract', False):
            # Make them a contract customer
            # Generate account number if they don't have one
            if not customer['account_number']:
                # Get highest account number and add 1
                max_account = conn.execute(
                    "SELECT MAX(account_number) as max_num FROM Customer"
                ).fetchone()['max_num']
                
                account_number = (max_account or 1000) + 1
            else:
                account_number = customer['account_number']
            
            cursor.execute("""
                UPDATE Customer
                SET has_contract = 1, account_number = ?
                WHERE customer_id = ?
            """, (account_number, customer_id))
            
            message = f'Customer converted to contract account #{account_number}'
        else:
            # Remove contract status
            cursor.execute("""
                UPDATE Customer
                SET has_contract = 0
                WHERE customer_id = ?
            """, (customer_id,))
            
            message = 'Contract status removed'
        
        conn.commit()
        
        return jsonify({
            'message': message,
            'customer_id': customer_id,
            'has_contract': data.get('has_contract', False),
            'account_number': account_number if data.get('has_contract') else None
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
