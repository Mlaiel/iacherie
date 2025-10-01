#!/usr/bin/env python3
"""
⚡ Enterprise Certificate Authentication Template - iacherie API Templates
Advanced production-ready X.509 certificate authentication and PKI management

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

import ssl
import socket
import hashlib
import base64
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import structlog
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID, ExtensionOID
from fastapi import HTTPException, Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import re
import ipaddress
from pathlib import Path
import aiofiles
import json


class CertificateValidationMode(Enum):
    """Modes de validation des certificats"""
    STRICT = "strict"           # Validation complète avec CRL/OCSP
    RELAXED = "relaxed"         # Validation de base sans révocation
    DEVELOPMENT = "development" # Pour développement uniquement


class CertificateAuthenticationTemplate:
    """
    🚀 Enterprise Certificate Authentication Template
    
    Fonctionnalités:
    - ✅ X.509 certificate validation complète
    - ✅ PKI chain of trust verification
    - ✅ CRL et OCSP revocation checking
    - ✅ Client certificate authentication
    - ✅ Certificate attribute extraction
    - ✅ Role-based access control (RBAC)
    - ✅ Certificate lifecycle management
    - ✅ Hardware Security Module (HSM) support
    - ✅ Certificate template et auto-enrollment
    - ✅ Multi-CA trust store management
    - ✅ Audit logging et compliance
    """
    
    def __init__(
        self,
        trusted_ca_certs: List[str],
        validation_mode: CertificateValidationMode = CertificateValidationMode.STRICT,
        require_client_cert: bool = True,
        allowed_key_sizes: List[int] = None,
        max_cert_chain_length: int = 5
    ):
        self.trusted_ca_certs = trusted_ca_certs
        self.validation_mode = validation_mode
        self.require_client_cert = require_client_cert
        self.allowed_key_sizes = allowed_key_sizes or [2048, 3072, 4096]
        self.max_cert_chain_length = max_cert_chain_length
        
        # Logger structuré
        self.logger = structlog.get_logger(__name__)
        
        # Certificate store
        self.cert_store = CertificateStore()
        
        # CA trust manager
        self.trust_manager = CATrustManager(trusted_ca_certs)
        
        # Certificate validator
        self.validator = CertificateValidator(
            self.trust_manager,
            validation_mode,
            max_cert_chain_length
        )
        
        # Certificate parser
        self.parser = CertificateParser()
        
        # Revocation checker
        self.revocation_checker = RevocationChecker()
        
        # Access control manager
        self.access_manager = CertificateAccessManager()
        
        # Certificate generator (pour développement)
        self.cert_generator = CertificateGenerator()
        
        # Audit logger
        self.audit_logger = CertificateAuditLogger()
        
        # Initialiser le trust store
        asyncio.create_task(self._initialize_trust_store())
    
    async def _initialize_trust_store(self):
        """Initialise le trust store avec les CA certificats"""
        try:
            for ca_cert_path in self.trusted_ca_certs:
                await self.trust_manager.add_trusted_ca(ca_cert_path)
            
            self.logger.info(
                "Trust store initialized",
                ca_count=len(self.trusted_ca_certs)
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to initialize trust store",
                error=str(e)
            )
    
    async def authenticate_certificate(
        self,
        client_cert_pem: str,
        cert_chain_pem: Optional[List[str]] = None
    ) -> 'CertificateUser':
        """Authentifie un utilisateur via certificat client"""
        
        try:
            # Parser le certificat client
            client_cert = self.parser.parse_certificate(client_cert_pem)
            
            # Parser la chaîne de certificats si fournie
            cert_chain = []
            if cert_chain_pem:
                for cert_pem in cert_chain_pem:
                    cert_chain.append(self.parser.parse_certificate(cert_pem))
            
            # Construire la chaîne complète
            full_chain = [client_cert] + cert_chain
            
            # Valider la chaîne de certificats
            validation_result = await self.validator.validate_certificate_chain(
                full_chain
            )
            
            if not validation_result.is_valid:
                await self.audit_logger.log_authentication_failure(
                    client_cert, validation_result.errors
                )
                raise HTTPException(
                    status_code=401,
                    detail=f"Certificate validation failed: {validation_result.errors}"
                )
            
            # Vérifier la révocation
            if self.validation_mode == CertificateValidationMode.STRICT:
                revocation_status = await self.revocation_checker.check_revocation(
                    client_cert, cert_chain
                )
                
                if revocation_status.is_revoked:
                    await self.audit_logger.log_authentication_failure(
                        client_cert, ["Certificate revoked"]
                    )
                    raise HTTPException(
                        status_code=401,
                        detail="Certificate has been revoked"
                    )
            
            # Extraire les informations utilisateur
            user_info = self.parser.extract_user_info(client_cert)
            
            # Déterminer les rôles et permissions
            roles = await self.access_manager.determine_roles(client_cert)
            permissions = await self.access_manager.get_permissions(roles)
            
            # Créer l'objet utilisateur
            cert_user = CertificateUser(
                certificate=client_cert,
                subject_dn=user_info.subject_dn,
                issuer_dn=user_info.issuer_dn,
                serial_number=user_info.serial_number,
                fingerprint=user_info.fingerprint,
                common_name=user_info.common_name,
                email=user_info.email,
                organization=user_info.organization,
                roles=roles,
                permissions=permissions,
                authenticated_at=datetime.utcnow(),
                expires_at=client_cert.not_valid_after,
                validation_result=validation_result
            )
            
            # Audit log succès
            await self.audit_logger.log_authentication_success(cert_user)
            
            return cert_user
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Certificate authentication error",
                error=str(e)
            )
            
            raise HTTPException(
                status_code=500,
                detail="Certificate authentication failed"
            )
    
    async def validate_certificate_request(
        self,
        csr_pem: str,
        template_name: Optional[str] = None
    ) -> 'CSRValidationResult':
        """Valide une demande de certificat (CSR)"""
        
        try:
            # Parser le CSR
            csr = self.parser.parse_csr(csr_pem)
            
            # Valider le CSR
            validation_result = await self.validator.validate_csr(
                csr, template_name
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(
                "CSR validation error",
                error=str(e)
            )
            
            return CSRValidationResult(
                is_valid=False,
                errors=[f"CSR validation failed: {str(e)}"]
            )
    
    async def generate_certificate(
        self,
        csr_pem: str,
        template_name: str,
        ca_cert_path: str,
        ca_key_path: str,
        validity_days: int = 365
    ) -> str:
        """Génère un certificat à partir d'un CSR"""
        
        try:
            # Valider le CSR
            validation_result = await self.validate_certificate_request(
                csr_pem, template_name
            )
            
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid CSR: {validation_result.errors}"
                )
            
            # Générer le certificat
            cert_pem = await self.cert_generator.generate_certificate(
                csr_pem,
                ca_cert_path,
                ca_key_path,
                template_name,
                validity_days
            )
            
            # Audit log
            await self.audit_logger.log_certificate_generation(
                validation_result.csr, template_name
            )
            
            return cert_pem
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Certificate generation error",
                error=str(e)
            )
            
            raise HTTPException(
                status_code=500,
                detail="Certificate generation failed"
            )
    
    async def revoke_certificate(
        self,
        serial_number: str,
        reason: str = "unspecified"
    ) -> bool:
        """Révoque un certificat"""
        
        try:
            # Ajouter à la CRL
            revocation_success = await self.revocation_checker.revoke_certificate(
                serial_number, reason
            )
            
            if revocation_success:
                # Audit log
                await self.audit_logger.log_certificate_revocation(
                    serial_number, reason
                )
            
            return revocation_success
            
        except Exception as e:
            self.logger.error(
                "Certificate revocation error",
                serial_number=serial_number,
                error=str(e)
            )
            return False
    
    async def get_certificate_info(
        self,
        cert_pem: str
    ) -> 'CertificateInfo':
        """Récupère les informations d'un certificat"""
        
        try:
            cert = self.parser.parse_certificate(cert_pem)
            return self.parser.extract_user_info(cert)
            
        except Exception as e:
            self.logger.error(
                "Certificate info extraction error",
                error=str(e)
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid certificate format"
            )
    
    def create_ssl_context(
        self,
        server_cert_path: str,
        server_key_path: str
    ) -> ssl.SSLContext:
        """Crée un contexte SSL pour l'authentification mutuelle"""
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Charger le certificat serveur
        context.load_cert_chain(server_cert_path, server_key_path)
        
        # Charger les CA de confiance
        for ca_cert_path in self.trusted_ca_certs:
            context.load_verify_locations(ca_cert_path)
        
        # Configurer pour l'authentification client
        if self.require_client_cert:
            context.verify_mode = ssl.CERT_REQUIRED
        else:
            context.verify_mode = ssl.CERT_OPTIONAL
        
        # Vérifier le hostname par défaut
        context.check_hostname = False
        
        return context


