#!/usr/bin/env python3
"""
Setup script to predownload the embedding model and prepare the environment.
"""

import subprocess
import sys
from fastembed import TextEmbedding

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Requirements installed successfully!")

def predownload_model():
    """Predownload the default embedding model to avoid delays during API calls"""
    print("🔽 Predownloading embedding model...")
    try:
        # Initialize the default embedding model - this will download it
        model = TextEmbedding()
        print("✅ Embedding model downloaded and cached successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to download embedding model: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Deep Job Seek...")
    
    try:
        install_requirements()
        success = predownload_model()
        
        if success:
            print("\n✅ Setup completed successfully!")
            print("🎯 You can now run: python main.py")
        else:
            print("\n⚠️  Setup completed with warnings. The API will work but may be slower on first run.")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()