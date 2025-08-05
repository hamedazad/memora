#!/usr/bin/env python3
"""
Version management script for Memora Memory Assistant
"""

import re
import sys
from datetime import datetime

def update_version(version_type='patch'):
    """
    Update version number based on semantic versioning
    
    Args:
        version_type (str): 'major', 'minor', or 'patch'
    """
    
    # Read current version
    with open('version.py', 'r') as f:
        content = f.read()
    
    # Extract current version
    version_match = re.search(r'__version__ = "(\d+)\.(\d+)\.(\d+)"', content)
    if not version_match:
        print("Error: Could not find version in version.py")
        return False
    
    major, minor, patch = map(int, version_match.groups())
    
    # Update version based on type
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        print(f"Error: Invalid version type '{version_type}'. Use 'major', 'minor', or 'patch'")
        return False
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Update version.py
    new_content = re.sub(
        r'__version__ = "\d+\.\d+\.\d+"',
        f'__version__ = "{new_version}"',
        content
    )
    new_content = re.sub(
        r'__version_info__ = \(\d+, \d+, \d+\)',
        f'__version_info__ = ({major}, {minor}, {patch})',
        new_content
    )
    
    # Add to version history
    today = datetime.now().strftime('%Y-%m-%d')
    history_entry = f'    "{new_version} - {input("Enter version description: ")}",'
    
    # Find the VERSION_HISTORY list and add new entry
    lines = new_content.split('\n')
    for i, line in enumerate(lines):
        if 'VERSION_HISTORY = [' in line:
            lines.insert(i + 1, history_entry)
            break
    
    new_content = '\n'.join(lines)
    
    # Write updated version.py
    with open('version.py', 'w') as f:
        f.write(new_content)
    
    print(f"Version updated to {new_version}")
    return True

def show_current_version():
    """Display current version information"""
    try:
        from version import get_version, get_version_info, get_version_history
        version = get_version()
        version_info = get_version_info()
        history = get_version_history()
        
        print(f"Current Version: {version}")
        print(f"Version Info: {version_info}")
        print("\nVersion History:")
        for entry in history:
            print(f"  {entry}")
            
    except ImportError as e:
        print(f"Error importing version information: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_version.py [command]")
        print("Commands:")
        print("  show                    - Show current version")
        print("  patch                   - Increment patch version (1.0.0 -> 1.0.1)")
        print("  minor                   - Increment minor version (1.0.0 -> 1.1.0)")
        print("  major                   - Increment major version (1.0.0 -> 2.0.0)")
        return
    
    command = sys.argv[1]
    
    if command == 'show':
        show_current_version()
    elif command in ['patch', 'minor', 'major']:
        update_version(command)
    else:
        print(f"Unknown command: {command}")
        print("Use 'show', 'patch', 'minor', or 'major'")

if __name__ == '__main__':
    main() 