"""
Push Notification Manager

Gestionnaire avancé des notifications push pour mobiles et web.
Support multi-plateformes avec Firebase, APNs, WebPush et analytics avancés.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, ML Engineer, Mobile Expert
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et constitue une violation des droits d'auteur.
Les contrevenants s'exposent à des poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import aiohttp
import asyncpg
import aioredis
from firebase_admin import messaging, credentials, initialize_app
import jwt
import time

logger = logging.getLogger(__name__)


class PushPlatform(Enum):
    """Plateformes de notification push"""
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    WINDOWS = "windows"
    MACOS = "macos"


class PushPriority(Enum):
    """Priorités des notifications push"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PushStatus(Enum):
    """Statuts des notifications push"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CLICKED = "clicked"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class NotificationType(Enum):
    """Types de notifications"""
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_REQUEST = "collaboration_request"
    REVENUE_UPDATE = "revenue_update"
    SYSTEM_ALERT = "system_alert"
    MARKETING = "marketing"
    SECURITY = "security"


@dataclass
class PushDevice:
    """Appareil pour notifications push"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    platform: PushPlatform = PushPlatform.ANDROID
    token: str = ""
    endpoint: Optional[str] = None
    p256dh_key: Optional[str] = None
    auth_key: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    device_model: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"
    is_active: bool = True
    last_seen: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PushNotification:
    """Notification push"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    device_id: Optional[str] = None
    platform: Optional[PushPlatform] = None
    notification_type: NotificationType = NotificationType.SYSTEM_ALERT
    title: str = ""
    body: str = ""
    icon: Optional[str] = None
    image: Optional[str] = None
    badge: Optional[int] = None
    sound: Optional[str] = None
    priority: PushPriority = PushPriority.NORMAL
    ttl: int = 86400  # 24 heures
    collapse_key: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, str]] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    click_action: Optional[str] = None
    deep_link: Optional[str] = None
    tracking_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PushDelivery:
    """Livraison de notification push"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notification_id: str = ""
    device_id: str = ""
    platform: PushPlatform = PushPlatform.ANDROID
    status: PushStatus = PushStatus.PENDING
    provider_message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class FirebasePushProvider:
    """Fournisseur Firebase Cloud Messaging"""
    
    def __init__(self, credentials_path: str, project_id: str):
        self.project_id = project_id
        self.app = None
        self._init_firebase(credentials_path)
    
    def _init_firebase(self, credentials_path: str):
        """Initialiser Firebase"""
        try:
            cred = credentials.Certificate(credentials_path)
            self.app = initialize_app(cred, name=f"push_{self.project_id}")
            logger.info(f"Firebase initialisé pour le projet {self.project_id}")
        except Exception as e:
            logger.error(f"Erreur initialisation Firebase: {e}")
            raise
    
    async def send_notification(self, notification: PushNotification, device: PushDevice) -> Dict[str, Any]:
        """Envoyer une notification via FCM"""
        try:
            # Construire le message FCM
            fcm_message = self._build_fcm_message(notification, device)
            
            # Envoyer via Firebase
            response = messaging.send(fcm_message, app=self.app)
            
            return {
                "success": True,
                "message_id": response,
                "platform": device.platform.value,
                "device_token": device.token
            }
            
        except messaging.UnregisteredError:
            return {
                "success": False,
                "error": "Device token invalid or expired",
                "should_remove_device": True
            }
        except messaging.SenderIdMismatchError:
            return {
                "success": False,
                "error": "Sender ID mismatch",
                "should_remove_device": True
            }
        except Exception as e:
            logger.error(f"Erreur envoi FCM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_fcm_message(self, notification: PushNotification, device: PushDevice) -> messaging.Message:
        """Construire un message FCM"""
        # Configuration de base
        fcm_notification = messaging.Notification(
            title=notification.title,
            body=notification.body,
            image=notification.image
        )
        
        # Configuration Android
        android_config = messaging.AndroidConfig(
            priority=self._get_android_priority(notification.priority),
            ttl=timedelta(seconds=notification.ttl),
            collapse_key=notification.collapse_key,
            notification=messaging.AndroidNotification(
                icon=notification.icon,
                sound=notification.sound,
                click_action=notification.click_action,
                badge=notification.badge
            )
        )
        
        # Configuration iOS
        apns_config = messaging.APNSConfig(
            headers={
                "apns-priority": self._get_apns_priority(notification.priority),
                "apns-expiration": str(int(time.time()) + notification.ttl)
            },
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=notification.title,
                        body=notification.body
                    ),
                    badge=notification.badge,
                    sound=notification.sound,
                    category=notification.notification_type.value
                )
            )
        )
        
        # Configuration Web
        webpush_config = messaging.WebpushConfig(
            headers={
                "TTL": str(notification.ttl)
            },
            notification=messaging.WebpushNotification(
                title=notification.title,
                body=notification.body,
                icon=notification.icon,
                image=notification.image,
                badge=notification.badge,
                actions=[
                    messaging.WebpushNotificationAction(
                        action=action["action"],
                        title=action["title"]
                    ) for action in notification.actions
                ]
            )
        )
        
        return messaging.Message(
            token=device.token,
            notification=fcm_notification,
            data=notification.data,
            android=android_config,
            apns=apns_config,
            webpush=webpush_config
        )
    
    def _get_android_priority(self, priority: PushPriority) -> str:
        """Convertir la priorité en priorité Android"""
        mapping = {
            PushPriority.LOW: "normal",
            PushPriority.NORMAL: "normal", 
            PushPriority.HIGH: "high",
            PushPriority.CRITICAL: "high"
        }
        return mapping.get(priority, "normal")
    
    def _get_apns_priority(self, priority: PushPriority) -> str:
        """Convertir la priorité en priorité APNs"""
        mapping = {
            PushPriority.LOW: "5",
            PushPriority.NORMAL: "5",
            PushPriority.HIGH: "10", 
            PushPriority.CRITICAL: "10"
        }
        return mapping.get(priority, "5")


