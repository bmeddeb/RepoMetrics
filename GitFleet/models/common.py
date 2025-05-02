"""
Common data models shared across different Git providers.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, Field, AnyHttpUrl


class ProviderType(str, Enum):
    """Enumeration of supported Git provider types."""

    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class UserInfo(BaseModel):
    """User information from a Git provider."""

    id: str
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        frozen=True,  # Make instances immutable
        extra='ignore',  # Ignore extra fields from API responses
    )


class RepoInfo(BaseModel):
    """Repository information from a Git provider."""

    name: str
    full_name: str
    clone_url: str  # Could use AnyHttpUrl for validation, but some APIs return Git URLs
    description: Optional[str] = None
    default_branch: str = "main"
    created_at: Optional[str] = None  # Keep as string to handle various date formats
    updated_at: Optional[str] = None
    language: Optional[str] = None
    fork: bool = False
    forks_count: int = 0
    stargazers_count: Optional[int] = None
    provider_type: ProviderType = ProviderType.GITHUB
    visibility: str = "public"
    owner: Optional[UserInfo] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        frozen=True,
        extra='ignore',
    )
    
    def created_datetime(self) -> Optional[datetime]:
        """Convert created_at string to datetime object."""
        if not self.created_at:
            return None
        try:
            return datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None
    
    def updated_datetime(self) -> Optional[datetime]:
        """Convert updated_at string to datetime object."""
        if not self.updated_at:
            return None
        try:
            return datetime.fromisoformat(self.updated_at.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None


class RateLimitInfo(BaseModel):
    """Rate limit information from a Git provider."""

    limit: int
    remaining: int
    reset_time: int
    used: int
    provider_type: ProviderType = ProviderType.GITHUB
    
    model_config = ConfigDict(frozen=True)
    
    def seconds_until_reset(self) -> int:
        """Get seconds until rate limit resets."""
        now = int(datetime.now().timestamp())
        return max(0, self.reset_time - now)


class RepoDetails(RepoInfo):
    """Detailed repository information structure."""
    
    topics: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    homepage: Optional[str] = None
    has_wiki: bool = False
    has_issues: bool = False
    has_projects: bool = False
    archived: bool = False
    pushed_at: Optional[str] = None
    size: int = 0
    
    def pushed_datetime(self) -> Optional[datetime]:
        """Convert pushed_at string to datetime object."""
        if not self.pushed_at:
            return None
        try:
            return datetime.fromisoformat(self.pushed_at.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None


class BranchInfo(BaseModel):
    """Branch information from a Git provider."""

    name: str
    commit_sha: str
    protected: bool = False
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(frozen=True, extra='ignore')


class ContributorInfo(BaseModel):
    """Contributor information from a Git provider."""

    id: str
    login: str
    contributions: int
    avatar_url: Optional[str] = None
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(frozen=True, extra='ignore')
