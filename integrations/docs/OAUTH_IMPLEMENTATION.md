# OAuth Implementation Guide

## Universal OAuth 2.0 Implementation for Ainflue Integrations

**Author:** Fahed Mlaiel <mlaiel@live.de>  
**Copyright:** (c) 2025 Fahed Mlaiel. All rights reserved.

---

## Overview

The Ainflue OAuth Manager provides a comprehensive, secure, and scalable OAuth 2.0 implementation supporting multiple providers and flows. This guide covers implementation details, security considerations, and best practices.

## Supported OAuth Providers

### Social Media Platforms
- **Google/YouTube** - OAuth 2.0 with OIDC
- **Facebook/Instagram** - Facebook Login API
- **Twitter/X** - OAuth 2.0 with PKCE
- **LinkedIn** - OAuth 2.0 for professional networks
- **TikTok** - TikTok for Developers OAuth
- **Spotify** - Spotify Web API OAuth
- **Discord** - Discord OAuth2
- **Twitch** - Twitch API OAuth
- **Snapchat** - Snap Kit OAuth
- **Pinterest** - Pinterest API OAuth
- **Reddit** - Reddit OAuth2

### Cloud Providers
- **Microsoft Azure** - Azure AD OAuth
- **Google Cloud** - Google Cloud OAuth
- **AWS** - AWS Cognito OAuth
- **Salesforce** - Salesforce OAuth

## OAuth Flow Types

### 1. Authorization Code Flow (Most Common)

```python
# Step 1: Generate authorization URL
auth_url, state = await oauth_manager.get_authorization_url(
    provider=OAuthProvider.GOOGLE,
    integration_name="youtube",
    user_id="user123",
    scope=["https://www.googleapis.com/auth/youtube"]
)

# Step 2: Redirect user to authorization URL
# User authorizes and returns with code

# Step 3: Exchange code for tokens
session = await oauth_manager.exchange_code_for_token(
    code=authorization_code,
    state=state
)
```

### 2. Client Credentials Flow (Server-to-Server)

```python
# Configure client credentials
await oauth_manager.configure_provider(
    provider=OAuthProvider.CUSTOM,
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="https://api.example.com/oauth/callback"
)

# Get client credentials token
token_response = await oauth_manager.get_client_credentials_token(
    provider=OAuthProvider.CUSTOM,
    scope=["api.read", "api.write"]
)
```

### 3. Device Code Flow (For Limited Input Devices)

```python
# Initiate device flow
device_response = await oauth_manager.initiate_device_flow(
    provider=OAuthProvider.GOOGLE,
    scope=["https://www.googleapis.com/auth/youtube"]
)

# Display device code to user
print(f"Go to {device_response['verification_uri']} and enter: {device_response['user_code']}")

# Poll for authorization
session = await oauth_manager.poll_device_authorization(
    device_code=device_response['device_code'],
    interval=device_response['interval']
)
```

## Security Implementation

### State Parameter Security

```python
def _generate_state(self) -> str:
    """Generate cryptographically secure state parameter."""
    return secrets.token_urlsafe(32)

def _validate_and_consume_state(self, state: str) -> Optional[Dict[str, Any]]:
    """Validate state parameter and prevent replay attacks."""
    if state not in self.pending_states:
        return None
    
    state_info = self.pending_states[state]
    
    # Check expiration (10-minute window)
    if datetime.utcnow() > state_info["expires_at"]:
        del self.pending_states[state]
        return None
    
    # Consume state (single use)
    del self.pending_states[state]
    return state_info
```

### Token Encryption

```python
def _encrypt_token(self, token: str) -> str:
    """Encrypt OAuth tokens using Fernet symmetric encryption."""
    return self.cipher_suite.encrypt(token.encode()).decode()

def _decrypt_token(self, encrypted_token: str) -> str:
    """Decrypt OAuth tokens."""
    return self.cipher_suite.decrypt(encrypted_token.encode()).decode()
```

### PKCE Implementation (for Public Clients)

```python
import hashlib
import base64

def generate_pkce_challenge():
    """Generate PKCE code verifier and challenge."""
    # Generate code verifier
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    # Generate code challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge
```

## Provider-Specific Implementations

### Google OAuth 2.0 with OIDC

```python
GOOGLE_CONFIG = OAuthConfig(
    provider=OAuthProvider.GOOGLE,
    client_id="your-client-id.googleusercontent.com",
    client_secret="your-client-secret",
    authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
    token_url="https://oauth2.googleapis.com/token",
    refresh_url="https://oauth2.googleapis.com/token",
    user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
    scope=[
        "openid",
        "email", 
        "profile",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.upload"
    ],
    additional_params={
        "access_type": "offline",  # Get refresh token
        "prompt": "consent"        # Force consent screen
    }
)
```

### Facebook OAuth Implementation

