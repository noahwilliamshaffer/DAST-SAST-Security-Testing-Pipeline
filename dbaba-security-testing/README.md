# CYBR-510 Assignment 4.1: DBABA Security Testing

This repository contains a comprehensive security testing framework and vulnerability assessment for the Deliberately Bad Address Book Appliance (DBABA) system as part of CYBR-510 Assignment 4.1.

## Overview

The DBABA system was subjected to extensive security testing to evaluate compliance with five critical security requirements (SR-1 through SR-5) and identify vulnerabilities that could compromise system security.

## Key Findings

- **8 Critical Vulnerabilities Identified**
- **40+ Test Cases Executed**
- **0/5 Security Requirements Fully Compliant**
- **Risk Level: CRITICAL**

### Critical Vulnerabilities
1. **SQL Injection** - Complete database compromise possible
2. **Plaintext Password Storage** - All passwords exposed
3. **Missing Account Lockout** - Unlimited brute force attempts
4. **File Permission Issues** - Database files world-readable
5. **Insufficient Input Validation** - Command injection possible
6. **Information Disclosure** - Sensitive data in logs
7. **Inconsistent Access Controls** - Authorization flaws
8. **Data Protection Failures** - No encryption at rest

## Repository Structure

```
├── Final_CYBR-510_Assignment_4.1_Report.md    # Main comprehensive report
├── test_run_output.txt                        # Automated test results
├── manual_test_output.txt                     # Manual testing results
├── pylint_dbaba_output.txt                    # Static code analysis
├── ABA_Traceability_Matrix__RTM_.csv         # Requirements traceability
├── tests/                                     # Automated test framework
│   ├── conftest.py
│   ├── pexpect_helpers.py
│   ├── test_auth.py
│   ├── test_privacy.py
│   ├── test_inputs.py
│   ├── test_storage.py
│   ├── test_logging.py
│   └── test_lin_bug.py
├── simple_test_runner.py                      # Automated test runner
├── manual_security_test.py                    # Manual testing script
├── M4-dbaba-2024/                            # DBABA source code
└── README.md                                  # This file
```

## Test Framework

### Automated Testing
- **Framework**: Python with pexpect library
- **Test Categories**: Authentication, Authorization, Input Validation, Data Protection, Error Handling
- **Coverage**: 40+ test cases across all security domains

### Manual Testing
- Interactive testing of DBABA CLI
- File permission analysis
- Static code analysis
- Vulnerability assessment

## Security Requirements Tested

| SR # | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| SR-1 | Password complexity enforcement | FAILED | Weak passwords accepted |
| SR-2 | Account lockout after 3 attempts | FAILED | No lockout mechanism |
| SR-3 | Authentication required | PARTIAL | Most commands require auth |
| SR-4 | Role-based access control | FAILED | Inconsistent controls |
| SR-5 | Sensitive information protection | FAILED | Data stored in plaintext |

## Usage

### Running Automated Tests
```bash
python3 simple_test_runner.py
```

### Running Manual Tests
```bash
python3 manual_security_test.py
```

### Running Individual Test Modules
```bash
python3 -m pytest tests/test_auth.py -v
python3 -m pytest tests/test_privacy.py -v
python3 -m pytest tests/test_inputs.py -v
```

## Dependencies

- Python 3.12+
- pexpect
- pytest
- pycryptodome

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install pexpect pytest pycryptodome
   ```
3. Run the tests

## Report

The comprehensive security test report is available in `Final_CYBR-510_Assignment_4.1_Report.md` and includes:

- Executive Summary
- Test Plan and Requirements Traceability
- Detailed Test Results
- Static Code Analysis
- Vulnerability Assessment
- Recommendations
- Evidence Documentation

## Extra Credit

Extensive investigation of the LIN elevation bug was conducted, including:
- Parameter manipulation attempts
- Special character injection
- Buffer overflow tests
- Race condition testing
- Whitespace manipulation

## Conclusion

The DBABA system fails to meet security requirements and contains multiple critical vulnerabilities that make it unsuitable for production use without major security improvements.

## Author

[Your Name]  
CYBR-510 Assignment 4.1  
December 2024

## License

This project is for educational purposes as part of CYBR-510 coursework.
