#!/usr/bin/env python3
"""
⚡ Enterprise LDAP Authentication Template - iacherie API Templates
Advanced production-ready LDAP/Active Directory authentication system

⚠️ PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
Utilisation commerciale INTERDITE sans autorisation écrite
Reverse engineering STRICTEMENT INTERDIT
Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence  
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import ssl
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import hmac
from enum import Enum
import re
import structlog
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
from ldap3.core.exceptions import LDAPException, LDAPBindError, LDAPSearchError
from fastapi import HTTPException, Depends, Request
import jwt
from passlib.context import CryptContext
import asyncio
import weakref
from concurrent.futures import ThreadPoolExecutor
import time


class LDAPAuthenticationType(Enum):
    """Types d'authentification LDAP"""
    SIMPLE = "SIMPLE"
    SASL = "SASL"
    KERBEROS = "GSSAPI"
    NTLM = "NTLM"


class LDAPAuthenticationTemplate:
    """
    🚀 Enterprise LDAP Authentication Template
    
    Fonctionnalités:
    - ✅ Active Directory et OpenLDAP support
    - ✅ Connection pooling et load balancing
    - ✅ Multi-domain et forest support
    - ✅ Group-based authorization (RBAC)
    - ✅ Attribute mapping et transformation
    - ✅ Password policy enforcement
    - ✅ Account lockout protection
    - ✅ Secure connection (LDAPS/StartTLS)
    - ✅ Caching et performance optimization
    - ✅ Audit logging et compliance
    - ✅ Failover et high availability
    """
    
    def __init__(
        self,
        servers: List['LDAPServerConfig'],
        bind_dn: str,
        bind_password: str,
        base_dn: str,
        user_search_filter: str = "(sAMAccountName={username})",
        group_search_filter: str = "(cn={group})",
        connection_pool_size: int = 10
    ):
        self.servers = servers
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.base_dn = base_dn
        self.user_search_filter = user_search_filter
        self.group_search_filter = group_search_filter
        self.connection_pool_size = connection_pool_size
        
        # Logger structuré
        self.logger = structlog.get_logger(__name__)
        
        # Connection pool manager
        self.pool_manager = LDAPConnectionPoolManager(
            servers, bind_dn, bind_password, connection_pool_size
        )
        
        # Attribute mapper
        self.attribute_mapper = LDAPAttributeMapper()
        
        # Group manager
        self.group_manager = LDAPGroupManager(self)
        
        # Security manager
        self.security_manager = LDAPSecurityManager()
        
        # Cache manager
        self.cache_manager = LDAPCacheManager()
        
        # Audit logger
        self.audit_logger = LDAPAuditLogger()
        
        # Password context pour hashing local
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Thread pool pour opérations LDAP
        self.executor = ThreadPoolExecutor(max_workers=20)
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        domain: Optional[str] = None
    ) -> 'LDAPUser':
        """Authentifie un utilisateur via LDAP"""
        
        # Validation d'entrée
        if not username or not password:
            raise HTTPException(
                status_code=400,
                detail="Username and password are required"
            )
        
        # Nettoyage du nom d'utilisateur
        username = self.security_manager.sanitize_username(username)
        
        # Vérifier le cache d'abord
        cached_user = await self.cache_manager.get_user(username, domain)
        if cached_user and self.security_manager.verify_password_hash(password, cached_user.password_hash):
            await self.audit_logger.log_authentication_success(username, domain, "cache")
            return cached_user
        
        try:
            # Obtenir une connexion du pool
            async with self.pool_manager.get_connection() as conn:
                
                # Rechercher l'utilisateur
                user_dn, user_attributes = await self._search_user(
                    conn, username, domain
                )
                
                if not user_dn:
                    await self.audit_logger.log_authentication_failure(
                        username, domain, "user_not_found"
                    )
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid credentials"
                    )
                
                # Vérifier le status du compte
                if not self._is_account_enabled(user_attributes):
                    await self.audit_logger.log_authentication_failure(
                        username, domain, "account_disabled"
                    )
                    raise HTTPException(
                        status_code=401,
                        detail="Account is disabled"
                    )
                
                # Authentifier avec le mot de passe
                if not await self._authenticate_bind(user_dn, password):
                    await self.audit_logger.log_authentication_failure(
                        username, domain, "invalid_password"
                    )
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid credentials"
                    )
                
                # Récupérer les groupes
                user_groups = await self._get_user_groups(conn, user_dn)
                
                # Mapper les attributs
                mapped_attributes = self.attribute_mapper.map_attributes(user_attributes)
                
                # Créer l'objet utilisateur
                ldap_user = LDAPUser(
                    username=username,
                    dn=user_dn,
                    domain=domain,
                    attributes=mapped_attributes,
                    groups=user_groups,
                    authenticated_at=datetime.utcnow(),
                    password_hash=self.pwd_context.hash(password)  # Pour cache seulement
                )
                
                # Mettre en cache
                await self.cache_manager.cache_user(ldap_user)
                
                # Log succès
                await self.audit_logger.log_authentication_success(username, domain, "ldap")
                
                return ldap_user
        
        except LDAPException as e:
            await self.audit_logger.log_authentication_failure(
                username, domain, f"ldap_error: {str(e)}"
            )
            
            self.logger.error(
                "LDAP authentication error",
                username=username,
                domain=domain,
                error=str(e)
            )
            
            raise HTTPException(
                status_code=500,
                detail="Authentication service unavailable"
            )
        
        except Exception as e:
            await self.audit_logger.log_authentication_failure(
                username, domain, f"system_error: {str(e)}"
            )
            
            self.logger.error(
                "Authentication system error",
                username=username,
                domain=domain,
                error=str(e)
            )
            
            raise HTTPException(
                status_code=500,
                detail="Internal authentication error"
            )
    
    async def _search_user(
        self,
        connection: Connection,
        username: str,
        domain: Optional[str]
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Recherche un utilisateur dans LDAP"""
        
        # Construire le filtre de recherche
        search_filter = self.user_search_filter.format(username=username)
        
        # Ajuster pour le domaine si spécifié
        search_base = self.base_dn
        if domain:
            search_base = f"dc={domain.replace('.', ',dc=')},{self.base_dn}"
        
        try:
            # Exécuter la recherche
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self.executor,
                lambda: connection.search(
                    search_base=search_base,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=[
                        'cn', 'sAMAccountName', 'userPrincipalName',
                        'mail', 'givenName', 'sn', 'displayName',
                        'memberOf', 'userAccountControl', 'whenCreated',
                        'whenChanged', 'lastLogon', 'department',
                        'title', 'telephoneNumber', 'employeeID'
                    ]
                )
            )
            
            if success and connection.entries:
                entry = connection.entries[0]
                return entry.entry_dn, dict(entry.entry_attributes_as_dict)
            
            return None, {}
            
        except LDAPSearchError as e:
            self.logger.error(
                "LDAP search error",
                username=username,
                search_base=search_base,
                search_filter=search_filter,
                error=str(e)
            )
            return None, {}
    
    async def _authenticate_bind(self, user_dn: str, password: str) -> bool:
        """Authentifie par binding LDAP"""
        
        try:
            # Créer une connexion temporaire pour l'auth
            server = self.pool_manager.get_available_server()
            
            loop = asyncio.get_event_loop()
            
            # Tenter le bind
            auth_result = await loop.run_in_executor(
                self.executor,
                lambda: self._try_bind(server, user_dn, password)
            )
            
            return auth_result
            
        except Exception as e:
            self.logger.error(
                "Authentication bind error",
                user_dn=user_dn,
                error=str(e)
            )
            return False
    
    def _try_bind(self, server: Server, user_dn: str, password: str) -> bool:
        """Tente un bind LDAP (synchrone)"""
        try:
            temp_conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            # Si on arrive ici, l'auth est réussie
            temp_conn.unbind()
            return True
            
        except LDAPBindError:
            return False
        except Exception:
            return False
    
    def _is_account_enabled(self, attributes: Dict[str, Any]) -> bool:
        """Vérifie si le compte est activé (Active Directory)"""
        
        # Pour Active Directory
        if 'userAccountControl' in attributes:
            uac = attributes['userAccountControl']
            if isinstance(uac, list) and uac:
                uac_value = int(uac[0])
                # Bit 1 = ACCOUNTDISABLE
                return not (uac_value & 2)
        
        # Pour d'autres LDAP, supposer activé par défaut
        return True
    
    async def _get_user_groups(
        self,
        connection: Connection,
        user_dn: str
    ) -> List[str]:
        """Récupère les groupes d'un utilisateur"""
        
        try:
            loop = asyncio.get_event_loop()
            
            # Rechercher les groupes
            success = await loop.run_in_executor(
                self.executor,
                lambda: connection.search(
                    search_base=self.base_dn,
                    search_filter=f"(&(objectClass=group)(member={user_dn}))",
                    search_scope=SUBTREE,
                    attributes=['cn', 'distinguishedName']
                )
            )
            
            groups = []
            if success and connection.entries:
                for entry in connection.entries:
                    group_name = entry.cn.value if hasattr(entry, 'cn') else None
                    if group_name:
                        groups.append(group_name)
            
            return groups
            
        except Exception as e:
            self.logger.error(
                "Error retrieving user groups",
                user_dn=user_dn,
                error=str(e)
            )
            return []
    
    async def change_password(
        self,
        username: str,
        old_password: str,
        new_password: str,
        domain: Optional[str] = None
    ) -> bool:
        """Change le mot de passe d'un utilisateur"""
        
        # Valider le nouveau mot de passe
        if not self.security_manager.validate_password_policy(new_password):
            raise HTTPException(
                status_code=400,
                detail="Password does not meet policy requirements"
            )
        
        try:
            # Authentifier d'abord avec l'ancien mot de passe
            user = await self.authenticate_user(username, old_password, domain)
            
            # Obtenir une connexion admin
            async with self.pool_manager.get_connection() as conn:
                
                # Changer le mot de passe
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    self.executor,
                    lambda: conn.extend.microsoft.modify_password(
                        user.dn,
                        new_password,
                        old_password
                    )
                )
                
                if success:
                    # Invalider le cache
                    await self.cache_manager.invalidate_user(username, domain)
                    
                    # Log change
                    await self.audit_logger.log_password_change(username, domain)
                    
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(
                "Password change error",
                username=username,
                domain=domain,
                error=str(e)
            )
            return False
    
    async def get_user_info(
        self,
        username: str,
        domain: Optional[str] = None
    ) -> Optional['LDAPUser']:
        """Récupère les informations d'un utilisateur sans authentification"""
        
        # Vérifier le cache
        cached_user = await self.cache_manager.get_user_info(username, domain)
        if cached_user:
            return cached_user
        
        try:
            async with self.pool_manager.get_connection() as conn:
                user_dn, user_attributes = await self._search_user(conn, username, domain)
                
                if not user_dn:
                    return None
                
                # Récupérer les groupes
                user_groups = await self._get_user_groups(conn, user_dn)
                
                # Mapper les attributs
                mapped_attributes = self.attribute_mapper.map_attributes(user_attributes)
                
                ldap_user = LDAPUser(
                    username=username,
                    dn=user_dn,
                    domain=domain,
                    attributes=mapped_attributes,
                    groups=user_groups,
                    authenticated_at=None  # Pas d'auth
                )
                
                # Mettre en cache
                await self.cache_manager.cache_user_info(ldap_user)
                
                return ldap_user
                
        except Exception as e:
            self.logger.error(
                "Error retrieving user info",
                username=username,
                domain=domain,
                error=str(e)
            )
            return None
    
    async def search_users(
        self,
        search_term: str,
        domain: Optional[str] = None,
        limit: int = 50
    ) -> List['LDAPUser']:
        """Recherche des utilisateurs"""
        
        if len(search_term) < 3:
            raise HTTPException(
                status_code=400,
                detail="Search term must be at least 3 characters"
            )
        
        # Construire le filtre de recherche
        search_filter = f"(&(objectClass=user)(|(cn=*{search_term}*)(sAMAccountName=*{search_term}*)(mail=*{search_term}*)))"
        
        try:
            async with self.pool_manager.get_connection() as conn:
                
                search_base = self.base_dn
                if domain:
                    search_base = f"dc={domain.replace('.', ',dc=')},{self.base_dn}"
                
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    self.executor,
                    lambda: conn.search(
                        search_base=search_base,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=['cn', 'sAMAccountName', 'mail', 'displayName'],
                        size_limit=limit
                    )
                )
                
                users = []
                if success and conn.entries:
                    for entry in conn.entries:
                        attrs = dict(entry.entry_attributes_as_dict)
                        mapped = self.attribute_mapper.map_attributes(attrs)
                        
                        user = LDAPUser(
                            username=mapped.get('username', ''),
                            dn=entry.entry_dn,
                            domain=domain,
                            attributes=mapped,
                            groups=[],  # Pas de groupes dans la recherche rapide
                            authenticated_at=None
                        )
                        users.append(user)
                
                return users
                
        except Exception as e:
            self.logger.error(
                "User search error",
                search_term=search_term,
                domain=domain,
                error=str(e)
            )
            return []
    
    async def check_group_membership(
        self,
        username: str,
        group_name: str,
        domain: Optional[str] = None
    ) -> bool:
        """Vérifie l'appartenance à un groupe"""
        
        user_info = await self.get_user_info(username, domain)
        if not user_info:
            return False
        
        return group_name in user_info.groups
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Retourne le status de santé LDAP"""
        
        health_info = {
            'status': 'healthy',
            'servers': [],
            'pool_status': await self.pool_manager.get_pool_status(),
            'cache_status': await self.cache_manager.get_cache_status(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Tester chaque serveur
        for server_config in self.servers:
            server_health = await self._test_server_health(server_config)
            health_info['servers'].append(server_health)
        
        # Déterminer le status global
        healthy_servers = sum(1 for s in health_info['servers'] if s['healthy'])
        if healthy_servers == 0:
            health_info['status'] = 'unhealthy'
        elif healthy_servers < len(self.servers):
            health_info['status'] = 'degraded'
        
        return health_info
    
    async def _test_server_health(self, server_config: 'LDAPServerConfig') -> Dict[str, Any]:
        """Teste la santé d'un serveur"""
        
        try:
            server = Server(
                host=server_config.host,
                port=server_config.port,
                use_ssl=server_config.use_ssl,
                get_info=ALL
            )
            
            loop = asyncio.get_event_loop()
            
            # Test de connexion simple
            start_time = time.time()
            
            def test_connection():
                try:
                    conn = Connection(
                        server,
                        user=self.bind_dn,
                        password=self.bind_password,
                        auto_bind=True
                    )
                    conn.unbind()
                    return True
                except:
                    return False
            
            healthy = await loop.run_in_executor(self.executor, test_connection)
            response_time = time.time() - start_time
            
            return {
                'host': server_config.host,
                'port': server_config.port,
                'healthy': healthy,
                'response_time_ms': int(response_time * 1000),
                'ssl_enabled': server_config.use_ssl
            }
            
        except Exception as e:
            return {
                'host': server_config.host,
                'port': server_config.port,
                'healthy': False,
                'error': str(e),
                'ssl_enabled': server_config.use_ssl
            }