class WebPushProvider:
    """Fournisseur Web Push direct"""
    
    def __init__(self, vapid_private_key: str, vapid_public_key: str, vapid_subject: str):
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_subject = vapid_subject
    
    async def send_notification(self, notification: PushNotification, device: PushDevice) -> Dict[str, Any]:
        """Envoyer une notification Web Push"""
        try:
            if not device.endpoint or not device.p256dh_key or not device.auth_key:
                raise ValueError("Données Web Push incomplètes")
            
            # Préparer le payload
            payload = {
                "title": notification.title,
                "body": notification.body,
                "icon": notification.icon,
                "image": notification.image,
                "badge": notification.badge,
                "data": notification.data,
                "actions": notification.actions,
                "tag": notification.collapse_key,
                "requireInteraction": notification.priority in [PushPriority.HIGH, PushPriority.CRITICAL]
            }
            
            # Chiffrer le payload
            encrypted_data = self._encrypt_payload(
                json.dumps(payload),
                device.p256dh_key,
                device.auth_key
            )
            
            # Générer les en-têtes VAPID
            vapid_headers = self._generate_vapid_headers(device.endpoint)
            
            # Envoyer la requête
            headers = {
                **vapid_headers,
                "Content-Type": "application/octet-stream",
                "Content-Encoding": "aes128gcm",
                "TTL": str(notification.ttl)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    device.endpoint,
                    data=encrypted_data,
                    headers=headers
                ) as response:
                    if response.status in [200, 201, 204]:
                        return {
                            "success": True,
                            "status_code": response.status,
                            "endpoint": device.endpoint
                        }
                    elif response.status == 410:
                        return {
                            "success": False,
                            "error": "Endpoint expired",
                            "should_remove_device": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"Erreur envoi Web Push: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _encrypt_payload(self, payload: str, p256dh_key: str, auth_key: str) -> bytes:
        """Chiffrer le payload Web Push"""
        try:
            # Décoder les clés
            receiver_key = base64.urlsafe_b64decode(p256dh_key + "==")
            auth_secret = base64.urlsafe_b64decode(auth_key + "==")
            
            # Générer une clé éphémère
            private_key = ec.generate_private_key(ec.SECP256R1())
            public_key = private_key.public_key()
            
            # Sérialiser la clé publique
            public_key_bytes = public_key.public_numbers().x.to_bytes(32, 'big') + \
                              public_key.public_numbers().y.to_bytes(32, 'big')
            
            # Calculer le secret partagé
            shared_key = private_key.exchange(
                ec.EllipticCurvePublicKey.from_encoded_point(
                    ec.SECP256R1(), 
                    b'\x04' + receiver_key
                )
            )
            
            # Dériver les clés de chiffrement
            context = b"WebPush: info\x00" + receiver_key + public_key_bytes
            prk = self._hkdf_extract(auth_secret, shared_key)
            key = self._hkdf_expand(prk, b"Content-Encoding: aes128gcm\x00" + context, 16)
            nonce = self._hkdf_expand(prk, b"Content-Encoding: nonce\x00" + context, 12)
            
            # Chiffrer
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, payload.encode(), None)
            
            # Construire le message final
            header = b'\x04' + public_key_bytes
            return header + ciphertext
            
        except Exception as e:
            logger.error(f"Erreur chiffrement Web Push: {e}")
            raise
    
    def _hkdf_extract(self, salt: bytes, ikm: bytes) -> bytes:
        """HKDF Extract"""
        import hmac
        import hashlib
        if len(salt) == 0:
            salt = b'\x00' * hashlib.sha256().digest_size
        return hmac.new(salt, ikm, hashlib.sha256).digest()
    
    def _hkdf_expand(self, prk: bytes, info: bytes, length: int) -> bytes:
        """HKDF Expand"""
        import hmac
        import hashlib
        t = b""
        okm = b""
        counter = 1
        while len(okm) < length:
            t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
            okm += t
            counter += 1
        return okm[:length]
    
    def _generate_vapid_headers(self, endpoint: str) -> Dict[str, str]:
        """Générer les en-têtes VAPID"""
        try:
            # Préparer les claims
            claims = {
                "aud": endpoint,
                "exp": int(time.time()) + 3600,  # Expire dans 1 heure
                "sub": self.vapid_subject
            }
            
            # Signer avec la clé privée VAPID
            token = jwt.encode(claims, self.vapid_private_key, algorithm="ES256")
            
            return {
                "Authorization": f"vapid t={token}, k={self.vapid_public_key}"
            }
            
        except Exception as e:
            logger.error(f"Erreur génération VAPID: {e}")
            raise