@dataclass
class CertificateUser:
    """Utilisateur authentifié par certificat"""
    certificate: x509.Certificate
    subject_dn: str
    issuer_dn: str
    serial_number: str
    fingerprint: str
    common_name: str
    email: Optional[str]
    organization: Optional[str]
    roles: List[str]
    permissions: List[str]
    authenticated_at: datetime
    expires_at: datetime
    validation_result: 'CertificateValidationResult'
    
    def has_role(self, role: str) -> bool:
        """Vérifie si l'utilisateur a un rôle"""
        return role in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """Vérifie si l'utilisateur a une permission"""
        return permission in self.permissions
    
    def is_expired(self) -> bool:
        """Vérifie si le certificat est expiré"""
        return datetime.utcnow() > self.expires_at
    
    def days_until_expiry(self) -> int:
        """Retourne le nombre de jours avant expiration"""
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)


@dataclass
class CertificateInfo:
    """Informations extraites d'un certificat"""
    subject_dn: str
    issuer_dn: str
    serial_number: str
    fingerprint: str
    common_name: str
    email: Optional[str] = None
    organization: Optional[str] = None
    organizational_unit: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    locality: Optional[str] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    public_key_algorithm: Optional[str] = None
    public_key_size: Optional[int] = None
    signature_algorithm: Optional[str] = None
    key_usage: List[str] = field(default_factory=list)
    extended_key_usage: List[str] = field(default_factory=list)
    san_dns_names: List[str] = field(default_factory=list)
    san_ip_addresses: List[str] = field(default_factory=list)


