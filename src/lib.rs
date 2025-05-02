#![allow(dead_code, non_snake_case)]

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::IntoPyObject;
use pyo3_async_runtimes::tokio;

use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;

// --- Import necessary items from modules ---
mod blame;
mod clone;
mod commits;
mod repo;
mod providers;
mod token;

use crate::clone::{InternalCloneStatus, InternalRepoCloneTask};
use crate::repo::InternalRepoManagerLogic;
use crate::token::TokenManager;

// --- Exposed Python Class: CloneStatus ---
#[pyclass(name = "CloneStatus", module = "GitFleet")]
#[derive(Debug, Clone)]
pub struct ExposedCloneStatus {
    #[pyo3(get)]
    pub status_type: String,
    #[pyo3(get)]
    pub progress: Option<u8>,
    #[pyo3(get)]
    pub error: Option<String>,
}

impl From<InternalCloneStatus> for ExposedCloneStatus {
    fn from(status: InternalCloneStatus) -> Self {
        match status {
            InternalCloneStatus::Queued => Self {
                status_type: "queued".to_string(),
                progress: None,
                error: None,
            },
            InternalCloneStatus::Cloning(p) => Self {
                status_type: "cloning".to_string(),
                progress: Some(p),
                error: None,
            },
            InternalCloneStatus::Completed => Self {
                status_type: "completed".to_string(),
                progress: None,
                error: None,
            },
            InternalCloneStatus::Failed(e) => Self {
                status_type: "failed".to_string(),
                progress: None,
                error: Some(e),
            },
        }
    }
}

// --- Exposed Python Class: CloneTask ---
#[pyclass(name = "CloneTask", module = "GitFleet")]
#[derive(Debug, Clone)]
pub struct ExposedCloneTask {
    #[pyo3(get)]
    pub url: String,
    #[pyo3(get)]
    pub status: ExposedCloneStatus,
    #[pyo3(get)]
    pub temp_dir: Option<String>,
}

impl From<InternalRepoCloneTask> for ExposedCloneTask {
    fn from(task: InternalRepoCloneTask) -> Self {
        Self {
            url: task.url,
            status: task.status.into(),
            temp_dir: task.temp_dir.map(|p| p.to_string_lossy().to_string()),
        }
    }
}

// --- Exposed Python Class: RepoManager ---
#[pyclass(name = "RepoManager", module = "GitFleet")]
#[derive(Clone)]
pub struct RepoManager {
    inner: Arc<InternalRepoManagerLogic>,
}

#[pymethods]
impl RepoManager {
    #[new]
    fn new(urls: Vec<String>, github_username: String, github_token: String) -> Self {
        let string_urls: Vec<&str> = urls.iter().map(|s| s.as_str()).collect();
        Self {
            inner: Arc::new(InternalRepoManagerLogic::new(
                &string_urls,
                &github_username,
                &github_token,
            )),
        }
    }

