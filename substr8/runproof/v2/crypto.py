"""Cryptographic utilities for RunProof v2."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import CryptoError
from nacl.encoding import HexEncoder


# ─────────────────────────────────────────────────────────────────────────────
# Hashing
# ─────────────────────────────────────────────────────────────────────────────

def sha256_hex(data: bytes) -> str:
    """Compute SHA256 hash and return as prefixed hex string."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_str(s: str) -> str:
    """Hash a string with SHA256."""
    return sha256_hex(s.encode("utf-8"))


def canonical_json(obj: Any) -> str:
    """Serialize object to canonical (deterministic) JSON."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_json(obj: Any) -> str:
    """Hash a JSON-serializable object deterministically."""
    return sha256_str(canonical_json(obj))


def compute_entry_hash(
    seq: int,
    event_type: str,
    timestamp: str,
    prev_hash: str | None,
    payload_hash: str | None,
) -> str:
    """
    Compute entry hash for a trace entry.
    
    Formula: SHA256(seq|type|timestamp|prev_hash|payload_hash)
    """
    components = [
        str(seq),
        event_type,
        timestamp,
        prev_hash or "",
        payload_hash or "",
    ]
    return sha256_str("|".join(components))


def compute_merkle_root(entry_hashes: list[str]) -> str:
    """
    Compute Merkle root from a list of entry hashes.
    
    Uses a binary tree structure with pairwise hashing.
    """
    if not entry_hashes:
        return sha256_str("")
    
    if len(entry_hashes) == 1:
        return entry_hashes[0]
    
    current_level = list(entry_hashes)
    
    while len(current_level) > 1:
        next_level = []
        
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            combined = sha256_str(left + right)
            next_level.append(combined)
        
        current_level = next_level
    
    return current_level[0]


def verify_hash_chain(entries: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """
    Verify the hash chain integrity of trace entries.
    
    Returns:
        Tuple of (valid, errors)
    """
    errors = []
    
    if not entries:
        return True, []
    
    for i, entry in enumerate(entries):
        # Check sequence
        expected_seq = i + 1
        actual_seq = entry.get("seq")
        if actual_seq != expected_seq:
            errors.append(f"Entry {i}: expected seq {expected_seq}, got {actual_seq}")
        
        # Check prev_hash linkage
        if i > 0:
            prev_entry = entries[i - 1]
            expected_prev = prev_entry.get("entry_hash")
            actual_prev = entry.get("prev_hash")
            if actual_prev != expected_prev:
                errors.append(f"Entry {i}: prev_hash mismatch")
        
        # Recompute and verify entry_hash
        computed = compute_entry_hash(
            seq=entry.get("seq", 0),
            event_type=entry.get("type", ""),
            timestamp=entry.get("timestamp", ""),
            prev_hash=entry.get("prev_hash"),
            payload_hash=entry.get("payload_hash"),
        )
        
        if computed != entry.get("entry_hash"):
            errors.append(f"Entry {i}: entry_hash mismatch (chain broken)")
    
    return len(errors) == 0, errors


# ─────────────────────────────────────────────────────────────────────────────
# Signing (Ed25519)
# ─────────────────────────────────────────────────────────────────────────────

class KeyPair:
    """Ed25519 key pair for signing RunProof artifacts."""
    
    def __init__(self, signing_key: SigningKey, key_id: str):
        self._signing_key = signing_key
        self._verify_key = signing_key.verify_key
        self.key_id = key_id
    
    @classmethod
    def generate(cls, key_id: str = "default") -> "KeyPair":
        """Generate a new key pair."""
        return cls(SigningKey.generate(), key_id)
    
    @classmethod
    def from_seed(cls, seed: bytes, key_id: str = "default") -> "KeyPair":
        """Create key pair from a 32-byte seed."""
        return cls(SigningKey(seed), key_id)
    
    @property
    def public_key_bytes(self) -> bytes:
        return bytes(self._verify_key)
    
    @property
    def public_key_hex(self) -> str:
        return "ed25519:" + self._verify_key.encode(encoder=HexEncoder).decode()
    
    def sign(self, message: bytes) -> bytes:
        """Sign a message, returning the signature."""
        signed = self._signing_key.sign(message)
        return signed.signature
    
    def sign_str(self, message: str) -> str:
        """Sign a string message, returning base64 signature."""
        import base64
        sig = self.sign(message.encode("utf-8"))
        return base64.b64encode(sig).decode()


def verify_signature(public_key: bytes, signature: bytes, message: bytes) -> bool:
    """Verify an Ed25519 signature."""
    try:
        verify_key = VerifyKey(public_key)
        verify_key.verify(message, signature)
        return True
    except (CryptoError, ValueError, Exception):
        return False


def verify_signature_str(public_key_hex: str, signature_b64: str, message: str) -> bool:
    """Verify signature with hex public key and base64 signature."""
    import base64
    
    try:
        # Strip prefix
        if public_key_hex.startswith("ed25519:"):
            public_key_hex = public_key_hex[8:]
        
        public_key = bytes.fromhex(public_key_hex)
        signature = base64.b64decode(signature_b64)
        message_bytes = message.encode("utf-8")
        
        return verify_signature(public_key, signature, message_bytes)
    except (CryptoError, ValueError, Exception):
        return False
