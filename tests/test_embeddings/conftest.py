"""Add research/ to sys.path so that `embeddings.time2vec.*` imports work."""
import sys
from pathlib import Path

_research = str(Path(__file__).parent.parent.parent / "research")
if _research not in sys.path:
    sys.path.insert(0, _research)
