# GitHub API Client

The GitFleet GitHub API client provides a convenient interface to interact with the GitHub API. This client allows you to fetch repository information, user data, and other GitHub-specific resources.

## Installation

The GitHub client is included with GitFleet. No additional installation is required.

```python
from GitFleet import GitHubClient
```

## Authentication

Initialize the client with your GitHub personal access token:

```python
github = GitHubClient(token="your-github-token")
```

You can create a token on GitHub at [https://github.com/settings/tokens](https://github.com/settings/tokens).

For GitHub Enterprise, you can specify a custom base URL:

```python
github = GitHubClient(
    token="your-github-token",
    base_url="https://github.your-company.com/api/v3"
)
```

## Basic Usage

### Fetch Repositories

Retrieve repositories for a user or organization:

```python
# Get repositories for a user
repos = await github.fetch_repositories("octocat")

# Print repository names
for repo in repos:
    print(f"{repo['full_name']} - {repo['description']}")
```

### User Information

Get information about the authenticated user:

```python
user_info = await github.fetch_user_info()
print(f"Authenticated as: {user_info['login']}")
print(f"Name: {user_info['name']}")
print(f"Email: {user_info['email']}")
```

### Repository Details

Fetch detailed information about a specific repository:

```python
repo_details = await github.fetch_repository_details("octocat", "hello-world")
print(f"Description: {repo_details['description']}")
print(f"Topics: {repo_details['topics']}")
print(f"License: {repo_details['license']}")
```

### Contributors and Branches

Get contributors for a repository:

```python
contributors = await github.fetch_contributors("octocat", "hello-world")
for contributor in contributors:
    print(f"{contributor['login']} - {contributor['contributions']} contributions")
```

Get branches for a repository:

```python
branches = await github.fetch_branches("octocat", "hello-world")
for branch in branches:
    print(f"{branch['name']} - {'Protected' if branch['protected'] else 'Not protected'}")
```

### Rate Limits

Check your current rate limit status:

```python
rate_limit = await github.get_rate_limit()
print(f"API calls remaining: {rate_limit['remaining']}/{rate_limit['limit']}")
print(f"Reset time: {rate_limit['reset_time']}")
```

## Error Handling

The GitHub client raises specific exceptions for different error cases:

```python
from GitFleet.providers.base import ProviderError, AuthError, RateLimitError

try:
    repos = await github.fetch_repositories("octocat")
except AuthError as e:
    print(f"Authentication error: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Resets at: {e.reset_time}")
except ProviderError as e:
    print(f"GitHub API error: {e}")
```

## Data Analysis with Pandas

Convert API response data to pandas DataFrames for analysis:

```python
# Fetch repositories and convert to DataFrame
repos = await github.fetch_repositories("octocat")
df = await github.to_pandas(repos)

# Analyze the data
print(f"Most popular repositories (by stars):")
popular_repos = df.sort_values("stargazers_count", ascending=False)
print(popular_repos[["name", "stargazers_count", "forks_count"]].head())

# Language distribution
print("\nLanguage distribution:")
print(df["language"].value_counts())
```

## Pagination

The GitHub client automatically handles pagination. You don't need to worry about pagination limits as the client will fetch all available results.