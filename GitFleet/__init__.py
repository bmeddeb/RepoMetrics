"""
GitFleet - High-performance Git repository analysis and API clients

This module provides Python bindings for Git repository analysis and API
clients for various Git hosting providers (GitHub, GitLab, BitBucket).
"""

# Import core repository management classes
from GitFleet import (
    RepoManager,
    CloneStatus,
    CloneTask,
    GitHubClient,
)

# Re-export providers package for nicer imports
from . import providers

__all__ = [
    # Core repository management
    "RepoManager",
    "CloneStatus",
    "CloneTask",
    
    # Provider clients
    "GitHubClient",
    "providers",
]

__version__ = "0.2.0"
