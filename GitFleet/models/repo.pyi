"""Type stubs for repository management models."""

from typing import Dict, List, Optional, Any, Union, ClassVar, Type, TypeVar, Protocol
from enum import Enum

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class RustCloneStatus(Protocol):
    """Protocol for Rust-generated CloneStatus class."""
    status_type: str
    progress: Optional[int]
    error: Optional[str]

class RustCloneTask(Protocol):
    """Protocol for Rust-generated CloneTask class."""
    url: str
    status: RustCloneStatus
    temp_dir: Optional[str]

class RustRepoManager(Protocol):
    """Protocol for Rust-generated RepoManager class."""
    def __init__(self, urls: List[str], github_username: str, github_token: str) -> None: ...
    async def clone_all(self) -> None: ...
    async def fetch_clone_tasks(self) -> Dict[str, RustCloneTask]: ...
    async def clone(self, url: str) -> None: ...
    async def bulk_blame(self, repo_path: str, file_paths: List[str]) -> Dict[str, Any]: ...
    async def extract_commits(self, repo_path: str) -> List[Dict[str, Any]]: ...
    def cleanup(self) -> Dict[str, Union[bool, str]]: ...

class CloneStatusType(str, Enum):
    """Enumeration of possible clone status types."""
    QUEUED: str
    CLONING: str
    COMPLETED: str
    FAILED: str

class CloneStatus(BaseModel):
    """Pydantic model for clone status information."""
    status_type: CloneStatusType
    progress: Optional[int]
    error: Optional[str]
    
    model_config: ClassVar[ConfigDict]
    
    @classmethod
    def from_rust(cls, rust_status: RustCloneStatus) -> "CloneStatus": ...
    
    def model_dump(self) -> Dict[str, Any]: ...
    def model_dump_json(self, indent: Optional[int] = None) -> str: ...
    @classmethod
    def model_validate(cls: Type[T], obj: Any) -> T: ...

class CloneTask(BaseModel):
    """Pydantic model for clone task information."""
    url: str
    status: CloneStatus
    temp_dir: Optional[str]
    
    model_config: ClassVar[ConfigDict]
    
    @classmethod
    def from_rust(cls, rust_task: RustCloneTask) -> "CloneTask": ...
    
    def model_dump(self) -> Dict[str, Any]: ...
    def model_dump_json(self, indent: Optional[int] = None) -> str: ...
    @classmethod
    def model_validate(cls: Type[T], obj: Any) -> T: ...

class RepoManager:
    """Wrapper class for the Rust RepoManager with Pydantic model support."""
    _rust_manager: RustRepoManager
    
    def __init__(self, urls: List[str], github_username: str, github_token: str) -> None: ...
    async def clone_all(self) -> None: ...
    async def fetch_clone_tasks(self) -> Dict[str, CloneTask]: ...
    async def clone(self, url: str) -> None: ...
    async def bulk_blame(self, repo_path: str, file_paths: List[str]) -> Dict[str, Any]: ...
    async def extract_commits(self, repo_path: str) -> List[Dict[str, Any]]: ...
    def cleanup(self) -> Dict[str, Union[bool, str]]: ...

def clone_status_to_pydantic(rust_status: RustCloneStatus) -> CloneStatus: ...
def clone_task_to_pydantic(rust_task: RustCloneTask) -> CloneTask: ...