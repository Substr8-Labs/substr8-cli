"""
RunProof - Portable, Verifiable Agent Run Artifacts

RunProof is a cryptographically verifiable artifact produced at the end
of every governed agent run. It packages:

- Who ran (agent identity + hash)
- What they were allowed to do (ACC policy + policy hash)
- What they did (DCT tamper-evident ledger)
- Conversation integrity receipts (CIA)
- Memory provenance pointers (GAM)

Versions:
- v1 (RunProofBundle): Directory-based bundle format
- v2 (RunProof): Single JSON file with hash chain + Merkle root
"""

# v1 - Directory bundle format
from .bundle import RunProofBundle, create_runproof, load_runproof
from .verify import verify_runproof as verify_runproof_v1, VerificationResult
from .hash import compute_root_hash, canonical_json

# v2 - JSON file format (recommended)
from .v2 import (
    RunProof,
    RunProofHeader,
    RunState,
    TraceEntry,
    EventType,
    RunStatus,
    verify_runproof as verify_runproof_v2,
)

# Alias for latest
verify_runproof = verify_runproof_v2

__all__ = [
    # v1
    "RunProofBundle",
    "create_runproof",
    "load_runproof",
    "verify_runproof_v1",
    "VerificationResult",
    "compute_root_hash",
    "canonical_json",
    # v2 (recommended)
    "RunProof",
    "RunProofHeader",
    "RunState",
    "TraceEntry",
    "EventType",
    "RunStatus",
    "verify_runproof_v2",
    # Latest
    "verify_runproof",
]
