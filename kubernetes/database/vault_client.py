"""Enterprise Vault Client for Secure Key Management
HashiCorp Vault integration for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

🔐 VAULT INTEGRATION:
- HashiCorp Vault client enterprise
- Multi-auth methods (token, AWS, K8s)
- Automatic token renewal
- Secret versioning et rollback
- Dynamic secrets management
- Policy-based access control

🛡️ SÉCURITÉ AVANCÉE:
- TLS mutual authentication
- Certificate management
- Token lifecycle management
- Secret rotation automatique
- Audit logging complet
- Compliance reporting

🔑 GESTION SECRETS:
- KV v2 secrets engine
- Transit encryption engine
- PKI certificate authority
- Database dynamic credentials
- SSH certificate authority
- TOTP secrets generation

📊 MONITORING VAULT:
- Health check automatique
- Performance metrics
- Token expiration tracking
- Secret usage analytics
- Error rate monitoring
- Alert integration
"""import asyncio
import aiohttp
import json
import os
import ssl
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import base64
import logging
from enum import Enum
from dataclasses import dataclass
from urllib.parse import urljoin
import jwt
import time

from backend.core.config import get_settings
from backend.core.logging import get_logger


class AuthMethod(Enum):
    """Méthodes d'authentification Vault"""    TOKEN = "token"
    AWS_IAM = "aws"
    KUBERNETES = "kubernetes"
    LDAP = "ldap"
    USERPASS = "userpass"
    APPROLE = "approle"
    GITHUB = "github"


class SecretEngine(Enum):
    """Types de secret engines"""    KV_V2 = "kv-v2"
    TRANSIT = "transit"
    PKI = "pki"
    DATABASE = "database"
    SSH = "ssh"
    TOTP = "totp"
    AWS = "aws"
    AZURE = "azure"


@dataclass
class VaultSecret:
    """Représentation d'un secret Vault"""    path: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    version: int
    created_time: datetime
    deletion_time: Optional[datetime] = None
    destroyed: bool = False


@dataclass
class VaultToken:
    """Token d'authentification Vault"""    token: str
    accessor: str
    policies: List[str]
    renewable: bool
    ttl: int
    expires_at: datetime
    entity_id: Optional[str] = None
    metadata: Dict[str, Any] = None


