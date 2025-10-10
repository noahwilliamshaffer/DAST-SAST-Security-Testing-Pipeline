"""
Test for the LIN elevation bug (extra credit).
This test attempts to reproduce the bug where any user can access other accounts.
"""
import pytest
from pexpect_helpers import DBABAClient


class TestLINElevationBug:
    """Test for the LIN command elevation bug."""
    
    def test_lin_elevation_bug(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """
        Test for the LIN elevation bug where any user can access other accounts.
        
        This is the extra credit test case mentioned in the assignment.
        The bug allows a user to access other accounts by manipulating the LIN command.
        """
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create multiple users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # Set up user1 with some data
            client.login("user1", "TestPass123")
            client.add_record("user1secret", sn="User1", gn="Secret", pem="user1@secret.com")
            client.logout()
            
            # Set up user2 with some data
            client.login("user2", "TestPass123")
            client.add_record("user2secret", sn="User2", gn="Secret", pem="user2@secret.com")
            client.logout()
            
            # Now try to exploit the LIN bug
            # The bug might be related to how the LIN command handles parameters
            # Let's try various approaches to access other accounts
            
            # Approach 1: Try to login as user1 but with user2's session
            client.login("user2", "TestPass123")
            
            # Try to access user1's data while logged in as user2
            # This should fail if the system is secure
            output = client.read_record("user1secret")
            if "user1secret" in output and "User1" in output:
                # This would indicate the bug - user2 can access user1's data
                print("POTENTIAL BUG DETECTED: User2 can access User1's records")
                assert False, "LIN elevation bug detected: User2 accessed User1's data"
            else:
                # This is expected - user2 should not access user1's data
                assert "No record found" in output or "RecordID not found" in output
            
            client.logout()
            
            # Approach 2: Try to manipulate the LIN command parameters
            # The bug might be in how the LIN command processes the userID parameter
            client.login("user1", "TestPass123")
            
            # Try various LIN command manipulations
            lin_manipulations = [
                "LIN user2",  # Try to login as user2 while user1 is active
                "LIN admin",  # Try to login as admin while user1 is active
                "LIN user1 user2",  # Try to pass multiple parameters
                "LIN user1; user2",  # Try command chaining
            ]
            
            for manipulation in lin_manipulations:
                output = client.send_command(manipulation)
                
                # Check if the manipulation succeeded in switching users
                if "OK" in output and "Enter your password:" in output:
                    # If we get a password prompt for another user, that's suspicious
                    print(f"POTENTIAL BUG: LIN command accepted manipulation: {manipulation}")
                    print(f"Output: {output}")
                
                # Check if we can access other users' data after the manipulation
                output = client.read_record("user2secret")
                if "user2secret" in output and "User2" in output:
                    print("POTENTIAL BUG DETECTED: User1 can access User2's records after LIN manipulation")
                    assert False, "LIN elevation bug detected: User1 accessed User2's data"
    
    def test_lin_parameter_manipulation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test various parameter manipulations in the LIN command."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # Test various LIN parameter manipulations
            manipulations = [
                ("LIN user1 user2", "Multiple parameters"),
                ("LIN 'user1' 'user2'", "Quoted multiple parameters"),
                ("LIN user1,user2", "Comma-separated parameters"),
                ("LIN user1|user2", "Pipe-separated parameters"),
                ("LIN user1&user2", "Ampersand-separated parameters"),
                ("LIN user1 user2 admin", "Multiple user parameters"),
                ("LIN user1;LIN user2", "Command chaining"),
                ("LIN user1 && LIN user2", "Logical AND chaining"),
                ("LIN user1 || LIN user2", "Logical OR chaining"),
            ]
            
            for manipulation, description in manipulations:
                output = client.send_command(manipulation)
                print(f"Testing {description}: {manipulation}")
                print(f"Output: {output}")
                
                # Check if any manipulation succeeded in unexpected ways
                if "OK" in output and ("user1" in output or "user2" in output):
                    print(f"POTENTIAL BUG: {description} succeeded unexpectedly")
    
    def test_lin_with_special_characters(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test LIN command with special characters that might trigger the bug."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # Test special character manipulations
            special_tests = [
                "LIN user1\x00user2",  # Null byte injection
                "LIN user1\nuser2",    # Newline injection
                "LIN user1\tuser2",    # Tab injection
                "LIN user1\ruser2",    # Carriage return injection
                "LIN user1 user2\x00", # Null byte at end
                "LIN user1\x00",       # Null byte in middle
            ]
            
            for test in special_tests:
                try:
                    output = client.send_command(test)
                    print(f"Special character test: {repr(test)}")
                    print(f"Output: {output}")
                    
                    # Check for unexpected behavior
                    if "OK" in output and ("user1" in output or "user2" in output):
                        print(f"POTENTIAL BUG: Special character manipulation succeeded: {repr(test)}")
                except Exception as e:
                    print(f"Exception with special character test {repr(test)}: {e}")
    
    def test_lin_buffer_overflow(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test for potential buffer overflow in LIN command."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.logout()
            
            # Test very long usernames
            long_usernames = [
                "a" * 1000,  # Very long username
                "user1" + "a" * 1000,  # Username with prefix
                "a" * 1000 + "user1",  # Username with suffix
            ]
            
            for long_username in long_usernames:
                try:
                    output = client.send_command(f"LIN {long_username}")
                    print(f"Long username test: {len(long_username)} characters")
                    print(f"Output: {output}")
                    
                    # Check if the system handled it gracefully
                    if "Invalid userID" not in output and "Invalid credentials" not in output:
                        print(f"POTENTIAL BUG: Long username not properly rejected: {len(long_username)} chars")
                except Exception as e:
                    print(f"Exception with long username test: {e}")
    
    def test_lin_race_condition(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test for race conditions in LIN command."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # Try rapid successive LIN commands
            rapid_commands = [
                "LIN user1",
                "LIN user2", 
                "LIN admin",
                "LIN user1",
            ]
            
            for cmd in rapid_commands:
                output = client.send_command(cmd)
                print(f"Rapid command: {cmd}")
                print(f"Output: {output}")
                
                # Check for unexpected state changes
                if "OK" in output and "Enter your password:" in output:
                    print(f"POTENTIAL BUG: Rapid LIN commands caused unexpected state change")
    
    def test_lin_with_whitespace_manipulation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test LIN command with various whitespace manipulations."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # Test whitespace manipulations
            whitespace_tests = [
                "LIN  user1",      # Extra space
                "LIN user1 ",      # Trailing space
                "LIN  user1  ",    # Multiple spaces
                "LIN\tuser1",      # Tab instead of space
                "LIN\nuser1",      # Newline instead of space
                "LIN\ruser1",      # Carriage return instead of space
                "LIN user1\tuser2", # Tab-separated users
                "LIN user1\nuser2", # Newline-separated users
            ]
            
            for test in whitespace_tests:
                output = client.send_command(test)
                print(f"Whitespace test: {repr(test)}")
                print(f"Output: {output}")
                
                # Check for unexpected behavior
                if "OK" in output and ("user1" in output or "user2" in output):
                    print(f"POTENTIAL BUG: Whitespace manipulation succeeded: {repr(test)}")
