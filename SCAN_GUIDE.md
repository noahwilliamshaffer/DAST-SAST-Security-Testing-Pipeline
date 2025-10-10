# 🔒 Security Scanning Guide

Complete guide for running SAST (SonarQube) and DAST (OWASP ZAP) security scans on the DBABA application.

---

## 🚀 Quick Start

### Option 1: Run Everything (Recommended)
```bash
# Run complete SAST + DAST pipeline
bash scripts/run_all_scans.sh
```

This will:
1. Start SonarQube, OWASP ZAP, and DBABA app in Docker
2. Run SAST scan with SonarQube
3. Run DAST scan with OWASP ZAP  
4. Generate visual reports and charts
5. Create comprehensive HTML report

**Time:** ~10-15 minutes (first run includes Docker image downloads)

---

## 📋 Prerequisites

### Required Software
- **Docker** and **Docker Compose**
- **Python 3.9+**
- **curl**, **jq** (for API calls)
- **wget**, **unzip** (for sonar-scanner installation)

### Install Dependencies
```bash
# Install Python packages
pip3 install pandas matplotlib seaborn jinja2 numpy

# Check Docker is running
docker --version
docker-compose --version
```

---

## 🔧 Step-by-Step Manual Process

### Step 1: Start Services

```bash
# Start all Docker containers
docker-compose up -d

# Check status
docker-compose ps
```

**Services Started:**
- `sonarqube` - http://localhost:9000 (SAST)
- `zap` - http://localhost:8080 (DAST)
- `dbaba-app` - http://localhost:5000 (Target Application)

**Wait Time:** 2-3 minutes for SonarQube to fully start

### Step 2: Run SonarQube SAST Scan

```bash
# Run static analysis
bash scripts/run_sonarqube_scan.sh
```

**What It Does:**
- Installs sonar-scanner if not present
- Scans all Python code in dbaba application
- Uploads results to SonarQube server
- Exports JSON reports

**Results:**
- Console summary
- `results/sonarqube/sonarqube_issues.json`
- `results/sonarqube/sonarqube_metrics.json`
- Web UI: http://localhost:9000

### Step 3: Run OWASP ZAP DAST Scan

```bash
# Run dynamic analysis
bash scripts/run_zap_scan.sh
```

**What It Does:**
- Spiders the web application (discovers pages)
- Performs passive scanning (analyzes traffic)
- Runs active scanning (security tests)
- Exports multiple report formats

**Results:**
- Console summary
- `results/zap/zap_alerts.json`
- `results/zap/zap_report.html`
- `results/zap/zap_report.xml`

### Step 4: Generate Visualizations

```bash
# Create charts and reports
python3 scripts/visualize_combined_results.py
```

**Generates:**
- Executive summary dashboard
- Severity distribution charts
- SAST vs DAST comparison
- Tool breakdown analysis
- Vulnerability types chart
- Comprehensive HTML report

**Output Location:** `results/visualizations/`

---

## 📊 Understanding the Results

### Severity Levels

| Level | Priority | Action |
|-------|----------|--------|
| 🔴 **CRITICAL** | Immediate | Fix within 24 hours |
| 🔴 **HIGH** | Urgent | Fix within 1 week |
| 🟠 **MEDIUM** | Important | Fix in next sprint |
| 🟡 **LOW** | Minor | Fix when convenient |
| ℹ️ **INFO** | FYI | Consider for improvement |

### SAST vs DAST

**SAST (SonarQube)** finds:
- Code quality issues
- Security vulnerabilities in source code
- Hard-coded secrets
- Insecure cryptography
- Code smells

**DAST (OWASP ZAP)** finds:
- Runtime vulnerabilities
- SQL Injection
- Cross-Site Scripting (XSS)
- Missing security headers
- Authentication issues
- CSRF vulnerabilities

---

## 🌐 Web Interfaces

### SonarQube Dashboard
**URL:** http://localhost:9000  
**Credentials:** admin / admin (first login will prompt to change)

**Features:**
- Project overview
- Issues browser
- Security hotspots
- Code metrics
- Quality gates

### OWASP ZAP Reports
**HTML Report:** `results/zap/zap_report.html`

Open in browser to see:
- Alert summary
- Risk levels
- Detailed findings
- Solutions

### Combined Report
**HTML Report:** `results/visualizations/combined_security_report.html`

Professional report with:
- Executive summary
- Visual charts
- Tool comparison
- Detailed findings
- Recommendations

---

