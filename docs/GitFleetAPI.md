# GitFleet Library Public API

This document provides a comprehensive reference for all classes, methods, and functions available to users of the GitFleet library.

## Repository Management (Rust-powered)

### RepoManager
Core class for managing Git repositories:
- `__init__(urls: List[str], github_username: str, github_token: str)` - Initialize with repository URLs and credentials
- `clone_all() -> None` - Asynchronously clone all repositories
- `fetch_clone_tasks() -> Dict[str, CloneTask]` - Get status of all clone operations
- `clone(url: str) -> None` - Clone a single repository
- `bulk_blame(repo_path: str, file_paths: List[str]) -> Dict[str, Any]` - Perform git blame on multiple files
- `extract_commits(repo_path: str) -> List[Dict[str, Any]]` - Extract commit history
- `cleanup() -> Dict[str, Union[bool, str]]` - Clean up temporary directories

### CloneTask
Represents a repository cloning task:
- Properties: `url`, `status`, `temp_dir`
- `model_dump() -> Dict[str, Any]` - Convert to dictionary
- `model_dump_json(indent: Optional[int] = None) -> str` - Convert to JSON string
- `model_validate(obj: Any) -> CloneTask` - Create from dictionary/object

### CloneStatus
Represents the status of a cloning operation:
- Properties: `status_type`, `progress`, `error`
- `model_dump() -> Dict[str, Any]` - Convert to dictionary
- `model_dump_json(indent: Optional[int] = None) -> str` - Convert to JSON string
- `model_validate(obj: Any) -> CloneStatus` - Create from dictionary/object

### CloneStatusType
Enum for clone status:
- `QUEUED` - Task is waiting to start
- `CLONING` - Task is in progress
- `COMPLETED` - Task completed successfully
- `FAILED` - Task failed

## Provider Clients

### GitHubClient
Client for GitHub API:
- `__init__(token: str, base_url: Optional[str] = None, token_manager: Optional[TokenManager] = None, use_python_impl: bool = False)`
- `fetch_repositories(owner: str) -> List[RepoInfo]` - Get repositories for owner
- `fetch_user_info() -> UserInfo` - Get authenticated user info
- `get_rate_limit() -> RateLimitInfo` - Get API rate limit info
- `fetch_repository_details(owner: str, repo: str) -> RepoDetails` - Get detailed repo info
- `fetch_contributors(owner: str, repo: str) -> List[ContributorInfo]` - Get repo contributors
- `fetch_branches(owner: str, repo: str) -> List[BranchInfo]` - Get repo branches
- `validate_credentials() -> bool` - Check if credentials are valid

### GitProviderClient
Abstract base class for Git provider clients:
- `__init__(provider_type: ProviderType)` - Initialize with provider type
- Abstract methods implemented by concrete clients (see GitHubClient)
- `to_pandas(data: Union[List[Any], Any]) -> pandas.DataFrame` - Convert data to DataFrame

### ProviderType
Enum for Git provider types:
- `GITHUB` - GitHub provider
- `GITLAB` - GitLab provider
- `BITBUCKET` - BitBucket provider

## Data Models

### UserInfo
User information from Git providers:
- Properties: `id`, `login`, `name`, `email`, `avatar_url`, `provider_type`, `raw_data`
- `model_dump() -> Dict[str, Any]` - Serialize to dict
- `model_dump_json(indent: Optional[int] = None) -> str` - Serialize to JSON
- `model_validate(obj: Any) -> UserInfo` - Create from dict/object

### RepoInfo
Basic repository information:
- Properties: `name`, `full_name`, `clone_url`, `description`, `default_branch`, `created_at`, `updated_at`, `language`, `fork`, `forks_count`, `stargazers_count`, `provider_type`, `visibility`, `owner`, `raw_data`
- `created_datetime() -> Optional[datetime]` - Parse created_at as datetime
- `updated_datetime() -> Optional[datetime]` - Parse updated_at as datetime
- `model_dump() -> Dict[str, Any]` - Serialize to dict
- `model_dump_json(indent: Optional[int] = None) -> str` - Serialize to JSON
- `model_validate(obj: Any) -> RepoInfo` - Create from dict/object

### RepoDetails
Detailed repository information (extends RepoInfo):
- Additional properties: `topics`, `license`, `homepage`, `has_wiki`, `has_issues`, `has_projects`, `archived`, `pushed_at`, `size`
- `pushed_datetime() -> Optional[datetime]` - Parse pushed_at as datetime
- All methods from RepoInfo

