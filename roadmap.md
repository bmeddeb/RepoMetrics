# 🗺️ GitFleet Roadmap

## 🚀 Project Vision

**GitFleet** aims to be the fastest and most scalable library for Git repository analysis in Python—powered by Rust for performance-critical operations and Python for high-level orchestration.

---

## 🧠 Design Philosophy

GitFleet follows a hybrid Rust/Python model:

| Use **Rust** when: | Use **Python** when: |
|--------------------|----------------------|
| The task involves **I/O + CPU-bound** processing (e.g., git blame, parsing many files) | The task is **I/O-bound only** (e.g., fetching metadata from GitHub API) |
| You need **true multithreading** (e.g., `rayon`, native threads) | Async workflows using `asyncio`, `httpx`, etc. are sufficient |
| The operation scales poorly in Python due to GIL | The task is lightweight, user-facing, or flexible |

### 🔥 Rust Core Operations

- Bulk `git blame` (using `rayon`)
- Commit history / `git log` parsing
- File tree scanning (`ls-tree`)
- Diff and patch inspection
- Contributor and LOC stats

### 🐍 Python Async Operations

- GitHub/GitLab/GitBucket API clients (`httpx`, `aiohttp`)
- Token management and rate limit tracking
- Orchestration of analysis flows
- Data export (Pandas, CSV, JSON)
- CLI and web interface integration

---

## 📦 Milestone Roadmap

| Milestone | Feature | Status | Notes |
|----------|---------|--------|-------|
| **v0.1.0** | Async bulk cloning + bulk blame via Rust | ✅ Complete | Core functionality |
| **v0.2.0** | Add GitHub/GitLab/GitBucket async API clients | 🟡 In Progress | Include project/user/repo metadata |
| **v0.3.0** | Implement multi-token manager with rate limit handling | 🟡 In Progress | Round-robin and fallback logic |
| **v0.4.0** | Pandas DataFrame exports (`to_pandas()` methods) | ⬜ Planned | Useful for analytics & grading |
| **v0.5.0** | Repository snapshot/diff analysis | ⬜ Planned | `git diff` across time ranges |
| **v0.6.0** | File history and blame heatmap support | ⬜ Planned | Contributor/time-based visual output |
| **v0.7.0** | Progress reporting callbacks/hooks (Python-side) | ⬜ Planned | For use in UI and batch jobs |
| **v0.8.0** | Pre-built wheels for Linux, macOS, Windows | ⬜ Planned | Use GitHub Actions + `maturin` |
| **v1.0.0** | Full documentation site + examples | ⬜ Planned | Hosted with MkDocs  |

---

## 💡 Long-Term Ideas

- GraphQL and REST hybrid client mode
- Repo visualization (commit tree, blame map)
- Web dashboard with real-time status via Dash or FastAPI
- Plugin system for user-defined analysis steps

---

## 🤝 Contributing

Want to shape GitFleet? Contributions are welcome! See CONTRIBUTING.md (coming soon).