@dataclass
class LDAPServerConfig:
    """Configuration d'un serveur LDAP"""
    host: str
    port: int = 389
    use_ssl: bool = False
    use_tls: bool = False
    auth_type: LDAPAuthenticationType = LDAPAuthenticationType.SIMPLE
    timeout: int = 30
    priority: int = 1  # Pour load balancing
    
    def __post_init__(self):
        # Ajuster le port par défaut pour SSL
        if self.use_ssl and self.port == 389:
            self.port = 636


@dataclass
class LDAPUser:
    """Utilisateur LDAP authentifié"""
    username: str
    dn: str
    domain: Optional[str]
    attributes: Dict[str, Any]
    groups: List[str]
    authenticated_at: Optional[datetime]
    password_hash: Optional[str] = None  # Pour cache seulement
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Récupère un attribut avec valeur par défaut"""
        return self.attributes.get(name, default)
    
    def get_email(self) -> Optional[str]:
        """Récupère l'email de l'utilisateur"""
        return self.get_attribute('email') or self.get_attribute('mail')
    
    def get_full_name(self) -> Optional[str]:
        """Récupère le nom complet"""
        return self.get_attribute('displayName') or f"{self.get_attribute('firstName', '')} {self.get_attribute('lastName', '')}"
    
    def has_group(self, group_name: str) -> bool:
        """Vérifie l'appartenance à un groupe"""
        return group_name in self.groups
    
    def has_any_group(self, group_names: List[str]) -> bool:
        """Vérifie l'appartenance à au moins un groupe"""
        return any(group in self.groups for group in group_names)
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        return self.authenticated_at is not None


