# CloneTask

The `CloneTask` class represents a repository cloning task and its current status. It is typically used to track the progress and results of repository cloning operations managed by `RepoManager`.

A `CloneTask` object is returned by methods such as `RepoManager.fetch_clone_tasks()`, which provides a mapping from repository URLs to their associated `CloneTask`.

## Fields

- `url` (`str`): The URL of the repository being cloned.
- `status` (`CloneStatus`): The current status of the cloning operation (see the `CloneStatus` documentation for details).
- `temp_dir` (`Optional[str]`): The path to the temporary directory where the repository was cloned, or `None` if cloning has not completed or failed.

## Typical Usage

You do not create `CloneTask` objects directly. Instead, you receive them from `RepoManager` methods, most commonly from `fetch_clone_tasks()`.

### Example: Checking Clone Statuses

```python
import asyncio
from RepoMetrics import RepoManager

async def main():
    urls = ["https://github.com/owner/repo1.git"]
    manager = RepoManager(urls, "username", "token")
    await manager.clone_all()
    clone_tasks = await manager.fetch_clone_tasks()
    for url, task in clone_tasks.items():
        print(f"Repo: {url}")
        print(f"  Status: {task.status.status_type}")
        print(f"  Temp dir: {task.temp_dir}")

asyncio.run(main())
```

### Example: Using temp_dir for Further Operations

After cloning, you can use the `temp_dir` field of a `CloneTask` to perform further operations, such as blame or commit extraction:

```python
# ... after fetching clone_tasks ...
for url, task in clone_tasks.items():
    if task.temp_dir:
        blame = await manager.bulk_blame(task.temp_dir, ["main.py"])
        print(f"Blame for {url}: {blame}")
```

---

For details on the `status` field, see the [CloneStatus](./CloneStatus.md) documentation.