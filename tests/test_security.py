"""Tests for PII protection and security components."""

import pytest

from services.security.kms_stub import DecryptionResult, EncryptionResult, KMSStub
from services.security.pii_scanner import PIIScanner


class TestPIIScanner:
    """Test cases for PII scanner."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = PIIScanner()

    def test_email_detection(self):
        """Test email address detection."""
        text = "Contact john.doe@example.com for support"
        findings = self.scanner.scan_text(text)

        assert len(findings) == 1
        assert findings[0]["type"] == "email"
        assert findings[0]["value"] == "john.doe@example.com"
        assert findings[0]["confidence"] == 0.95

    def test_phone_detection(self):
        """Test phone number detection."""
        text = "Call me at (555) 123-4567 or 555.123.4567"
        findings = self.scanner.scan_text(text)

        phone_findings = [f for f in findings if f["type"] == "phone"]
        assert len(phone_findings) >= 1

    def test_ssn_detection(self):
        """Test SSN detection."""
        text = "SSN: 123-45-6789"
        findings = self.scanner.scan_text(text)

        ssn_findings = [f for f in findings if f["type"] == "ssn"]
        assert len(ssn_findings) == 1
        assert ssn_findings[0]["value"] == "123-45-6789"

    def test_credit_card_detection(self):
        """Test credit card number detection."""
        text = "Card: 4111 1111 1111 1111"
        findings = self.scanner.scan_text(text)

        cc_findings = [f for f in findings if f["type"] == "credit_card"]
        assert len(cc_findings) == 1

    def test_ip_detection(self):
        """Test IP address detection."""
        text = "Server IP: 192.168.1.1"
        findings = self.scanner.scan_text(text)

        ip_findings = [f for f in findings if f["type"] == "ip_address"]
        assert len(ip_findings) == 1
        assert ip_findings[0]["value"] == "192.168.1.1"

    def test_multiple_pii_types(self):
        """Test detection of multiple PII types in one text."""
        text = """
        User john.doe@example.com registered with phone (555) 123-4567.
        SSN: 123-45-6789, IP: 192.168.1.1
        """
        findings = self.scanner.scan_text(text)

        types_found = {f["type"] for f in findings}
        expected_types = {"email", "phone", "ssn", "ip_address"}

        assert expected_types.issubset(types_found)

    def test_scan_and_tokenize(self):
        """Test PII scanning and tokenization."""
        text = "Email: john.doe@example.com, Phone: (555) 123-4567"
        result = self.scanner.scan_and_tokenize(text)

        assert result["has_pii"] is True
        assert result["pii_count"] >= 2
        assert "tokenized_text" in result
        assert "tokens" in result

        # Check that tokens replace original values
        assert "john.doe@example.com" not in result["tokenized_text"]
        assert "(555) 123-4567" not in result["tokenized_text"]
        assert "[EMAIL_TOKEN_" in result["tokenized_text"]

    def test_no_pii_found(self):
        """Test scanning text with no PII."""
        text = "This is just regular text with no sensitive information."
        result = self.scanner.scan_and_tokenize(text)

        assert result["has_pii"] is False
        assert result["pii_count"] == 0
        assert result["original_text"] == result["tokenized_text"]

    def test_get_supported_pii_types(self):
        """Test getting supported PII types."""
        types = self.scanner.get_supported_pii_types()

        expected_types = ["email", "phone", "ssn", "credit_card", "ip_address", "api_key"]
        assert all(t in types for t in expected_types)

    def test_email_validation(self):
        """Test email validation."""
        assert self.scanner._validate_email("test@example.com") is True
        assert self.scanner._validate_email("invalid-email") is False
        assert self.scanner._validate_email("test@.com") is False

    def test_phone_validation(self):
        """Test phone number validation."""
        assert self.scanner._validate_phone("(555) 123-4567") is True
        assert self.scanner._validate_phone("555-123-4567") is True
        assert self.scanner._validate_phone("abc-123-4567") is False
        assert self.scanner._validate_phone("123") is False

    def test_ssn_validation(self):
        """Test SSN validation."""
        assert self.scanner._validate_ssn("123-45-6789") is True
        assert self.scanner._validate_ssn("123456789") is True
        assert self.scanner._validate_ssn("000-00-0000") is False
        assert self.scanner._validate_ssn("123-45-67") is False

    def test_credit_card_validation(self):
        """Test credit card validation using Luhn algorithm."""
        # Valid test card number
        assert self.scanner._validate_credit_card("4111111111111111") is True
        # Invalid card number
        assert self.scanner._validate_credit_card("4111111111111112") is False

    def test_ip_validation(self):
        """Test IP address validation."""
        assert self.scanner._validate_ip("192.168.1.1") is True
        assert self.scanner._validate_ip("255.255.255.255") is True
        assert self.scanner._validate_ip("256.1.1.1") is False
        assert self.scanner._validate_ip("192.168.1") is False


class TestKMSStub:
    """Test cases for KMS stub with PII protection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.kms = KMSStub(master_key="test_master_key_12345")

    def test_initialization(self):
        """Test KMS stub initialization."""
        assert self.kms.master_key is not None
        assert isinstance(self.kms._token_store, dict)
        assert isinstance(self.kms._reverse_store, dict)

    def test_scan_and_tokenize_pii(self):
        """Test PII scanning and tokenization in KMS."""
        text = "Contact john.doe@example.com for support"
        result = self.kms.scan_and_tokenize_pii(text)

        assert result["has_pii"] is True
        assert result["pii_count"] == 1
        assert "john.doe@example.com" not in result["tokenized_data"]
        assert "TK_" in result["tokenized_data"]

    def test_restore_pii_from_tokens(self):
        """Test PII restoration from tokens."""
        # First tokenize
        text = "Email: test@example.com"
        tokenized_result = self.kms.scan_and_tokenize_pii(text)

        # Then restore
        restored = self.kms.restore_pii_from_tokens(tokenized_result["tokenized_data"])

        assert restored == text

    @pytest.mark.asyncio
    async def test_encrypt_with_pii_protection(self):
        """Test encryption with automatic PII tokenization."""
        text = "User john.doe@example.com logged in from 192.168.1.1"

        result = await self.kms.encrypt_with_pii_protection(text, key_id="test_key")

        assert isinstance(result, EncryptionResult)
        assert result.key_id == "test_key"
        assert result.algorithm == "AES-XOR-256"
        assert len(result.pii_tokens) >= 2  # email and IP
        assert "john.doe@example.com" in result.pii_tokens.values()

    @pytest.mark.asyncio
    async def test_encrypt_without_pii(self):
        """Test encryption of text without PII."""
        text = "This is just regular text"

        result = await self.kms.encrypt_with_pii_protection(text, key_id="test_key")

        assert isinstance(result, EncryptionResult)
        assert len(result.pii_tokens) == 0
        assert result.key_id == "test_key"

    @pytest.mark.asyncio
    async def test_decrypt_with_pii_restoration(self):
        """Test decryption with PII restoration."""
        original_text = "Contact john.doe@example.com"

        # Encrypt
        encrypt_result = await self.kms.encrypt_with_pii_protection(
            original_text, key_id="test_key"
        )

        # Decrypt with tokens
        decrypt_result = await self.kms.decrypt_with_pii_restoration(
            encrypt_result.encrypted_data, key_id="test_key", pii_tokens=encrypt_result.pii_tokens
        )

        assert isinstance(decrypt_result, DecryptionResult)
        assert decrypt_result.decrypted_data == original_text
        assert decrypt_result.pii_restored is True

    @pytest.mark.asyncio
    async def test_decrypt_without_pii_tokens(self):
        """Test decryption without PII tokens."""
        text = "This is just regular text"

        # Encrypt
        encrypt_result = await self.kms.encrypt_with_pii_protection(text, key_id="test_key")

        # Decrypt without tokens
        decrypt_result = await self.kms.decrypt_with_pii_restoration(
            encrypt_result.encrypted_data, key_id="test_key"
        )

        assert decrypt_result.decrypted_data == text
        assert decrypt_result.pii_restored is False

    def test_generate_token(self):
        """Test token generation."""
        value1 = "test@example.com"
        value2 = "test@example.com"  # Same value should generate same token

        token1 = self.kms._generate_token(value1)
        token2 = self.kms._generate_token(value2)

        assert token1 == token2
        assert token1.startswith("TK_")
        assert len(token1) == 24  # TK_ + 16 hex chars

    def test_restore_from_token(self):
        """Test token restoration."""
        original_value = "test@example.com"
        token = self.kms._generate_token(original_value)

        restored_value = self.kms._restore_from_token(token)

        assert restored_value == original_value

    def test_get_pii_statistics(self):
        """Test PII statistics retrieval."""
        # Add some tokens
        self.kms._generate_token("test1@example.com")
        self.kms._generate_token("test2@example.com")

        stats = self.kms.get_pii_statistics()

        assert stats["total_tokens"] == 2
        assert stats["total_hashes"] == 2
        assert isinstance(stats["token_sample"], list)

    def test_clear_pii_store(self):
        """Test PII store clearing."""
        # Add some tokens
        self.kms._generate_token("test@example.com")

        assert len(self.kms._token_store) > 0

        self.kms.clear_pii_store()

        assert len(self.kms._token_store) == 0
        assert len(self.kms._reverse_store) == 0

    def test_encrypt_decrypt_roundtrip(self):
        """Test full encrypt/decrypt roundtrip."""
        import asyncio

        async def test_roundtrip():
            original_text = "User john.doe@example.com with SSN 123-45-6789"

            # Encrypt
            encrypt_result = await self.kms.encrypt_with_pii_protection(
                original_text, key_id="test_key"
            )

            # Decrypt
            decrypt_result = await self.kms.decrypt_with_pii_restoration(
                encrypt_result.encrypted_data,
                key_id="test_key",
                pii_tokens=encrypt_result.pii_tokens,
            )

            assert decrypt_result.decrypted_data == original_text
            assert decrypt_result.pii_restored is True

        asyncio.run(test_roundtrip())

    def test_different_key_ids(self):
        """Test encryption with different key IDs."""
        import asyncio

        async def test_different_keys():
            text = "Test data"
            key_id1 = "key1"
            key_id2 = "key2"

            result1 = await self.kms.encrypt_with_pii_protection(text, key_id=key_id1)
            result2 = await self.kms.encrypt_with_pii_protection(text, key_id=key_id2)

            # Different key IDs should produce different encrypted data
            assert result1.encrypted_data != result2.encrypted_data
            assert result1.key_id == key_id1
            assert result2.key_id == key_id2

        asyncio.run(test_different_keys())


