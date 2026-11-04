"""Expose closeout unit tests to existing orchestration CI discovery.

The shared worker-qc job discovers orchestration/tests/test_*.py. Importing the
existing TestCase ensures its tests run without a new CI workflow or duplicate
implementation. Keep assertions in the canonical component test module.
"""
from orchestration.conversation_closeout.test_closeout import CloseoutTests
