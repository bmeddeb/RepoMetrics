"""
Authentication utilities for Git provider API clients.
"""

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from GitFleet.providers.base import ProviderType


@dataclass
class CredentialEntry:
    """Represents a stored credential for a Git provider."""

    provider: ProviderType
    token: str
    username: Optional[str] = None
    host: Optional[str] = None


class CredentialManager:
    """Manages secure storage and retrieval of Git provider credentials."""

    _DEFAULT_CREDS_FILE = "~/.gitfleet/credentials.json"

    def __init__(self, credentials_file: Optional[str] = None):
        """Initialize the credential manager.

        Args:
            credentials_file: Path to the credentials file. If None, uses the default location.
        """
        self.credentials_file = credentials_file or os.path.expanduser(
            self._DEFAULT_CREDS_FILE
        )
        self._creds_cache: Dict[ProviderType, List[CredentialEntry]] = {}
        self._ensure_creds_dir()

    def _ensure_creds_dir(self) -> None:
        """Ensure the credentials directory exists."""
        creds_dir = os.path.dirname(self.credentials_file)
        os.makedirs(os.path.expanduser(creds_dir), exist_ok=True)

    def _encode_token(self, token: str) -> str:
        """Simple encoding of token (not secure, just to prevent casual viewing)."""
        return base64.b64encode(token.encode()).decode()

    def _decode_token(self, encoded_token: str) -> str:
        """Decode an encoded token."""
        return base64.b64decode(encoded_token.encode()).decode()

    def save_credential(
        self,
        provider: ProviderType,
        token: str,
        username: Optional[str] = None,
        host: Optional[str] = None,
    ) -> None:
        """Save a credential for a provider.

        Args:
            provider: The provider type
            token: The API token
            username: Optional username associated with the token
            host: Optional custom hostname (for enterprise instances)
        """
        # Load existing credentials
        try:
            with open(os.path.expanduser(self.credentials_file), "r") as f:
                creds_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            creds_data = {}

        # Initialize provider list if needed
        if provider.value not in creds_data:
            creds_data[provider.value] = []

        # Add the new credential
        creds_data[provider.value].append(
            {"token": self._encode_token(token), "username": username, "host": host}
        )

        # Save updated credentials
        with open(os.path.expanduser(self.credentials_file), "w") as f:
            json.dump(creds_data, f, indent=2)

        # Clear cache
        self._creds_cache = {}

    def get_credentials(
        self, provider: ProviderType, host: Optional[str] = None
    ) -> List[CredentialEntry]:
        """Get all credentials for a provider.

        Args:
            provider: The provider type
            host: Optional host to filter by (for enterprise instances)

        Returns:
            List of credential entries
        """
        # Check cache first
        cache_key = (provider, host) if host else provider
        if provider in self._creds_cache:
            return self._creds_cache[provider]

        # Load credentials from file
        try:
            with open(os.path.expanduser(self.credentials_file), "r") as f:
                creds_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        # Get credentials for the provider
        provider_creds = creds_data.get(provider.value, [])

        # Filter by host if specified
        if host:
            provider_creds = [
                cred
                for cred in provider_creds
                if cred.get("host") == host or cred.get("host") is None
            ]

        # Convert to CredentialEntry objects
        result = []
        for cred in provider_creds:
            result.append(
                CredentialEntry(
                    provider=provider,
                    token=self._decode_token(cred["token"]),
                    username=cred.get("username"),
                    host=cred.get("host"),
                )
            )

        # Update cache
        self._creds_cache[provider] = result
        return result

    def remove_credential(self, provider: ProviderType, token: str) -> bool:
        """Remove a credential.

        Args:
            provider: The provider type
            token: The token to remove (unencoded)

        Returns:
            True if the credential was removed, False if not found
        """
        # Load credentials
        try:
            with open(os.path.expanduser(self.credentials_file), "r") as f:
                creds_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        # Check if provider exists
        if provider.value not in creds_data:
            return False

        # Find and remove the credential
        encoded_token = self._encode_token(token)
        provider_creds = creds_data[provider.value]
        original_length = len(provider_creds)

        creds_data[provider.value] = [
            cred for cred in provider_creds if cred.get("token") != encoded_token
        ]

        # Check if anything was removed
        if len(creds_data[provider.value]) == original_length:
            return False

        # Save updated credentials
        with open(os.path.expanduser(self.credentials_file), "w") as f:
            json.dump(creds_data, f, indent=2)

        # Clear cache
        self._creds_cache = {}
        return True

    def clear_credentials(self, provider: Optional[ProviderType] = None) -> None:
        """Clear all credentials or just for a specific provider.

        Args:
            provider: Optional provider to clear credentials for. If None, clears all.
        """
        try:
            with open(os.path.expanduser(self.credentials_file), "r") as f:
                creds_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        if provider:
            # Clear just this provider
            if provider.value in creds_data:
                creds_data[provider.value] = []
        else:
            # Clear all providers
            creds_data = {}

        # Save updated credentials
        with open(os.path.expanduser(self.credentials_file), "w") as f:
            json.dump(creds_data, f, indent=2)

        # Clear cache
        self._creds_cache = {}