```python
FACEBOOK_CONFIG = OAuthConfig(
    provider=OAuthProvider.FACEBOOK,
    client_id="your-facebook-app-id",
    client_secret="your-facebook-app-secret",
    authorization_url="https://www.facebook.com/v18.0/dialog/oauth",
    token_url="https://graph.facebook.com/v18.0/oauth/access_token",
    user_info_url="https://graph.facebook.com/v18.0/me",
    scope=[
        "email",
        "public_profile",
        "pages_manage_posts",
        "pages_read_engagement",
        "instagram_basic",
        "instagram_content_publish"
    ],
    additional_params={
        "response_type": "code"
    }
)
```

### Twitter OAuth 2.0 Implementation

```python
TWITTER_CONFIG = OAuthConfig(
    provider=OAuthProvider.TWITTER,
    client_id="your-twitter-client-id",
    client_secret="your-twitter-client-secret",
    authorization_url="https://twitter.com/i/oauth2/authorize",
    token_url="https://api.twitter.com/2/oauth2/token",
    refresh_url="https://api.twitter.com/2/oauth2/token",
    revoke_url="https://api.twitter.com/2/oauth2/revoke",
    user_info_url="https://api.twitter.com/2/users/me",
    scope=[
        "tweet.read",
        "tweet.write",
        "users.read",
        "follows.read",
        "follows.write"
    ],
    additional_params={
        "code_challenge_method": "S256"  # PKCE required
    }
)
```

## Token Management

### Automatic Token Refresh

```python
async def _auto_refresh_token(self, session_key: str) -> None:
    """Automatically refresh tokens before expiration."""
    while True:
        try:
            session = self.sessions.get(session_key)
            if not session:
                break
            
            # Calculate time until token expiration
            if session.token.expires_at:
                time_until_expiry = (
                    session.token.expires_at - datetime.utcnow()
                ).total_seconds()
                
                # Refresh 5 minutes before expiration
                sleep_time = max(time_until_expiry - 300, 60)
            else:
                sleep_time = 3600  # Default 1 hour
            
            await asyncio.sleep(sleep_time)
            
            # Perform token refresh
            new_token = await self.refresh_token(session_key)
            if not new_token:
                # Token refresh failed, remove session
                del self.sessions[session_key]
                break
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            self.logger.error(f"Auto-refresh error: {str(e)}")
            await asyncio.sleep(300)  # Retry in 5 minutes
```

### Token Validation

```python
async def validate_token(self, session_key: str) -> bool:
    """Validate OAuth token and refresh if necessary."""
    session = self.sessions.get(session_key)
    if not session:
        return False
    
    # Check if token is expired
    if self._is_token_expired(session.token):
        # Attempt refresh
        new_token = await self.refresh_token(session_key)
        if not new_token:
            # Clean up invalid session
            del self.sessions[session_key]
            return False
    
    # Optionally validate with provider
    if await self._validate_with_provider(session):
        return True
    
    return False
```

## Error Handling

### OAuth Error Types

```python
class OAuthError(Exception):
    """Base OAuth error."""
    pass

class InvalidGrantError(OAuthError):
    """Invalid authorization grant."""
    pass

class InvalidClientError(OAuthError):
    """Invalid client credentials."""
    pass

class InvalidScopeError(OAuthError):
    """Invalid or unauthorized scope."""
    pass

class AccessDeniedError(OAuthError):
    """User denied access."""
    pass

class ServerError(OAuthError):
    """Authorization server error."""
    pass
```

### Error Response Handling

```python
async def _handle_token_error(self, response: dict) -> None:
    """Handle OAuth token error responses."""
    error = response.get("error")
    error_description = response.get("error_description", "")
    
    error_mapping = {
        "invalid_grant": InvalidGrantError,
        "invalid_client": InvalidClientError,
        "invalid_scope": InvalidScopeError,
        "access_denied": AccessDeniedError,
        "server_error": ServerError,
        "temporarily_unavailable": ServerError
    }
    
    error_class = error_mapping.get(error, OAuthError)
    raise error_class(f"{error}: {error_description}")
```

## Best Practices

### 1. Scope Management

```python
# Minimal scope principle
MINIMAL_SCOPES = {
    "youtube": ["https://www.googleapis.com/auth/youtube.readonly"],
    "instagram": ["instagram_basic"],
    "twitter": ["tweet.read", "users.read"]
}

# Progressive scope requests
async def request_additional_scope(
    self, 
    session_key: str, 
    additional_scopes: List[str]
) -> bool:
    """Request additional OAuth scopes."""
    session = self.sessions.get(session_key)
    if not session:
        return False
    
    current_scopes = set(session.token.scope)
    new_scopes = current_scopes.union(set(additional_scopes))
    
    # Re-authorize with expanded scopes
    auth_url, state = await self.get_authorization_url(
        provider=session.provider,
        integration_name=session.integration_name,
        user_id=session.user_id,
        custom_scope=list(new_scopes)
    )
    
    return auth_url
```

### 2. Session Management

```python
async def cleanup_expired_sessions(self) -> int:
    """Clean up expired OAuth sessions."""
    cleaned_count = 0
    current_time = datetime.utcnow()
    
    expired_sessions = [
        key for key, session in self.sessions.items()
        if (session.token.expires_at and 
            current_time > session.token.expires_at and
            not session.token.refresh_token)
    ]
    
    for session_key in expired_sessions:
        await self.revoke_token(session_key)
        del self.sessions[session_key]
        cleaned_count += 1
    
    return cleaned_count
```

