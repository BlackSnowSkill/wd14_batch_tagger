#!/usr/bin/env python3
"""
Installation script for BSS WD14 Batch Tagger ComfyUI custom node.
This script handles dependency installation and initial setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"Python version check passed: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Read requirements from requirements.txt
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("Error: requirements.txt not found")
        return False
    
    # Install dependencies with upgrade flag for onnxruntime
    if not run_command(f"pip install --upgrade -r {requirements_file}", "Installing dependencies from requirements.txt"):
        print("Failed to install dependencies from requirements.txt")
        return False
    
    # Force reinstall onnxruntime if there are compatibility issues
    print("Ensuring onnxruntime compatibility...")
    run_command("pip install --upgrade --force-reinstall 'onnxruntime>=1.18.0,<2.0.0'", "Ensuring onnxruntime compatibility")
    
    # Check for GPU support and version
    print("Checking for GPU support...")
    try:
        import onnxruntime as ort
        # Check version compatibility
        version = ort.__version__
        print(f"onnxruntime version: {version}")
        
        # Simple version check (major.minor format)
        try:
            major, minor = map(int, version.split('.')[:2])
            if major < 1 or (major == 1 and minor < 18):
                print("⚠️  onnxruntime version is too old, upgrading...")
                run_command("pip install --upgrade 'onnxruntime>=1.18.0,<2.0.0'", "Upgrading onnxruntime")
        except (ValueError, AttributeError):
            print("⚠️  Could not parse onnxruntime version, but it's installed")
        
        providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in providers:
            print("✅ CUDA support detected - GPU acceleration available")
        else:
            print("ℹ️  CUDA support not available - will use CPU only")
    except ImportError:
        print("⚠️  Could not check GPU support - onnxruntime not properly installed")
    except Exception as e:
        print(f"⚠️  Error checking onnxruntime: {e}")
    
    return True

def create_models_directory():
    """Create models directory if it doesn't exist."""
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    print(f"Models directory ready: {models_dir}")
    return True

def verify_installation():
    """Verify that the installation was successful."""
    print("Verifying installation...")
    
    try:
        # Test imports
        import numpy as np
        import PIL
        import onnxruntime as ort
        import huggingface_hub
        
        print("✅ All required packages imported successfully")
        
        # Test node imports
        sys.path.insert(0, str(Path(__file__).parent))
        from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        
        print(f"✅ Custom nodes loaded: {list(NODE_CLASS_MAPPINGS.keys())}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main installation function."""
    print("=" * 60)
    print("BSS WD14 Batch Tagger - Installation Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create models directory
    if not create_models_directory():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ Installation completed successfully!")
    print("=" * 60)
    print("The BSS WD14 Batch Tagger custom node is now ready to use.")
    print("Restart ComfyUI to see the new nodes in the interface.")
    print("")
    print("Available nodes:")
    print("- BSS Load Images from Folder 📂")
    print("- BSS WD14 Batch Tagger 🌿")
    print("")
    print("For usage instructions, see the README.md file.")
    print("=" * 60)

if __name__ == "__main__":
    main()
