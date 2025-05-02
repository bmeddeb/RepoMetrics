from typing import Dict, List, Optional, Union, Any, Awaitable


class CloneStatus:
    status_type: str
    progress: Optional[int]
    error: Optional[str]


class CloneTask:
    url: str
    status: CloneStatus
    temp_dir: Optional[str]


class RepoManager:
    def __init__(
        self, urls: List[str], github_username: str, github_token: str) -> None: ...

    def clone_all(self) -> Awaitable[None]: ...

    def fetch_clone_tasks(self) -> Awaitable[Dict[str, CloneTask]]: ...

    def clone(self, url: str) -> Awaitable[None]: ...

    def bulk_blame(
        self, repo_path: str, file_paths: List[str]
    ) -> Awaitable[Dict[str, Union[List[Dict[str, Any]], str]]]: ...

    def extract_commits(
        self, repo_path: str) -> Awaitable[Union[List[Dict[str, Any]], str]]: ...

    def cleanup(self) -> Dict[str, Union[bool, str]]: ...
