#!/usr/bin/env python3
"""
Test runner for DBABA security tests.
This script runs all the security tests and captures the output.
"""
import sys
import os
import traceback
from pathlib import Path

# Add the tests directory to the path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

def run_test_module(module_name, test_class_name=None):
    """Run a specific test module or test class."""
    try:
        module = __import__(module_name)
        print(f"\n{'='*60}")
        print(f"Running {module_name}")
        print(f"{'='*60}")
        
        if test_class_name:
            test_class = getattr(module, test_class_name)
            test_methods = [method for method in dir(test_class) if method.startswith('test_')]
            print(f"Found {len(test_methods)} test methods in {test_class_name}")
            
            for method_name in test_methods:
                print(f"\n--- Running {method_name} ---")
                try:
                    # Create test instance
                    test_instance = test_class()
                    # Set up fixtures (simplified)
                    test_instance.dbaba_path = Path(__file__).parent / "M4-dbaba-2024" / "dbaba" / "dbaba.py"
                    test_instance.dbaba_working_dir = Path(__file__).parent / "M4-dbaba-2024" / "dbaba"
                    test_instance.temp_dir = "/tmp"
                    
                    # Run the test method
                    method = getattr(test_instance, method_name)
                    method()
                    print(f"✓ {method_name} PASSED")
                except Exception as e:
                    print(f"✗ {method_name} FAILED: {e}")
                    traceback.print_exc()
        else:
            print(f"Module {module_name} loaded successfully")
            
    except Exception as e:
        print(f"Error running {module_name}: {e}")
        traceback.print_exc()

def main():
    """Main test runner."""
    print("DBABA Security Test Suite")
    print("=" * 60)
    
    # Test modules to run
    test_modules = [
        ("test_auth", "TestPasswordComplexity"),
        ("test_auth", "TestAccountLockout"), 
        ("test_auth", "TestAuthenticationRequired"),
        ("test_auth", "TestPasswordChange"),
        ("test_privacy", "TestRoleBasedAccessControl"),
        ("test_privacy", "TestSensitiveInformationProtection"),
        ("test_privacy", "TestDataIsolation"),
        ("test_inputs", "TestInputValidation"),
        ("test_inputs", "TestInjectionAttacks"),
        ("test_inputs", "TestPathTraversal"),
        ("test_inputs", "TestInputLengthLimits"),
        ("test_inputs", "TestMalformedInputs"),
        ("test_storage", "TestDataEncryption"),
        ("test_storage", "TestFilePermissions"),
        ("test_storage", "TestDataIntegrity"),
        ("test_storage", "TestDataCleanup"),
        ("test_logging", "TestErrorMessageSecurity"),
        ("test_logging", "TestAuditLogSecurity"),
        ("test_logging", "TestLoggingCompleteness"),
        ("test_logging", "TestErrorHandling"),
        ("test_lin_bug", "TestLINElevationBug"),
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for module_name, test_class_name in test_modules:
        try:
            run_test_module(module_name, test_class_name)
        except Exception as e:
            print(f"Failed to run {module_name}.{test_class_name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {passed_tests} passed, {failed_tests} failed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
