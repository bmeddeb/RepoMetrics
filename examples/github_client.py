#!/usr/bin/env python3
"""
GitHub API Client Example

This example demonstrates how to use the GitFleet GitHub API client to:
1. Fetch repositories for a user
2. Get repository details
3. List contributors and branches
4. Check rate limits
"""

import os
import asyncio
from pprint import pprint
from GitFleet import GitHubClient


async def main():
    # Initialize the GitHub client with a token
    # You can get a token from https://github.com/settings/tokens
    github_token = os.environ.get("GITHUB_TOKEN", "")
    
    if not github_token:
        print("⚠️ GitHub token not found in environment variables.")
        print("Set the GITHUB_TOKEN environment variable to use this example.")
        print("You can create a token at: https://github.com/settings/tokens")
        return
    
    # Create the GitHub client
    github = GitHubClient(token=github_token)
    
    # Print the authenticated user info
    print("\n🧑‍💻 Authenticated User Information:")
    user_info = await github.fetch_user_info()
    pprint(user_info)
    
    # Check rate limits
    print("\n📊 API Rate Limits:")
    rate_limits = await github.get_rate_limit()
    pprint(rate_limits)
    
    # Get repositories for a specific user
    username = "octocat"  # Example GitHub user
    print(f"\n📚 Repositories for {username}:")
    repos = await github.fetch_repositories(username)
    
    # Print basic info about each repository
    for i, repo in enumerate(repos[:5], 1):  # Show first 5 repos
        print(f"  {i}. {repo['full_name']} - {repo['description'] or 'No description'}")
        print(f"     ↳ {repo['stargazers_count']} stars, {repo['forks_count']} forks, {repo['language'] or 'No language'}")
    
    if len(repos) > 5:
        print(f"  ... and {len(repos) - 5} more repositories")
    
    # Get detailed information about a specific repository
    if repos:
        repo = repos[0]
        owner, repo_name = repo["full_name"].split("/")
        
        print(f"\n📖 Details for {repo['full_name']}:")
        repo_details = await github.fetch_repository_details(owner, repo_name)
        print(f"  Description: {repo_details['description'] or 'None'}")
        print(f"  Topics: {', '.join(repo_details['topics']) or 'None'}")
        print(f"  License: {repo_details['license'] or 'None'}")
        print(f"  Created: {repo_details['created_at']}")
        print(f"  Last updated: {repo_details['updated_at']}")
        
        # Get contributors
        print(f"\n👥 Top Contributors:")
        contributors = await github.fetch_contributors(owner, repo_name)
        for i, contributor in enumerate(contributors[:5], 1):  # Show top 5
            print(f"  {i}. {contributor['login']} - {contributor['contributions']} contributions")
        
        if len(contributors) > 5:
            print(f"  ... and {len(contributors) - 5} more contributors")
        
        # Get branches
        print(f"\n🌿 Branches:")
        branches = await github.fetch_branches(owner, repo_name)
        for i, branch in enumerate(branches[:5], 1):  # Show first 5
            protected = "🔒 Protected" if branch["protected"] else "🔓 Not protected"
            print(f"  {i}. {branch['name']} - {protected}")
        
        if len(branches) > 5:
            print(f"  ... and {len(branches) - 5} more branches")
    
    # Use the to_pandas method to convert data to pandas DataFrame
    try:
        print("\n📊 Converting repositories to pandas DataFrame:")
        import pandas as pd
        repos_df = await github.to_pandas(repos)
        print(f"  DataFrame shape: {repos_df.shape}")
        print("  Columns:", ", ".join(repos_df.columns[:10]) + "...")
    except ImportError:
        print("  pandas not installed. Install with: pip install pandas")


if __name__ == "__main__":
    # Set up the event loop and run the main async function
    asyncio.run(main())