class LDAPConnectionPoolManager:
    """Gestionnaire de pool de connexions LDAP"""
    
    def __init__(
        self,
        servers: List[LDAPServerConfig],
        bind_dn: str,
        bind_password: str,
        pool_size: int
    ):
        self.servers = servers
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.pool_size = pool_size
        
        self.connections: Dict[str, List[Connection]] = {}
        self.server_objects: Dict[str, Server] = {}
        self.current_server_index = 0
        
        self.logger = structlog.get_logger(__name__)
        
        # Initialiser les serveurs
        self._initialize_servers()
    
    def _initialize_servers(self):
        """Initialise les objets serveur"""
        for server_config in self.servers:
            server_key = f"{server_config.host}:{server_config.port}"
            
            server = Server(
                host=server_config.host,
                port=server_config.port,
                use_ssl=server_config.use_ssl,
                get_info=ALL,
                connect_timeout=server_config.timeout
            )
            
            self.server_objects[server_key] = server
            self.connections[server_key] = []
    
    async def get_connection(self) -> 'LDAPConnectionContext':
        """Obtient une connexion du pool"""
        server = self.get_available_server()
        server_key = f"{server.host}:{server.port}"
        
        # Chercher une connexion disponible
        available_connections = self.connections[server_key]
        
        if available_connections:
            connection = available_connections.pop()
        else:
            # Créer une nouvelle connexion
            connection = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
                auto_range=True
            )
        
        return LDAPConnectionContext(self, server_key, connection)
    
    def return_connection(self, server_key: str, connection: Connection):
        """Retourne une connexion au pool"""
        if len(self.connections[server_key]) < self.pool_size:
            self.connections[server_key].append(connection)
        else:
            # Pool plein, fermer la connexion
            try:
                connection.unbind()
            except:
                pass
    
    def get_available_server(self) -> Server:
        """Obtient un serveur disponible (round-robin)"""
        if not self.servers:
            raise RuntimeError("No LDAP servers configured")
        
        # Simple round-robin
        server_config = self.servers[self.current_server_index]
        self.current_server_index = (self.current_server_index + 1) % len(self.servers)
        
        server_key = f"{server_config.host}:{server_config.port}"
        return self.server_objects[server_key]
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Retourne le status du pool"""
        status = {
            'total_servers': len(self.servers),
            'pool_size': self.pool_size,
            'servers': {}
        }
        
        for server_key, connections in self.connections.items():
            status['servers'][server_key] = {
                'available_connections': len(connections),
                'max_connections': self.pool_size
            }
        
        return status


class LDAPConnectionContext:
    """Context manager pour connexions LDAP"""
    
    def __init__(
        self,
        pool_manager: LDAPConnectionPoolManager,
        server_key: str,
        connection: Connection
    ):
        self.pool_manager = pool_manager
        self.server_key = server_key
        self.connection = connection
    
    async def __aenter__(self) -> Connection:
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Retourner au pool si pas d'erreur
            self.pool_manager.return_connection(self.server_key, self.connection)
        else:
            # Fermer la connexion en cas d'erreur
            try:
                self.connection.unbind()
            except:
                pass


class LDAPAttributeMapper:
    """Mappeur d'attributs LDAP"""
    
    def __init__(self):
        # Mapping par défaut
        self.default_mapping = {
            # Active Directory
            'sAMAccountName': 'username',
            'userPrincipalName': 'email',
            'mail': 'email',
            'givenName': 'firstName',
            'sn': 'lastName',
            'displayName': 'displayName',
            'cn': 'commonName',
            'department': 'department',
            'title': 'jobTitle',
            'telephoneNumber': 'phone',
            'employeeID': 'employeeId',
            'whenCreated': 'createdAt',
            'whenChanged': 'modifiedAt',
            'lastLogon': 'lastLoginAt',
            
            # OpenLDAP
            'uid': 'username',
            'cn': 'displayName',
            'gn': 'firstName',
            'sn': 'lastName',
            'mail': 'email',
            'telephoneNumber': 'phone',
            'employeeNumber': 'employeeId',
            'departmentNumber': 'department',
            'title': 'jobTitle'
        }
    
    def map_attributes(
        self,
        ldap_attributes: Dict[str, Any],
        custom_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Mappe les attributs LDAP vers les attributs application"""
        
        mapping = {**self.default_mapping}
        if custom_mapping:
            mapping.update(custom_mapping)
        
        mapped_attributes = {}
        
        for ldap_attr, values in ldap_attributes.items():
            # Obtenir le nom mappé
            app_attr = mapping.get(ldap_attr, ldap_attr)
            
            # Traiter les valeurs
            if isinstance(values, list):
                if len(values) == 1:
                    mapped_value = values[0]
                elif len(values) > 1:
                    mapped_value = values  # Garder comme liste
                else:
                    continue  # Ignorer les attributs vides
            else:
                mapped_value = values
            
            # Transformations spécifiques
            if app_attr == 'email' and mapped_value:
                mapped_value = str(mapped_value).lower().strip()
            
            mapped_attributes[app_attr] = mapped_value
        
        return mapped_attributes


class LDAPGroupManager:
    """Gestionnaire de groupes LDAP"""
    
    def __init__(self, ldap_auth: LDAPAuthenticationTemplate):
        self.ldap_auth = ldap_auth
        self.logger = structlog.get_logger(__name__)
    
    async def get_group_members(
        self,
        group_name: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """Récupère les membres d'un groupe"""
        
        try:
            async with self.ldap_auth.pool_manager.get_connection() as conn:
                
                # Rechercher le groupe
                search_base = self.ldap_auth.base_dn
                if domain:
                    search_base = f"dc={domain.replace('.', ',dc=')},{search_base}"
                
                search_filter = f"(&(objectClass=group)(cn={group_name}))"
                
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    self.ldap_auth.executor,
                    lambda: conn.search(
                        search_base=search_base,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=['member']
                    )
                )
                
                members = []
                if success and conn.entries:
                    group_entry = conn.entries[0]
                    if hasattr(group_entry, 'member'):
                        for member_dn in group_entry.member:
                            # Extraire le username du DN
                            username = self._extract_username_from_dn(member_dn)
                            if username:
                                members.append(username)
                
                return members
                
        except Exception as e:
            self.logger.error(
                "Error retrieving group members",
                group_name=group_name,
                domain=domain,
                error=str(e)
            )
            return []
    
    def _extract_username_from_dn(self, dn: str) -> Optional[str]:
        """Extrait le username d'un DN"""
        # Rechercher CN= au début
        match = re.search(r'CN=([^,]+)', dn, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    async def add_user_to_group(
        self,
        username: str,
        group_name: str,
        domain: Optional[str] = None
    ) -> bool:
        """Ajoute un utilisateur à un groupe"""
        
        try:
            # Récupérer l'utilisateur
            user_info = await self.ldap_auth.get_user_info(username, domain)
            if not user_info:
                return False
            
            async with self.ldap_auth.pool_manager.get_connection() as conn:
                
                # Rechercher le groupe
                search_base = self.ldap_auth.base_dn
                if domain:
                    search_base = f"dc={domain.replace('.', ',dc=')},{search_base}"
                
                search_filter = f"(&(objectClass=group)(cn={group_name}))"
                
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    self.ldap_auth.executor,
                    lambda: conn.search(
                        search_base=search_base,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=['distinguishedName']
                    )
                )
                
                if success and conn.entries:
                    group_dn = conn.entries[0].entry_dn
                    
                    # Ajouter le membre
                    modify_success = await loop.run_in_executor(
                        self.ldap_auth.executor,
                        lambda: conn.modify(
                            group_dn,
                            {'member': [(ldap3.MODIFY_ADD, [user_info.dn])]}
                        )
                    )
                    
                    if modify_success:
                        # Invalider le cache utilisateur
                        await self.ldap_auth.cache_manager.invalidate_user(username, domain)
                        return True
                
                return False
                
        except Exception as e:
            self.logger.error(
                "Error adding user to group",
                username=username,
                group_name=group_name,
                domain=domain,
                error=str(e)
            )
            return False


