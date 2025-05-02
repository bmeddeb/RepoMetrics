# Migration Guide

This guide helps users migrate from older versions of GitFleet to the latest version with minimal disruption.

## Migrating from v0.1.x to v0.2.x

GitFleet v0.2.0 introduces several important changes that improve the structure, type safety, and flexibility of the library.

### Key Changes

1. **Provider APIs**: Restructured provider APIs with dataclass-based models
2. **Dual Implementation**: Option to use either Rust-based or Python implementations 
3. **Token Management**: Built-in TokenManager for handling multiple tokens
4. **Error Handling**: Improved error hierarchy with provider-specific errors

### Updated Import Paths

The import structure has changed slightly to reflect the new organization:

**Old (v0.1.x):**
```python
from GitFleet import RepoManager
from GitFleet.api import GitHubAPI
```

**New (v0.2.x):**
```python
from GitFleet import RepoManager
from GitFleet import GitHubClient
```

### GitHub Client Changes

The GitHub client has been significantly enhanced with dataclasses:

**Old (v0.1.x):**
```python
from GitFleet.api import GitHubAPI

github = GitHubAPI(token="your-token")
repos = await github.get_repos("octocat")

# Dictionary-based response
for repo in repos:
    print(f"Name: {repo['name']}")
    print(f"Stars: {repo['stargazers_count']}")
```

**New (v0.2.x):**
```python
from GitFleet import GitHubClient

github = GitHubClient(token="your-token")
repos = await github.fetch_repositories("octocat")

# Dataclass-based response
for repo in repos:
    print(f"Name: {repo.name}")
    print(f"Stars: {repo.stargazers_count}")
```

### Method Naming Changes

Some method names have been updated for clarity and consistency:

| Old Method (v0.1.x) | New Method (v0.2.x) |
|---------------------|---------------------|
| `get_repos()` | `fetch_repositories()` |
| `get_user()` | `fetch_user_info()` |
| `get_rate_limit()` | `get_rate_limit()` (unchanged) |
| `get_repo_details()` | `fetch_repository_details()` |
| `get_contributors()` | `fetch_contributors()` |
| `get_branches()` | `fetch_branches()` |

### Error Handling Changes

Error classes have been reorganized into a hierarchy:

**Old (v0.1.x):**
```python
from GitFleet.api.exceptions import GitHubError, RateLimitError

try:
    repos = await github.get_repos("octocat")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except GitHubError as e:
    print(f"GitHub error: {e}")
```

**New (v0.2.x):**
```python
from GitFleet.providers.base import ProviderError, AuthError, RateLimitError

try:
    repos = await github.fetch_repositories("octocat")
except RateLimitError as e:
    print(f"Rate limited (resets at {e.reset_time}): {e}")
except AuthError as e:
    print(f"Authentication error: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
```

### TokenManager Integration

If you were manually managing tokens before, you can now use the built-in TokenManager:

**Old (v0.1.x):**
```python
from GitFleet.api import GitHubAPI

# Manual token rotation
github1 = GitHubAPI(token="token1")
github2 = GitHubAPI(token="token2")

try:
    repos = await github1.get_repos("octocat")
except RateLimitError:
    repos = await github2.get_repos("octocat")
```

**New (v0.2.x):**
```python
from GitFleet import GitHubClient
from GitFleet.providers import TokenManager, ProviderType

# Automatic token rotation
token_manager = TokenManager()
token_manager.add_token("token1", ProviderType.GITHUB)
token_manager.add_token("token2", ProviderType.GITHUB)

github = GitHubClient(token="token1", token_manager=token_manager)
repos = await github.fetch_repositories("octocat")  # Automatic token rotation
```

### To Pandas Conversion

The conversion to pandas DataFrames is now more flexible:

**Old (v0.1.x):**
```python
import pandas as pd
repos = await github.get_repos("octocat")
df = pd.DataFrame(repos)
```

**New (v0.2.x):**
```python
# Option 1: Use the utility function
from GitFleet import to_dataframe
repos = await github.fetch_repositories("octocat")
df = to_dataframe(repos)

# Option 2: Use the client method
repos = await github.fetch_repositories("octocat")
df = await github.to_pandas(repos)
```

### Forcing Python Implementation

If you encounter issues with the Rust implementation, you can force the Python implementation:

```python
# Force Python implementation
github = GitHubClient(
    token="your-token",
    use_python_impl=True
)
```

## Step-by-Step Migration

1. **Update GitFleet**: `pip install gitfleet>=0.2.0`

2. **Update imports**: Change import paths as shown above

3. **Update method calls**: Rename method calls to match the new names

4. **Update response handling**: Change dictionary access to attribute access

5. **Update error handling**: Use the new error hierarchy

6. **Consider TokenManager**: Use the built-in TokenManager for multiple tokens

7. **Test thoroughly**: Verify all functionality in a non-production environment

## Common Issues and Solutions

### Issue: AttributeError when accessing response data

**Problem**: Accessing response data as a dictionary instead of an object
```python
repo['name']  # Error
```

**Solution**: Use attribute access
```python
repo.name  # Correct
```

### Issue: ModuleNotFoundError for older imports

**Problem**: Using old import paths
```python
from GitFleet.api import GitHubAPI  # Error
```

**Solution**: Update import paths
```python
from GitFleet import GitHubClient  # Correct
```

### Issue: TokenManager not working with different providers

**Problem**: Not specifying the provider type correctly

**Solution**: Use the ProviderType enum
```python
from GitFleet.providers import ProviderType
token_manager.add_token("token", ProviderType.GITHUB)
```

## Getting Help

If you encounter issues during migration:

1. Check the [documentation](https://github.com/your-org/gitfleet/docs)
2. Open an issue on the [GitHub repository](https://github.com/your-org/gitfleet/issues)
3. Contact the maintainers at support@example.com