"""
🔐 GATEWAY AUTHENTICATION SERVICE
Service d'authentification centralisé pour API Gateway

Fonctionnalités:
- OAuth2/OIDC integration
- JWT token validation
- Multi-tenant authentication
- SSO support
- API key management

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
import time
import jwt
import hashlib
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AuthMethod(Enum):
    """Méthodes d'authentification supportées"""
    JWT_BEARER = "jwt_bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"

@dataclass
class AuthContext:
    """Contexte d'authentification"""
    user_id: str
    tenant_id: str
    roles: List[str]
    permissions: List[str]
    auth_method: AuthMethod
    token_exp: Optional[int] = None
    api_key_id: Optional[str] = None
    metadata: Dict[str, Any] = None

class GatewayAuthentication:
    """
    🔐 SERVICE AUTHENTIFICATION GATEWAY ENTERPRISE
    
    Authentification centralisée pour toutes les requêtes API
    Support OAuth2/OIDC, JWT, API Keys, multi-tenant
    """
    
    def __init__(self, service_id: str = None):
        self.service_id = service_id or f"gateway-auth-{int(time.time())}"
        self.status = "initializing"
        self.jwt_secret = "ainflue-enterprise-jwt-secret-2025"  # En production: variable d'environnement
        self.api_keys = {}
        self.oauth_providers = {}
        self.auth_cache = {}
        
    async def initialize(self) -> bool:
        """Initialiser le service d'authentification"""
        logger.info("🔐 Initializing Gateway Authentication Service...")
        
        try:
            # Charger les clés API
            await self._load_api_keys()
            
            # Configurer les providers OAuth
            await self._configure_oauth_providers()
            
            self.status = "ready"
            logger.info("✅ Gateway Authentication Service initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gateway Authentication: {e}")
            self.status = "error"
            return False
    
    async def _load_api_keys(self) -> None:
        """Charger les clés API depuis la base de données"""
        # Simulation - en production, charger depuis la DB
        self.api_keys = {
            "ak_prod_ainflue_12345": {
                "key_id": "ak_prod_ainflue_12345",
                "tenant_id": "ainflue_enterprise",
                "user_id": "system_api",
                "permissions": ["read", "write", "admin"],
                "rate_limit": 10000,
                "created_at": time.time(),
                "last_used": None,
                "active": True
            },
            "ak_dev_test_67890": {
                "key_id": "ak_dev_test_67890", 
                "tenant_id": "development",
                "user_id": "dev_user",
                "permissions": ["read", "write"],
                "rate_limit": 1000,
                "created_at": time.time(),
                "last_used": None,
                "active": True
            }
        }
    
    async def _configure_oauth_providers(self) -> None:
        """Configurer les providers OAuth2/OIDC"""
        self.oauth_providers = {
            "google": {
                "client_id": "google_client_id",
                "client_secret": "google_client_secret",
                "authorization_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scopes": ["email", "profile"]
            },
            "github": {
                "client_id": "github_client_id",
                "client_secret": "github_client_secret",
                "authorization_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scopes": ["user:email"]
            }
        }
    
    async def authenticate_request(
        self, 
        authorization_header: str = None,
        api_key: str = None,
        request_path: str = None,
        request_method: str = "GET"
    ) -> Optional[AuthContext]:
        """
        Authentifier une requête entrante
        
        Args:
            authorization_header: Header Authorization (Bearer token)
            api_key: Clé API dans les headers ou query params
            request_path: Chemin de la requête
            request_method: Méthode HTTP
        """
        try:
            # Vérifier le cache d'authentification
            cache_key = self._generate_cache_key(authorization_header, api_key)
            if cache_key in self.auth_cache:
                cached_auth = self.auth_cache[cache_key]
                if cached_auth['expires_at'] > time.time():
                    return cached_auth['context']
            
            # Authentification par Bearer Token (JWT)
            if authorization_header and authorization_header.startswith("Bearer "):
                token = authorization_header[7:]  # Enlever "Bearer "
                auth_context = await self._authenticate_jwt(token)
                if auth_context:
                    self._cache_auth_result(cache_key, auth_context, 300)  # Cache 5min
                    return auth_context
            
            # Authentification par API Key
            if api_key:
                auth_context = await self._authenticate_api_key(api_key)
                if auth_context:
                    self._cache_auth_result(cache_key, auth_context, 600)  # Cache 10min
                    return auth_context
            
            # Aucune authentification valide trouvée
            logger.warning(f"Authentication failed for path: {request_path}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
    
    async def _authenticate_jwt(self, token: str) -> Optional[AuthContext]:
        """Authentifier un token JWT"""
        try:
            # Décoder et valider le JWT
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Extraire les informations du payload
            user_id = payload.get('sub')
            tenant_id = payload.get('tenant_id', 'default')
            roles = payload.get('roles', [])
            permissions = payload.get('permissions', [])
            exp = payload.get('exp')
            
            if not user_id:
                logger.warning("JWT missing user_id (sub)")
                return None
            
            return AuthContext(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles,
                permissions=permissions,
                auth_method=AuthMethod.JWT_BEARER,
                token_exp=exp
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    async def _authenticate_api_key(self, api_key: str) -> Optional[AuthContext]:
        """Authentifier une clé API"""
        # Hasher la clé pour la recherche sécurisée
        key_info = self.api_keys.get(api_key)
        
        if not key_info:
            logger.warning(f"Unknown API key: {api_key[:10]}...")
            return None
        
        if not key_info['active']:
            logger.warning(f"Inactive API key: {api_key[:10]}...")
            return None
        
        # Mettre à jour la dernière utilisation
        key_info['last_used'] = time.time()
        
        return AuthContext(
            user_id=key_info['user_id'],
            tenant_id=key_info['tenant_id'],
            roles=["api_user"],
            permissions=key_info['permissions'],
            auth_method=AuthMethod.API_KEY,
            api_key_id=key_info['key_id'],
            metadata={"rate_limit": key_info['rate_limit']}
        )
    
    def _generate_cache_key(self, auth_header: str = None, api_key: str = None) -> str:
        """Générer une clé de cache pour l'authentification"""
        key_data = f"{auth_header or ''}-{api_key or ''}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _cache_auth_result(self, cache_key: str, auth_context: AuthContext, ttl_seconds: int):
        """Mettre en cache le résultat d'authentification"""
        self.auth_cache[cache_key] = {
            'context': auth_context,
            'expires_at': time.time() + ttl_seconds
        }
        
        # Nettoyage du cache (simple LRU)
        if len(self.auth_cache) > 1000:
            # Supprimer les entrées expirées
            current_time = time.time()
            expired_keys = [k for k, v in self.auth_cache.items() if v['expires_at'] < current_time]
            for key in expired_keys:
                del self.auth_cache[key]
    
    async def generate_jwt_token(
        self, 
        user_id: str,
        tenant_id: str = "default",
        roles: List[str] = None,
        permissions: List[str] = None,
        expires_in_seconds: int = 3600
    ) -> str:
        """Générer un token JWT"""
        payload = {
            'sub': user_id,
            'tenant_id': tenant_id,
            'roles': roles or [],
            'permissions': permissions or [],
            'iat': int(time.time()),
            'exp': int(time.time() + expires_in_seconds),
            'iss': 'ainflue-api-gateway'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        logger.info(f"Generated JWT token for user: {user_id}")
        return token
    
    async def create_api_key(
        self,
        user_id: str,
        tenant_id: str,
        permissions: List[str],
        rate_limit: int = 1000
    ) -> Dict[str, Any]:
        """Créer une nouvelle clé API"""
        import secrets
        
        # Générer une clé sécurisée
        api_key = f"ak_{tenant_id}_{secrets.token_urlsafe(32)}"
        
        key_info = {
            "key_id": api_key,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "permissions": permissions,
            "rate_limit": rate_limit,
            "created_at": time.time(),
            "last_used": None,
            "active": True
        }
        
        self.api_keys[api_key] = key_info
        
        logger.info(f"Created API key for user: {user_id}")
        return {
            "api_key": api_key,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "permissions": permissions,
            "rate_limit": rate_limit
        }
    
    async def revoke_api_key(self, api_key: str) -> bool:
        """Révoquer une clé API"""
        if api_key in self.api_keys:
            self.api_keys[api_key]['active'] = False
            logger.info(f"Revoked API key: {api_key[:10]}...")
            return True
        return False
    
    async def validate_permissions(
        self, 
        auth_context: AuthContext,
        required_permissions: List[str]
    ) -> bool:
        """Valider que l'utilisateur a les permissions requises"""
        if not required_permissions:
            return True
        
        user_permissions = set(auth_context.permissions)
        required_permissions_set = set(required_permissions)
        
        # Vérifier si l'utilisateur a toutes les permissions requises
        has_permissions = required_permissions_set.issubset(user_permissions)
        
        # Vérifier les rôles admin
        if not has_permissions and "admin" in auth_context.roles:
            has_permissions = True
        
        return has_permissions
    
    async def get_oauth_authorization_url(self, provider: str, state: str = None) -> Optional[str]:
        """Obtenir l'URL d'autorisation OAuth2"""
        if provider not in self.oauth_providers:
            return None
        
        provider_config = self.oauth_providers[provider]
        
        import urllib.parse
        params = {
            'client_id': provider_config['client_id'],
            'response_type': 'code',
            'scope': ' '.join(provider_config['scopes']),
            'redirect_uri': f"https://api.ainflue.com/auth/oauth/{provider}/callback"
        }
        
        if state:
            params['state'] = state
        
        url = f"{provider_config['authorization_url']}?{urllib.parse.urlencode(params)}"
        return url
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'authentification"""
        active_api_keys = len([k for k in self.api_keys.values() if k['active']])
        cache_entries = len(self.auth_cache)
        
        return {
            'service_id': self.service_id,
            'status': self.status,
            'total_api_keys': len(self.api_keys),
            'active_api_keys': active_api_keys,
            'cache_entries': cache_entries,
            'oauth_providers': list(self.oauth_providers.keys()),
            'supported_auth_methods': [method.value for method in AuthMethod]
        }

# Instance globale du service
gateway_authentication = GatewayAuthentication()

async def main():
    """Test du service d'authentification gateway"""
    await gateway_authentication.initialize()
    
    # Test de génération de token JWT
    token = await gateway_authentication.generate_jwt_token(
        "user123",
        "ainflue_enterprise",
        ["creator", "user"],
        ["read", "write", "upload"]
    )
    print(f"Generated JWT: {token}")
    
    # Test d'authentification avec le token
    auth_context = await gateway_authentication.authenticate_request(
        authorization_header=f"Bearer {token}"
    )
    print(f"Auth context: {auth_context}")
    
    # Test de création d'API key
    api_key_info = await gateway_authentication.create_api_key(
        "user456",
        "development",
        ["read", "write"]
    )
    print(f"API Key created: {api_key_info}")

if __name__ == "__main__":
    asyncio.run(main())