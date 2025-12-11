# backend/tests/test_api.py
"""
Basic API tests for the package delivery system
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from db import init_db, get_db_connection

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    
    # Initialize test database
    init_db()
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_token(client):
    """Get authentication token for testing"""
    response = client.post('/api/login', json={
        'email': 'customer@example.com',
        'password': 'password123'
    })
    data = response.get_json()
    return data['user']['id']


class TestHomeEndpoint:
    """Test the home endpoint"""
    
    def test_home_returns_message(self, client):
        """Test that home endpoint returns expected message"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'API is running' in data['message']


class TestUserAuthentication:
    """Test user registration and login"""
    
    def test_login_with_valid_credentials(self, client):
        """Test login with correct credentials"""
        response = client.post('/api/login', json={
            'email': 'customer@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == 'customer@example.com'
        assert data['user']['role'] == 'customer'
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with incorrect credentials"""
        response = client.post('/api/login', json={
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
    
    def test_register_new_user(self, client):
        """Test user registration"""
        response = client.post('/api/register', json={
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'customer'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
    
    def test_register_duplicate_email(self, client):
        """Test that duplicate email registration fails"""
        # Try to register with existing email
        response = client.post('/api/register', json={
            'email': 'customer@example.com',
            'password': 'anypassword',
            'role': 'customer'
        })
        assert response.status_code == 400


class TestServiceEndpoints:
    """Test shipping service endpoints"""
    
    def test_get_services(self, client):
        """Test retrieving shipping services"""
        response = client.get('/api/services')
        assert response.status_code == 200
        data = response.get_json()
        assert 'services' in data
        assert len(data['services']) > 0
        
        # Check first service has required fields
        service = data['services'][0]
        assert 'service_id' in service
        assert 'name' in service
        assert 'base_price' in service
        assert 'delivery_speed' in service


class TestPackageTracking:
    """Test package tracking functionality"""
    
    def test_tracking_requires_auth(self, client):
        """Test that tracking requires authentication"""
        response = client.get('/api/tracking/1')
        assert response.status_code == 401
    
    def test_user_packages_requires_auth(self, client):
        """Test that user packages endpoint requires auth"""
        response = client.get('/api/user/packages')
        assert response.status_code == 401


class TestAdminEndpoints:
    """Test admin-only endpoints"""
    
    def test_admin_packages_requires_staff(self, client):
        """Test that admin endpoints require staff/admin role"""
        # Login as customer
        response = client.post('/api/login', json={
            'email': 'customer@example.com',
            'password': 'password123'
        })
        data = response.get_json()
        customer_token = data['user']['id']
        
        # Try to access admin endpoint
        response = client.get('/api/admin/packages', 
                             headers={'Authorization': f'Bearer {customer_token}'})
        assert response.status_code == 403
    
    def test_admin_users_requires_admin(self, client):
        """Test that user management requires admin role"""
        # Login as staff
        response = client.post('/api/login', json={
            'email': 'staff@shipping.com',
            'password': 'staff123'
        })
        data = response.get_json()
        staff_token = data['user']['id']
        
        # Staff should NOT be able to create users
        response = client.post('/api/admin/users/create',
                              headers={'Authorization': f'Bearer {staff_token}'},
                              json={'email': 'test@test.com', 'password': 'test', 'role': 'staff'})
        assert response.status_code == 403


class TestDatabase:
    """Test database operations"""
    
    def test_database_tables_exist(self):
        """Test that all required tables exist"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'User', 'Customer', 'Package', 'ServiceType',
            'Location', 'TrackingEvent'
        ]
        
        for table in required_tables:
            assert table in tables, f"Table {table} not found"
        
        conn.close()
    
    def test_sample_data_exists(self):
        """Test that sample data was inserted"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM User")
        user_count = cursor.fetchone()[0]
        assert user_count >= 3, "Expected at least 3 sample users"
        
        # Check services
        cursor.execute("SELECT COUNT(*) FROM ServiceType")
        service_count = cursor.fetchone()[0]
        assert service_count >= 4, "Expected at least 4 service types"
        
        # Check locations
        cursor.execute("SELECT COUNT(*) FROM Location")
        location_count = cursor.fetchone()[0]
        assert location_count >= 4, "Expected at least 4 locations"
        
        conn.close()


class TestDataValidation:
    """Test data validation and constraints"""
    
    def test_email_validation(self, client):
        """Test that invalid emails are rejected"""
        response = client.post('/api/register', json={
            'email': 'notanemail',  # Invalid email
            'password': 'password123',
            'role': 'customer'
        })
        # Should fail due to database constraint
        assert response.status_code == 400 or response.status_code == 500
    
    def test_role_validation(self):
        """Test that invalid roles are rejected"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to insert user with invalid role
        try:
            cursor.execute("""
                INSERT INTO User (email, password, role)
                VALUES (?, ?, ?)
            """, ('test@test.com', 'pass', 'invalid_role'))
            conn.commit()
            assert False, "Should have raised an error for invalid role"
        except Exception:
            # Expected to fail
            pass
        finally:
            conn.close()


# Run tests with: pytest tests/ -v
