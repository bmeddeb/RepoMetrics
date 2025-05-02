"""
GitFleet - High-performance Git blame operations and repository management

This module provides Python bindings for Git repository analysis,
focusing on blame operations and commit history. It also includes
clients for interacting with Git provider APIs.
"""

# Import from the Rust module will happen when imported from outside
# to avoid circular imports
# Import provider clients
from GitFleet.providers import (GitHubClient, GitProviderClient, ProviderType,
                                TokenManager)
# Import utility functions
from GitFleet.utils import CredentialManager, RateLimiter, to_dataframe

__all__ = [
    # Core repository management
    "RepoManager",
    "CloneStatus",
    "CloneTask",
    # Provider clients
    "GitProviderClient",
    "ProviderType",
    "GitHubClient",
    "TokenManager",
    # Utilities
    "CredentialManager",
    "RateLimiter",
    "to_dataframe",
]

__version__ = "0.1.0"
