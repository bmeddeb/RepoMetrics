# Pydantic Implementation Plan for GitFleet

This document outlines the specific steps to integrate Pydantic into the GitFleet codebase for improved data validation, serialization, and documentation.

## 1. Dependencies Update

### 1.1 Update `pyproject.toml`

```toml
[project]
# ...existing dependencies...
dependencies = [
    # ...existing dependencies...
    "pydantic>=2.11.0",  # Latest version for improved performance & features
]

[project.optional-dependencies]
# ...existing optional dependencies...
all = [
    # ...existing dependencies...
    "pydantic>=2.11.0",
]
```

## 2. Data Models Migration

### 2.1 Convert Common Models (`GitFleet/models/common.py`)

Replace current dataclasses with Pydantic models:

```python
"""
Common data models shared across different Git providers.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, AnyHttpUrl, ConfigDict


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
    clone_url: str  # Could use AnyHttpUrl for validation, but some APIs may return Git URLs
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
    
    # Method for converting date strings to datetime objects
    def created_datetime(self) -> Optional[datetime]:
        """Convert created_at string to datetime object."""
        if not self.created_at:
            return None
        try:
            return datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
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
    
    # Helper method for time until reset
    def seconds_until_reset(self) -> int:
        """Get seconds until rate limit resets."""
        now = int(datetime.now().timestamp())
        return max(0, self.reset_time - now)


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
```

### 2.2 Use Pydantic.dataclasses for Token Management (`GitFleet/providers/token_manager.py`)

```python
"""
Token management system for Git provider API clients with rate limit awareness.
"""

import time
import asyncio
from typing import Dict, List, Optional, Union, Tuple

from pydantic import Field
from pydantic.dataclasses import dataclass

from .base import ProviderType


@dataclass(frozen=False)  # Need to update fields like remaining_calls
class TokenStatus:
    """Represents the status of an API token."""
    is_valid: bool
    remaining_calls: int
    reset_time: Optional[int] = None
    last_used: Optional[float] = Field(default_factory=lambda: time.time())
    
    @property
    def is_rate_limited(self) -> bool:
        """Check if the token is currently rate limited."""
        if self.remaining_calls <= 0 and self.reset_time:
            return time.time() < self.reset_time
        return False
    
    @property
    def is_available(self) -> bool:
        """Check if the token is available for use."""
        return self.is_valid and not self.is_rate_limited


@dataclass(frozen=False)  # Need mutable status field
class TokenInfo:
    """Information about an API token."""
    token: str
    provider: ProviderType
    username: Optional[str] = None
    status: Optional[TokenStatus] = None
    
    def __post_init__(self):
        if self.status is None:
            self.status = TokenStatus(
                is_valid=True, 
                remaining_calls=5000,  # Default assumption
                reset_time=None,
                last_used=time.time()
            )

# Rest of the TokenManager class remains largely the same
# ...
```

### 2.3 Add Secure Token Handling in Credential Manager (`GitFleet/utils/auth.py`)

```python
from pydantic import SecretStr
from pydantic.dataclasses import dataclass

@dataclass
class CredentialEntry:
    """Represents a stored credential for a Git provider."""
    provider: ProviderType
    token: SecretStr  # Securely handles sensitive information
    username: Optional[str] = None
    host: Optional[str] = None
    
    def get_token(self) -> str:
        """Get the raw token string."""
        return self.token.get_secret_value()
```

## 3. API Client Implementation Updates

### 3.1 GitHub Client Update (`GitFleet/providers/github.py`)

```python
"""
GitHub API client implementation.
"""

import time
import httpx
from typing import Dict, List, Any, Optional, Union, TypeVar, Type, cast
from datetime import datetime

from GitFleet.providers.base import GitProviderClient, ProviderType
from GitFleet.providers.token_manager import TokenManager, TokenInfo
from GitFleet.models.common import UserInfo, RepoInfo, RateLimitInfo, BranchInfo, ContributorInfo

# Rest of imports...

class GitHubClient(GitProviderClient):
    # ... existing initialization ...
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        # ... existing implementation ...
        
        # Same request logic, but with validation on return
        return response.json()
    
    # Replace conversion methods with Pydantic model construction
    async def fetch_repositories(self, owner: str) -> List[RepoInfo]:
        """Fetch repositories for a user or organization."""
        data = await self._request("GET", f"/users/{owner}/repos?per_page=100")
        return [RepoInfo.model_validate(repo, from_attributes=True) for repo in data]
    
    async def fetch_user_info(self) -> UserInfo:
        """Fetch information about the authenticated user."""
        data = await self._request("GET", "/user")
        return UserInfo.model_validate(data, from_attributes=True)
    
    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit information."""
        response = await self._request("GET", "/rate_limit")
        return RateLimitInfo.model_validate(response["resources"]["core"], from_attributes=True)
    
    async def fetch_repository_details(self, owner: str, repo: str) -> RepoInfo:
        """Fetch detailed information about a specific repository."""
        data = await self._request("GET", f"/repos/{owner}/{repo}")
        return RepoInfo.model_validate(data, from_attributes=True)
    
    async def fetch_contributors(self, owner: str, repo: str) -> List[ContributorInfo]:
        """Fetch contributors for a repository."""
        data = await self._request("GET", f"/repos/{owner}/{repo}/contributors")
        return [ContributorInfo.model_validate(contributor, from_attributes=True) 
                for contributor in data]
    
    async def fetch_branches(self, owner: str, repo: str) -> List[BranchInfo]:
        """Fetch branches for a repository."""
        data = await self._request("GET", f"/repos/{owner}/{repo}/branches")
        return [BranchInfo.model_validate(branch, from_attributes=True) for branch in data]
    
    # ... rest of class implementation ...
```

