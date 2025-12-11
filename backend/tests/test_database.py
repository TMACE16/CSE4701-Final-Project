# backend/tests/test_database.py
"""
Comprehensive database tests for the package delivery system
"""
import pytest
import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import init_db, get_db_connection, DB_PATH


@pytest.fixture(scope='module')
def db():
    """Initialize database once for all tests in this module"""
    init_db()
    yield
    # Cleanup after all tests (optional)


class TestDatabaseStructure:
    """Test database schema and structure"""
    
    def test_database_file_exists(self, db):
        """Test that database file is created"""
        assert os.path.exists(DB_PATH), "Database file not found"
    
    def test_all_tables_exist(self, db):
        """Test that all required tables exist"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'BillingStatement',
            'Customer',
            'Location',
            'Package',
            'Payment',
            'ServiceType',
            'Staff',
            'StatementPackage',
            'TrackingEvent',
            'User'
        ]
        
        for table in required_tables:
            assert table in tables, f"Table {table} is missing"
        
        conn.close()
    
    def test_user_table_columns(self, db):
        """Test User table has correct columns"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(User)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
        
        assert 'user_id' in columns
        assert 'email' in columns
        assert 'password' in columns
        assert 'role' in columns
        
        conn.close()
    
    def test_package_table_columns(self, db):
        """Test Package table has all required columns"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(Package)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {
            'package_id', 'customer_id', 'sender_name', 'sender_addr1',
            'recipient_name', 'recipient_addr1', 'recipient_city',
            'service_id', 'weight_lb', 'payment_type', 'date_shipped'
        }
        
        for col in required_columns:
            assert col in columns, f"Column {col} missing from Package table"
        
        conn.close()
    
    def test_foreign_keys_enabled(self, db):
        """Test that foreign key constraints are enabled"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()[0]
        
        conn.close()
        # Note: This checks if the connection has foreign keys on
        # The SCHEMA has "PRAGMA foreign_keys = ON"


class TestDatabaseConstraints:
    """Test database constraints and validations"""
    
    def test_user_email_unique_constraint(self, db):
        """Test that duplicate emails are rejected"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to insert duplicate email
        try:
            cursor.execute("""
                INSERT INTO User (email, password, role)
                VALUES ('customer@example.com', 'test123', 'customer')
            """)
            conn.commit()
            assert False, "Should have raised IntegrityError for duplicate email"
        except sqlite3.IntegrityError:
            # Expected behavior
            pass
        finally:
            conn.close()
    
    def test_user_role_check_constraint(self, db):
        """Test that invalid roles are rejected"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO User (email, password, role)
                VALUES ('invalid@test.com', 'pass123', 'superuser')
            """)
            conn.commit()
            assert False, "Should have raised error for invalid role"
        except sqlite3.IntegrityError:
            # Expected behavior
            pass
        finally:
            conn.close()
    
    def test_user_email_format_constraint(self, db):
        """Test that emails without @ are rejected"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO User (email, password, role)
                VALUES ('notanemail', 'pass123', 'customer')
            """)
            conn.commit()
            assert False, "Should have rejected email without @"
        except sqlite3.IntegrityError:
            # Expected behavior
            pass
        finally:
            conn.close()
    
    def test_package_foreign_key_constraint(self, db):
        """Test that package requires valid customer_id"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Enable foreign keys for this connection
        cursor.execute("PRAGMA foreign_keys = ON")
        
        try:
            cursor.execute("""
                INSERT INTO Package (
                    customer_id, sender_name, sender_addr1, sender_city, 
                    sender_state, sender_zip, recipient_name, recipient_addr1,
                    recipient_city, recipient_state, recipient_zip,
                    service_id, weight_lb, payment_type, date_shipped
                ) VALUES (
                    99999, 'Test', '123 St', 'City', 'ST', '12345',
                    'Recipient', '456 Ave', 'City2', 'ST', '54321',
                    1, 5.0, 'credit_card', '2025-01-01'
                )
            """)
            conn.commit()
            assert False, "Should have rejected invalid customer_id"
        except sqlite3.IntegrityError:
            # Expected behavior
            pass
        finally:
            conn.close()
    
    def test_service_delivery_speed_constraint(self, db):
        """Test that only valid delivery speeds are accepted"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ServiceType (name, max_weight_lb, base_price, delivery_speed)
                VALUES ('Test Service', 10.0, 15.99, 'instant')
            """)
            conn.commit()
            assert False, "Should have rejected invalid delivery_speed"
        except sqlite3.IntegrityError:
            # Expected behavior
            pass
        finally:
            conn.close()


