"""
Type stubs for GitFleet package.
"""

from typing import Any, Awaitable, Dict, List, Optional, Union

# Import from core Rust bindings
class CloneStatus:
    status_type: str
    progress: Optional[int]
    error: Optional[str]

class CloneTask:
    url: str
    status: CloneStatus
    temp_dir: Optional[str]

class RepoManager:
    def __init__(
        self, urls: List[str], github_username: str, github_token: str
    ) -> None: ...
    def clone_all(self) -> Awaitable[None]: ...
    def fetch_clone_tasks(self) -> Awaitable[Dict[str, CloneTask]]: ...
    def clone(self, url: str) -> Awaitable[None]: ...
    def bulk_blame(
        self, repo_path: str, file_paths: List[str]
    ) -> Awaitable[Dict[str, Union[List[Dict[str, Any]], str]]]: ...
    def extract_commits(
        self, repo_path: str
    ) -> Awaitable[Union[List[Dict[str, Any]], str]]: ...
    def cleanup(self) -> Dict[str, Union[bool, str]]: ...

# Import provider clients
from GitFleet.providers import (
    GitHubClient,
    GitProviderClient,
    ProviderType,
    TokenManager,
    TokenInfo,
    TokenStatus,
    GitHubError,
    AuthError,
    RateLimitError,
)

# Import utility functions
from GitFleet.utils import (
    CredentialManager,
    CredentialEntry,
    RateLimiter,
    rate_limited,
    to_dataframe,
    to_dict,
    to_json,
    flatten_dataframe,
)

# Import models
from GitFleet.models import (
    UserInfo,
    RepoInfo,
    RateLimitInfo,
    BranchInfo,
    ContributorInfo,
)

__version__: str
