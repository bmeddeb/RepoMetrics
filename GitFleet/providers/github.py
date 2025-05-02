"""
GitHub API Client

This module provides a client for interacting with the GitHub API.
"""

from typing import Dict, List, Optional, Any, Union
import asyncio

from .base import (
    GitProviderClient, ProviderType, RepoInfo, UserInfo, 
    RateLimitInfo, RepoDetails, ContributorInfo, BranchInfo,
    ProviderError, RateLimitError, AuthError
)

# Import the Rust module using PyO3
from GitFleet import GitHubClient as RustGitHubClient


class GitHubClient(GitProviderClient):
    """GitHub API client for interacting with GitHub repositories and users.
    
    This client provides methods for fetching repositories, user information,
    and other GitHub-specific data.
    
    Args:
        token: GitHub personal access token
        base_url: Optional custom base URL for GitHub Enterprise
    """
    
    def __init__(self, token: str, base_url: Optional[str] = None):
        """Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token
            base_url: Optional custom base URL for GitHub Enterprise
        """
        super().__init__(ProviderType.GITHUB)
        self._client = RustGitHubClient(token, base_url)
    
    async def fetch_repositories(self, owner: str) -> List[RepoInfo]:
        """Fetch repositories for an owner or organization.
        
        Args:
            owner: GitHub username or organization name
            
        Returns:
            List of repository information objects
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        try:
            repos = await self._client.fetch_repositories(owner)
            return repos
        except Exception as e:
            self._handle_error(e)
    
    async def fetch_user_info(self) -> UserInfo:
        """Fetch information about the authenticated user.
        
        Returns:
            User information for the authenticated user
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        try:
            user_info = await self._client.fetch_user_info()
            return user_info
        except Exception as e:
            self._handle_error(e)
    
    async def get_rate_limit(self) -> RateLimitInfo:
        """Get current rate limit information.
        
        Returns:
            Current rate limit status
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
        """
        try:
            rate_limit = await self._client.get_rate_limit()
            return rate_limit
        except Exception as e:
            self._handle_error(e)
    
    async def fetch_repository_details(self, owner: str, repo: str) -> RepoDetails:
        """Fetch detailed information about a specific repository.
        
        Args:
            owner: GitHub username or organization name
            repo: Repository name
            
        Returns:
            Detailed repository information
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        try:
            repo_details = await self._client.fetch_repository_details(owner, repo)
            return repo_details
        except Exception as e:
            self._handle_error(e)
    
    async def fetch_contributors(self, owner: str, repo: str) -> List[ContributorInfo]:
        """Fetch contributors for a repository.
        
        Args:
            owner: GitHub username or organization name
            repo: Repository name
            
        Returns:
            List of contributor information
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        try:
            contributors = await self._client.fetch_contributors(owner, repo)
            return contributors
        except Exception as e:
            self._handle_error(e)
    
    async def fetch_branches(self, owner: str, repo: str) -> List[BranchInfo]:
        """Fetch branches for a repository.
        
        Args:
            owner: GitHub username or organization name
            repo: Repository name
            
        Returns:
            List of branch information
            
        Raises:
            ProviderError: If the API request fails
            AuthError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        try:
            branches = await self._client.fetch_branches(owner, repo)
            return branches
        except Exception as e:
            self._handle_error(e)
    
    async def validate_credentials(self) -> bool:
        """Check if the current token is valid.
        
        Returns:
            True if credentials are valid, False otherwise
            
        Raises:
            ProviderError: If the validation check fails for reasons other than auth
        """
        try:
            is_valid = await self._client.validate_credentials()
            return is_valid
        except Exception as e:
            self._handle_error(e)
    
    def _handle_error(self, error: Exception) -> None:
        """Handle errors from the Rust client.
        
        Args:
            error: Exception from the Rust client
            
        Raises:
            Appropriate Python exception based on the error type
        """
        error_message = str(error)
        
        if "Authentication error" in error_message:
            raise AuthError(error_message, self.provider_type)
        elif "Rate limit exceeded" in error_message:
            # Extract reset time from error message if available
            import re
            reset_match = re.search(r"resets at timestamp: (\d+)", error_message)
            reset_time = int(reset_match.group(1)) if reset_match else 0
            raise RateLimitError(error_message, self.provider_type, reset_time)
        elif "Resource not found" in error_message:
            raise ProviderError(error_message, self.provider_type)
        else:
            raise ProviderError(error_message, self.provider_type)