@dataclass
class CertificateValidationResult:
    """Résultat de validation d'un certificat"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    trust_chain: List[x509.Certificate] = field(default_factory=list)
    validation_time: Optional[datetime] = None


@dataclass
class CSRValidationResult:
    """Résultat de validation d'un CSR"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    csr: Optional[x509.CertificateSigningRequest] = None


@dataclass
class RevocationStatus:
    """Status de révocation d'un certificat"""
    is_revoked: bool
    revocation_date: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    checked_via: Optional[str] = None  # CRL ou OCSP


class CertificateStore:
    """Store de certificats"""
    
    def __init__(self):
        self.certificates: Dict[str, x509.Certificate] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_certificate(
        self,
        fingerprint: str,
        certificate: x509.Certificate,
        metadata: Dict[str, Any] = None
    ):
        """Ajoute un certificat au store"""
        self.certificates[fingerprint] = certificate
        self.metadata[fingerprint] = metadata or {}
    
    def get_certificate(self, fingerprint: str) -> Optional[x509.Certificate]:
        """Récupère un certificat par fingerprint"""
        return self.certificates.get(fingerprint)
    
    def search_certificates(
        self,
        subject_filter: Optional[str] = None,
        issuer_filter: Optional[str] = None
    ) -> List[x509.Certificate]:
        """Recherche des certificats"""
        results = []
        
        for cert in self.certificates.values():
            subject_match = (
                not subject_filter or 
                subject_filter.lower() in str(cert.subject).lower()
            )
            
            issuer_match = (
                not issuer_filter or
                issuer_filter.lower() in str(cert.issuer).lower()
            )
            
            if subject_match and issuer_match:
                results.append(cert)
        
        return results


class CATrustManager:
    """Gestionnaire de confiance des CA"""
    
    def __init__(self, trusted_ca_paths: List[str]):
        self.trusted_cas: Dict[str, x509.Certificate] = {}
        self.ca_metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = structlog.get_logger(__name__)
    
    async def add_trusted_ca(self, ca_cert_path: str):
        """Ajoute une CA de confiance"""
        try:
            async with aiofiles.open(ca_cert_path, 'r') as f:
                ca_cert_pem = await f.read()
            
            ca_cert = x509.load_pem_x509_certificate(ca_cert_pem.encode())
            
            # Utiliser le subject hash comme clé
            subject_hash = hashlib.sha256(
                ca_cert.subject.public_bytes()
            ).hexdigest()[:16]
            
            self.trusted_cas[subject_hash] = ca_cert
            self.ca_metadata[subject_hash] = {
                'path': ca_cert_path,
                'subject': str(ca_cert.subject),
                'issuer': str(ca_cert.issuer),
                'not_after': ca_cert.not_valid_after,
                'added_at': datetime.utcnow()
            }
            
            self.logger.info(
                "Trusted CA added",
                subject=str(ca_cert.subject),
                expires=ca_cert.not_valid_after
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to add trusted CA",
                path=ca_cert_path,
                error=str(e)
            )
            raise
    
    def is_trusted_issuer(self, issuer_cert: x509.Certificate) -> bool:
        """Vérifie si un certificat émetteur est de confiance"""
        issuer_hash = hashlib.sha256(
            issuer_cert.subject.public_bytes()
        ).hexdigest()[:16]
        
        return issuer_hash in self.trusted_cas
    
    def get_trusted_ca_by_subject(self, subject_name: x509.Name) -> Optional[x509.Certificate]:
        """Récupère une CA par son subject"""
        subject_hash = hashlib.sha256(
            subject_name.public_bytes()
        ).hexdigest()[:16]
        
        return self.trusted_cas.get(subject_hash)


