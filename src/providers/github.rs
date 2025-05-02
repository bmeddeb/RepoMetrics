/*
 * GitHub API Client Implementation
 */

use async_trait::async_trait;
use reqwest::{Client, header};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::providers::common::{
    BranchInfo, ContributorInfo, GitProvider, ProviderError, ProviderType,
    RateLimitInfo, RepoDetails, RepoInfo, UserInfo,
};

/// GitHub API client implementation
pub struct GitHubProvider {
    /// HTTP client for API requests
    client: Client,
    /// Authentication token
    token: String,
    /// Base URL for GitHub API (allows GitHub Enterprise support)
    base_url: String,
}

// Basic GitHub repository response structure
#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubRepo {
    pub id: u64,
    pub name: String,
    pub full_name: String,
    pub private: bool,
    pub html_url: String,
    pub description: Option<String>,
    pub fork: bool,
    pub url: String,
    pub clone_url: String,
    pub default_branch: String,
    pub created_at: String,
    pub updated_at: String,
    pub pushed_at: Option<String>,
    pub language: Option<String>,
    pub forks_count: u32,
    pub stargazers_count: u32,
    pub owner: GitHubUser,
    pub topics: Option<Vec<String>>,
    pub visibility: Option<String>,
    pub archived: Option<bool>,
    pub license: Option<GitHubLicense>,
    pub has_issues: Option<bool>,
    pub has_wiki: Option<bool>,
    pub has_projects: Option<bool>,
    pub size: Option<u64>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubUser {
    pub login: String,
    pub id: u64,
    pub avatar_url: String,
    pub url: String,
    pub html_url: String,
    pub type_field: Option<String>,
    #[serde(rename = "type")]
    pub user_type: Option<String>,
    pub site_admin: Option<bool>,
    pub name: Option<String>,
    pub email: Option<String>,
    pub company: Option<String>,
    pub location: Option<String>,
    pub bio: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubRateLimit {
    pub resources: GitHubRateLimitResources,
    pub rate: GitHubRateLimitRate,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubRateLimitResources {
    pub core: GitHubRateLimitRate,
    pub search: GitHubRateLimitRate,
    pub graphql: GitHubRateLimitRate,
    pub integration_manifest: Option<GitHubRateLimitRate>,
    pub code_scanning_upload: Option<GitHubRateLimitRate>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubRateLimitRate {
    pub limit: u32,
    pub used: u32,
    pub remaining: u32,
    pub reset: u64,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubLicense {
    pub key: String,
    pub name: String,
    pub spdx_id: Option<String>,
    pub url: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubBranch {
    pub name: String,
    pub commit: GitHubCommitRef,
    pub protected: bool,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubCommitRef {
    pub sha: String,
    pub url: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct GitHubContributor {
    pub login: String,
    pub id: u64,
    pub avatar_url: String,
    pub contributions: u32,
    pub type_field: Option<String>,
    #[serde(rename = "type")]
    pub user_type: Option<String>,
}

impl GitHubProvider {
    /// Create a new GitHub provider
    pub fn new(token: String, base_url: Option<String>) -> Self {
        // Set up headers with auth token
        let mut headers = header::HeaderMap::new();
        headers.insert(
            header::ACCEPT,
            header::HeaderValue::from_static("application/vnd.github.v3+json"),
        );
        headers.insert(
            header::USER_AGENT,
            header::HeaderValue::from_static("GitFleet-Library"),
        );

        let client = Client::builder()
            .default_headers(headers)
            .build()
            .unwrap_or_default();

        Self {
            client,
            token,
            base_url: base_url.unwrap_or_else(|| "https://api.github.com".to_string()),
        }
    }

    /// Extract rate limit information from response headers
    fn extract_rate_limit_from_headers(
        &self,
        headers: &header::HeaderMap,
    ) -> Option<RateLimitInfo> {
        let limit = headers
            .get("x-ratelimit-limit")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u32>().ok());

        let remaining = headers
            .get("x-ratelimit-remaining")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u32>().ok());

        let reset = headers
            .get("x-ratelimit-reset")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u64>().ok());

        let used = headers
            .get("x-ratelimit-used")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u32>().ok());

        if let (Some(limit), Some(remaining), Some(reset)) = (limit, remaining, reset) {
            Some(RateLimitInfo {
                limit,
                remaining,
                reset_time: reset,
                used: used.unwrap_or(limit - remaining),
                provider_type: ProviderType::GitHub,
            })
        } else {
            None
        }
    }

    /// Check if an error is due to rate limiting
    fn is_rate_limit_error(&self, status: reqwest::StatusCode, body: &Value) -> Option<u64> {
        if status == reqwest::StatusCode::FORBIDDEN {
            // Check for rate limit messages in the response
            if let Some(message) = body.get("message").and_then(|m| m.as_str()) {
                if message.contains("rate limit") || message.contains("API rate limit exceeded") {
                    // Try to get reset time from the response
                    if let Some(reset) = body
                        .get("resources")
                        .and_then(|r| r.get("core"))
                        .and_then(|c| c.get("reset"))
                        .and_then(|t| t.as_u64())
                    {
                        return Some(reset);
                    }
                    
                    // Fallback to current time + 1 hour
                    return Some(
                        SystemTime::now()
                            .duration_since(UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs()
                            + 3600,
                    );
                }
            }
        }
        None
    }

    /// Convert GitHub repo to common RepoInfo
    fn convert_repo(&self, repo: GitHubRepo) -> RepoInfo {
        RepoInfo {
            name: repo.name,
            full_name: repo.full_name,
            clone_url: repo.clone_url,
            description: repo.description,
            default_branch: repo.default_branch,
            created_at: repo.created_at,
            updated_at: repo.updated_at,
            language: repo.language,
            fork: repo.fork,
            forks_count: repo.forks_count,
            stargazers_count: Some(repo.stargazers_count),
            provider_type: ProviderType::GitHub,
            visibility: repo.visibility.unwrap_or_else(|| {
                if repo.private {
                    "private".to_string()
                } else {
                    "public".to_string()
                }
            }),
            owner: UserInfo {
                id: repo.owner.id.to_string(),
                login: repo.owner.login,
                name: repo.owner.name,
                email: repo.owner.email,
                avatar_url: Some(repo.owner.avatar_url),
                provider_type: ProviderType::GitHub,
                raw_data: Some(serde_json::to_value(&repo.owner).ok()?),
            },
            raw_data: Some(serde_json::to_value(&repo).ok()?),
        }
    }

    /// Convert GitHub repo to detailed RepoDetails
    fn convert_repo_details(&self, repo: GitHubRepo) -> RepoDetails {
        let repo_info = self.convert_repo(repo.clone());
        
        RepoDetails {
            basic_info: repo_info,
            topics: repo.topics.unwrap_or_default(),
            license: repo.license.map(|l| l.name),
            homepage: None, // Not in the basic model, would be added with full details
            has_wiki: repo.has_wiki.unwrap_or(false),
            has_issues: repo.has_issues.unwrap_or(false),
            has_projects: repo.has_projects.unwrap_or(false),
            archived: repo.archived.unwrap_or(false),
            pushed_at: repo.pushed_at,
            size: repo.size.unwrap_or(0),
            provider_type: ProviderType::GitHub,
            raw_data: serde_json::to_value(&repo).ok(),
        }
    }
}

#[async_trait]
impl GitProvider for GitHubProvider {
    fn provider_type(&self) -> ProviderType {
        ProviderType::GitHub
    }
    
    fn base_url(&self) -> &str {
        &self.base_url
    }
    
    async fn fetch_repositories(&self, owner: &str) -> Result<Vec<RepoInfo>, ProviderError> {
        let url = format!("{}/users/{}/repos?per_page=100", self.base_url, owner);
        
        let response = self.client
            .get(&url)
            .header(header::AUTHORIZATION, format!("token {}", self.token))
            .send()
            .await
            .map_err(|e| ProviderError::RequestFailed(format!("Failed to fetch repositories: {}", e)))?;
        
        let status = response.status();
        let headers = response.headers().clone();
        
        // Check for rate limit headers
        if let Some(rate_limit) = self.extract_rate_limit_from_headers(&headers) {
            if rate_limit.remaining == 0 {
                return Err(ProviderError::RateLimitExceeded {
                    reset_time: rate_limit.reset_time,
                });
            }
        }
        
        // Handle HTTP errors
        if !status.is_success() {
            let body: Value = response
                .json()
                .await
                .unwrap_or_else(|_| Value::Object(serde_json::Map::new()));
            
            // Check if this is a rate limit error
            if let Some(reset_time) = self.is_rate_limit_error(status, &body) {
                return Err(ProviderError::RateLimitExceeded { reset_time });
            }
            
            // Other errors
            match status.as_u16() {
                401 => return Err(ProviderError::AuthError("Invalid GitHub token".to_string())),
                404 => return Err(ProviderError::NotFound(format!("User '{}' not found", owner))),
                _ => {
                    let message = body
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown error")
                        .to_string();
                    return Err(ProviderError::RequestFailed(format!(
                        "GitHub API error ({}): {}",
                        status.as_u16(),
                        message
                    )));
                }
            }
        }
        
        // Parse the successful response
        let repos: Vec<GitHubRepo> = response
            .json()
            .await
            .map_err(|e| ProviderError::ParseError(format!("Failed to parse GitHub response: {}", e)))?;
        
        // Convert to common format
        Ok(repos
            .into_iter()
            .map(|repo| self.convert_repo(repo))
            .collect())
    }
    
    async fn fetch_user_info(&self) -> Result<UserInfo, ProviderError> {
        let url = format!("{}/user", self.base_url);
        
        let response = self.client
            .get(&url)
            .header(header::AUTHORIZATION, format!("token {}", self.token))
            .send()
            .await
            .map_err(|e| ProviderError::RequestFailed(format!("Failed to fetch user info: {}", e)))?;
        
        let status = response.status();
        let headers = response.headers().clone();
        
        // Handle HTTP errors
        if !status.is_success() {
            let body: Value = response
                .json()
                .await
                .unwrap_or_else(|_| Value::Object(serde_json::Map::new()));
            
            // Check if this is a rate limit error
            if let Some(reset_time) = self.is_rate_limit_error(status, &body) {
                return Err(ProviderError::RateLimitExceeded { reset_time });
            }
            
            // Other errors
            match status.as_u16() {
                401 => return Err(ProviderError::AuthError("Invalid GitHub token".to_string())),
                _ => {
                    let message = body
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown error")
                        .to_string();
                    return Err(ProviderError::RequestFailed(format!(
                        "GitHub API error ({}): {}",
                        status.as_u16(),
                        message
                    )));
                }
            }
        }
        
        // Parse the successful response
        let user: GitHubUser = response
            .json()
            .await
            .map_err(|e| ProviderError::ParseError(format!("Failed to parse GitHub user response: {}", e)))?;
        
        // Convert to common format
        Ok(UserInfo {
            id: user.id.to_string(),
            login: user.login,
            name: user.name,
            email: user.email,
            avatar_url: Some(user.avatar_url),
            provider_type: ProviderType::GitHub,
            raw_data: serde_json::to_value(&user).ok(),
        })
    }
    
    async fn get_rate_limit(&self) -> Result<RateLimitInfo, ProviderError> {
        let url = format!("{}/rate_limit", self.base_url);
        
        let response = self.client
            .get(&url)
            .header(header::AUTHORIZATION, format!("token {}", self.token))
            .send()
            .await
            .map_err(|e| ProviderError::RequestFailed(format!("Failed to fetch rate limit: {}", e)))?;
        
        let status = response.status();
        
        // Handle HTTP errors
        if !status.is_success() {
            let body: Value = response
                .json()
                .await
                .unwrap_or_else(|_| Value::Object(serde_json::Map::new()));
            
            // Other errors
            match status.as_u16() {
                401 => return Err(ProviderError::AuthError("Invalid GitHub token".to_string())),
                _ => {
                    let message = body
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown error")
                        .to_string();
                    return Err(ProviderError::RequestFailed(format!(
                        "GitHub API error ({}): {}",
                        status.as_u16(),
                        message
                    )));
                }
            }
        }
        
        // Parse the successful response
        let rate_limit: GitHubRateLimit = response
            .json()
            .await
            .map_err(|e| ProviderError::ParseError(format!("Failed to parse GitHub rate limit response: {}", e)))?;
        
        // Convert to common format (using core limits)
        Ok(RateLimitInfo {
            limit: rate_limit.resources.core.limit,
            remaining: rate_limit.resources.core.remaining,
            reset_time: rate_limit.resources.core.reset,
            used: rate_limit.resources.core.used,
            provider_type: ProviderType::GitHub,
        })
    }
    
    async fn fetch_repository_details(&self, owner: &str, repo: &str) -> Result<RepoDetails, ProviderError> {
        let url = format!("{}/repos/{}/{}", self.base_url, owner, repo);
        
        let response = self.client
            .get(&url)
            .header(header::AUTHORIZATION, format!("token {}", self.token))
            .send()
            .await
            .map_err(|e| ProviderError::RequestFailed(format!("Failed to fetch repository details: {}", e)))?;
        
        let status = response.status();
        let headers = response.headers().clone();
        
        // Handle HTTP errors
        if !status.is_success() {
            let body: Value = response
                .json()
                .await
                .unwrap_or_else(|_| Value::Object(serde_json::Map::new()));
            
            // Check if this is a rate limit error
            if let Some(reset_time) = self.is_rate_limit_error(status, &body) {
                return Err(ProviderError::RateLimitExceeded { reset_time });
            }
            
            // Other errors
            match status.as_u16() {
                401 => return Err(ProviderError::AuthError("Invalid GitHub token".to_string())),
                404 => return Err(ProviderError::NotFound(format!("Repository '{}/{}' not found", owner, repo))),
                _ => {
                    let message = body
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown error")
                        .to_string();
                    return Err(ProviderError::RequestFailed(format!(
                        "GitHub API error ({}): {}",
                        status.as_u16(),
                        message
                    )));
                }
            }
        }
        
        // Parse the successful response
        let repo_data: GitHubRepo = response
            .json()
            .await
            .map_err(|e| ProviderError::ParseError(format!("Failed to parse GitHub repo response: {}", e)))?;
        
        // Convert to detailed format
        Ok(self.convert_repo_details(repo_data))
    }
    
    async fn fetch_contributors(&self, owner: &str, repo: &str) -> Result<Vec<ContributorInfo>, ProviderError> {
        let url = format!("{}/repos/{}/{}/contributors", self.base_url, owner, repo);
        
        let response = self.client
            .get(&url)
            .header(header::AUTHORIZATION, format!("token {}", self.token))
            .send()
            .await
            .map_err(|e| ProviderError::RequestFailed(format!("Failed to fetch contributors: {}", e)))?;
        
        let status = response.status();
        
        // Handle HTTP errors
        if !status.is_success() {
            let body: Value = response
                .json()
                .await
                .unwrap_or_else(|_| Value::Object(serde_json::Map::new()));
            
            // Check if this is a rate limit error
            if let Some(reset_time) = self.is_rate_limit_error(status, &body) {
                return Err(ProviderError::RateLimitExceeded { reset_time });
            }
            
            // Other errors
            match status.as_u16() {
                401 => return Err(ProviderError::AuthError("Invalid GitHub token".to_string())),
                404 => return Err(ProviderError::NotFound(format!("Repository '{}/{}' not found", owner, repo))),
                _ => {
                    let message = body
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown error")
                        .to_string();
                    return Err(ProviderError::RequestFailed(format!(
                        "GitHub API error ({}): {}",
                        status.as_u16(),
                        message
                    )));
                }
            }
        }
        
        // Parse the successful response
        let contributors: Vec<GitHubContributor> = response
            .json()
            .await
            .map_err(|e| ProviderError::ParseError(format!("Failed to parse GitHub contributors response: {}", e)))?;
        
        // Convert to common format
        Ok(contributors
            .into_iter()
            .map(|c| ContributorInfo {
                login: c.login,
                id: c.id.to_string(),
                avatar_url: Some(c.avatar_url),
                contributions: c.contributions,
                provider_type: ProviderType::GitHub,
            })
            .collect())
    }
    
    async fn fetch_branches(&self, owner: &str, repo: &str) -> Result<Vec<BranchInfo>, ProviderError> {
        let url = format!("{}/repos/{}/{}/branches", self.base_url, owner, repo);
        
        let response = self.client
            .get(&url)
            .header(header::AUTHORIZATION, format!("token {}", self.token))
            .send()
            .await
            .map_err(|e| ProviderError::RequestFailed(format!("Failed to fetch branches: {}", e)))?;
        
        let status = response.status();
        
        // Handle HTTP errors
        if !status.is_success() {
            let body: Value = response
                .json()
                .await
                .unwrap_or_else(|_| Value::Object(serde_json::Map::new()));
            
            // Check if this is a rate limit error
            if let Some(reset_time) = self.is_rate_limit_error(status, &body) {
                return Err(ProviderError::RateLimitExceeded { reset_time });
            }
            
            // Other errors
            match status.as_u16() {
                401 => return Err(ProviderError::AuthError("Invalid GitHub token".to_string())),
                404 => return Err(ProviderError::NotFound(format!("Repository '{}/{}' not found", owner, repo))),
                _ => {
                    let message = body
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown error")
                        .to_string();
                    return Err(ProviderError::RequestFailed(format!(
                        "GitHub API error ({}): {}",
                        status.as_u16(),
                        message
                    )));
                }
            }
        }
        
        // Parse the successful response
        let branches: Vec<GitHubBranch> = response
            .json()
            .await
            .map_err(|e| ProviderError::ParseError(format!("Failed to parse GitHub branches response: {}", e)))?;
        
        // Convert to common format
        Ok(branches
            .into_iter()
            .map(|b| BranchInfo {
                name: b.name,
                commit_sha: b.commit.sha,
                protected: b.protected,
                provider_type: ProviderType::GitHub,
            })
            .collect())
    }
    
    async fn validate_credentials(&self) -> Result<bool, ProviderError> {
        // Simplest way to validate credentials is to try fetching user info
        match self.fetch_user_info().await {
            Ok(_) => Ok(true),
            Err(ProviderError::AuthError(_)) => Ok(false),
            Err(e) => Err(e),
        }
    }
}