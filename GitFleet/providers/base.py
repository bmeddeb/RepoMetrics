"""
Base Git Provider Client

This module provides the base class for all Git provider API clients.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import asyncio
from dataclasses import dataclass


class ProviderType(str, Enum):
    """Enumeration of supported Git provider types."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"

@dataclass
class RepoInfo:
    """Common repository information structure."""
    name: str
    full_name: str
    clone_url: str
    description: Optional[str]
    default_branch: str
    created_at: str
    updated_at: str
    language: Optional[str]
    fork: bool
    forks_count: int
    stargazers_count: Optional[int]
    provider_type: ProviderType
    visibility: str
    owner: Dict[str, Any]
    # Store raw provider data for advanced use cases
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class UserInfo:
    """User information structure."""
    id: str
    login: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    provider_type: ProviderType
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class RateLimitInfo:
    """Rate limit information structure."""
    limit: int
    remaining: int
    reset_time: int
    used: int
    provider_type: ProviderType


@dataclass
class RepoDetails(RepoInfo):
    """Detailed repository information structure."""
    topics: List[str]
    license: Optional[str]
    homepage: Optional[str]
    has_wiki: bool
    has_issues: bool
    has_projects: bool
    archived: bool
    pushed_at: Optional[str]
    size: int


@dataclass
class ContributorInfo:
    """Contributor information structure."""
    login: str
    id: str
    avatar_url: Optional[str]
    contributions: int
    provider_type: ProviderType


@dataclass
class BranchInfo:
    """Branch information structure."""
    name: str
    commit_sha: str
    protected: bool
    provider_type: ProviderType


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    
    def __init__(self, message: str, provider_type: ProviderType):
        self.message = message
        self.provider_type = provider_type
        super().__init__(f"{provider_type.value}: {message}")


class RateLimitError(ProviderError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str, provider_type: ProviderType, reset_time: int):
        self.reset_time = reset_time
        super().__init__(
            f"{message} (resets at {reset_time})", provider_type
        )


class AuthError(ProviderError):
    """Exception raised for authentication failures."""
    pass


class GitProviderClient(ABC):
    """Base class for Git provider API clients.
    
    This abstract class defines the common interface that all provider-specific
    clients should implement.
    """
    
    def __init__(self, provider_type: ProviderType):
        """Initialize the base provider client.
        
        Args:
            provider_type: The type of Git provider this client handles
        """
        self.provider_type = provider_type
    
    @abstractmethod
    async def fetch_repositories(self, owner: str) -> List[RepoInfo]:
        """Fetch repositories for an owner/organization.
        
        Args:
            owner: Username or organization name
            
        Returns:
            List of repository information objects
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        pass
    
    @abstractmethod
    async def fetch_user_info(self) -> UserInfo:
        """Fetch information about the authenticated user.
        
        Returns:
            User information for the authenticated user
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        pass
    
    @abstractmethod
    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit information.
        
        Returns:
            Current rate limit status
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
        """
        pass
    
    @abstractmethod
    async def fetch_repository_details(self, owner: str, repo: str) -> RepoDetails:
        """Fetch detailed information about a specific repository.
        
        Args:
            owner: Username or organization name
            repo: Repository name
            
        Returns:
            Detailed repository information
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        pass
    
    @abstractmethod
    async def fetch_contributors(self, owner: str, repo: str) -> List[ContributorInfo]:
        """Fetch contributors for a repository.
        
        Args:
            owner: Username or organization name
            repo: Repository name
            
        Returns:
            List of contributor information
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        pass
    
    @abstractmethod
    async def fetch_branches(self, owner: str, repo: str) -> List[BranchInfo]:
        """Fetch branches for a repository.
        
        Args:
            owner: Username or organization name
            repo: Repository name
            
        Returns:
            List of branch information
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Check if the current token/credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
            
        Raises:
            ProviderError: If the validation check fails for reasons other than auth
        """
        pass
    
    async def to_pandas(self, data: Union[List[Any], Any]) -> "pandas.DataFrame":
        """Convert provider data to pandas DataFrame.
        
        This is a helper method for data analysis that converts API response data
        to a pandas DataFrame. If pandas is not installed, raises an ImportError.
        
        Args:
            data: API response data (list of objects or single object)
            
        Returns:
            pandas DataFrame with the data
            
        Raises:
            ImportError: If pandas is not installed
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this functionality. "
                "Install it with 'pip install pandas'."
            )
        
        # Convert single object to list
        if not isinstance(data, list):
            data = [data]
        
        # Handle empty list
        if not data:
            return pd.DataFrame()
        
        # Convert dataclasses to dicts if needed
        import dataclasses
        if dataclasses.is_dataclass(data[0]):
            data = [dataclasses.asdict(item) for item in data]
        
        return pd.DataFrame(data)
