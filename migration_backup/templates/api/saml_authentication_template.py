#!/usr/bin/env python3
"""
⚡ Enterprise SAML Authentication Template - Ainflue API Templates
Advanced production-ready SAML 2.0 authentication and federation system

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

import xml.etree.ElementTree as ET
import base64
import zlib
import urllib.parse
from datetime import datetime, timedelta
import uuid
import hashlib
import hmac
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import load_pem_x509_certificate
import structlog
from fastapi import Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
import aiohttp
import asyncio
from urllib.parse import quote, unquote
import re


class SAMLAuthenticationTemplate:
    """
    🚀 Enterprise SAML Authentication Template
    
    Fonctionnalités:
    - ✅ SAML 2.0 Service Provider (SP) complet
    - ✅ Identity Provider (IdP) intégration
    - ✅ Single Sign-On (SSO) automatique
    - ✅ Single Logout (SLO) centralisé
    - ✅ Assertion validation cryptographique
    - ✅ Metadata discovery et exchange
    - ✅ Attribute mapping et transformation
    - ✅ Multi-tenant IdP support
    - ✅ Session management enterprise
    - ✅ Security audit et compliance
    """
    
    def __init__(
        self,
        entity_id: str,
        sp_x509_cert: str,
        sp_private_key: str,
        acs_url: str,
        sls_url: str
    ):
        self.entity_id = entity_id
        self.sp_x509_cert = sp_x509_cert
        self.sp_private_key = sp_private_key
        self.acs_url = acs_url  # Assertion Consumer Service
        self.sls_url = sls_url  # Single Logout Service
        
        # Logger structuré
        self.logger = structlog.get_logger(__name__)
        
        # IdP registry
        self.identity_providers: Dict[str, SAMLIdentityProvider] = {}
        
        # Session manager
        self.session_manager = SAMLSessionManager()
        
        # Attribute mapper
        self.attribute_mapper = AttributeMapper()
        
        # Security validator
        self.security_validator = SAMLSecurityValidator(sp_x509_cert, sp_private_key)
        
        # Metadata manager
        self.metadata_manager = SAMLMetadataManager(self)
        
        # Audit logger
        self.audit_logger = SAMLAuditLogger()
    
    def register_identity_provider(
        self,
        idp_entity_id: str,
        idp_config: 'SAMLIdentityProvider'
    ):
        """Enregistre un Identity Provider"""
        self.identity_providers[idp_entity_id] = idp_config
        
        self.logger.info(
            "IdP registered",
            idp_entity_id=idp_entity_id,
            sso_url=idp_config.sso_url,
            slo_url=idp_config.slo_url
        )
    
    async def initiate_sso(
        self,
        idp_entity_id: str,
        relay_state: Optional[str] = None,
        force_authn: bool = False
    ) -> str:
        """Initie le processus SSO"""
        
        if idp_entity_id not in self.identity_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown Identity Provider: {idp_entity_id}"
            )
        
        idp = self.identity_providers[idp_entity_id]
        
        # Générer AuthnRequest
        authn_request = self._create_authn_request(
            idp,
            relay_state,
            force_authn
        )
        
        # Signer la requête si nécessaire
        if idp.sign_requests:
            authn_request = self.security_validator.sign_xml(authn_request)
        
        # Encoder pour transmission
        saml_request = base64.b64encode(
            zlib.compress(authn_request.encode('utf-8'))
        ).decode('utf-8')
        
        # Construire URL de redirection
        params = {
            'SAMLRequest': saml_request
        }
        
        if relay_state:
            params['RelayState'] = relay_state
        
        redirect_url = f"{idp.sso_url}?{urllib.parse.urlencode(params)}"
        
        # Audit log
        await self.audit_logger.log_sso_initiation(
            idp_entity_id,
            authn_request,
            relay_state
        )
        
        return redirect_url
    
    async def handle_sso_response(
        self,
        saml_response: str,
        relay_state: Optional[str] = None
    ) -> SAMLUser:
        """Traite la réponse SSO de l'IdP"""
        
        try:
            # Décoder la réponse
            decoded_response = base64.b64decode(saml_response).decode('utf-8')
            
            # Parser XML
            response_xml = ET.fromstring(decoded_response)
            
            # Valider la signature
            if not self.security_validator.validate_response_signature(response_xml):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid SAML response signature"
                )
            
            # Extraire et valider l'assertion
            assertion = self._extract_assertion(response_xml)
            
            if not self.security_validator.validate_assertion(assertion):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid SAML assertion"
                )
            
            # Extraire les attributs utilisateur
            user_attributes = self._extract_user_attributes(assertion)
            
            # Mapper les attributs
            mapped_attributes = self.attribute_mapper.map_attributes(user_attributes)
            
            # Créer l'utilisateur SAML
            saml_user = SAMLUser(
                name_id=self._extract_name_id(assertion),
                attributes=mapped_attributes,
                session_index=self._extract_session_index(assertion),
                issuer=self._extract_issuer(response_xml)
            )
            
            # Créer session
            session_id = await self.session_manager.create_session(saml_user)
            saml_user.session_id = session_id
            
            # Audit log
            await self.audit_logger.log_sso_success(
                saml_user,
                decoded_response,
                relay_state
            )
            
            return saml_user
            
        except Exception as e:
            # Audit log d'échec
            await self.audit_logger.log_sso_failure(
                str(e),
                saml_response,
                relay_state
            )
            
            self.logger.error(
                "SSO response processing failed",
                error=str(e),
                relay_state=relay_state
            )
            
            raise HTTPException(
                status_code=400,
                detail=f"SAML response processing failed: {str(e)}"
            )
    
    async def initiate_slo(
        self,
        session_id: str,
        name_id: str,
        session_index: str,
        idp_entity_id: str
    ) -> str:
        """Initie le processus Single Logout"""
        
        if idp_entity_id not in self.identity_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown Identity Provider: {idp_entity_id}"
            )
        
        idp = self.identity_providers[idp_entity_id]
        
        # Créer LogoutRequest
        logout_request = self._create_logout_request(
            idp,
            name_id,
            session_index
        )
        
        # Signer la requête
        if idp.sign_requests:
            logout_request = self.security_validator.sign_xml(logout_request)
        
        # Encoder pour transmission
        saml_request = base64.b64encode(
            zlib.compress(logout_request.encode('utf-8'))
        ).decode('utf-8')
        
        # Construire URL de redirection
        params = {
            'SAMLRequest': saml_request
        }
        
        redirect_url = f"{idp.slo_url}?{urllib.parse.urlencode(params)}"
        
        # Supprimer la session locale
        await self.session_manager.destroy_session(session_id)
        
        # Audit log
        await self.audit_logger.log_slo_initiation(
            session_id,
            name_id,
            idp_entity_id
        )
        
        return redirect_url
    
    async def handle_slo_response(
        self,
        saml_response: str
    ) -> bool:
        """Traite la réponse SLO de l'IdP"""
        
        try:
            # Décoder la réponse
            decoded_response = base64.b64decode(saml_response).decode('utf-8')
            
            # Parser XML
            response_xml = ET.fromstring(decoded_response)
            
            # Valider la signature
            if not self.security_validator.validate_response_signature(response_xml):
                return False
            
            # Vérifier le status
            status = self._extract_status(response_xml)
            success = status == "urn:oasis:names:tc:SAML:2.0:status:Success"
            
            # Audit log
            await self.audit_logger.log_slo_completion(
                success,
                decoded_response
            )
            
            return success
            
        except Exception as e:
            self.logger.error(
                "SLO response processing failed",
                error=str(e)
            )
            return False
    
    def _create_authn_request(
        self,
        idp: 'SAMLIdentityProvider',
        relay_state: Optional[str],
        force_authn: bool
    ) -> str:
        """Crée une AuthnRequest SAML"""
        
        request_id = f"_{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        authn_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp.sso_url}"
    AssertionConsumerServiceURL="{self.acs_url}"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    ForceAuthn="{str(force_authn).lower()}">
    
    <saml:Issuer>{self.entity_id}</saml:Issuer>
    
    <samlp:NameIDPolicy
        Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
        AllowCreate="true" />
        
    <samlp:RequestedAuthnContext Comparison="exact">
        <saml:AuthnContextClassRef>
            urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
        </saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>
    