### RateLimitInfo
API rate limit information:
- Properties: `limit`, `remaining`, `reset_time`, `used`, `provider_type`
- `seconds_until_reset() -> int` - Get seconds until rate limit resets
- `model_dump() -> Dict[str, Any]` - Serialize to dict
- `model_dump_json(indent: Optional[int] = None) -> str` - Serialize to JSON
- `model_validate(obj: Any) -> RateLimitInfo` - Create from dict/object

### BranchInfo
Git branch information:
- Properties: `name`, `commit_sha`, `protected`, `provider_type`, `raw_data`
- `model_dump() -> Dict[str, Any]` - Serialize to dict
- `model_dump_json(indent: Optional[int] = None) -> str` - Serialize to JSON
- `model_validate(obj: Any) -> BranchInfo` - Create from dict/object

### ContributorInfo
Repository contributor information:
- Properties: `id`, `login`, `contributions`, `avatar_url`, `provider_type`, `raw_data`
- `model_dump() -> Dict[str, Any]` - Serialize to dict
- `model_dump_json(indent: Optional[int] = None) -> str` - Serialize to JSON
- `model_validate(obj: Any) -> ContributorInfo` - Create from dict/object

## Token Management

### TokenManager
Manages API tokens and rate limits:
- `__init__(max_retries: int = 3)` - Initialize with retry count
- `add_token(token: str, provider_type: ProviderType) -> None` - Add token
- `get_next_available_token(provider_type: ProviderType) -> Optional[TokenInfo]` - Get available token
- `update_rate_limit(token: str, provider_type: ProviderType, remaining: int, reset_time: int) -> None` - Update limits
- `mark_token_invalid(token: str, provider_type: ProviderType) -> None` - Mark token as invalid
- `get_all_tokens(provider_type: Optional[ProviderType] = None) -> List[TokenInfo]` - Get all tokens

### TokenInfo
Information about an API token:
- Properties: `token`, `provider_type`, `remaining`, `reset_time`, `status`
- `secret_token` - Property that returns token as SecretStr for secure handling

## Authentication and Security

### CredentialManager
Manages and securely stores credentials:
- `__init__(encryption_key: Optional[str] = None, use_encryption: bool = True)` - Initialize
- `add_credential(provider_type: ProviderType, token: str, username: Optional[str] = None, email: Optional[str] = None) -> None` - Add credential
- `get_credential(provider_type: ProviderType) -> Optional[CredentialEntry]` - Get credential
- `list_credentials() -> List[CredentialEntry]` - List all credentials
- `remove_credential(provider_type: ProviderType) -> bool` - Remove credential
- `save_to_file(file_path: str) -> None` - Save credentials to file
- `load_from_file(file_path: str) -> None` - Load credentials from file
- `clear_all() -> None` - Clear all credentials

## Utility Functions

### Data Conversion

- `to_dataframe(data: Union[List[Dict[str, Any]], Dict[str, Any], List[Any], BaseModel, List[BaseModel]]) -> pandas.DataFrame` - Convert to pandas DataFrame
- `flatten_dataframe(df: pandas.DataFrame, separator: str = "_") -> pandas.DataFrame` - Flatten nested DataFrame columns
- `to_json(obj: Any, indent: Optional[int] = None) -> str` - Convert object to JSON string
- `to_dict(obj: Any) -> Dict[str, Any]` - Convert object to dictionary

### Rate Limiting

- `RateLimiter` - Class for rate limiting API calls
  - `__init__(requests_per_second: float)` - Initialize with rate limit
  - `acquire() -> None` - Acquire a token (blocks if rate exceeded)
  - `try_acquire() -> bool` - Try to acquire a token (non-blocking)

### Rust Type Conversion

- `clone_status_to_pydantic(rust_status: RustCloneStatus) -> CloneStatus` - Convert Rust CloneStatus to Pydantic model
- `clone_task_to_pydantic(rust_task: RustCloneTask) -> CloneTask` - Convert Rust CloneTask to Pydantic model

## Package Structure

The library is organized into several subpackages:
- `GitFleet` - Main package
- `GitFleet.models` - Data models
- `GitFleet.providers` - Git provider clients
- `GitFleet.utils` - Utility functions and classes

## Optional Features

The library has several optional features that can be installed:
- `pydantic` - Enhanced validation and serialization
- `pandas` - Data analysis and DataFrame support
- `crypto` - Secure credential encryption

Install with extras like: `pip install "gitfleet[pydantic,pandas]"`