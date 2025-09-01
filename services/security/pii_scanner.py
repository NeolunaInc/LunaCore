"""PII Scanner for detecting and tokenizing sensitive information."""

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PIIFinding:
    """Represents a PII finding in text."""

    type: str
    value: str
    start: int
    end: int
    confidence: float
    context: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "context": self.context,
        }


class PIIScanner:
    """Scanner for detecting Personally Identifiable Information (PII)."""

    def __init__(self):
        # Email pattern
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

        # Phone number patterns (US, international formats)
        self.phone_patterns = [
            re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),  # 123-456-7890 format
            re.compile(r"\(\d{3}\)\s*\d{3}[-.]?\d{4}"),  # (123) 456-7890
            re.compile(r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}"),  # +1 123 456 7890
        ]

        # SSN pattern (US Social Security Number)
        self.ssn_pattern = re.compile(r"\b\d{3}[-]?\d{2}[-]?\d{4}\b")

        # Credit card patterns (basic detection)
        self.cc_patterns = [
            re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),  # 16-digit cards
            re.compile(r"\b\d{4}[- ]?\d{6}[- ]?\d{5}\b"),  # 15-digit cards (Amex)
        ]

        # IP address pattern
        self.ip_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

        # API key patterns (common formats)
        self.api_key_patterns = [
            re.compile(r"\b[A-Za-z0-9]{32}\b"),  # 32-char keys
            re.compile(r"\b[A-Za-z0-9]{40}\b"),  # 40-char keys (GitHub tokens)
            re.compile(r"\bsk-[A-Za-z0-9]{48}\b"),  # OpenAI API keys
            re.compile(r"\b[A-Za-z0-9_-]{20,100}\b"),  # Generic API keys
        ]

    def _validate_email(self, email: str) -> bool:
        """Validate email format more thoroughly."""
        if not self.email_pattern.match(email):
            return False

        # Additional validation
        local, domain = email.split("@", 1)

        # Local part should not be too long
        if len(local) > 64:
            return False

        # Domain should have valid structure
        return "." in domain and len(domain) >= 4

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        # Remove formatting characters
        clean_phone = re.sub(r"[\s\-\(\)\.\+]", "", phone)

        # Should be 10-15 digits
        if not 10 <= len(clean_phone) <= 15:
            return False

        # Should contain only digits
        return clean_phone.isdigit()

    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format."""
        clean_ssn = re.sub(r"[-]", "", ssn)

        if len(clean_ssn) != 9:
            return False

        # Check for invalid patterns (all zeros, sequential)
        if clean_ssn in [
            "000000000",
            "111111111",
            "222222222",
            "333333333",
            "444444444",
            "555555555",
            "666666666",
            "777777777",
            "888888888",
            "999999999",
        ]:
            return False

        # Check area number (first 3 digits)
        area = int(clean_ssn[:3])
        return area != 0 and area < 900

    def _validate_credit_card(self, cc: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        clean_cc = re.sub(r"[\s-]", "", cc)

        if not 13 <= len(clean_cc) <= 19:
            return False

        # Luhn algorithm
        def luhn_checksum(card_num: str) -> bool:
            def digits_of(n: str) -> list[int]:
                return [int(d) for d in n]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(str(d * 2)))
            return checksum % 10 == 0

        return luhn_checksum(clean_cc)

    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address format."""
        parts = ip.split(".")
        if len(parts) != 4:
            return False

        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if not 0 <= num <= 255:
                return False

        return True

    def _get_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Get context around a PII finding."""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        return text[context_start:context_end]

    def scan_text(self, text: str) -> list[dict[str, Any]]:
        """Scan text for PII and return findings."""
        findings = []

        # Scan for emails
        for match in self.email_pattern.finditer(text):
            email = match.group()
            if self._validate_email(email):
                findings.append(
                    PIIFinding(
                        type="email",
                        value=email,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.95,
                        context=self._get_context(text, match.start(), match.end()),
                    ).to_dict()
                )

        # Scan for phone numbers
        for pattern in self.phone_patterns:
            for match in pattern.finditer(text):
                phone = match.group()
                if self._validate_phone(phone):
                    findings.append(
                        PIIFinding(
                            type="phone",
                            value=phone,
                            start=match.start(),
                            end=match.end(),
                            confidence=0.90,
                            context=self._get_context(text, match.start(), match.end()),
                        ).to_dict()
                    )

        # Scan for SSNs
        for match in self.ssn_pattern.finditer(text):
            ssn = match.group()
            if self._validate_ssn(ssn):
                findings.append(
                    PIIFinding(
                        type="ssn",
                        value=ssn,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.98,
                        context=self._get_context(text, match.start(), match.end()),
                    ).to_dict()
                )

        # Scan for credit cards
        for pattern in self.cc_patterns:
            for match in pattern.finditer(text):
                cc = match.group()
                if self._validate_credit_card(cc):
                    findings.append(
                        PIIFinding(
                            type="credit_card",
                            value=cc,
                            start=match.start(),
                            end=match.end(),
                            confidence=0.85,
                            context=self._get_context(text, match.start(), match.end()),
                        ).to_dict()
                    )

        # Scan for IP addresses
        for match in self.ip_pattern.finditer(text):
            ip = match.group()
            if self._validate_ip(ip):
                findings.append(
                    PIIFinding(
                        type="ip_address",
                        value=ip,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.80,
                        context=self._get_context(text, match.start(), match.end()),
                    ).to_dict()
                )

        # Scan for API keys (lower confidence)
        for pattern in self.api_key_patterns:
            for match in pattern.finditer(text):
                api_key = match.group()
                # Additional validation for API keys
                if (
                    len(api_key) >= 20
                    and any(c.isupper() for c in api_key)
                    and any(c.islower() for c in api_key)
                ):
                    findings.append(
                        PIIFinding(
                            type="api_key",
                            value=api_key,
                            start=match.start(),
                            end=match.end(),
                            confidence=0.60,
                            context=self._get_context(text, match.start(), match.end()),
                        ).to_dict()
                    )

        return findings

    def scan_and_tokenize(self, text: str) -> dict[str, Any]:
        """Scan text for PII and return tokenized version."""
        findings = self.scan_text(text)

        if not findings:
            return {"original_text": text, "tokenized_text": text, "findings": [], "has_pii": False}

        # Sort findings by position (reverse order to avoid offset issues)
        findings.sort(key=lambda x: x["start"], reverse=True)

        tokenized_text = text
        tokens = {}

        for finding in findings:
            original_value = finding["value"]
            token = f"[{finding['type'].upper()}_TOKEN_{len(tokens)}]"

            # Replace in text
            start = finding["start"]
            end = finding["end"]
            tokenized_text = tokenized_text[:start] + token + tokenized_text[end:]

            tokens[token] = {
                "original_value": original_value,
                "type": finding["type"],
                "confidence": finding["confidence"],
            }

        return {
            "original_text": text,
            "tokenized_text": tokenized_text,
            "findings": findings,
            "tokens": tokens,
            "has_pii": True,
            "pii_count": len(findings),
        }

    def get_supported_pii_types(self) -> list[str]:
        """Get list of supported PII types."""
        return ["email", "phone", "ssn", "credit_card", "ip_address", "api_key"]
