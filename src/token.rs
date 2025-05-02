/*
 * Token Management Module
 *
 * This module handles authentication tokens for Git providers,
 * including rotation, rate limit tracking, and fallback logic.
 */

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use crate::providers::{ProviderType, RateLimitInfo};

/// Token status categorizes a token's current usability
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TokenStatus {
    /// Token is available for use
    Available,
    /// Token has exceeded its rate limit
    RateLimited { reset_time: u64 },
    /// Token has been revoked or is invalid
    Invalid,
}

/// Information about a provider authentication token
#[derive(Debug, Clone)]
pub struct TokenInfo {
    /// The actual token string (never expose in logs)
    pub token: String,
    /// The provider this token is for
    pub provider: ProviderType,
    /// Optional username associated with this token
    pub username: Option<String>,
    /// Current rate limit information
    pub rate_limit: Option<RateLimitInfo>,
    /// Current status of this token
    pub status: TokenStatus,
    /// Last time this token was used
    pub last_used: u64,
}

impl TokenInfo {
    /// Create a new token info
    pub fn new(token: String, provider: ProviderType, username: Option<String>) -> Self {
        Self {
            token,
            provider,
            username,
            rate_limit: None,
            status: TokenStatus::Available,
            last_used: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or(Duration::from_secs(0))
                .as_secs(),
        }
    }

    /// Check if this token is currently available for use
    pub fn is_available(&self) -> bool {
        match self.status {
            TokenStatus::Available => true,
            TokenStatus::RateLimited { reset_time } => {
                let current_time = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or(Duration::from_secs(0))
                    .as_secs();
                current_time >= reset_time
            }
            TokenStatus::Invalid => false,
        }
    }

    /// Update rate limit information for this token
    pub fn update_rate_limit(&mut self, rate_limit: RateLimitInfo) {
        self.rate_limit = Some(rate_limit);
        
        // If no requests remaining, mark as rate limited
        if rate_limit.remaining == 0 {
            self.status = TokenStatus::RateLimited {
                reset_time: rate_limit.reset_time,
            };
        } else {
            // Otherwise ensure it's marked as available
            if let TokenStatus::RateLimited { .. } = self.status {
                self.status = TokenStatus::Available;
            }
        }
    }

    /// Mark this token as used
    pub fn mark_used(&mut self) {
        self.last_used = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or(Duration::from_secs(0))
            .as_secs();
    }

    /// Mark this token as invalid
    pub fn mark_invalid(&mut self) {
        self.status = TokenStatus::Invalid;
    }
}

/// Multi-token manager with rate limit handling
#[derive(Clone)]
pub struct TokenManager {
    /// Tokens by provider type
    tokens: Arc<Mutex<HashMap<ProviderType, Vec<TokenInfo>>>>,
    /// Current index for each provider (for round-robin)
    current_indices: Arc<Mutex<HashMap<ProviderType, usize>>>,
}

impl TokenManager {
    /// Create a new token manager
    pub fn new() -> Self {
        Self {
            tokens: Arc::new(Mutex::new(HashMap::new())),
            current_indices: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Add a token to the manager
    pub fn add_token(&self, token: String, provider: ProviderType, username: Option<String>) {
        let token_info = TokenInfo::new(token, provider, username);
        
        let mut tokens = self.tokens.lock().unwrap();
        tokens.entry(provider).or_insert_with(Vec::new).push(token_info);
    }

    /// Add multiple tokens at once
    pub fn add_tokens(&self, tokens: Vec<(String, ProviderType, Option<String>)>) {
        let mut tokens_map = self.tokens.lock().unwrap();
        
        for (token, provider, username) in tokens {
            let token_info = TokenInfo::new(token, provider, username);
            tokens_map.entry(provider).or_insert_with(Vec::new).push(token_info);
        }
    }

    /// Get the next available token for a provider using round-robin with rate limit awareness
    pub fn get_next_available_token(&self, provider: ProviderType) -> Option<TokenInfo> {
        let mut tokens = self.tokens.lock().unwrap();
        let mut indices = self.current_indices.lock().unwrap();
        
        let provider_tokens = tokens.get_mut(&provider)?;
        
        if provider_tokens.is_empty() {
            return None;
        }
        
        // Get current index for this provider
        let current_index = *indices.entry(provider).or_insert(0);
        let num_tokens = provider_tokens.len();
        
        // Try to find an available token starting from the current index
        for i in 0..num_tokens {
            let index = (current_index + i) % num_tokens;
            let token = &mut provider_tokens[index];
            
            if token.is_available() {
                // Update the index for next time
                *indices.entry(provider).or_insert(0) = (index + 1) % num_tokens;
                
                // Mark the token as used
                token.mark_used();
                
                return Some(token.clone());
            }
        }
        
        // No available tokens found
        None
    }

    /// Update rate limit information for a token
    pub fn update_rate_limit(&self, token: &str, provider: ProviderType, rate_limit: RateLimitInfo) {
        let mut tokens = self.tokens.lock().unwrap();
        
        if let Some(provider_tokens) = tokens.get_mut(&provider) {
            for token_info in provider_tokens.iter_mut() {
                if token_info.token == token {
                    token_info.update_rate_limit(rate_limit);
                    break;
                }
            }
        }
    }

    /// Mark a token as invalid
    pub fn mark_token_invalid(&self, token: &str, provider: ProviderType) {
        let mut tokens = self.tokens.lock().unwrap();
        
        if let Some(provider_tokens) = tokens.get_mut(&provider) {
            for token_info in provider_tokens.iter_mut() {
                if token_info.token == token {
                    token_info.mark_invalid();
                    break;
                }
            }
        }
    }

    /// Get all tokens for a provider
    pub fn get_all_tokens(&self, provider: ProviderType) -> Vec<TokenInfo> {
        let tokens = self.tokens.lock().unwrap();
        
        tokens
            .get(&provider)
            .cloned()
            .unwrap_or_else(Vec::new)
    }

    /// Get count of available tokens for a provider
    pub fn count_available_tokens(&self, provider: ProviderType) -> usize {
        let tokens = self.tokens.lock().unwrap();
        
        tokens
            .get(&provider)
            .map(|provider_tokens| {
                provider_tokens.iter().filter(|t| t.is_available()).count()
            })
            .unwrap_or(0)
    }
}