"""
GitFleet - High-performance Git repository analysis and API clients

This module provides Python bindings for Git repository analysis,
focusing on blame operations and commit history. It also includes
clients for interacting with Git hosting providers (GitHub, GitLab, BitBucket).
"""

# Import from the Rust module if available
try:
    # Import directly from the Rust extension
    try:
        from .GitFleet import (
            RepoManager,
            CloneStatus as RustCloneStatus,
            CloneTask as RustCloneTask,
        )
        # Import Pydantic models and conversion utilities
        from .models.repo import (
            CloneStatusType,
            PydanticCloneStatus,
            PydanticCloneTask,
            to_pydantic_status,
            to_pydantic_task,
            convert_clone_tasks,
        )
        RUST_AVAILABLE = True
    except ImportError:
        # Will be defined when Rust extension is built
        RUST_AVAILABLE = False
        RepoManager = None
        RustCloneStatus = None 
        RustCloneTask = None
        CloneStatusType = None
        PydanticCloneStatus = None
        PydanticCloneTask = None
        to_pydantic_status = None
        to_pydantic_task = None
        convert_clone_tasks = None
except Exception:
    # Will be defined when Rust extension is built
    RUST_AVAILABLE = False
    RepoManager = None
    RustCloneStatus = None
    RustCloneTask = None
    CloneStatusType = None
    PydanticCloneStatus = None
    PydanticCloneTask = None
    to_pydantic_status = None
    to_pydantic_task = None
    convert_clone_tasks = None

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
    "RustCloneStatus",
    "RustCloneTask",
    "CloneStatusType",
    
    # Pydantic models and conversions
    "PydanticCloneStatus",
    "PydanticCloneTask",
    "to_pydantic_status",
    "to_pydantic_task",
    "convert_clone_tasks",
    
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
]

__version__ = "0.2.8"
