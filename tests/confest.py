import sys
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Add project root to Python import path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))