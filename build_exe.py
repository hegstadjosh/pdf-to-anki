import PyInstaller.__main__
import os
import sys
import subprocess
import site
from pathlib import Path

def build_exe():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to your main script
    main_script = os.path.join(script_dir, 'app.py')
    
    # Path to your .env.example
    env_example = os.path.join(script_dir, '.env.example')
    
    # Base command arguments
    args = [
        main_script,
        '--name=PDFToAnki',
        '--onefile',
        # '--windowed',  # Removed windowed mode to show console
        '--add-data', f'{env_example}{os.pathsep}.env.example',
        '--hidden-import=customtkinter',
        '--hidden-import=tkinter',
        '--hidden-import=PIL',
        '--collect-all=customtkinter',
        '--debug=all',  # Add debug information
        '--clean',
        '--noconfirm',
    ]
    
    # Add icon if it exists
    icon_path = os.path.join(script_dir, 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        args.extend(['--icon', icon_path])
    
    # Build the executable
    PyInstaller.__main__.run(args)

if __name__ == '__main__':
    build_exe() 