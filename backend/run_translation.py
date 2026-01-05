#!/usr/bin/env python
"""
Runner script for translation to handle import paths correctly.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now import and run the translation script
from scripts.translate_content import main

if __name__ == "__main__":
    main()
