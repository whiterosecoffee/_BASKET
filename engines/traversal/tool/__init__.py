"""Read-only source-gated traversal entrypoint; never a new engine."""
from .tool import run, digest
__all__ = ["run", "digest"]
