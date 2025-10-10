"""
Privacy and access control tests for DBABA.
Tests SR-4 (access rights) and SR-5 (sensitive information protection).
"""
import pytest
from pexpect_helpers import DBABAClient


class TestRoleBasedAccessControl:
    """Test SR-4: Access rights and role-based access control."""
    
    def test_admin_cannot_add_records(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that admin cannot add address book records."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Login as admin
            client.login("admin", "AdminPass123")
            
            # Try to add a record
            output = client.add_record("testrecord", sn="Test", gn="User")
            assert "Admin not authorized" in output
    
    def test_admin_cannot_read_records(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that admin cannot read address book records."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Login as admin
            client.login("admin", "AdminPass123")
            
            # Try to read records
            output = client.read_record("testrecord")
            assert "Admin not authorized" in output
            
            output = client.read_all_records()
            assert "Admin not authorized" in output
    
    def test_admin_cannot_export_import(self, dbaba_path, dbaba_working_dir, clean_dbaba_state, temp_dir):
        """Test that admin cannot export or import records."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Login as admin
            client.login("admin", "AdminPass123")
            
            # Try to export
            output = client.export_database(str(temp_dir / "test.csv"))
            assert "Admin not authorized" in output
            
            # Try to import
            output = client.import_database(str(temp_dir / "test.csv"))
            assert "Admin not authorized" in output
    
    def test_regular_user_can_manage_records(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that regular users can manage their own records."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create and login as regular user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Add a record
            output = client.add_record("testrecord", sn="Test", gn="User", pem="test@example.com")
            assert "OK" in output
            
            # Read the record
            output = client.read_record("testrecord")
            assert "testrecord" in output
            assert "Test" in output
            assert "User" in output
    
    def test_user_cannot_access_other_user_records(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that users cannot access other users' records."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create two users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # User1 adds a record
            client.login("user1", "TestPass123")
            client.add_record("secretrecord", sn="Secret", gn="Data", pem="secret@example.com")
            client.logout()
            
            # User2 tries to read User1's record
            client.login("user2", "TestPass123")
            output = client.read_record("secretrecord")
            assert "No record found" in output or "RecordID not found" in output


class TestSensitiveInformationProtection:
    """Test SR-5: Sensitive information protection."""
    
    def test_admin_cannot_read_confidential_information(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that admin cannot read users' confidential information."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user and add confidential information
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            # Add record with confidential information
            client.add_record("confidential", 
                            sn="Confidential", 
                            gn="Data", 
                            pem="confidential@example.com",
                            pph="555-0123",
                            sa="123 Secret St",
                            city="Secret City")
            client.logout()
            
            # Admin tries to read confidential information
            client.login("admin", "AdminPass123")
            
            # Admin should not be able to read records at all
            output = client.read_record("confidential")
            assert "Admin not authorized" in output
    
    def test_audit_log_protection(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that audit logs are protected and only accessible by admin."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            # User performs some actions to generate audit logs
            client.login("testuser", "TestPass123")
            client.add_record("testrecord", sn="Test", gn="User")
            client.logout()
            
            # User tries to read audit log
            client.login("testuser", "TestPass123")
            output = client.read_audit_log()
            assert "Admin not active" in output
            
            # Admin can read audit log
            client.logout()
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            assert "OK" in output or "LS" in output or "LO" in output
    
    def test_password_not_exposed_in_logs(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that passwords are not exposed in audit logs."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user with a specific password
            test_password = "SecretPassword123"
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            # Login with the password
            client.login("testuser", test_password)
            client.logout()
            
            # Admin reads audit log
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            
            # Password should not appear in audit log
            assert test_password not in output
            assert "SecretPassword123" not in output


class TestDataIsolation:
    """Test data isolation between users."""
    
    def test_user_data_isolation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that user data is properly isolated."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create two users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # User1 adds records
            client.login("user1", "TestPass123")
            client.add_record("user1record", sn="User1", gn="Data")
            client.add_record("sharedname", sn="Shared", gn="Name1")
            client.logout()
            
            # User2 adds records with same record ID
            client.login("user2", "TestPass123")
            client.add_record("user2record", sn="User2", gn="Data")
            client.add_record("sharedname", sn="Shared", gn="Name2")
            client.logout()
            
            # User1 should only see their records
            client.login("user1", "TestPass123")
            output = client.read_all_records()
            assert "user1record" in output
            assert "sharedname" in output
            assert "Name1" in output
            assert "user2record" not in output
            assert "Name2" not in output
            client.logout()
            
            # User2 should only see their records
            client.login("user2", "TestPass123")
            output = client.read_all_records()
            assert "user2record" in output
            assert "sharedname" in output
            assert "Name2" in output
            assert "user1record" not in output
            assert "Name1" not in output
