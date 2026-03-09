"""RunProof verification utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .crypto import compute_merkle_root, verify_hash_chain, sha256_json, verify_signature_str


@dataclass
class CheckResult:
    """Result of a single verification check."""
    
    name: str
    passed: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Complete verification result."""
    
    valid: bool
    proof_id: str | None = None
    run_id: str | None = None
    agent_id: str | None = None
    checks: list[CheckResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    
    @property
    def summary(self) -> dict[str, Any]:
        """Get summary for display."""
        return {
            "valid": self.valid,
            "proof_id": self.proof_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "checks": {c.name: c.passed for c in self.checks},
            "errors": self.errors,
        }


def verify_runproof(proof: dict[str, Any]) -> VerificationResult:
    """
    Verify a RunProof artifact.
    
    Performs:
    1. Schema validation
    2. Hash chain verification
    3. Merkle root verification
    4. Signature verification
    
    Args:
        proof: RunProof as dictionary
    
    Returns:
        VerificationResult with all check details
    """
    result = VerificationResult(valid=False)
    
    # Extract header info
    header = proof.get("header", {})
    result.proof_id = header.get("proof_id")
    result.run_id = header.get("run_id")
    result.agent_id = header.get("agent_id")
    
    # ─── Check 1: Schema ──────────────────────────────────────────────────────
    schema_check = _verify_schema(proof)
    result.checks.append(schema_check)
    
    if not schema_check.passed:
        result.errors.append("Schema validation failed")
        return result
    
    # ─── Check 2: Hash Chain ──────────────────────────────────────────────────
    trace = proof.get("trace", [])
    chain_valid, chain_errors = verify_hash_chain(trace)
    
    chain_check = CheckResult(
        name="hash_chain",
        passed=chain_valid,
        message="Event chain intact" if chain_valid else "Chain broken",
        details={"errors": chain_errors} if chain_errors else {},
    )
    result.checks.append(chain_check)
    
    if not chain_valid:
        result.errors.extend(chain_errors)
    
    # ─── Check 3: Merkle Root ─────────────────────────────────────────────────
    entry_hashes = [e.get("entry_hash", "") for e in trace]
    computed_root = compute_merkle_root(entry_hashes)
    
    commitments = proof.get("commitments", {})
    expected_root = commitments.get("event_root", "")
    
    merkle_valid = computed_root == expected_root
    
    merkle_check = CheckResult(
        name="merkle_root",
        passed=merkle_valid,
        message="Merkle root matches" if merkle_valid else "Merkle root mismatch",
        details={
            "computed": computed_root[:20] + "..." if computed_root else "",
            "expected": expected_root[:20] + "..." if expected_root else "",
        },
    )
    result.checks.append(merkle_check)
    
    if not merkle_valid:
        result.errors.append("Merkle root mismatch")
    
    # ─── Check 4: Signature ───────────────────────────────────────────────────
    sig_check = _verify_signature(proof)
    result.checks.append(sig_check)
    
    if not sig_check.passed:
        result.errors.append("Signature verification failed")
    
    # ─── Final Result ─────────────────────────────────────────────────────────
    result.valid = all(c.passed for c in result.checks)
    
    return result


def _verify_schema(proof: dict[str, Any]) -> CheckResult:
    """Verify proof schema structure."""
    errors = []
    
    # Check schema version
    version = proof.get("schema_version")
    if version != "runproof/v2":
        errors.append(f"Expected schema_version 'runproof/v2', got '{version}'")
    
    # Check required top-level fields
    required = ["header", "identity", "context", "trace", "outputs", "commitments"]
    for field_name in required:
        if field_name not in proof:
            errors.append(f"Missing required field: {field_name}")
    
    # Check header fields
    header = proof.get("header", {})
    header_required = ["proof_id", "run_id", "agent_id", "runtime", "started_at", "status"]
    for field_name in header_required:
        if field_name not in header:
            errors.append(f"Missing header field: {field_name}")
    
    # Check identity fields
    identity = proof.get("identity", {})
    signer = identity.get("signer", {})
    signer_required = ["key_id", "public_key", "issuer"]
    for field_name in signer_required:
        if field_name not in signer:
            errors.append(f"Missing signer field: {field_name}")
    
    # Check commitments fields
    commitments = proof.get("commitments", {})
    commits_required = ["event_root", "proof_hash", "signature"]
    for field_name in commits_required:
        if field_name not in commitments:
            errors.append(f"Missing commitments field: {field_name}")
    
    return CheckResult(
        name="schema",
        passed=len(errors) == 0,
        message="Schema valid" if not errors else "Schema invalid",
        details={"errors": errors} if errors else {},
    )


def _verify_signature(proof: dict[str, Any]) -> CheckResult:
    """Verify proof signature."""
    try:
        identity = proof.get("identity", {})
        signer = identity.get("signer", {})
        public_key = signer.get("public_key", "")
        
        commitments = proof.get("commitments", {})
        signature = commitments.get("signature", {})
        sig_value = signature.get("value", "")
        proof_hash = commitments.get("proof_hash", "")
        
        if not public_key or not sig_value or not proof_hash:
            return CheckResult(
                name="signature",
                passed=False,
                message="Missing signature components",
            )
        
        # Verify signature over proof_hash
        valid = verify_signature_str(public_key, sig_value, proof_hash)
        
        return CheckResult(
            name="signature",
            passed=valid,
            message="Signature valid" if valid else "Signature invalid",
            details={
                "key_id": signer.get("key_id"),
                "issuer": signer.get("issuer"),
                "algorithm": signature.get("algorithm"),
            },
        )
        
    except Exception as e:
        return CheckResult(
            name="signature",
            passed=False,
            message=f"Signature verification error: {e}",
        )