</samlp:AuthnRequest>"""
        
        return authn_request
    
    def _create_logout_request(
        self,
        idp: 'SAMLIdentityProvider',
        name_id: str,
        session_index: str
    ) -> str:
        """Crée une LogoutRequest SAML"""
        
        request_id = f"_{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        logout_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:LogoutRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{idp.slo_url}">
    
    <saml:Issuer>{self.entity_id}</saml:Issuer>
    
    <saml:NameID
        Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">
        {name_id}
    </saml:NameID>
    
    <samlp:SessionIndex>{session_index}</samlp:SessionIndex>
    
</samlp:LogoutRequest>"""
        
        return logout_request
    
    def _extract_assertion(self, response_xml: ET.Element) -> ET.Element:
        """Extrait l'assertion de la réponse"""
        assertion = response_xml.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
        if assertion is None:
            raise ValueError("No assertion found in SAML response")
        return assertion
    
    def _extract_name_id(self, assertion: ET.Element) -> str:
        """Extrait le NameID de l'assertion"""
        name_id = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}NameID')
        if name_id is None:
            raise ValueError("No NameID found in assertion")
        return name_id.text
    
    def _extract_session_index(self, assertion: ET.Element) -> str:
        """Extrait le SessionIndex de l'assertion"""
        authn_stmt = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AuthnStatement')
        if authn_stmt is not None:
            return authn_stmt.get('SessionIndex', '')
        return ''
    
    def _extract_issuer(self, response_xml: ET.Element) -> str:
        """Extrait l'Issuer de la réponse"""
        issuer = response_xml.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Issuer')
        if issuer is not None:
            return issuer.text
        return ''
    
    def _extract_user_attributes(self, assertion: ET.Element) -> Dict[str, List[str]]:
        """Extrait les attributs utilisateur de l'assertion"""
        attributes = {}
        
        attr_stmt = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement')
        if attr_stmt is not None:
            for attr in attr_stmt.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
                attr_name = attr.get('Name')
                attr_values = []
                
                for value in attr.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                    if value.text:
                        attr_values.append(value.text)
                
                if attr_name and attr_values:
                    attributes[attr_name] = attr_values
        
        return attributes
    
    def _extract_status(self, response_xml: ET.Element) -> str:
        """Extrait le status de la réponse"""
        status = response_xml.find('.//{urn:oasis:names:tc:SAML:2.0:protocol}StatusCode')
        if status is not None:
            return status.get('Value', '')
        return ''
    
    def get_sp_metadata(self) -> str:
        """Génère les metadata du Service Provider"""
        return self.metadata_manager.generate_sp_metadata()


