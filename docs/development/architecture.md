# GitFleet Architecture

This page provides an overview of GitFleet's architecture, explaining the design decisions, component interactions, and implementation details.

## High-Level Architecture

GitFleet is built with a hybrid architecture that combines the performance of Rust with the convenience and ecosystem of Python:

```
┌────────────────────────────────────────────────────────────┐
│                      Python Layer                          │
│                                                            │
│  ┌───────────────┐   ┌────────────────┐   ┌─────────────┐  │
│  │ RepoManager   │   │ Provider APIs  │   │ Models      │  │
│  │ Python API    │   │ (GitHub, etc.) │   │ (Pydantic)  │  │
│  └───────────────┘   └────────────────┘   └─────────────┘  │
└────────────────────────────────────────────────────────────┘
                          │
                          │ PyO3
                          ▼
┌────────────────────────────────────────────────────────────┐
│                       Rust Layer                           │
│                                                            │
│  ┌───────────────┐   ┌────────────────┐   ┌─────────────┐  │
│  │ RepoManager   │   │ Git Operations │   │ Core Models │  │
│  │ Implementation│   │ (blame, etc.)  │   │             │  │
│  └───────────────┘   └────────────────┘   └─────────────┘  │
└────────────────────────────────────────────────────────────┘
                          │
                          │ FFI
                          ▼
┌────────────────────────────────────────────────────────────┐
│                     External Resources                      │
│                                                            │
│  ┌───────────────┐   ┌────────────────┐   ┌─────────────┐  │
│  │ Local Git     │   │ GitHub API     │   │ File System │  │
│  │ Repositories  │   │                │   │             │  │
│  └───────────────┘   └────────────────┘   └─────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## Core Components

### Rust Core Library

The core functionality is implemented in Rust for maximum performance:

- **Repository Manager**: Manages repository cloning, cleanup, and operations
- **Blame Engine**: High-performance blame analysis
- **Commit Extractor**: Efficient commit history processing
- **Clone Manager**: Asynchronous repository cloning with progress tracking

#### Key Rust Modules

- `src/lib.rs`: Main entrypoint and Python binding definitions
- `src/repo.rs`: Repository management logic
- `src/blame.rs`: Git blame implementation
- `src/commits.rs`: Commit history extraction
- `src/clone.rs`: Repository cloning with progress tracking
- `src/token.rs`: Token management for API authentication

### Python Interface

The Python interface provides a user-friendly API with additional features:

- **Asyncio Integration**: All operations are exposed as Python coroutines
- **Pydantic Models**: Type validation and serialization
- **Provider APIs**: Interfaces for Git hosting providers
- **Pandas Integration**: Convert results to DataFrames

#### Key Python Modules

- `GitFleet/__init__.py`: Main package exports
- `GitFleet/models/`: Data models for repository operations
- `GitFleet/providers/`: Provider API clients (GitHub, etc.)
- `GitFleet/utils/`: Utility functions and helpers

## Concurrency Model

GitFleet uses a hybrid concurrency model:

- **Rust**: Uses Tokio for asynchronous operations
- **Python**: Exposes asyncio coroutines for non-blocking operations
- **Bridge**: Uses pyo3-asyncio to bridge between Tokio and asyncio

Operations that could block (like Git operations) are executed in separate threads to avoid blocking the main event loop.

## Memory Management

GitFleet optimizes memory usage through:

- **Rust Ownership**: Ensures memory safety without garbage collection
- **Arc Sharing**: Shared resources use atomic reference counting
- **Temporary Directories**: Automatic cleanup of temporary clone directories
- **Stream Processing**: Large result sets are processed as streams, not loaded entirely in memory

## Error Handling

Error handling is comprehensive:

- **Rust Results**: Functions return `Result<T, E>` for error handling
- **Python Exceptions**: Rust errors are converted to appropriate Python exceptions
- **Status Objects**: Operations provide status objects with detailed information
- **Logging**: Comprehensive logging throughout the codebase

## Testing Strategy

GitFleet employs a multi-layered testing strategy:

- **Rust Unit Tests**: Test core functionality in isolation
- **Python Unit Tests**: Test Python-specific functionality
- **Integration Tests**: Test the full stack from Python to external systems
- **Property-Based Tests**: Test with randomized inputs for robustness

## Performance Optimizations

Several performance optimizations are employed:

- **Parallel Processing**: Multiple repositories processed concurrently
- **Lazy Loading**: Results loaded on demand to reduce memory usage
- **Caching**: Common operations are cached to avoid redundant work
- **Native Implementation**: Performance-critical code in Rust
- **Tokio Runtime**: Efficient task scheduler for concurrent operations

## Security Considerations

GitFleet prioritizes security:

- **Token Management**: Secure handling of API tokens
- **Temporary Storage**: Secure creation and cleanup of temporary directories
- **Input Validation**: Comprehensive validation of all inputs
- **Safe Defaults**: Conservative defaults for all operations

## Related Documentation

- [Python-Rust Bridge](python-rust-bridge.md): Details on the PyO3 integration
- [Contributing Guide](contributing.md): How to contribute to GitFleet
- [Performance Tips](../advanced/performance.md): Tips for maximizing performance