#!/usr/bin/env python3
"""
Identity Provider Manager - Enterprise SSO and Identity Federation System
Advanced identity management with SAML, OAuth2, LDAP, and multi-provider support

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import secrets
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdentityProviderType(Enum):
    """Types de fournisseurs d'identité"""
    SAML2 = "saml2"
    OAUTH2 = "oauth2"
    OIDC = "oidc"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "active_directory"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    CUSTOM = "custom"

class AuthenticationMethod(Enum):
    """Méthodes d'authentification"""
    PASSWORD = "password"
    MFA = "mfa"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"
    SSO = "sso"
    FEDERATED = "federated"

@dataclass
class IdentityProvider:
    """Configuration fournisseur d'identité"""
    provider_id: str
    name: str
    provider_type: IdentityProviderType
    enabled: bool
    configuration: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'provider_id': self.provider_id,
            'name': self.name,
            'provider_type': self.provider_type.value,
            'enabled': self.enabled,
            'configuration': self.configuration,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

@dataclass
class FederatedUser:
    """Utilisateur fédéré depuis IdP externe"""
    user_id: str
    external_id: str
    provider_id: str
    username: str
    email: str
    display_name: str
    attributes: Dict[str, Any]
    groups: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'external_id': self.external_id,
            'provider_id': self.provider_id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'attributes': self.attributes,
            'groups': self.groups,
            'roles': self.roles,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }

