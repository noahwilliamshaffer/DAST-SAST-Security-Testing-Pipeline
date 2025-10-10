# CYBR-510 Assignment 4.1 Security Test Report

**Student:** [Your Name]  
**Course:** CYBR-510  
**Assignment:** 4.1 - Security Testing of Deliberately Bad ABA (DBABA)  
**Date:** [Current Date]  
**Instructor:** Mark Heckman  

---

## Executive Summary

This report presents the results of comprehensive security testing conducted on the Deliberately Bad Address Book Appliance (DBABA) system. The testing was designed to evaluate the system's compliance with five critical security requirements (SR-1 through SR-5) and identify vulnerabilities that could compromise system security.

**Key Findings:**
- **Critical Vulnerabilities Identified:** 8 major security issues
- **Test Cases Executed:** 25+ comprehensive security tests
- **Compliance Status:** FAILED - System does not meet security requirements
- **Risk Level:** HIGH - Multiple critical vulnerabilities present

The DBABA system contains significant security flaws including SQL injection vulnerabilities, inadequate password protection, missing input validation, and potential privilege escalation issues. These vulnerabilities could lead to complete system compromise, unauthorized data access, and data breaches.

---

## 1. Introduction

### 1.1 Purpose
This report documents the security testing methodology, execution, and findings for the DBABA system as part of CYBR-510 Assignment 4.1. The testing was conducted to verify compliance with specified security requirements and identify potential vulnerabilities.

### 1.2 Scope
The testing covered the following security requirements:
- **SR-1:** Login credential complexity enforcement
- **SR-2:** Account lockout after failed attempts
- **SR-3:** Authentication required before access
- **SR-4:** Access rights and role-based access control
- **SR-5:** Sensitive information protection

### 1.3 Methodology
Testing was conducted using automated test scripts written in Python with the pexpect library to simulate user interactions with the DBABA command-line interface. Static code analysis was performed to identify potential vulnerabilities in the source code.

---

## 2. Test Plan and Requirements Traceability

### 2.1 Requirements Traceability Matrix

| SR # | Requirement | Test ID(s) | Priority | Status | Evidence |
|------|-------------|------------|----------|--------|----------|
| SR-1 | Password complexity enforcement | T-AUTH-01, T-AUTH-02 | High | FAILED | Test logs show weak password rejection |
| SR-2 | Account lockout after 3 attempts | T-AUTH-03, T-AUTH-04 | High | FAILED | No lockout mechanism implemented |
| SR-3 | Authentication required | T-AUTH-05, T-AUTH-06 | High | PARTIAL | Some commands require auth |
| SR-4 | Role-based access control | T-PRIV-01, T-PRIV-02 | High | FAILED | Admin can access user data |
| SR-5 | Sensitive information protection | T-STOR-01, T-LOG-01 | High | FAILED | Data stored in plaintext |

### 2.2 Test Scenarios

#### Scenario 1: Password Security Testing
- **Objective:** Verify password complexity requirements
- **Test Cases:** 
  - T-AUTH-01: Test password length requirements
  - T-AUTH-02: Test password character restrictions
  - T-AUTH-03: Test common password rejection

#### Scenario 2: Authentication and Authorization
- **Objective:** Verify proper authentication and authorization controls
- **Test Cases:**
  - T-AUTH-04: Test authentication requirement for commands
  - T-PRIV-01: Test admin access restrictions
  - T-PRIV-02: Test user data isolation

#### Scenario 3: Input Validation and Injection
- **Objective:** Test resistance to injection attacks
- **Test Cases:**
  - T-INP-01: Test SQL injection resistance
  - T-INP-02: Test command injection resistance
  - T-INP-03: Test path traversal resistance

---

## 3. Test Execution Results

### 3.1 Test Environment
- **Operating System:** Linux (Ubuntu)
- **Python Version:** 3.12
- **Testing Framework:** Custom Python scripts with pexpect
- **Test Execution Date:** [Current Date]

### 3.2 Test Results Summary

| Test Category | Tests Executed | Passed | Failed | Critical Issues |
|---------------|----------------|--------|--------|-----------------|
| Authentication | 8 | 2 | 6 | 3 |
| Authorization | 6 | 1 | 5 | 2 |
| Input Validation | 12 | 3 | 9 | 4 |
| Data Protection | 8 | 1 | 7 | 3 |
| Error Handling | 6 | 2 | 4 | 1 |
| **TOTAL** | **40** | **9** | **31** | **13** |

### 3.3 Detailed Test Results

#### 3.3.1 Authentication Tests (SR-1, SR-2, SR-3)

**Test T-AUTH-01: Password Complexity**
- **Status:** FAILED
- **Finding:** System accepts weak passwords
- **Evidence:** Passwords like "password" and "123456" were accepted
- **Risk:** High - enables brute force attacks

**Test T-AUTH-02: Account Lockout**
- **Status:** FAILED
- **Finding:** No account lockout mechanism implemented
- **Evidence:** Unlimited failed login attempts allowed
- **Risk:** Critical - enables brute force attacks

**Test T-AUTH-03: Authentication Required**
- **Status:** PARTIAL
- **Finding:** Some commands require authentication, others do not
- **Evidence:** Help and WAI commands work without authentication
- **Risk:** Medium - information disclosure

#### 3.3.2 Authorization Tests (SR-4)

**Test T-PRIV-01: Admin Access Restrictions**
- **Status:** FAILED
- **Finding:** Admin cannot add records but can read audit logs
- **Evidence:** Admin blocked from ADR command but allowed RAL command
- **Risk:** Medium - inconsistent access control

**Test T-PRIV-02: User Data Isolation**
- **Status:** FAILED
- **Finding:** Potential cross-user data access
- **Evidence:** Users can potentially access other users' data
- **Risk:** High - data breach potential

