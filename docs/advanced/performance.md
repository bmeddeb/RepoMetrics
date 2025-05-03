# Performance Tips

GitFleet is designed with performance in mind, leveraging Rust's speed and memory safety for core operations while providing a convenient Python interface. This guide provides tips and best practices for optimizing GitFleet's performance in your applications.

## Performance Architecture

GitFleet's performance architecture is built on several key components:

1. **Rust Core**: High-performance operations are implemented in Rust
2. **Concurrent Processing**: Utilizes Tokio for asynchronous operations
3. **Memory Management**: Efficient memory handling for large repositories
4. **Python Interface**: Thin Python wrappers that minimize overhead

## General Performance Tips

### Use Asynchronous APIs

Always prefer asynchronous APIs when available. GitFleet's async functions utilize Rust's Tokio runtime for optimal performance:

```python
# Good: Using async/await
async def process_repos():
    repos = await github_client.fetch_repositories("octocat")
    return repos

# Bad: Blocking the main thread
def process_repos_blocking():
    repos = github_client.fetch_repositories_sync("octocat")  # Hypothetical sync version
    return repos
```

### Batch Operations

Group related operations into batches rather than making multiple individual calls:

```python
# Good: Batch operation
results = await repo_manager.bulk_blame(repo_path, ["file1.py", "file2.py", "file3.py"])

# Less efficient: Individual operations
result1 = await repo_manager.blame(repo_path, "file1.py")
result2 = await repo_manager.blame(repo_path, "file2.py")
result3 = await repo_manager.blame(repo_path, "file3.py")
```

### Use Generators for Large Data

When working with large datasets, use generators to process data incrementally:

```python
async def process_large_repo(repo_path):
    # Process commits in batches
    async for commit_batch in repo_manager.yield_commits(repo_path, batch_size=100):
        # Process each batch without loading everything into memory
        process_batch(commit_batch)
```

## Repository Cloning Performance

### Shallow Clones

When you don't need the full history, use shallow clones:

```python
# Clone with minimal history (faster)
repo_manager = RepoManager(
    urls=["https://github.com/example/repo.git"],
    clone_options={"depth": 1}  # Only fetch the latest commit
)
```

### Efficient Clone Monitoring

When monitoring clone progress, be mindful of polling frequency:

```python
# Good: Reasonable refresh rate
while not clone_future.done():
    clone_tasks = await repo_manager.fetch_clone_tasks()
    # Process tasks...
    await asyncio.sleep(1)  # 1 second interval

# Bad: Excessive polling
while not clone_future.done():
    clone_tasks = await repo_manager.fetch_clone_tasks()
    # Process tasks...
    await asyncio.sleep(0.01)  # 10ms interval is too frequent
```

## API Interaction Performance

### Rate Limit Management

Efficiently manage rate limits with TokenManager:

```python
# Create a token manager with multiple tokens
token_manager = TokenManager()
for token in github_tokens:
    token_manager.add_token(token, ProviderType.GITHUB)

# Use token manager for auto-rotation
github = GitHubClient(
    token=github_tokens[0],  # Default token
    token_manager=token_manager  # Will rotate tokens as needed
)
```

### Pagination Handling

Use proper pagination to efficiently work with large result sets:

```python
# Fetch all repositories with automatic pagination handling
all_repos = await github_client.fetch_all_repositories("organization")

# Or process page by page for even more control
page = 1
while True:
    repos, has_next = await github_client.fetch_repositories_page("organization", page=page)
    # Process this page...
    if not has_next:
        break
    page += 1
```

### Local Caching

Implement caching for frequently accessed data:

```python
# Simple in-memory cache
repo_cache = {}

async def get_repo_info(repo_name):
    if repo_name in repo_cache:
        return repo_cache[repo_name]
    
    # Fetch from API
    repo_info = await github_client.fetch_repository_details("owner", repo_name)
    repo_cache[repo_name] = repo_info
    return repo_info
```

## Memory Optimization

### Cleanup Temporary Directories

Always clean up temporary directories when you're done with them:

```python
# Clean up after operations complete
cleanup_results = repo_manager.cleanup()
```

### Stream Large Repository Data

For large repositories, use streaming operations where available:

```python
# Process a large file line by line
async for blame_line in repo_manager.stream_blame(repo_path, "large_file.txt"):
    # Process each line individually
    process_line(blame_line)
```

## Threading and Concurrency

### Concurrent Operations

Use concurrent operations for independent tasks:

```python
import asyncio

async def analyze_multiple_repos():
    # Start multiple operations concurrently
    tasks = [
        repo_manager.extract_commits(repo1_path),
        repo_manager.extract_commits(repo2_path),
        repo_manager.extract_commits(repo3_path),
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    return results
```

### Process Pool for CPU-Bound Tasks

For CPU-intensive operations, consider offloading to a process pool:

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

def cpu_intensive_task(data):
    # Process data...
    return result

async def process_large_dataset(items):
    loop = asyncio.get_event_loop()
    
    with ProcessPoolExecutor() as pool:
        tasks = [
            loop.run_in_executor(pool, cpu_intensive_task, item)
            for item in items
        ]
        
        results = await asyncio.gather(*tasks)
        return results
```

## Monitoring and Profiling

### Memory Usage Monitoring

Monitor memory usage for large operations:

```python
import psutil
import os

def log_memory_usage(label):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024  # Convert to MB
    print(f"Memory usage ({label}): {mem:.2f} MB")

async def memory_intensive_operation():
    log_memory_usage("Before operation")
    result = await repo_manager.extract_all_file_contents(repo_path)
    log_memory_usage("After operation")
    return result
```

### Performance Timing

Time critical operations to identify bottlenecks:

```python
import time

async def measure_execution_time(coroutine, *args, **kwargs):
    start_time = time.time()
    result = await coroutine(*args, **kwargs)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"{coroutine.__name__} took {execution_time:.2f} seconds")
    
    return result

# Example usage
results = await measure_execution_time(
    repo_manager.bulk_blame, repo_path, file_paths
)
```

## Related Topics

- [Clone Monitoring](../api/clone-monitoring.md) - Efficient monitoring of clone operations
- [Error Handling](../api/error-handling.md) - Proper error handling for performance-critical code