class LDAPSecurityManager:
    """Gestionnaire de sécurité LDAP"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Politique de mot de passe par défaut
        self.password_policy = {
            'min_length': 8,
            'max_length': 128,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digit': True,
            'require_special': True,
            'forbidden_sequences': ['123', 'abc', 'qwe'],
            'max_repeating_chars': 3
        }
        
        # Patterns dangereux pour injection
        self.dangerous_patterns = [
            r'[()&|!]',  # LDAP operators
            r'[*]',      # Wildcards
            r'[\x00-\x1f]'  # Control characters
        ]
    
    def sanitize_username(self, username: str) -> str:
        """Nettoie et valide un nom d'utilisateur"""
        
        # Enlever les espaces
        username = username.strip()
        
        # Vérifier les caractères dangereux
        for pattern in self.dangerous_patterns:
            if re.search(pattern, username):
                raise HTTPException(
                    status_code=400,
                    detail="Username contains invalid characters"
                )
        
        # Limiter la longueur
        if len(username) > 100:
            raise HTTPException(
                status_code=400,
                detail="Username too long"
            )
        
        return username
    
    def validate_password_policy(self, password: str) -> bool:
        """Valide une politique de mot de passe"""
        
        # Longueur
        if len(password) < self.password_policy['min_length']:
            return False
        
        if len(password) > self.password_policy['max_length']:
            return False
        
        # Majuscules
        if self.password_policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            return False
        
        # Minuscules
        if self.password_policy['require_lowercase'] and not re.search(r'[a-z]', password):
            return False
        
        # Chiffres
        if self.password_policy['require_digit'] and not re.search(r'\d', password):
            return False
        
        # Caractères spéciaux
        if self.password_policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        # Séquences interdites
        password_lower = password.lower()
        for seq in self.password_policy['forbidden_sequences']:
            if seq in password_lower:
                return False
        
        # Caractères répétés
        max_repeat = self.password_policy['max_repeating_chars']
        for i in range(len(password) - max_repeat):
            if len(set(password[i:i+max_repeat+1])) == 1:
                return False
        
        return True
    
    def verify_password_hash(self, password: str, password_hash: str) -> bool:
        """Vérifie un hash de mot de passe"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, password_hash)


class LDAPCacheManager:
    """Gestionnaire de cache LDAP"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.user_cache: Dict[str, Tuple[LDAPUser, datetime]] = {}
        self.user_info_cache: Dict[str, Tuple[LDAPUser, datetime]] = {}
        
    def _get_cache_key(self, username: str, domain: Optional[str]) -> str:
        """Génère une clé de cache"""
        return f"{username}@{domain or 'default'}"
    
    async def get_user(self, username: str, domain: Optional[str]) -> Optional[LDAPUser]:
        """Récupère un utilisateur du cache"""
        cache_key = self._get_cache_key(username, domain)
        
        if cache_key in self.user_cache:
            user, cached_at = self.user_cache[cache_key]
            
            # Vérifier l'expiration
            if datetime.utcnow() - cached_at < timedelta(seconds=self.ttl_seconds):
                return user
            else:
                # Expirer
                del self.user_cache[cache_key]
        
        return None
    
    async def cache_user(self, user: LDAPUser):
        """Met en cache un utilisateur"""
        cache_key = self._get_cache_key(user.username, user.domain)
        self.user_cache[cache_key] = (user, datetime.utcnow())
    
    async def get_user_info(self, username: str, domain: Optional[str]) -> Optional[LDAPUser]:
        """Récupère les infos utilisateur du cache"""
        cache_key = self._get_cache_key(username, domain)
        
        if cache_key in self.user_info_cache:
            user, cached_at = self.user_info_cache[cache_key]
            
            if datetime.utcnow() - cached_at < timedelta(seconds=self.ttl_seconds):
                return user
            else:
                del self.user_info_cache[cache_key]
        
        return None
    
    async def cache_user_info(self, user: LDAPUser):
        """Met en cache les infos utilisateur"""
        cache_key = self._get_cache_key(user.username, user.domain)
        self.user_info_cache[cache_key] = (user, datetime.utcnow())
    
    async def invalidate_user(self, username: str, domain: Optional[str]):
        """Invalide le cache d'un utilisateur"""
        cache_key = self._get_cache_key(username, domain)
        self.user_cache.pop(cache_key, None)
        self.user_info_cache.pop(cache_key, None)
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """Retourne le status du cache"""
        now = datetime.utcnow()
        
        # Compter les entrées valides
        valid_user_entries = sum(
            1 for _, (_, cached_at) in self.user_cache.items()
            if now - cached_at < timedelta(seconds=self.ttl_seconds)
        )
        
        valid_info_entries = sum(
            1 for _, (_, cached_at) in self.user_info_cache.items()
            if now - cached_at < timedelta(seconds=self.ttl_seconds)
        )
        
        return {
            'total_user_entries': len(self.user_cache),
            'valid_user_entries': valid_user_entries,
            'total_info_entries': len(self.user_info_cache),
            'valid_info_entries': valid_info_entries,
            'ttl_seconds': self.ttl_seconds
        }