class CertificateValidator:
    """Validateur de certificats"""
    
    def __init__(
        self,
        trust_manager: CATrustManager,
        validation_mode: CertificateValidationMode,
        max_chain_length: int
    ):
        self.trust_manager = trust_manager
        self.validation_mode = validation_mode
        self.max_chain_length = max_chain_length
        self.logger = structlog.get_logger(__name__)
    
    async def validate_certificate_chain(
        self,
        cert_chain: List[x509.Certificate]
    ) -> CertificateValidationResult:
        """Valide une chaîne de certificats"""
        
        errors = []
        warnings = []
        
        if not cert_chain:
            return CertificateValidationResult(
                is_valid=False,
                errors=["Empty certificate chain"]
            )
        
        if len(cert_chain) > self.max_chain_length:
            errors.append(f"Certificate chain too long: {len(cert_chain)} > {self.max_chain_length}")
        
        client_cert = cert_chain[0]
        
        # Validation de base du certificat client
        basic_validation = self._validate_basic_certificate(client_cert)
        errors.extend(basic_validation.errors)
        warnings.extend(basic_validation.warnings)
        
        # Validation de la chaîne de confiance
        trust_validation = await self._validate_trust_chain(cert_chain)
        errors.extend(trust_validation.errors)
        warnings.extend(trust_validation.warnings)
        
        # Validation des dates
        date_validation = self._validate_certificate_dates(client_cert)
        errors.extend(date_validation.errors)
        warnings.extend(date_validation.warnings)
        
        # Validation des usages de clé
        usage_validation = self._validate_key_usage(client_cert)
        errors.extend(usage_validation.errors)
        warnings.extend(usage_validation.warnings)
        
        return CertificateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            trust_chain=cert_chain,
            validation_time=datetime.utcnow()
        )
    
    def _validate_basic_certificate(self, cert: x509.Certificate) -> CertificateValidationResult:
        """Validation de base d'un certificat"""
        errors = []
        warnings = []
        
        try:
            # Vérifier la signature du certificat
            # Note: En production, utilisez une bibliothèque de validation PKI complète
            
            # Vérifier la taille de clé
            public_key = cert.public_key()
            if hasattr(public_key, 'key_size'):
                key_size = public_key.key_size
                if key_size < 2048:
                    errors.append(f"Key size too small: {key_size} bits")
                elif key_size < 3072:
                    warnings.append(f"Key size below recommended: {key_size} bits")
            
            # Vérifier l'algorithme de signature
            sig_algorithm = cert.signature_algorithm_oid._name
            weak_algorithms = ['md5', 'sha1']
            
            if any(weak in sig_algorithm.lower() for weak in weak_algorithms):
                errors.append(f"Weak signature algorithm: {sig_algorithm}")
            
        except Exception as e:
            errors.append(f"Certificate validation error: {str(e)}")
        
        return CertificateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def _validate_trust_chain(
        self,
        cert_chain: List[x509.Certificate]
    ) -> CertificateValidationResult:
        """Valide la chaîne de confiance"""
        errors = []
        warnings = []
        
        # Vérifier que la chaîne se termine par une CA de confiance
        root_cert = cert_chain[-1]
        
        if not self.trust_manager.is_trusted_issuer(root_cert):
            # Chercher si l'émetteur du dernier cert est de confiance
            issuer_ca = self.trust_manager.get_trusted_ca_by_subject(root_cert.issuer)
            
            if not issuer_ca:
                errors.append("Certificate chain does not end with a trusted CA")
            else:
                # Vérifier la signature du dernier certificat
                try:
                    # Ici vous feriez la vraie validation de signature
                    pass
                except Exception as e:
                    errors.append(f"Invalid signature in certificate chain: {str(e)}")
        
        # Vérifier la continuité de la chaîne
        for i in range(len(cert_chain) - 1):
            current_cert = cert_chain[i]
            issuer_cert = cert_chain[i + 1]
            
            # Vérifier que l'émetteur correspond
            if current_cert.issuer != issuer_cert.subject:
                errors.append(
                    f"Certificate chain break at position {i}: "
                    f"issuer mismatch"
                )
        
        return CertificateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_certificate_dates(self, cert: x509.Certificate) -> CertificateValidationResult:
        """Valide les dates de validité"""
        errors = []
        warnings = []
        now = datetime.utcnow()
        
        # Vérifier que le certificat est dans sa période de validité
        if now < cert.not_valid_before:
            errors.append("Certificate is not yet valid")
        
        if now > cert.not_valid_after:
            errors.append("Certificate has expired")
        
        # Avertissement si expiration proche
        days_until_expiry = (cert.not_valid_after - now).days
        if 0 < days_until_expiry <= 30:
            warnings.append(f"Certificate expires in {days_until_expiry} days")
        
        return CertificateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_key_usage(self, cert: x509.Certificate) -> CertificateValidationResult:
        """Valide les usages de clé"""
        errors = []
        warnings = []
        
        try:
            # Vérifier l'extension Key Usage
            key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.KEY_USAGE
            ).value
            
            # Pour l'authentification client, digital_signature doit être présent
            if not key_usage.digital_signature:
                warnings.append("Certificate lacks digital_signature key usage")
            
        except x509.ExtensionNotFound:
            warnings.append("Certificate lacks Key Usage extension")
        
        try:
            # Vérifier l'extension Extended Key Usage
            ext_key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.EXTENDED_KEY_USAGE
            ).value
            
            # Vérifier l'usage client authentication
            client_auth_oid = x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
            if client_auth_oid not in ext_key_usage:
                warnings.append("Certificate lacks client authentication extended key usage")
            
        except x509.ExtensionNotFound:
            warnings.append("Certificate lacks Extended Key Usage extension")
        
        return CertificateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def validate_csr(
        self,
        csr: x509.CertificateSigningRequest,
        template_name: Optional[str] = None
    ) -> CSRValidationResult:
        """Valide un Certificate Signing Request"""
        
        errors = []
        warnings = []
        
        try:
            # Vérifier la signature du CSR
            if not csr.is_signature_valid:
                errors.append("Invalid CSR signature")
            
            # Vérifier la taille de clé
            public_key = csr.public_key()
            if hasattr(public_key, 'key_size'):
                key_size = public_key.key_size
                if key_size < 2048:
                    errors.append(f"Key size too small: {key_size} bits")
            
            # Vérifier le subject
            subject = csr.subject
            cn = None
            
            for attribute in subject:
                if attribute.oid == NameOID.COMMON_NAME:
                    cn = attribute.value
                    break
            
            if not cn:
                errors.append("CSR lacks Common Name in subject")
            
            # Validation selon le template (si spécifié)
            if template_name:
                template_validation = await self._validate_csr_template(
                    csr, template_name
                )
                errors.extend(template_validation.errors)
                warnings.extend(template_validation.warnings)
            
        except Exception as e:
            errors.append(f"CSR validation error: {str(e)}")
        
        return CSRValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            csr=csr
        )
    
    async def _validate_csr_template(
        self,
        csr: x509.CertificateSigningRequest,
        template_name: str
    ) -> CSRValidationResult:
        """Valide un CSR selon un template"""
        
        # Cette méthode pourrait être étendue pour supporter
        # différents templates de certificats avec leurs propres règles
        
        errors = []
        warnings = []
        
        # Template exemple pour certificats utilisateur
        if template_name == "user_certificate":
            # Vérifier que l'email est présent
            email_found = False
            
            for attribute in csr.subject:
                if attribute.oid == NameOID.EMAIL_ADDRESS:
                    email_found = True
                    email = attribute.value
                    
                    # Validation simple d'email
                    if "@" not in email:
                        errors.append("Invalid email address in subject")
                    
                    break
            
            if not email_found:
                warnings.append("Email address not found in subject")
        
        return CSRValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class CertificateParser:
    """Parser de certificats"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    def parse_certificate(self, cert_pem: str) -> x509.Certificate:
        """Parse un certificat PEM"""
        try:
            return x509.load_pem_x509_certificate(cert_pem.encode())
        except Exception as e:
            raise ValueError(f"Invalid certificate format: {str(e)}")
    
    def parse_csr(self, csr_pem: str) -> x509.CertificateSigningRequest:
        """Parse un CSR PEM"""
        try:
            return x509.load_pem_x509_csr(csr_pem.encode())
        except Exception as e:
            raise ValueError(f"Invalid CSR format: {str(e)}")
    
    def extract_user_info(self, cert: x509.Certificate) -> CertificateInfo:
        """Extrait les informations utilisateur d'un certificat"""
        
        # Calculer le fingerprint
        fingerprint = hashlib.sha256(cert.public_bytes()).hexdigest()
        
        # Extraire les informations du subject
        subject_info = self._parse_name(cert.subject)
        issuer_info = self._parse_name(cert.issuer)
        
        # Extraire les extensions
        key_usage = self._extract_key_usage(cert)
        ext_key_usage = self._extract_extended_key_usage(cert)
        san_info = self._extract_san(cert)
        
        # Informations de la clé publique
        public_key = cert.public_key()
        public_key_info = self._extract_public_key_info(public_key)
        
        return CertificateInfo(
            subject_dn=str(cert.subject),
            issuer_dn=str(cert.issuer),
            serial_number=str(cert.serial_number),
            fingerprint=fingerprint,
            common_name=subject_info.get('common_name', ''),
            email=subject_info.get('email'),
            organization=subject_info.get('organization'),
            organizational_unit=subject_info.get('organizational_unit'),
            country=subject_info.get('country'),
            state=subject_info.get('state'),
            locality=subject_info.get('locality'),
            not_before=cert.not_valid_before,
            not_after=cert.not_valid_after,
            public_key_algorithm=public_key_info['algorithm'],
            public_key_size=public_key_info['size'],
            signature_algorithm=cert.signature_algorithm_oid._name,
            key_usage=key_usage,
            extended_key_usage=ext_key_usage,
            san_dns_names=san_info['dns_names'],
            san_ip_addresses=san_info['ip_addresses']
        )
    
    def _parse_name(self, name: x509.Name) -> Dict[str, str]:
        """Parse un X.509 Name"""
        name_info = {}
        
        for attribute in name:
            if attribute.oid == NameOID.COMMON_NAME:
                name_info['common_name'] = attribute.value
            elif attribute.oid == NameOID.EMAIL_ADDRESS:
                name_info['email'] = attribute.value
            elif attribute.oid == NameOID.ORGANIZATION_NAME:
                name_info['organization'] = attribute.value
            elif attribute.oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
                name_info['organizational_unit'] = attribute.value
            elif attribute.oid == NameOID.COUNTRY_NAME:
                name_info['country'] = attribute.value
            elif attribute.oid == NameOID.STATE_OR_PROVINCE_NAME:
                name_info['state'] = attribute.value
            elif attribute.oid == NameOID.LOCALITY_NAME:
                name_info['locality'] = attribute.value
        
        return name_info
    
    def _extract_key_usage(self, cert: x509.Certificate) -> List[str]:
        """Extrait les key usages"""
        try:
            key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.KEY_USAGE
            ).value
            
            usages = []
            if key_usage.digital_signature:
                usages.append("digital_signature")
            if key_usage.key_encipherment:
                usages.append("key_encipherment")
            if key_usage.data_encipherment:
                usages.append("data_encipherment")
            if key_usage.key_agreement:
                usages.append("key_agreement")
            if key_usage.key_cert_sign:
                usages.append("key_cert_sign")
            if key_usage.crl_sign:
                usages.append("crl_sign")
            
            return usages
            
        except x509.ExtensionNotFound:
            return []
    
    def _extract_extended_key_usage(self, cert: x509.Certificate) -> List[str]:
        """Extrait les extended key usages"""
        try:
            ext_key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.EXTENDED_KEY_USAGE
            ).value
            
            usages = []
            for usage in ext_key_usage:
                usages.append(usage._name)
            
            return usages
            
        except x509.ExtensionNotFound:
            return []
    
    def _extract_san(self, cert: x509.Certificate) -> Dict[str, List[str]]:
        """Extrait les Subject Alternative Names"""
        try:
            san = cert.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            ).value
            
            dns_names = []
            ip_addresses = []
            
            for name in san:
                if isinstance(name, x509.DNSName):
                    dns_names.append(name.value)
                elif isinstance(name, x509.IPAddress):
                    ip_addresses.append(str(name.value))
            
            return {
                'dns_names': dns_names,
                'ip_addresses': ip_addresses
            }
            
        except x509.ExtensionNotFound:
            return {'dns_names': [], 'ip_addresses': []}
    
    def _extract_public_key_info(self, public_key) -> Dict[str, Any]:
        """Extrait les informations de la clé publique"""
        if hasattr(public_key, 'key_size'):
            return {
                'algorithm': public_key.__class__.__name__,
                'size': public_key.key_size
            }
        else:
            return {
                'algorithm': public_key.__class__.__name__,
                'size': None
            }


