#!/usr/bin/env python3
"""
SAST Results Visualization Script
Creates charts and graphs from SAST scan results.
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
RESULTS_DIR = PROJECT_ROOT / "results" / "sast"
VISUALIZATIONS_DIR = PROJECT_ROOT / "results" / "visualizations"

# Create visualizations directory
VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)


def load_bandit_results():
    """Load and parse Bandit results."""
    bandit_file = RESULTS_DIR / "bandit_results.json"
    
    if not bandit_file.exists():
        print("⚠️  Bandit results not found")
        return pd.DataFrame()
    
    try:
        with open(bandit_file, 'r') as f:
            data = json.load(f)
        
        results = data.get("results", [])
        
        if not results:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "tool": "Bandit",
                "severity": r.get("issue_severity", "UNKNOWN"),
                "confidence": r.get("issue_confidence", "UNKNOWN"),
                "type": r.get("test_id", ""),
                "description": r.get("issue_text", ""),
                "file": r.get("filename", ""),
                "line": r.get("line_number", 0),
            }
            for r in results
        ])
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading Bandit results: {e}")
        return pd.DataFrame()


def load_pylint_results():
    """Load and parse Pylint results."""
    pylint_file = RESULTS_DIR / "pylint_results.json"
    
    if not pylint_file.exists():
        print("⚠️  Pylint results not found")
        return pd.DataFrame()
    
    try:
        with open(pylint_file, 'r') as f:
            data = json.load(f)
        
        if not data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "tool": "Pylint",
                "severity": r.get("type", "").upper(),
                "type": r.get("symbol", ""),
                "description": r.get("message", ""),
                "file": r.get("path", ""),
                "line": r.get("line", 0),
                "category": r.get("message-id", ""),
            }
            for r in data
        ])
        
        # Map Pylint types to standard severity
        severity_map = {
            "ERROR": "HIGH",
            "WARNING": "MEDIUM",
            "CONVENTION": "LOW",
            "REFACTOR": "LOW",
            "FATAL": "CRITICAL"
        }
        df["severity"] = df["severity"].map(severity_map).fillna("LOW")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading Pylint results: {e}")
        return pd.DataFrame()


def load_safety_results():
    """Load and parse Safety results."""
    safety_file = RESULTS_DIR / "safety_results.json"
    
    if not safety_file.exists():
        print("⚠️  Safety results not found")
        return pd.DataFrame()
    
    try:
        with open(safety_file, 'r') as f:
            content = f.read()
            if not content or content == "[]":
                return pd.DataFrame()
            data = json.loads(content)
        
        if not data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "tool": "Safety",
                "severity": "HIGH",  # Dependency vulnerabilities are typically high priority
                "type": "Dependency Vulnerability",
                "description": f"{r.get('vulnerability', '')} in {r.get('package', '')}",
                "package": r.get("package", ""),
                "version": r.get("installed_version", ""),
            }
            for r in data
        ])
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading Safety results: {e}")
        return pd.DataFrame()


def create_severity_distribution_chart(df):
    """Create a bar chart showing severity distribution."""
    if df.empty:
        print("⚠️  No data to visualize")
        return
    
    print("📊 Creating severity distribution chart...")
    
    # Define severity order and colors
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    colors = {"CRITICAL": "#d32f2f", "HIGH": "#f57c00", "MEDIUM": "#fbc02d", "LOW": "#388e3c"}
    
    # Count by severity
    severity_counts = df["severity"].value_counts()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Filter to only severities that exist in data
    existing_severities = [s for s in severity_order if s in severity_counts.index]
    counts = [severity_counts[s] for s in existing_severities]
    bar_colors = [colors[s] for s in existing_severities]
    
    # Create bar chart
    bars = ax.bar(existing_severities, counts, color=bar_colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_xlabel("Severity Level", fontsize=12, fontweight='bold')
    ax.set_ylabel("Number of Issues", fontsize=12, fontweight='bold')
    ax.set_title("SAST Security Issues by Severity", fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "severity_distribution.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_tool_comparison_chart(df):
    """Create a chart comparing findings by tool."""
    if df.empty:
        return
    
    print("📊 Creating tool comparison chart...")
    
    # Count by tool and severity
    tool_severity = df.groupby(["tool", "severity"]).size().unstack(fill_value=0)
    
    # Define colors
    severity_colors = {"CRITICAL": "#d32f2f", "HIGH": "#f57c00", "MEDIUM": "#fbc02d", "LOW": "#388e3c"}
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create stacked bar chart
    tool_severity.plot(kind='bar', stacked=True, ax=ax, 
                       color=[severity_colors.get(col, "#999999") for col in tool_severity.columns],
                       edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel("Tool", fontsize=12, fontweight='bold')
    ax.set_ylabel("Number of Issues", fontsize=12, fontweight='bold')
    ax.set_title("SAST Findings by Tool and Severity", fontsize=14, fontweight='bold', pad=20)
    ax.legend(title="Severity", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "tool_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_issue_types_chart(df):
    """Create a pie chart of issue types."""
    if df.empty:
        return
    
    print("📊 Creating issue types chart...")
    
    # Get top 10 issue types
    type_counts = df["type"].value_counts().head(10)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create pie chart
    colors = sns.color_palette("husl", len(type_counts))
    wedges, texts, autotexts = ax.pie(type_counts.values, labels=type_counts.index,
                                        autopct='%1.1f%%', startangle=90,
                                        colors=colors, textprops={'fontsize': 10})
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title("Top 10 Issue Types Found by SAST Tools", fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "issue_types.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_file_heatmap(df):
    """Create a heatmap showing which files have the most issues."""
    if df.empty or "file" not in df.columns:
        return
    
    print("📊 Creating file heatmap...")
    
    # Get files with issues
    file_df = df[df["file"].notna()].copy()
    
    if file_df.empty:
        return
    
    # Extract just filename from path
    file_df["filename"] = file_df["file"].apply(lambda x: Path(x).name if x else "unknown")
    
    # Count by file and severity
    file_severity = file_df.groupby(["filename", "severity"]).size().unstack(fill_value=0)
    
    # Keep top 15 files
    top_files = file_df["filename"].value_counts().head(15).index
    file_severity = file_severity.loc[file_severity.index.isin(top_files)]
    
    if file_severity.empty:
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(file_severity, annot=True, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Number of Issues'}, ax=ax, linewidths=0.5)
    
    ax.set_xlabel("Severity", fontsize=12, fontweight='bold')
    ax.set_ylabel("File", fontsize=12, fontweight='bold')
    ax.set_title("Security Issues by File", fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_file = VISUALIZATIONS_DIR / "file_heatmap.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_summary_statistics(df):
    """Create a summary statistics visualization."""
    if df.empty:
        return
    
    print("📊 Creating summary statistics...")
    
    # Calculate statistics
    total_issues = len(df)
    critical_issues = len(df[df["severity"] == "CRITICAL"])
    high_issues = len(df[df["severity"] == "HIGH"])
    medium_issues = len(df[df["severity"] == "MEDIUM"])
    low_issues = len(df[df["severity"] == "LOW"])
    
    tools_used = df["tool"].nunique()
    files_affected = df["file"].nunique() if "file" in df.columns else 0
    
    # Create figure with summary boxes
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    
    # Title
    fig.suptitle('SAST Security Scan Summary Report', fontsize=18, fontweight='bold', y=0.95)
    
    # Create summary boxes
    summary_data = [
        ("Total Issues", total_issues, "#2196F3"),
        ("Critical", critical_issues, "#d32f2f"),
        ("High", high_issues, "#f57c00"),
        ("Medium", medium_issues, "#fbc02d"),
        ("Low", low_issues, "#388e3c"),
        ("Tools Used", tools_used, "#9C27B0"),
        ("Files Scanned", files_affected, "#607D8B"),
    ]
    
    # Layout boxes in grid
    rows = 2
    cols = 4
    
    for idx, (label, value, color) in enumerate(summary_data):
        row = idx // cols
        col = idx % cols
        
        x = col * 0.25 + 0.05
        y = 0.75 - (row * 0.35)
        
        # Draw box
        box = plt.Rectangle((x, y), 0.18, 0.25, transform=fig.transFigure,
                            facecolor=color, edgecolor='black', linewidth=2, alpha=0.8)
        fig.add_artist(box)
        
        # Add value
        fig.text(x + 0.09, y + 0.15, str(value),
                ha='center', va='center', fontsize=32, fontweight='bold',
                color='white', transform=fig.transFigure)
        
        # Add label
        fig.text(x + 0.09, y + 0.05, label,
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='white', transform=fig.transFigure)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.5, 0.05, f'Report Generated: {timestamp}',
            ha='center', va='center', fontsize=10, style='italic',
            transform=fig.transFigure)
    
    output_file = VISUALIZATIONS_DIR / "summary_report.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    plt.close()


def generate_html_report(df):
    """Generate an HTML report with all findings."""
    if df.empty:
        return
    
    print("📄 Creating HTML report...")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAST Security Scan Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-box {{
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                color: white;
            }}
            .stat-box h3 {{
                margin: 0;
                font-size: 36px;
            }}
            .stat-box p {{
                margin: 5px 0 0 0;
                font-size: 14px;
            }}
            .critical {{ background-color: #d32f2f; }}
            .high {{ background-color: #f57c00; }}
            .medium {{ background-color: #fbc02d; }}
            .low {{ background-color: #388e3c; }}
            .info {{ background-color: #2196F3; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .severity-badge {{
                padding: 5px 10px;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .timestamp {{
                text-align: center;
                color: #7f8c8d;
                font-style: italic;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 SAST Security Scan Report</h1>
            <p><strong>Target Application:</strong> DBABA Address Book</p>
            <p><strong>Scan Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h2>📊 Summary Statistics</h2>
            <div class="stats">
                <div class="stat-box info">
                    <h3>{len(df)}</h3>
                    <p>Total Issues</p>
                </div>
                <div class="stat-box critical">
                    <h3>{len(df[df['severity'] == 'CRITICAL'])}</h3>
                    <p>Critical</p>
                </div>
                <div class="stat-box high">
                    <h3>{len(df[df['severity'] == 'HIGH'])}</h3>
                    <p>High Severity</p>
                </div>
                <div class="stat-box medium">
                    <h3>{len(df[df['severity'] == 'MEDIUM'])}</h3>
                    <p>Medium Severity</p>
                </div>
                <div class="stat-box low">
                    <h3>{len(df[df['severity'] == 'LOW'])}</h3>
                    <p>Low Severity</p>
                </div>
            </div>
            
            <h2>📈 Visualizations</h2>
            <img src="summary_report.png" alt="Summary Report">
            <img src="severity_distribution.png" alt="Severity Distribution">
            <img src="tool_comparison.png" alt="Tool Comparison">
            <img src="issue_types.png" alt="Issue Types">
            <img src="file_heatmap.png" alt="File Heatmap">
            
            <h2>📋 Detailed Findings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Tool</th>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>File</th>
                        <th>Line</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add rows for each issue (limit to first 100 for readability)
    severity_colors = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low"
    }
    
    for _, row in df.head(100).iterrows():
        severity_class = severity_colors.get(row.get("severity", ""), "info")
        file_name = Path(row.get("file", "")).name if pd.notna(row.get("file")) else "N/A"
        line_num = row.get("line", "N/A")
        
        html_content += f"""
                    <tr>
                        <td>{row.get('tool', 'N/A')}</td>
                        <td><span class="severity-badge {severity_class}">{row.get('severity', 'N/A')}</span></td>
                        <td>{row.get('type', 'N/A')}</td>
                        <td>{row.get('description', 'N/A')[:100]}...</td>
                        <td>{file_name}</td>
                        <td>{line_num}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
            
            <p class="timestamp">Report generated by DAST-SAST Security Testing Pipeline</p>
        </div>
    </body>
    </html>
    """
    
    output_file = VISUALIZATIONS_DIR / "security_report.html"
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Saved: {output_file}")


def main():
    """Main visualization function."""
    print("="*60)
    print("SAST Results Visualization")
    print("="*60 + "\n")
    
    # Load all results
    print("📂 Loading SAST scan results...\n")
    bandit_df = load_bandit_results()
    pylint_df = load_pylint_results()
    safety_df = load_safety_results()
    
    # Combine all results
    all_dfs = [df for df in [bandit_df, pylint_df, safety_df] if not df.empty]
    
    if not all_dfs:
        print("❌ No scan results found. Run SAST scans first!")
        return 1
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"✅ Loaded {len(combined_df)} total findings\n")
    print("-"*60 + "\n")
    
    # Create visualizations
    create_severity_distribution_chart(combined_df)
    create_tool_comparison_chart(combined_df)
    create_issue_types_chart(combined_df)
    create_file_heatmap(combined_df)
    create_summary_statistics(combined_df)
    generate_html_report(combined_df)
    
    print("\n" + "="*60)
    print(f"✅ All visualizations saved to: {VISUALIZATIONS_DIR}")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

