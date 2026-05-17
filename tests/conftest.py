import sys
from pathlib import Path

# so tests can import habit, db, etc. from parent folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
