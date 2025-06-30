#!/usr/bin/env python3
"""Script to migrate all swarm examples from PyLEDSimulator to SLDK simulator."""

import os
import re

# List of files to migrate
swarm_files = [
    "PyLEDSimulator/examples/theme_park_waits_swarm_advanced.py",
    "PyLEDSimulator/examples/theme_park_waits_swarm_gif.py",
    "PyLEDSimulator/examples/theme_park_waits_swarm_gif_hq.py",
    "PyLEDSimulator/examples/theme_park_waits_simple_swarm.py",
    "PyLEDSimulator/examples/theme_park_waits_swarm_sprites.py",
    "PyLEDSimulator/examples/theme_park_waits_swarm_circuitpython.py",
    "PyLEDSimulator/examples/circuitpython_swarm_player.py",
    "PyLEDSimulator/examples/complete_swarm_demo.py",
    "PyLEDSimulator/examples/generate_swarm_frames.py",
    "PyLEDSimulator/examples/play_swarm_frames.py",
    "code_swarm_demo.py",
    "code_swarm_demo_full.py"
]

def migrate_file(filepath):
    """Migrate a single file from PyLEDSimulator to SLDK."""
    print(f"Migrating {filepath}...")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if already migrated
        if 'sldk.simulator' in content:
            print(f"  ✓ Already migrated")
            return
        
        # Replace the path setup and imports
        # Pattern 1: sys.path.insert with pyledsimulator import
        pattern1 = r'sys\.path\.insert\(0, os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)\s*\n\s*from pyledsimulator'
        if re.search(pattern1, content):
            content = re.sub(
                pattern1,
                'sys.path.insert(0, os.path.join(os.path.dirname(__file__), \'../..\' if \'PyLEDSimulator\' in __file__ else \'.\', \'sldk\', \'src\'))\n\nfrom sldk.simulator',
                content
            )
        
        # Pattern 2: Just the import without path setup
        content = content.replace('from pyledsimulator.', 'from sldk.simulator.')
        content = content.replace('import pyledsimulator', 'import sldk.simulator')
        
        # Add path setup if missing
        if 'from sldk.simulator' in content and 'sys.path.insert' not in content:
            # Find the import line
            import_match = re.search(r'(from sldk\.simulator.*)', content)
            if import_match:
                import_line = import_match.group(1)
                # Add path setup before import
                path_setup = '''# Add SLDK to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..' if 'PyLEDSimulator' in __file__ else '.', 'sldk', 'src'))

'''
                content = content.replace(import_line, path_setup + import_line)
        
        # Write the migrated content
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"  ✓ Migrated successfully")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

def main():
    """Run the migration."""
    print("Starting PyLEDSimulator to SLDK migration...")
    print("=" * 50)
    
    for filepath in swarm_files:
        if os.path.exists(filepath):
            migrate_file(filepath)
        else:
            print(f"✗ File not found: {filepath}")
    
    print("\n" + "=" * 50)
    print("Migration complete!")

if __name__ == "__main__":
    main()