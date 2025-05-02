"""
Type stubs for base provider interface.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional

class ProviderType(str, Enum):
    GITHUB: str = "github"
    GITLAB: str = "gitlab"
    BITBUCKET: str = "bitbucket"

class GitProviderClient(ABC):
    provider_type: ProviderType

    def __init__(self, provider_type: ProviderType) -> None: ...
    @abstractmethod
    async def fetch_repositories(self, owner: str) -> List[Dict[str, Any]]: ...
    @abstractmethod
    async def fetch_user_info(self) -> Dict[str, Any]: ...
    @abstractmethod
    async def get_rate_limit(self) -> Dict[str, Any]: ...
    @abstractmethod
    async def fetch_repository_details(
        self, owner: str, repo: str
    ) -> Dict[str, Any]: ...
    @abstractmethod
    async def fetch_contributors(
        self, owner: str, repo: str
    ) -> List[Dict[str, Any]]: ...
    @abstractmethod
    async def fetch_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]: ...
    @abstractmethod
    async def validate_credentials(self) -> bool: ...
    async def to_pandas(self, data: Any) -> "pandas.DataFrame": ...
