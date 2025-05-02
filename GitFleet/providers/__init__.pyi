"""
Type stubs for Git provider API clients.
"""

from GitFleet.providers.base import GitProviderClient, ProviderType
from GitFleet.providers.github import (
    GitHubClient,
    GitHubError,
    AuthError,
    RateLimitError,
)
from GitFleet.providers.token_manager import TokenManager, TokenInfo, TokenStatus

__all__ = [
    # Base classes
    "GitProviderClient",
    "ProviderType",
    # Token management
    "TokenManager",
    "TokenInfo",
    "TokenStatus",
    # GitHub client
    "GitHubClient",
    "GitHubError",
    "AuthError",
    "RateLimitError",
]
