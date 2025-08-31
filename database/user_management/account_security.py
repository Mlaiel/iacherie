"""Account Security Database Models and Operations

Gestion complète de la sécurité des comptes avec authentification multi-facteur,
surveillance des menaces et protection avancée.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Cybersecurity Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum as PyEnum
import logging
import uuid
import hashlib
import secrets
import base64
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

Base = declarative_base()


class SecurityEventType(PyEnum):
    """Types d'événements de sécurité."""    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    TWO_FACTOR_DISABLED = "two_factor_disabled"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    API_KEY_GENERATED = "api_key_generated"
    API_KEY_REVOKED = "api_key_revoked"
    DEVICE_REGISTERED = "device_registered"
    DEVICE_REMOVED = "device_removed"


class ThreatLevel(PyEnum):
    """Niveaux de menace."""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeviceType(PyEnum):
    """Types d'appareils."""    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    API_CLIENT = "api_client"
    UNKNOWN = "unknown"


class SecurityStatus(PyEnum):
    """Statuts de sécurité du compte."""    SECURE = "secure"
    AT_RISK = "at_risk"
    COMPROMISED = "compromised"
    LOCKED = "locked"
    UNDER_REVIEW = "under_review"


class UserSecurity(Base):
    """    Profil de sécurité principal de l'utilisateur.
    """    __tablename__ = "user_security"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Authentification
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255), nullable=False)
    password_last_changed = Column(DateTime, default=datetime.utcnow)
    password_expires_at = Column(DateTime)
    force_password_change = Column(Boolean, default=False)
    
    # Authentification multi-facteur
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))  # Chiffré
    backup_codes = Column(JSON)  # Codes de récupération chiffrés
    two_factor_last_used = Column(DateTime)
    
    # Sécurité du compte
    security_status = Column(Enum(SecurityStatus), default=SecurityStatus.SECURE)
    account_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime)
    
    # Tokens et sessions
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime)
    email_verification_token = Column(String(255))
    email_verification_expires = Column(DateTime)
    
    # Clés API
    api_key_hash = Column(String(255))
    api_key_last_used = Column(DateTime)
    api_rate_limit = Column(Integer, default=1000)  # Requêtes par heure
    
    # Surveillance et alertes
    suspicious_activity_score = Column(Decimal(5, 2), default=0.00)
    last_security_scan = Column(DateTime)
    security_alerts_enabled = Column(Boolean, default=True)
    login_notifications = Column(Boolean, default=True)
    
    # Conformité et audit
    gdpr_consent_date = Column(DateTime)
    data_retention_days = Column(Integer, default=365)
    last_audit_date = Column(DateTime)
    compliance_score = Column(Decimal(5, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="security")
    security_logs = relationship("UserSecurityLog", back_populates="user_security")
    trusted_devices = relationship("TrustedDevice", back_populates="user_security")
    api_keys = relationship("APIKey", back_populates="user_security")

    def __repr__(self):
        return f"<UserSecurity({self.user_id})>"
    
    def is_password_expired(self) -> bool:
        """Vérifie si le mot de passe a expiré."""        if not self.password_expires_at:
            return False
        return datetime.utcnow() > self.password_expires_at
    
    def is_account_locked(self) -> bool:
        """Vérifie si le compte est verrouillé."""        if not self.account_locked:
            return False
        if self.locked_until and datetime.utcnow() > self.locked_until:
            return False
        return True
    
    def calculate_security_score(self) -> float:
        """Calcule le score de sécurité du compte."""        score = 0.0
        
        # Mot de passe récent (+20%)
        if self.password_last_changed and (datetime.utcnow() - self.password_last_changed).days < 90:
            score += 20
        
        # 2FA activé (+30%)
        if self.two_factor_enabled:
            score += 30
        
        # Pas d'activité suspecte (+25%)
        if self.suspicious_activity_score < 5.0:
            score += 25
        
        # Appareils de confiance (+15%)
        if len(self.trusted_devices) > 0:
            score += 15
        
        # Pas de tentatives de connexion échouées récentes (+10%)
        if not self.last_failed_login or (datetime.utcnow() - self.last_failed_login).days > 7:
            score += 10
        
        return min(100.0, score)


class UserSecurityLog(Base):
    """    Journal des événements de sécurité utilisateur.
    """    __tablename__ = "user_security_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_security_id = Column(String, ForeignKey("user_security.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Événement
    event_type = Column(Enum(SecurityEventType), nullable=False)
    threat_level = Column(Enum(ThreatLevel), default=ThreatLevel.LOW)
    description = Column(Text)
    
    # Contexte technique
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_fingerprint = Column(String(255))
    session_id = Column(String(255))
    
    # Géolocalisation
    country_code = Column(String(3))
    city = Column(String(100))
    coordinates = Column(JSON)  # {"lat": 48.8566, "lng": 2.3522}
    
    # Détails de l'événement
    event_data = Column(JSON)
    success = Column(Boolean, default=True)
    error_code = Column(String(50))
    risk_score = Column(Decimal(5, 2), default=0.00)
    
    # Action et résolution
    action_taken = Column(String(255))
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(255))
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user_security = relationship("UserSecurity", back_populates="security_logs")
    user = relationship("User", back_populates="security_logs")

    def __repr__(self):
        return f"<UserSecurityLog({self.event_type.value}, {self.threat_level.value})>"


