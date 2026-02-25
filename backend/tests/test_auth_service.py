"""Tests for the authentication service (password hashing & verification).

The auth_service module imports python-jose at module level, which may fail
in some environments. We mock jose before importing to isolate the bcrypt
functions under test.
"""

import sys
from unittest.mock import MagicMock

import pytest

# Mock jose to avoid cryptography backend issues in CI/sandbox
_jose_mock = MagicMock()
sys.modules.setdefault("jose", _jose_mock)
sys.modules.setdefault("jose.jwt", _jose_mock)
sys.modules.setdefault("jose.jws", _jose_mock)
sys.modules.setdefault("jose.jwk", _jose_mock)
sys.modules.setdefault("jose.backends", _jose_mock)
sys.modules.setdefault("jose.backends.base", _jose_mock)
sys.modules.setdefault("jose.backends.cryptography_backend", _jose_mock)

from app.services.auth_service import hash_password, verify_password


class TestPasswordHashing:
    """bcrypt password hashing and verification."""

    def test_hash_produces_bcrypt_format(self) -> None:
        hashed = hash_password("secret123")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self) -> None:
        password = "myP@ssw0rd!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_reject_wrong_password(self) -> None:
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes_for_same_password(self) -> None:
        """bcrypt uses random salt, so hashes should differ."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_both_hashes_verify(self) -> None:
        password = "same"
        h1 = hash_password(password)
        h2 = hash_password(password)
        assert verify_password(password, h1) is True
        assert verify_password(password, h2) is True

    def test_unicode_password(self) -> None:
        password = "パスワード123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_empty_password(self) -> None:
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("not_empty", hashed) is False
