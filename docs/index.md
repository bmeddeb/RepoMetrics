# GitFleet Python API

Welcome to the documentation for the GitFleet Python API, which provides high-performance Git blame operations and repository management.

## Features

- **High-Performance**: Core operations implemented in Rust for maximum speed
- **Async Operations**: All repository operations are non-blocking using asyncio
- **Git Provider Integration**: Support for GitHub, GitLab, and BitBucket APIs
- **Pydantic Models**: Strong validation and serialization for all data
- **Token Management**: Automatic token rotation and rate limit handling
- **Pandas Integration**: Convert results to DataFrames for analysis

## Available Classes

- [RepoManager](./RepoManager.md): Main interface for managing repositories, cloning, blame, and commit extraction.
- [CloneStatus](./CloneStatus.md): Represents the status of a repository cloning operation.
- [CloneTask](./CloneTask.md): Represents a repository cloning task and its status.

See the [complete API reference](./GitFleetAPI.md) for all available classes and methods.

---

## Quick Reference

### RepoManager
- `clone_all()`
- `fetch_clone_tasks()`
- `clone(url)`
- `bulk_blame(repo_path, file_paths)`
- `extract_commits(repo_path)`
- `cleanup()`

### CloneStatus
- `status_type`
- `progress`
- `error`

### CloneTask
- `url`
- `status`
- `temp_dir`

Click on a class name above to see detailed documentation for each class and its methods.