class TrustedDevice(Base):
    """    Appareils de confiance pour l'authentification.
    """    __tablename__ = "trusted_devices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_security_id = Column(String, ForeignKey("user_security.id"), nullable=False)
    
    # Identifiants de l'appareil
    device_fingerprint = Column(String(255), nullable=False, unique=True)
    device_name = Column(String(255))
    device_type = Column(Enum(DeviceType), default=DeviceType.UNKNOWN)
    
    # Informations techniques
    browser = Column(String(100))
    operating_system = Column(String(100))
    screen_resolution = Column(String(20))
    timezone = Column(String(50))
    
    # Localisation
    country_code = Column(String(3))
    city = Column(String(100))
    last_ip = Column(String(45))
    
    # État et sécurité
    is_active = Column(Boolean, default=True)
    is_trusted = Column(Boolean, default=False)
    trust_score = Column(Decimal(5, 2), default=0.00)
    
    # Usage
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    login_count = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime)
    auto_trust_enabled = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user_security = relationship("UserSecurity", back_populates="trusted_devices")

    def __repr__(self):
        return f"<TrustedDevice({self.device_name}, {self.device_type.value})>"
    
    def is_expired(self) -> bool:
        """Vérifie si l'appareil de confiance a expiré."""        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def update_last_seen(self, ip_address: str):
        """Met à jour la dernière utilisation de l'appareil."""        self.last_seen = datetime.utcnow()
        self.last_ip = ip_address
        self.login_count += 1


class APIKey(Base):
    """    Clés API pour l'accès programmatique.
    """    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_security_id = Column(String, ForeignKey("user_security.id"), nullable=False)
    
    # Identifiants
    key_name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    key_prefix = Column(String(10))  # Premiers caractères visibles
    
    # Permissions et limites
    permissions = Column(JSON)  # Liste des permissions
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Restrictions
    allowed_ips = Column(JSON)  # IPs autorisées
    allowed_domains = Column(JSON)  # Domaines autorisés
    restricted_endpoints = Column(JSON)  # Endpoints restreints
    
    # État
    is_active = Column(Boolean, default=True)
    is_master_key = Column(Boolean, default=False)
    
    # Usage
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    expires_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # Sécurité
    last_used_ip = Column(String(45))
    suspicious_usage = Column(Boolean, default=False)
    
    # Relations
    user_security = relationship("UserSecurity", back_populates="api_keys")
    usage_logs = relationship("APIUsageLog", back_populates="api_key")

    def __repr__(self):
        return f"<APIKey({self.key_name}, {self.key_prefix}...)>"
    
    def is_expired(self) -> bool:
        """Vérifie si la clé API a expiré."""        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def can_access_endpoint(self, endpoint: str) -> bool:
        """Vérifie si la clé peut accéder à un endpoint."""        if not self.is_active or self.is_expired():
            return False
        
        if self.is_master_key:
            return True
        
        restricted = self.restricted_endpoints or []
        return endpoint not in restricted
    
    def record_usage(self, ip_address: str, endpoint: str):
        """Enregistre une utilisation de la clé."""        self.last_used = datetime.utcnow()
        self.last_used_ip = ip_address
        self.usage_count += 1


class APIUsageLog(Base):
    """    Journal d'utilisation des clés API.
    """    __tablename__ = "api_usage_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=False)
    
    # Requête
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Réponse
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    response_size_bytes = Column(Integer)
    
    # Métadonnées
    request_data = Column(JSON)  # Données de la requête (anonymisées)
    error_message = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    api_key = relationship("APIKey", back_populates="usage_logs")

    def __repr__(self):
        return f"<APIUsageLog({self.method} {self.endpoint}, {self.status_code})>"


