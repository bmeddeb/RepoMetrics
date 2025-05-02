"""
GitHub API client implementation.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

import httpx

from GitFleet.models.common import (BranchInfo, ContributorInfo, RateLimitInfo,
                                    RepoInfo, UserInfo)

from .base import GitProviderClient, ProviderType
from .token_manager import TokenInfo, TokenManager

T = TypeVar("T")


class GitHubError(Exception):
    """Base exception for GitHub API errors."""

    pass


class AuthError(GitHubError):
    """Exception raised for authentication errors."""

    pass


class RateLimitError(GitHubError):
    """Exception raised when rate limits are exceeded."""

    def __init__(self, message: str, reset_time: int):
        self.reset_time = reset_time
        super().__init__(message)


class GitHubClient(GitProviderClient):
    """GitHub API client implementation."""

    def __init__(
        self,
        token: str,
        base_url: Optional[str] = None,
        token_manager: Optional[TokenManager] = None,
    ):
        """Initialize the GitHub client.

        Args:
            token: GitHub personal access token
            base_url: Optional custom base URL for GitHub Enterprise
            token_manager: Optional token manager for rate limit handling
        """
        super().__init__(ProviderType.GITHUB)
        self.token = token
        self.base_url = base_url or "https://api.github.com"

        # Setup token management
        self.token_manager = token_manager
        if token_manager:
            token_manager.add_token(token, ProviderType.GITHUB)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an authenticated request to the GitHub API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Get a token from the manager if available, otherwise use the default
        token_to_use = self.token
        token_info = None
        if self.token_manager:
            token_info = await self.token_manager.get_next_available_token(
                ProviderType.GITHUB
            )
            if token_info:
                token_to_use = token_info.token

        headers = {
            "Authorization": f"token {token_to_use}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitFleet-Client",
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method, url=url, headers=headers, **kwargs
            )

            # Update rate limit info if token manager is available
            if self.token_manager and token_info:
                remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                await self.token_manager.update_rate_limit(
                    token_to_use, ProviderType.GITHUB, remaining, reset_time
                )

            # Handle rate limiting
            if (
                response.status_code == 403
                and "X-RateLimit-Remaining" in response.headers
            ):
                if int(response.headers["X-RateLimit-Remaining"]) == 0:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    raise RateLimitError(
                        f"Rate limit exceeded. Resets at {reset_time}", reset_time
                    )

            # Handle authentication errors
            if response.status_code == 401:
                if self.token_manager and token_info:
                    await self.token_manager.mark_token_invalid(
                        token_to_use, ProviderType.GITHUB
                    )
                raise AuthError("Invalid GitHub token")

            # Raise for other error status codes
            response.raise_for_status()

            return response.json()

    def _convert_to_model(self, data: Dict[str, Any], model_class: Type[T]) -> T:
        """Convert API response data to a model instance."""
        # For RepoInfo, we need to handle the owner nested object
        if model_class == RepoInfo and "owner" in data and data["owner"]:
            owner_data = data["owner"]
            owner = UserInfo(
                id=str(owner_data.get("id", "")),
                login=owner_data.get("login", ""),
                name=owner_data.get("name"),
                email=owner_data.get("email"),
                avatar_url=owner_data.get("avatar_url"),
                provider_type=ProviderType.GITHUB,
                raw_data=owner_data,
            )

            # Create the RepoInfo instance with owner
            return cast(
                T,
                RepoInfo(
                    name=data["name"],
                    full_name=data["full_name"],
                    clone_url=data["clone_url"],
                    description=data.get("description"),
                    default_branch=data.get("default_branch", "main"),
                    created_at=data.get("created_at"),
                    updated_at=data.get("updated_at"),
                    language=data.get("language"),
                    fork=data.get("fork", False),
                    forks_count=data.get("forks_count", 0),
                    stargazers_count=data.get("stargazers_count"),
                    visibility=data.get("visibility", "public"),
                    provider_type=ProviderType.GITHUB,
                    owner=owner,
                    raw_data=data,
                ),
            )

        # For UserInfo
        elif model_class == UserInfo:
            return cast(
                T,
                UserInfo(
                    id=str(data.get("id", "")),
                    login=data["login"],
                    name=data.get("name"),
                    email=data.get("email"),
                    avatar_url=data.get("avatar_url"),
                    provider_type=ProviderType.GITHUB,
                    raw_data=data,
                ),
            )

        # For RateLimitInfo
        elif model_class == RateLimitInfo:
            return cast(
                T,
                RateLimitInfo(
                    limit=data["limit"],
                    remaining=data["remaining"],
                    reset_time=data["reset"],
                    used=data["used"],
                    provider_type=ProviderType.GITHUB,
                ),
            )

        # For BranchInfo
        elif model_class == BranchInfo:
            return cast(
                T,
                BranchInfo(
                    name=data["name"],
                    commit_sha=data["commit"]["sha"],
                    protected=data.get("protected", False),
                    provider_type=ProviderType.GITHUB,
                    raw_data=data,
                ),
            )

        # For ContributorInfo
        elif model_class == ContributorInfo:
            return cast(
                T,
                ContributorInfo(
                    id=str(data.get("id", "")),
                    login=data["login"],
                    contributions=data["contributions"],
                    avatar_url=data.get("avatar_url"),
                    provider_type=ProviderType.GITHUB,
                    raw_data=data,
                ),
            )

        raise ValueError(f"Unsupported model class: {model_class}")

    async def fetch_repositories(self, owner: str) -> List[RepoInfo]:
        """Fetch repositories for a user or organization."""
        data = await self._request("GET", f"/users/{owner}/repos?per_page=100")
        return [self._convert_to_model(repo, RepoInfo) for repo in data]

    async def fetch_user_info(self) -> UserInfo:
        """Fetch information about the authenticated user."""
        data = await self._request("GET", "/user")
        return self._convert_to_model(data, UserInfo)

    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit information."""
        response = await self._request("GET", "/rate_limit")
        return self._convert_to_model(response["resources"]["core"], RateLimitInfo)

    async def fetch_repository_details(self, owner: str, repo: str) -> RepoInfo:
        """Fetch detailed information about a specific repository."""
        data = await self._request("GET", f"/repos/{owner}/{repo}")
        return self._convert_to_model(data, RepoInfo)

    async def fetch_contributors(self, owner: str, repo: str) -> List[ContributorInfo]:
        """Fetch contributors for a repository."""
        data = await self._request("GET", f"/repos/{owner}/{repo}/contributors")
        return [
            self._convert_to_model(contributor, ContributorInfo) for contributor in data
        ]

    async def fetch_branches(self, owner: str, repo: str) -> List[BranchInfo]:
        """Fetch branches for a repository."""
        data = await self._request("GET", f"/repos/{owner}/{repo}/branches")
        return [self._convert_to_model(branch, BranchInfo) for branch in data]

    async def validate_credentials(self) -> bool:
        """Check if the current token is valid."""
        try:
            await self.fetch_user_info()
            return True
        except AuthError:
            return False
        except Exception:
            raise  # Re-raise other exceptions