## 📁 Results Directory Structure

```
results/
├── sonarqube/
│   ├── sonarqube_issues.json    # All SonarQube findings
│   └── sonarqube_metrics.json   # Project metrics
├── zap/
│   ├── zap_alerts.json          # ZAP findings (JSON)
│   ├── zap_report.html          # ZAP report (HTML)
│   └── zap_report.xml           # ZAP report (XML)
└── visualizations/
    ├── executive_summary.png
    ├── combined_severity.png
    ├── sast_vs_dast.png
    ├── tool_breakdown.png
    ├── vulnerability_types.png
    └── combined_security_report.html  # Main report
```

---

## 🔍 Interpreting Findings

### SonarQube Issues

Example findings you might see:
- **Hard-coded credentials** - Passwords in source code
- **SQL injection risks** - Unsanitized SQL queries
- **Path traversal** - Unsafe file operations
- **Weak cryptography** - Insecure algorithms

### ZAP Alerts

Example findings you might see:
- **SQL Injection** - Database manipulation possible
- **XSS** - JavaScript injection possible
- **Missing headers** - Security headers not set
- **Insecure cookies** - Cookie security issues

---

## ⚙️ Configuration

### SonarQube Configuration
Edit `sonar-project.properties`:
```properties
sonar.projectKey=dbaba-security-testing
sonar.projectName=DBABA Address Book Application
sonar.sources=dbaba-security-testing/M4-dbaba-2024/dbaba
sonar.python.version=3.12
```

### Docker Configuration
Edit `docker-compose.yml` to:
- Change ports
- Add more services
- Modify resource limits

---

## 🐛 Troubleshooting

### SonarQube Not Starting
```bash
# Check logs
docker-compose logs sonarqube

# Restart service
docker-compose restart sonarqube

# Wait 2-3 minutes, then check
curl http://localhost:9000/api/system/status
```

### ZAP Scan Failing
```bash
# Check ZAP logs
docker-compose logs zap

# Verify target app is running
curl http://localhost:5000

# Restart ZAP
docker-compose restart zap
```

### sonar-scanner Not Found
```bash
# The script will auto-install it, or manually:
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
unzip sonar-scanner-cli-5.0.1.3006-linux.zip
sudo mv sonar-scanner-5.0.1.3006-linux /opt/sonar-scanner
sudo ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
```

### Permission Denied on Scripts
```bash
# Make scripts executable
chmod +x scripts/*.sh scripts/*.py
```

---

## 🛑 Stopping Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 📊 Exporting Results

### Export for CI/CD
```bash
# JSON files are ready for programmatic use
cat results/sonarqube/sonarqube_issues.json | jq '.issues | length'
cat results/zap/zap_alerts.json | jq '.alerts | length'
```

### Share with Team
```bash
# Package all results
tar -czf security-scan-results.tar.gz results/

# Or just the HTML reports
cp results/visualizations/combined_security_report.html ~/Desktop/
cp results/zap/zap_report.html ~/Desktop/
```

---

## 🔄 Continuous Integration

### GitHub Actions Example

Create `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Security Scans
        run: |
          docker-compose up -d
          sleep 120  # Wait for services
          bash scripts/run_all_scans.sh
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: security-reports
          path: results/
```

---

## 📚 Additional Resources

### SonarQube
- Documentation: https://docs.sonarqube.org/
- Python Rules: https://rules.sonarsource.com/python/
- Community: https://community.sonarsource.com/

### OWASP ZAP
- Documentation: https://www.zaproxy.org/docs/
- API: https://www.zaproxy.org/docs/api/
- Getting Started: https://www.zaproxy.org/getting-started/

### Security Best Practices
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE: https://cwe.mitre.org/
- SANS Top 25: https://www.sans.org/top25-software-errors/

---

## 💡 Tips

1. **First Run:** Takes longer due to Docker image downloads (~5-10 min)
2. **Incremental Scans:** Subsequent scans are much faster (~5 min)
3. **Review Regularly:** Run scans after major code changes
4. **Fix High Severity First:** Prioritize critical and high severity issues
5. **Understand False Positives:** Not all findings are exploitable
6. **Both Tools Matter:** SAST and DAST find different issues

---

## 🆘 Getting Help

- Check logs: `docker-compose logs [service-name]`
- Verify services: `docker-compose ps`
- Test connectivity: `curl http://localhost:[port]`
- Read error messages carefully
- Check the documentation links above

---

**Happy Secure Coding! 🔒**

