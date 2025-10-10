"""
Storage security tests for DBABA.
Tests for plaintext storage, file permissions, and data protection.
"""
import pytest
import os
import stat
from pathlib import Path
from pexpect_helpers import DBABAClient


class TestDataEncryption:
    """Test that sensitive data is not stored in plaintext."""
    
    def test_passwords_not_stored_in_plaintext(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that passwords are not stored in plaintext."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create users with specific passwords
            test_password = "SecretPassword123"
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", test_password)
            client.logout()
            
            # Check password file
            pw_file = dbaba_working_dir / "abapwfile"
            if pw_file.exists():
                with open(pw_file, 'r') as f:
                    content = f.read()
                    # Password should not appear in plaintext
                    assert test_password not in content
                    assert "SecretPassword123" not in content
                    # Should contain hashed data
                    assert ":" in content  # Format should be user:hash
    
    def test_confidential_information_not_in_audit_logs(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that confidential information is not leaked in audit logs."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user and add confidential data
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            confidential_data = "SecretEmail@confidential.com"
            client.add_record("confidential", pem=confidential_data, pph="555-0123", sa="123 Secret St")
            client.logout()
            
            # Check audit log
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            
            # Confidential data should not appear in audit logs
            assert confidential_data not in output
            assert "SecretEmail@confidential.com" not in output
            assert "555-0123" not in output
            assert "123 Secret St" not in output
    
    def test_database_file_encryption(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that database files contain encrypted/hashed data."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user and add sensitive data
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            sensitive_data = "VerySensitiveData@secret.com"
            client.add_record("sensitive", pem=sensitive_data, pph="555-9999", sa="999 Secret Lane")
            client.logout()
            
            # Check database file
            db_file = dbaba_working_dir / "dbadb-db"
            if db_file.exists():
                with open(db_file, 'rb') as f:
                    content = f.read()
                    # Sensitive data should not appear in plaintext
                    assert sensitive_data.encode() not in content
                    assert b"VerySensitiveData@secret.com" not in content
                    assert b"555-9999" not in content
                    assert b"999 Secret Lane" not in content


class TestFilePermissions:
    """Test file permissions and access controls."""
    
    def test_database_file_permissions(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that database files have appropriate permissions."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create some data to generate files
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            client.add_record("testrecord", sn="Test", gn="User")
            client.logout()
            
            # Check file permissions
            files_to_check = ["dbadb-db", "abapwfile", "abaaudit"]
            
            for filename in files_to_check:
                file_path = dbaba_working_dir / filename
                if file_path.exists():
                    file_stat = file_path.stat()
                    file_mode = stat.filemode(file_stat.st_mode)
                    
                    # File should not be world-readable
                    assert not (file_stat.st_mode & stat.S_IROTH), f"{filename} is world-readable"
                    # File should not be world-writable
                    assert not (file_stat.st_mode & stat.S_IWOTH), f"{filename} is world-writable"
                    # File should not be world-executable
                    assert not (file_stat.st_mode & stat.S_IXOTH), f"{filename} is world-executable"


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_record_integrity(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that records maintain integrity."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Add a record
            client.add_record("integritytest", sn="Integrity", gn="Test", pem="test@example.com")
            
            # Read the record back
            output = client.read_record("integritytest")
            assert "integritytest" in output
            assert "Integrity" in output
            assert "Test" in output
            assert "test@example.com" in output
            
            # Edit the record
            client.send_command("EDR integritytest sn=Modified")
            
            # Read again to verify change
            output = client.read_record("integritytest")
            assert "Modified" in output
            assert "Integrity" not in output
    
    def test_user_data_isolation_in_storage(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that user data is properly isolated in storage."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create two users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # User1 adds data
            client.login("user1", "TestPass123")
            client.add_record("user1data", sn="User1", gn="Data", pem="user1@example.com")
            client.logout()
            
            # User2 adds data
            client.login("user2", "TestPass123")
            client.add_record("user2data", sn="User2", gn="Data", pem="user2@example.com")
            client.logout()
            
            # User1 should only see their data
            client.login("user1", "TestPass123")
            output = client.read_all_records()
            assert "user1data" in output
            assert "user1@example.com" in output
            assert "user2data" not in output
            assert "user2@example.com" not in output
            client.logout()
            
            # User2 should only see their data
            client.login("user2", "TestPass123")
            output = client.read_all_records()
            assert "user2data" in output
            assert "user2@example.com" in output
            assert "user1data" not in output
            assert "user1@example.com" not in output


class TestDataCleanup:
    """Test data cleanup and deletion."""
    
    def test_user_deletion_removes_data(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that deleting a user removes all their data."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user and add data
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            client.add_record("testdata", sn="Test", gn="Data", pem="test@example.com")
            client.logout()
            
            # Delete the user
            client.login("admin", "AdminPass123")
            client.delete_user("testuser")
            
            # Try to login as deleted user
            client.logout()
            output = client.login("testuser", "TestPass123")
            assert "Invalid credentials" in output
    
    def test_record_deletion(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that record deletion works properly."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Add a record
            client.add_record("deletetest", sn="Delete", gn="Test")
            
            # Verify it exists
            output = client.read_record("deletetest")
            assert "deletetest" in output
            
            # Delete the record
            output = client.delete_record("deletetest")
            assert "OK" in output
            
            # Verify it's gone
            output = client.read_record("deletetest")
            assert "No record found" in output or "RecordID not found" in output
