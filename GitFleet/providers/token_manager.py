"""
Token management system for Git provider API clients with rate limit awareness.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from .base import ProviderType


@dataclass
class TokenStatus:
    """Represents the status of an API token."""

    is_valid: bool
    remaining_calls: int
    reset_time: Optional[int] = None
    last_used: Optional[float] = None

    @property
    def is_rate_limited(self) -> bool:
        """Check if the token is currently rate limited."""
        if self.remaining_calls <= 0 and self.reset_time:
            return time.time() < self.reset_time
        return False

    @property
    def is_available(self) -> bool:
        """Check if the token is available for use."""
        return self.is_valid and not self.is_rate_limited


@dataclass
class TokenInfo:
    """Information about an API token."""

    token: str
    provider: ProviderType
    username: Optional[str] = None
    status: Optional[TokenStatus] = None

    def __post_init__(self):
        if self.status is None:
            self.status = TokenStatus(
                is_valid=True,
                remaining_calls=5000,  # Default assumption
                reset_time=None,
                last_used=time.time(),
            )


class TokenManager:
    """Manages multiple API tokens with rate limit awareness."""

    def __init__(self):
        self.tokens: Dict[ProviderType, List[TokenInfo]] = {
            provider: [] for provider in ProviderType
        }
        self.current_indices: Dict[ProviderType, int] = {
            provider: 0 for provider in ProviderType
        }
        self._lock = asyncio.Lock()

    def add_token(
        self, token: str, provider: ProviderType, username: Optional[str] = None
    ) -> None:
        """Add a token to the manager."""
        token_info = TokenInfo(token=token, provider=provider, username=username)
        self.tokens[provider].append(token_info)

    async def get_next_available_token(
        self, provider: ProviderType
    ) -> Optional[TokenInfo]:
        """Get the next available token using round-robin with rate limit awareness."""
        async with self._lock:
            provider_tokens = self.tokens[provider]

            if not provider_tokens:
                return None

            # Start from the current index and look for an available token
            current_index = self.current_indices[provider]
            for i in range(len(provider_tokens)):
                idx = (current_index + i) % len(provider_tokens)
                token = provider_tokens[idx]

                if token.status.is_available:
                    # Update index for next time
                    self.current_indices[provider] = (idx + 1) % len(provider_tokens)
                    # Mark as used
                    token.status.last_used = time.time()
                    return token

            # No available token found
            return None

    async def update_rate_limit(
        self, token: str, provider: ProviderType, remaining: int, reset_time: int
    ) -> None:
        """Update rate limit information for a token."""
        async with self._lock:
            for token_info in self.tokens[provider]:
                if token_info.token == token:
                    token_info.status.remaining_calls = remaining
                    token_info.status.reset_time = reset_time
                    break

    async def mark_token_invalid(self, token: str, provider: ProviderType) -> None:
        """Mark a token as invalid (e.g., revoked or unauthorized)."""
        async with self._lock:
            for token_info in self.tokens[provider]:
                if token_info.token == token:
                    token_info.status.is_valid = False
                    break
