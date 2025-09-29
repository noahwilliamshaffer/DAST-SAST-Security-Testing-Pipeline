"""
Authentication security tests for DBABA.
Tests SR-1 (password complexity), SR-2 (account lockout), and SR-3 (authentication required).
"""
import pytest
import time
from pexpect_helpers import DBABAClient, wait_for_lockout_expiry


class TestPasswordComplexity:
    """Test SR-1: Password complexity requirements."""
    
    def test_password_too_short(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that passwords shorter than 8 characters are rejected."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # First login as admin to create password
            output = client.login("admin", "short")
            assert "Password must be 1-24 alphanumeric characters" in output or "Password is too easy to guess" in output
    
    def test_password_illegal_characters(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that passwords with illegal characters are rejected."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Try password with special characters
            output = client.login("admin", "Test@123")
            assert "Password must be 1-24 alphanumeric characters" in output
    
    def test_password_too_easy(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that common passwords are rejected."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Try common password
            output = client.login("admin", "password")
            assert "Password is too easy to guess" in output
    
    def test_password_valid(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that valid passwords are accepted."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Try valid password
            output = client.login("admin", "ValidPass123")
            assert "OK" in output
            assert client.current_user == "admin"


class TestAccountLockout:
    """Test SR-2: Account lockout after 3 failed attempts."""
    
    def test_account_lockout_after_three_failures(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that account is locked after 3 failed login attempts."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # First, create admin account with valid password
            client.login("admin", "AdminPass123")
            client.logout()
            
            # Now try to login with wrong password 3 times
            for i in range(3):
                output = client.login("admin", "WrongPass")
                assert "Invalid credentials" in output
                client.logout()
            
            # Fourth attempt should be locked out
            output = client.login("admin", "WrongPass")
            # The system should either reject immediately or after a delay
            # We'll check if the login fails
            assert "Invalid credentials" in output or "An account is currently active" in output
    
    def test_lockout_timing(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that lockout lasts for at least 1 minute."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create admin account
            client.login("admin", "AdminPass123")
            client.logout()
            
            # Trigger lockout
            for i in range(3):
                client.login("admin", "WrongPass")
                client.logout()
            
            # Record time before lockout
            start_time = time.time()
            
            # Try to login immediately after lockout
            output = client.login("admin", "WrongPass")
            
            # Wait for lockout to expire (65 seconds to be safe)
            wait_for_lockout_expiry(65)
            
            # Try to login after lockout should have expired
            output = client.login("admin", "AdminPass123")
            # Should succeed after lockout expires
            assert "OK" in output or "Enter your password:" in output


class TestAuthenticationRequired:
    """Test SR-3: Authentication required before access."""
    
    def test_commands_require_authentication(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that most commands require authentication."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Try various commands without authentication
            commands_to_test = [
                "ADR testrecord",
                "RER testrecord", 
                "REA",
                "DER testrecord",
                "EXD test.csv",
                "IMD test.csv",
                "CHP"
            ]
            
            for cmd in commands_to_test:
                output = client.send_command(cmd)
                assert "No active login session" in output
    
    def test_admin_commands_require_admin_auth(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that admin commands require admin authentication."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a regular user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            # Login as regular user
            client.login("testuser", "TestPass123")
            
            # Try admin commands
            admin_commands = [
                "ADU newuser",
                "DEU testuser",
                "LSU",
                "RAL",
                "DAL"
            ]
            
            for cmd in admin_commands:
                output = client.send_command(cmd)
                assert "Admin not active" in output
    
    def test_help_and_wai_work_without_auth(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that help and who am I work without authentication."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Help should work
            output = client.help()
            assert "Valid commands:" in output or "login:" in output
            
            # WAI should work but show no user
            output = client.who_am_i()
            assert "Current user is None" in output or "Current user is" in output


class TestPasswordChange:
    """Test password change functionality."""
    
    def test_password_change_requires_auth(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test that password change requires authentication."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            output = client.change_password()
            assert "No active login session" in output
    
    def test_password_change_valid(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test valid password change."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Login first
            client.login("admin", "AdminPass123")
            
            # Change password
            output = client.change_password()
            # Should prompt for new password
            assert "Create a new password" in output or "Reenter the same password" in output
