"""
Script to remove typing imports and annotations from all Python files
in the src directory to make them compatible with CircuitPython 9.x.
"""
import os
import re
import sys

def remove_typing_imports(content):
    """Remove typing imports from Python file content"""
    # Remove 'from typing import' lines
    content = re.sub(r'from\s+typing\s+import\s+.*?\n', '', content)
    
    # Remove type annotations in function declarations
    content = re.sub(r'def\s+([a-zA-Z0-9_]+)\s*\(\s*([^)]*?)\s*\)\s*->\s*[a-zA-Z0-9_\[\],\s\.]+\s*:', r'def \1(\2):', content)
    
    # Remove parameter type annotations
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        # Find function parameters with type annotations
        if ':' in line and '(' in line and ')' in line:
            parts = line.split('(', 1)
            if len(parts) == 2:
                before_params = parts[0]
                params_and_after = parts[1]
                
                # Process parameters
                param_parts = params_and_after.split(')', 1)
                if len(param_parts) == 2:
                    params = param_parts[0]
                    after_params = param_parts[1]
                    
                    # Remove parameter type annotations
                    new_params = re.sub(r'([a-zA-Z0-9_]+)\s*:\s*[a-zA-Z0-9_\[\],\s\.]+', r'\1', params)
                    
                    # Reconstruct the line
                    new_line = before_params + '(' + new_params + ')' + after_params
                    new_lines.append(new_line)
                    continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def process_file(file_path):
    """Process a single Python file to remove typing"""
    print(f"Processing {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Skip files that don't have typing imports
    if 'from typing import' not in content:
        return
    
    # Remove typing imports and annotations
    new_content = remove_typing_imports(content)
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {file_path}")

def process_directory(directory):
    """Process all Python files in a directory and its subdirectories"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == "__main__":
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    process_directory(src_dir)
    print("Finished removing typing imports and annotations from all Python files.")