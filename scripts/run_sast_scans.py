#!/usr/bin/env python3
"""
SAST Scanner Script
Runs multiple static analysis security testing tools on the dbaba application.
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
DBABA_PATH = PROJECT_ROOT / "dbaba-security-testing" / "M4-dbaba-2024" / "dbaba"
RESULTS_DIR = PROJECT_ROOT / "results" / "sast"

# Create results directory
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_bandit_scan():
    """Run Bandit security scanner on Python code."""
    print("🔍 Running Bandit (Python Security Scanner)...")
    
    output_file = RESULTS_DIR / "bandit_results.json"
    
    try:
        result = subprocess.run(
            [
                "bandit",
                "-r", str(DBABA_PATH),
                "-f", "json",
                "-o", str(output_file)
            ],
            capture_output=True,
            text=True
        )
        
        print(f"✅ Bandit scan complete. Results saved to {output_file}")
        
        # Also save text version for human reading
        text_output = RESULTS_DIR / "bandit_results.txt"
        subprocess.run(
            [
                "bandit",
                "-r", str(DBABA_PATH),
                "-f", "txt"
            ],
            stdout=open(text_output, 'w'),
            stderr=subprocess.PIPE
        )
        
        return True
    except Exception as e:
        print(f"❌ Bandit scan failed: {e}")
        return False


def run_pylint_scan():
    """Run Pylint code quality and security analysis."""
    print("🔍 Running Pylint (Code Quality & Security)...")
    
    output_file = RESULTS_DIR / "pylint_results.json"
    text_output = RESULTS_DIR / "pylint_results.txt"
    
    try:
        # Get all Python files
        python_files = list(DBABA_PATH.glob("*.py"))
        
        if not python_files:
            print("⚠️  No Python files found")
            return False
        
        # Run pylint with JSON output
        result = subprocess.run(
            ["pylint"] + [str(f) for f in python_files] + [
                "--output-format=json",
                "--disable=C0114,C0115,C0116",  # Disable some docstring warnings
            ],
            capture_output=True,
            text=True,
            cwd=str(DBABA_PATH)
        )
        
        # Save JSON output
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        
        # Run again for human-readable output
        result = subprocess.run(
            ["pylint"] + [str(f) for f in python_files] + [
                "--disable=C0114,C0115,C0116",
            ],
            capture_output=True,
            text=True,
            cwd=str(DBABA_PATH)
        )
        
        with open(text_output, 'w') as f:
            f.write(result.stdout)
        
        print(f"✅ Pylint scan complete. Results saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Pylint scan failed: {e}")
        return False


def run_safety_scan():
    """Run Safety to check for known vulnerabilities in dependencies."""
    print("🔍 Running Safety (Dependency Vulnerability Scanner)...")
    
    output_file = RESULTS_DIR / "safety_results.json"
    
    try:
        # Check if requirements file exists
        req_file = PROJECT_ROOT / "requirements.txt"
        if not req_file.exists():
            print("⚠️  No requirements.txt found, skipping Safety scan")
            return False
        
        result = subprocess.run(
            [
                "safety", "check",
                "--file", str(req_file),
                "--json"
            ],
            capture_output=True,
            text=True
        )
        
        # Save output
        with open(output_file, 'w') as f:
            f.write(result.stdout if result.stdout else "[]")
        
        # Text output
        text_output = RESULTS_DIR / "safety_results.txt"
        result = subprocess.run(
            ["safety", "check", "--file", str(req_file)],
            capture_output=True,
            text=True
        )
        
        with open(text_output, 'w') as f:
            f.write(result.stdout if result.stdout else "No vulnerabilities found")
        
        print(f"✅ Safety scan complete. Results saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Safety scan failed: {e}")
        return False


def create_summary_report():
    """Create a summary JSON combining all scan results."""
    print("📊 Creating summary report...")
    
    summary = {
        "scan_type": "SAST",
        "target": str(DBABA_PATH),
        "tools": {
            "bandit": {},
            "pylint": {},
            "safety": {}
        }
    }
    
    # Load Bandit results
    bandit_file = RESULTS_DIR / "bandit_results.json"
    if bandit_file.exists():
        try:
            with open(bandit_file, 'r') as f:
                bandit_data = json.load(f)
                summary["tools"]["bandit"] = {
                    "total_issues": len(bandit_data.get("results", [])),
                    "high_severity": len([r for r in bandit_data.get("results", []) if r.get("issue_severity") == "HIGH"]),
                    "medium_severity": len([r for r in bandit_data.get("results", []) if r.get("issue_severity") == "MEDIUM"]),
                    "low_severity": len([r for r in bandit_data.get("results", []) if r.get("issue_severity") == "LOW"]),
                }
        except Exception as e:
            print(f"⚠️  Could not parse Bandit results: {e}")
    
    # Load Pylint results
    pylint_file = RESULTS_DIR / "pylint_results.json"
    if pylint_file.exists():
        try:
            with open(pylint_file, 'r') as f:
                pylint_data = json.load(f)
                summary["tools"]["pylint"] = {
                    "total_issues": len(pylint_data),
                    "error": len([r for r in pylint_data if r.get("type") == "error"]),
                    "warning": len([r for r in pylint_data if r.get("type") == "warning"]),
                    "convention": len([r for r in pylint_data if r.get("type") == "convention"]),
                    "refactor": len([r for r in pylint_data if r.get("type") == "refactor"]),
                }
        except Exception as e:
            print(f"⚠️  Could not parse Pylint results: {e}")
    
    # Load Safety results
    safety_file = RESULTS_DIR / "safety_results.json"
    if safety_file.exists():
        try:
            with open(safety_file, 'r') as f:
                content = f.read()
                if content and content != "[]":
                    safety_data = json.loads(content)
                    summary["tools"]["safety"] = {
                        "total_vulnerabilities": len(safety_data),
                    }
                else:
                    summary["tools"]["safety"] = {
                        "total_vulnerabilities": 0,
                    }
        except Exception as e:
            print(f"⚠️  Could not parse Safety results: {e}")
            summary["tools"]["safety"] = {"total_vulnerabilities": 0}
    
    # Save summary
    summary_file = RESULTS_DIR / "sast_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Summary report created: {summary_file}")
    
    # Print summary to console
    print("\n" + "="*60)
    print("SAST SCAN SUMMARY")
    print("="*60)
    
    if "bandit" in summary["tools"] and summary["tools"]["bandit"]:
        bandit = summary["tools"]["bandit"]
        print(f"\n🔒 Bandit Security Issues:")
        print(f"   Total: {bandit.get('total_issues', 0)}")
        print(f"   🔴 High: {bandit.get('high_severity', 0)}")
        print(f"   🟠 Medium: {bandit.get('medium_severity', 0)}")
        print(f"   🟡 Low: {bandit.get('low_severity', 0)}")
    
    if "pylint" in summary["tools"] and summary["tools"]["pylint"]:
        pylint = summary["tools"]["pylint"]
        print(f"\n📋 Pylint Code Quality Issues:")
        print(f"   Total: {pylint.get('total_issues', 0)}")
        print(f"   🔴 Errors: {pylint.get('error', 0)}")
        print(f"   🟠 Warnings: {pylint.get('warning', 0)}")
        print(f"   🔵 Convention: {pylint.get('convention', 0)}")
        print(f"   🟣 Refactor: {pylint.get('refactor', 0)}")
    
    if "safety" in summary["tools"] and summary["tools"]["safety"]:
        safety = summary["tools"]["safety"]
        print(f"\n🛡️  Safety Dependency Vulnerabilities:")
        print(f"   Total: {safety.get('total_vulnerabilities', 0)}")
    
    print("\n" + "="*60)
    print(f"📁 All results saved to: {RESULTS_DIR}")
    print("="*60 + "\n")


def main():
    """Run all SAST scans."""
    print("="*60)
    print("SAST Security Scanner")
    print("Static Application Security Testing for DBABA")
    print("="*60 + "\n")
    
    print(f"Target: {DBABA_PATH}\n")
    
    # Check if target exists
    if not DBABA_PATH.exists():
        print(f"❌ Error: Target directory not found: {DBABA_PATH}")
        sys.exit(1)
    
    # Run scans
    results = {
        "bandit": run_bandit_scan(),
        "pylint": run_pylint_scan(),
        "safety": run_safety_scan(),
    }
    
    print("\n" + "-"*60 + "\n")
    
    # Create summary
    create_summary_report()
    
    # Check if all scans succeeded
    if all(results.values()):
        print("✅ All SAST scans completed successfully!")
        return 0
    else:
        print("⚠️  Some scans failed or were skipped.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

