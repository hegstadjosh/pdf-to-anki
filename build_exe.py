import PyInstaller.__main__
import os
import sys
import spacy
import subprocess
import site
from pathlib import Path

def ensure_spacy_model():
    """Ensure the required spaCy model is downloaded."""
    try:
        spacy.load('en_core_web_sm')
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)

def find_spacy_model():
    """Find the spaCy model directory."""
    try:
        import en_core_web_sm
        model_path = Path(en_core_web_sm.__file__).parent
        return str(model_path)
    except ImportError:
        site_packages = site.getsitepackages()[0]
        model_path = os.path.join(site_packages, 'en_core_web_sm')
        if os.path.exists(model_path):
            return model_path
        raise RuntimeError("Could not find spaCy model. Please run 'python -m spacy download en_core_web_sm' first.")

def build_exe():
    # Ensure spaCy model is downloaded
    ensure_spacy_model()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to your main script
    main_script = os.path.join(script_dir, 'app.py')
    
    # Path to your .env.example
    env_example = os.path.join(script_dir, '.env.example')
    
    # Get spaCy model path
    spacy_model = find_spacy_model()
    
    # Create a hook file for spaCy
    hook_content = '''
from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('en_core_web_sm', include_py_files=True)
'''
    hook_file = os.path.join(script_dir, 'hook-en_core_web_sm.py')
    with open(hook_file, 'w') as f:
        f.write(hook_content)
    
    # Base command arguments
    args = [
        main_script,
        '--name=PDFToAnki',
        '--onefile',
        '--windowed',  # Use --noconsole on Windows
        '--add-data', f'{env_example}{os.pathsep}.env.example',
        '--hidden-import=en_core_web_sm',
        '--additional-hooks-dir=.',
        '--clean',
        '--noconfirm',
    ]
    
    # Add icon if it exists
    icon_path = os.path.join(script_dir, 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        args.extend(['--icon', icon_path])
    
    try:
        # Build the executable
        PyInstaller.__main__.run(args)
    finally:
        # Clean up hook file
        if os.path.exists(hook_file):
            os.remove(hook_file)

if __name__ == '__main__':
    build_exe() 