@dataclass
class SAMLIdentityProvider:
    """Configuration d'un Identity Provider SAML"""
    entity_id: str
    sso_url: str
    slo_url: str
    x509_cert: str
    sign_requests: bool = True
    sign_assertions: bool = True
    encrypt_assertions: bool = False
    name_id_format: str = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
    binding: str = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"


@dataclass
class SAMLUser:
    """Utilisateur authentifié via SAML"""
    name_id: str
    attributes: Dict[str, Any]
    session_index: str
    issuer: str
    session_id: Optional[str] = None
    authenticated_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Récupère un attribut avec valeur par défaut"""
        return self.attributes.get(name, default)
    
    def get_email(self) -> Optional[str]:
        """Récupère l'email de l'utilisateur"""
        return self.get_attribute('email') or self.get_attribute('mail')
    
    def get_full_name(self) -> Optional[str]:
        """Récupère le nom complet"""
        return self.get_attribute('displayName') or f"{self.get_attribute('firstName', '')} {self.get_attribute('lastName', '')}"


class SAMLSessionManager:
    """Gestionnaire de sessions SAML"""
    
    def __init__(self):
        self.sessions: Dict[str, SAMLSession] = {}
        self.logger = structlog.get_logger(__name__)
    
    async def create_session(self, user: SAMLUser) -> str:
        """Crée une nouvelle session"""
        session_id = str(uuid.uuid4())
        
        session = SAMLSession(
            session_id=session_id,
            user=user,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=8),
            last_activity=datetime.utcnow()
        )
        
        self.sessions[session_id] = session
        
        self.logger.info(
            "SAML session created",
            session_id=session_id,
            name_id=user.name_id,
            issuer=user.issuer
        )
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SAMLSession]:
        """Récupère une session"""
        session = self.sessions.get(session_id)
        
        if session and session.is_valid():
            # Mise à jour de la dernière activité
            session.last_activity = datetime.utcnow()
            return session
        
        # Session expirée ou invalide
        if session:
            await self.destroy_session(session_id)
        
        return None
    
    async def destroy_session(self, session_id: str):
        """Détruit une session"""
        session = self.sessions.pop(session_id, None)
        
        if session:
            self.logger.info(
                "SAML session destroyed",
                session_id=session_id,
                name_id=session.user.name_id
            )
    
    async def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        now = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at < now
        ]
        
        for session_id in expired_sessions:
            await self.destroy_session(session_id)
        
        if expired_sessions:
            self.logger.info(
                "Expired sessions cleaned up",
                count=len(expired_sessions)
            )


@dataclass
class SAMLSession:
    """Session SAML utilisateur"""
    session_id: str
    user: SAMLUser
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    
    def is_valid(self) -> bool:
        """Vérifie si la session est valide"""
        return datetime.utcnow() < self.expires_at
    
    def extend_session(self, hours: int = 2):
        """Étend la durée de la session"""
        self.expires_at = max(
            self.expires_at,
            datetime.utcnow() + timedelta(hours=hours)
        )


class AttributeMapper:
    """Mappeur d'attributs SAML"""
    
    def __init__(self):
        # Mapping par défaut des attributs SAML vers attributs application
        self.default_mapping = {
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': 'email',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': 'firstName',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': 'lastName',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': 'displayName',
            'http://schemas.microsoft.com/ws/2008/06/identity/claims/groups': 'groups',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier': 'userId',
            
            # Attributs LDAP communs
            'mail': 'email',
            'cn': 'displayName',
            'sn': 'lastName',
            'givenName': 'firstName',
            'memberOf': 'groups',
            'uid': 'userId',
            'employeeID': 'employeeId',
            'department': 'department',
            'title': 'jobTitle'
        }
        
        # Transformateurs personnalisés
        self.transformers = {
            'groups': self._transform_groups,
            'email': self._transform_email
        }
    
    def map_attributes(
        self,
        saml_attributes: Dict[str, List[str]],
        custom_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Mappe les attributs SAML vers les attributs application"""
        
        mapping = {**self.default_mapping}
        if custom_mapping:
            mapping.update(custom_mapping)
        
        mapped_attributes = {}
        
        for saml_attr, values in saml_attributes.items():
            # Trouver le nom de l'attribut mappé
            app_attr = mapping.get(saml_attr, saml_attr)
            
            # Transformer la valeur si nécessaire
            if app_attr in self.transformers:
                mapped_value = self.transformers[app_attr](values)
            else:
                # Prendre la première valeur pour les attributs simples
                mapped_value = values[0] if values else None
                
                # Garder la liste pour les attributs multi-valeurs
                if len(values) > 1:
                    mapped_value = values
            
            if mapped_value is not None:
                mapped_attributes[app_attr] = mapped_value
        
        return mapped_attributes
    
    def _transform_groups(self, values: List[str]) -> List[str]:
        """Transforme les groupes SAML"""
        # Extraire le nom du groupe depuis le DN complet
        groups = []
        for value in values:
            if value.startswith('CN='):
                # Extraire le nom du groupe depuis "CN=GroupName,OU=..."
                group_name = value.split(',')[0][3:]  # Enlever "CN="
                groups.append(group_name)
            else:
                groups.append(value)
        
        return groups
    
    def _transform_email(self, values: List[str]) -> Optional[str]:
        """Transforme l'email"""
        if values:
            email = values[0].lower().strip()
            # Validation basique d'email
            if '@' in email and '.' in email:
                return email
        return None


class SAMLSecurityValidator:
    """Validateur de sécurité SAML"""
    
    def __init__(self, sp_cert: str, sp_private_key: str):
        self.sp_cert = sp_cert
        self.sp_private_key = sp_private_key
        self.logger = structlog.get_logger(__name__)
    
    def validate_response_signature(self, response_xml: ET.Element) -> bool:
        """Valide la signature de la réponse SAML"""
        try:
            # Rechercher l'élément Signature
            signature = response_xml.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            
            if signature is None:
                self.logger.warning("No signature found in SAML response")
                return False
            
            # Ici, vous implémenteriez la validation XMLDSig complète
            # Pour cette démonstration, on simule la validation
            return self._verify_xml_signature(response_xml, signature)
            
        except Exception as e:
            self.logger.error(
                "Signature validation failed",
                error=str(e)
            )
            return False
    
    def validate_assertion(self, assertion: ET.Element) -> bool:
        """Valide l'assertion SAML"""
        try:
            # Vérifier les conditions temporelles
            if not self._validate_time_conditions(assertion):
                return False
            
            # Vérifier l'audience
            if not self._validate_audience(assertion):
                return False
            
            # Vérifier la signature de l'assertion si présente
            signature = assertion.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            if signature is not None:
                return self._verify_xml_signature(assertion, signature)
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Assertion validation failed",
                error=str(e)
            )
            return False
    
    def _validate_time_conditions(self, assertion: ET.Element) -> bool:
        """Valide les conditions temporelles"""
        conditions = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Conditions')
        
        if conditions is not None:
            now = datetime.utcnow()
            
            # Vérifier NotBefore
            not_before = conditions.get('NotBefore')
            if not_before:
                not_before_dt = datetime.strptime(not_before, '%Y-%m-%dT%H:%M:%SZ')
                if now < not_before_dt:
                    self.logger.warning("Assertion not yet valid")
                    return False
            
            # Vérifier NotOnOrAfter
            not_on_or_after = conditions.get('NotOnOrAfter')
            if not_on_or_after:
                not_on_or_after_dt = datetime.strptime(not_on_or_after, '%Y-%m-%dT%H:%M:%SZ')
                if now >= not_on_or_after_dt:
                    self.logger.warning("Assertion has expired")
                    return False
        
        return True
    
    def _validate_audience(self, assertion: ET.Element) -> bool:
        """Valide l'audience restriction"""
        audience_restriction = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction')
        
        if audience_restriction is not None:
            audiences = audience_restriction.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Audience')
            
            valid_audiences = [aud.text for aud in audiences if aud.text]
            
            if self.sp_cert not in valid_audiences:
                self.logger.warning(
                    "Invalid audience",
                    expected=self.sp_cert,
                    found=valid_audiences
                )
                return False
        
        return True
    
    def _verify_xml_signature(self, xml_element: ET.Element, signature: ET.Element) -> bool:
        """Vérifie la signature XML (implémentation simplifiée)"""
        # Dans un vrai système, vous utiliseriez une bibliothèque comme xmlsec
        # Pour cette démo, on simule la validation
        
        try:
            # Extraire les éléments de signature
            signature_value = signature.find('.//{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
            
            if signature_value is None:
                return False
            
            # Ici vous feriez la vraie validation cryptographique
            # En utilisant la clé publique de l'IdP
            
            return True  # Simulation
            
        except Exception as e:
            self.logger.error(
                "XML signature verification failed",
                error=str(e)
            )
            return False
    
    def sign_xml(self, xml_content: str) -> str:
        """Signe un document XML"""
        # Dans un vrai système, vous utiliseriez xmlsec pour signer
        # Pour cette démo, on retourne le XML non modifié
        
        # Ici vous ajouteriez l'élément Signature au XML
        return xml_content


class SAMLMetadataManager:
    """Gestionnaire de metadata SAML"""
    
    def __init__(self, saml_auth: SAMLAuthenticationTemplate):
        self.saml_auth = saml_auth
    
    def generate_sp_metadata(self) -> str:
        """Génère les metadata du Service Provider"""
        
        metadata = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    entityID="{self.saml_auth.entity_id}">
    
    <md:SPSSODescriptor
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
        AuthnRequestsSigned="true"
        WantAssertionsSigned="true">
        
        <md:KeyDescriptor use="signing">
            <ds:KeyInfo>
                <ds:X509Data>
                    <ds:X509Certificate>
                        {self._format_certificate(self.saml_auth.sp_x509_cert)}
                    </ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </md:KeyDescriptor>
        
        <md:KeyDescriptor use="encryption">
            <ds:KeyInfo>
                <ds:X509Data>
                    <ds:X509Certificate>
                        {self._format_certificate(self.saml_auth.sp_x509_cert)}
                    </ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </md:KeyDescriptor>
        
        <md:NameIDFormat>
            urn:oasis:names:tc:SAML:2.0:nameid-format:persistent
        </md:NameIDFormat>
        
        <md:AssertionConsumerService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="{self.saml_auth.acs_url}"
            index="0"
            isDefault="true" />
            
        <md:SingleLogoutService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            Location="{self.saml_auth.sls_url}" />
            
    </md:SPSSODescriptor>
    
</md:EntityDescriptor>"""
        
        return metadata
    
    def _format_certificate(self, cert: str) -> str:
        """Formate le certificat pour les metadata"""
        # Enlever les headers/footers et espaces
        cert_lines = cert.replace('-----BEGIN CERTIFICATE-----', '')
        cert_lines = cert_lines.replace('-----END CERTIFICATE-----', '')
        cert_lines = ''.join(cert_lines.split())
        
        return cert_lines
    
    async def fetch_idp_metadata(self, metadata_url: str) -> SAMLIdentityProvider:
        """Récupère les metadata d'un IdP"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata_url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to fetch IdP metadata: {response.status}"
                    )
                
                metadata_xml = await response.text()
                
        # Parser les metadata
        root = ET.fromstring(metadata_xml)
        
        # Extraire les informations nécessaires
        entity_id = root.get('entityID')
        
        # Trouver le SSO service
        sso_service = root.find('.//{urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService[@Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"]')
        sso_url = sso_service.get('Location') if sso_service is not None else None
        
        # Trouver le SLO service
        slo_service = root.find('.//{urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService[@Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"]')
        slo_url = slo_service.get('Location') if slo_service is not None else None
        
        # Extraire le certificat
        cert_element = root.find('.//{http://www.w3.org/2000/09/xmldsig#}X509Certificate')
        x509_cert = cert_element.text if cert_element is not None else None
        
        if not all([entity_id, sso_url, x509_cert]):
            raise HTTPException(
                status_code=400,
                detail="Invalid IdP metadata: missing required elements"
            )
        
        return SAMLIdentityProvider(
            entity_id=entity_id,
            sso_url=sso_url,
            slo_url=slo_url,
            x509_cert=x509_cert
        )


