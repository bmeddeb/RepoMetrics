"""
Testing utilities for GitFleet.

This module provides test-specific implementations of core GitFleet classes
that can be used for testing without making real network or filesystem calls.
"""

from .mocks import (
    MockRepoManager,
    MockCloneStatus,
    MockCloneTask,
    create_test_blame_data,
    create_test_commit_data,
)

__all__ = [
    "MockRepoManager",
    "MockCloneStatus",
    "MockCloneTask",
    "create_test_blame_data",
    "create_test_commit_data",
]