## 4. Utility Functions Enhancement

### 4.1 Data Conversion Utilities (`GitFleet/utils/converters.py`)

```python
"""
Data conversion utilities for working with provider API data.
"""

from typing import List, Dict, Any, Union, Optional, TypeVar, Type
import datetime
import json
from pydantic import BaseModel

T = TypeVar('T')


def to_dict(obj: Any) -> Dict[str, Any]:
    """Convert an object to a dictionary.
    
    Handles Pydantic models, dataclasses, and primitive types.
    
    Args:
        obj: The object to convert
        
    Returns:
        Dictionary representation of the object
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    # ... rest of implementation for other types ...


def to_json(obj: Any, indent: Optional[int] = None) -> str:
    """Convert an object to a JSON string.
    
    Args:
        obj: The object to convert
        indent: Optional indentation level
        
    Returns:
        JSON string representation of the object
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump_json(indent=indent)
    # ... rest of implementation ...


def to_dataframe(data: Union[List[Dict[str, Any]], Dict[str, Any], List[Any], BaseModel, List[BaseModel]]) -> 'pandas.DataFrame':
    """Convert data to a pandas DataFrame.
    
    Args:
        data: The data to convert. Can be Pydantic models or other types.
        
    Returns:
        pandas DataFrame
    
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
    
    # Handle single object case
    if not isinstance(data, list):
        if isinstance(data, BaseModel):
            data = [data.model_dump()]
        else:
            data = [data]
    else:
        # Handle list of Pydantic models
        if data and isinstance(data[0], BaseModel):
            data = [item.model_dump() for item in data]
    
    # ... rest of implementation ...
    
    return pd.DataFrame(data)

# ... rest of utility functions ...
```

## 5. Type Stubs Update

### 5.1 Common Models Stubs (`GitFleet/models/common.pyi`)

```python
"""
Type stubs for common data models.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, AnyHttpUrl, ConfigDict

class ProviderType(str, Enum):
    GITHUB: str
    GITLAB: str
    BITBUCKET: str

class UserInfo(BaseModel):
    id: str
    login: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    provider_type: ProviderType
    raw_data: Optional[Dict[str, Any]]
    
    model_config: ConfigDict
    
    def model_dump(self) -> Dict[str, Any]: ...
    def model_dump_json(self, indent: Optional[int] = None) -> str: ...
    @classmethod
    def model_validate(cls, obj: Any, from_attributes: bool = False) -> "UserInfo": ...

# ... similar updates for other models ...
```

## 6. Implementation Phases

### Phase 1: Dependencies and Core Models
1. Update pyproject.toml to include Pydantic
2. Convert models/common.py to use Pydantic models
3. Update GitHub client to use the new models
4. Update utility functions to handle Pydantic models

### Phase 2: Security and Token Management
1. Enhance CredentialEntry to use SecretStr for token storage
2. Convert TokenInfo and TokenStatus to pydantic.dataclasses
3. Update related components to work with the new models

### Phase 3: Testing and Documentation
1. Add unit tests for model validation with sample API responses
2. Update stubs and documentation
3. Update example files to demonstrate Pydantic features

## 7. Benefits and Considerations

### Benefits
- Automatic data validation for API responses
- Type safety and better error messages
- Built-in JSON schema generation for documentation
- Secure handling of sensitive data (tokens, credentials)
- Cleaner data transformation pipelines

### Performance Considerations
- Pydantic v2 is significantly faster than v1, but still has overhead compared to pure dataclasses
- Use Pydantic for input validation and API responses where correctness is priority
- For high-performance paths, consider standard dataclasses or custom optimizations

## 8. Migration Strategy

### Backward Compatibility
The implementation should maintain backward compatibility:
- Add new functionality without breaking existing code
- Use Pydantic's model_validate methods that accept both dicts and objects
- Keep consistent field names between old and new implementations

### Testing Strategy
- Test each converted module independently
- Verify validation works as expected with real-world API responses
- Test performance impact in realistic scenarios