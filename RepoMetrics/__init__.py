"""
RepoMetrics - High-performance Git blame operations and repository management

This module provides Python bindings for Git repository analysis,
focusing on blame operations and commit history.
"""

from .repo_metrics import (
    RepoManager,
    CloneStatus,
    CloneTask,
)

__all__ = [
    "RepoManager",
    "CloneStatus",
    "CloneTask",
]

__version__ = "0.1.0"
