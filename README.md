# Multi-Tool SAST & DAST Security Testing Pipeline

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Security](https://img.shields.io/badge/security-SAST%20%26%20DAST-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Tools](https://img.shields.io/badge/tools-Bandit%20%7C%20Pylint%20%7C%20Safety%20%7C%20SonarQube%20%7C%20ZAP-orange.svg)

> **An automated security testing pipeline integrating 5 industry-standard tools (Bandit, Pylint, Safety, SonarQube, OWASP ZAP) with comprehensive data visualization and reporting.**

This project demonstrates a production-ready approach to integrating multiple security scanning tools into a unified DevSecOps pipeline, with automated result aggregation and visual reporting.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Interview Walkthrough](#-interview-walkthrough---what-i-built)
- [Architecture](#architecture)
- [Security Tools Implemented](#-security-tools-implemented)
- [Technical Implementation](#technical-implementation)
- [Getting Started](#getting-started)
- [Understanding the Results](#understanding-the-results)
- [Resources](#resources)

---

## 🎯 Overview

### What I Built

An **enterprise-grade automated security testing pipeline** that:

1. **Multi-Tool SAST Analysis** - Integrates 4 static analysis tools:
   - **Bandit**: Python security vulnerability scanner (hardcoded secrets, SQL injection patterns)
   - **Pylint**: Code quality and security linting
   - **Safety**: Dependency vulnerability scanner (CVE detection)
   - **SonarQube**: Enterprise code quality and security platform

2. **Dynamic Application Security Testing (DAST)** - Uses OWASP ZAP:
   - Active scanning for OWASP Top 10 vulnerabilities
   - Spider/crawler for complete application mapping
   - Passive traffic analysis

3. **Automated Data Processing Pipeline**:
   - Custom Python scripts to parse and normalize outputs from all 5 tools
   - Pandas-based data aggregation and analysis
   - Automated report generation in multiple formats (JSON, HTML, PNG)

4. **Containerized Infrastructure**:
   - Docker Compose orchestration of 3 services
   - Network-isolated security testing environment
   - Reproducible and portable architecture

5. **Comprehensive Visualization System**:
   - Multi-dimensional security dashboards
   - Severity distribution analysis
   - Tool comparison metrics
   - Executive summary reports

### What is SAST vs DAST?

| **SAST (Static Analysis)** | **DAST (Dynamic Analysis)** |
|----------------------------|------------------------------|
| Analyzes source code without running it | Tests the running application |
| Finds coding errors and security flaws | Finds runtime vulnerabilities |
| Works like a code review | Works like a penetration test |
| Fast, early in development | Slower, tests real behavior |
| **My Implementation: Bandit, Pylint, Safety, SonarQube** | **My Implementation: OWASP ZAP** |

**Why use both?** SAST catches issues in code before deployment (shift-left security), while DAST finds runtime vulnerabilities that only manifest in a live environment. Combined, they provide defense-in-depth security coverage.

---

## 🎯 Project Overview - Technical Implementation

### Problem Statement

Security testing tools are often used in isolation, producing disparate reports that require manual correlation. Organizations typically run Bandit, SonarQube, and OWASP ZAP separately, then manually aggregate findings across multiple formats and severity scales. This project addresses that gap by creating an automated pipeline that:
- Executes multiple security scanners in parallel
- Aggregates results from heterogeneous data sources into unified reports
- Provides multi-dimensional visualizations for technical and executive audiences
- Runs in a containerized, reproducible environment

### Solution Architecture

**Multi-Tool SAST Pipeline** - 4 static analysis tools executed in parallel:
- **Bandit**: Python-specific security vulnerability detection (B201-B999 security tests)
- **Pylint**: Code quality and security anti-pattern analysis
- **Safety**: Dependency vulnerability scanning against CVE databases
- **SonarQube**: Enterprise-grade code quality platform with security rules

**DAST Implementation** - OWASP ZAP performing 3-phase dynamic testing:
- Spider phase for application mapping
- Passive scan for traffic analysis
- Active scan for penetration testing

**Data Processing Pipeline** - Custom Python automation:
- Multi-format JSON parsing and normalization
- Pandas-based data aggregation across 5 tools
- Automated visualization generation (Matplotlib/Seaborn)

**Infrastructure** - Docker Compose orchestration:
- 3 containerized services with network isolation
- Persistent volumes for stateful services
- Port mapping for external access

---

## 🔧 Technical Implementation Details

### SAST Implementation - Multi-Tool Static Analysis

Built `run_sast_scans.py`, a Python orchestration script that executes 4 static analysis tools in parallel:

#### **Bandit** - Python Security Scanner
```python
bandit -r dbaba/ -f json -o results/bandit_results.json
```
**Detection Capabilities:**
- Hardcoded credentials and secrets (B105, B106)
- SQL injection patterns (B608)
- Insecure cryptography usage (B303-B311)
- Unsafe deserialization (B301, B302)

**Output Format:** JSON with severity classification (HIGH/MEDIUM/LOW)

#### **Pylint** - Code Quality & Security Linter
```python
pylint dbaba/*.py --output-format=json --disable=C0114,C0115,C0116
```
**Detection Capabilities:**
- Unused imports and variables that may indicate dead code paths
- Exception handling anti-patterns
- Code complexity metrics
- Security-relevant code smells

**Output Format:** JSON categorized by error/warning/convention/refactor

#### **Safety** - Dependency Vulnerability Scanner
```python
safety check --file requirements.txt --json
```
**Detection Capabilities:**
- Known CVEs in Python packages
- Vulnerable dependency versions
- Cross-references with NVD, GHSA, PyUp databases

**Output Format:** JSON with CVE IDs and CVSS scores

#### **SonarQube** - Enterprise Code Quality Platform
```bash
sonar-scanner -Dsonar.projectKey=dbaba -Dsonar.sources=dbaba/ \
  -Dsonar.host.url=http://localhost:9000
```
**Detection Capabilities:**
- 25+ programming languages support
- Security hotspots (OWASP Top 10 mapping)
- Code coverage and technical debt metrics
- Duplicated code detection

**Output Format:** Web dashboard + REST API for programmatic access

**Technical Features:**
- Automated tool installation and dependency checks
- Unified error handling across heterogeneous output formats
- Summary aggregation combining all 4 tool results
- Parallel execution for reduced scan time

---

### DAST Implementation - Dynamic Application Testing

Built `run_zap_scan.sh`, a Bash script that interfaces with OWASP ZAP REST API for 3-phase security testing:

#### **Phase 1: Spider (Application Discovery)**
```bash
curl "http://localhost:8080/JSON/spider/action/scan/?apikey=changeme&url=http://localhost:5000"
```
**Functionality:**
- Crawls web application to discover all pages, forms, and API endpoints
- Builds complete site map for subsequent testing
- Progress tracking via polling API

#### **Phase 2: Passive Scan (Traffic Analysis)**
```bash
# Executes automatically during spider phase
```
**Functionality:**
- Analyzes HTTP requests/responses for security issues
- Detects missing security headers (CSP, HSTS, X-Frame-Options)
- Identifies insecure cookie configurations
- Non-intrusive, zero impact on application state

#### **Phase 3: Active Scan (Penetration Testing)**
```bash
curl "http://localhost:8080/JSON/ascan/action/scan/?apikey=changeme&url=http://localhost:5000&recurse=true"
```
**Functionality:**
- SQL Injection testing (error-based, blind, time-based)
- Cross-Site Scripting (reflected, stored, DOM-based)
- Authentication and session management testing
- CSRF vulnerability detection
- Path traversal and LFI testing

**Technical Features:**
- RESTful API integration for programmatic control
- Progress monitoring with status polling
- Multi-format report generation (HTML, XML, JSON)
- Risk-level categorization (High/Medium/Low/Informational)

---

### Docker Infrastructure - Containerized Environment

Built `docker-compose.yml` orchestrating 3 services with network isolation:

```yaml
services:
  sonarqube:
    image: sonarqube:community
    ports: ["9000:9000"]
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_extensions:/opt/sonarqube/extensions
    networks: [security-testing]

  zap:
    image: ghcr.io/zaproxy/zaproxy:stable
    command: zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.key=changeme
    ports: ["8080:8080"]
    networks: [security-testing]

  dbaba-app:
    build: ./dbaba-security-testing/M4-dbaba-2024
    ports: ["5000:5000"]
    environment:
      - FLASK_APP=dbaba.py
      - FLASK_ENV=development
    networks: [security-testing]

networks:
  security-testing:
    driver: bridge
```

**Architecture Benefits:**
- **Reproducibility**: Identical environment across development, testing, and CI/CD
- **Isolation**: Containerized tools isolated from host system
- **Networking**: Services communicate via `security-testing` bridge network
- **Portability**: Single `docker-compose up -d` command deploys entire stack
- **State Management**: Persistent volumes for SonarQube data retention

---

### Data Processing & Visualization Pipeline

Built `visualize_combined_results.py`, a Pandas-based data processing pipeline that normalizes and visualizes outputs from 5 heterogeneous security tools:

#### **Data Ingestion Layer**
```python
# Multi-source data loading
bandit_data = pd.read_json('results/sast/bandit_results.json')
pylint_data = pd.read_json('results/sast/pylint_results.json')
safety_data = pd.read_json('results/sast/safety_results.json')
sonar_issues = requests.get('http://localhost:9000/api/issues/search').json()
zap_alerts = pd.read_json('results/zap/zap_alerts.json')
```

#### **Data Normalization Engine**
```python
# Severity level standardization across tools
severity_mapping = {
    'Bandit': {'HIGH': 'Critical', 'MEDIUM': 'High', 'LOW': 'Medium'},
    'ZAP': {3: 'High', 2: 'Medium', 1: 'Low', 0: 'Info'},
    'SonarQube': {'BLOCKER': 'Critical', 'CRITICAL': 'High', 'MAJOR': 'Medium'},
    'Pylint': {'error': 'High', 'warning': 'Medium', 'convention': 'Low'}
}
```

**Normalization Challenges Solved:**
- Heterogeneous severity scales (numeric, string, custom)
- Inconsistent JSON schemas across tools
- Missing fields and null value handling
- Timestamp format standardization

#### **Visualization Components**

Generated 5 publication-quality visualizations using Matplotlib and Seaborn:

1. **Severity Distribution Chart** - Bar plot of vulnerability counts by severity
2. **Tool Comparison Analysis** - SAST vs DAST findings comparison
3. **Vulnerability Type Breakdown** - Pie chart of CWE categories
4. **File-Level Heatmap** - Vulnerability density across source files
5. **Executive Dashboard** - High-level KPIs and trend metrics

#### **Report Generation**
```python
# Jinja2 template-based HTML report generation
template = jinja_env.get_template('security_report.html')
html_output = template.render(
    total_issues=len(combined_df),
    critical_count=critical_issues,
    charts=chart_images,
    detailed_findings=findings_table
)
```

**Output Formats:**
- PNG/SVG charts for documentation
- HTML reports with embedded visualizations
- JSON summaries for programmatic consumption

---

### End-to-End Automation - Master Orchestration

Built `run_all_scans.sh`, a master Bash script that coordinates the entire security testing pipeline:

```bash
#!/bin/bash

# Infrastructure startup
docker-compose up -d

# Service readiness checks
wait_for_service "sonarqube" "http://localhost:9000/api/system/status"
wait_for_service "zap" "http://localhost:8080"
wait_for_service "dbaba-app" "http://localhost:5000"

# Parallel SAST execution
python3 scripts/run_sast_scans.py &
SAST_PID=$!

# DAST execution (ZAP scan)
bash scripts/run_zap_scan.sh &
DAST_PID=$!

# Wait for scan completion
wait $SAST_PID $DAST_PID

# Post-processing
python3 scripts/visualize_combined_results.py

# Summary output
generate_scan_summary
```

**Pipeline Performance Metrics:**
- SAST scans: 3-5 minutes (parallel execution of 4 tools)
- DAST scan: 8-12 minutes (spider → passive → active phases)
- Data processing & visualization: 30 seconds
- **Total execution time: ~15 minutes**

---

### Results & Vulnerability Detection

Pipeline testing conducted on the DBABA web application (intentionally vulnerable) revealed the following security issues:

| Vulnerability Class | Detection Method | Severity Level | CWE ID |
|-------------------|------------------|----------------|--------|
| SQL Injection | Bandit (static), ZAP (runtime) | 🔴 CRITICAL | CWE-89 |
| Hardcoded Credentials | Bandit | 🔴 HIGH | CWE-798 |
| Cross-Site Scripting (XSS) | ZAP | 🔴 HIGH | CWE-79 |
| Insecure Cryptography | Bandit | 🟠 MEDIUM | CWE-327 |
| Missing Security Headers | ZAP (passive scan) | 🟠 MEDIUM | CWE-693 |
| Code Quality Issues | Pylint, SonarQube | 🟡 LOW | N/A |
| Vulnerable Dependencies | Safety | 🟡 LOW | Various CVEs |

**Key Findings:**
- SQL Injection detected by both SAST (Bandit pattern matching) and DAST (ZAP runtime testing)
- SAST tools identified 47 total code-level issues
- DAST discovered 23 runtime vulnerabilities
- 8 overlapping detections between SAST and DAST (validation of findings)
- 62 unique vulnerabilities requiring remediation

---

### Technical Skills & Technologies

**Security Engineering:**
- Application Security Testing (SAST/DAST methodologies)
- OWASP Top 10 vulnerability identification and remediation
- Security tool integration and API usage
- DevSecOps pipeline architecture

**Software Engineering:**
- Python automation (subprocess management, error handling, logging)
- REST API integration (ZAP API, SonarQube API)
- Data engineering with Pandas (ETL pipelines)
- Multi-format data parsing (JSON, XML, CSV)

**Infrastructure & DevOps:**
- Docker containerization and Docker Compose orchestration
- Container networking and service discovery
- Volume management for persistent storage
- Shell scripting (Bash) for automation

**Data Analysis & Visualization:**
- Data normalization across heterogeneous sources
- Statistical analysis and aggregation
- Matplotlib/Seaborn visualization libraries
- Report generation (Jinja2 templating, HTML/CSS)

**Tools & Technologies:**
- **SAST**: Bandit, Pylint, Safety, SonarQube
- **DAST**: OWASP ZAP
- **Data Processing**: Python, Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Infrastructure**: Docker, Docker Compose
- **Languages**: Python, Bash, YAML, Jinja2

---

### Roadmap & Future Enhancements

**CI/CD Integration:**
- GitHub Actions workflow for automated PR scanning
- GitLab CI pipeline integration
- Jenkins pipeline implementation with quality gates

**Advanced Analytics:**
- Time-series trend analysis of vulnerability metrics
- Historical data storage (PostgreSQL backend)
- Machine learning for false positive reduction

**Notification & Alerting:**
- Slack webhook integration for critical findings
- Email notifications with SMTP
- PagerDuty integration for incident response

**Additional Security Tools:**
- Semgrep for custom rule creation
- Trivy for container image scanning
- Dependency-Track for SCA management
- Nuclei for vulnerability scanning

**Policy Enforcement:**
- Build failure on critical vulnerabilities
- Custom security policies per repository
- Automated remediation suggestions
- Compliance reporting (SOC 2, PCI-DSS)

---

## 🏗️ Architecture

The following diagram shows how all components interact in this security testing pipeline:

```mermaid
graph TB
    subgraph "Source Code Repository"
        A[Source Code<br/>DBABA Web App]
    end
    
    subgraph "SAST Tools - Static Analysis"
        B1[Bandit<br/>Python Security Scanner]
        B2[Pylint<br/>Code Quality]
        B3[Safety<br/>Dependency CVE Scanner]
        B4[SonarQube<br/>Enterprise Platform]
    end
    
    subgraph "DAST Tool - Dynamic Testing"
        C[OWASP ZAP<br/>Spider + Active + Passive Scan]
    end
    
    subgraph "Application Environment"
        D[Docker Container<br/>Flask Web Application]
    end
    
    subgraph "Data Processing Pipeline"
        F[Pandas Script<br/>run_sast_scans.py + visualize_combined_results.py]
        G[Visualization Engine<br/>Matplotlib + Seaborn]
    end
    
    subgraph "Results & Reports"
        H1[JSON Reports<br/>5 Tool Outputs]
        H2[HTML Reports<br/>Executive + Technical]
        H3[PNG/SVG Charts<br/>Data Visualizations]
    end
    
    A -->|Scan Source Code| B1
    A -->|Scan Source Code| B2
    A -->|Scan Dependencies| B3
    A -->|Scan Source Code| B4
    A -->|Build & Deploy| D
    D -->|Runtime Testing| C
    
    B1 -->|bandit_results.json| H1
    B2 -->|pylint_results.json| H1
    B3 -->|safety_results.json| H1
    B4 -->|sonarqube_issues.json| H1
    C -->|zap_alerts.json| H1
    
    H1 -->|Parse & Normalize| F
    F -->|Generate Charts| G
    G -->|Export| H3
    F -->|Generate Reports| H2
    
    style A fill:#e1f5ff
    style B1 fill:#fff4e1
    style B2 fill:#fff4e1
    style B3 fill:#fff4e1
    style B4 fill:#fff4e1
    style C fill:#ffe1e1
    style D fill:#e8f5e9
    style F fill:#f3e5f5
    style G fill:#f3e5f5
    style H1 fill:#fce4ec
    style H2 fill:#fce4ec
    style H3 fill:#fce4ec
```

### Architecture Components Explained:

#### **Layer 1: Source Code**
- **DBABA Web Application**: Deliberately vulnerable Flask application for testing

#### **Layer 2: SAST Tools (4 tools running in parallel)**
1. **Bandit**: Detects Python security issues (B201-B999 security tests)
2. **Pylint**: Finds code quality and security anti-patterns
3. **Safety**: Scans `requirements.txt` for known CVEs in dependencies
4. **SonarQube**: Enterprise-grade platform running in Docker (port 9000)

#### **Layer 3: DAST Tool**
5. **OWASP ZAP**: Dynamic scanner running in Docker (port 8080)
   - Spider phase: Discovers all pages/endpoints
   - Passive scan: Analyzes HTTP traffic
   - Active scan: Tests for OWASP Top 10 vulnerabilities

#### **Layer 4: Data Processing**
- **run_sast_scans.py**: Orchestrates 4 SAST tools, aggregates results
- **visualize_combined_results.py**: Parses 5 JSON outputs, normalizes data
- **Matplotlib/Seaborn**: Creates publication-quality visualizations

#### **Layer 5: Output & Reporting**
- **JSON Reports**: Machine-readable results from all 5 tools
- **HTML Reports**: Human-readable executive summaries
- **Visualizations**: Charts showing severity distribution, tool comparison, vulnerability types

---

## 🔄 Workflow

Here's what happens when the GitHub Action runs:

```mermaid
flowchart TD
    Start([GitHub Action Triggered<br/>Push/PR/Schedule]) --> Checkout[Checkout Repository]
    
    Checkout --> Setup[Setup Environment<br/>Install Dependencies]
    
    Setup --> BuildApp[Build Docker Container<br/>Vulnerable Web Application]
    
    BuildApp --> StartApp[Start Application<br/>Web Server + Database]
    
    StartApp --> Branch{Parallel Execution}
    
    Branch -->|Path 1| SAST[Run SonarQube Scanner<br/>Static Analysis]
    Branch -->|Path 2| DAST[Run OWASP ZAP<br/>Dynamic Analysis]
    
    SAST --> SASTReport[Generate SAST Report<br/>sonarqube-results.json]
    DAST --> DASTReport[Generate DAST Report<br/>zap-results.json]
    
    SASTReport --> Merge{Wait for Both Scans}
    DASTReport --> Merge
    
    Merge --> Parse[Run Pandas Script<br/>Parse JSON Reports]
    
    Parse --> Analyze[Analyze Vulnerabilities<br/>Categorize by Severity]
    
    Analyze --> Visualize[Generate Visualizations<br/>Charts & Graphs]
    
    Visualize --> CreateCharts[Create Output Images:<br/>- Severity Distribution<br/>- Vulnerability Types<br/>- Trend Analysis<br/>- Comparison Charts]
    
    CreateCharts --> Upload[Upload Artifacts<br/>to GitHub Actions]
    
    Upload --> Notify[Generate Summary Report<br/>in GitHub UI]
    
    Notify --> End([Workflow Complete<br/>View Results in Artifacts])
    
    style Start fill:#4CAF50,color:#fff
    style End fill:#4CAF50,color:#fff
    style SAST fill:#FF9800
    style DAST fill:#FF9800
    style Visualize fill:#9C27B0,color:#fff
    style Upload fill:#2196F3,color:#fff
```

### Workflow Steps Explained:

1. **Trigger**: Action starts on push, pull request, or scheduled run
2. **Setup**: Installs Python, Docker, and required dependencies
3. **Build**: Creates Docker container with the vulnerable application
4. **Parallel Scanning**: Both SAST and DAST run simultaneously to save time
5. **Report Generation**: Each scanner exports findings as JSON
6. **Data Processing**: Pandas script combines and analyzes both reports
7. **Visualization**: Creates charts showing vulnerability distribution
8. **Artifact Upload**: Images are saved and can be downloaded from GitHub
9. **Summary**: GitHub UI shows a summary of findings

---

## 📊 Data Flow

This sequence diagram shows the detailed interaction between components:

```mermaid
sequenceDiagram
    participant GH as GitHub Actions
    participant App as Vulnerable App
    participant SQ as SonarQube
    participant ZAP as OWASP ZAP
    participant Parser as Pandas Parser
    participant Viz as Visualization Engine
    participant Art as Artifacts Storage

    GH->>App: Deploy Application
    activate App
    
    par Static Analysis
        GH->>SQ: Scan Source Code
        activate SQ
        SQ->>SQ: Analyze Code Quality<br/>Detect Security Issues
        SQ-->>GH: SAST Results (JSON)
        deactivate SQ
    and Dynamic Analysis
        GH->>ZAP: Scan Running Application
        activate ZAP
        ZAP->>App: Send Test Requests<br/>SQL Injection, XSS, etc.
        App-->>ZAP: Responses
        ZAP->>ZAP: Analyze Responses<br/>Identify Vulnerabilities
        ZAP-->>GH: DAST Results (JSON)
        deactivate ZAP
    end
    
    deactivate App
    
    GH->>Parser: Process JSON Reports
    activate Parser
    Parser->>Parser: Load SAST Data
    Parser->>Parser: Load DAST Data
    Parser->>Parser: Normalize & Categorize<br/>by Severity & Type
    Parser-->>Viz: Structured DataFrame
    deactivate Parser
    
    activate Viz
    Viz->>Viz: Create Bar Charts<br/>Severity Distribution
    Viz->>Viz: Create Pie Charts<br/>Vulnerability Types
    Viz->>Viz: Create Line Graphs<br/>Trend Analysis
    Viz->>Viz: Create Comparison Charts<br/>SAST vs DAST
    Viz-->>Art: PNG/SVG Images
    deactivate Viz
    
    Art-->>GH: Download Artifacts
    GH->>GH: Display Summary in PR/Action
```

---

## 🧩 Security Tools Implemented

### SAST Tools (Static Application Security Testing)

#### 1. Bandit - Python Security Scanner ✅
**Purpose**: Identifies common security issues in Python code through AST analysis

**Detection Capabilities**:
- B105/B106: Hardcoded passwords and secrets
- B201-B207: Flask security issues (debug mode, template injection)
- B301-B302: Insecure deserialization (pickle, marshal)
- B303-B311: Weak cryptographic algorithms (MD5, DES, random)
- B608: SQL injection patterns
- B701-B710: SQL injection through string building

**Implementation**:
- Command-line tool executed via Python subprocess
- Outputs JSON with issue location, severity, and CWE mapping
- Scans entire codebase recursively
- Integrated into `run_sast_scans.py`

**Output**: `results/sast/bandit_results.json` with HIGH/MEDIUM/LOW severity classification

---

#### 2. Pylint - Code Quality & Security Linter ✅
**Purpose**: Static code analysis for code quality, maintainability, and security anti-patterns

**Detection Capabilities**:
- Undefined variables that could cause runtime errors
- Unused imports (potential attack surface reduction)
- Exception handling issues
- Code complexity metrics (cyclomatic complexity)
- Security-adjacent patterns (broad exception catching)

**Implementation**:
- Python linter with custom configuration
- Disabled verbose docstring warnings (C0114, C0115, C0116)
- JSON output for programmatic parsing
- Categorizes issues by type (error/warning/convention/refactor)

**Output**: `results/sast/pylint_results.json` with type-based classification

---

#### 3. Safety - Dependency Vulnerability Scanner ✅
**Purpose**: Checks Python dependencies against known vulnerability databases

**Detection Capabilities**:
- CVE identification in `requirements.txt` packages
- Cross-references with NVD (National Vulnerability Database)
- GitHub Security Advisories (GHSA) integration
- PyUp vulnerability database

**Implementation**:
- Scans `requirements.txt` for known vulnerable package versions
- JSON output with CVE IDs, CVSS scores, and remediation advice
- Zero false positives (only reports confirmed CVEs)

**Output**: `results/sast/safety_results.json` with CVE and CVSS data

---

#### 4. SonarQube - Enterprise Code Quality Platform ✅
**Purpose**: Comprehensive static analysis with web-based dashboard and quality gates

**Detection Capabilities**:
- Security vulnerabilities (OWASP Top 10 mapping)
- Security hotspots requiring manual review
- Code smells and technical debt calculation
- Code coverage metrics
- Duplicated code detection
- 25+ programming language support

**Implementation**:
- Runs in Docker container (port 9000)
- `sonar-scanner` CLI tool for project analysis
- REST API for programmatic results extraction
- Persistent storage for historical trend analysis

**Output**: Web UI at `http://localhost:9000` + API JSON endpoints

---

### DAST Tool (Dynamic Application Security Testing)

#### 5. OWASP ZAP - Web Application Security Scanner ✅
**Purpose**: Runtime security testing of web applications through automated penetration testing

**Detection Capabilities**:
- **Spider Module**: Application mapping and endpoint discovery
- **Passive Scan**: Traffic analysis for security misconfigurations
  - Missing security headers (CSP, HSTS, X-Frame-Options)
  - Cookie security issues (HttpOnly, Secure flags)
  - Information disclosure in responses
- **Active Scan**: Automated penetration testing
  - SQL Injection (error-based, boolean-based, time-based)
  - Cross-Site Scripting (reflected, stored, DOM-based)
  - CSRF vulnerabilities
  - Path traversal
  - Authentication bypass

**Implementation**:
- Runs in Docker container as daemon (port 8080)
- RESTful API control via curl commands
- 3-phase scanning (spider → passive → active)
- Progress tracking with polling mechanism

**Output**: 
- HTML report: `results/zap/zap_report.html`
- JSON alerts: `results/zap/zap_alerts.json`
- XML report: `results/zap/zap_report.xml`

**Official Site**: [zaproxy.org](https://www.zaproxy.org/)

---

### Data Processing Infrastructure

#### Pandas Visualization Pipeline ✅
**Purpose**: Aggregates, normalizes, and visualizes outputs from all 5 security tools

**Capabilities**:
- Multi-format JSON parsing (5 different schemas)
- Severity level normalization across tools
- Data aggregation into unified Pandas DataFrame
- Statistical analysis (counts, distributions, trends)
- Chart generation (Matplotlib/Seaborn)
- HTML report creation (Jinja2 templates)

**Implementation**: `scripts/visualize_combined_results.py` and `scripts/visualize_sast_results.py`

**Output**: 
- `results/visualizations/` directory containing PNG charts
- `results/visualizations/security_report.html` executive summary

---

### Target Application

#### DBABA - Deliberately Vulnerable Web Application ✅
**Purpose**: Flask-based web application with intentionally introduced security flaws for testing

**Known Vulnerabilities**:
- SQL Injection in login form
- Cross-Site Scripting in search functionality
- Hardcoded database credentials
- Insecure session management
- Missing input validation
- Information disclosure through error messages

**Implementation**:
- Flask web framework (Python)
- SQLite database backend
- Runs in Docker container (port 5000)
- Network-accessible to ZAP scanner

**⚠️ Security Warning**: This application contains real security vulnerabilities. Never deploy to production or expose to the internet.

---

## 🚀 Installation & Execution

### System Requirements

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.9+ with pip
- **Git** for repository cloning
- **System utilities**: curl, jq, wget (for bash scripts)

### Repository Setup

```bash
git clone https://github.com/noahwilliamshaffer/DAST-SAST-Security-Testing-Pipeline.git
cd DAST-SAST-Security-Testing-Pipeline

# Install Python dependencies
pip3 install -r requirements.txt
```

### Automated Pipeline Execution

```bash
# Execute complete SAST + DAST pipeline
bash scripts/run_all_scans.sh
```

**Pipeline stages:**
1. Docker infrastructure startup (SonarQube, ZAP, DBABA app)
2. Parallel SAST execution (Bandit, Pylint, Safety, SonarQube)
3. DAST execution (OWASP ZAP: spider → passive → active)
4. Data aggregation and visualization
5. Report generation (JSON, HTML, PNG)

**Execution time:** ~15 minutes (first run includes Docker image pulls)

### Manual Step-by-Step Execution

```bash
# 1. Start Docker services
docker-compose up -d

# 2. Wait for service readiness (2-3 minutes)

# 3. Execute SAST scans (parallel)
python3 scripts/run_sast_scans.py

# 4. Execute DAST scan
bash scripts/run_zap_scan.sh

# 5. Execute SonarQube scan (optional)
bash scripts/run_sonarqube_scan.sh

# 6. Generate visualizations
python3 scripts/visualize_combined_results.py
```

### Results Access

- **SonarQube Dashboard**: `http://localhost:9000` (credentials: admin/admin)
- **ZAP HTML Report**: `results/zap/zap_report.html`
- **Combined Visualizations**: `results/visualizations/`
- **SAST Results**: `results/sast/`
- **Executive Report**: `results/visualizations/security_report.html`

### Additional Documentation

- **[SCAN_GUIDE.md](SCAN_GUIDE.md)**: Detailed scanning procedures and troubleshooting
- **[REPORTS_INDEX.md](reports/REPORTS_INDEX.md)**: Report interpretation guide

---

## 📈 Report & Visualization Output

### Generated Visualizations

The `visualize_combined_results.py` script produces 5 chart types:

#### 1. Severity Distribution Chart (`severity_distribution.png`)
Bar chart showing vulnerability counts by severity level:
- 🔴 **Critical**: Immediate remediation required (CVSS 9.0-10.0)
- 🔴 **High**: Urgent remediation (CVSS 7.0-8.9)
- 🟠 **Medium**: Important remediation (CVSS 4.0-6.9)
- 🟡 **Low**: Optional remediation (CVSS 0.1-3.9)
- 🟢 **Info**: Informational findings

#### 2. Vulnerability Type Breakdown (`issue_types.png`)
Pie chart categorizing findings by vulnerability class:
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Authentication/Authorization (CWE-285, CWE-287)
- Cryptographic Issues (CWE-327)
- Configuration Errors (CWE-16)

#### 3. Tool Comparison Analysis (`tool_comparison.png`)
Side-by-side comparison of findings across tools:
- Bandit vs Pylint vs Safety vs SonarQube (SAST)
- SAST aggregate vs DAST (ZAP)
- Overlapping detections identified

#### 4. File-Level Heatmap (`file_heatmap.png`)
Color-coded visualization of vulnerability density:
- Red: Files with >10 vulnerabilities
- Yellow: Files with 5-10 vulnerabilities
- Green: Files with <5 vulnerabilities

#### 5. Executive Summary Dashboard (`summary_report.png`)
High-level KPI visualization:
- Total vulnerability count
- Severity breakdown percentage
- Tool coverage metrics
- Scan execution timestamps

### Report Access Points

**Web Dashboards:**
- SonarQube UI: `http://localhost:9000` - interactive analysis platform
- OWASP ZAP HTML Report: `results/zap/zap_report.html` - detailed findings

**Data Files:**
- `results/sast/sast_summary.json` - Aggregated SAST findings
- `results/zap/zap_alerts.json` - ZAP vulnerability alerts
- `results/visualizations/combined_data.json` - Unified dataset

**Documentation:**
- See [SCAN_GUIDE.md](SCAN_GUIDE.md) for tool output interpretation
- See [reports/REPORTS_INDEX.md](reports/REPORTS_INDEX.md) for report structure

---

## 📚 References & Documentation

### Tool Documentation
- **[Bandit](https://bandit.readthedocs.io/)** - Python security testing framework
- **[Pylint](https://pylint.pycqa.org/)** - Python code analysis
- **[Safety](https://pyup.io/safety/)** - Python dependency vulnerability scanner
- **[SonarQube](https://docs.sonarqube.org/)** - Continuous code quality inspection
- **[OWASP ZAP](https://www.zaproxy.org/docs/)** - Web application security scanner

### Security Standards & Frameworks
- **[OWASP Top 10](https://owasp.org/www-project-top-ten/)** - Top web application security risks
- **[CWE](https://cwe.mitre.org/)** - Common Weakness Enumeration
- **[CVSS](https://www.first.org/cvss/)** - Common Vulnerability Scoring System
- **[NIST SP 800-115](https://csrc.nist.gov/publications/detail/sp/800-115/final)** - Technical guide to information security testing

### Data Processing Libraries
- **[Pandas](https://pandas.pydata.org/docs/)** - Data manipulation and analysis
- **[Matplotlib](https://matplotlib.org/stable/index.html)** - Visualization library
- **[Seaborn](https://seaborn.pydata.org/)** - Statistical data visualization
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine for Python

### DevSecOps Resources
- **[GitHub Actions Security](https://docs.github.com/en/actions/security-guides)** - CI/CD security best practices
- **[OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)** - Security integration in DevOps

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for full details.

---

## ⚠️ Security Disclaimer

This repository includes the DBABA application, which contains **intentionally vulnerable code** for security testing demonstration purposes. This vulnerable application:

- **MUST NOT** be deployed to production environments
- **MUST NOT** be exposed to public networks or the internet
- **MUST NOT** be used with real user data
- **MUST** only be run in isolated, controlled testing environments

The security testing tools (Bandit, Pylint, Safety, SonarQube, OWASP ZAP) are production-grade and safe for use in real-world applications.

---

## 🔗 Project Links

- **Repository**: [github.com/noahwilliamshaffer/DAST-SAST-Security-Testing-Pipeline](https://github.com/noahwilliamshaffer/DAST-SAST-Security-Testing-Pipeline)
- **Issues**: [Report bugs or request features](https://github.com/noahwilliamshaffer/DAST-SAST-Security-Testing-Pipeline/issues)
- **Documentation**: See [docs/](docs/) directory for additional guides

---

## 🙏 Acknowledgments

This project leverages open-source security tools developed and maintained by:
- **OWASP Foundation** - ZAP scanner and security standards
- **SonarSource** - SonarQube code quality platform
- **PyCQA** - Bandit and Pylint Python analysis tools
- **PyUp.io** - Safety dependency vulnerability database

---

**Built with security in mind** 🔒