class IdentityProviderManager:
    """Gestionnaire principal des fournisseurs d'identité"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisation gestionnaire IdP"""
        self.config = config or {}
        self.providers: Dict[str, IdentityProvider] = {}
        self.federated_users: Dict[str, FederatedUser] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Configuration SAML
        self.saml_sp_config = self.config.get('saml_sp_config', {})
        self.saml_private_key = self._load_saml_private_key()
        self.saml_certificate = self._load_saml_certificate()
        
        # Configuration JWT
        self.jwt_secret = self.config.get('jwt_secret', secrets.token_urlsafe(32))
        self.jwt_algorithm = self.config.get('jwt_algorithm', 'HS256')
        self.jwt_expiry = self.config.get('jwt_expiry', 3600)  # 1 heure
        
        logger.info("Identity Provider Manager initialized successfully")
    
    def _load_saml_private_key(self) -> Any:
        """Chargement clé privée SAML"""
        try:
            key_data = self.config.get('saml_private_key')
            if key_data:
                return serialization.load_pem_private_key(key_data.encode(), password=None)
            else:
                # Génération clé si non fournie
                private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                return private_key
        except Exception as e:
            logger.error(f"Error loading SAML private key: {str(e)}")
            return None
    
    def _load_saml_certificate(self) -> Optional[str]:
        """Chargement certificat SAML"""
        return self.config.get('saml_certificate')
    
    async def register_identity_provider(
        self,
        name: str,
        provider_type: IdentityProviderType,
        configuration: Dict[str, Any]
    ) -> str:
        """Enregistrement nouveau fournisseur d'identité"""
        try:
            provider_id = str(uuid.uuid4())
            
            # Validation configuration selon type
            validated_config = await self._validate_provider_config(provider_type, configuration)
            
            provider = IdentityProvider(
                provider_id=provider_id,
                name=name,
                provider_type=provider_type,
                enabled=True,
                configuration=validated_config
            )
            
            # Test connexion
            connection_test = await self._test_provider_connection(provider)
            if not connection_test['success']:
                raise ValueError(f"Provider connection test failed: {connection_test['error']}")
            
            self.providers[provider_id] = provider
            
            logger.info(f"Registered identity provider: {name} ({provider_type.value})")
            return provider_id
            
        except Exception as e:
            logger.error(f"Error registering identity provider: {str(e)}")
            raise
    
    async def _validate_provider_config(
        self,
        provider_type: IdentityProviderType,
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validation configuration fournisseur"""
        
        required_fields = {
            IdentityProviderType.SAML2: ['sso_url', 'entity_id', 'x509_cert'],
            IdentityProviderType.OAUTH2: ['client_id', 'client_secret', 'authorization_url', 'token_url'],
            IdentityProviderType.OIDC: ['client_id', 'client_secret', 'discovery_url'],
            IdentityProviderType.LDAP: ['server_url', 'bind_dn', 'bind_password', 'user_base_dn'],
            IdentityProviderType.GOOGLE: ['client_id', 'client_secret'],
            IdentityProviderType.MICROSOFT: ['client_id', 'client_secret', 'tenant_id']
        }
        
        if provider_type in required_fields:
            for field in required_fields[provider_type]:
                if field not in configuration:
                    raise ValueError(f"Missing required field: {field}")
        
        return configuration
    
    async def _test_provider_connection(self, provider: IdentityProvider) -> Dict[str, Any]:
        """Test connexion fournisseur d'identité"""
        try:
            if provider.provider_type == IdentityProviderType.SAML2:
                return await self._test_saml_connection(provider)
            elif provider.provider_type in [IdentityProviderType.OAUTH2, IdentityProviderType.OIDC]:
                return await self._test_oauth_connection(provider)
            elif provider.provider_type == IdentityProviderType.LDAP:
                return await self._test_ldap_connection(provider)
            else:
                return {'success': True, 'message': 'Connection test not implemented for this provider type'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _test_saml_connection(self, provider: IdentityProvider) -> Dict[str, Any]:
        """Test connexion SAML"""
        try:
            # Récupération métadonnées IdP
            metadata_url = provider.configuration.get('metadata_url')
            if metadata_url:
                response = requests.get(metadata_url, timeout=10)
                if response.status_code == 200:
                    # Parse métadonnées XML
                    root = ET.fromstring(response.content)
                    return {'success': True, 'message': 'SAML metadata retrieved successfully'}
            
            return {'success': True, 'message': 'SAML configuration appears valid'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _test_oauth_connection(self, provider: IdentityProvider) -> Dict[str, Any]:
        """Test connexion OAuth2/OIDC"""
        try:
            if provider.provider_type == IdentityProviderType.OIDC:
                # Récupération configuration OIDC
                discovery_url = provider.configuration.get('discovery_url')
                if discovery_url:
                    response = requests.get(discovery_url, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'message': 'OIDC discovery endpoint accessible'}
            
            # Test endpoints OAuth2
            auth_url = provider.configuration.get('authorization_url')
            if auth_url:
                response = requests.head(auth_url, timeout=10)
                if response.status_code < 500:
                    return {'success': True, 'message': 'OAuth2 endpoints accessible'}
            
            return {'success': True, 'message': 'OAuth2 configuration appears valid'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _test_ldap_connection(self, provider: IdentityProvider) -> Dict[str, Any]:
        """Test connexion LDAP"""
        try:
            # Simulation test LDAP (nécessiterait ldap3 library)
            server_url = provider.configuration.get('server_url')
            bind_dn = provider.configuration.get('bind_dn')
            
            if server_url and bind_dn:
                return {'success': True, 'message': 'LDAP configuration appears valid'}
            
            return {'success': False, 'error': 'Invalid LDAP configuration'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def initiate_sso_login(
        self,
        provider_id: str,
        relay_state: str = None
    ) -> Dict[str, Any]:
        """Initiation connexion SSO"""
        try:
            if provider_id not in self.providers:
                raise ValueError(f"Provider {provider_id} not found")
            
            provider = self.providers[provider_id]
            
            if provider.provider_type == IdentityProviderType.SAML2:
                return await self._initiate_saml_login(provider, relay_state)
            elif provider.provider_type in [IdentityProviderType.OAUTH2, IdentityProviderType.OIDC]:
                return await self._initiate_oauth_login(provider, relay_state)
            else:
                raise ValueError(f"SSO not supported for provider type: {provider.provider_type.value}")
                
        except Exception as e:
            logger.error(f"Error initiating SSO login: {str(e)}")
            raise
    
    async def _initiate_saml_login(
        self,
        provider: IdentityProvider,
        relay_state: str = None
    ) -> Dict[str, Any]:
        """Initiation connexion SAML"""
        try:
            # Génération AuthnRequest SAML
            request_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            sp_entity_id = self.saml_sp_config.get('entity_id', 'https://iacherie.com/saml/sp')
            acs_url = self.saml_sp_config.get('acs_url', 'https://iacherie.com/saml/acs')
            
            authn_request = f"""
            <samlp:AuthnRequest
                xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                ID="{request_id}"
                Version="2.0"
                IssueInstant="{timestamp}"
                Destination="{provider.configuration['sso_url']}"
                AssertionConsumerServiceURL="{acs_url}">
                <saml:Issuer>{sp_entity_id}</saml:Issuer>
            </samlp:AuthnRequest>
            """
            
            # Encodage et redirection
            encoded_request = base64.b64encode(authn_request.encode()).decode()
            
            redirect_url = f"{provider.configuration['sso_url']}?SAMLRequest={encoded_request}"
            if relay_state:
                redirect_url += f"&RelayState={relay_state}"
            
            return {
                'redirect_url': redirect_url,
                'request_id': request_id,
                'method': 'GET'
            }
            
        except Exception as e:
            logger.error(f"Error initiating SAML login: {str(e)}")
            raise
    
    async def _initiate_oauth_login(
        self,
        provider: IdentityProvider,
        relay_state: str = None
    ) -> Dict[str, Any]:
        """Initiation connexion OAuth2/OIDC"""
        try:
            state = secrets.token_urlsafe(32)
            nonce = secrets.token_urlsafe(32)
            
            params = {
                'client_id': provider.configuration['client_id'],
                'response_type': 'code',
                'scope': provider.configuration.get('scope', 'openid email profile'),
                'redirect_uri': provider.configuration.get('redirect_uri', 'https://iacherie.com/auth/callback'),
                'state': state,
                'nonce': nonce
            }
            
            auth_url = provider.configuration['authorization_url']
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            redirect_url = f"{auth_url}?{param_string}"
            
            # Sauvegarde état pour validation
            self.active_sessions[state] = {
                'provider_id': provider.provider_id,
                'nonce': nonce,
                'relay_state': relay_state,
                'timestamp': datetime.utcnow()
            }
            
            return {
                'redirect_url': redirect_url,
                'state': state,
                'method': 'GET'
            }
            
        except Exception as e:
            logger.error(f"Error initiating OAuth login: {str(e)}")
            raise
    
    async def process_sso_response(
        self,
        provider_id: str,
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traitement réponse SSO"""
        try:
            if provider_id not in self.providers:
                raise ValueError(f"Provider {provider_id} not found")
            
            provider = self.providers[provider_id]
            
            if provider.provider_type == IdentityProviderType.SAML2:
                return await self._process_saml_response(provider, response_data)
            elif provider.provider_type in [IdentityProviderType.OAUTH2, IdentityProviderType.OIDC]:
                return await self._process_oauth_response(provider, response_data)
            else:
                raise ValueError(f"SSO response processing not supported for: {provider.provider_type.value}")
                
        except Exception as e:
            logger.error(f"Error processing SSO response: {str(e)}")
            raise
    
    async def _process_saml_response(
        self,
        provider: IdentityProvider,
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traitement réponse SAML"""
        try:
            saml_response = response_data.get('SAMLResponse')
            if not saml_response:
                raise ValueError("Missing SAMLResponse")
            
            # Décodage réponse SAML
            decoded_response = base64.b64decode(saml_response)
            root = ET.fromstring(decoded_response)
            
            # Extraction assertions (simplifiée)
            namespaces = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }
            
            assertion = root.find('.//saml:Assertion', namespaces)
            if assertion is None:
                raise ValueError("No assertion found in SAML response")
            
            # Extraction attributs utilisateur
            subject = assertion.find('.//saml:Subject/saml:NameID', namespaces)
            email = subject.text if subject is not None else None
            
            attributes = {}
            for attr in assertion.findall('.//saml:Attribute', namespaces):
                attr_name = attr.get('Name')
                attr_values = [v.text for v in attr.findall('.//saml:AttributeValue', namespaces)]
                attributes[attr_name] = attr_values[0] if len(attr_values) == 1 else attr_values
            
            # Création utilisateur fédéré
            federated_user = await self._create_federated_user(
                provider=provider,
                external_id=email,
                email=email,
                attributes=attributes
            )
            
            # Génération token JWT
            jwt_token = self._generate_jwt_token(federated_user)
            
            return {
                'success': True,
                'user': federated_user.to_dict(),
                'token': jwt_token,
                'provider': provider.name
            }
            
        except Exception as e:
            logger.error(f"Error processing SAML response: {str(e)}")
            raise
    
    async def _process_oauth_response(
        self,
        provider: IdentityProvider,
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traitement réponse OAuth2/OIDC"""
        try:
            code = response_data.get('code')
            state = response_data.get('state')
            
            if not code or not state:
                raise ValueError("Missing authorization code or state")
            
            # Validation état
            if state not in self.active_sessions:
                raise ValueError("Invalid or expired state")
            
            session = self.active_sessions[state]
            
            # Échange code contre token
            token_data = await self._exchange_oauth_code(provider, code)
            
            # Récupération informations utilisateur
            user_info = await self._get_oauth_user_info(provider, token_data['access_token'])
            
            # Création utilisateur fédéré
            federated_user = await self._create_federated_user(
                provider=provider,
                external_id=user_info.get('sub', user_info.get('id')),
                email=user_info.get('email'),
                attributes=user_info
            )
            
            # Nettoyage session
            del self.active_sessions[state]
            
            # Génération token JWT
            jwt_token = self._generate_jwt_token(federated_user)
            
            return {
                'success': True,
                'user': federated_user.to_dict(),
                'token': jwt_token,
                'provider': provider.name
            }
            
        except Exception as e:
            logger.error(f"Error processing OAuth response: {str(e)}")
            raise
    
    async def _exchange_oauth_code(
        self,
        provider: IdentityProvider,
        code: str
    ) -> Dict[str, Any]:
        """Échange code OAuth contre token"""
        try:
            token_url = provider.configuration['token_url']
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': provider.configuration['client_id'],
                'client_secret': provider.configuration['client_secret'],
                'redirect_uri': provider.configuration.get('redirect_uri', 'https://iacherie.com/auth/callback')
            }
            
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error exchanging OAuth code: {str(e)}")
            raise
    
    async def _get_oauth_user_info(
        self,
        provider: IdentityProvider,
        access_token: str
    ) -> Dict[str, Any]:
        """Récupération informations utilisateur OAuth"""
        try:
            if provider.provider_type == IdentityProviderType.OIDC:
                userinfo_url = provider.configuration.get('userinfo_url', 'https://openid.provider.com/userinfo')
            else:
                userinfo_url = provider.configuration.get('user_info_url')
            
            if not userinfo_url:
                raise ValueError("No user info URL configured")
            
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(userinfo_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting OAuth user info: {str(e)}")
            raise
    
    async def _create_federated_user(
        self,
        provider: IdentityProvider,
        external_id: str,
        email: str,
        attributes: Dict[str, Any]
    ) -> FederatedUser:
        """Création ou mise à jour utilisateur fédéré"""
        try:
            # Recherche utilisateur existant
            existing_user = None
            for user in self.federated_users.values():
                if user.external_id == external_id and user.provider_id == provider.provider_id:
                    existing_user = user
                    break
            
            if existing_user:
                # Mise à jour utilisateur existant
                existing_user.last_login = datetime.utcnow()
                existing_user.attributes.update(attributes)
                return existing_user
            else:
                # Création nouvel utilisateur
                user_id = str(uuid.uuid4())
                
                federated_user = FederatedUser(
                    user_id=user_id,
                    external_id=external_id,
                    provider_id=provider.provider_id,
                    username=attributes.get('preferred_username', email.split('@')[0] if email else external_id),
                    email=email,
                    display_name=attributes.get('name', attributes.get('displayName', email)),
                    attributes=attributes,
                    groups=attributes.get('groups', []),
                    roles=self._map_provider_roles(provider, attributes),
                    last_login=datetime.utcnow()
                )
                
                self.federated_users[user_id] = federated_user
                
                logger.info(f"Created federated user: {email} from provider {provider.name}")
                return federated_user
                
        except Exception as e:
            logger.error(f"Error creating federated user: {str(e)}")
            raise
    
    def _map_provider_roles(
        self,
        provider: IdentityProvider,
        attributes: Dict[str, Any]
    ) -> List[str]:
        """Mapping rôles fournisseur vers rôles locaux"""
        try:
            role_mapping = provider.configuration.get('role_mapping', {})
            user_roles = []
            
            # Récupération rôles depuis attributs
            provider_roles = attributes.get('roles', attributes.get('groups', []))
            
            for provider_role in provider_roles:
                if provider_role in role_mapping:
                    local_role = role_mapping[provider_role]
                    if local_role not in user_roles:
                        user_roles.append(local_role)
                else:
                    # Mapping par défaut
                    if provider_role.lower() in ['admin', 'administrator']:
                        user_roles.append('admin')
                    elif provider_role.lower() in ['user', 'member']:
                        user_roles.append('user')
            
            # Rôle par défaut si aucun trouvé
            if not user_roles:
                user_roles.append('user')
            
            return user_roles
            
        except Exception as e:
            logger.error(f"Error mapping provider roles: {str(e)}")
            return ['user']
    
    def _generate_jwt_token(self, federated_user: FederatedUser) -> str:
        """Génération token JWT pour utilisateur fédéré"""
        try:
            payload = {
                'sub': federated_user.user_id,
                'email': federated_user.email,
                'name': federated_user.display_name,
                'provider_id': federated_user.provider_id,
                'roles': federated_user.roles,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.jwt_expiry)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {str(e)}")
            raise
    
    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validation token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Vérification utilisateur existe toujours
            user_id = payload.get('sub')
            if user_id in self.federated_users:
                user = self.federated_users[user_id]
                return {
                    'valid': True,
                    'user': user.to_dict(),
                    'payload': payload
                }
            else:
                return {'valid': False, 'error': 'User not found'}
                
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
        except Exception as e:
            logger.error(f"Error validating JWT token: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    async def sync_users_from_provider(self, provider_id: str) -> Dict[str, Any]:
        """Synchronisation utilisateurs depuis fournisseur"""
        try:
            if provider_id not in self.providers:
                raise ValueError(f"Provider {provider_id} not found")
            
            provider = self.providers[provider_id]
            
            if provider.provider_type == IdentityProviderType.LDAP:
                return await self._sync_ldap_users(provider)
            else:
                return {'success': False, 'error': 'Sync not supported for this provider type'}
                
        except Exception as e:
            logger.error(f"Error syncing users from provider: {str(e)}")
            raise
    
    async def _sync_ldap_users(self, provider: IdentityProvider) -> Dict[str, Any]:
        """Synchronisation utilisateurs LDAP"""
        try:
            # Simulation synchronisation LDAP
            # Dans une implémentation réelle, utiliser ldap3
            
            synced_count = 0
            updated_count = 0
            
            # Simulation récupération utilisateurs LDAP
            ldap_users = [
                {
                    'dn': 'cn=john.doe,ou=users,dc=company,dc=com',
                    'mail': 'john.doe@company.com',
                    'displayName': 'John Doe',
                    'memberOf': ['cn=developers,ou=groups,dc=company,dc=com']
                }
            ]
            
            for ldap_user in ldap_users:
                await self._create_federated_user(
                    provider=provider,
                    external_id=ldap_user['dn'],
                    email=ldap_user['mail'],
                    attributes=ldap_user
                )
                synced_count += 1
            
            # Mise à jour timestamp sync
            provider.last_sync = datetime.utcnow()
            
            return {
                'success': True,
                'synced_users': synced_count,
                'updated_users': updated_count,
                'last_sync': provider.last_sync.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing LDAP users: {str(e)}")
            raise
    
    async def get_provider_statistics(self) -> Dict[str, Any]:
        """Statistiques fournisseurs d'identité"""
        try:
            stats = {
                'total_providers': len(self.providers),
                'enabled_providers': len([p for p in self.providers.values() if p.enabled]),
                'provider_types': {},
                'total_federated_users': len(self.federated_users),
                'users_by_provider': {},
                'recent_logins': 0
            }
            
            # Statistiques par type
            for provider in self.providers.values():
                provider_type = provider.provider_type.value
                stats['provider_types'][provider_type] = stats['provider_types'].get(provider_type, 0) + 1
            
            # Utilisateurs par fournisseur
            for user in self.federated_users.values():
                provider_id = user.provider_id
                if provider_id in self.providers:
                    provider_name = self.providers[provider_id].name
                    stats['users_by_provider'][provider_name] = stats['users_by_provider'].get(provider_name, 0) + 1
            
            # Connexions récentes (24h)
            yesterday = datetime.utcnow() - timedelta(days=1)
            stats['recent_logins'] = len([
                u for u in self.federated_users.values()
                if u.last_login and u.last_login >= yesterday
            ])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting provider statistics: {str(e)}")
            raise

# Factory function
def create_identity_provider_manager(config: Dict[str, Any] = None) -> IdentityProviderManager:
    """Factory pour création gestionnaire IdP"""
    return IdentityProviderManager(config)

# Export classes principales
__all__ = [
    'IdentityProviderManager',
    'IdentityProvider',
    'FederatedUser',
    'IdentityProviderType',
    'AuthenticationMethod',
    'create_identity_provider_manager'
]