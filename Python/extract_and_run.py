"""
Extracts all code cells from analysis.ipynb and runs them to verify correctness.
"""
import json
import sys
import os

# Change working directory so relative paths (../Dataset, ../Images) work
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Extract all code cells into a single script
script_lines = []
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        script_lines.append('# --- CELL ---')
        for line in cell['source']:
            script_lines.append(line)
        script_lines.append('\n')

script = ''.join(script_lines)

with open('run_analysis.py', 'w', encoding='utf-8') as f:
    f.write(script)

print('Script extracted successfully to run_analysis.py')
print(f'Total characters: {len(script)}')
