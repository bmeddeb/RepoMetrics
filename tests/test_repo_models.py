"""
Tests for Repository Models (CloneStatus, CloneTask, RepoManager)

This module contains tests for the Pydantic models associated with 
repository management including CloneStatus and CloneTask,
and the RepoManager wrapper.
"""

import pytest
import asyncio
from typing import Dict, List, Any, Optional

from GitFleet.models.repo import (
    CloneStatusType, 
    CloneStatus, 
    CloneTask, 
    RepoManager,
    RUST_AVAILABLE
)

# Mock classes to simulate Rust behavior
class MockRustCloneStatus:
    """Mock Rust CloneStatus for testing."""
    def __init__(
        self,
        status_type: str,
        progress: Optional[int] = None,
        error: Optional[str] = None
    ):
        self.status_type = status_type
        self.progress = progress
        self.error = error

class MockRustCloneTask:
    """Mock Rust CloneTask for testing."""
    def __init__(
        self,
        url: str,
        status: MockRustCloneStatus,
        temp_dir: Optional[str] = None
    ):
        self.url = url
        self.status = status
        self.temp_dir = temp_dir

class MockRustRepoManager:
    """Mock Rust RepoManager for testing."""
    def __init__(self, urls: List[str], github_username: str, github_token: str):
        self.urls = urls
        self.github_username = github_username
        self.github_token = github_token
        self._tasks = {}
        
        # Initialize with queued status for all repos
        for url in urls:
            status = MockRustCloneStatus(status_type="queued")
            self._tasks[url] = MockRustCloneTask(url=url, status=status)
            
    async def clone_all(self) -> None:
        """Simulate cloning all repositories."""
        # In a real implementation, this would be async
        for url in self.urls:
            await self.clone(url)
            
    async def clone(self, url: str) -> None:
        """Simulate cloning a single repository."""
        # Mark as cloning
        self._tasks[url].status = MockRustCloneStatus(status_type="cloning", progress=0)
        
        # Simulate progress
        for i in range(0, 101, 20):
            self._tasks[url].status = MockRustCloneStatus(status_type="cloning", progress=i)
            await asyncio.sleep(0.01)  # Small delay to simulate actual work
            
        # Mark as completed with a temp directory
        self._tasks[url].status = MockRustCloneStatus(status_type="completed")
        self._tasks[url].temp_dir = f"/tmp/mock_repo_{url.split('/')[-1]}"
        
    async def fetch_clone_tasks(self) -> Dict[str, MockRustCloneTask]:
        """Return the current clone tasks."""
        return self._tasks
    
    async def bulk_blame(self, repo_path: str, file_paths: List[str]) -> Dict[str, Any]:
        """Mock blame operation."""
        return {file: [{"line": 1, "content": "test", "commit": "abcdef"}] for file in file_paths}
    
    async def extract_commits(self, repo_path: str) -> List[Dict[str, Any]]:
        """Mock commit extraction."""
        return [{"hash": "abcdef", "author": "Test User", "message": "Test commit"}]
    
    def cleanup(self) -> Dict[str, Any]:
        """Mock cleanup operation."""
        return {url: True for url in self.urls}

# Patch the Rust modules for testing
@pytest.fixture
def patch_rust_modules(monkeypatch):
    """Replace Rust modules with mocks for testing."""
    monkeypatch.setattr("GitFleet.models.repo.RustRepoManager", MockRustRepoManager)
    monkeypatch.setattr("GitFleet.models.repo.RustCloneStatus", MockRustCloneStatus)
    monkeypatch.setattr("GitFleet.models.repo.RustCloneTask", MockRustCloneTask)
    monkeypatch.setattr("GitFleet.models.repo.RUST_AVAILABLE", True)
    
    yield
    
    # Restore the original state
    monkeypatch.undo()

# Tests for CloneStatusType
def test_clone_status_type():
    """Test CloneStatusType enum values."""
    assert CloneStatusType.QUEUED.value == "queued"
    assert CloneStatusType.CLONING.value == "cloning"
    assert CloneStatusType.COMPLETED.value == "completed"
    assert CloneStatusType.FAILED.value == "failed"
    
    # Test string conversion using value property
    assert CloneStatusType.QUEUED.value == "queued"
    
    # Test equality
    assert CloneStatusType.QUEUED == "queued"
    assert CloneStatusType.CLONING == "cloning"

