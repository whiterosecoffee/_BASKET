"""Expose canonical closeout/QC tests to the existing worker-qc discovery.

Keep assertions in their owning modules. Imports are deliberately unconditional:
missing dependencies or import failures must fail CI, never skip this coverage.
No workflow change or second implementation is needed.
"""
from orchestration.conversation_closeout.versions.test_acceptance import AcceptanceTests
from orchestration.conversation_closeout.versions.test_qc_intake import QcIntakeTests
from orchestration.conversation_closeout.versions.test_qc_submit import QcSubmitTests