class PushNotificationManager:
    """Gestionnaire principal des notifications push"""
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis, config: Dict[str, Any]):
        self.db_pool = db_pool
        self.redis = redis_client
        self.config = config
        self.providers = self._init_providers()
        self.max_batch_size = config.get("max_batch_size", 500)
        
    def _init_providers(self) -> Dict[str, Any]:
        """Initialiser les fournisseurs de push"""
        providers = {}
        
        # Firebase
        if firebase_config := self.config.get("firebase"):
            providers["firebase"] = FirebasePushProvider(
                firebase_config["credentials_path"],
                firebase_config["project_id"]
            )
        
        # Web Push
        if webpush_config := self.config.get("webpush"):
            providers["webpush"] = WebPushProvider(
                webpush_config["vapid_private_key"],
                webpush_config["vapid_public_key"],
                webpush_config["vapid_subject"]
            )
        
        return providers
    
    async def register_device(self, device: PushDevice) -> str:
        """Enregistrer un appareil"""
        try:
            # Vérifier si l'appareil existe déjà
            existing = await self._find_device_by_token(device.token)
            if existing:
                # Mettre à jour
                device.id = existing["id"]
                await self._update_device(device)
            else:
                # Créer nouveau
                await self._create_device(device)
            
            return device.id
            
        except Exception as e:
            logger.error(f"Erreur enregistrement appareil: {e}")
            raise
    
    async def send_notification(self, notification: PushNotification) -> str:
        """Envoyer une notification"""
        try:
            # Sauvegarder la notification
            notification_id = await self._save_notification(notification)
            
            # Récupérer les appareils cibles
            devices = await self._get_target_devices(notification)
            
            if not devices:
                logger.warning(f"Aucun appareil trouvé pour la notification {notification_id}")
                return notification_id
            
            # Programmer l'envoi
            if notification.scheduled_at and notification.scheduled_at > datetime.utcnow():
                await self._schedule_notification(notification, devices)
            else:
                await self._send_to_devices(notification, devices)
            
            return notification_id
            
        except Exception as e:
            logger.error(f"Erreur envoi notification: {e}")
            raise
    
    async def send_bulk_notifications(self, notifications: List[PushNotification]) -> List[str]:
        """Envoyer des notifications en lot"""
        try:
            notification_ids = []
            
            # Traiter par batch
            for i in range(0, len(notifications), self.max_batch_size):
                batch = notifications[i:i + self.max_batch_size]
                
                # Envoyer chaque notification du batch
                batch_tasks = [self.send_notification(notif) for notif in batch]
                batch_ids = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Collecter les IDs valides
                for result in batch_ids:
                    if isinstance(result, str):
                        notification_ids.append(result)
                    else:
                        logger.error(f"Erreur dans le batch: {result}")
            
            return notification_ids
            
        except Exception as e:
            logger.error(f"Erreur envoi bulk: {e}")
            raise
    
    async def _send_to_devices(self, notification: PushNotification, devices: List[Dict[str, Any]]):
        """Envoyer à une liste d'appareils"""
        try:
            # Grouper par plateforme
            platform_groups = {}
            for device in devices:
                platform = PushPlatform(device["platform"])
                if platform not in platform_groups:
                    platform_groups[platform] = []
                platform_groups[platform].append(device)
            
            # Envoyer par plateforme
            for platform, platform_devices in platform_groups.items():
                await self._send_to_platform(notification, platform, platform_devices)
                
        except Exception as e:
            logger.error(f"Erreur envoi appareils: {e}")
    
    async def _send_to_platform(self, notification: PushNotification, platform: PushPlatform, devices: List[Dict[str, Any]]):
        """Envoyer à une plateforme spécifique"""
        try:
            # Sélectionner le bon fournisseur
            provider = None
            if platform in [PushPlatform.ANDROID, PushPlatform.IOS]:
                provider = self.providers.get("firebase")
            elif platform == PushPlatform.WEB:
                provider = self.providers.get("webpush")
            
            if not provider:
                logger.error(f"Aucun fournisseur pour la plateforme {platform}")
                return
            
            # Envoyer à chaque appareil
            for device_data in devices:
                device = PushDevice(
                    id=device_data["id"],
                    user_id=device_data["user_id"],
                    platform=platform,
                    token=device_data["token"],
                    endpoint=device_data.get("endpoint"),
                    p256dh_key=device_data.get("p256dh_key"),
                    auth_key=device_data.get("auth_key")
                )
                
                # Envoyer via le fournisseur
                result = await provider.send_notification(notification, device)
                
                # Enregistrer la livraison
                delivery = PushDelivery(
                    notification_id=notification.id,
                    device_id=device.id,
                    platform=platform,
                    status=PushStatus.SENT if result["success"] else PushStatus.FAILED,
                    provider_message_id=result.get("message_id"),
                    sent_at=datetime.utcnow() if result["success"] else None,
                    failed_at=datetime.utcnow() if not result["success"] else None,
                    failure_reason=result.get("error"),
                    response_data=result
                )
                
                await self._save_delivery(delivery)
                
                # Supprimer l'appareil si nécessaire
                if result.get("should_remove_device"):
                    await self._deactivate_device(device.id)
                    
        except Exception as e:
            logger.error(f"Erreur envoi plateforme {platform}: {e}")
    
    async def _schedule_notification(self, notification: PushNotification, devices: List[Dict[str, Any]]):
        """Programmer une notification"""
        try:
            # Ajouter à la queue Redis
            schedule_data = {
                "notification_id": notification.id,
                "device_ids": [device["id"] for device in devices]
            }
            
            await self.redis.zadd(
                "push:scheduled",
                {json.dumps(schedule_data): notification.scheduled_at.timestamp()}
            )
            
            logger.info(f"Notification {notification.id} programmée pour {notification.scheduled_at}")
            
        except Exception as e:
            logger.error(f"Erreur programmation notification: {e}")
    
    async def process_scheduled_notifications(self):
        """Traiter les notifications programmées"""
        try:
            now = datetime.utcnow().timestamp()
            
            # Récupérer les notifications à envoyer
            scheduled = await self.redis.zrangebyscore(
                "push:scheduled",
                0,
                now,
                withscores=True
            )
            
            for schedule_data, timestamp in scheduled:
                data = json.loads(schedule_data.decode())
                
                # Charger la notification et les appareils
                notification = await self._load_notification(data["notification_id"])
                devices = await self._load_devices(data["device_ids"])
                
                if notification and devices:
                    await self._send_to_devices(notification, devices)
                
                # Supprimer de la queue
                await self.redis.zrem("push:scheduled", schedule_data)
                
        except Exception as e:
            logger.error(f"Erreur traitement notifications programmées: {e}")
    
    async def _get_target_devices(self, notification: PushNotification) -> List[Dict[str, Any]]:
        """Récupérer les appareils cibles"""
        async with self.db_pool.acquire() as conn:
            if notification.device_id:
                # Appareil spécifique
                query = "SELECT * FROM push_devices WHERE id = $1 AND is_active = true"
                rows = await conn.fetch(query, notification.device_id)
            else:
                # Tous les appareils de l'utilisateur
                query = """
                    SELECT * FROM push_devices 
                    WHERE user_id = $1 AND is_active = true
                """
                if notification.platform:
                    query += " AND platform = $2"
                    rows = await conn.fetch(query, notification.user_id, notification.platform.value)
                else:
                    rows = await conn.fetch(query, notification.user_id)
            
            return [dict(row) for row in rows]
    
    async def _save_notification(self, notification: PushNotification) -> str:
        """Sauvegarder une notification"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO push_notifications (
                    id, user_id, device_id, platform, notification_type,
                    title, body, icon, image, badge, sound, priority,
                    ttl, collapse_key, data, actions, scheduled_at,
                    expires_at, click_action, deep_link, tracking_enabled,
                    created_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23)
                RETURNING id
            """
            
            result = await conn.fetchval(
                query,
                notification.id, notification.user_id, notification.device_id,
                notification.platform.value if notification.platform else None,
                notification.notification_type.value, notification.title,
                notification.body, notification.icon, notification.image,
                notification.badge, notification.sound, notification.priority.value,
                notification.ttl, notification.collapse_key, json.dumps(notification.data),
                json.dumps(notification.actions), notification.scheduled_at,
                notification.expires_at, notification.click_action,
                notification.deep_link, notification.tracking_enabled,
                notification.created_at, json.dumps(notification.metadata)
            )
            
            return result
    
    async def _save_delivery(self, delivery: PushDelivery):
        """Sauvegarder une livraison"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO push_deliveries (
                    id, notification_id, device_id, platform, status,
                    provider_message_id, sent_at, delivered_at, clicked_at,
                    dismissed_at, failed_at, failure_reason, retry_count,
                    max_retries, next_retry_at, response_data, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            """
            
            await conn.execute(
                query,
                delivery.id, delivery.notification_id, delivery.device_id,
                delivery.platform.value, delivery.status.value,
                delivery.provider_message_id, delivery.sent_at,
                delivery.delivered_at, delivery.clicked_at, delivery.dismissed_at,
                delivery.failed_at, delivery.failure_reason, delivery.retry_count,
                delivery.max_retries, delivery.next_retry_at,
                json.dumps(delivery.response_data), delivery.created_at
            )
    
    async def _create_device(self, device: PushDevice):
        """Créer un nouvel appareil"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO push_devices (
                    id, user_id, platform, token, endpoint, p256dh_key,
                    auth_key, app_version, os_version, device_model,
                    timezone, language, is_active, last_seen, created_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """
            
            await conn.execute(
                query,
                device.id, device.user_id, device.platform.value, device.token,
                device.endpoint, device.p256dh_key, device.auth_key,
                device.app_version, device.os_version, device.device_model,
                device.timezone, device.language, device.is_active,
                device.last_seen, device.created_at, json.dumps(device.metadata)
            )
    
    async def _update_device(self, device: PushDevice):
        """Mettre à jour un appareil"""
        async with self.db_pool.acquire() as conn:
            query = """
                UPDATE push_devices SET
                    token = $2, endpoint = $3, p256dh_key = $4, auth_key = $5,
                    app_version = $6, os_version = $7, device_model = $8,
                    timezone = $9, language = $10, is_active = $11,
                    last_seen = $12, metadata = $13
                WHERE id = $1
            """
            
            await conn.execute(
                query,
                device.id, device.token, device.endpoint, device.p256dh_key,
                device.auth_key, device.app_version, device.os_version,
                device.device_model, device.timezone, device.language,
                device.is_active, device.last_seen, json.dumps(device.metadata)
            )
    
    async def _find_device_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Trouver un appareil par token"""
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM push_devices WHERE token = $1"
            row = await conn.fetchrow(query, token)
            return dict(row) if row else None
    
    async def _deactivate_device(self, device_id: str):
        """Désactiver un appareil"""
        async with self.db_pool.acquire() as conn:
            query = "UPDATE push_devices SET is_active = false WHERE id = $1"
            await conn.execute(query, device_id)
    
    async def _load_notification(self, notification_id: str) -> Optional[PushNotification]:
        """Charger une notification"""
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM push_notifications WHERE id = $1"
            row = await conn.fetchrow(query, notification_id)
            
            if not row:
                return None
            
            return PushNotification(
                id=row["id"],
                user_id=row["user_id"],
                device_id=row["device_id"],
                platform=PushPlatform(row["platform"]) if row["platform"] else None,
                notification_type=NotificationType(row["notification_type"]),
                title=row["title"],
                body=row["body"],
                icon=row["icon"],
                image=row["image"],
                badge=row["badge"],
                sound=row["sound"],
                priority=PushPriority(row["priority"]),
                ttl=row["ttl"],
                collapse_key=row["collapse_key"],
                data=json.loads(row["data"] or "{}"),
                actions=json.loads(row["actions"] or "[]"),
                scheduled_at=row["scheduled_at"],
                expires_at=row["expires_at"],
                click_action=row["click_action"],
                deep_link=row["deep_link"],
                tracking_enabled=row["tracking_enabled"],
                created_at=row["created_at"],
                metadata=json.loads(row["metadata"] or "{}")
            )
    
    async def _load_devices(self, device_ids: List[str]) -> List[Dict[str, Any]]:
        """Charger plusieurs appareils"""
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM push_devices WHERE id = ANY($1) AND is_active = true"
            rows = await conn.fetch(query, device_ids)
            return [dict(row) for row in rows]
    
    async def get_notification_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Récupérer les analytics de notifications"""
        async with self.db_pool.acquire() as conn:
            # Statistiques générales
            stats_query = """
                SELECT 
                    COUNT(DISTINCT n.id) as total_notifications,
                    COUNT(d.id) as total_deliveries,
                    COUNT(CASE WHEN d.status = 'sent' THEN 1 END) as sent,
                    COUNT(CASE WHEN d.status = 'delivered' THEN 1 END) as delivered,
                    COUNT(CASE WHEN d.status = 'clicked' THEN 1 END) as clicked,
                    COUNT(CASE WHEN d.status = 'failed' THEN 1 END) as failed
                FROM push_notifications n
                LEFT JOIN push_deliveries d ON n.id = d.notification_id
                WHERE n.created_at BETWEEN $1 AND $2
            """
            
            stats = await conn.fetchrow(stats_query, start_date, end_date)
            
            # Statistiques par plateforme
            platform_query = """
                SELECT 
                    d.platform,
                    COUNT(*) as total,
                    COUNT(CASE WHEN d.status = 'sent' THEN 1 END) as sent,
                    COUNT(CASE WHEN d.status = 'clicked' THEN 1 END) as clicked
                FROM push_deliveries d
                JOIN push_notifications n ON d.notification_id = n.id
                WHERE n.created_at BETWEEN $1 AND $2
                GROUP BY d.platform
            """
            
            platform_stats = await conn.fetch(platform_query, start_date, end_date)
            
            # Calculer les taux
            total_deliveries = stats["total_deliveries"] or 1
            delivery_rate = (stats["sent"] / total_deliveries) * 100
            click_rate = (stats["clicked"] / total_deliveries) * 100
            failure_rate = (stats["failed"] / total_deliveries) * 100
            
            return {
                "period": {"start": start_date, "end": end_date},
                "totals": dict(stats),
                "rates": {
                    "delivery_rate": round(delivery_rate, 2),
                    "click_rate": round(click_rate, 2),
                    "failure_rate": round(failure_rate, 2)
                },
                "by_platform": [dict(row) for row in platform_stats]
            }
