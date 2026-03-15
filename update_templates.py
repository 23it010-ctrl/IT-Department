import os
import glob

templates_dir = 'templates'
files = glob.glob(os.path.join(templates_dir, '*.html'))

old_pattern = "url_for('static', filename='uploads/' + "
new_pattern = "url_for('uploaded_file', filename="

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_pattern in content:
        print(f"Updating {file_path}")
        # Need to handle the closing parenthesis too. 
        # url_for('static', filename='uploads/' + some_var) -> url_for('uploaded_file', filename=some_var)
        # Note: some instances might have 'url_for('static', filename='uploads/alan.png')'
        
        updated_content = content.replace("url_for('static', filename='uploads/' + ", "url_for('uploaded_file', filename=")
        
        # Also handle cases with literal strings if any
        # url_for('static', filename='uploads/alan.png') -> url_for('uploaded_file', filename='alan.png')
        import re
        updated_content = re.sub(r"url_for\('static', filename='uploads/([^']+)'\)", r"url_for('uploaded_file', filename='\1')", updated_content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

print("Replacement complete.")
