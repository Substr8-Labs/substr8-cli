"""RunState Schema

Live execution state for LangGraph orchestration.

Used by the State Orchestration Layer to manage:
- Run lifecycle
- Retries and loops
- Human-in-the-loop pauses
- Child agent delegation
- Checkpointing
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LifecycleStatus(str, Enum):
    """Run lifecycle states."""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_FOR_HUMAN = "waiting_for_human"
    WAITING_FOR_CHILD = "waiting_for_child"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HumanReviewStatus(str, Enum):
    """Human review state."""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SettlementStatus(str, Enum):
    """Economic settlement state."""
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    SUBMITTED = "submitted"
    SETTLED = "settled"
    FAILED = "failed"


# ─────────────────────────────────────────────────────────────────────────────
# Child Run Reference
# ─────────────────────────────────────────────────────────────────────────────


class ChildRunRef(BaseModel):
    """Reference to a child/delegated run."""
    
    run_id: str = Field(..., description="Child run identifier")
    agent_id: str = Field(..., description="Child agent identifier")
    status: str = Field(..., description="Child run status")
    proof_id: str | None = Field(None, description="Child proof ID if finalized")
    proof_hash: str | None = Field(None, description="Child proof hash")
    delegation_seq: int | None = Field(None, description="Sequence number of delegation event")
    started_at: datetime | None = None
    completed_at: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Human Review State
# ─────────────────────────────────────────────────────────────────────────────


class HumanReviewState(BaseModel):
    """Human-in-the-loop review state."""
    
    required: bool = Field(False, description="Whether human review is required")
    status: HumanReviewStatus = Field(
        HumanReviewStatus.NOT_REQUIRED, description="Current review status"
    )
    reviewer_id: str | None = Field(None, description="Reviewer identity")
    request_hash: str | None = Field(None, description="Hash of review request payload")
    response_hash: str | None = Field(None, description="Hash of review response")
    resume_token: str | None = Field(None, description="Token for resuming execution")
    requested_at: datetime | None = None
    responded_at: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Retry State
# ─────────────────────────────────────────────────────────────────────────────


class RetryState(BaseModel):
    """Retry tracking state."""
    
    count: int = Field(0, ge=0, description="Number of retries attempted")
    max_retries: int = Field(3, ge=0, description="Maximum retry budget")
    last_error: str | None = Field(None, description="Last error message")
    last_error_hash: str | None = Field(None, description="Hash of last error details")
    last_retry_at: datetime | None = None
    
    @property
    def can_retry(self) -> bool:
        """Check if retry budget remains."""
        return self.count < self.max_retries


# ─────────────────────────────────────────────────────────────────────────────
# Validation State
# ─────────────────────────────────────────────────────────────────────────────


class ValidationState(BaseModel):
    """Quality/validation loop state."""
    
    required: bool = Field(False, description="Whether validation is required")
    passed: bool | None = Field(None, description="Validation result")
    loop_count: int = Field(0, ge=0, description="Number of validation loops")
    max_loops: int = Field(3, ge=0, description="Maximum validation attempts")
    failure_reasons: list[str] = Field(default_factory=list)
    last_validated_at: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Settlement State
# ─────────────────────────────────────────────────────────────────────────────


class SettlementState(BaseModel):
    """Economic/payment state."""
    
    billable: bool = Field(False, description="Whether work is billable")
    accepted: bool = Field(False, description="Whether output was accepted")
    eligible_for_settlement: bool = Field(False, description="Ready for payment")
    settlement_status: SettlementStatus = Field(
        SettlementStatus.NOT_APPLICABLE, description="Settlement progress"
    )
    settlement_ref: str | None = Field(None, description="Ledger/payment reference")
    amount: float | None = Field(None, description="Settlement amount")
    currency: str | None = Field(None, description="Currency code")
    settled_at: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint
# ─────────────────────────────────────────────────────────────────────────────


class Checkpoint(BaseModel):
    """State checkpoint for resume/recovery."""
    
    checkpoint_id: str = Field(..., description="Unique checkpoint identifier")
    checkpoint_hash: str = Field(..., description="Hash of checkpoint state")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    node: str | None = Field(None, description="Graph node at checkpoint")
    step_index: int = Field(0, description="Step index at checkpoint")
    transition_reason: str | None = Field(None, description="Why checkpoint was created")
    last_event_id: str | None = Field(None, description="Last emitted event ID")


# ─────────────────────────────────────────────────────────────────────────────
# RunState (Top-level)
# ─────────────────────────────────────────────────────────────────────────────


class RunState(BaseModel):
    """
    Canonical live state object for a run.
    
    Managed by LangGraph as the State Orchestration Layer.
    RunProof is derived from state transitions, not from this object directly.
    """
    
    # ─── Identification ───────────────────────────────────────────────────────
    run_id: str = Field(..., description="Unique run identifier")
    workflow_id: str | None = Field(None, description="Workflow/job identifier")
    session_id: str | None = Field(None, description="Session/conversation identifier")
    agent_id: str = Field(..., description="Agent identifier")
    parent_run_id: str | None = Field(None, description="Parent run (if delegated)")
    
    # ─── Lifecycle ────────────────────────────────────────────────────────────
    lifecycle_status: LifecycleStatus = Field(
        LifecycleStatus.CREATED, description="Current lifecycle state"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    
    # ─── Execution ────────────────────────────────────────────────────────────
    current_node: str | None = Field(None, description="Current graph node")
    previous_node: str | None = Field(None, description="Previous graph node")
    step_index: int = Field(0, ge=0, description="Current step number")
    transition_reason: str | None = Field(None, description="Why last transition happened")
    branch_id: str | None = Field(None, description="Active branch identifier")
    loop_iteration: int = Field(0, ge=0, description="Current loop iteration")
    
    # ─── Input/Output ─────────────────────────────────────────────────────────
    input_hash: str | None = Field(None, description="Hash of input")
    output_hash: str | None = Field(None, description="Hash of output")
    
    # ─── Delegation ───────────────────────────────────────────────────────────
    child_runs: list[ChildRunRef] = Field(
        default_factory=list, description="Child/delegated runs"
    )
    
    # ─── Human Review ─────────────────────────────────────────────────────────
    human_review: HumanReviewState = Field(default_factory=HumanReviewState)
    
    # ─── Retry ────────────────────────────────────────────────────────────────
    retry: RetryState = Field(default_factory=RetryState)
    
    # ─── Validation ───────────────────────────────────────────────────────────
    validation: ValidationState = Field(default_factory=ValidationState)
    
    # ─── Settlement ───────────────────────────────────────────────────────────
    settlement: SettlementState = Field(default_factory=SettlementState)
    
    # ─── Checkpoints ──────────────────────────────────────────────────────────
    checkpoints: list[Checkpoint] = Field(
        default_factory=list, description="State checkpoints"
    )
    last_checkpoint_id: str | None = Field(None, description="Most recent checkpoint")
    
    # ─── Custom ───────────────────────────────────────────────────────────────
    tags: dict[str, Any] = Field(default_factory=dict, description="Custom tags/metadata")
    
    # ─── Helpers ──────────────────────────────────────────────────────────────
    
    @property
    def is_terminal(self) -> bool:
        """Check if run is in a terminal state."""
        return self.lifecycle_status in {
            LifecycleStatus.COMPLETED,
            LifecycleStatus.FAILED,
            LifecycleStatus.CANCELLED,
        }
    
    @property
    def is_waiting(self) -> bool:
        """Check if run is waiting for external input."""
        return self.lifecycle_status in {
            LifecycleStatus.WAITING_FOR_HUMAN,
            LifecycleStatus.WAITING_FOR_CHILD,
            LifecycleStatus.PAUSED,
        }
    
    @property
    def pending_children(self) -> list[ChildRunRef]:
        """Get child runs that haven't completed."""
        return [c for c in self.child_runs if c.status not in {"completed", "failed"}]
    
    def add_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Add a checkpoint to the state."""
        self.checkpoints.append(checkpoint)
        self.last_checkpoint_id = checkpoint.checkpoint_id
    
    def get_latest_checkpoint(self) -> Checkpoint | None:
        """Get the most recent checkpoint."""
        return self.checkpoints[-1] if self.checkpoints else None
