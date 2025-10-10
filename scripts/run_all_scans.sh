#!/bin/bash
# Master Script to Run Complete SAST + DAST Security Testing

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     DAST & SAST Security Testing Pipeline                 ║"
echo "║     SonarQube (SAST) + OWASP ZAP (DAST)                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Start services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Starting Docker services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready (this may take 2-3 minutes)..."
echo ""

# Wait for SonarQube
echo "   Waiting for SonarQube..."
for i in {1..60}; do
    if curl -s http://localhost:9000/api/system/status 2>/dev/null | grep -q "UP"; then
        echo "   ✅ SonarQube is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "   ⚠️  SonarQube took longer than expected"
    fi
    sleep 3
done

# Wait for ZAP
echo "   Waiting for OWASP ZAP..."
for i in {1..30}; do
    if curl -s http://localhost:8080 2>/dev/null > /dev/null; then
        echo "   ✅ OWASP ZAP is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  OWASP ZAP took longer than expected"
    fi
    sleep 2
done

# Wait for DBABA app
echo "   Waiting for DBABA application..."
for i in {1..20}; do
    if curl -s http://localhost:5000 2>/dev/null > /dev/null; then
        echo "   ✅ DBABA application is ready"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "   ⚠️  DBABA application took longer than expected"
    fi
    sleep 2
done

echo ""
echo "✅ All services are running!"
echo ""

# Step 2: Run SonarQube SAST Scan
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Running SonarQube SAST Scan..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

bash scripts/run_sonarqube_scan.sh || echo "⚠️  SonarQube scan had issues (continuing...)"

echo ""

# Step 3: Run OWASP ZAP DAST Scan
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Running OWASP ZAP DAST Scan..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

bash scripts/run_zap_scan.sh || echo "⚠️  ZAP scan had issues (continuing...)"

echo ""

# Step 4: Generate Visualizations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Generating Visualizations..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "scripts/visualize_combined_results.py" ]; then
    python3 scripts/visualize_combined_results.py || echo "⚠️  Visualization had issues"
else
    echo "⚠️  Combined visualization script not found yet"
fi

echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   SCAN COMPLETE!                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results Location:"
echo "   • SonarQube Results:  results/sonarqube/"
echo "   • ZAP Results:        results/zap/"
echo "   • Visualizations:     results/visualizations/"
echo ""
echo "🌐 Web Interfaces:"
echo "   • SonarQube:  http://localhost:9000  (admin/admin)"
echo "   • ZAP Daemon: http://localhost:8080"
echo "   • DBABA App:  http://localhost:5000"
echo ""
echo "📄 Key Files:"
echo "   • ZAP HTML Report:    results/zap/zap_report.html"
echo "   • Combined Report:    results/visualizations/security_report.html"
echo ""
echo "To stop services: docker-compose down"
echo ""

