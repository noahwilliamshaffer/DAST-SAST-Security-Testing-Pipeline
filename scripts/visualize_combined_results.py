#!/usr/bin/env python3
"""
Combined SAST + DAST Visualization Script
Creates charts from SonarQube (SAST) and OWASP ZAP (DAST) results.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
SONAR_RESULTS_DIR = PROJECT_ROOT / "results" / "sonarqube"
ZAP_RESULTS_DIR = PROJECT_ROOT / "results" / "zap"
VISUALIZATIONS_DIR = PROJECT_ROOT / "results" / "visualizations"

# Create visualizations directory
VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)


def load_sonarqube_results():
    """Load and parse SonarQube results."""
    sonar_file = SONAR_RESULTS_DIR / "sonarqube_issues.json"
    
    if not sonar_file.exists():
        print("⚠️  SonarQube results not found")
        return pd.DataFrame()
    
    try:
        with open(sonar_file, 'r') as f:
            data = json.load(f)
        
        issues = data.get("issues", [])
        
        if not issues:
            print("⚠️  No SonarQube issues found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "tool": "SonarQube",
                "source": "SAST",
                "severity": r.get("severity", "INFO"),
                "type": r.get("type", ""),
                "rule": r.get("rule", ""),
                "message": r.get("message", ""),
                "component": r.get("component", ""),
                "line": r.get("line", 0),
            }
            for r in issues
        ])
        
        # Map SonarQube severity to standard levels
        severity_map = {
            "BLOCKER": "CRITICAL",
            "CRITICAL": "CRITICAL",
            "MAJOR": "HIGH",
            "MINOR": "MEDIUM",
            "INFO": "LOW"
        }
        df["severity"] = df["severity"].map(severity_map).fillna("LOW")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading SonarQube results: {e}")
        return pd.DataFrame()


def load_zap_results():
    """Load and parse OWASP ZAP results."""
    zap_file = ZAP_RESULTS_DIR / "zap_alerts.json"
    
    if not zap_file.exists():
        print("⚠️  ZAP results not found")
        return pd.DataFrame()
    
    try:
        with open(zap_file, 'r') as f:
            data = json.load(f)
        
        alerts = data.get("alerts", [])
        
        if not alerts:
            print("⚠️  No ZAP alerts found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "tool": "OWASP ZAP",
                "source": "DAST",
                "severity": r.get("risk", "Informational").upper(),
                "type": r.get("alert", ""),
                "confidence": r.get("confidence", ""),
                "description": r.get("description", ""),
                "url": r.get("url", ""),
                "solution": r.get("solution", ""),
                "cwe": r.get("cweid", ""),
            }
            for r in alerts
        ])
        
        # Map ZAP risk to standard severity
        severity_map = {
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW",
            "INFORMATIONAL": "INFO"
        }
        df["severity"] = df["severity"].map(severity_map).fillna("INFO")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading ZAP results: {e}")
        return pd.DataFrame()


def create_sast_vs_dast_comparison(df):
    """Create comparison chart between SAST and DAST findings."""
    if df.empty:
        return
    
    print("📊 Creating SAST vs DAST comparison...")
    
    # Count by source and severity
    comparison = df.groupby(["source", "severity"]).size().unstack(fill_value=0)
    
    # Define colors
    severity_colors = {"CRITICAL": "#d32f2f", "HIGH": "#f57c00", "MEDIUM": "#fbc02d", "LOW": "#388e3c", "INFO": "#2196F3"}
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create grouped bar chart
    comparison.plot(kind='bar', ax=ax,
                   color=[severity_colors.get(col, "#999999") for col in comparison.columns],
                   edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel("Analysis Type", fontsize=12, fontweight='bold')
    ax.set_ylabel("Number of Issues", fontsize=12, fontweight='bold')
    ax.set_title("SAST vs DAST Security Findings", fontsize=14, fontweight='bold', pad=20)
    ax.legend(title="Severity", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "sast_vs_dast.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_combined_severity_chart(df):
    """Create combined severity distribution chart."""
    if df.empty:
        return
    
    print("📊 Creating combined severity distribution...")
    
    # Define severity order and colors
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    colors = {"CRITICAL": "#d32f2f", "HIGH": "#f57c00", "MEDIUM": "#fbc02d", "LOW": "#388e3c", "INFO": "#2196F3"}
    
    # Count by severity
    severity_counts = df["severity"].value_counts()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Filter to only severities that exist in data
    existing_severities = [s for s in severity_order if s in severity_counts.index]
    counts = [severity_counts[s] for s in existing_severities]
    bar_colors = [colors[s] for s in existing_severities]
    
    # Create bar chart
    bars = ax.bar(existing_severities, counts, color=bar_colors, edgecolor='black', linewidth=2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_xlabel("Severity Level", fontsize=14, fontweight='bold')
    ax.set_ylabel("Number of Issues", fontsize=14, fontweight='bold')
    ax.set_title("Combined SAST + DAST Security Issues by Severity", fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "combined_severity.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_tool_breakdown(df):
    """Create tool breakdown pie chart."""
    if df.empty:
        return
    
    print("📊 Creating tool breakdown...")
    
    tool_counts = df["tool"].value_counts()
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Pie chart for tool distribution
    colors1 = ["#3498db", "#e74c3c"]
    wedges1, texts1, autotexts1 = ax1.pie(tool_counts.values, labels=tool_counts.index,
                                            autopct='%1.1f%%', startangle=90,
                                            colors=colors1, textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    for autotext in autotexts1:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax1.set_title("Findings by Tool", fontsize=14, fontweight='bold', pad=20)
    
    # Bar chart for severity by tool
    tool_severity = df.groupby(["tool", "severity"]).size().unstack(fill_value=0)
    severity_colors = {"CRITICAL": "#d32f2f", "HIGH": "#f57c00", "MEDIUM": "#fbc02d", "LOW": "#388e3c", "INFO": "#2196F3"}
    
    tool_severity.plot(kind='barh', stacked=True, ax=ax2,
                      color=[severity_colors.get(col, "#999999") for col in tool_severity.columns],
                      edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel("Number of Issues", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Tool", fontsize=12, fontweight='bold')
    ax2.set_title("Severity Distribution by Tool", fontsize=14, fontweight='bold', pad=20)
    ax2.legend(title="Severity", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "tool_breakdown.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_vulnerability_types_chart(df):
    """Create vulnerability types comparison."""
    if df.empty:
        return
    
    print("📊 Creating vulnerability types chart...")
    
    # Get top 15 vulnerability types
    type_counts = df["type"].value_counts().head(15)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create horizontal bar chart
    colors = sns.color_palette("husl", len(type_counts))
    bars = ax.barh(range(len(type_counts)), type_counts.values, color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_yticks(range(len(type_counts)))
    ax.set_yticklabels(type_counts.index, fontsize=10)
    ax.set_xlabel("Number of Occurrences", fontsize=12, fontweight='bold')
    ax.set_title("Top 15 Vulnerability Types (SAST + DAST)", fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "vulnerability_types.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_executive_summary(sonar_df, zap_df, combined_df):
    """Create executive summary dashboard."""
    print("📊 Creating executive summary...")
    
    # Calculate statistics
    total_issues = len(combined_df)
    sast_issues = len(sonar_df)
    dast_issues = len(zap_df)
    
    critical = len(combined_df[combined_df["severity"] == "CRITICAL"])
    high = len(combined_df[combined_df["severity"] == "HIGH"])
    medium = len(combined_df[combined_df["severity"] == "MEDIUM"])
    low = len(combined_df[combined_df["severity"] == "LOW"])
    info = len(combined_df[combined_df["severity"] == "INFO"])
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 4, hspace=0.4, wspace=0.3)
    
    # Title
    fig.suptitle('DAST & SAST Security Testing - Executive Summary', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Summary boxes
    summary_data = [
        ("Total Issues", total_issues, "#2196F3"),
        ("SAST Findings", sast_issues, "#9C27B0"),
        ("DAST Findings", dast_issues, "#FF5722"),
        ("Critical", critical, "#d32f2f"),
        ("High", high, "#f57c00"),
        ("Medium", medium, "#fbc02d"),
        ("Low", low, "#388e3c"),
        ("Info", info, "#607D8B"),
    ]
    
    for idx, (label, value, color) in enumerate(summary_data):
        row = idx // 4
        col = idx % 4
        
        ax = fig.add_subplot(gs[row, col])
        ax.axis('off')
        
        # Create box
        ax.add_patch(plt.Rectangle((0.1, 0.2), 0.8, 0.6, 
                                   facecolor=color, edgecolor='black', 
                                   linewidth=3, transform=ax.transAxes))
        
        # Add value
        ax.text(0.5, 0.6, str(value),
               ha='center', va='center', fontsize=40, fontweight='bold',
               color='white', transform=ax.transAxes)
        
        # Add label
        ax.text(0.5, 0.35, label,
               ha='center', va='center', fontsize=13, fontweight='bold',
               color='white', transform=ax.transAxes)
    
    # Add mini charts in bottom row
    ax1 = fig.add_subplot(gs[2, :2])
    severity_counts = combined_df["severity"].value_counts()
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    existing = [s for s in severity_order if s in severity_counts.index]
    counts = [severity_counts[s] for s in existing]
    colors = ["#d32f2f", "#f57c00", "#fbc02d", "#388e3c", "#2196F3"][:len(existing)]
    
    ax1.bar(existing, counts, color=colors, edgecolor='black', linewidth=2)
    ax1.set_title("Severity Distribution", fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    ax2 = fig.add_subplot(gs[2, 2:])
    tool_counts = combined_df["tool"].value_counts()
    ax2.pie(tool_counts.values, labels=tool_counts.index, autopct='%1.1f%%',
           colors=["#3498db", "#e74c3c"], textprops={'fontweight': 'bold'})
    ax2.set_title("SAST vs DAST Distribution", fontweight='bold')
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.5, 0.02, f'Report Generated: {timestamp}',
            ha='center', va='center', fontsize=11, style='italic')
    
    output_file = VISUALIZATIONS_DIR / "executive_summary.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    plt.close()


def generate_html_report(sonar_df, zap_df, combined_df):
    """Generate comprehensive HTML report."""
    print("📄 Creating comprehensive HTML report...")
    
    total = len(combined_df)
    sast = len(sonar_df)
    dast = len(zap_df)
    critical = len(combined_df[combined_df["severity"] == "CRITICAL"])
    high = len(combined_df[combined_df["severity"] == "HIGH"])
    medium = len(combined_df[combined_df["severity"] == "MEDIUM"])
    low = len(combined_df[combined_df["severity"] == "LOW"])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DAST & SAST Security Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background-color: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 36px;
                margin-bottom: 10px;
            }}
            .header p {{
                font-size: 18px;
                opacity: 0.9;
            }}
            .content {{
                padding: 40px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .stat-card {{
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-card h3 {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .stat-card p {{
                font-size: 16px;
                opacity: 0.9;
            }}
            .total {{ background: linear-gradient(135deg, #2196F3, #1976D2); }}
            .sast {{ background: linear-gradient(135deg, #9C27B0, #7B1FA2); }}
            .dast {{ background: linear-gradient(135deg, #FF5722, #E64A19); }}
            .critical {{ background: linear-gradient(135deg, #d32f2f, #b71c1c); }}
            .high {{ background: linear-gradient(135deg, #f57c00, #e65100); }}
            .medium {{ background: linear-gradient(135deg, #fbc02d, #f9a825); }}
            .low {{ background: linear-gradient(135deg, #388e3c, #2e7d32); }}
            
            .section {{
                margin: 40px 0;
            }}
            .section h2 {{
                color: #2c3e50;
                border-left: 5px solid #667eea;
                padding-left: 15px;
                margin-bottom: 20px;
                font-size: 28px;
            }}
            .chart-container {{
                margin: 30px 0;
                text-align: center;
            }}
            .chart-container img {{
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            th, td {{
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}
            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 12px;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .badge {{
                padding: 6px 12px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
            }}
            .badge-critical {{ background-color: #d32f2f; }}
            .badge-high {{ background-color: #f57c00; }}
            .badge-medium {{ background-color: #fbc02d; color: #333; }}
            .badge-low {{ background-color: #388e3c; }}
            .badge-info {{ background-color: #2196F3; }}
            
            .footer {{
                background-color: #2c3e50;
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .tools-used {{
                display: flex;
                justify-content: space-around;
                margin: 30px 0;
                flex-wrap: wrap;
            }}
            .tool-box {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                flex: 1;
                margin: 10px;
                min-width: 250px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .tool-box h3 {{
                color: #667eea;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Security Testing Report</h1>
                <p>DAST & SAST Analysis for DBABA Application</p>
                <p style="font-size: 14px; margin-top: 10px;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <h2>📊 Executive Summary</h2>
                    <div class="stats-grid">
                        <div class="stat-card total">
                            <h3>{total}</h3>
                            <p>Total Issues Found</p>
                        </div>
                        <div class="stat-card sast">
                            <h3>{sast}</h3>
                            <p>SAST Findings (SonarQube)</p>
                        </div>
                        <div class="stat-card dast">
                            <h3>{dast}</h3>
                            <p>DAST Findings (OWASP ZAP)</p>
                        </div>
                        <div class="stat-card critical">
                            <h3>{critical}</h3>
                            <p>Critical Severity</p>
                        </div>
                        <div class="stat-card high">
                            <h3>{high}</h3>
                            <p>High Severity</p>
                        </div>
                        <div class="stat-card medium">
                            <h3>{medium}</h3>
                            <p>Medium Severity</p>
                        </div>
                        <div class="stat-card low">
                            <h3>{low}</h3>
                            <p>Low Severity</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🛠️ Tools Used</h2>
                    <div class="tools-used">
                        <div class="tool-box">
                            <h3>SonarQube</h3>
                            <p><strong>Type:</strong> SAST (Static Analysis)</p>
                            <p>Industry-leading code quality and security analysis</p>
                            <p><strong>Findings:</strong> {sast}</p>
                        </div>
                        <div class="tool-box">
                            <h3>OWASP ZAP</h3>
                            <p><strong>Type:</strong> DAST (Dynamic Analysis)</p>
                            <p>Open-source web application security scanner</p>
                            <p><strong>Findings:</strong> {dast}</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Visual Analysis</h2>
                    
                    <div class="chart-container">
                        <h3>Executive Summary Dashboard</h3>
                        <img src="executive_summary.png" alt="Executive Summary">
                    </div>
                    
                    <div class="chart-container">
                        <h3>Combined Severity Distribution</h3>
                        <img src="combined_severity.png" alt="Severity Distribution">
                    </div>
                    
                    <div class="chart-container">
                        <h3>SAST vs DAST Comparison</h3>
                        <img src="sast_vs_dast.png" alt="SAST vs DAST">
                    </div>
                    
                    <div class="chart-container">
                        <h3>Tool Breakdown Analysis</h3>
                        <img src="tool_breakdown.png" alt="Tool Breakdown">
                    </div>
                    
                    <div class="chart-container">
                        <h3>Top Vulnerability Types</h3>
                        <img src="vulnerability_types.png" alt="Vulnerability Types">
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Detailed Findings (Top 50)</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Tool</th>
                                <th>Type</th>
                                <th>Severity</th>
                                <th>Issue</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Add top 50 issues
    severity_class_map = {
        "CRITICAL": "badge-critical",
        "HIGH": "badge-high",
        "MEDIUM": "badge-medium",
        "LOW": "badge-low",
        "INFO": "badge-info"
    }
    
    for _, row in combined_df.head(50).iterrows():
        severity_class = severity_class_map.get(row["severity"], "badge-info")
        issue_text = row.get("message", row.get("description", ""))[:150]
        
        html_content += f"""
                            <tr>
                                <td>{row['tool']}</td>
                                <td>{row.get('type', 'N/A')}</td>
                                <td><span class="badge {severity_class}">{row['severity']}</span></td>
                                <td>{issue_text}...</td>
                            </tr>
        """
    
    html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>💡 Recommendations</h2>
                    <ul style="line-height: 2; font-size: 16px;">
                        <li><strong>Critical & High Issues:</strong> Address immediately - these represent serious security vulnerabilities</li>
                        <li><strong>Medium Issues:</strong> Schedule for resolution in the next development cycle</li>
                        <li><strong>Low Issues:</strong> Address as part of ongoing code quality improvements</li>
                        <li><strong>Review Both SAST & DAST:</strong> Each tool finds different types of vulnerabilities - both are important</li>
                        <li><strong>Continuous Scanning:</strong> Integrate these tools into your CI/CD pipeline</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>DAST & SAST Security Testing Pipeline</strong></p>
                <p>Powered by SonarQube and OWASP ZAP</p>
                <p style="margin-top: 10px; opacity: 0.8;">For more details, visit the SonarQube dashboard at http://localhost:9000</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    output_file = VISUALIZATIONS_DIR / "combined_security_report.html"
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Saved: {output_file}")


def main():
    """Main visualization function."""
    print("="*60)
    print("Combined SAST + DAST Visualization")
    print("SonarQube + OWASP ZAP Results")
    print("="*60 + "\n")
    
    # Load results
    print("📂 Loading scan results...\n")
    sonar_df = load_sonarqube_results()
    zap_df = load_zap_results()
    
    if sonar_df.empty and zap_df.empty:
        print("❌ No scan results found!")
        print("   Run scans first: bash scripts/run_all_scans.sh")
        return 1
    
    # Combine results
    all_dfs = [df for df in [sonar_df, zap_df] if not df.empty]
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"✅ Loaded results:")
    print(f"   • SonarQube (SAST): {len(sonar_df)} findings")
    print(f"   • OWASP ZAP (DAST): {len(zap_df)} findings")
    print(f"   • Total: {len(combined_df)} findings\n")
    print("-"*60 + "\n")
    
    # Create visualizations
    create_combined_severity_chart(combined_df)
    create_sast_vs_dast_comparison(combined_df)
    create_tool_breakdown(combined_df)
    create_vulnerability_types_chart(combined_df)
    create_executive_summary(sonar_df, zap_df, combined_df)
    generate_html_report(sonar_df, zap_df, combined_df)
    
    print("\n" + "="*60)
    print(f"✅ All visualizations saved to: {VISUALIZATIONS_DIR}")
    print(f"📄 Open the report: {VISUALIZATIONS_DIR}/combined_security_report.html")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

