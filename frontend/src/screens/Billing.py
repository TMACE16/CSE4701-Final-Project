# backend/billing.py
"""
billing.py - Billing and invoice routes
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from db import get_db_connection
from datetime import datetime

billing_routes = Blueprint('billing_routes', __name__)

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


@billing_routes.route('/billing/statements', methods=['GET'])
@login_required
def get_billing_statements():
    """
    Get all billing statements for a contract customer.
    ---
    responses:
      200:
        description: List of billing statements
      403:
        description: Not a contract customer
    """
    conn = get_db_connection()
    
    try:
        # Check if user has a contract
        customer = conn.execute("""
            SELECT customer_id, has_contract, account_number
            FROM Customer
            WHERE user_id = ?
        """, (request.user_id,)).fetchone()
        
        if not customer:
            return jsonify({'error': 'Customer profile not found'}), 404
        
        if not customer['has_contract']:
            return jsonify({'error': 'Only contract customers have billing statements'}), 403
        
        # Get all statements
        statements = conn.execute("""
            SELECT *
            FROM BillingStatement
            WHERE customer_id = ?
            ORDER BY statement_month DESC
        """, (customer['customer_id'],)).fetchall()
        
        return jsonify({
            'account_number': customer['account_number'],
            'statements': [
                {
                    'statement_id': s['statement_id'],
                    'statement_month': s['statement_month'],
                    'total_amount': s['total_amount'],
                    'status': s['status']
                }
                for s in statements
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@billing_routes.route('/billing/statements/<int:statement_id>', methods=['GET'])
@login_required
def get_statement_details(statement_id):
    """
    Get detailed information for a specific billing statement.
    ---
    parameters:
      - in: path
        name: statement_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Statement details with packages
      403:
        description: Unauthorized
    """
    conn = get_db_connection()
    
    try:
        # Get customer
        customer = conn.execute("""
            SELECT customer_id
            FROM Customer
            WHERE user_id = ?
        """, (request.user_id,)).fetchone()
        
        if not customer:
            return jsonify({'error': 'Customer profile not found'}), 404
        
        # Get statement
        statement = conn.execute("""
            SELECT *
            FROM BillingStatement
            WHERE statement_id = ? AND customer_id = ?
        """, (statement_id, customer['customer_id'])).fetchone()
        
        if not statement:
            return jsonify({'error': 'Statement not found or unauthorized'}), 403
        
        # Get packages in this statement
        packages = conn.execute("""
            SELECT 
                p.package_id,
                p.recipient_name,
                p.recipient_city,
                p.recipient_state,
                p.date_shipped,
                p.weight_lb,
                st.name as service_name,
                st.base_price as cost
            FROM Package p
            JOIN ServiceType st ON p.service_id = st.service_id
            JOIN StatementPackage sp ON p.package_id = sp.package_id
            WHERE sp.statement_id = ?
            ORDER BY p.date_shipped DESC
        """, (statement_id,)).fetchall()
        
        return jsonify({
            'statement': {
                'statement_id': statement['statement_id'],
                'statement_month': statement['statement_month'],
                'total_amount': statement['total_amount'],
                'status': statement['status']
            },
            'packages': [
                {
                    'tracking_number': p['package_id'],
                    'recipient_name': p['recipient_name'],
                    'recipient_location': f"{p['recipient_city']}, {p['recipient_state']}",
                    'date_shipped': p['date_shipped'],
                    'weight': p['weight_lb'],
                    'service': p['service_name'],
                    'cost': p['cost']
                }
                for p in packages
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@billing_routes.route('/billing/payment-history', methods=['GET'])
@login_required
def get_payment_history():
    """
    Get payment history for the customer.
    ---
    responses:
      200:
        description: List of payments
    """
    conn = get_db_connection()
    
    try:
        customer = conn.execute("""
            SELECT customer_id
            FROM Customer
            WHERE user_id = ?
        """, (request.user_id,)).fetchone()
        
        if not customer:
            return jsonify({'error': 'Customer profile not found'}), 404
        
        payments = conn.execute("""
            SELECT 
                payment_id,
                date_paid,
                amount,
                method,
                package_id
            FROM Payment
            WHERE customer_id = ?
            ORDER BY date_paid DESC
        """, (customer['customer_id'],)).fetchall()
        
        return jsonify({
            'payments': [
                {
                    'payment_id': p['payment_id'],
                    'date_paid': p['date_paid'],
                    'amount': p['amount'],
                    'method': p['method'],
                    'tracking_number': p['package_id']
                }
                for p in payments
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@billing_routes.route('/billing/make-payment', methods=['POST'])
@login_required
def make_payment():
    """
    Process a payment (simplified - would integrate with payment gateway).
    ---
    parameters:
      - in: body
        name: payment
        required: true
        schema:
          type: object
          required:
            - amount
            - method
          properties:
            amount:
              type: number
            method:
              type: string
              enum: [credit_card, account]
            statement_id:
              type: integer
    responses:
      201:
        description: Payment processed
    """
    data = request.get_json()
    conn = get_db_connection()
    
    try:
        customer = conn.execute("""
            SELECT customer_id
            FROM Customer
            WHERE user_id = ?
        """, (request.user_id,)).fetchone()
        
        if not customer:
            return jsonify({'error': 'Customer profile not found'}), 404
        
        cursor = conn.cursor()
        
        # Record payment
        cursor.execute("""
            INSERT INTO Payment (customer_id, date_paid, amount, method)
            VALUES (?, ?, ?, ?)
        """, (
            customer['customer_id'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data['amount'],
            data['method']
        ))
        
        # If paying a statement, update its status
        if 'statement_id' in data:
            cursor.execute("""
                UPDATE BillingStatement
                SET status = 'paid'
                WHERE statement_id = ?
            """, (data['statement_id'],))
        
        conn.commit()
        
        return jsonify({
            'message': 'Payment processed successfully',
            'payment_id': cursor.lastrowid
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
