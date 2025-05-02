# Token Management

GitFleet includes a token management system that helps you handle API rate limits and authentication across multiple tokens. This is especially useful for high-volume applications that need to maximize their API usage.

## Why Token Management?

Git hosting providers like GitHub, GitLab, and BitBucket implement rate limiting on their APIs to ensure fair usage. When you exceed these limits, your requests will be rejected until the rate limit resets.

Using multiple tokens allows you to:

1. Increase the total number of requests you can make
2. Continue operations when one token hits its rate limit
3. Distribute API load across multiple accounts

## Using Multiple Tokens

The simplest way to use multiple tokens is to create separate client instances and manually handle fallback logic:

```python
import asyncio
from GitFleet import GitHubClient
from GitFleet.providers.base import RateLimitError

# Initialize clients with different tokens
github1 = GitHubClient(token="token1")
github2 = GitHubClient(token="token2")

async def fetch_with_fallback(owner):
    try:
        # Try with the first token
        repos = await github1.fetch_repositories(owner)
        return repos
    except RateLimitError:
        # Fallback to the second token
        repos = await github2.fetch_repositories(owner)
        return repos
```

## Advanced Token Management

For more complex scenarios, you can implement a token rotation system:

```python
import asyncio
from GitFleet import GitHubClient
from GitFleet.providers.base import RateLimitError

class TokenManager:
    def __init__(self, tokens):
        self.tokens = tokens
        self.clients = [GitHubClient(token=token) for token in tokens]
        self.current_index = 0
        
    def get_next_client(self):
        client = self.clients[self.current_index]
        # Rotate to the next token
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
    
    async def fetch_with_rotation(self, owner):
        # Try with all available tokens
        for _ in range(len(self.clients)):
            client = self.get_next_client()
            try:
                return await client.fetch_repositories(owner)
            except RateLimitError:
                # Try the next token
                continue
        
        # If all tokens are rate limited
        raise RateLimitError("All tokens have exceeded rate limits", "github", 0)

# Usage
tokens = ["token1", "token2", "token3"]
manager = TokenManager(tokens)

async def main():
    # Fetch using token rotation
    for owner in ["octocat", "torvalds", "gvanrossum"]:
        try:
            repos = await manager.fetch_with_rotation(owner)
            print(f"Found {len(repos)} repos for {owner}")
        except RateLimitError:
            print(f"Could not fetch repos for {owner}, all tokens rate limited")

asyncio.run(main())
```

## Rate Limit Awareness

Monitor rate limits for your tokens to make informed decisions:

```python
async def check_rate_limits(clients):
    for i, client in enumerate(clients):
        try:
            rate_limit = await client.get_rate_limit()
            print(f"Token {i+1}: {rate_limit['remaining']}/{rate_limit['limit']} remaining")
            print(f"         Resets at: {rate_limit['reset_time']}")
        except Exception as e:
            print(f"Token {i+1}: Error - {e}")
```

## Best Practices

1. **Store tokens securely**: Never hard-code tokens in your source code. Use environment variables or secure secret management.

2. **Monitor rate limits**: Check rate limits regularly to anticipate when you might need to switch tokens.

3. **Handle rate limit errors**: Always catch `RateLimitError` exceptions and implement appropriate fallback logic.

4. **Respect API limits**: Even with multiple tokens, be respectful of API limits and avoid making unnecessary requests.

5. **Implement exponential backoff**: When all tokens are rate-limited, implement exponential backoff before retrying.

```python
import asyncio
import time
import random

async def fetch_with_backoff(client, owner, max_retries=5):
    for attempt in range(max_retries):
        try:
            return await client.fetch_repositories(owner)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Give up after max_retries
            
            # Calculate wait time with exponential backoff and jitter
            wait_time = min(2 ** attempt + random.random(), 60)
            print(f"Rate limited. Waiting {wait_time:.2f} seconds before retry...")
            await asyncio.sleep(wait_time)
```