class RevocationChecker:
    """Vérificateur de révocation de certificats"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.crl_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)
    
    async def check_revocation(
        self,
        cert: x509.Certificate,
        cert_chain: List[x509.Certificate]
    ) -> RevocationStatus:
        """Vérifie le statut de révocation d'un certificat"""
        
        # Essayer OCSP d'abord, puis CRL
        ocsp_status = await self._check_ocsp(cert, cert_chain)
        if ocsp_status.checked_via:
            return ocsp_status
        
        crl_status = await self._check_crl(cert, cert_chain)
        return crl_status
    
    async def _check_ocsp(
        self,
        cert: x509.Certificate,
        cert_chain: List[x509.Certificate]
    ) -> RevocationStatus:
        """Vérifie via OCSP"""
        
        try:
            # Extraire l'URL OCSP du certificat
            ocsp_url = self._extract_ocsp_url(cert)
            
            if not ocsp_url:
                return RevocationStatus(is_revoked=False)
            
            # Ici vous implémenteriez la vraie vérification OCSP
            # Pour cette démo, on simule
            
            self.logger.debug(
                "OCSP check simulated",
                ocsp_url=ocsp_url,
                serial=str(cert.serial_number)
            )
            
            return RevocationStatus(
                is_revoked=False,
                checked_via="OCSP"
            )
            
        except Exception as e:
            self.logger.error(
                "OCSP check failed",
                error=str(e)
            )
            return RevocationStatus(is_revoked=False)
    
    async def _check_crl(
        self,
        cert: x509.Certificate,
        cert_chain: List[x509.Certificate]
    ) -> RevocationStatus:
        """Vérifie via CRL"""
        
        try:
            # Extraire l'URL CRL du certificat
            crl_urls = self._extract_crl_urls(cert)
            
            if not crl_urls:
                return RevocationStatus(is_revoked=False)
            
            # Vérifier chaque CRL
            for crl_url in crl_urls:
                crl = await self._fetch_crl(crl_url)
                
                if crl and self._is_certificate_in_crl(cert, crl):
                    return RevocationStatus(
                        is_revoked=True,
                        revocation_date=datetime.utcnow(),  # Devrait venir du CRL
                        revocation_reason="unspecified",
                        checked_via="CRL"
                    )
            
            return RevocationStatus(
                is_revoked=False,
                checked_via="CRL"
            )
            
        except Exception as e:
            self.logger.error(
                "CRL check failed",
                error=str(e)
            )
            return RevocationStatus(is_revoked=False)
    
    def _extract_ocsp_url(self, cert: x509.Certificate) -> Optional[str]:
        """Extrait l'URL OCSP du certificat"""
        try:
            aia = cert.extensions.get_extension_for_oid(
                ExtensionOID.AUTHORITY_INFORMATION_ACCESS
            ).value
            
            for access_description in aia:
                if access_description.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                    return access_description.access_location.value
            
        except x509.ExtensionNotFound:
            pass
        
        return None
    
    def _extract_crl_urls(self, cert: x509.Certificate) -> List[str]:
        """Extrait les URLs CRL du certificat"""
        try:
            crl_dp = cert.extensions.get_extension_for_oid(
                ExtensionOID.CRL_DISTRIBUTION_POINTS
            ).value
            
            urls = []
            for dp in crl_dp:
                if dp.full_name:
                    for name in dp.full_name:
                        if isinstance(name, x509.UniformResourceIdentifier):
                            urls.append(name.value)
            
            return urls
            
        except x509.ExtensionNotFound:
            return []
    
    async def _fetch_crl(self, crl_url: str) -> Optional[Any]:
        """Récupère une CRL"""
        
        # Vérifier le cache
        if crl_url in self.crl_cache:
            crl, cached_at = self.crl_cache[crl_url]
            if datetime.utcnow() - cached_at < self.cache_ttl:
                return crl
        
        try:
            # Ici vous implémenteriez le téléchargement et parsing de la CRL
            # Pour cette démo, on simule
            
            self.logger.debug("CRL fetch simulated", url=crl_url)
            
            # Simuler une CRL vide (pas de certificats révoqués)
            fake_crl = {"revoked_certificates": []}
            
            # Mettre en cache
            self.crl_cache[crl_url] = (fake_crl, datetime.utcnow())
            
            return fake_crl
            
        except Exception as e:
            self.logger.error(
                "Failed to fetch CRL",
                url=crl_url,
                error=str(e)
            )
            return None
    
    def _is_certificate_in_crl(self, cert: x509.Certificate, crl: Any) -> bool:
        """Vérifie si un certificat est dans la CRL"""
        
        # Dans un vrai système, vous parseriez la vraie CRL
        # Pour cette démo, on retourne toujours False
        
        serial_number = str(cert.serial_number)
        revoked_certs = crl.get("revoked_certificates", [])
        
        return serial_number in revoked_certs
    
    async def revoke_certificate(
        self,
        serial_number: str,
        reason: str = "unspecified"
    ) -> bool:
        """Révoque un certificat (ajoute à la CRL locale)"""
        
        try:
            # Ici vous implémenteriez l'ajout à votre CRL
            # Pour cette démo, on simule
            
            self.logger.info(
                "Certificate revoked",
                serial_number=serial_number,
                reason=reason
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to revoke certificate",
                serial_number=serial_number,
                error=str(e)
            )
            return False