    /// Clones all repositories configured in this manager instance asynchronously.
    #[pyo3(name = "clone_all")]
    fn clone_all<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            inner.clone_all().await;
            Python::with_gil(|py| Ok(py.None()))
        })
    }

    /// Fetches the current status of all cloning tasks asynchronously.
    #[pyo3(name = "fetch_clone_tasks")]
    fn fetch_clone_tasks<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let internal_tasks = inner.get_internal_tasks().await;
            let result: HashMap<String, ExposedCloneTask> = internal_tasks
                .into_iter()
                .map(|(k, v)| (k, v.into()))
                .collect();
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let dict = PyDict::new(py);
                for (k, v) in result {
                    dict.set_item(k, v)?;
                }
                Ok(dict.into())
            })
        })
    }

    /// Clones a single repository specified by URL asynchronously.
    #[pyo3(name = "clone")]
    fn clone<'py>(&self, py: Python<'py>, _url: String) -> PyResult<Bound<'py, PyAny>> {
        let _inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move { Python::with_gil(|py| Ok(py.None())) })
    }

    /// Performs 'git blame' on multiple files within a cloned repository asynchronously.
    #[pyo3(name = "bulk_blame")]
    fn bulk_blame<'py>(
        &self,
        py: Python<'py>,
        repo_path: String,
        file_paths: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result_map = inner
                .bulk_blame(&PathBuf::from(repo_path), file_paths)
                .await;
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                match result_map {
                    Ok(blame_results_map) => {
                        let py_result_dict = PyDict::new(py);
                        for (file_path, blame_result) in blame_results_map {
                            match blame_result {
                                Ok(blame_lines) => {
                                    let py_blame_list = PyList::empty(py);
                                    for line_info in blame_lines {
                                        let line_dict = PyDict::new(py);
                                        line_dict.set_item("commit_id", &line_info.commit_id)?;
                                        line_dict
                                            .set_item("author_name", &line_info.author_name)?;
                                        line_dict
                                            .set_item("author_email", &line_info.author_email)?;
                                        line_dict
                                            .set_item("orig_line_no", line_info.orig_line_no)?;
                                        line_dict
                                            .set_item("final_line_no", line_info.final_line_no)?;
                                        line_dict
                                            .set_item("line_content", &line_info.line_content)?;
                                        py_blame_list.append(line_dict)?;
                                    }
                                    py_result_dict.set_item(file_path, py_blame_list)?;
                                }
                                Err(e) => {
                                    py_result_dict.set_item(file_path, e)?;
                                }
                            }
                        }
                        Ok(py_result_dict.into())
                    }
                    Err(e) => Ok(e.into_pyobject(py).unwrap().into()),
                }
            })
        })
    }

    /// Extracts commit data from a cloned repository asynchronously.
    #[pyo3(name = "extract_commits")]
    fn extract_commits<'py>(
        &self,
        py: Python<'py>,
        repo_path: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        let repo_path_clone = repo_path.clone();
        tokio::future_into_py(py, async move {
            // Run the commit extraction in a blocking thread
            let result_vec = ::tokio::task::spawn_blocking(move || {
                inner.extract_commits(&PathBuf::from(repo_path_clone))
            })
            .await
            .unwrap_or_else(|e| Err(format!("Task execution failed: {}", e)));
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                match result_vec {
                    Ok(commit_infos) => {
                        let py_commit_list = PyList::empty(py);
                        for info in commit_infos {
                            let commit_dict = PyDict::new(py);
                            commit_dict.set_item("sha", &info.sha)?;
                            commit_dict.set_item("repo_name", &info.repo_name)?;
                            commit_dict.set_item("message", &info.message)?;
                            commit_dict.set_item("author_name", &info.author_name)?;
                            commit_dict.set_item("author_email", &info.author_email)?;
                            commit_dict.set_item("author_timestamp", info.author_timestamp)?;
                            commit_dict.set_item("author_offset", info.author_offset)?;
                            commit_dict.set_item("committer_name", &info.committer_name)?;
                            commit_dict.set_item("committer_email", &info.committer_email)?;
                            commit_dict
                                .set_item("committer_timestamp", info.committer_timestamp)?;
                            commit_dict.set_item("committer_offset", info.committer_offset)?;
                            commit_dict.set_item("additions", info.additions)?;
                            commit_dict.set_item("deletions", info.deletions)?;
                            commit_dict.set_item("is_merge", info.is_merge)?;
                            py_commit_list.append(commit_dict)?;
                        }
                        Ok(py_commit_list.into())
                    }
                    Err(err_string) => Ok(err_string.into_pyobject(py).unwrap().into()),
                }
            })
        })
    }

    /// Cleans up all temporary directories created for cloned repositories.
    /// Returns a dictionary with repository URLs as keys and cleanup results as values.
    #[pyo3(name = "cleanup")]
    fn cleanup<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let inner = Arc::clone(&self.inner);
        let results = inner.cleanup_temp_dirs();
        let py_dict = PyDict::new(py);

        for (url, result) in results {
            match result {
                Ok(_) => {
                    py_dict.set_item(url, true)?;
                }
                Err(error_msg) => {
                    py_dict.set_item(url, error_msg)?;
                }
            }
        }

        Ok(py_dict.into())
    }
}

// --- Exposed GitHub Client Class ---
#[pyclass(name = "GitHubClient", module = "GitFleet")]
#[derive(Clone)]
pub struct ExposedGitHubClient {
    inner: Arc<providers::github::GitHubProvider>,
}

