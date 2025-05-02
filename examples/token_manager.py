#!/usr/bin/env python3
"""
Token Manager Example

This example demonstrates how to use multiple tokens with the GitFleet library
to handle rate limiting across different API providers.
"""

import os
import asyncio
import time
from pprint import pprint
from GitFleet import GitHubClient


async def main():
    # Get GitHub tokens from environment variables
    # Format: TOKEN1,TOKEN2,TOKEN3
    github_tokens = os.environ.get("GITHUB_TOKENS", "").split(",")
    
    if not github_tokens or not github_tokens[0]:
        # Fall back to single token
        github_tokens = [os.environ.get("GITHUB_TOKEN", "")]
        if not github_tokens[0]:
            print("⚠️ No GitHub tokens found in environment variables.")
            print("Set the GITHUB_TOKENS or GITHUB_TOKEN environment variable to use this example.")
            return
    
    print(f"Using {len(github_tokens)} GitHub token(s)")
    
    # Create clients with different tokens
    github_clients = [GitHubClient(token=token) for token in github_tokens]
    
    # Check rate limits for all tokens
    print("\n📊 API Rate Limits for each token:")
    for i, client in enumerate(github_clients, 1):
        try:
            rate_limit = await client.get_rate_limit()
            print(f"Token {i}: {rate_limit['remaining']}/{rate_limit['limit']} requests remaining")
            print(f"       Resets at: {time.ctime(rate_limit['reset_time'])}")
        except Exception as e:
            print(f"Token {i}: Error - {e}")
    
    # Function to demonstrate using multiple tokens
    async def fetch_repositories_with_fallback(owners):
        print(f"\n📚 Fetching repositories for {len(owners)} users:")
        
        results = {}
        
        # Simple round-robin token use for demonstration
        for i, owner in enumerate(owners):
            client = github_clients[i % len(github_clients)]
            try:
                print(f"Using token {(i % len(github_clients)) + 1} to fetch repos for {owner}")
                repos = await client.fetch_repositories(owner)
                results[owner] = repos
                print(f"  ✅ Found {len(repos)} repositories for {owner}")
                
                # Get updated rate limit
                rate_limit = await client.get_rate_limit()
                print(f"  📊 Remaining requests: {rate_limit['remaining']}/{rate_limit['limit']}")
            except Exception as e:
                print(f"  ❌ Error fetching repos for {owner}: {e}")
                
                # Try another token if available
                if len(github_clients) > 1:
                    fallback_client = github_clients[(i + 1) % len(github_clients)]
                    try:
                        print(f"  🔄 Trying fallback token {((i + 1) % len(github_clients)) + 1}")
                        repos = await fallback_client.fetch_repositories(owner)
                        results[owner] = repos
                        print(f"  ✅ Found {len(repos)} repositories for {owner} with fallback token")
                    except Exception as e2:
                        print(f"  ❌ Fallback token also failed: {e2}")
        
        return results
    
    # Test with multiple users
    sample_users = ["octocat", "torvalds", "gvanrossum", "kennethreitz", "yyx990803"]
    repo_results = await fetch_repositories_with_fallback(sample_users)
    
    # Print summary of all repos found
    print("\n📋 Summary:")
    total_repos = sum(len(repos) for repos in repo_results.values())
    print(f"Total repositories found: {total_repos}")
    for owner, repos in repo_results.items():
        print(f"  {owner}: {len(repos)} repositories")


if __name__ == "__main__":
    # Set up the event loop and run the main async function
    asyncio.run(main())