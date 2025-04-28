# CloneStatus

The `CloneStatus` class represents the current status of a repository cloning operation. It is used to track the progress and outcome of cloning tasks managed by `RepoManager` and is typically accessed as the `status` field of a `CloneTask` object.

## Fields

- `status_type` (`str`): The type of status. Possible values are:
  - `'queued'`: The cloning task is waiting to start.
  - `'cloning'`: The repository is currently being cloned. See `progress` for completion percentage.
  - `'completed'`: The repository has been successfully cloned.
  - `'failed'`: The cloning operation failed. See `error` for details.
- `progress` (`Optional[int]`): The percentage of completion (0-100) if the task is currently cloning, or `None` otherwise.
- `error` (`Optional[str]`): An error message if the cloning operation failed, or `None` otherwise.

## Typical Usage

You will most often encounter `CloneStatus` as part of a `CloneTask` when checking the status of repository cloning operations.

### Example: Checking the Status of a CloneTask

```python
import asyncio
from RepoMetrics import RepoManager

async def main():
    urls = ["https://github.com/owner/repo1.git"]
    manager = RepoManager(urls, "username", "token")
    await manager.clone_all()
    clone_tasks = await manager.fetch_clone_tasks()
    for url, task in clone_tasks.items():
        status = task.status
        print(f"Repo: {url}")
        print(f"  Status: {status.status_type}")
        if status.status_type == "cloning":
            print(f"  Progress: {status.progress}%")
        if status.status_type == "failed":
            print(f"  Error: {status.error}")

asyncio.run(main())
```

---

The `CloneStatus` class helps you monitor and react to the state of repository cloning operations in your workflow.

_Detailed documentation coming soon._