#[pymethods]
impl ExposedGitHubClient {
    #[new]
    fn new(token: String, base_url: Option<String>) -> Self {
        Self {
            inner: Arc::new(providers::github::GitHubProvider::new(token, base_url)),
        }
    }

    /// Fetches repositories for the specified owner/organization
    #[pyo3(name = "fetch_repositories")]
    fn fetch_repositories<'py>(&self, py: Python<'py>, owner: String) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.fetch_repositories(&owner).await?;
            
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let py_repos = PyList::empty(py);
                for repo_info in result {
                    let repo_dict = PyDict::new(py);
                    repo_dict.set_item("name", &repo_info.name)?;
                    repo_dict.set_item("full_name", &repo_info.full_name)?;
                    repo_dict.set_item("clone_url", &repo_info.clone_url)?;
                    repo_dict.set_item("description", &repo_info.description)?;
                    repo_dict.set_item("default_branch", &repo_info.default_branch)?;
                    repo_dict.set_item("created_at", &repo_info.created_at)?;
                    repo_dict.set_item("updated_at", &repo_info.updated_at)?;
                    repo_dict.set_item("language", &repo_info.language)?;
                    repo_dict.set_item("fork", repo_info.fork)?;
                    repo_dict.set_item("forks_count", repo_info.forks_count)?;
                    repo_dict.set_item("stargazers_count", &repo_info.stargazers_count)?;
                    repo_dict.set_item("provider_type", format!("{}", repo_info.provider_type))?;
                    repo_dict.set_item("visibility", &repo_info.visibility)?;
                    
                    // Owner info as nested dict
                    let owner_dict = PyDict::new(py);
                    owner_dict.set_item("id", &repo_info.owner.id)?;
                    owner_dict.set_item("login", &repo_info.owner.login)?;
                    owner_dict.set_item("name", &repo_info.owner.name)?;
                    owner_dict.set_item("email", &repo_info.owner.email)?;
                    owner_dict.set_item("avatar_url", &repo_info.owner.avatar_url)?;
                    repo_dict.set_item("owner", owner_dict)?;
                    
                    py_repos.append(repo_dict)?;
                }
                Ok(py_repos.into())
            })
        })
    }

    /// Fetches information about the authenticated user
    #[pyo3(name = "fetch_user_info")]
    fn fetch_user_info<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.fetch_user_info().await?;
            
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let user_dict = PyDict::new(py);
                user_dict.set_item("id", &result.id)?;
                user_dict.set_item("login", &result.login)?;
                user_dict.set_item("name", &result.name)?;
                user_dict.set_item("email", &result.email)?;
                user_dict.set_item("avatar_url", &result.avatar_url)?;
                user_dict.set_item("provider_type", format!("{}", result.provider_type))?;
                Ok(user_dict.into())
            })
        })
    }

    /// Gets current rate limit information
    #[pyo3(name = "get_rate_limit")]
    fn get_rate_limit<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.get_rate_limit().await?;
            
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let limit_dict = PyDict::new(py);
                limit_dict.set_item("limit", result.limit)?;
                limit_dict.set_item("remaining", result.remaining)?;
                limit_dict.set_item("reset_time", result.reset_time)?;
                limit_dict.set_item("used", result.used)?;
                limit_dict.set_item("provider_type", format!("{}", result.provider_type))?;
                Ok(limit_dict.into())
            })
        })
    }

    /// Fetches detailed information about a specific repository
    #[pyo3(name = "fetch_repository_details")]
    fn fetch_repository_details<'py>(
        &self,
        py: Python<'py>,
        owner: String,
        repo: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.fetch_repository_details(&owner, &repo).await?;
            
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let repo_dict = PyDict::new(py);
                
                // Basic info
                repo_dict.set_item("name", &result.basic_info.name)?;
                repo_dict.set_item("full_name", &result.basic_info.full_name)?;
                repo_dict.set_item("clone_url", &result.basic_info.clone_url)?;
                repo_dict.set_item("description", &result.basic_info.description)?;
                repo_dict.set_item("default_branch", &result.basic_info.default_branch)?;
                repo_dict.set_item("created_at", &result.basic_info.created_at)?;
                repo_dict.set_item("updated_at", &result.basic_info.updated_at)?;
                repo_dict.set_item("language", &result.basic_info.language)?;
                repo_dict.set_item("fork", result.basic_info.fork)?;
                repo_dict.set_item("forks_count", result.basic_info.forks_count)?;
                repo_dict.set_item("stargazers_count", &result.basic_info.stargazers_count)?;
                repo_dict.set_item("provider_type", format!("{}", result.provider_type))?;
                repo_dict.set_item("visibility", &result.basic_info.visibility)?;
                
                // Owner info as nested dict
                let owner_dict = PyDict::new(py);
                owner_dict.set_item("id", &result.basic_info.owner.id)?;
                owner_dict.set_item("login", &result.basic_info.owner.login)?;
                owner_dict.set_item("name", &result.basic_info.owner.name)?;
                owner_dict.set_item("email", &result.basic_info.owner.email)?;
                owner_dict.set_item("avatar_url", &result.basic_info.owner.avatar_url)?;
                repo_dict.set_item("owner", owner_dict)?;
                
                // Additional detailed info
                let topics = PyList::new(py, &result.topics);
                repo_dict.set_item("topics", topics)?;
                repo_dict.set_item("license", &result.license)?;
                repo_dict.set_item("homepage", &result.homepage)?;
                repo_dict.set_item("has_wiki", result.has_wiki)?;
                repo_dict.set_item("has_issues", result.has_issues)?;
                repo_dict.set_item("has_projects", result.has_projects)?;
                repo_dict.set_item("archived", result.archived)?;
                repo_dict.set_item("pushed_at", &result.pushed_at)?;
                repo_dict.set_item("size", result.size)?;
                
                Ok(repo_dict.into())
            })
        })
    }

    /// Fetches contributors for a repository
    #[pyo3(name = "fetch_contributors")]
    fn fetch_contributors<'py>(
        &self,
        py: Python<'py>,
        owner: String,
        repo: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.fetch_contributors(&owner, &repo).await?;
            
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let contributors_list = PyList::empty(py);
                
                for contributor in result {
                    let contributor_dict = PyDict::new(py);
                    contributor_dict.set_item("login", &contributor.login)?;
                    contributor_dict.set_item("id", &contributor.id)?;
                    contributor_dict.set_item("avatar_url", &contributor.avatar_url)?;
                    contributor_dict.set_item("contributions", contributor.contributions)?;
                    contributor_dict.set_item("provider_type", format!("{}", contributor.provider_type))?;
                    
                    contributors_list.append(contributor_dict)?;
                }
                
                Ok(contributors_list.into())
            })
        })
    }

    /// Fetches branches for a repository
    #[pyo3(name = "fetch_branches")]
    fn fetch_branches<'py>(
        &self,
        py: Python<'py>,
        owner: String,
        repo: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.fetch_branches(&owner, &repo).await?;
            
            Python::with_gil(|py| -> PyResult<Py<PyAny>> {
                let branches_list = PyList::empty(py);
                
                for branch in result {
                    let branch_dict = PyDict::new(py);
                    branch_dict.set_item("name", &branch.name)?;
                    branch_dict.set_item("commit_sha", &branch.commit_sha)?;
                    branch_dict.set_item("protected", branch.protected)?;
                    branch_dict.set_item("provider_type", format!("{}", branch.provider_type))?;
                    
                    branches_list.append(branch_dict)?;
                }
                
                Ok(branches_list.into())
            })
        })
    }

    /// Checks if the current token/credentials are valid
    #[pyo3(name = "validate_credentials")]
    fn validate_credentials<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let inner = Arc::clone(&self.inner);
        tokio::future_into_py(py, async move {
            let result = inner.validate_credentials().await?;
            Python::with_gil(|py| Ok(result.into_py(py)))
        })
    }
}

// --- Python module definition ---
#[allow(non_snake_case)]
#[pymodule]
fn GitFleet(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<RepoManager>()?;
    m.add_class::<ExposedCloneStatus>()?;
    m.add_class::<ExposedCloneTask>()?;
    m.add_class::<ExposedGitHubClient>()?;
    Ok(())
}
