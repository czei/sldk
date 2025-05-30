"""Root conftest.py to prevent code.py from interfering with pytest."""
import os

# Early hook to modify sys.modules before any imports
def pytest_configure(config):
    """Hook that runs before test collection to prevent code.py conflicts."""
    # If pdb hasn't loaded yet, temporarily rename our code.py
    project_root = os.path.dirname(os.path.abspath(__file__))
    code_py_path = os.path.join(project_root, 'code.py')
    code_py_backup = os.path.join(project_root, 'code.py.testing_backup')
    
    if os.path.exists(code_py_path) and not os.path.exists(code_py_backup):
        os.rename(code_py_path, code_py_backup)
        config._code_py_renamed = True
    else:
        config._code_py_renamed = False

def pytest_unconfigure(config):
    """Hook that runs after all tests to restore code.py."""
    if hasattr(config, '_code_py_renamed') and config._code_py_renamed:
        project_root = os.path.dirname(os.path.abspath(__file__))
        code_py_path = os.path.join(project_root, 'code.py')
        code_py_backup = os.path.join(project_root, 'code.py.testing_backup')
        
        if os.path.exists(code_py_backup):
            os.rename(code_py_backup, code_py_path)

# Configure pytest-asyncio
# Set the asyncio fixture loop scope to prevent warnings
pytest_plugins = ['pytest_asyncio']