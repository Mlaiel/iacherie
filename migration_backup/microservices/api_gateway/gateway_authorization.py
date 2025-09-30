#!/usr/bin/env python3
"""
🛡️ Gateway Authorization Service - Enterprise Grade
Service d'autorisation enterprise pour API Gateway Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import re
from collections import defaultdict

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Permission(Enum):
    """Types de permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"

class ResourceType(Enum):
    """Types de ressources"""
    USER = "user"
    CONTENT = "content"
    API = "api"
    SYSTEM = "system"
    DATA = "data"

class AuthorizationDecision(Enum):
    """Décisions d'autorisation"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"

@dataclass
class Resource:
    """Ressource à protéger"""
    resource_id: str
    resource_type: ResourceType
    path: str
    owner_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Policy:
    """Politique d'autorisation"""
    policy_id: str
    name: str
    description: str
    resource_pattern: str
    subjects: List[str]  # users, roles, groups
    permissions: List[Permission]
    conditions: Dict[str, Any]
    effect: AuthorizationDecision
    priority: int = 1
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class AuthorizationContext:
    """Contexte d'autorisation"""
    user_id: str
    roles: List[str]
    scopes: List[str]
    request_path: str
    request_method: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AuthorizationResult:
    """Résultat d'autorisation"""
    decision: AuthorizationDecision
    reason: str
    matched_policies: List[str] = None
    required_permissions: List[Permission] = None
    conditional_requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.matched_policies is None:
            self.matched_policies = []
        if self.required_permissions is None:
            self.required_permissions = []
        if self.conditional_requirements is None:
            self.conditional_requirements = {}

