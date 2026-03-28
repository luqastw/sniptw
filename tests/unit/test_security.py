"""Unit tests for security functions."""

import pytest
from jose import jwt

from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class TestHashPassword:
    """Tests for hash_password function."""

    def test_hash_password_returns_string(self):
        """hash_password should return a string."""
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_hash_password_returns_bcrypt_hash(self):
        """hash_password should return a valid bcrypt hash."""
        result = hash_password("mypassword")
        # bcrypt hashes start with $2b$ (or $2a$, $2y$)
        assert result.startswith("$2")

    def test_hash_password_different_for_same_input(self):
        """hash_password should produce different hashes for same password (due to salt)."""
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_hash_password_with_empty_string(self):
        """hash_password should work with empty string."""
        result = hash_password("")
        assert isinstance(result, str)
        assert result.startswith("$2")

    def test_hash_password_with_special_characters(self):
        """hash_password should handle special characters."""
        result = hash_password("p@$$w0rd!#$%^&*()")
        assert isinstance(result, str)
        assert result.startswith("$2")

    def test_hash_password_with_unicode(self):
        """hash_password should handle unicode characters."""
        result = hash_password("senhaçãoéêü")
        assert isinstance(result, str)
        assert result.startswith("$2")


class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_verify_password_correct(self):
        """verify_password should return True for correct password."""
        password = "correctpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password should return False for incorrect password."""
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_string(self):
        """verify_password should work with empty string."""
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_verify_password_special_characters(self):
        """verify_password should handle special characters."""
        password = "p@$$w0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_unicode(self):
        """verify_password should handle unicode characters."""
        password = "senhaçãoéêü"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_case_sensitive(self):
        """verify_password should be case sensitive."""
        hashed = hash_password("Password")
        assert verify_password("password", hashed) is False
        assert verify_password("PASSWORD", hashed) is False
        assert verify_password("Password", hashed) is True


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_returns_string(self):
        """create_access_token should return a string."""
        token = create_access_token({"sub": "test@example.com"})
        assert isinstance(token, str)

    def test_create_access_token_is_valid_jwt(self):
        """create_access_token should return a valid JWT."""
        token = create_access_token({"sub": "test@example.com"})
        # JWT has 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_access_token_contains_payload(self):
        """create_access_token should encode the payload correctly."""
        email = "test@example.com"
        token = create_access_token({"sub": email})

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert decoded["sub"] == email

    def test_create_access_token_contains_expiration(self):
        """create_access_token should include expiration claim."""
        token = create_access_token({"sub": "test@example.com"})

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert "exp" in decoded

    def test_create_access_token_preserves_extra_data(self):
        """create_access_token should preserve additional data in payload."""
        data = {"sub": "test@example.com", "role": "admin", "custom": "value"}
        token = create_access_token(data)

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "admin"
        assert decoded["custom"] == "value"

    def test_create_access_token_does_not_modify_input(self):
        """create_access_token should not modify the input data dict."""
        original_data = {"sub": "test@example.com"}
        data_copy = original_data.copy()

        create_access_token(original_data)

        assert original_data == data_copy

    def test_create_access_token_with_empty_dict(self):
        """create_access_token should work with empty dict."""
        token = create_access_token({})
        assert isinstance(token, str)

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert "exp" in decoded
