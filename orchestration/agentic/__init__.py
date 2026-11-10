"""B00 project manager control plane: read-only GitHub, safe validations, ledger replay."""
from .manager import GuardError, evaluate, append_event, load_events, run_safe_checks
