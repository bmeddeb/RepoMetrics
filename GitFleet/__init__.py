"""
GitFleet - High-performance Git repository analysis and API clients

This module provides Python bindings for Git repository analysis,
focusing on blame operations and commit history. It also includes
clients for interacting with Git hosting providers (GitHub, GitLab, BitBucket).
"""

# Import from the Rust module if available
try:
    # Import from the compiled extension if available
    try:
        from .GitFleet import (
            RepoManager as RustRepoManager,
            CloneStatus as RustCloneStatus,
            CloneTask as RustCloneTask,
        )
        # Import our wrapper models that support Pydantic
        from .models.repo import (
            RepoManager,
            CloneStatus, 
            CloneTask,
            CloneStatusType,
            clone_status_to_pydantic,
            clone_task_to_pydantic
        )
    except ImportError:
        # Will be defined when Rust extension is built
        RustRepoManager = None
        RustCloneStatus = None
        RustCloneTask = None
        RepoManager = None
        CloneStatus = None 
        CloneTask = None
        CloneStatusType = None
        clone_status_to_pydantic = None
        clone_task_to_pydantic = None
except Exception:
    # Will be defined when Rust extension is built
    RustRepoManager = None
    RustCloneStatus = None
    RustCloneTask = None
    RepoManager = None
    CloneStatus = None
    CloneTask = None
    CloneStatusType = None
    clone_status_to_pydantic = None
    clone_task_to_pydantic = None

# Import provider clients
from .providers.github import GitHubClient
from .providers.base import GitProviderClient
from .models.common import ProviderType
from .providers.token_manager import TokenManager, TokenInfo

# Import data models
from .models.common import (
    RepoInfo, UserInfo, RateLimitInfo, RepoDetails,
    ContributorInfo, BranchInfo
)

# Import utility functions
from .utils.auth import CredentialManager
from .utils.rate_limit import RateLimiter
from .utils.converters import to_dataframe, to_json, to_dict, flatten_dataframe

# Re-export providers and models packages for nicer imports
from . import providers
from . import models
from . import utils

__all__ = [
    # Core repository management
    "RepoManager",
    "CloneStatus",
    "CloneTask",
    "CloneStatusType",
    
    # Provider clients
    "GitProviderClient",
    "ProviderType",
    "GitHubClient",
    "TokenManager",
    "TokenInfo",
    "providers",
    
    # Data models
    "RepoInfo",
    "UserInfo",
    "RateLimitInfo",
    "RepoDetails",
    "ContributorInfo",
    "BranchInfo",
    "models",
    
    # Utilities
    "CredentialManager",
    "RateLimiter",
    "to_dataframe",
    "to_json",
    "to_dict",
    "flatten_dataframe",
    
    # Conversion utilities for Rust types
    "clone_status_to_pydantic",
    "clone_task_to_pydantic",
]

__version__ = "0.2.2"
