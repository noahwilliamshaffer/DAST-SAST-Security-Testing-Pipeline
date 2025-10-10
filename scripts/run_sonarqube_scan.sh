#!/bin/bash
# SonarQube SAST Scanner Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/results/sonarqube"

echo "============================================================"
echo "SonarQube SAST Scanner"
echo "============================================================"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check if SonarQube is running
echo "🔍 Checking SonarQube server..."
if ! curl -s http://localhost:9000/api/system/status | grep -q "UP"; then
    echo "❌ SonarQube is not running!"
    echo "   Start it with: docker-compose up -d sonarqube"
    echo "   Wait ~2 minutes for startup, then access: http://localhost:9000"
    echo "   Default credentials: admin/admin"
    exit 1
fi

echo "✅ SonarQube server is running"
echo ""

# Wait for SonarQube to be ready
echo "⏳ Waiting for SonarQube to be fully ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -u admin:admin http://localhost:9000/api/system/status | grep -q '"status":"UP"'; then
        echo "✅ SonarQube is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ SonarQube did not become ready in time"
    exit 1
fi

echo ""
echo "🔍 Running SonarQube scanner..."
echo ""

# Check if sonar-scanner is installed
if ! command -v sonar-scanner &> /dev/null; then
    echo "⚠️  sonar-scanner not found. Installing..."
    
    # Download and install sonar-scanner
    cd /tmp
    SONAR_SCANNER_VERSION="5.0.1.3006"
    wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip
    unzip -q sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip
    sudo mv sonar-scanner-${SONAR_SCANNER_VERSION}-linux /opt/sonar-scanner
    sudo ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
    
    echo "✅ sonar-scanner installed"
fi

# Run the scan
cd "$PROJECT_ROOT"
sonar-scanner \
    -Dsonar.host.url=http://localhost:9000 \
    -Dsonar.login=admin \
    -Dsonar.password=admin \
    -Dsonar.projectKey=dbaba-security-testing \
    -Dsonar.projectName="DBABA Address Book" \
    -Dsonar.sources=dbaba-security-testing/M4-dbaba-2024/dbaba \
    -Dsonar.python.version=3.12 \
    -Dsonar.sourceEncoding=UTF-8

echo ""
echo "✅ SonarQube scan complete!"
echo ""
echo "============================================================"
echo "📊 View results at: http://localhost:9000"
echo "============================================================"
echo ""

# Export results as JSON
echo "📥 Exporting results as JSON..."

# Wait for analysis to complete
sleep 5

# Get project analysis results
curl -s -u admin:admin \
    "http://localhost:9000/api/issues/search?componentKeys=dbaba-security-testing&ps=500" \
    > "$RESULTS_DIR/sonarqube_issues.json"

# Get metrics
curl -s -u admin:admin \
    "http://localhost:9000/api/measures/component?component=dbaba-security-testing&metricKeys=bugs,vulnerabilities,code_smells,security_hotspots,coverage,duplicated_lines_density" \
    > "$RESULTS_DIR/sonarqube_metrics.json"

echo "✅ Results exported to: $RESULTS_DIR"
echo ""

