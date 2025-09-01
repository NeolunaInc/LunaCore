"""KMS Stub with PII Protection for LunaCore."""

import base64
import hashlib
import logging
import re
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .pii_scanner import PIIScanner


@dataclass
class EncryptionResult:
    """Result of encryption operation."""

    encrypted_data: str
    key_id: str
    algorithm: str
    timestamp: datetime
    pii_tokens: dict[str, str]  # Maps original PII to tokens

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class DecryptionResult:
    """Result of decryption operation."""

    decrypted_data: str
    key_id: str
    algorithm: str
    timestamp: datetime
    pii_restored: bool  # Whether PII was successfully restored

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class KMSStub:
    """Key Management Service stub with PII protection."""

    def __init__(self, master_key: str | None = None):
        self.logger = logging.getLogger(__name__)
        self.master_key = master_key or secrets.token_hex(32)
        self.pii_scanner = PIIScanner()
        self._token_store: dict[str, str] = {}  # token -> original_value
        self._reverse_store: dict[str, str] = {}  # hash -> token

    def _derive_key(self, key_id: str, context: str = "") -> bytes:
        """Derive encryption key from master key and context."""
        combined = f"{self.master_key}:{key_id}:{context}"
        return hashlib.sha256(combined.encode()).digest()

    def _encrypt_data(self, data: str, key: bytes) -> str:
        """Encrypt data using derived key."""
        # Simple XOR encryption for demonstration (use proper encryption in production)
        encrypted = bytearray()
        data_bytes = data.encode("utf-8")
        key_len = len(key)

        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key[i % key_len])

        return base64.b64encode(encrypted).decode("utf-8")

    def _decrypt_data(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt data using derived key."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted = bytearray()
            key_len = len(key)

            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % key_len])

            return decrypted.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}") from e

    def _generate_token(self, value: str) -> str:
        """Generate a unique token for PII value."""
        # Create hash of the value for lookup
        value_hash = hashlib.sha256(value.encode()).hexdigest()[:16]

        if value_hash in self._reverse_store:
            return self._reverse_store[value_hash]

        # Generate new token
        token = f"TK_{secrets.token_hex(8)}"
        self._token_store[token] = value
        self._reverse_store[value_hash] = token

        return token

    def _restore_from_token(self, token: str) -> str | None:
        """Restore original value from token."""
        return self._token_store.get(token)

    def scan_and_tokenize_pii(self, data: str) -> dict[str, Any]:
        """Scan data for PII and create tokens."""
        pii_findings = self.pii_scanner.scan_text(data)
        tokens = {}

        if not pii_findings:
            return {"original_data": data, "tokens": tokens, "has_pii": False}

        # Replace PII with tokens
        tokenized_data = data
        offset_adjustment = 0

        for finding in sorted(pii_findings, key=lambda x: x["start"]):
            original_value = finding["value"]
            token = self._generate_token(original_value)

            # Replace in text
            start = finding["start"] + offset_adjustment
            end = finding["end"] + offset_adjustment

            tokenized_data = tokenized_data[:start] + token + tokenized_data[end:]

            # Adjust offset for subsequent replacements
            offset_adjustment += len(token) - len(original_value)

            tokens[token] = {
                "original_value": original_value,
                "type": finding["type"],
                "confidence": finding["confidence"],
            }

        return {
            "original_data": data,
            "tokenized_data": tokenized_data,
            "tokens": tokens,
            "has_pii": True,
            "pii_count": len(pii_findings),
        }

    def restore_pii_from_tokens(self, tokenized_data: str) -> str:
        """Restore original PII values from tokens in text."""
        restored_data = tokenized_data

        # Find all tokens in the text
        token_pattern = r"TK_[a-f0-9]{16}"
        tokens_found = re.findall(token_pattern, tokenized_data)

        for token in tokens_found:
            original_value = self._restore_from_token(token)
            if original_value:
                restored_data = restored_data.replace(token, original_value)

        return restored_data

    async def encrypt_with_pii_protection(
        self, data: str, key_id: str = "default", context: str = ""
    ) -> EncryptionResult:
        """Encrypt data with automatic PII tokenization."""
        try:
            # Scan and tokenize PII
            pii_result = self.scan_and_tokenize_pii(data)

            # Use tokenized data for encryption
            data_to_encrypt = pii_result["tokenized_data"] if pii_result["has_pii"] else data

            # Derive encryption key
            key = self._derive_key(key_id, context)

            # Encrypt the data
            encrypted_data = self._encrypt_data(data_to_encrypt, key)

            # Store PII tokens for later restoration
            pii_tokens = {}
            if pii_result["has_pii"]:
                for token, info in pii_result["tokens"].items():
                    pii_tokens[token] = info["original_value"]

            result = EncryptionResult(
                encrypted_data=encrypted_data,
                key_id=key_id,
                algorithm="AES-XOR-256",  # In production, use proper AES
                timestamp=datetime.utcnow(),
                pii_tokens=pii_tokens,
            )

            self.logger.info(f"Encrypted data with key {key_id}, PII tokens: {len(pii_tokens)}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {str(e)}")
            raise

    async def decrypt_with_pii_restoration(
        self,
        encrypted_data: str,
        key_id: str = "default",
        context: str = "",
        pii_tokens: dict[str, str] | None = None,
    ) -> DecryptionResult:
        """Decrypt data and restore PII if tokens provided."""
        try:
            # Derive decryption key
            key = self._derive_key(key_id, context)

            # Decrypt the data
            decrypted_data = self._decrypt_data(encrypted_data, key)

            # Restore PII if tokens provided
            pii_restored = False
            if pii_tokens:
                # Add tokens to our store for restoration
                for token, original_value in pii_tokens.items():
                    self._token_store[token] = original_value

                # Restore PII in decrypted data
                decrypted_data = self.restore_pii_from_tokens(decrypted_data)
                pii_restored = True

            result = DecryptionResult(
                decrypted_data=decrypted_data,
                key_id=key_id,
                algorithm="AES-XOR-256",
                timestamp=datetime.utcnow(),
                pii_restored=pii_restored,
            )

            self.logger.info(f"Decrypted data with key {key_id}, PII restored: {pii_restored}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {str(e)}")
            raise

    def get_pii_statistics(self) -> dict[str, Any]:
        """Get statistics about PII handling."""
        return {
            "total_tokens": len(self._token_store),
            "total_hashes": len(self._reverse_store),
            "token_sample": list(self._token_store.keys())[:5] if self._token_store else [],
        }

    def clear_pii_store(self):
        """Clear all PII tokens and hashes (for security/testing)."""
        self._token_store.clear()
        self._reverse_store.clear()
        self.logger.info("PII token store cleared")