class GatewayAuthorizationService:
    """
    🛡️ Service d'autorisation API Gateway enterprise
    Gestion complète des autorisations basées sur des politiques
    """
    
    def __init__(self):
        """Initialisation du service d'autorisation"""
        
        # Stockage des politiques et ressources
        self.policies: Dict[str, Policy] = {}
        self.resources: Dict[str, Resource] = {}
        self.role_hierarchy: Dict[str, List[str]] = {}
        
        # Cache d'autorisation
        self.authorization_cache: Dict[str, AuthorizationResult] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Métriques enterprise
        self.metrics = {
            'total_authorization_checks': 0,
            'allowed_requests': 0,
            'denied_requests': 0,
            'conditional_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'policy_evaluations': 0
        }
        
        # Configuration par défaut
        self._setup_default_policies()
        
        logger.info("🛡️ Gateway Authorization Service initialisé")
    
    def _setup_default_policies(self):
        """Configuration des politiques par défaut"""
        try:
            # Politique admin complète
            admin_policy = Policy(
                policy_id="admin_full_access",
                name="Administration complète",
                description="Accès complet pour les administrateurs",
                resource_pattern="/*",
                subjects=["role:admin"],
                permissions=[Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN],
                conditions={},
                effect=AuthorizationDecision.ALLOW,
                priority=100
            )
            self.policies[admin_policy.policy_id] = admin_policy
            
            # Politique lecture publique
            public_read_policy = Policy(
                policy_id="public_read_access",
                name="Lecture publique",
                description="Accès en lecture pour le contenu public",
                resource_pattern="/api/public/*",
                subjects=["role:viewer", "role:creator"],
                permissions=[Permission.READ],
                conditions={},
                effect=AuthorizationDecision.ALLOW,
                priority=10
            )
            self.policies[public_read_policy.policy_id] = public_read_policy
            
            # Politique créateur
            creator_policy = Policy(
                policy_id="creator_content_access",
                name="Accès créateur",
                description="Accès aux contenus pour les créateurs",
                resource_pattern="/api/content/*",
                subjects=["role:creator"],
                permissions=[Permission.READ, Permission.WRITE],
                conditions={"owner_match": True},
                effect=AuthorizationDecision.CONDITIONAL,
                priority=50
            )
            self.policies[creator_policy.policy_id] = creator_policy
            
            # Hiérarchie des rôles
            self.role_hierarchy = {
                "admin": ["creator", "viewer"],
                "creator": ["viewer"],
                "viewer": []
            }
            
            logger.info("✅ Politiques par défaut configurées")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration politiques par défaut: {e}")
    
    async def create_policy(
        self,
        name: str,
        description: str,
        resource_pattern: str,
        subjects: List[str],
        permissions: List[Permission],
        conditions: Optional[Dict[str, Any]] = None,
        effect: AuthorizationDecision = AuthorizationDecision.ALLOW,
        priority: int = 1
    ) -> str:
        """
        Créer une nouvelle politique d'autorisation
        
        Args:
            name: Nom de la politique
            description: Description
            resource_pattern: Pattern de ressource (regex)
            subjects: Sujets (users, roles, groups)
            permissions: Permissions requises
            conditions: Conditions additionnelles
            effect: Effet (ALLOW/DENY/CONDITIONAL)
            priority: Priorité (plus élevé = plus prioritaire)
        
        Returns:
            ID de la politique créée
        """
        try:
            policy_id = f"policy_{uuid.uuid4().hex[:8]}"
            
            policy = Policy(
                policy_id=policy_id,
                name=name,
                description=description,
                resource_pattern=resource_pattern,
                subjects=subjects,
                permissions=permissions,
                conditions=conditions or {},
                effect=effect,
                priority=priority
            )
            
            self.policies[policy_id] = policy
            
            # Invalidation du cache
            self.authorization_cache.clear()
            
            logger.info(f"✅ Politique créée: {policy_id} - {name}")
            return policy_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création politique: {e}")
            raise
    
    async def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        path: str,
        owner_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enregistrer une ressource
        
        Args:
            resource_id: ID unique de la ressource
            resource_type: Type de ressource
            path: Chemin de la ressource
            owner_id: Propriétaire de la ressource
            metadata: Métadonnées additionnelles
        
        Returns:
            True si succès
        """
        try:
            resource = Resource(
                resource_id=resource_id,
                resource_type=resource_type,
                path=path,
                owner_id=owner_id,
                metadata=metadata or {}
            )
            
            self.resources[resource_id] = resource
            
            logger.info(f"✅ Ressource enregistrée: {resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement ressource: {e}")
            return False
    
    async def authorize(
        self,
        context: AuthorizationContext,
        required_permissions: List[Permission]
    ) -> AuthorizationResult:
        """
        Autoriser une requête
        
        Args:
            context: Contexte d'autorisation
            required_permissions: Permissions requises
        
        Returns:
            Résultat d'autorisation
        """
        try:
            self.metrics['total_authorization_checks'] += 1
            
            # Vérification du cache
            cache_key = self._generate_cache_key(context, required_permissions)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.metrics['cache_hits'] += 1
                return cached_result
            
            self.metrics['cache_misses'] += 1
            
            # Évaluation des politiques
            result = await self._evaluate_policies(context, required_permissions)
            
            # Mise en cache
            self._cache_result(cache_key, result)
            
            # Mise à jour des métriques
            if result.decision == AuthorizationDecision.ALLOW:
                self.metrics['allowed_requests'] += 1
            elif result.decision == AuthorizationDecision.DENY:
                self.metrics['denied_requests'] += 1
            else:
                self.metrics['conditional_requests'] += 1
            
            logger.info(f"🔍 Autorisation: {result.decision.value} pour {context.user_id} sur {context.request_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur autorisation: {e}")
            return AuthorizationResult(
                decision=AuthorizationDecision.DENY,
                reason=f"Erreur d'autorisation: {str(e)}"
            )
    
    async def _evaluate_policies(
        self,
        context: AuthorizationContext,
        required_permissions: List[Permission]
    ) -> AuthorizationResult:
        """Évaluer les politiques d'autorisation"""
        try:
            # Récupération des rôles étendus (hiérarchie)
            extended_roles = self._get_extended_roles(context.roles)
            
            # Tri des politiques par priorité
            sorted_policies = sorted(
                self.policies.values(),
                key=lambda p: p.priority,
                reverse=True
            )
            
            matched_policies = []
            allow_policies = []
            deny_policies = []
            conditional_policies = []
            
            # Évaluation de chaque politique
            for policy in sorted_policies:
                if not policy.is_active:
                    continue
                
                self.metrics['policy_evaluations'] += 1
                
                # Vérification du pattern de ressource
                if not self._match_resource_pattern(policy.resource_pattern, context.request_path):
                    continue
                
                # Vérification des sujets
                if not self._match_subjects(policy.subjects, context.user_id, extended_roles):
                    continue
                
                # Vérification des permissions
                if not self._match_permissions(policy.permissions, required_permissions):
                    continue
                
                matched_policies.append(policy.policy_id)
                
                # Évaluation des conditions
                condition_result = await self._evaluate_conditions(policy.conditions, context)
                
                if policy.effect == AuthorizationDecision.ALLOW:
                    if condition_result['passed']:
                        allow_policies.append(policy)
                    elif condition_result['conditional']:
                        conditional_policies.append((policy, condition_result['requirements']))
                elif policy.effect == AuthorizationDecision.DENY:
                    if condition_result['passed']:
                        deny_policies.append(policy)
                elif policy.effect == AuthorizationDecision.CONDITIONAL:
                    conditional_policies.append((policy, condition_result['requirements']))
            
            # Détermination de la décision finale
            if deny_policies:
                # Toute politique DENY l'emporte
                return AuthorizationResult(
                    decision=AuthorizationDecision.DENY,
                    reason=f"Accès refusé par politique: {deny_policies[0].name}",
                    matched_policies=matched_policies
                )
            
            if allow_policies:
                # Au moins une politique ALLOW
                return AuthorizationResult(
                    decision=AuthorizationDecision.ALLOW,
                    reason=f"Accès autorisé par politique: {allow_policies[0].name}",
                    matched_policies=matched_policies
                )
            
            if conditional_policies:
                # Politiques conditionnelles
                requirements = {}
                for policy, reqs in conditional_policies:
                    requirements.update(reqs)
                
                return AuthorizationResult(
                    decision=AuthorizationDecision.CONDITIONAL,
                    reason="Accès conditionnel - vérifications supplémentaires requises",
                    matched_policies=matched_policies,
                    conditional_requirements=requirements
                )
            
            # Aucune politique ne correspond - DENY par défaut
            return AuthorizationResult(
                decision=AuthorizationDecision.DENY,
                reason="Aucune politique d'autorisation ne correspond",
                matched_policies=matched_policies,
                required_permissions=required_permissions
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation politiques: {e}")
            return AuthorizationResult(
                decision=AuthorizationDecision.DENY,
                reason="Erreur lors de l'évaluation des politiques"
            )
    
    def _match_resource_pattern(self, pattern: str, resource_path: str) -> bool:
        """Vérifier si le chemin correspond au pattern"""
        try:
            # Conversion du pattern en regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            return bool(re.match(regex_pattern, resource_path))
        except:
            return False
    
    def _match_subjects(self, subjects: List[str], user_id: str, roles: List[str]) -> bool:
        """Vérifier si l'utilisateur correspond aux sujets"""
        try:
            for subject in subjects:
                if subject == f"user:{user_id}":
                    return True
                elif subject.startswith("role:"):
                    role_name = subject[5:]  # Enlever "role:"
                    if role_name in roles:
                        return True
                elif subject == "*":  # Wildcard
                    return True
            
            return False
        except:
            return False
    
    def _match_permissions(
        self,
        policy_permissions: List[Permission],
        required_permissions: List[Permission]
    ) -> bool:
        """Vérifier si les permissions correspondent"""
        try:
            # Vérification que toutes les permissions requises sont dans la politique
            return all(perm in policy_permissions for perm in required_permissions)
        except:
            return False
    
    def _get_extended_roles(self, base_roles: List[str]) -> List[str]:
        """Obtenir les rôles étendus avec hiérarchie"""
        try:
            extended = set(base_roles)
            
            for role in base_roles:
                if role in self.role_hierarchy:
                    extended.update(self.role_hierarchy[role])
            
            return list(extended)
        except:
            return base_roles
    
    async def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: AuthorizationContext
    ) -> Dict[str, Any]:
        """Évaluer les conditions d'une politique"""
        try:
            if not conditions:
                return {'passed': True, 'conditional': False, 'requirements': {}}
            
            result = {'passed': True, 'conditional': False, 'requirements': {}}
            
            # Vérification owner_match
            if 'owner_match' in conditions and conditions['owner_match']:
                resource_path = context.request_path
                resource = self._find_resource_by_path(resource_path)
                
                if resource and resource.owner_id:
                    if resource.owner_id != context.user_id:
                        result['passed'] = False
                        result['conditional'] = True
                        result['requirements']['owner_verification'] = {
                            'required_owner': resource.owner_id,
                            'current_user': context.user_id
                        }
                
            # Vérification time_range
            if 'time_range' in conditions:
                time_range = conditions['time_range']
                current_hour = context.timestamp.hour
                
                if not (time_range.get('start', 0) <= current_hour <= time_range.get('end', 23)):
                    result['passed'] = False
                    result['requirements']['time_restriction'] = time_range
            
            # Vérification IP
            if 'allowed_ips' in conditions and context.ip_address:
                allowed_ips = conditions['allowed_ips']
                if context.ip_address not in allowed_ips:
                    result['passed'] = False
                    result['requirements']['ip_restriction'] = allowed_ips
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur évaluation conditions: {e}")
            return {'passed': False, 'conditional': False, 'requirements': {}}
    
    def _find_resource_by_path(self, path: str) -> Optional[Resource]:
        """Trouver une ressource par son chemin"""
        for resource in self.resources.values():
            if resource.path == path:
                return resource
        return None
    
    def _generate_cache_key(
        self,
        context: AuthorizationContext,
        required_permissions: List[Permission]
    ) -> str:
        """Générer une clé de cache"""
        try:
            key_parts = [
                context.user_id,
                "|".join(sorted(context.roles)),
                "|".join(sorted(context.scopes)),
                context.request_path,
                context.request_method,
                "|".join(sorted([p.value for p in required_permissions]))
            ]
            return hashlib.sha256("|".join(key_parts).encode()).hexdigest()
        except:
            return f"cache_{uuid.uuid4().hex[:8]}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[AuthorizationResult]:
        """Récupérer un résultat du cache"""
        try:
            # Simulation de cache avec TTL
            # En production, utiliser Redis ou un cache distribué
            return self.authorization_cache.get(cache_key)
        except:
            return None
    
    def _cache_result(self, cache_key: str, result: AuthorizationResult) -> None:
        """Mettre en cache un résultat"""
        try:
            # Limitation de la taille du cache
            if len(self.authorization_cache) >= 10000:
                # Nettoyage simple - en production, utiliser LRU
                self.authorization_cache.clear()
            
            self.authorization_cache[cache_key] = result
        except Exception as e:
            logger.error(f"❌ Erreur mise en cache: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Récupération des métriques
        
        Returns:
            Métriques d'autorisation
        """
        return {
            **self.metrics,
            'total_policies': len(self.policies),
            'active_policies': sum(1 for p in self.policies.values() if p.is_active),
            'total_resources': len(self.resources),
            'cache_size': len(self.authorization_cache),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def list_policies(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Lister les politiques
        
        Args:
            active_only: Ne lister que les politiques actives
        
        Returns:
            Liste des politiques
        """
        try:
            policies = []
            for policy in self.policies.values():
                if active_only and not policy.is_active:
                    continue
                
                policies.append({
                    'policy_id': policy.policy_id,
                    'name': policy.name,
                    'description': policy.description,
                    'resource_pattern': policy.resource_pattern,
                    'subjects': policy.subjects,
                    'permissions': [p.value for p in policy.permissions],
                    'effect': policy.effect.value,
                    'priority': policy.priority,
                    'is_active': policy.is_active,
                    'created_at': policy.created_at.isoformat()
                })
            
            return sorted(policies, key=lambda x: x['priority'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erreur listing politiques: {e}")
            return []

# Instance globale du service
gateway_authorization = GatewayAuthorizationService()

# API publique
__all__ = [
    'GatewayAuthorizationService',
    'Permission',
    'ResourceType',
    'AuthorizationDecision',
    'Resource',
    'Policy',
    'AuthorizationContext',
    'AuthorizationResult',
    'gateway_authorization'
]

if __name__ == "__main__":
    # Test de démonstration
    async def demo():
        service = GatewayAuthorizationService()
        
        # Enregistrement d'une ressource
        await service.register_resource(
            resource_id="content_123",
            resource_type=ResourceType.CONTENT,
            path="/api/content/123",
            owner_id="creator_user"
        )
        
        # Création d'une politique personnalisée
        policy_id = await service.create_policy(
            name="Test Policy",
            description="Politique de test",
            resource_pattern="/api/test/*",
            subjects=["role:creator"],
            permissions=[Permission.READ, Permission.WRITE],
            effect=AuthorizationDecision.ALLOW
        )
        
        # Test d'autorisation
        context = AuthorizationContext(
            user_id="creator_user",
            roles=["creator"],
            scopes=["read", "write"],
            request_path="/api/content/123",
            request_method="GET",
            ip_address="192.168.1.1"
        )
        
        result = await service.authorize(context, [Permission.READ])
        print(f"Autorisation: {result.decision.value}")
        print(f"Raison: {result.reason}")
        
        # Métriques
        metrics = service.get_metrics()
        print(f"Métriques: {metrics}")
        
        # Liste des politiques
        policies = await service.list_policies()
        print(f"Politiques: {len(policies)} configurées")
    
    # Exécution du test
    asyncio.run(demo())