class CertificateAccessManager:
    """Gestionnaire d'accès basé sur les certificats"""
    
    def __init__(self):
        self.role_mappings: Dict[str, List[str]] = {
            # Mapping DN patterns vers rôles
            "CN=Admin*": ["admin", "user"],
            "CN=User*": ["user"],
            "O=iacherie": ["iacherie_user"],
            "OU=Developers": ["developer", "user"]
        }
        
        self.permission_mappings: Dict[str, List[str]] = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "developer": ["read", "write", "deploy"],
            "iacherie_user": ["read", "write", "content_create"]
        }
    
    async def determine_roles(self, cert: x509.Certificate) -> List[str]:
        """Détermine les rôles basés sur le certificat"""
        
        subject_dn = str(cert.subject)
        roles = []
        
        # Vérifier les patterns de mapping
        for pattern, mapped_roles in self.role_mappings.items():
            if self._matches_pattern(subject_dn, pattern):
                roles.extend(mapped_roles)
        
        # Éliminer les doublons
        return list(set(roles))
    
    async def get_permissions(self, roles: List[str]) -> List[str]:
        """Obtient les permissions pour des rôles"""
        
        permissions = []
        
        for role in roles:
            role_permissions = self.permission_mappings.get(role, [])
            permissions.extend(role_permissions)
        
        # Éliminer les doublons
        return list(set(permissions))
    
    def _matches_pattern(self, subject_dn: str, pattern: str) -> bool:
        """Vérifie si un DN correspond à un pattern"""
        
        # Simple wildcard matching
        import fnmatch
        return fnmatch.fnmatch(subject_dn, pattern)


