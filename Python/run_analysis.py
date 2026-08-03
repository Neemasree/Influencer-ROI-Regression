# Non-interactive backend — saves graphs to files without blocking
import matplotlib
matplotlib.use('Agg')

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import json

with open('analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

script_lines = []
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        script_lines.append('# --- CELL ---\n')
        for line in cell['source']:
            script_lines.append(line)
        script_lines.append('\n')

with open('_run_temp.py', 'w', encoding='utf-8') as f:
    f.write(''.join(script_lines))

print('Script extracted. Running...')
