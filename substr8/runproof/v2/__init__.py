"""
RunProof v2 - Portable JSON-based proof format.

Schema version: runproof/v2

v2 is a single JSON file (.runproof.json) with:
- Cryptographic hash chain for event integrity
- Merkle root for set integrity  
- Ed25519 signature for authenticity

Usage:
    from substr8.runproof.v2 import RunProof, verify_runproof
    
    # Load and verify
    proof = RunProof.model_validate_json(json_str)
    result = verify_runproof(proof.model_dump())
"""

from .schema import (
    RunProof,
    RunProofHeader,
    TraceEntry,
    EventType,
    RunStatus,
    TriggerType,
    RedactionMode,
    SignatureAlgorithm,
    Signer,
    Policy,
    Identity,
    Context,
    ModelInfo,
    Outputs,
    Artifact,
    Commitments,
    Signature,
    Anchors,
    Metadata,
)

from .state import (
    RunState,
    LifecycleStatus,
    ChildRunRef,
    HumanReviewState,
    HumanReviewStatus,
    RetryState,
    ValidationState,
    SettlementState,
    SettlementStatus,
    Checkpoint,
)

from .crypto import (
    sha256_hex,
    sha256_str,
    sha256_json,
    canonical_json,
    compute_entry_hash,
    compute_merkle_root,
    verify_hash_chain,
    KeyPair,
    verify_signature,
    verify_signature_str,
)

from .verify import (
    verify_runproof,
    VerificationResult,
    CheckResult,
)

__all__ = [
    # Schema
    "RunProof",
    "RunProofHeader",
    "TraceEntry",
    "EventType",
    "RunStatus",
    "TriggerType",
    "RedactionMode",
    "SignatureAlgorithm",
    "Signer",
    "Policy",
    "Identity",
    "Context",
    "ModelInfo",
    "Outputs",
    "Artifact",
    "Commitments",
    "Signature",
    "Anchors",
    "Metadata",
    # State
    "RunState",
    "LifecycleStatus",
    "ChildRunRef",
    "HumanReviewState",
    "HumanReviewStatus",
    "RetryState",
    "ValidationState",
    "SettlementState",
    "SettlementStatus",
    "Checkpoint",
    # Crypto
    "sha256_hex",
    "sha256_str",
    "sha256_json",
    "canonical_json",
    "compute_entry_hash",
    "compute_merkle_root",
    "verify_hash_chain",
    "KeyPair",
    "verify_signature",
    "verify_signature_str",
    # Verify
    "verify_runproof",
    "VerificationResult",
    "CheckResult",
]