# Tests for CloneStatus
def test_clone_status_creation():
    """Test CloneStatus model creation and validation."""
    # Test basic initialization
    status = CloneStatus(status_type=CloneStatusType.QUEUED)
    assert status.status_type == CloneStatusType.QUEUED
    assert status.progress is None
    assert status.error is None
    
    # Test with progress
    status = CloneStatus(status_type=CloneStatusType.CLONING, progress=50)
    assert status.status_type == CloneStatusType.CLONING
    assert status.progress == 50
    
    # Test with error
    status = CloneStatus(status_type=CloneStatusType.FAILED, error="Connection failed")
    assert status.status_type == CloneStatusType.FAILED
    assert status.error == "Connection failed"

def test_clone_status_validation():
    """Test CloneStatus validation rules."""
    # Test valid status types
    for status_type in CloneStatusType:
        status = CloneStatus(status_type=status_type)
        assert status.status_type == status_type
    
    # Test string status type (should convert to enum)
    status = CloneStatus(status_type="queued")
    assert status.status_type == CloneStatusType.QUEUED
    
    # Test progress validation (should be 0-100)
    status = CloneStatus(status_type=CloneStatusType.CLONING, progress=0)
    assert status.progress == 0
    
    status = CloneStatus(status_type=CloneStatusType.CLONING, progress=100)
    assert status.progress == 100
    
    # Progress should be None for non-cloning status
    status = CloneStatus(status_type=CloneStatusType.COMPLETED)
    assert status.progress is None
    
    # Error should only be set for failed status
    status = CloneStatus(status_type=CloneStatusType.FAILED, error="Test error")
    assert status.error == "Test error"

@pytest.mark.asyncio
async def test_clone_status_from_rust(patch_rust_modules):
    """Test CloneStatus.from_rust conversion."""
    # Create a mock Rust CloneStatus
    rust_status = MockRustCloneStatus(
        status_type="cloning",
        progress=75,
        error=None
    )
    
    # Convert to Pydantic model
    status = CloneStatus.from_rust(rust_status)
    
    # Verify fields
    assert status.status_type == CloneStatusType.CLONING
    assert status.progress == 75
    assert status.error is None
    
    # Test with error
    rust_status = MockRustCloneStatus(
        status_type="failed",
        progress=None,
        error="Git error: repository not found"
    )
    
    status = CloneStatus.from_rust(rust_status)
    assert status.status_type == CloneStatusType.FAILED
    assert status.progress is None
    assert status.error == "Git error: repository not found"

# Tests for CloneTask
def test_clone_task_creation():
    """Test CloneTask model creation and validation."""
    # Test basic initialization
    status = CloneStatus(status_type=CloneStatusType.QUEUED)
    task = CloneTask(
        url="https://github.com/user/repo.git",
        status=status
    )
    
    assert task.url == "https://github.com/user/repo.git"
    assert task.status == status
    assert task.temp_dir is None
    
    # Test with temp_dir
    task = CloneTask(
        url="https://github.com/user/repo.git",
        status=status,
        temp_dir="/tmp/repo"
    )
    
    assert task.temp_dir == "/tmp/repo"

@pytest.mark.asyncio
async def test_clone_task_from_rust(patch_rust_modules):
    """Test CloneTask.from_rust conversion."""
    # Create a mock Rust CloneStatus
    rust_status = MockRustCloneStatus(
        status_type="completed",
        progress=None
    )
    
    # Create a mock Rust CloneTask
    rust_task = MockRustCloneTask(
        url="https://github.com/user/repo.git",
        status=rust_status,
        temp_dir="/tmp/test_repo"
    )
    
    # Convert to Pydantic model
    task = CloneTask.from_rust(rust_task)
    
    # Verify fields
    assert task.url == "https://github.com/user/repo.git"
    assert task.status.status_type == CloneStatusType.COMPLETED
    assert task.temp_dir == "/tmp/test_repo"
    
    # Test without temp_dir
    rust_task = MockRustCloneTask(
        url="https://github.com/user/repo.git",
        status=MockRustCloneStatus(status_type="queued"),
        temp_dir=None
    )
    
    task = CloneTask.from_rust(rust_task)
    assert task.temp_dir is None

