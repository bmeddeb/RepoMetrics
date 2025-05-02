"""
Git provider API clients for GitHub, GitLab, and BitBucket.
"""

from GitFleet.providers.base import GitProviderClient, ProviderType
from GitFleet.providers.github import (AuthError, GitHubClient, GitHubError,
                                       RateLimitError)
from GitFleet.providers.token_manager import (TokenInfo, TokenManager,
                                              TokenStatus)

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
    # These will be implemented later
    # "GitLabClient",
    # "BitBucketClient",
]