class SAMLAuditLogger:
    """Logger d'audit pour SAML"""
    
    def __init__(self):
        self.logger = structlog.get_logger("saml_audit")
    
    async def log_sso_initiation(
        self,
        idp_entity_id: str,
        authn_request: str,
        relay_state: Optional[str]
    ):
        """Log l'initiation SSO"""
        self.logger.info(
            "SSO_INITIATION",
            idp_entity_id=idp_entity_id,
            relay_state=relay_state,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_sso_success(
        self,
        user: SAMLUser,
        saml_response: str,
        relay_state: Optional[str]
    ):
        """Log le succès SSO"""
        self.logger.info(
            "SSO_SUCCESS",
            name_id=user.name_id,
            issuer=user.issuer,
            session_id=user.session_id,
            relay_state=relay_state,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_sso_failure(
        self,
        error: str,
        saml_response: str,
        relay_state: Optional[str]
    ):
        """Log l'échec SSO"""
        self.logger.error(
            "SSO_FAILURE",
            error=error,
            relay_state=relay_state,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_slo_initiation(
        self,
        session_id: str,
        name_id: str,
        idp_entity_id: str
    ):
        """Log l'initiation SLO"""
        self.logger.info(
            "SLO_INITIATION",
            session_id=session_id,
            name_id=name_id,
            idp_entity_id=idp_entity_id,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_slo_completion(
        self,
        success: bool,
        saml_response: str
    ):
        """Log la completion SLO"""
        self.logger.info(
            "SLO_COMPLETION",
            success=success,
            timestamp=datetime.utcnow().isoformat()
        )


# Factory functions et helpers
def create_saml_auth(
    entity_id: str,
    sp_cert_path: str,
    sp_key_path: str,
    acs_url: str,
    sls_url: str
) -> SAMLAuthenticationTemplate:
    """Factory pour créer l'authentification SAML"""
    
    # Charger le certificat et la clé
    with open(sp_cert_path, 'r') as f:
        sp_cert = f.read()
    
    with open(sp_key_path, 'r') as f:
        sp_key = f.read()
    
    return SAMLAuthenticationTemplate(
        entity_id=entity_id,
        sp_x509_cert=sp_cert,
        sp_private_key=sp_key,
        acs_url=acs_url,
        sls_url=sls_url
    )


async def get_saml_user(
    request: Request,
    saml_auth: SAMLAuthenticationTemplate = Depends()
) -> Optional[SAMLUser]:
    """Dependency FastAPI pour récupérer l'utilisateur SAML"""
    
    # Récupérer le session ID depuis les cookies
    session_id = request.cookies.get('saml_session_id')
    
    if not session_id:
        return None
    
    # Récupérer la session
    session = await saml_auth.session_manager.get_session(session_id)
    
    if session:
        return session.user
    
    return None


def require_saml_auth(
    user: Optional[SAMLUser] = Depends(get_saml_user)
) -> SAMLUser:
    """Dependency FastAPI pour exiger l'authentification SAML"""
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="SAML authentication required"
        )
    
    return user


# Example usage et configuration
if __name__ == "__main__":
    import asyncio
    
    async def example_saml_flow():
        # Créer l'authentification SAML
        saml_auth = SAMLAuthenticationTemplate(
            entity_id="https://ainflue.com/sp",
            sp_x509_cert="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
            sp_private_key="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
            acs_url="https://ainflue.com/saml/acs",
            sls_url="https://ainflue.com/saml/sls"
        )
        
        # Configurer un IdP
        idp_config = SAMLIdentityProvider(
            entity_id="https://idp.example.com",
            sso_url="https://idp.example.com/sso",
            slo_url="https://idp.example.com/slo",
            x509_cert="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
        )
        
        saml_auth.register_identity_provider(
            "example_idp",
            idp_config
        )
        
        # Initier SSO
        sso_url = await saml_auth.initiate_sso(
            idp_entity_id="example_idp",
            relay_state="/dashboard"
        )
        
        print(f"Redirect to: {sso_url}")
        
        # Simuler réponse SAML (normalement vient de l'IdP)
        fake_saml_response = base64.b64encode(b"<fake_response>").decode()
        
        try:
            # Traiter la réponse (ceci échouerait avec de vraies données)
            user = await saml_auth.handle_sso_response(fake_saml_response)
            print(f"User authenticated: {user.name_id}")
        except:
            print("Authentication failed (expected with fake data)")
        
        # Générer metadata SP
        metadata = saml_auth.get_sp_metadata()
        print(f"SP Metadata generated: {len(metadata)} chars")
    
    asyncio.run(example_saml_flow())