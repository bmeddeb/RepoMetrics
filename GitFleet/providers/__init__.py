"""
GitFleet Provider API Clients

This package contains API clients for various Git hosting providers:
- GitHub
- GitLab
- BitBucket

These clients allow you to interact with repository information, 
user data, and other provider-specific features.
"""

from .github import GitHubClient
# These imports will be uncommented as we implement them
# from .gitlab import GitLabClient
# from .bitbucket import BitBucketClient
from .base import GitProviderClient, ProviderType

__all__ = [
    "GitHubClient",
    # Will be uncommented as we implement them
    # "GitLabClient", 
    # "BitBucketClient",
    "GitProviderClient",
    "ProviderType",
]