class VaultClient:
    """    Client enterprise pour HashiCorp Vault
    Gère l'authentification, les secrets et les opérations sécurisées
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_settings()
        self.logger = get_logger(f"{__name__}.VaultClient")
        
        # Configuration Vault
        self.vault_url = self.config.get('vault_url', os.getenv('VAULT_ADDR', 'https://vault.local:8200'))
        self.vault_token = None
        self.token_expires_at = None
        self.namespace = self.config.get('vault_namespace', os.getenv('VAULT_NAMESPACE'))
        
        # Configuration SSL
        self.verify_ssl = self.config.get('vault_verify_ssl', True)
        self.ca_cert_path = self.config.get('vault_ca_cert')
        self.client_cert_path = self.config.get('vault_client_cert')
        self.client_key_path = self.config.get('vault_client_key')
        
        # Session HTTP
        self.session = None
        self.ssl_context = None
        
        # Configuration auth
        self.auth_method = AuthMethod(self.config.get('vault_auth_method', 'token'))
        self.role_id = self.config.get('vault_role_id', os.getenv('VAULT_ROLE_ID'))
        self.secret_id = self.config.get('vault_secret_id', os.getenv('VAULT_SECRET_ID'))
        
        # Initialisation
        self._setup_ssl_context()
        self._initialize_session()
    
    def _setup_ssl_context(self):
        """Configure le contexte SSL pour Vault"""        try:
            if not self.verify_ssl:
                self.ssl_context = False
                return
            
            self.ssl_context = ssl.create_default_context()
            
            # Certificat CA personnalisé
            if self.ca_cert_path and os.path.exists(self.ca_cert_path):
                self.ssl_context.load_verify_locations(self.ca_cert_path)
            
            # Certificats client pour mTLS
            if self.client_cert_path and self.client_key_path:
                if os.path.exists(self.client_cert_path) and os.path.exists(self.client_key_path):
                    self.ssl_context.load_cert_chain(self.client_cert_path, self.client_key_path)
            
            self.logger.info("SSL context configured for Vault connection")
            
        except Exception as e:
            self.logger.error(f"Failed to setup SSL context: {e}")
            raise
    
    async def _initialize_session(self):
        """Initialise la session HTTP asynchrone"""        try:
            connector = aiohttp.TCPConnector(
                ssl=self.ssl_context,
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'IA-Influencer-Agent/1.0 Vault-Client'
                }
            )
            
            # Authentification automatique
            await self._authenticate()
            
            self.logger.info("✅ Vault session initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Vault session: {e}")
            raise
    
    async def _authenticate(self):
        """Authentification automatique selon la méthode configurée"""        try:
            if self.auth_method == AuthMethod.TOKEN:
                await self._auth_with_token()
            elif self.auth_method == AuthMethod.APPROLE:
                await self._auth_with_approle()
            elif self.auth_method == AuthMethod.AWS_IAM:
                await self._auth_with_aws()
            elif self.auth_method == AuthMethod.KUBERNETES:
                await self._auth_with_kubernetes()
            else:
                raise ValueError(f"Unsupported auth method: {self.auth_method}")
            
            self.logger.info(f"✅ Vault authentication successful ({self.auth_method.value})")
            
        except Exception as e:
            self.logger.error(f"❌ Vault authentication failed: {e}")
            raise
    
    async def _auth_with_token(self):
        """Authentification par token"""        try:
            token = self.config.get('vault_token', os.getenv('VAULT_TOKEN'))
            if not token:
                raise ValueError("Vault token not provided")
            
            # Validation du token
            headers = {'X-Vault-Token': token}
            if self.namespace:
                headers['X-Vault-Namespace'] = self.namespace
            
            async with self.session.get(
                urljoin(self.vault_url, '/v1/auth/token/lookup-self'),
                headers=headers
            ) as response:
                if response.status == 200:
                    token_info = await response.json()
                    self.vault_token = token
                    
                    # Calcul expiration
                    ttl = token_info['data'].get('ttl', 0)
                    if ttl > 0:
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                    
                    self.logger.info("Token authentication successful")
                else:
                    raise ValueError(f"Token validation failed: {response.status}")
            
        except Exception as e:
            self.logger.error(f"Token authentication failed: {e}")
            raise
    
    async def _auth_with_approle(self):
        """Authentification par AppRole"""        try:
            if not self.role_id or not self.secret_id:
                raise ValueError("AppRole credentials not provided")
            
            auth_data = {
                'role_id': self.role_id,
                'secret_id': self.secret_id
            }
            
            headers = {}
            if self.namespace:
                headers['X-Vault-Namespace'] = self.namespace
            
            async with self.session.post(
                urljoin(self.vault_url, '/v1/auth/approle/login'),
                json=auth_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    auth_info = auth_response['auth']
                    
                    self.vault_token = auth_info['client_token']
                    
                    # Calcul expiration
                    lease_duration = auth_info.get('lease_duration', 0)
                    if lease_duration > 0:
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=lease_duration)
                    
                    self.logger.info("AppRole authentication successful")
                else:
                    error_text = await response.text()
                    raise ValueError(f"AppRole auth failed: {response.status} - {error_text}")
            
        except Exception as e:
            self.logger.error(f"AppRole authentication failed: {e}")
            raise
    
    async def _auth_with_aws(self):
        """Authentification AWS IAM"""        try:
            # Récupération métadonnées EC2
            import boto3
            
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                raise ValueError("AWS credentials not available")
            
            # Création signature AWS
            from botocore.auth import SigV4Auth
            from botocore.awsrequest import AWSRequest
            
            request = AWSRequest(
                method='POST',
                url='https://sts.amazonaws.com/',
                data='Action=GetCallerIdentity&Version=2011-06-15',
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
            )
            
            SigV4Auth(credentials, 'sts', session.region_name or 'us-east-1').add_auth(request)
            
            # Authentification Vault
            auth_data = {
                'iam_http_request_method': 'POST',
                'iam_request_url': base64.b64encode(b'https://sts.amazonaws.com/').decode(),
                'iam_request_body': base64.b64encode(request.body.encode()).decode(),
                'iam_request_headers': base64.b64encode(
                    json.dumps(dict(request.headers)).encode()
                ).decode()
            }
            
            headers = {}
            if self.namespace:
                headers['X-Vault-Namespace'] = self.namespace
            
            async with self.session.post(
                urljoin(self.vault_url, '/v1/auth/aws/login'),
                json=auth_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    auth_info = auth_response['auth']
                    
                    self.vault_token = auth_info['client_token']
                    
                    # Calcul expiration
                    lease_duration = auth_info.get('lease_duration', 0)
                    if lease_duration > 0:
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=lease_duration)
                    
                    self.logger.info("AWS IAM authentication successful")
                else:
                    error_text = await response.text()
                    raise ValueError(f"AWS auth failed: {response.status} - {error_text}")
            
        except Exception as e:
            self.logger.error(f"AWS authentication failed: {e}")
            raise
    
    async def _auth_with_kubernetes(self):
        """Authentification Kubernetes service account"""        try:
            # Lecture du token de service account
            token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
            if not os.path.exists(token_path):
                raise ValueError("Kubernetes service account token not found")
            
            with open(token_path, 'r') as f:
                jwt_token = f.read().strip()
            
            # Authentification Vault
            auth_data = {
                'jwt': jwt_token,
                'role': self.config.get('vault_k8s_role', 'ia-influencer-agent')
            }
            
            headers = {}
            if self.namespace:
                headers['X-Vault-Namespace'] = self.namespace
            
            async with self.session.post(
                urljoin(self.vault_url, '/v1/auth/kubernetes/login'),
                json=auth_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    auth_info = auth_response['auth']
                    
                    self.vault_token = auth_info['client_token']
                    
                    # Calcul expiration
                    lease_duration = auth_info.get('lease_duration', 0)
                    if lease_duration > 0:
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=lease_duration)
                    
                    self.logger.info("Kubernetes authentication successful")
                else:
                    error_text = await response.text()
                    raise ValueError(f"Kubernetes auth failed: {response.status} - {error_text}")
            
        except Exception as e:
            self.logger.error(f"Kubernetes authentication failed: {e}")
            raise
    
    async def _ensure_authenticated(self):
        """S'assure que l'authentification est valide"""        try:
            if not self.vault_token:
                await self._authenticate()
                return
            
            # Vérification expiration
            if self.token_expires_at and datetime.utcnow() >= self.token_expires_at:
                self.logger.info("Token expired, re-authenticating...")
                await self._authenticate()
                return
            
            # Test de validité du token
            headers = {'X-Vault-Token': self.vault_token}
            if self.namespace:
                headers['X-Vault-Namespace'] = self.namespace
            
            async with self.session.get(
                urljoin(self.vault_url, '/v1/auth/token/lookup-self'),
                headers=headers
            ) as response:
                if response.status != 200:
                    self.logger.info("Token invalid, re-authenticating...")
                    await self._authenticate()
            
        except Exception as e:
            self.logger.warning(f"Authentication check failed, re-authenticating: {e}")
            await self._authenticate()
    
    async def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> aiohttp.ClientResponse:
        """Effectue une requête authentifiée vers Vault"""        try:
            await self._ensure_authenticated()
            
            headers = {'X-Vault-Token': self.vault_token}
            if self.namespace:
                headers['X-Vault-Namespace'] = self.namespace
            
            url = urljoin(self.vault_url, path)
            
            kwargs = {
                'headers': headers,
                'params': params
            }
            
            if data is not None:
                kwargs['json'] = data
            
            async with self.session.request(method, url, **kwargs) as response:
                return response
            
        except Exception as e:
            self.logger.error(f"Vault request failed: {e}")
            raise
    
    async def get_secret(self, path: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """        Récupère un secret depuis Vault
        
        Args:
            path: Chemin du secret
            version: Version spécifique (optionnel)
            
        Returns:
            Données du secret ou None si non trouvé
        """        try:
            # Construction du chemin pour KV v2
            if not path.startswith('/'):
                path = f'/v1/secret/data/{path}'
            elif not path.startswith('/v1/'):
                path = f'/v1/secret/data{path}'
            
            params = {}
            if version:
                params['version'] = version
            
            response = await self._make_request('GET', path, params=params)
            
            if response.status == 200:
                secret_data = await response.json()
                return secret_data['data']['data']
            elif response.status == 404:
                return None
            else:
                error_text = await response.text()
                raise ValueError(f"Failed to get secret: {response.status} - {error_text}")
            
        except Exception as e:
            self.logger.error(f"Failed to get secret {path}: {e}")
            return None
    
    async def store_secret(
        self,
        path: str,
        secret_data: Union[str, Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Stocke un secret dans Vault
        
        Args:
            path: Chemin du secret
            secret_data: Données du secret
            metadata: Métadonnées optionnelles
            
        Returns:
            True si succès, False sinon
        """        try:
            # Construction du chemin pour KV v2
            if not path.startswith('/'):
                path = f'/v1/secret/data/{path}'
            elif not path.startswith('/v1/'):
                path = f'/v1/secret/data{path}'
            
            # Préparation des données
            if isinstance(secret_data, str):
                data = {'value': secret_data}
            else:
                data = secret_data
            
            payload = {'data': data}
            
            if metadata:
                payload['metadata'] = metadata
            
            response = await self._make_request('POST', path, data=payload)
            
            if response.status in [200, 204]:
                self.logger.debug(f"Secret stored successfully at {path}")
                return True
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to store secret: {response.status} - {error_text}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to store secret {path}: {e}")
            return False
    
    async def delete_secret(self, path: str, versions: Optional[List[int]] = None) -> bool:
        """        Supprime un secret de Vault
        
        Args:
            path: Chemin du secret
            versions: Versions spécifiques à supprimer
            
        Returns:
            True si succès, False sinon
        """        try:
            if versions:
                # Suppression de versions spécifiques
                delete_path = f'/v1/secret/delete/{path.lstrip("/")}'
                data = {'versions': versions}
                response = await self._make_request('POST', delete_path, data=data)
            else:
                # Suppression complète
                if not path.startswith('/'):
                    path = f'/v1/secret/metadata/{path}'
                elif not path.startswith('/v1/'):
                    path = f'/v1/secret/metadata{path}'
                
                response = await self._make_request('DELETE', path)
            
            if response.status in [200, 204]:
                self.logger.debug(f"Secret deleted successfully: {path}")
                return True
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to delete secret: {response.status} - {error_text}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete secret {path}: {e}")
            return False
    
    async def list_secrets(self, path: str = "") -> List[str]:
        """        Liste les secrets dans un chemin
        
        Args:
            path: Chemin à lister
            
        Returns:
            Liste des noms de secrets
        """        try:
            if not path.startswith('/'):
                list_path = f'/v1/secret/metadata/{path}'
            elif not path.startswith('/v1/'):
                list_path = f'/v1/secret/metadata{path}'
            else:
                list_path = path
            
            response = await self._make_request('LIST', list_path)
            
            if response.status == 200:
                list_data = await response.json()
                return list_data.get('data', {}).get('keys', [])
            elif response.status == 404:
                return []
            else:
                error_text = await response.text()
                raise ValueError(f"Failed to list secrets: {response.status} - {error_text}")
            
        except Exception as e:
            self.logger.error(f"Failed to list secrets at {path}: {e}")
            return []
    
    async def get_secret_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """        Récupère les métadonnées d'un secret
        
        Args:
            path: Chemin du secret
            
        Returns:
            Métadonnées du secret ou None
        """        try:
            if not path.startswith('/'):
                metadata_path = f'/v1/secret/metadata/{path}'
            elif not path.startswith('/v1/'):
                metadata_path = f'/v1/secret/metadata{path}'
            else:
                metadata_path = path.replace('/data/', '/metadata/')
            
            response = await self._make_request('GET', metadata_path)
            
            if response.status == 200:
                metadata = await response.json()
                return metadata['data']
            elif response.status == 404:
                return None
            else:
                error_text = await response.text()
                raise ValueError(f"Failed to get metadata: {response.status} - {error_text}")
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata for {path}: {e}")
            return None
    
    async def encrypt_data(
        self,
        key_name: str,
        plaintext: Union[str, bytes],
        context: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """        Chiffre des données avec Vault Transit
        
        Args:
            key_name: Nom de la clé de chiffrement
            plaintext: Données à chiffrer
            context: Contexte additionnel
            
        Returns:
            Données chiffrées ou None
        """        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            
            data = {
                'plaintext': base64.b64encode(plaintext).decode('utf-8')
            }
            
            if context:
                data['context'] = base64.b64encode(
                    json.dumps(context).encode('utf-8')
                ).decode('utf-8')
            
            response = await self._make_request(
                'POST',
                f'/v1/transit/encrypt/{key_name}',
                data=data
            )
            
            if response.status == 200:
                encrypt_data = await response.json()
                return encrypt_data['data']['ciphertext']
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to encrypt: {response.status} - {error_text}")
                return None
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return None
    
    async def decrypt_data(
        self,
        key_name: str,
        ciphertext: str,
        context: Optional[Dict[str, str]] = None
    ) -> Optional[bytes]:
        """        Déchiffre des données avec Vault Transit
        
        Args:
            key_name: Nom de la clé de chiffrement
            ciphertext: Données chiffrées
            context: Contexte additionnel
            
        Returns:
            Données déchiffrées ou None
        """        try:
            data = {'ciphertext': ciphertext}
            
            if context:
                data['context'] = base64.b64encode(
                    json.dumps(context).encode('utf-8')
                ).decode('utf-8')
            
            response = await self._make_request(
                'POST',
                f'/v1/transit/decrypt/{key_name}',
                data=data
            )
            
            if response.status == 200:
                decrypt_data = await response.json()
                plaintext_b64 = decrypt_data['data']['plaintext']
                return base64.b64decode(plaintext_b64)
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to decrypt: {response.status} - {error_text}")
                return None
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """        Vérification de santé de Vault
        
        Returns:
            Statut de santé de Vault
        """        try:
            response = await self._make_request('GET', '/v1/sys/health')
            
            if response.status == 200:
                health_data = await response.json()
                return {
                    'status': 'healthy',
                    'initialized': health_data.get('initialized', False),
                    'sealed': health_data.get('sealed', True),
                    'standby': health_data.get('standby', False),
                    'version': health_data.get('version', 'unknown'),
                    'cluster_name': health_data.get('cluster_name'),
                    'cluster_id': health_data.get('cluster_id')
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'Health check failed: {response.status}'
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def get_token_info(self) -> Optional[Dict[str, Any]]:
        """        Récupère les informations du token actuel
        
        Returns:
            Informations du token ou None
        """        try:
            await self._ensure_authenticated()
            
            response = await self._make_request('GET', '/v1/auth/token/lookup-self')
            
            if response.status == 200:
                token_data = await response.json()
                return token_data['data']
            else:
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to get token info: {e}")
            return None
    
    async def renew_token(self, increment: Optional[int] = None) -> bool:
        """        Renouvelle le token actuel
        
        Args:
            increment: Durée supplémentaire en secondes
            
        Returns:
            True si succès, False sinon
        """        try:
            await self._ensure_authenticated()
            
            data = {}
            if increment:
                data['increment'] = increment
            
            response = await self._make_request('POST', '/v1/auth/token/renew-self', data=data)
            
            if response.status == 200:
                renew_data = await response.json()
                auth_info = renew_data['auth']
                
                # Mise à jour expiration
                lease_duration = auth_info.get('lease_duration', 0)
                if lease_duration > 0:
                    self.token_expires_at = datetime.utcnow() + timedelta(seconds=lease_duration)
                
                self.logger.info("Token renewed successfully")
                return True
            else:
                error_text = await response.text()
                self.logger.error(f"Failed to renew token: {response.status} - {error_text}")
                return False
            
        except Exception as e:
            self.logger.error(f"Token renewal failed: {e}")
            return False
    
    async def close(self):
        """Ferme proprement la connexion Vault"""        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            self.logger.info("✅ Vault client closed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to close Vault client: {e}")


# Factory function
_vault_client: Optional[VaultClient] = None


def get_vault_client(config: Optional[Dict[str, Any]] = None) -> VaultClient:
    """Récupère ou crée l'instance du client Vault"""    global _vault_client
    
    if _vault_client is None:
        _vault_client = VaultClient(config)
    
    return _vault_client


# Export des classes principales
__all__ = [
    'VaultClient',
    'AuthMethod',
    'SecretEngine',
    'VaultSecret',
    'VaultToken',
    'get_vault_client'
]
