"""
Base classes and interfaces for Git provider API clients.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderType(str, Enum):
    """Enumeration of supported Git provider types."""

    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class GitProviderClient(ABC):
    """Base abstract class for Git provider API clients."""

    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type

    @abstractmethod
    async def fetch_repositories(self, owner: str) -> List[Dict[str, Any]]:
        """Fetch repositories for an owner/organization."""
        pass

    @abstractmethod
    async def fetch_user_info(self) -> Dict[str, Any]:
        """Fetch information about the authenticated user."""
        pass

    @abstractmethod
    async def get_rate_limit(self) -> Dict[str, Any]:
        """Get current rate limit information."""
        pass

    @abstractmethod
    async def fetch_repository_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch detailed information about a specific repository."""
        pass

    @abstractmethod
    async def fetch_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch contributors for a repository."""
        pass

    @abstractmethod
    async def fetch_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch branches for a repository."""
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Check if the current token/credentials are valid."""
        pass

    async def to_pandas(self, data):
        """Convert provider data to pandas DataFrame."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this functionality. "
                "Install it with 'pip install pandas'."
            )

        # If it's a single object, convert to list for pandas
        if not isinstance(data, list):
            data = [data]

        return pd.DataFrame(data)
