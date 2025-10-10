#!/bin/bash
# OWASP ZAP DAST Scanner Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/results/zap"
ZAP_API_KEY="changeme"
TARGET_URL="http://dbaba-app:5000"

echo "============================================================"
echo "OWASP ZAP DAST Scanner"
echo "============================================================"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check if ZAP is running
echo "🔍 Checking OWASP ZAP daemon..."
if ! curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "❌ OWASP ZAP is not running!"
    echo "   Start it with: docker-compose up -d zap"
    exit 1
fi

echo "✅ OWASP ZAP is running"
echo ""

# Check if target application is running
echo "🔍 Checking target application..."
if ! curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "❌ Target application is not running!"
    echo "   Start it with: docker-compose up -d dbaba-app"
    exit 1
fi

echo "✅ Target application is running at http://localhost:5000"
echo ""

# Spider the application
echo "🕷️  Phase 1: Spidering the application (discovering pages)..."
SPIDER_ID=$(curl -s "http://localhost:8080/JSON/spider/action/scan/?apikey=$ZAP_API_KEY&url=http://localhost:5000&maxChildren=10" | jq -r '.scan')

echo "   Spider scan ID: $SPIDER_ID"
echo "   Waiting for spider to complete..."

# Wait for spider to complete
while true; do
    PROGRESS=$(curl -s "http://localhost:8080/JSON/spider/view/status/?apikey=$ZAP_API_KEY&scanId=$SPIDER_ID" | jq -r '.status')
    echo "   Spider progress: $PROGRESS%"
    
    if [ "$PROGRESS" = "100" ]; then
        break
    fi
    sleep 2
done

echo "✅ Spider complete"
echo ""

# Passive scan (automatically runs during spidering)
echo "🔍 Phase 2: Passive scanning (analyzing traffic)..."
sleep 5
echo "✅ Passive scan complete"
echo ""

# Active scan
echo "🎯 Phase 3: Active scanning (security testing)..."
SCAN_ID=$(curl -s "http://localhost:8080/JSON/ascan/action/scan/?apikey=$ZAP_API_KEY&url=http://localhost:5000&recurse=true&inScopeOnly=false" | jq -r '.scan')

echo "   Active scan ID: $SCAN_ID"
echo "   This may take several minutes..."

# Wait for active scan to complete
while true; do
    PROGRESS=$(curl -s "http://localhost:8080/JSON/ascan/view/status/?apikey=$ZAP_API_KEY&scanId=$SCAN_ID" | jq -r '.status')
    echo "   Active scan progress: $PROGRESS%"
    
    if [ "$PROGRESS" = "100" ]; then
        break
    fi
    sleep 5
done

echo "✅ Active scan complete"
echo ""

# Generate reports
echo "📄 Generating reports..."

# HTML Report
curl -s "http://localhost:8080/OTHER/core/other/htmlreport/?apikey=$ZAP_API_KEY" \
    > "$RESULTS_DIR/zap_report.html"

# JSON Report
curl -s "http://localhost:8080/JSON/core/view/alerts/?apikey=$ZAP_API_KEY&baseurl=http://localhost:5000" \
    > "$RESULTS_DIR/zap_alerts.json"

# XML Report
curl -s "http://localhost:8080/OTHER/core/other/xmlreport/?apikey=$ZAP_API_KEY" \
    > "$RESULTS_DIR/zap_report.xml"

echo "✅ Reports generated"
echo ""

# Summary
echo "============================================================"
echo "SCAN SUMMARY"
echo "============================================================"

ALERTS=$(curl -s "http://localhost:8080/JSON/core/view/numberOfAlerts/?apikey=$ZAP_API_KEY" | jq -r '.numberOfAlerts')
HIGH=$(curl -s "http://localhost:8080/JSON/core/view/alertsSummary/?apikey=$ZAP_API_KEY&baseurl=" | jq -r '.alertsSummary[] | select(.risk=="High") | .count // 0' | head -1)
MEDIUM=$(curl -s "http://localhost:8080/JSON/core/view/alertsSummary/?apikey=$ZAP_API_KEY&baseurl=" | jq -r '.alertsSummary[] | select(.risk=="Medium") | .count // 0' | head -1)
LOW=$(curl -s "http://localhost:8080/JSON/core/view/alertsSummary/?apikey=$ZAP_API_KEY&baseurl=" | jq -r '.alertsSummary[] | select(.risk=="Low") | .count // 0' | head -1)
INFO=$(curl -s "http://localhost:8080/JSON/core/view/alertsSummary/?apikey=$ZAP_API_KEY&baseurl=" | jq -r '.alertsSummary[] | select(.risk=="Informational") | .count // 0' | head -1)

echo ""
echo "🎯 Total Alerts: ${ALERTS:-0}"
echo "🔴 High Risk: ${HIGH:-0}"
echo "🟠 Medium Risk: ${MEDIUM:-0}"
echo "🟡 Low Risk: ${LOW:-0}"
echo "ℹ️  Informational: ${INFO:-0}"
echo ""
echo "============================================================"
echo "📁 Results saved to: $RESULTS_DIR"
echo "📄 View HTML report: $RESULTS_DIR/zap_report.html"
echo "============================================================"
echo ""