# Tests for RepoManager
@pytest.mark.asyncio
async def test_repo_manager_initialization(patch_rust_modules):
    """Test RepoManager initialization."""
    urls = ["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Should initialize without errors
    assert isinstance(manager, RepoManager)
    
    # Should have initialized the Rust manager
    assert hasattr(manager, "_rust_manager")
    assert isinstance(manager._rust_manager, MockRustRepoManager)

@pytest.mark.asyncio
async def test_repo_manager_clone_all(patch_rust_modules):
    """Test RepoManager.clone_all."""
    urls = ["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Clone all repositories
    await manager.clone_all()
    
    # Fetch and check tasks
    clone_tasks = await manager.fetch_clone_tasks()
    
    assert len(clone_tasks) == 2
    assert "https://github.com/user/repo1.git" in clone_tasks
    assert "https://github.com/user/repo2.git" in clone_tasks
    
    # All tasks should have completed status
    for url, task in clone_tasks.items():
        assert task.status.status_type == CloneStatusType.COMPLETED
        assert task.temp_dir is not None

@pytest.mark.asyncio
async def test_repo_manager_clone(patch_rust_modules):
    """Test RepoManager.clone (single repository)."""
    urls = ["https://github.com/user/repo1.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Clone a single repository
    await manager.clone("https://github.com/user/repo1.git")
    
    # Check task status
    clone_tasks = await manager.fetch_clone_tasks()
    task = clone_tasks["https://github.com/user/repo1.git"]
    
    assert task.status.status_type == CloneStatusType.COMPLETED
    assert task.temp_dir is not None

@pytest.mark.asyncio
async def test_repo_manager_fetch_clone_tasks(patch_rust_modules):
    """Test RepoManager.fetch_clone_tasks."""
    urls = ["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Fetch tasks before cloning
    pre_clone_tasks = await manager.fetch_clone_tasks()
    
    assert len(pre_clone_tasks) == 2
    for url, task in pre_clone_tasks.items():
        assert task.status.status_type == CloneStatusType.QUEUED
        assert task.temp_dir is None
    
    # Clone and check again
    await manager.clone_all()
    post_clone_tasks = await manager.fetch_clone_tasks()
    
    for url, task in post_clone_tasks.items():
        assert task.status.status_type == CloneStatusType.COMPLETED
        assert task.temp_dir is not None

def test_repo_manager_cleanup(patch_rust_modules):
    """Test RepoManager.cleanup."""
    urls = ["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Cleanup should return results for all URLs
    results = manager.cleanup()
    
    assert len(results) == 2
    assert all(results.values())  # All should be True (success)

@pytest.mark.asyncio
async def test_repo_manager_bulk_blame(patch_rust_modules):
    """Test RepoManager.bulk_blame."""
    urls = ["https://github.com/user/repo1.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Clone the repository
    await manager.clone_all()
    
    # Get the temp directory
    tasks = await manager.fetch_clone_tasks()
    temp_dir = tasks["https://github.com/user/repo1.git"].temp_dir
    
    # Run bulk blame
    blame_results = await manager.bulk_blame(temp_dir, ["file1.py", "file2.py"])
    
    # Check results
    assert len(blame_results) == 2
    assert "file1.py" in blame_results
    assert "file2.py" in blame_results

@pytest.mark.asyncio
async def test_repo_manager_extract_commits(patch_rust_modules):
    """Test RepoManager.extract_commits."""
    urls = ["https://github.com/user/repo1.git"]
    manager = RepoManager(urls, "test_user", "test_token")
    
    # Clone the repository
    await manager.clone_all()
    
    # Get the temp directory
    tasks = await manager.fetch_clone_tasks()
    temp_dir = tasks["https://github.com/user/repo1.git"].temp_dir
    
    # Extract commits
    commits = await manager.extract_commits(temp_dir)
    
    # Check results
    assert len(commits) == 1
    assert "hash" in commits[0]
    assert "author" in commits[0]
    assert "message" in commits[0]