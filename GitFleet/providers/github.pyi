"""
Type stubs for GitHub API client.
"""

import time
import httpx
from typing import Dict, List, Any, Optional, Union, TypeVar, Type, cast
from datetime import datetime

from GitFleet.providers.base import GitProviderClient, ProviderType
from GitFleet.providers.token_manager import TokenManager, TokenInfo
from GitFleet.models.common import (
    UserInfo,
    RepoInfo,
    RateLimitInfo,
    BranchInfo,
    ContributorInfo,
)

T = TypeVar("T")

class GitHubError(Exception): ...
class AuthError(GitHubError): ...

class RateLimitError(GitHubError):
    reset_time: int

    def __init__(self, message: str, reset_time: int) -> None: ...

class GitHubClient(GitProviderClient):
    token: str
    base_url: str
    token_manager: Optional[TokenManager]

    def __init__(
        self,
        token: str,
        base_url: Optional[str] = None,
        token_manager: Optional[TokenManager] = None,
    ) -> None: ...
    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any: ...
    def _convert_to_model(self, data: Dict[str, Any], model_class: Type[T]) -> T: ...
    async def fetch_repositories(self, owner: str) -> List[RepoInfo]: ...
    async def fetch_user_info(self) -> UserInfo: ...
    async def get_rate_limit(self) -> RateLimitInfo: ...
    async def fetch_repository_details(self, owner: str, repo: str) -> RepoInfo: ...
    async def fetch_contributors(
        self, owner: str, repo: str
    ) -> List[ContributorInfo]: ...
    async def fetch_branches(self, owner: str, repo: str) -> List[BranchInfo]: ...
    async def validate_credentials(self) -> bool: ...
