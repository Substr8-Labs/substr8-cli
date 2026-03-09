"""RunProof v2 Schema

Cryptographically verifiable receipt for agent execution.

Schema version: runproof/v2
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Run completion status."""
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class TriggerType(str, Enum):
    """What triggered the run."""
    USER_PROMPT = "user_prompt"
    API = "api"
    SCHEDULE = "schedule"
    EVENT = "event"


class RedactionMode(str, Enum):
    """How sensitive data is handled."""
    HASHED = "hashed"
    PARTIAL = "partial"
    EMBEDDED = "embedded"


class EventType(str, Enum):
    """Canonical event types."""
    RUN_STARTED = "run_started"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_CANCELLED = "run_cancelled"
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    DECISION_MADE = "decision_made"
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_COMPLETED = "tool_call_completed"
    TOOL_CALL_FAILED = "tool_call_failed"
    DELEGATION_STARTED = "delegation_started"
    DELEGATION_COMPLETED = "delegation_completed"
    DELEGATION_FAILED = "delegation_failed"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    STATE_TRANSITION = "state_transition"
    CAPABILITY_CHECK = "capability_check"
    POLICY_ALLOW = "policy_allow"
    POLICY_DENY = "policy_deny"
    ARTIFACT_EMITTED = "artifact_emitted"
    PAYMENT_AUTHORIZED = "payment_authorized"
    PAYMENT_SETTLED = "payment_settled"
    PAYMENT_FAILED = "payment_failed"
    ERROR = "error"
    RETRY = "retry"
    HUMAN_REVIEW_REQUESTED = "human_review_requested"
    HUMAN_REVIEW_COMPLETED = "human_review_completed"
    CUSTOM = "custom"


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms."""
    ED25519 = "ed25519"
    ECDSA_P256 = "ecdsa-p256"


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────


class RunProofHeader(BaseModel):
    """Run metadata and identification."""
    
    proof_id: str = Field(..., description="Unique proof artifact identifier")
    run_id: str = Field(..., description="Execution identifier")
    tenant_id: str | None = Field(None, description="Multi-tenant isolation")
    agent_id: str = Field(..., description="Agent identifier (e.g., claims/orchestrator)")
    agent_version_hash: str | None = Field(None, description="SHA256 hash of agent definition")
    runtime: str = Field(..., description="Execution environment (langgraph, openclaw, etc.)")
    runtime_version: str | None = Field(None, description="Runtime version for reproducibility")
    started_at: datetime = Field(..., description="Run start timestamp")
    ended_at: datetime | None = Field(None, description="Run end timestamp")
    status: RunStatus = Field(..., description="Run completion status")
    parent_run_id: str | None = Field(None, description="Parent run for delegation/retry")
    session_id: str | None = Field(None, description="Conversation context")
    workflow_id: str | None = Field(None, description="Job-level chain")


# ─────────────────────────────────────────────────────────────────────────────
# Identity
# ─────────────────────────────────────────────────────────────────────────────


class Signer(BaseModel):
    """Proof signer identity."""
    
    key_id: str = Field(..., description="Signing key identifier")
    public_key: str = Field(..., description="Public key (prefixed with algorithm)")
    issuer: str = Field(..., description="Key issuer (substr8labs, customer, runtime)")


class Policy(BaseModel):
    """Governance policy reference."""
    
    capability_profile_id: str | None = Field(None, description="ACC capability profile")
    policy_hash: str | None = Field(None, description="SHA256 hash of policy document")


class Identity(BaseModel):
    """Signer and policy information."""
    
    signer: Signer
    policy: Policy | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Context
# ─────────────────────────────────────────────────────────────────────────────


class ModelInfo(BaseModel):
    """LLM model information."""
    
    provider: str = Field(..., description="Model provider (anthropic, openai, etc.)")
    model_id: str = Field(..., description="Model identifier")


class Context(BaseModel):
    """Execution context."""
    
    trigger_type: TriggerType = Field(..., description="What triggered the run")
    input_hash: str = Field(..., description="SHA256 hash of input (privacy-safe)")
    input_redaction_mode: RedactionMode = Field(
        RedactionMode.HASHED, description="How input is stored"
    )
    model: ModelInfo | None = None
    tools_available: list[str] = Field(default_factory=list, description="Available tool names")


# ─────────────────────────────────────────────────────────────────────────────
# Trace
# ─────────────────────────────────────────────────────────────────────────────


class TraceEntry(BaseModel):
    """Single event in the execution trace."""
    
    seq: int = Field(..., ge=1, description="Sequence number (1-indexed)")
    event_id: str = Field(..., description="Unique event identifier")
    type: EventType = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    prev_hash: str | None = Field(None, description="Hash of previous entry (chain)")
    payload_hash: str | None = Field(None, description="SHA256 hash of payload")
    payload_ref: str | None = Field(None, description="External payload reference")
    payload: dict[str, Any] | None = Field(None, description="Event payload (if embedded)")
    entry_hash: str = Field(..., description="SHA256 hash of this entry")


# ─────────────────────────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────────────────────────


class Artifact(BaseModel):
    """Output artifact reference."""
    
    artifact_id: str
    artifact_type: Literal["file", "json", "report"]
    artifact_hash: str
    uri: str | None = None


class Outputs(BaseModel):
    """Run outputs."""
    
    result_hash: str = Field(..., description="SHA256 hash of final output")
    result_redaction_mode: RedactionMode = Field(
        RedactionMode.HASHED, description="How output is stored"
    )
    artifacts: list[Artifact] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Commitments
# ─────────────────────────────────────────────────────────────────────────────


class Signature(BaseModel):
    """Cryptographic signature."""
    
    algorithm: SignatureAlgorithm = Field(SignatureAlgorithm.ED25519)
    value: str = Field(..., description="Base64-encoded signature")


class Commitments(BaseModel):
    """Cryptographic commitments."""
    
    event_root: str = Field(..., description="Merkle root of trace entries")
    proof_hash: str = Field(..., description="SHA256 of canonical proof envelope")
    signature: Signature


# ─────────────────────────────────────────────────────────────────────────────
# Anchors
# ─────────────────────────────────────────────────────────────────────────────


class Anchors(BaseModel):
    """External anchoring references."""
    
    registry_id: str | None = Field(None, description="Registry entry ID")
    registry_anchor_hash: str | None = Field(None, description="Registry anchor hash")
    transparency_log_entry: str | None = Field(None, description="Transparency log reference")


# ─────────────────────────────────────────────────────────────────────────────
# Metadata
# ─────────────────────────────────────────────────────────────────────────────


class Metadata(BaseModel):
    """Additional metadata."""
    
    tags: list[str] = Field(default_factory=list)
    custom: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# RunProof (Top-level)
# ─────────────────────────────────────────────────────────────────────────────


class RunProof(BaseModel):
    """
    RunProof v2 - Cryptographically verifiable receipt for agent execution.
    
    Proves that a specific agent/runtime identity produced a specific ordered
    execution trace and outputs under a specific policy context, and that the
    artifact has not been altered since signing.
    """
    
    schema_version: Literal["runproof/v2"] = Field(
        "runproof/v2", description="Schema version"
    )
    header: RunProofHeader
    identity: Identity
    context: Context
    trace: list[TraceEntry] = Field(default_factory=list)
    outputs: Outputs
    commitments: Commitments
    anchors: Anchors = Field(default_factory=Anchors)
    metadata: Metadata = Field(default_factory=Metadata)
    
    model_config = {
        "json_schema_extra": {
            "title": "RunProof",
            "description": "Cryptographically verifiable receipt for agent execution",
            "$id": "https://substr8labs.com/schemas/runproof/v2"
        }
    }