class TestPIIProtectionIntegration:
    """Integration tests for PII protection system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.kms = KMSStub()

    @pytest.mark.asyncio
    async def test_complex_pii_scenario(self):
        """Test complex scenario with multiple PII types."""
        complex_text = """
        Customer john.doe@example.com registered on 2024-01-15.
        Phone: (555) 123-4567, SSN: 123-45-6789
        Billing address: 123 Main St, IP: 192.168.1.1
        Card ending in 4111
        """

        # Encrypt with PII protection
        encrypt_result = await self.kms.encrypt_with_pii_protection(
            complex_text, key_id="customer_data"
        )

        # Verify PII was detected and tokenized
        assert len(encrypt_result.pii_tokens) >= 4  # email, phone, ssn, ip

        # Decrypt and verify restoration
        decrypt_result = await self.kms.decrypt_with_pii_restoration(
            encrypt_result.encrypted_data,
            key_id="customer_data",
            pii_tokens=encrypt_result.pii_tokens,
        )

        assert decrypt_result.decrypted_data == complex_text
        assert decrypt_result.pii_restored is True

    @pytest.mark.asyncio
    async def test_partial_pii_restoration(self):
        """Test decryption with partial PII tokens."""
        text = "Contact john.doe@example.com or jane.smith@example.com"

        # Encrypt
        encrypt_result = await self.kms.encrypt_with_pii_protection(text, key_id="test")

        # Remove one token to simulate partial restoration
        tokens = encrypt_result.pii_tokens.copy()
        if len(tokens) > 1:
            first_token = next(iter(tokens.keys()))
            del tokens[first_token]

        # Decrypt with partial tokens
        decrypt_result = await self.kms.decrypt_with_pii_restoration(
            encrypt_result.encrypted_data, key_id="test", pii_tokens=tokens
        )

        # Should still decrypt but with some tokens not restored
        assert decrypt_result.decrypted_data != text  # Won't be identical
        assert "[EMAIL_TOKEN_" in decrypt_result.decrypted_data  # Some tokens remain

        emails_in_result = [
            email
            for email in encrypt_result.pii_tokens.values()
            if email in decrypt_result.decrypted_data
        ]
        assert len(emails_in_result) > 0

    def test_pii_statistics_tracking(self):
        """Test PII statistics are properly tracked."""
        # Start with clean slate
        self.kms.clear_pii_store()

        # Process text with PII
        text = "Emails: test1@example.com, test2@example.com, test3@example.com"
        self.kms.scan_and_tokenize_pii(text)

        stats = self.kms.get_pii_statistics()

        assert stats["total_tokens"] == 3
        assert stats["total_hashes"] == 3
        assert len(stats["token_sample"]) <= 5  # Limited sample
