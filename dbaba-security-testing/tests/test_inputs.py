"""
Input validation and injection tests for DBABA.
Tests various input validation scenarios and injection attacks.
"""
import pytest
import os
from pexpect_helpers import DBABAClient, create_test_csv_file


class TestInputValidation:
    """Test input validation for various commands."""
    
    def test_record_id_validation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test record ID validation."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Test invalid record IDs
            invalid_ids = [
                "",  # Empty
                "a" * 17,  # Too long
                "test@123",  # Special characters
                "test 123",  # Spaces
                "test-123",  # Hyphens
                "test_123",  # Underscores
            ]
            
            for invalid_id in invalid_ids:
                output = client.add_record(invalid_id, sn="Test")
                assert "Invalid record_id" in output
    
    def test_field_validation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test field validation."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Test invalid field names
            output = client.add_record("testrecord", invalidfield="value")
            assert "One or more invalid record data fields" in output
            
            # Test invalid field values (too long)
            long_value = "x" * 65  # Exceeds 64 character limit
            output = client.add_record("testrecord", sn=long_value)
            # The system should handle this gracefully
    
    def test_user_id_validation(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test user ID validation."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            client.login("admin", "AdminPass123")
            
            # Test invalid user IDs
            invalid_user_ids = [
                "",  # Empty
                "a" * 17,  # Too long
                "test@123",  # Special characters
                "test 123",  # Spaces
                "test-123",  # Hyphens
            ]
            
            for invalid_id in invalid_user_ids:
                output = client.add_user(invalid_id)
                assert "Invalid userID" in output


class TestInjectionAttacks:
    """Test for various injection attacks."""
    
    def test_sql_injection_in_record_fields(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test SQL injection in record fields."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Try SQL injection in various fields
            sql_payloads = [
                "'; DROP TABLE AbaTable; --",
                "' OR '1'='1",
                "'; INSERT INTO AbaTable VALUES ('hacker', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack', 'hack'); --",
                "1' UNION SELECT * FROM AbaTable --"
            ]
            
            for payload in sql_payloads:
                output = client.add_record("testrecord", sn=payload)
                # Should either reject or sanitize the input
                # The system should not crash or execute the SQL
                assert "OK" in output or "One or more invalid record data fields" in output
    
    def test_command_injection_in_filenames(self, dbaba_path, dbaba_working_dir, clean_dbaba_state, temp_dir):
        """Test command injection in file operations."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Add a test record
            client.add_record("testrecord", sn="Test", gn="User")
            
            # Try command injection in export filename
            malicious_filenames = [
                "test; rm -rf /",
                "test && echo 'hacked'",
                "test | cat /etc/passwd",
                "test$(whoami)",
                "test`id`"
            ]
            
            for filename in malicious_filenames:
                output = client.export_database(filename)
                # Should either reject the filename or sanitize it
                assert "OK" in output or "Invalid" in filename or "Can't open" in output


class TestPathTraversal:
    """Test path traversal attacks."""
    
    def test_path_traversal_export(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test path traversal in export operations."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Add a test record
            client.add_record("testrecord", sn="Test", gn="User")
            
            # Try path traversal attacks
            path_traversal_attempts = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "/etc/passwd",
                "C:\\Windows\\System32\\drivers\\etc\\hosts",
                "....//....//....//etc//passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
            ]
            
            for path in path_traversal_attempts:
                output = client.export_database(path)
                # Should reject or sanitize the path
                assert "OK" in output or "Invalid" in output or "Can't open" in output
    
    def test_path_traversal_import(self, dbaba_path, dbaba_working_dir, clean_dbaba_state, temp_dir):
        """Test path traversal in import operations."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Create a legitimate test file
            test_file = create_test_csv_file(temp_dir, "legitimate.csv", [
                "testrecord,Test,User,,,,,,,,,,"
            ])
            
            # Try path traversal attacks
            path_traversal_attempts = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "/etc/passwd",
                "C:\\Windows\\System32\\drivers\\etc\\hosts"
            ]
            
            for path in path_traversal_attempts:
                output = client.import_database(path)
                # Should reject the path
                assert "File doesn't exist" in output or "Can't open" in output or "Invalid" in output


class TestInputLengthLimits:
    """Test input length limits and DoS protection."""
    
    def test_long_inputs(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test handling of very long inputs."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Test very long field values
            very_long_value = "x" * 10000
            output = client.add_record("testrecord", sn=very_long_value)
            # Should either reject or truncate
            assert "OK" in output or "One or more invalid record data fields" in output
    
    def test_many_records(self, dbaba_path, dbaba_working_dir, clean_dbaba_state, temp_dir):
        """Test handling of many records (DoS protection)."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Create a file with many records
            many_records = []
            for i in range(1000):  # 1000 records
                many_records.append(f"record{i},Test{i},User{i},,,,,,,,,,")
            
            test_file = create_test_csv_file(temp_dir, "many_records.csv", many_records)
            
            # Try to import many records
            output = client.import_database(str(test_file))
            # Should either succeed or fail gracefully
            assert "OK" in output or "Number of records exceeds maximum" in output or "Can't open" in output


class TestMalformedInputs:
    """Test handling of malformed inputs."""
    
    def test_malformed_csv_import(self, dbaba_path, dbaba_working_dir, clean_dbaba_state, temp_dir):
        """Test handling of malformed CSV files."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Create a user
            client.login("admin", "AdminPass123")
            client.add_user("testuser")
            client.logout()
            
            client.login("testuser", "TestPass123")
            
            # Test various malformed CSV files
            malformed_files = [
                ["incomplete,record"],  # Missing fields
                ["record1,field1,field2,field3,field4,field5,field6,field7,field8,field9,field10,field11,field12,field13"],  # Too many fields
                ["", "valid,record,with,all,fields,,,,,,,,"],  # Empty line
                ["record1,field1,field2,field3,field4,field5,field6,field7,field8,field9,field10,field11,field12,field13\nrecord2,incomplete"],  # Mixed valid/invalid
            ]
            
            for i, malformed_data in enumerate(malformed_files):
                test_file = create_test_csv_file(temp_dir, f"malformed{i}.csv", malformed_data)
                output = client.import_database(str(test_file))
                # Should reject malformed files
                assert "Incomplete record or invalid format" in output or "Invalid record ID" in output or "Can't open" in output
    
    def test_empty_inputs(self, dbaba_path, dbaba_working_dir, clean_dbaba_state):
        """Test handling of empty inputs."""
        with DBABAClient(dbaba_path, dbaba_working_dir) as client:
            # Test empty commands
            output = client.send_command("")
            # Should not crash
            
            # Test commands with missing parameters
            output = client.send_command("ADR")
            assert "No record_id" in output
            
            output = client.send_command("RER")
            assert "Invalid record_id" in output
            
            output = client.send_command("DER")
            assert "No record_id" in output