class SecurityRepository:
    """    Repository pattern pour la gestion de la sécurité des comptes.
    Implémentation professionnelle avec chiffrement et surveillance.
    """    
    def __init__(self, session: Session, encryption_key: str = None):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def create_user_security(self, user_id: str, password: str) -> UserSecurity:
        """        Crée le profil de sécurité pour un nouvel utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            UserSecurity: Profil de sécurité créé
        """        try:
            # Génération du sel et hachage du mot de passe
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            # Création du profil de sécurité
            user_security = UserSecurity(
                user_id=user_id,
                password_hash=password_hash,
                password_salt=salt,
                password_expires_at=datetime.utcnow() + timedelta(days=90)
            )
            
            self.session.add(user_security)
            self.session.commit()
            
            # Log de création
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.LOGIN_SUCCESS,
                "Profil de sécurité créé",
                ThreatLevel.LOW
            )
            
            self.logger.info(f"Profil de sécurité créé: {user_id}")
            return user_security
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur création profil sécurité: {str(e)}")
            raise
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """        Vérifie le mot de passe d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            password: Mot de passe à vérifier
            
        Returns:
            bool: True si le mot de passe est correct
        """        user_security = self.session.query(UserSecurity).filter(
            UserSecurity.user_id == user_id
        ).first()
        
        if not user_security:
            return False
        
        # Vérification du verrouillage
        if user_security.is_account_locked():
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.LOGIN_FAILED,
                "Tentative de connexion sur compte verrouillé",
                ThreatLevel.HIGH
            )
            return False
        
        # Vérification du mot de passe
        password_hash = self._hash_password(password, user_security.password_salt)
        is_valid = password_hash == user_security.password_hash
        
        if is_valid:
            # Réinitialisation des tentatives échouées
            user_security.failed_login_attempts = 0
            user_security.last_failed_login = None
            
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.LOGIN_SUCCESS,
                "Connexion réussie",
                ThreatLevel.LOW
            )
        else:
            # Incrément des tentatives échouées
            user_security.failed_login_attempts += 1
            user_security.last_failed_login = datetime.utcnow()
            
            # Verrouillage automatique après 5 tentatives
            if user_security.failed_login_attempts >= 5:
                user_security.account_locked = True
                user_security.locked_until = datetime.utcnow() + timedelta(hours=1)
                threat_level = ThreatLevel.HIGH
            else:
                threat_level = ThreatLevel.MEDIUM
            
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.LOGIN_FAILED,
                f"Tentative de connexion échouée ({user_security.failed_login_attempts}/5)",
                threat_level
            )
        
        self.session.commit()
        return is_valid
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """        Change le mot de passe d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
            
        Returns:
            bool: True si le changement a réussi
        """        try:
            # Vérification de l'ancien mot de passe
            if not self.verify_password(user_id, old_password):
                return False
            
            user_security = self.session.query(UserSecurity).filter(
                UserSecurity.user_id == user_id
            ).first()
            
            if not user_security:
                return False
            
            # Génération du nouveau hash
            new_salt = secrets.token_hex(32)
            new_hash = self._hash_password(new_password, new_salt)
            
            # Mise à jour
            user_security.password_hash = new_hash
            user_security.password_salt = new_salt
            user_security.password_last_changed = datetime.utcnow()
            user_security.password_expires_at = datetime.utcnow() + timedelta(days=90)
            user_security.force_password_change = False
            
            self.session.commit()
            
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.PASSWORD_CHANGE,
                "Mot de passe modifié avec succès",
                ThreatLevel.LOW
            )
            
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur changement mot de passe: {str(e)}")
            return False
    
    def enable_two_factor(self, user_id: str) -> Optional[str]:
        """        Active l'authentification à deux facteurs.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Optional[str]: Secret 2FA en base32
        """        try:
            user_security = self.session.query(UserSecurity).filter(
                UserSecurity.user_id == user_id
            ).first()
            
            if not user_security:
                return None
            
            # Génération du secret 2FA
            secret = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
            encrypted_secret = self.cipher_suite.encrypt(secret.encode()).decode()
            
            # Génération des codes de récupération
            backup_codes = [secrets.token_hex(8) for _ in range(10)]
            encrypted_codes = [
                self.cipher_suite.encrypt(code.encode()).decode() 
                for code in backup_codes
            ]
            
            # Mise à jour
            user_security.two_factor_enabled = True
            user_security.two_factor_secret = encrypted_secret
            user_security.backup_codes = encrypted_codes
            
            self.session.commit()
            
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.TWO_FACTOR_ENABLED,
                "Authentification 2FA activée",
                ThreatLevel.LOW
            )
            
            return secret
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur activation 2FA: {str(e)}")
            return None
    
    def generate_api_key(self, user_id: str, key_name: str, 
                        permissions: List[str] = None) -> Optional[str]:
        """        Génère une nouvelle clé API.
        
        Args:
            user_id: ID de l'utilisateur
            key_name: Nom de la clé
            permissions: Permissions accordées
            
        Returns:
            Optional[str]: Clé API générée
        """        try:
            user_security = self.session.query(UserSecurity).filter(
                UserSecurity.user_id == user_id
            ).first()
            
            if not user_security:
                return None
            
            # Génération de la clé
            api_key = f"ak_{secrets.token_urlsafe(32)}"
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            key_prefix = api_key[:8]
            
            # Création de l'enregistrement
            api_key_record = APIKey(
                user_security_id=user_security.id,
                key_name=key_name,
                key_hash=key_hash,
                key_prefix=key_prefix,
                permissions=permissions or [],
                expires_at=datetime.utcnow() + timedelta(days=365)
            )
            
            self.session.add(api_key_record)
            self.session.commit()
            
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.API_KEY_GENERATED,
                f"Clé API générée: {key_name}",
                ThreatLevel.LOW
            )
            
            return api_key
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur génération clé API: {str(e)}")
            return None
    
    def register_trusted_device(self, user_id: str, device_data: Dict[str, Any]) -> bool:
        """        Enregistre un appareil de confiance.
        
        Args:
            user_id: ID de l'utilisateur
            device_data: Données de l'appareil
            
        Returns:
            bool: True si enregistré avec succès
        """        try:
            user_security = self.session.query(UserSecurity).filter(
                UserSecurity.user_id == user_id
            ).first()
            
            if not user_security:
                return False
            
            # Création de l'empreinte de l'appareil
            device_fingerprint = self._generate_device_fingerprint(device_data)
            
            # Vérification si l'appareil existe déjà
            existing_device = self.session.query(TrustedDevice).filter(
                TrustedDevice.device_fingerprint == device_fingerprint
            ).first()
            
            if existing_device:
                existing_device.update_last_seen(device_data.get('ip_address', ''))
                self.session.commit()
                return True
            
            # Nouveau device
            trusted_device = TrustedDevice(
                user_security_id=user_security.id,
                device_fingerprint=device_fingerprint,
                device_name=device_data.get('device_name', 'Unknown Device'),
                device_type=DeviceType(device_data.get('device_type', 'unknown')),
                browser=device_data.get('browser'),
                operating_system=device_data.get('operating_system'),
                country_code=device_data.get('country_code'),
                city=device_data.get('city'),
                last_ip=device_data.get('ip_address'),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            self.session.add(trusted_device)
            self.session.commit()
            
            self._log_security_event(
                user_security.id,
                user_id,
                SecurityEventType.DEVICE_REGISTERED,
                f"Appareil enregistré: {trusted_device.device_name}",
                ThreatLevel.LOW
            )
            
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Erreur enregistrement appareil: {str(e)}")
            return False
    
    def get_security_score(self, user_id: str) -> float:
        """        Calcule le score de sécurité d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            float: Score de sécurité (0-100)
        """        user_security = self.session.query(UserSecurity).filter(
            UserSecurity.user_id == user_id
        ).first()
        
        if not user_security:
            return 0.0
        
        return user_security.calculate_security_score()
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash un mot de passe avec un sel."""        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _generate_device_fingerprint(self, device_data: Dict[str, Any]) -> str:
        """Génère une empreinte unique pour un appareil."""        fingerprint_data = f"{device_data.get('user_agent', '')}" \
                          f"{device_data.get('screen_resolution', '')}" \
                          f"{device_data.get('timezone', '')}" \
                          f"{device_data.get('language', '')}"
        
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def _log_security_event(self, user_security_id: str, user_id: str, 
                           event_type: SecurityEventType, description: str,
                           threat_level: ThreatLevel, event_data: Dict = None):
        """Enregistre un événement de sécurité."""        try:
            security_log = UserSecurityLog(
                user_security_id=user_security_id,
                user_id=user_id,
                event_type=event_type,
                threat_level=threat_level,
                description=description,
                event_data=event_data or {}
            )
            
            self.session.add(security_log)
            # Note: commit sera fait par la fonction appelante
            
        except Exception as e:
            self.logger.error(f"Erreur log sécurité: {str(e)}")


# Configuration des relations
UserSecurity.security_logs = relationship("UserSecurityLog", back_populates="user_security")
UserSecurity.trusted_devices = relationship("TrustedDevice", back_populates="user_security")
UserSecurity.api_keys = relationship("APIKey", back_populates="user_security")