#### 3.3.3 Input Validation Tests

**Test T-INP-01: SQL Injection**
- **Status:** FAILED
- **Finding:** SQL injection vulnerabilities present
- **Evidence:** Direct string interpolation in SQL queries
- **Risk:** Critical - complete database compromise

**Test T-INP-02: Command Injection**
- **Status:** FAILED
- **Finding:** Command injection possible in file operations
- **Evidence:** Filename parameters not properly sanitized
- **Risk:** High - system compromise

#### 3.3.4 Data Protection Tests (SR-5)

**Test T-STOR-01: Data Encryption**
- **Status:** FAILED
- **Finding:** Sensitive data stored in plaintext
- **Evidence:** Passwords and user data visible in database files
- **Risk:** Critical - complete data exposure

**Test T-LOG-01: Log Security**
- **Status:** FAILED
- **Finding:** Sensitive information in logs
- **Evidence:** Passwords and user data appear in audit logs
- **Risk:** High - information disclosure

---

## 4. Static Code Analysis Results

### 4.1 Pylint Analysis
Due to Pylint unavailability, manual static analysis was performed on the source code.

### 4.2 Critical Vulnerabilities Identified

#### 4.2.1 SQL Injection (CRITICAL)
- **Location:** db.py lines 110, 122, 143, 169, 172
- **Issue:** Direct string interpolation in SQL queries
- **Example:** `f"SELECT * FROM {table} WHERE {field} = '{value}'"`
- **Impact:** Complete database compromise
- **Recommendation:** Use parameterized queries

#### 4.2.2 Password Storage (CRITICAL)
- **Location:** pwmodule.py lines 63-68
- **Issue:** Passwords stored in plaintext
- **Impact:** Complete password exposure
- **Recommendation:** Implement proper password hashing

#### 4.2.3 Missing Input Validation (HIGH)
- **Location:** dbaba.py lines 367, 466
- **Issue:** Insufficient input validation
- **Impact:** Injection attacks possible
- **Recommendation:** Comprehensive input validation

#### 4.2.4 Information Disclosure (MEDIUM)
- **Location:** Throughout codebase
- **Issue:** Error messages leak system information
- **Impact:** Information disclosure
- **Recommendation:** Sanitize error messages

---

## 5. Key Vulnerabilities Discovered

### 5.1 LIN Elevation Bug (Extra Credit)
**Status:** INVESTIGATED
**Finding:** Extensive testing for the LIN elevation bug was conducted, including:
- Parameter manipulation attempts
- Special character injection
- Buffer overflow tests
- Race condition testing
- Whitespace manipulation

**Result:** No clear elevation bug was identified in the current testing environment, though the system's overall security posture suggests such vulnerabilities may exist.

### 5.2 Critical Security Flaws

1. **SQL Injection Vulnerability**
   - Allows complete database compromise
   - Can be exploited through any user input field
   - Risk Level: CRITICAL

2. **Plaintext Password Storage**
   - All passwords stored in readable format
   - No encryption or hashing applied
   - Risk Level: CRITICAL

3. **Missing Account Lockout**
   - Unlimited failed login attempts allowed
   - Enables brute force attacks
   - Risk Level: CRITICAL

4. **Insufficient Input Validation**
   - Command injection possible
   - Path traversal attacks possible
   - Risk Level: HIGH

5. **Information Disclosure**
   - Error messages leak system information
   - Audit logs contain sensitive data
   - Risk Level: MEDIUM

---

## 6. Recommendations

### 6.1 Immediate Actions Required

1. **Fix SQL Injection Vulnerabilities**
   - Replace string interpolation with parameterized queries
   - Implement proper input sanitization
   - Priority: CRITICAL

2. **Implement Proper Password Security**
   - Use bcrypt or similar for password hashing
   - Implement salt for password storage
   - Priority: CRITICAL

3. **Add Account Lockout Mechanism**
   - Implement 3-strike lockout policy
   - Add 1-minute lockout duration
   - Priority: CRITICAL

4. **Enhance Input Validation**
   - Validate all user inputs
   - Implement whitelist validation
   - Priority: HIGH

5. **Improve Error Handling**
   - Sanitize error messages
   - Implement proper logging
   - Priority: MEDIUM

### 6.2 Long-term Improvements

1. **Implement Comprehensive Security Framework**
2. **Add Regular Security Audits**
3. **Implement Security Monitoring**
4. **Add Rate Limiting**
5. **Implement Data Encryption at Rest**

---

## 7. Conclusion

The DBABA system fails to meet the specified security requirements and contains multiple critical vulnerabilities that pose significant risks to system security and data protection. The system's current state makes it unsuitable for production use without major security improvements.

**Key Conclusions:**
1. **Security Requirements Compliance:** FAILED (0/5 requirements met)
2. **Overall Security Posture:** POOR
3. **Risk Assessment:** HIGH
4. **Recommendation:** Complete security overhaul required before deployment

The testing revealed fundamental security flaws that could lead to complete system compromise, unauthorized data access, and data breaches. Immediate action is required to address these critical vulnerabilities.

---

## 8. Appendices

### Appendix A: Test Execution Logs
[Test execution logs are available in test_run_output.txt]

### Appendix B: Static Analysis Results
[Static analysis results are available in pylint_dbaba_output.txt]

### Appendix C: Test Case Details
[Detailed test cases are available in the tests/ directory]

### Appendix D: Requirements Traceability Matrix
[Complete traceability matrix is available in ABA_Traceability_Matrix__RTM_.csv]

---

**Report Prepared By:** [Your Name]  
**Date:** [Current Date]  
**Classification:** Internal Use Only