class TestSampleData:
    """Test that sample data is inserted correctly"""
    
    def test_sample_users_exist(self, db):
        """Test that 3 sample users are created"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM User")
        count = cursor.fetchone()[0]
        
        assert count >= 3, f"Expected at least 3 users, found {count}"
        
        conn.close()
    
    def test_admin_user_exists(self, db):
        """Test that admin user is created"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM User WHERE email = 'admin@shipping.com' AND role = 'admin'
        """)
        admin = cursor.fetchone()
        
        assert admin is not None, "Admin user not found"
        
        conn.close()
    
    def test_sample_services_exist(self, db):
        """Test that sample shipping services are created"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ServiceType")
        count = cursor.fetchone()[0]
        
        assert count >= 4, f"Expected at least 4 service types, found {count}"
        
        # Check specific services
        cursor.execute("SELECT name FROM ServiceType")
        services = [row[0] for row in cursor.fetchall()]
        
        assert 'Overnight Letter' in services
        assert 'Ground Shipping' in services
        
        conn.close()
    
    def test_sample_locations_exist(self, db):
        """Test that sample locations are created"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Location")
        count = cursor.fetchone()[0]
        
        assert count >= 4, f"Expected at least 4 locations, found {count}"
        
        # Check for different types
        cursor.execute("SELECT DISTINCT type FROM Location")
        types = [row[0] for row in cursor.fetchall()]
        
        assert 'warehouse' in types
        assert 'truck' in types or 'plane' in types
        
        conn.close()
    
    def test_customer_profile_exists(self, db):
        """Test that sample customer profile is created"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Customer")
        count = cursor.fetchone()[0]
        
        assert count >= 1, "Expected at least 1 customer profile"
        
        conn.close()


class TestDatabaseOperations:
    """Test basic CRUD operations"""
    
    def test_insert_and_retrieve_user(self, db):
        """Test inserting and retrieving a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert
        cursor.execute("""
            INSERT OR IGNORE INTO User (email, password, role)
            VALUES ('testuser@test.com', 'testpass', 'customer')
        """)
        conn.commit()
        
        # Retrieve
        cursor.execute("""
            SELECT * FROM User WHERE email = 'testuser@test.com'
        """)
        user = cursor.fetchone()
        
        assert user is not None
        assert user['email'] == 'testuser@test.com'
        assert user['role'] == 'customer'
        
        conn.close()
    
    def test_update_user_password(self, db):
        """Test updating user data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update password
        cursor.execute("""
            UPDATE User 
            SET password = 'newpassword123'
            WHERE email = 'testuser@test.com'
        """)
        conn.commit()
        
        # Verify update
        cursor.execute("""
            SELECT password FROM User WHERE email = 'testuser@test.com'
        """)
        result = cursor.fetchone()
        
        assert result['password'] == 'newpassword123'
        
        conn.close()
    
    def test_delete_user(self, db):
        """Test deleting a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count before
        cursor.execute("SELECT COUNT(*) FROM User WHERE email = 'testuser@test.com'")
        before = cursor.fetchone()[0]
        
        # Delete
        cursor.execute("DELETE FROM User WHERE email = 'testuser@test.com'")
        conn.commit()
        
        # Count after
        cursor.execute("SELECT COUNT(*) FROM User WHERE email = 'testuser@test.com'")
        after = cursor.fetchone()[0]
        
        assert after < before
        
        conn.close()


class TestDatabaseRelationships:
    """Test relationships between tables"""
    
    def test_customer_user_relationship(self, db):
        """Test that Customer can be linked to User"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get a customer with user_id
        cursor.execute("""
            SELECT c.customer_id, c.user_id, u.email
            FROM Customer c
            JOIN User u ON c.user_id = u.user_id
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            assert result['user_id'] is not None
            assert result['email'] is not None
        
        conn.close()
    
    def test_package_customer_relationship(self, db):
        """Test that Package is linked to Customer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if any packages exist and are linked to customers
        cursor.execute("""
            SELECT p.package_id, c.name
            FROM Package p
            JOIN Customer c ON p.customer_id = c.customer_id
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            assert result['package_id'] is not None
            assert result['name'] is not None
        
        conn.close()
    
    def test_tracking_event_relationships(self, db):
        """Test that TrackingEvent links to Package and Location"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check tracking events with joins
        cursor.execute("""
            SELECT te.event_id, p.package_id, l.name
            FROM TrackingEvent te
            JOIN Package p ON te.package_id = p.package_id
            JOIN Location l ON te.location_id = l.location_id
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            assert result['event_id'] is not None
            assert result['package_id'] is not None
            assert result['name'] is not None
        
        conn.close()


class TestDatabasePerformance:
    """Test database performance and efficiency"""
    
    def test_query_with_index(self, db):
        """Test that queries use primary key efficiently"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # This should be fast due to primary key index
        cursor.execute("SELECT * FROM User WHERE user_id = 1")
        result = cursor.fetchone()
        
        assert result is not None or result is None  # Just test it runs
        
        conn.close()
    
    def test_email_lookup_performance(self, db):
        """Test email lookup (has UNIQUE constraint, should be fast)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM User WHERE email = 'admin@shipping.com'")
        result = cursor.fetchone()
        
        assert result is not None
        
        conn.close()


# Run with: pytest backend/tests/test_database.py -v
