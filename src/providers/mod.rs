/*
 * Git Provider API Module
 *
 * This module contains implementations for different Git provider APIs
 * (GitHub, GitLab, BitBucket) along with common traits and data types.
 */

// Re-export provider modules
pub mod common;
pub mod github;
// These will be uncommented as we implement them
// pub mod gitlab;
// pub mod bitbucket;

// Re-export common types for easier access
pub use common::{GitProvider, ProviderError, ProviderType, RepoInfo, UserInfo, RateLimitInfo, RepoDetails};
pub use github::GitHubProvider;