### 3. Rate Limiting OAuth Requests

```python
class OAuthRateLimiter:
    """Rate limiter for OAuth endpoints."""
    
    def __init__(self):
        self.request_counts = {}
        self.rate_limits = {
            "authorization": (10, 60),  # 10 requests per minute
            "token": (100, 3600),       # 100 requests per hour
            "refresh": (1000, 3600)     # 1000 refreshes per hour
        }
    
    async def check_rate_limit(self, endpoint: str, client_id: str) -> bool:
        """Check if request is within rate limits."""
        key = f"{endpoint}:{client_id}"
        current_time = time.time()
        
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        # Clean old requests
        max_requests, time_window = self.rate_limits[endpoint]
        cutoff_time = current_time - time_window
        
        self.request_counts[key] = [
            timestamp for timestamp in self.request_counts[key]
            if timestamp > cutoff_time
        ]
        
        # Check limit
        if len(self.request_counts[key]) >= max_requests:
            return False
        
        # Record request
        self.request_counts[key].append(current_time)
        return True
```

## Monitoring and Logging

### OAuth Event Logging

```python
async def _log_oauth_event(
    self,
    event_type: str,
    provider: str,
    user_id: str,
    success: bool,
    error: Optional[str] = None
) -> None:
    """Log OAuth events for monitoring and audit."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "provider": provider,
        "user_id": user_id,
        "success": success,
        "error": error,
        "ip_address": self._get_client_ip(),
        "user_agent": self._get_user_agent()
    }
    
    # Log to audit system
    await self.audit_logger.log("oauth_event", log_entry)
    
    # Send metrics
    await self.metrics.increment(
        "oauth.events",
        tags={
            "event_type": event_type,
            "provider": provider,
            "success": str(success)
        }
    )
```

### Performance Metrics

```python
class OAuthMetrics:
    """OAuth performance metrics collection."""
    
    async def record_authorization_flow(
        self,
        provider: str,
        duration: float,
        success: bool
    ) -> None:
        """Record authorization flow metrics."""
        await self.metrics.histogram(
            "oauth.authorization_duration",
            duration,
            tags={"provider": provider, "success": str(success)}
        )
    
    async def record_token_refresh(
        self,
        provider: str,
        duration: float,
        success: bool
    ) -> None:
        """Record token refresh metrics."""
        await self.metrics.histogram(
            "oauth.token_refresh_duration", 
            duration,
            tags={"provider": provider, "success": str(success)}
        )
```

## Testing OAuth Implementation

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestOAuthManager:
    
    @pytest.mark.asyncio
    async def test_authorization_url_generation(self):
        """Test OAuth authorization URL generation."""
        oauth_manager = OAuthManager()
        
        auth_url, state = await oauth_manager.get_authorization_url(
            provider=OAuthProvider.GOOGLE,
            integration_name="youtube",
            user_id="test_user"
        )
        
        assert "accounts.google.com" in auth_url
        assert "state=" in auth_url
        assert len(state) == 43  # Base64 encoded 32 bytes
    
    @pytest.mark.asyncio
    async def test_token_exchange(self):
        """Test authorization code to token exchange."""
        oauth_manager = OAuthManager()
        
        # Mock HTTP response
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
            mock_post.return_value = mock_response
            
            # Set up test state
            oauth_manager.pending_states["test_state"] = {
                "provider": OAuthProvider.GOOGLE,
                "integration_name": "youtube",
                "user_id": "test_user",
                "expires_at": datetime.utcnow() + timedelta(minutes=10)
            }
            
            session = await oauth_manager.exchange_code_for_token(
                code="test_code",
                state="test_state"
            )
            
            assert session is not None
            assert session.token.access_token == "test_token"
```

### Integration Tests

```python
@pytest.mark.integration
class TestOAuthIntegration:
    
    async def test_google_oauth_flow(self):
        """Test complete Google OAuth flow with real endpoints."""
        # This would test against Google's OAuth sandbox
        pass
    
    async def test_facebook_oauth_flow(self):
        """Test complete Facebook OAuth flow."""
        # This would test against Facebook's test app
        pass
```

## Troubleshooting Common Issues

### 1. Invalid Redirect URI

**Problem:** `redirect_uri_mismatch` error
**Solution:** Ensure redirect URI exactly matches registered URI in provider console

### 2. Scope Permission Issues

**Problem:** `insufficient_scope` error  
**Solution:** Request appropriate scopes during authorization

### 3. Token Expiration

**Problem:** `invalid_token` error
**Solution:** Implement automatic token refresh

### 4. Rate Limiting

**Problem:** `rate_limit_exceeded` error
**Solution:** Implement exponential backoff and request throttling

---

**Security Note:** Always store OAuth credentials securely, use HTTPS for all OAuth flows, and implement proper CSRF protection with state parameters.

**Contact:** mlaiel@live.de for OAuth implementation questions and support.