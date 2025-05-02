"""
Common data models shared across different Git providers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderType(str, Enum):
    """Enumeration of supported Git provider types."""

    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


@dataclass
class UserInfo:
    """User information from a Git provider."""

    id: str
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class RepoInfo:
    """Repository information from a Git provider."""

    name: str
    full_name: str
    clone_url: str
    description: Optional[str] = None
    default_branch: str = "main"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    language: Optional[str] = None
    fork: bool = False
    forks_count: int = 0
    stargazers_count: Optional[int] = None
    provider_type: ProviderType = ProviderType.GITHUB
    visibility: str = "public"
    owner: Optional[UserInfo] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class RateLimitInfo:
    """Rate limit information from a Git provider."""

    limit: int
    remaining: int
    reset_time: int
    used: int
    provider_type: ProviderType = ProviderType.GITHUB


@dataclass
class BranchInfo:
    """Branch information from a Git provider."""

    name: str
    commit_sha: str
    protected: bool = False
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class ContributorInfo:
    """Contributor information from a Git provider."""

    id: str
    login: str
    contributions: int
    avatar_url: Optional[str] = None
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None
