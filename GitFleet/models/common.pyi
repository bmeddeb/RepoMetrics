"""
Type stubs for common data models.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProviderType(str, Enum):
    GITHUB: str = "github"
    GITLAB: str = "gitlab"
    BITBUCKET: str = "bitbucket"

@dataclass
class UserInfo:
    id: str
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class RepoInfo:
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
    limit: int
    remaining: int
    reset_time: int
    used: int
    provider_type: ProviderType = ProviderType.GITHUB

@dataclass
class BranchInfo:
    name: str
    commit_sha: str
    protected: bool = False
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class ContributorInfo:
    id: str
    login: str
    contributions: int
    avatar_url: Optional[str] = None
    provider_type: ProviderType = ProviderType.GITHUB
    raw_data: Optional[Dict[str, Any]] = None
