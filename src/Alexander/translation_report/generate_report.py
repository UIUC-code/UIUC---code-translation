import json
import os
from datetime import datetime

def generate_html_report(json_data):
    c_data = json_data["c_analysis"]
    rust_data = json_data["rust_analysis"]
    security_comparison = json_data["security_comparison"]
    compiler_errors = json_data["rust_compiler_errors"]
    
    risk_reduction = round((security_comparison["total_c_risks"] - security_comparison["intercepted_errors"]) / 
                          security_comparison["total_c_risks"] * 100, 2) if security_comparison["total_c_risks"] > 0 else 100
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>C to Rust Security Analysis Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{
                --primary: #3498db;
                --secondary: #2ecc71;
                --danger: #e74c3c;
                --dark: #2c3e50;
                --light: #ecf0f1;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            body {{
                background-color: #f8f9fa;
                color: #333;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            header {{
                background: linear-gradient(135deg, var(--dark), var(--primary));
                color: white;
                padding: 40px 20px;
                text-align: center;
                margin-bottom: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                font-size: 1.2rem;
                opacity: 0.9;
            }}
            
            .summary {{
                background: white;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .summary-card {{
                background: var(--light);
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                transition: transform 0.3s ease;
            }}
            
            .summary-card:hover {{
                transform: translateY(-5px);
            }}
            
            .summary-card h3 {{
                font-size: 1.1rem;
                margin-bottom: 10px;
                color: var(--dark);
            }}
            
            .summary-value {{
                font-size: 2.2rem;
                font-weight: bold;
            }}
            
            .c-risk {{
                color: var(--danger);
            }}
            
            .rust-feature {{
                color: var(--secondary);
            }}
            
            .section {{
                background: white;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            
            .section-title {{
                font-size: 1.8rem;
                margin-bottom: 20px;
                color: var(--dark);
                padding-bottom: 10px;
                border-bottom: 2px solid var(--light);
            }}
            
            .chart-container {{
                height: 400px;
                margin: 30px 0;
                position: relative;
            }}
            
            .comparison-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .comparison-card {{
                background: var(--light);
                border-radius: 8px;
                padding: 20px;
            }}
            
            .comparison-card h3 {{
                text-align: center;
                margin-bottom: 15px;
                color: var(--dark);
            }}
            
            .improvement {{
                text-align: center;
                font-size: 1.8rem;
                font-weight: bold;
                color: var(--secondary);
                margin: 20px 0;
            }}
            
            .key-points {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .point-card {{
                background: var(--light);
                border-radius: 8px;
                padding: 20px;
                border-left: 4px solid var(--primary);
            }}
            
            .point-card h4 {{
                margin-bottom: 10px;
                color: var(--dark);
            }}
            
            footer {{
                text-align: center;
                padding: 20px;
                margin-top: 40px;
                color: #777;
                font-size: 0.9rem;
            }}
            
            @media (max-width: 768px) {{
                .summary-grid, .comparison-grid, .key-points {{
                    grid-template-columns: 1fr;
                }}
                
                h1 {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>C to Rust Security Analysis Report</h1>
                <p class="subtitle">Comprehensive security comparison of C and Rust implementations</p>
            </header>
            
            <section class="summary">
                <h2>Security Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>C Security Risks</h3>
                        <div class="summary-value c-risk">{security_comparison["total_c_risks"]}</div>
                        <p>Critical vulnerabilities detected</p>
                    </div>
                    <div class="summary-card">
                        <h3>Rust Security Features</h3>
                        <div class="summary-value rust-feature">{security_comparison["total_rust_features"]}</div>
                        <p>Built-in safety mechanisms</p>
                    </div>
                    <div class="summary-card">
                        <h3>Risk Reduction</h3>
                        <div class="summary-value">{risk_reduction}%</div>
                        <p>Security vulnerabilities eliminated</p>
                    </div>
                    <div class="summary-card">
                        <h3>Compiler Interceptions</h3>
                        <div class="summary-value">{security_comparison["intercepted_errors"]}</div>
                        <p>Security errors caught at compile time</p>
                    </div>
                </div>
            </section>
            
            <section class="section">
                <h2 class="section-title">Security Risk Comparison</h2>
                <div class="chart-container">
                    <canvas id="riskComparisonChart"></canvas>
                </div>
                
                <div class="comparison-grid">
                    <div class="comparison-card">
                        <h3>C Code Risks</h3>
                        <ul>
                            <li>Dangling pointers: {security_comparison["c_risk_breakdown"]["dangling_pointers"]} risks</li>
                            <li>Pointer arithmetic: {security_comparison["c_risk_breakdown"]["pointer_arithmetic"]} risks</li>
                            <li>Memory leaks: {security_comparison["c_risk_breakdown"]["memory_leak_risk"]} risks</li>
                            <li>Buffer overflow: {security_comparison["c_risk_breakdown"]["buffer_overflow_risk"]} risks</li>
                            <li>Null dereference: {security_comparison["c_risk_breakdown"]["null_dereference_risk"]} risks</li>
                        </ul>
                    </div>
                    <div class="comparison-card">
                        <h3>Rust Security Features</h3>
                        <ul>
                            <li>Ownership system: {security_comparison["rust_feature_breakdown"]["ownership"]} features</li>
                            <li>Memory safety: {security_comparison["rust_feature_breakdown"]["memory_safety"]} features</li>
                            <li>Error handling: {security_comparison["rust_feature_breakdown"]["error_handling"]} features</li>
                            <li>Boundary safety: {security_comparison["rust_feature_breakdown"]["boundary_safety"]} features</li>
                        </ul>
                    </div>
                </div>
                
                <div class="improvement">
                    Risk Reduction: {risk_reduction}%
                </div>
            </section>
            
            <section class="section">
                <h2 class="section-title">Memory Management Comparison</h2>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
                
                <div class="key-points">
                    <div class="point-card">
                        <h4>C Memory Management</h4>
                        <p>Manual memory allocation and deallocation with malloc/free</p>
                        <p>Allocations: {c_data["memory_operations"]["allocations"]}, 
                           Deallocations: {c_data["memory_operations"]["deallocations"]}</p>
                    </div>
                    <div class="point-card">
                        <h4>Rust Memory Management</h4>
                        <p>Automatic memory management with ownership system</p>
                        <p>Safe allocations: {rust_data["memory_management"]["safe_allocations"]}, 
                           Safe containers: {rust_data["memory_management"]["safe_containers"]}</p>
                    </div>
                </div>
            </section>
            
            <section class="section">
                <h2 class="section-title">Compiler Analysis</h2>
                <div class="comparison-grid">
                    <div class="comparison-card">
                        <h3>Compiler Errors</h3>
                        <p>Total errors: {compiler_errors["error_count"]}</p>
                        {"".join(f'<li>{error}</li>' for error in compiler_errors["errors"]) if compiler_errors["error_count"] > 0 else "<p>No compiler errors detected</p>"}
                    </div>
                    <div class="comparison-card">
                        <h3>Security Errors Intercepted</h3>
                        {"".join(f'<li>{error}: {count}</li>' for error, count in compiler_errors["security_errors"].items()) if compiler_errors["security_errors"] else "<p>No security-related errors detected</p>"}
                    </div>
                </div>
            </section>
            
            <footer>
                <p>Security Analysis Report | Generated on: {datetime.now().strftime("%B %d, %Y")}</p>
                <p>C to Rust Translation Security Visualization</p>
            </footer>
        </div>

        <script>
            // Initialize charts after page load
            document.addEventListener('DOMContentLoaded', function() {{
                // Risk Comparison Chart
                const riskCtx = document.getElementById('riskComparisonChart').getContext('2d');
                const riskChart = new Chart(riskCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {list(security_comparison["c_risk_breakdown"].keys())},
                        datasets: [
                            {{
                                label: 'C Risks',
                                data: {list(security_comparison["c_risk_breakdown"].values())},
                                backgroundColor: '#e74c3c',
                                borderColor: '#c0392b',
                                borderWidth: 1
                            }},
                            {{
                                label: 'Rust Risks',
                                data: [0, 0, 0, 0, 0],
                                backgroundColor: '#2ecc71',
                                borderColor: '#27ae60',
                                borderWidth: 1
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Number of Risks'
                                }}
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'C vs Rust Security Risks',
                                font: {{
                                    size: 18
                                }}
                            }},
                            legend: {{
                                position: 'top'
                            }}
                        }}
                    }}
                }});
                
                // Memory Management Chart
                const memoryCtx = document.getElementById('memoryChart').getContext('2d');
                const memoryChart = new Chart(memoryCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Allocations', 'Deallocations'],
                        datasets: [
                            {{
                                label: 'C Memory Management',
                                data: [
                                    {security_comparison["memory_comparison"]["c_manual_allocations"]},
                                    {security_comparison["memory_comparison"]["c_manual_deallocations"]}
                                ],
                                backgroundColor: '#e74c3c',
                                borderColor: '#c0392b',
                                borderWidth: 1
                            }},
                            {{
                                label: 'Rust Memory Management',
                                data: [
                                    {security_comparison["memory_comparison"]["rust_auto_allocations"]},
                                    {security_comparison["memory_comparison"]["rust_auto_containers"]}
                                ],
                                backgroundColor: '#2ecc71',
                                borderColor: '#27ae60',
                                borderWidth: 1
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Operations Count'
                                }}
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Memory Management Comparison',
                                font: {{
                                    size: 18
                                }}
                            }},
                            legend: {{
                                position: 'top'
                            }}
                        }}
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

def save_html_report(html_content, filename="security_report.html"):
    """将HTML报告保存到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Security report saved to {os.path.abspath(filename)}")

# 示例JSON数据（替换为您的实际数据）
json_data = {
  "c_analysis": {
    "dangling_pointers": 0,
    "pointer_arithmetic": 0,
    "memory_leak_risk": 0,
    "buffer_overflow_risk": 0,
    "null_dereference_risk": 2,
    "memory_operations": {
      "allocations": 1,
      "deallocations": 2,
      "unsafe_functions": {
        "strcpy": 0,
        "strcat": 0,
        "sprintf": 0,
        "gets": 0,
        "scanf": 0
      }
    }
  },
  "rust_analysis": {
    "ownership_system": {
      "transfers": 0,
      "borrows": 10,
      "mutable_borrows": 3,
      "lifetimes": 4
    },
    "memory_management": {
      "safe_allocations": 4,
      "safe_containers": 0
    },
    "error_handling": {
      "option_usage": 4,
      "result_usage": 0,
      "unwrap_calls": 0,
      "expect_calls": 0
    },
    "boundary_safety": {
      "slice_access": 0,
      "iter_usage": 0
    }
  },
  "rust_compiler_errors": {
    "error_count": 0,
    "errors": [],
    "security_errors": {}
  },
  "security_comparison": {
    "total_c_risks": 2,
    "total_rust_features": 18,
    "c_risk_breakdown": {
      "dangling_pointers": 0,
      "pointer_arithmetic": 0,
      "memory_leak_risk": 0,
      "buffer_overflow_risk": 0,
      "null_dereference_risk": 2
    },
    "rust_feature_breakdown": {
      "ownership": 10,
      "memory_safety": 4,
      "error_handling": 4,
      "boundary_safety": 0
    },
    "memory_comparison": {
      "c_manual_allocations": 1,
      "c_manual_deallocations": 2,
      "rust_auto_allocations": 4,
      "rust_auto_containers": 0
    },
    "intercepted_errors": 0,
    "rust_error_details": {
      "error_count": 0,
      "errors": [],
      "security_errors": {}
    }
  }
}


if __name__ == "__main__":

    # with open("security_data.json", "r") as f:
    #     json_data = json.load(f)
    
    html_report = generate_html_report(json_data)
    save_html_report(html_report)