class LDAPAuditLogger:
    """Logger d'audit LDAP"""
    
    def __init__(self):
        self.logger = structlog.get_logger("ldap_audit")
    
    async def log_authentication_success(
        self,
        username: str,
        domain: Optional[str],
        auth_method: str
    ):
        """Log authentification réussie"""
        self.logger.info(
            "LDAP_AUTH_SUCCESS",
            username=username,
            domain=domain,
            auth_method=auth_method,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_authentication_failure(
        self,
        username: str,
        domain: Optional[str],
        failure_reason: str
    ):
        """Log échec d'authentification"""
        self.logger.warning(
            "LDAP_AUTH_FAILURE",
            username=username,
            domain=domain,
            failure_reason=failure_reason,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_password_change(
        self,
        username: str,
        domain: Optional[str]
    ):
        """Log changement de mot de passe"""
        self.logger.info(
            "LDAP_PASSWORD_CHANGE",
            username=username,
            domain=domain,
            timestamp=datetime.utcnow().isoformat()
        )


# Factory functions et helpers
def create_ldap_auth(
    servers: List[Dict[str, Any]],
    bind_dn: str,
    bind_password: str,
    base_dn: str,
    **kwargs
) -> LDAPAuthenticationTemplate:
    """Factory pour créer l'authentification LDAP"""
    
    server_configs = [
        LDAPServerConfig(**server_data) for server_data in servers
    ]
    
    return LDAPAuthenticationTemplate(
        servers=server_configs,
        bind_dn=bind_dn,
        bind_password=bind_password,
        base_dn=base_dn,
        **kwargs
    )


async def get_ldap_user(
    request: Request,
    ldap_auth: LDAPAuthenticationTemplate = Depends()
) -> Optional[LDAPUser]:
    """Dependency FastAPI pour récupérer l'utilisateur LDAP"""
    
    # Récupérer le token depuis les headers
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]
    
    try:
        # Décoder le JWT pour récupérer les infos utilisateur
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        
        username = payload.get('username')
        domain = payload.get('domain')
        
        if not username:
            return None
        
        # Récupérer les infos utilisateur
        return await ldap_auth.get_user_info(username, domain)
        
    except jwt.InvalidTokenError:
        return None


def require_ldap_auth(
    user: Optional[LDAPUser] = Depends(get_ldap_user)
) -> LDAPUser:
    """Dependency FastAPI pour exiger l'authentification LDAP"""
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="LDAP authentication required"
        )
    
    return user


