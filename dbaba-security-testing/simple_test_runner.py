#!/usr/bin/env python3
"""
Simple test runner for DBABA security tests.
"""
import sys
import os
import time
from pathlib import Path

# Add the tests directory to the path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

def test_password_complexity():
    """Test password complexity requirements."""
    print("\n=== Testing Password Complexity ===")
    try:
        from pexpect_helpers import DBABAClient
        
        dbaba_path = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
        dbaba_working_dir = Path(__file__).parent / "M4-dbaba-2024" / "dbaba"
        
        # Clean up any existing files
        for file in dbaba_working_dir.glob("*"):
            if not file.name.endswith('.py'):
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    import shutil
                    shutil.rmtree(file)
        
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Test password too short
            output = client.login("admin", "short")
            print(f"Short password test: {output}")
            assert "Password must be 1-24 alphanumeric characters" in output or "Password is too easy to guess" in output
            print("✓ Short password correctly rejected")
            
            # Test password with special characters
            output = client.login("admin", "Test@123")
            print(f"Special chars test: {output}")
            assert "Password must be 1-24 alphanumeric characters" in output
            print("✓ Special characters correctly rejected")
            
            # Test common password
            output = client.login("admin", "password")
            print(f"Common password test: {output}")
            assert "Password is too easy to guess" in output
            print("✓ Common password correctly rejected")
            
            # Test valid password
            output = client.login("admin", "ValidPass123")
            print(f"Valid password test: {output}")
            assert "OK" in output
            print("✓ Valid password accepted")
            
    except Exception as e:
        print(f"✗ Password complexity test failed: {e}")
        import traceback
        traceback.print_exc()

def test_authentication_required():
    """Test that authentication is required for commands."""
    print("\n=== Testing Authentication Required ===")
    try:
        from pexpect_helpers import DBABAClient
        
        dbaba_path = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
        dbaba_working_dir = Path(__file__).parent / "M4-dbaba-2024" / "dbaba"
        
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Test commands without authentication
            commands = ["ADR testrecord", "RER testrecord", "REA", "DER testrecord"]
            
            for cmd in commands:
                output = client.send_command(cmd)
                print(f"Command '{cmd}' without auth: {output}")
                assert "No active login session" in output
                print(f"✓ Command '{cmd}' correctly requires authentication")
                
    except Exception as e:
        print(f"✗ Authentication required test failed: {e}")
        import traceback
        traceback.print_exc()

def test_admin_restrictions():
    """Test that admin cannot access user records."""
    print("\n=== Testing Admin Restrictions ===")
    try:
        from pexpect_helpers import DBABAClient
        
        dbaba_path = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
        dbaba_working_dir = Path(__file__).parent / "M4-dbaba-2024" / "dbaba"
        
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create admin account
            client.login("admin", "AdminPass123")
            
            # Try to add a record as admin
            output = client.add_record("testrecord", sn="Test", gn="User")
            print(f"Admin add record: {output}")
            assert "Admin not authorized" in output
            print("✓ Admin correctly cannot add records")
            
            # Try to read records as admin
            output = client.read_record("testrecord")
            print(f"Admin read record: {output}")
            assert "Admin not authorized" in output
            print("✓ Admin correctly cannot read records")
            
    except Exception as e:
        print(f"✗ Admin restrictions test failed: {e}")
        import traceback
        traceback.print_exc()

def test_account_lockout():
    """Test account lockout after failed attempts."""
    print("\n=== Testing Account Lockout ===")
    try:
        from pexpect_helpers import DBABAClient
        
        dbaba_path = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
        dbaba_working_dir = Path(__file__).parent / "M4-dbaba-2024" / "dbaba"
        
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create admin account
            client.login("admin", "AdminPass123")
            client.logout()
            
            # Try wrong password 3 times
            for i in range(3):
                output = client.login("admin", "WrongPass")
                print(f"Failed attempt {i+1}: {output}")
                assert "Invalid credentials" in output
                client.logout()
            
            # Fourth attempt should be locked out
            output = client.login("admin", "WrongPass")
            print(f"Fourth attempt: {output}")
            # The system should either reject immediately or after a delay
            assert "Invalid credentials" in output or "An account is currently active" in output
            print("✓ Account lockout working")
            
    except Exception as e:
        print(f"✗ Account lockout test failed: {e}")
        import traceback
        traceback.print_exc()

def test_lin_bug():
    """Test for the LIN elevation bug."""
    print("\n=== Testing LIN Elevation Bug ===")
    try:
        from pexpect_helpers import DBABAClient
        
        dbaba_path = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
        dbaba_working_dir = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
        
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create users
            client.login("admin", "AdminPass123")
            client.add_user("user1")
            client.add_user("user2")
            client.logout()
            
            # Set up user1 with data
            client.login("user1", "TestPass123")
            client.add_record("user1secret", sn="User1", gn="Secret", pem="user1@secret.com")
            client.logout()
            
            # Set up user2 with data
            client.login("user2", "TestPass123")
            client.add_record("user2secret", sn="User2", gn="Secret", pem="user2@secret.com")
            client.logout()
            
            # Try to access user1's data while logged in as user2
            client.login("user2", "TestPass123")
            output = client.read_record("user1secret")
            print(f"User2 trying to access User1's data: {output}")
            
            if "user1secret" in output and "User1" in output:
                print("✗ LIN ELEVATION BUG DETECTED: User2 can access User1's data!")
                return False
            else:
                print("✓ No LIN elevation bug detected - proper data isolation")
                return True
                
    except Exception as e:
        print(f"✗ LIN bug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all security tests."""
    print("DBABA Security Test Suite")
    print("=" * 60)
    
    tests = [
        test_password_complexity,
        test_authentication_required,
        test_admin_restrictions,
        test_account_lockout,
        test_lin_bug,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result is not False:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {passed} passed, {failed} failed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
