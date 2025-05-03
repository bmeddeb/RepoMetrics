# Python-Rust Bridge

GitFleet uses a hybrid architecture with a Rust core and Python bindings through [PyO3](https://github.com/PyO3/pyo3). This page explains how the Python-Rust bridge works and how to use it effectively.

## Architecture Overview

GitFleet's architecture consists of three main layers:

1. **Rust Core Library**: High-performance, memory-safe implementation of Git operations
2. **PyO3 Bridge Layer**: Exposes Rust functionality to Python with asyncio integration
3. **Python Interface**: User-friendly API with additional Python-specific features

## How PyO3 is Used in GitFleet

The PyO3 library allows GitFleet to expose Rust functionality to Python in a way that feels natural to Python developers. Here's how it works:

### Rust Struct Definitions with PyO3 Annotations

```rust
use pyo3::prelude::*;

#[pyclass]
struct RepoManager {
    urls: Vec<String>,
    github_token: String,
    // ...other fields
}

#[pymethods]
impl RepoManager {
    #[new]
    fn new(urls: Vec<String>, github_token: String) -> Self {
        RepoManager {
            urls,
            github_token,
            // ...initialize other fields
        }
    }
    
    fn clone_all(&self, py: Python) -> PyResult<PyObject> {
        // Implementation of clone_all that returns a Python Future
        // ...
    }
    
    // ...other methods
}
```

### Async Bridge with pyo3-async-runtime

GitFleet uses [pyo3-asyncio](https://github.com/awestlake87/pyo3-asyncio) to bridge between Rust's async model (Tokio) and Python's asyncio:

```rust
use pyo3::prelude::*;
use pyo3_asyncio::tokio::future_into_py;

#[pymethods]
impl RepoManager {
    fn clone_all<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let urls = self.urls.clone();
        let github_token = self.github_token.clone();
        
        // Create a Rust future
        let fut = async move {
            // Clone repositories asynchronously with tokio
            // ...
            Ok(Python::with_gil(|py| {
                // Convert result to Python object
                // ...
            })?)
        };
        
        // Convert Rust future to Python future
        future_into_py(py, fut)
    }
}
```

## Exposed Rust API

The following Rust modules are exposed to Python:

| Rust Module | Python Module | Description |
|-------------|---------------|-------------|
| `src/repo.rs` | `GitFleet.RepoManager` | Repository management |
| `src/clone.rs` | `GitFleet.models.repo` | Clone operations |
| `src/blame.rs` | `GitFleet.models.repo` | Blame functionality |
| `src/commits.rs` | `GitFleet.models.repo` | Commit extraction |
| `src/token.rs` | `GitFleet.providers.token_manager` | Token management |

## Data Conversion Between Python and Rust

GitFleet handles data conversion between Python and Rust transparently:

### Python to Rust

- Python strings → Rust `String`
- Python lists → Rust `Vec<T>`
- Python dicts → Rust `HashMap<K, V>` or custom structs
- Python None → Rust `Option<T>` as `None`

### Rust to Python

- Rust `String` → Python strings
- Rust `Vec<T>` → Python lists
- Rust `HashMap<K, V>` → Python dicts
- Rust structs → Python dataclasses or dicts
- Rust `Result<T, E>` → Python return value or exception
- Rust `Option<T>` → Python value or None

## Fallback to Python Implementation

For flexibility, GitFleet provides a pure Python implementation that can be used when the Rust implementation is not available or when explicitly requested:

```python
from GitFleet import RepoManager

# Use Rust implementation (default)
repo_manager = RepoManager(urls=["https://github.com/user/repo"])

# Force Python implementation
python_repo_manager = RepoManager(
    urls=["https://github.com/user/repo"],
    use_python_impl=True
)
```

## Performance Considerations

The Rust implementation offers significant performance benefits:

- **Memory Efficiency**: Rust's ownership model reduces memory usage
- **Processing Speed**: Blame and commit analysis is typically 5-10x faster in Rust
- **Concurrency**: Tokio's work-stealing scheduler efficiently handles many repositories
- **GIL Avoidance**: Compute-intensive operations run outside Python's GIL

## Contributing to the Bridge Layer

When contributing to the Python-Rust bridge:

1. Make changes to the Rust implementation first
2. Update the PyO3 bindings to expose the new functionality
3. Update the Python interface to match
4. Test both implementations (Rust and pure Python)
5. Document any differences in behavior between implementations

## Related Documentation

- [Architecture Overview](architecture.md)
- [Contributing Guide](contributing.md)
- [Performance Tips](../advanced/performance.md)