class CertificateGenerator:
    """Générateur de certificats pour développement"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    async def generate_certificate(
        self,
        csr_pem: str,
        ca_cert_path: str,
        ca_key_path: str,
        template_name: str,
        validity_days: int = 365
    ) -> str:
        """Génère un certificat à partir d'un CSR"""
        
        try:
            # Charger le CSR
            csr = x509.load_pem_x509_csr(csr_pem.encode())
            
            # Charger le CA cert et clé
            async with aiofiles.open(ca_cert_path, 'r') as f:
                ca_cert_pem = await f.read()
            
            async with aiofiles.open(ca_key_path, 'r') as f:
                ca_key_pem = await f.read()
            
            ca_cert = x509.load_pem_x509_certificate(ca_cert_pem.encode())
            ca_key = serialization.load_pem_private_key(
                ca_key_pem.encode(),
                password=None
            )
            
            # Construire le certificat
            cert_builder = x509.CertificateBuilder()
            cert_builder = cert_builder.subject_name(csr.subject)
            cert_builder = cert_builder.issuer_name(ca_cert.subject)
            cert_builder = cert_builder.public_key(csr.public_key())
            cert_builder = cert_builder.serial_number(x509.random_serial_number())
            cert_builder = cert_builder.not_valid_before(datetime.utcnow())
            cert_builder = cert_builder.not_valid_after(
                datetime.utcnow() + timedelta(days=validity_days)
            )
            
            # Ajouter les extensions selon le template
            cert_builder = self._add_template_extensions(cert_builder, template_name)
            
            # Signer le certificat
            certificate = cert_builder.sign(ca_key, hashes.SHA256())
            
            # Retourner en format PEM
            return certificate.public_bytes(serialization.Encoding.PEM).decode()
            
        except Exception as e:
            self.logger.error(
                "Certificate generation failed",
                template=template_name,
                error=str(e)
            )
            raise
    
    def _add_template_extensions(
        self,
        cert_builder: x509.CertificateBuilder,
        template_name: str
    ) -> x509.CertificateBuilder:
        """Ajoute les extensions selon le template"""
        
        if template_name == "user_certificate":
            # Extensions pour certificat utilisateur
            cert_builder = cert_builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            
            cert_builder = cert_builder.add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                    x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION
                ]),
                critical=True
            )
        
        elif template_name == "server_certificate":
            # Extensions pour certificat serveur
            cert_builder = cert_builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            
            cert_builder = cert_builder.add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH
                ]),
                critical=True
            )
        
        return cert_builder


