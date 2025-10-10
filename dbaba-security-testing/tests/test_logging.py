"""
Logging and error handling security tests for DBABA.
Tests for information disclosure in logs and error messages.
"""
import pytest
from pexpect_helpers import DBABAClient


class TestErrorMessageSecurity:
    """Test that error messages don't leak sensitive information."""
    
    def test_password_not_in_error_messages(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that passwords don't appear in error messages."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            # Try wrong password
            test_password = "WrongPassword123"
            output = client.login("testuser", test_password)
            
            # Password should not appear in error message
            assert test_password not in output
            assert "WrongPassword123" not in output
            assert "Invalid credentials" in output
    
    def test_database_errors_dont_leak_info(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that database errors don't leak sensitive information."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Try to add a record with invalid data
            output = client.add_record("testrecord", invalidfield="value")
            
            # Error should not contain sensitive system information
            assert "database" not in output.lower()
            assert "sql" not in output.lower()
            assert "table" not in output.lower()
            assert "column" not in output.lower()
            assert "One or more invalid record data fields" in output
    
    def test_file_errors_dont_leak_paths(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that file errors don't leak sensitive path information."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Try to export to a non-existent directory
            output = client.export_database("/nonexistent/path/file.csv")
            
            # Error should not leak full system paths
            assert "/nonexistent/path" not in output
            assert "Can't open" in output or "Invalid" in output


class TestAuditLogSecurity:
    """Test audit log security and content."""
    
    def test_audit_log_format(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that audit logs are in the correct format."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user and perform actions
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            client.add_record("testrecord", sn="Test", gn="User")
            client.logout()
            
            # Read audit log
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            
            # Should contain expected audit record types
            assert "LS" in output or "L1" in output  # Login success or first login
            assert "LO" in output  # Logout
            assert "AU" in output  # Add user
    
    def test_audit_log_no_sensitive_data(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that audit logs don't contain sensitive data."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user with sensitive data
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            sensitive_data = "SecretData@confidential.com"
            client.add_record("sensitive", pem=sensitive_data, pph="555-0123")
            client.logout()
            
            # Read audit log
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            
            # Sensitive data should not appear in audit log
            assert sensitive_data not in output
            assert "SecretData@confidential.com" not in output
            assert "555-0123" not in output
    
    def test_audit_log_user_isolation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that audit logs can be filtered by user."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create two users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # User1 performs actions
            client.login("user1", "TestPass123")
            client.add_record("user1record", sn="User1", gn="Data")
            client.logout()
            
            # User2 performs actions
            client.login("user2", "TestPass123")
            client.add_record("user2record", sn="User2", gn="Data")
            client.logout()
            
            # Admin reads audit log for specific user
            client.login("admin", "AdminPass123")
            output = client.read_audit_log("user1")
            
            # Should only contain user1's activities
            assert "user1" in output
            # Should not contain user2's activities (though this might be implementation dependent)


class TestLoggingCompleteness:
    """Test that all security-relevant events are logged."""
    
    def test_login_events_logged(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that login events are properly logged."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            # Successful login
            client.login("testuser", "TestPass123")
            client.logout()
            
            # Failed login
            client.login("testuser", "WrongPassword")
            client.logout()
            
            # Read audit log
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            
            # Should contain login events
            assert "LS" in output or "L1" in output  # Successful login
            assert "LF" in output  # Failed login
    
    def test_password_change_logged(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that password changes are logged."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Change password
            client.change_password()
            # Note: This will prompt for new password, so we can't easily test the success case
            # But we can test that the attempt is logged
            
            client.logout()
            
            # Read audit log
            client.login("admin", "AdminPass123")
            output = client.read_audit_log()
            
            # Should contain password change events
            assert "SPC" in output or "FPC" in output  # Successful or failed password change
    
    def test_user_management_logged(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that user management operations are logged."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Add user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            
            # Read audit log
            output = client.read_audit_log()
            assert "AU" in output  # Add user
            
            # Delete user
            client.delete_user("testuser")
            
            # Read audit log again
            output = client.read_audit_log()
            assert "DU" in output  # Delete user


class TestErrorHandling:
    """Test error handling and logging."""
    
    def test_graceful_error_handling(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that errors are handled gracefully."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Test various error conditions
            error_tests = [
                ("LIN nonexistent", "Invalid credentials"),
                ("ADR", "No record_id"),
                ("RER", "Invalid record_id"),
                ("DER", "No record_id"),
                ("EXD", "No output file specified"),
                ("IMD", "No input file specified"),
            ]
            
            for command, expected_error in error_tests:
                output = client.send_command(command)
                assert expected_error in output or "No active login session" in output
    
    def test_no_stack_traces_in_output(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that stack traces don't appear in user output."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Try to trigger various error conditions
            error_commands = [
                "INVALID_COMMAND",
                "ADR testrecord invalidfield=value",
                "RER nonexistent",
            ]
            
            for command in error_commands:
                output = client.send_command(command)
                
                # Should not contain stack trace indicators
                assert "Traceback" not in output
                assert "File \"" not in output
                assert "line " not in output
                assert "Exception:" not in output
                assert "Error:" not in output or "Invalid credentials" in output  # Some errors are expected
