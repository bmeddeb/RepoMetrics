# RepoMetrics Python API

Welcome to the documentation for the RepoMetrics Python API, which provides high-performance Git blame operations and repository management.

## Available Classes

- [RepoManager](./RepoManager.md): Main interface for managing repositories, cloning, blame, and commit extraction.
- [CloneStatus](./CloneStatus.md): Represents the status of a repository cloning operation.
- [CloneTask](./CloneTask.md): Represents a repository cloning task and its status.

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