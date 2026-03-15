import os
import glob

# Update python file
app_py_path = 'd:/Depart/app.py'
with open(app_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(app_py_path, 'w', encoding='utf-8') as f:
    for line in lines:
        line = line.replace("request.form.get('action')", "request.form.get('req_action')")
        line = line.replace("request.form['action']", "request.form['req_action']")
        f.write(line)

# Update HTML files
for html_file in glob.glob('d:/Depart/templates/*.html'):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_text = f.read()
    html_text = html_text.replace('name="action"', 'name="req_action"')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_text)

print('Replaced name="action" with name="req_action" in app.py and HTML templates!')
