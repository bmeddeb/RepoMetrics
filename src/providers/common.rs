/*
 * Common Git Provider Types and Traits
 *
 * This module defines the common interface and data types for all Git providers.
 */

use std::fmt;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};

/// Enumeration of supported Git provider types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Deserialize, Serialize)]
pub enum ProviderType {
    GitHub,
    GitLab,
    BitBucket,
}

impl fmt::Display for ProviderType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ProviderType::GitHub => write!(f, "GitHub"),
            ProviderType::GitLab => write!(f, "GitLab"),
            ProviderType::BitBucket => write!(f, "BitBucket"),
        }
    }
}

/// Provider-specific errors
#[derive(Debug, Clone)]
pub enum ProviderError {
    /// Authentication failed (invalid token, credentials, etc.)
    AuthError(String),
    /// Request failed due to rate limiting
    RateLimitExceeded { reset_time: u64 },
    /// Resource not found
    NotFound(String),
    /// API request failed
    RequestFailed(String),
    /// Response parsing failed
    ParseError(String),
    /// General provider error
    Other(String),
}

impl fmt::Display for ProviderError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ProviderError::AuthError(msg) => write!(f, "Authentication error: {}", msg),
            ProviderError::RateLimitExceeded { reset_time } => {
                write!(f, "Rate limit exceeded. Resets at timestamp: {}", reset_time)
            }
            ProviderError::NotFound(resource) => write!(f, "Resource not found: {}", resource),
            ProviderError::RequestFailed(msg) => write!(f, "Request failed: {}", msg),
            ProviderError::ParseError(msg) => write!(f, "Failed to parse response: {}", msg),
            ProviderError::Other(msg) => write!(f, "Provider error: {}", msg),
        }
    }
}

/// Common repository information returned by all providers
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RepoInfo {
    pub name: String,
    pub full_name: String,
    pub clone_url: String,
    pub description: Option<String>,
    pub default_branch: String,
    pub created_at: String,
    pub updated_at: String,
    pub language: Option<String>,
    pub fork: bool,
    pub forks_count: u32,
    pub stargazers_count: Option<u32>,
    pub provider_type: ProviderType,
    pub visibility: String,
    pub owner: UserInfo,
    // Raw provider-specific data for advanced use cases
    #[serde(skip_serializing, skip_deserializing)]
    pub raw_data: Option<serde_json::Value>,
}

/// User information returned by providers
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct UserInfo {
    pub id: String,
    pub login: String,
    pub name: Option<String>,
    pub email: Option<String>,
    pub avatar_url: Option<String>,
    pub provider_type: ProviderType,
    // Raw provider-specific data
    #[serde(skip_serializing, skip_deserializing)]
    pub raw_data: Option<serde_json::Value>,
}

/// Rate limit information from providers
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RateLimitInfo {
    pub limit: u32,
    pub remaining: u32,
    pub reset_time: u64,
    pub used: u32,
    pub provider_type: ProviderType,
}

/// Detailed repository information
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RepoDetails {
    pub basic_info: RepoInfo,
    pub topics: Vec<String>,
    pub license: Option<String>,
    pub homepage: Option<String>,
    pub has_wiki: bool,
    pub has_issues: bool,
    pub has_projects: bool,
    pub archived: bool,
    pub pushed_at: Option<String>,
    pub size: u64,
    pub provider_type: ProviderType,
    // Raw provider-specific data
    #[serde(skip_serializing, skip_deserializing)]
    pub raw_data: Option<serde_json::Value>,
}

/// Contributor information
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ContributorInfo {
    pub login: String,
    pub id: String,
    pub avatar_url: Option<String>,
    pub contributions: u32,
    pub provider_type: ProviderType,
}

/// Branch information
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct BranchInfo {
    pub name: String,
    pub commit_sha: String,
    pub protected: bool,
    pub provider_type: ProviderType,
}

/// Common trait that all Git providers must implement
#[async_trait]
pub trait GitProvider: Send + Sync {
    /// Returns the type of this provider
    fn provider_type(&self) -> ProviderType;
    
    /// Returns the base URL for this provider
    fn base_url(&self) -> &str;
    
    /// Fetch repositories for the specified owner/organization
    async fn fetch_repositories(&self, owner: &str) -> Result<Vec<RepoInfo>, ProviderError>;
    
    /// Fetch information about the authenticated user
    async fn fetch_user_info(&self) -> Result<UserInfo, ProviderError>;
    
    /// Get current rate limit information
    async fn get_rate_limit(&self) -> Result<RateLimitInfo, ProviderError>;
    
    /// Fetch detailed information about a specific repository
    async fn fetch_repository_details(&self, owner: &str, repo: &str) -> Result<RepoDetails, ProviderError>;
    
    /// Fetch contributors for a repository
    async fn fetch_contributors(&self, owner: &str, repo: &str) -> Result<Vec<ContributorInfo>, ProviderError>;
    
    /// Fetch branches for a repository
    async fn fetch_branches(&self, owner: &str, repo: &str) -> Result<Vec<BranchInfo>, ProviderError>;
    
    /// Check if the current token/credentials are valid
    async fn validate_credentials(&self) -> Result<bool, ProviderError>;
}