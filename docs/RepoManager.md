# RepoManager

The `RepoManager` class is the main interface for managing multiple Git repositories, performing high-performance clone operations, running blame analysis, and extracting commit history. It is designed for asynchronous use, allowing you to efficiently manage and analyze many repositories in parallel.

> **Note:** All major methods of `RepoManager` are asynchronous and should be awaited. You can use Python's `asyncio` or any compatible event loop to run these methods.

## Overview

- Manage a set of repositories (clone, track status, cleanup)
- Perform bulk blame operations on files
- Extract commit history from repositories
- All operations are designed to be non-blocking and scalable

## Initialization

```python
from RepoMetrics import RepoManager

# List of repository URLs to manage
urls = [
    "https://github.com/owner/repo1.git",
    "https://github.com/owner/repo2.git",
]

# Create a RepoManager instance
manager = RepoManager(urls, github_username="your-username", github_token="your-token")
```

## Methods

### clone_all()
Clones all repositories configured in this manager instance asynchronously.

```python
await manager.clone_all()
```

### fetch_clone_tasks()
Fetches the current status of all cloning tasks asynchronously. Returns a dictionary mapping repository URLs to `CloneTask` objects, which include a `CloneStatus`.

```python
clone_tasks = await manager.fetch_clone_tasks()
for url, task in clone_tasks.items():
    print(url, task.status.status_type)
```

### clone(url)
Clones a single repository specified by URL asynchronously.

```python
await manager.clone("https://github.com/owner/repo3.git")
```

### bulk_blame(repo_path, file_paths)
Performs 'git blame' on multiple files within a cloned repository asynchronously. Returns a dictionary mapping file paths to blame results.

```python
blame_results = await manager.bulk_blame("/path/to/repo", ["file1.py", "file2.py"])
for file, lines in blame_results.items():
    print(f"Blame for {file}:", lines)
```

### extract_commits(repo_path)
Extracts commit data from a cloned repository asynchronously. Returns a list of commit dictionaries.

```python
commits = await manager.extract_commits("/path/to/repo")
print(f"Found {len(commits)} commits.")
```

### cleanup()
Cleans up all temporary directories created for cloned repositories. Returns a dictionary with repository URLs as keys and cleanup results as values (True for success, or an error message).

```python
cleanup_results = manager.cleanup()
for url, result in cleanup_results.items():
    print(f"Cleanup for {url}: {result}")
```

---

## Simple Example

```python
import asyncio
from RepoMetrics import RepoManager

async def main():
    urls = ["https://github.com/owner/repo1.git"]
    manager = RepoManager(urls, "username", "token")
    await manager.clone_all()
    tasks = await manager.fetch_clone_tasks()
    print(tasks)
    await manager.bulk_blame("/path/to/repo", ["file1.py"])
    await manager.extract_commits("/path/to/repo")
    manager.cleanup()

asyncio.run(main())
```

## Advanced Example: Managing Multiple Repositories

```python
import asyncio
from RepoMetrics import RepoManager

async def main():
    urls = [
        "https://github.com/owner/repo1.git",
        "https://github.com/owner/repo2.git",
        "https://github.com/owner/repo3.git",
    ]
    manager = RepoManager(urls, "username", "token")
    await manager.clone_all()
    clone_tasks = await manager.fetch_clone_tasks()
    for url, task in clone_tasks.items():
        print(f"{url}: {task.status.status_type}")
    # Run blame on all files in all repos (example)
    for url, task in clone_tasks.items():
        if task.temp_dir:
            blame = await manager.bulk_blame(task.temp_dir, ["main.py", "utils.py"])
            print(f"Blame for {url}: {blame}")
    # Extract commits
    for url, task in clone_tasks.items():
        if task.temp_dir:
            commits = await manager.extract_commits(task.temp_dir)
            print(f"Commits for {url}: {len(commits)} found.")
    # Cleanup
    results = manager.cleanup()
    print("Cleanup results:", results)

asyncio.run(main())
```

---

For details on `CloneTask` and `CloneStatus`, see their respective documentation pages.
