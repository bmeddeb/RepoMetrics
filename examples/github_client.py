"""
Example of using the GitHub API client in GitFleet.

This example demonstrates how to:
1. Create a GitHub client
2. Fetch repositories for a user
3. Get detailed information about a repository
4. Convert the results to pandas DataFrames
"""

import asyncio
import os
from pprint import pprint

from GitFleet import GitHubClient, to_dataframe


async def main():
    # Get GitHub token from environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Please set the GITHUB_TOKEN environment variable")
        return

    # Create a GitHub client
    client = GitHubClient(token)

    # Validate credentials
    is_valid = await client.validate_credentials()
    if not is_valid:
        print("Invalid GitHub token")
        return

    # Get authenticated user info
    user = await client.fetch_user_info()
    print(f"Authenticated as: {user.login} ({user.name})")

    # Get repositories for a user
    username = "octocat"  # Example GitHub user
    print(f"\nFetching repositories for {username}...")
    repos = await client.fetch_repositories(username)

    # Print repository information
    print(f"Found {len(repos)} repositories:")
    for i, repo in enumerate(repos[:5], 1):  # Print just the first 5
        print(f"{i}. {repo.full_name} - {repo.description}")

    if repos:
        # Get detailed information about the first repository
        repo = repos[0]
        print(f"\nGetting details for {repo.full_name}...")
        repo_details = await client.fetch_repository_details(username, repo.name)

        # Print some detailed information
        print(f"Repository: {repo_details.full_name}")
        print(f"Description: {repo_details.description}")
        print(f"Language: {repo_details.language}")
        print(f"Stars: {repo_details.stargazers_count}")
        print(f"Forks: {repo_details.forks_count}")
        print(f"Default Branch: {repo_details.default_branch}")

        # Convert to pandas DataFrame (if pandas is installed)
        try:
            df = to_dataframe(repos)
            print("\nDataFrame of repositories:")
            print(df[["name", "full_name", "stargazers_count"]].head())
        except ImportError:
            print("\nPandas is not installed. Install with 'pip install pandas'")

    # Get rate limit information
    rate_limit = await client.get_rate_limit()
    print(f"\nRate Limit: {rate_limit.remaining}/{rate_limit.limit} remaining")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