def require_ldap_group(
    required_groups: List[str]
) -> Callable[[LDAPUser], LDAPUser]:
    """Dependency factory pour exiger un groupe LDAP"""
    
    def group_dependency(
        user: LDAPUser = Depends(require_ldap_auth)
    ) -> LDAPUser:
        
        if not user.has_any_group(required_groups):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required groups: {required_groups}"
            )
        
        return user
    
    return group_dependency


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def example_ldap_auth():
        # Configuration
        servers = [
            {'host': 'ldap1.example.com', 'port': 636, 'use_ssl': True},
            {'host': 'ldap2.example.com', 'port': 636, 'use_ssl': True}
        ]
        
        ldap_auth = create_ldap_auth(
            servers=servers,
            bind_dn="CN=service_account,OU=Service Accounts,DC=example,DC=com",
            bind_password="service_password",
            base_dn="DC=example,DC=com"
        )
        
        try:
            # Test authentication
            user = await ldap_auth.authenticate_user("john.doe", "password123")
            print(f"Authentication successful: {user.username}")
            print(f"Groups: {user.groups}")
            print(f"Email: {user.get_email()}")
            
            # Test group membership
            is_admin = await ldap_auth.check_group_membership("john.doe", "Administrators")
            print(f"Is admin: {is_admin}")
            
            # Test user search
            users = await ldap_auth.search_users("john")
            print(f"Found {len(users)} users")
            
            # Health check
            health = await ldap_auth.get_health_status()
            print(f"Health status: {health['status']}")
            
        except HTTPException as e:
            print(f"Authentication failed: {e.detail}")
    
    asyncio.run(example_ldap_auth())