"""
Repository management models for use with the Rust-based RepoManager.

This module provides Pydantic models that mirror the PyO3-generated classes
from the Rust implementation. These models simplify serialization, validation,
and conversion between the Rust objects and Python data.
"""

from typing import Dict, List, Optional, Any, Union, ClassVar
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

try:
    # Import the Rust-generated classes if available
    from GitFleet.GitFleet import RepoManager as RustRepoManager
    from GitFleet.GitFleet import CloneStatus as RustCloneStatus
    from GitFleet.GitFleet import CloneTask as RustCloneTask
    RUST_AVAILABLE = True
except ImportError:
    # Define stub classes if Rust extension isn't available
    RUST_AVAILABLE = False
    RustRepoManager = object
    RustCloneStatus = object
    RustCloneTask = object


class CloneStatusType(str, Enum):
    """Enumeration of possible clone status types."""
    QUEUED = "queued"
    CLONING = "cloning"
    COMPLETED = "completed"
    FAILED = "failed"


class CloneStatus(BaseModel):
    """Pydantic model for clone status information.
    
    This model mirrors the Rust-generated CloneStatus class and provides
    serialization, validation, and conversion capabilities.
    
    Attributes:
        status_type: The type of status (queued, cloning, completed, failed)
        progress: The percentage of completion (0-100) if cloning, or None
        error: An error message if failed, or None
    """
    status_type: CloneStatusType
    progress: Optional[int] = None
    error: Optional[str] = None
    
    model_config = ConfigDict(
        frozen=True,
        extra='ignore',
    )
    
    @classmethod
    def from_rust(cls, rust_status: RustCloneStatus) -> "CloneStatus":
        """Convert a Rust CloneStatus to this Pydantic model."""
        if not RUST_AVAILABLE:
            raise ImportError("Rust implementation not available")
        
        return cls(
            status_type=rust_status.status_type,
            progress=rust_status.progress,
            error=rust_status.error,
        )


class CloneTask(BaseModel):
    """Pydantic model for clone task information.
    
    This model mirrors the Rust-generated CloneTask class and provides
    serialization, validation, and conversion capabilities.
    
    Attributes:
        url: The URL of the repository being cloned
        status: The current status of the cloning operation (CloneStatus)
        temp_dir: The path to the temporary directory where the repository
                 was cloned, or None if cloning has not completed or failed
    """
    url: str
    status: CloneStatus
    temp_dir: Optional[str] = None
    
    model_config = ConfigDict(
        frozen=True,
        extra='ignore',
    )
    
    @classmethod
    def from_rust(cls, rust_task: RustCloneTask) -> "CloneTask":
        """Convert a Rust CloneTask to this Pydantic model."""
        if not RUST_AVAILABLE:
            raise ImportError("Rust implementation not available")
        
        return cls(
            url=rust_task.url,
            status=CloneStatus.from_rust(rust_task.status),
            temp_dir=rust_task.temp_dir,
        )


class RepoManager:
    """
    Wrapper class for the Rust RepoManager with Pydantic model support.
    
    This wrapper provides the same interface as the Rust RepoManager but
    converts the results to Pydantic models for better serialization and
    validation.
    
    Note: This is not a Pydantic model itself, but a wrapper that uses
    Pydantic models for its results.
    """
    
    def __init__(self, urls: List[str], github_username: str, github_token: str):
        """Initialize the RepoManager.
        
        Args:
            urls: List of repository URLs to manage
            github_username: GitHub username for authentication
            github_token: GitHub token for authentication
        
        Raises:
            ImportError: If the Rust implementation is not available
        """
        if not RUST_AVAILABLE:
            raise ImportError("Rust implementation not available")
        
        self._rust_manager = RustRepoManager(urls, github_username, github_token)
    
    async def clone_all(self) -> None:
        """Clone all repositories configured in this manager instance."""
        await self._rust_manager.clone_all()
    
    async def fetch_clone_tasks(self) -> Dict[str, CloneTask]:
        """Fetch the current status of all cloning tasks.
        
        Returns:
            Dictionary mapping repository URLs to CloneTask objects
        """
        rust_tasks = await self._rust_manager.fetch_clone_tasks()
        return {url: CloneTask.from_rust(task) for url, task in rust_tasks.items()}
    
    async def clone(self, url: str) -> None:
        """Clone a single repository specified by URL.
        
        Args:
            url: Repository URL to clone
        """
        await self._rust_manager.clone(url)
    
    async def bulk_blame(self, repo_path: str, file_paths: List[str]) -> Dict[str, Any]:
        """Perform 'git blame' on multiple files within a cloned repository.
        
        Args:
            repo_path: Path to the cloned repository
            file_paths: List of file paths to blame
            
        Returns:
            Dictionary mapping file paths to blame results
        """
        return await self._rust_manager.bulk_blame(repo_path, file_paths)
    
    async def extract_commits(self, repo_path: str) -> List[Dict[str, Any]]:
        """Extract commit data from a cloned repository.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            List of commit dictionaries
        """
        return await self._rust_manager.extract_commits(repo_path)
    
    def cleanup(self) -> Dict[str, Union[bool, str]]:
        """Clean up all temporary directories created for cloned repositories.
        
        Returns:
            Dictionary with repository URLs as keys and cleanup results as values
        """
        return self._rust_manager.cleanup()


# Convenience functions for working with the Rust types
def clone_status_to_pydantic(rust_status: RustCloneStatus) -> CloneStatus:
    """Convert a Rust CloneStatus to a Pydantic model."""
    return CloneStatus.from_rust(rust_status)


def clone_task_to_pydantic(rust_task: RustCloneTask) -> CloneTask:
    """Convert a Rust CloneTask to a Pydantic model."""
    return CloneTask.from_rust(rust_task)