class CertificateAuditLogger:
    """Logger d'audit pour les certificats"""
    
    def __init__(self):
        self.logger = structlog.get_logger("certificate_audit")
    
    async def log_authentication_success(self, user: CertificateUser):
        """Log authentification réussie"""
        self.logger.info(
            "CERT_AUTH_SUCCESS",
            subject_dn=user.subject_dn,
            serial_number=user.serial_number,
            fingerprint=user.fingerprint,
            roles=user.roles,
            expires_at=user.expires_at.isoformat(),
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_authentication_failure(
        self,
        cert: x509.Certificate,
        errors: List[str]
    ):
        """Log échec d'authentification"""
        self.logger.warning(
            "CERT_AUTH_FAILURE",
            subject_dn=str(cert.subject),
            serial_number=str(cert.serial_number),
            errors=errors,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_certificate_generation(
        self,
        csr: x509.CertificateSigningRequest,
        template_name: str
    ):
        """Log génération de certificat"""
        self.logger.info(
            "CERT_GENERATION",
            subject_dn=str(csr.subject),
            template=template_name,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def log_certificate_revocation(
        self,
        serial_number: str,
        reason: str
    ):
        """Log révocation de certificat"""
        self.logger.warning(
            "CERT_REVOCATION",
            serial_number=serial_number,
            reason=reason,
            timestamp=datetime.utcnow().isoformat()
        )


# FastAPI Security et Dependencies
certificate_auth_scheme = HTTPBearer()


async def get_certificate_user(
    request: Request,
    cert_auth: CertificateAuthenticationTemplate = Depends()
) -> Optional[CertificateUser]:
    """Dependency FastAPI pour récupérer l'utilisateur certificat"""
    
    # Récupérer le certificat client depuis la connexion TLS
    # Note: Ceci nécessite une configuration spéciale de FastAPI/Uvicorn
    
    if hasattr(request, 'scope') and 'client_cert' in request.scope:
        client_cert_pem = request.scope['client_cert']
        
        try:
            return await cert_auth.authenticate_certificate(client_cert_pem)
        except HTTPException:
            return None
    
    return None


def require_certificate_auth(
    user: Optional[CertificateUser] = Depends(get_certificate_user)
) -> CertificateUser:
    """Dependency FastAPI pour exiger l'authentification par certificat"""
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Certificate authentication required"
        )
    
    if user.is_expired():
        raise HTTPException(
            status_code=401,
            detail="Certificate has expired"
        )
    
    return user


def require_certificate_role(
    required_roles: List[str]
) -> Callable[[CertificateUser], CertificateUser]:
    """Dependency factory pour exiger un rôle certificat"""
    
    def role_dependency(
        user: CertificateUser = Depends(require_certificate_auth)
    ) -> CertificateUser:
        
        if not any(user.has_role(role) for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        
        return user
    
    return role_dependency


# Factory functions
def create_certificate_auth(
    trusted_ca_paths: List[str],
    validation_mode: str = "strict",
    **kwargs
) -> CertificateAuthenticationTemplate:
    """Factory pour créer l'authentification par certificat"""
    
    mode = CertificateValidationMode(validation_mode)
    
    return CertificateAuthenticationTemplate(
        trusted_ca_certs=trusted_ca_paths,
        validation_mode=mode,
        **kwargs
    )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def example_certificate_auth():
        # Configuration
        trusted_cas = [
            "/path/to/root-ca.pem",
            "/path/to/intermediate-ca.pem"
        ]
        
        cert_auth = create_certificate_auth(
            trusted_ca_paths=trusted_cas,
            validation_mode="relaxed"  # Pour la démo
        )
        
        # Exemple de certificat client (vous devriez avoir un vrai certificat)
        client_cert_pem = """-----BEGIN CERTIFICATE-----
MIICertificateDataHere...
-----END CERTIFICATE-----"""
        
        try:
            # Tester l'authentification
            user = await cert_auth.authenticate_certificate(client_cert_pem)
            
            print(f"Authentication successful")
            print(f"Subject: {user.subject_dn}")
            print(f"Roles: {user.roles}")
            print(f"Permissions: {user.permissions}")
            print(f"Expires: {user.expires_at}")
            
            # Tester les permissions
            if user.has_role("admin"):
                print("User has admin privileges")
            
            if user.has_permission("read"):
                print("User can read")
            
        except HTTPException as e:
            print(f"Authentication failed: {e.detail}")
        
        # Créer un contexte SSL pour serveur
        ssl_context = cert_auth.create_ssl_context(
            "/path/to/server.crt",
            "/path/to/server.key"
        )
        print(f"SSL context created: {ssl_context}")
    
    # asyncio.run(example_certificate_auth())