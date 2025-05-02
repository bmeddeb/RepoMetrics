# Git Provider API Clients

GitFleet includes API clients for various Git hosting providers that allow you to interact with repositories, users, and other provider-specific information.

## Available Providers

The following providers are currently implemented:

- [GitHub](github.md): Complete API client for GitHub with support for repositories, users, branches, and more.

Coming soon:
- GitLab: API client for GitLab (planned for v0.4.0)
- BitBucket: API client for BitBucket (planned for v0.5.0)

## Common Features

All provider clients share a common interface through the `GitProviderClient` base class, making it easy to work with different providers using the same code patterns.

Common functionality includes:

- Repository information retrieval
- User data access
- Branch and contributor details
- Rate limit handling

## Basic Usage

```python
import asyncio
from GitFleet import GitHubClient

async def main():
    # Initialize the client with your token
    github = GitHubClient(token="your-github-token")
    
    # Fetch repositories for a user
    repos = await github.fetch_repositories("octocat")
    
    # Get user information
    user_info = await github.fetch_user_info()
    
    # Check rate limits
    rate_limit = await github.get_rate_limit()
    
    print(f"Found {len(repos)} repositories")
    print(f"Authenticated as: {user_info['login']}")
    print(f"API calls remaining: {rate_limit['remaining']}/{rate_limit['limit']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Token Management

GitFleet supports token management for handling rate limits and authentication across multiple tokens:

```python
from GitFleet import GitHubClient

# Initialize clients with different tokens
github1 = GitHubClient(token="token1")
github2 = GitHubClient(token="token2")

# When one token hits rate limits, use another
try:
    repos = await github1.fetch_repositories("octocat")
except RateLimitError:
    # Fallback to another token
    repos = await github2.fetch_repositories("octocat")
```

See the [Token Management](../token-management.md) guide for more details.

## Data Analysis with Pandas

All provider clients support converting their responses to pandas DataFrames for data analysis:

```python
# Fetch repositories and convert to DataFrame
repos = await github.fetch_repositories("octocat")
df = await github.to_pandas(repos)

# Analyze the data
popular_repos = df.sort_values("stargazers_count", ascending=False)
languages = df["language"].value_counts()
```