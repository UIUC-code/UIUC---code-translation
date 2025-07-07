import os
import json
import shutil
import subprocess
from pathlib import Path
import time

KLEE_RESULTS = Path("klee_results")
REPORTS = Path("reports")
TEST_CASES = Path("test_cases")

def process_klee_results():
    """处理KLEE输出结果"""
    os.makedirs(TEST_CASES, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    
    # 汇总报告数据
    coverage_data = []
    test_case_details = {}
    
    for test_dir in KLEE_RESULTS.iterdir():
        if not test_dir.is_dir():
            continue
        
        test_name = test_dir.name
        print(f"Processing KLEE results for {test_name}...")
        
        # 1. 提取测试用例
        ktest_files = list(test_dir.glob("*.ktest"))
        if not ktest_files:
            print(f"  No KTEST files found for {test_name}")
            continue
        
        # 为每个测试创建可重现的测试用例
        test_case_dir = TEST_CASES / test_name
        os.makedirs(test_case_dir, exist_ok=True)
        
        test_case_details[test_name] = []
        
        for ktest in ktest_files:
            # 转换为可读格式
            ktest_txt = test_case_dir / (ktest.stem + ".txt")
            subprocess.run(["ktest-tool", str(ktest)], stdout=open(ktest_txt, "w"))
            
            # 收集测试用例详情
            test_case_details[test_name].append({
                "name": ktest.name,
                "text_file": ktest_txt.name,
                "path": str(ktest_txt.relative_to(TEST_CASES))
            })
            
            # 创建重现脚本
            replay_script = test_case_dir / (ktest.stem + "_replay.sh")
            with open(replay_script, "w") as f:
                f.write("#!/bin/bash\n\n")
                f.write(f"# Replay test case for {test_name}\n")
                f.write(f"ktest-tool {ktest}  # View test data\n")
                f.write(f"# Run your program with these inputs\n")
                f.write(f"# ./{test_name} <ARGS>\n")
        
        # 2. 收集覆盖率数据
        info_file = test_dir / "info"
        if info_file.exists():
            with open(info_file) as f:
                info_content = f.read()
                instructions = "N/A"
                paths = "N/A"
                
                if "Instructions:" in info_content:
                    instructions = info_content.split("Instructions:")[1].split("\n")[0].strip()
                if "Completed paths:" in info_content:
                    paths = info_content.split("Completed paths:")[1].split("\n")[0].strip()
            
            coverage_data.append({
                "test": test_name,
                "instructions": instructions,
                "paths": paths
            })
    
    # 3. 生成覆盖率报告
    coverage_report = REPORTS / "coverage_report.json"
    with open(coverage_report, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "total_tests": len(coverage_data),
            "coverage_data": coverage_data
        }, f, indent=2)
    
    # 4. 创建HTML报告
    html_report = REPORTS / "index.html"
    
    # 生成测试用例HTML内容
    test_case_html = ""
    for test_name, cases in test_case_details.items():
        test_case_html += f'<div class="test-group mb-4">\n'
        test_case_html += f'  <h3>{test_name}</h3>\n'
        test_case_html += '  <ul class="list-group">\n'
        
        for case in cases:
            test_case_html += f'    <li class="list-group-item">\n'
            test_case_html += f'      <a href="../test_cases/{test_name}/{case["text_file"]}" target="_blank">{case["name"]}</a>\n'
            test_case_html += '    </li>\n'
        
        test_case_html += '  </ul>\n'
        test_case_html += '</div>\n'
    
    # 生成HTML报告
    with open(html_report, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>KLEE Test Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .test-group {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
        .coverage-table {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">KLEE Test Report</h1>
        
        <h2>Coverage Summary</h2>
        <div id="coverage-table"></div>
        
        <h2 class="mt-5">Test Cases</h2>
        <div id="test-cases">
            {test_case_html if test_case_html else '<p>No test cases found</p>'}
        </div>
    </div>

    <script>
        // Load coverage data from JSON
        fetch('coverage_report.json')
            .then(response => response.json())
            .then(data => {{
                const table = document.getElementById('coverage-table');
                
                // Create coverage table
                let tableHTML = `
                    <table class="table table-striped coverage-table">
                        <thead>
                            <tr>
                                <th>Test</th>
                                <th>Instructions Covered</th>
                                <th>Paths Explored</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                data.coverage_data.forEach(item => {{
                    tableHTML += `
                        <tr>
                            <td>${{item.test}}</td>
                            <td>${{item.instructions}}</td>
                            <td>${{item.paths}}</td>
                        </tr>
                    `;
                }});
                
                tableHTML += `
                        </tbody>
                    </table>
                `;
                
                table.innerHTML = tableHTML;
            }})
            .catch(error => {{
                console.error('Error loading coverage data:', error);
                document.getElementById('coverage-table').innerHTML = 
                    '<p class="text-danger">Error loading coverage data</p>';
            }});
    </script>
</body>
</html>""")

    print(f"Report generated at: {html_report}")

if __name__ == "__main__":
    process_klee_results()
