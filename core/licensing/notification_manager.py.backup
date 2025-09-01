"""IA Influencer Agent - License Notification Manager
===============================================

Gestionnaire de notifications avancé pour tous les événements de licensing.
Gère les notifications multi-canal avec personnalisation et tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2024-2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LEGAL STRICT ⚠️
Ce code et tous les concepts associés sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants s'exposent à des poursuites judiciaires.

Contact autorisé: mlaiel@live.de
"""
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types de notifications."""
    LICENSE_CREATED = "license_created"
    LICENSE_APPROVED = "license_approved"
    LICENSE_REJECTED = "license_rejected"
    LICENSE_ACTIVATED = "license_activated"
    LICENSE_SUSPENDED = "license_suspended"
    LICENSE_EXPIRED = "license_expired"
    LICENSE_RENEWED = "license_renewed"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_OVERDUE = "payment_overdue"
    USAGE_DETECTED = "usage_detected"
    USAGE_VIOLATION = "usage_violation"
    COLLABORATION_OPPORTUNITY = "collaboration_opportunity"
    REVENUE_MILESTONE = "revenue_milestone"
    SLA_VIOLATION = "sla_violation"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(Enum):
    """Canaux de notification."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


class NotificationPriority(Enum):
    """Priorités de notification."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(Enum):
    """Statuts de notification."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    RETRYING = "retrying"


class LicenseNotificationManager:
    """
    Gestionnaire de notifications avancé pour l'IA Influencer Agent.
    
    Gère toutes les communications liées au licensing avec support
    multi-canal et règles de personnalisation sophistiquées.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le gestionnaire de notifications.
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.notification_templates = {}
        self.user_preferences = {}
        self.notification_queue = []
        self.sent_notifications = {}
        self.channel_providers = {}
        self.is_initialized = False
        
        logger.info("LicenseNotificationManager initialized")
    
    async def initialize(self):
        """Initialise le gestionnaire de notifications."""
        try:
            await self._load_notification_templates()
            await self._setup_channel_providers()
            await self._start_notification_processor()
            self.is_initialized = True
            logger.info("Notification manager successfully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize notification manager: {str(e)}")
            raise
    
    async def _load_notification_templates(self):
        """Charge les templates de notification."""
        self.notification_templates = {
            NotificationType.LICENSE_CREATED: {
                "subject": {
                    "en": "License Created Successfully",
                    "fr": "Licence Créée avec Succès",
                    "de": "Lizenz Erfolgreich Erstellt"
                },
                "body": {
                    "en": """
                    Hello {creator_name},
                    
                    Your license for "{content_title}" has been created successfully.
                    
                    License Details:
                    - License ID: {license_id}
                    - Type: {license_type}
                    - Status: {status}
                    - Created: {created_date}
                    
                    You can track your license progress in your dashboard.
                    
                    Best regards,
                    IA Influencer Agent Team
                    """,
                    "fr": """
                    Bonjour {creator_name},
                    
                    Votre licence pour "{content_title}" a été créée avec succès.
                    
                    Détails de la licence:
                    - ID Licence: {license_id}
                    - Type: {license_type}
                    - Statut: {status}
                    - Créée le: {created_date}
                    
                    Vous pouvez suivre le progrès de votre licence dans votre tableau de bord.
                    
                    Cordialement,
                    Équipe IA Influencer Agent
                    """,
                    "de": """
                    Hallo {creator_name},
                    
                    Ihre Lizenz für "{content_title}" wurde erfolgreich erstellt.
                    
                    Lizenzdetails:
                    - Lizenz-ID: {license_id}
                    - Typ: {license_type}
                    - Status: {status}
                    - Erstellt: {created_date}
                    
                    Sie können den Fortschritt Ihrer Lizenz in Ihrem Dashboard verfolgen.
                    
                    Mit freundlichen Grüßen,
                    IA Influencer Agent Team
                    """
                },
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                "priority": NotificationPriority.NORMAL
            },
            
            NotificationType.LICENSE_APPROVED: {
                "subject": {
                    "en": "License Approved - Ready to Activate",
                    "fr": "Licence Approuvée - Prête à Activer",
                    "de": "Lizenz Genehmigt - Bereit zur Aktivierung"
                },
                "body": {
                    "en": """
                    Congratulations {creator_name}!
                    
                    Your license for "{content_title}" has been approved and is ready for activation.
                    
                    License Details:
                    - License ID: {license_id}
                    - Approved Date: {approved_date}
                    - Revenue Potential: ${revenue_estimate}
                    
                    Next Steps:
                    1. Complete payment if required
                    2. License will be automatically activated
                    3. Start earning from your content!
                    
                    View License: {license_url}
                    
                    Best regards,
                    IA Influencer Agent Team
                    """,
                    "fr": """
                    Félicitations {creator_name}!
                    
                    Votre licence pour "{content_title}" a été approuvée et est prête pour activation.
                    
                    Détails de la licence:
                    - ID Licence: {license_id}
                    - Date d'approbation: {approved_date}
                    - Potentiel de revenus: ${revenue_estimate}
                    
                    Prochaines étapes:
                    1. Complétez le paiement si requis
                    2. La licence sera automatiquement activée
                    3. Commencez à gagner avec votre contenu!
                    
                    Voir la licence: {license_url}
                    
                    Cordialement,
                    Équipe IA Influencer Agent
                    """,
                    "de": """
                    Herzlichen Glückwunsch {creator_name}!
                    
                    Ihre Lizenz für "{content_title}" wurde genehmigt und ist bereit zur Aktivierung.
                    
                    Lizenzdetails:
                    - Lizenz-ID: {license_id}
                    - Genehmigungsdatum: {approved_date}
                    - Umsatzpotential: ${revenue_estimate}
                    
                    Nächste Schritte:
                    1. Zahlung vervollständigen falls erforderlich
                    2. Lizenz wird automatisch aktiviert
                    3. Beginnen Sie mit Ihrem Content zu verdienen!
                    
                    Lizenz anzeigen: {license_url}
                    
                    Mit freundlichen Grüßen,
                    IA Influencer Agent Team
                    """
                },
                "channels": [NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP],
                "priority": NotificationPriority.HIGH
            },
            
            NotificationType.LICENSE_REJECTED: {
                "subject": {
                    "en": "License Application Requires Attention",
                    "fr": "Demande de Licence Nécessite Attention",
                    "de": "Lizenzantrag Benötigt Aufmerksamkeit"
                },
                "body": {
                    "en": """
                    Hello {creator_name},
                    
                    Your license application for "{content_title}" requires some attention.
                    
                    Reason: {rejection_reason}
                    
                    What you can do:
                    1. Review the feedback provided
                    2. Make necessary adjustments
                    3. Resubmit your application
                    
                    Our team is here to help you succeed. Contact support if you need assistance.
                    
                    Best regards,
                    IA Influencer Agent Team
                    """,
                    "fr": """
                    Bonjour {creator_name},
                    
                    Votre demande de licence pour "{content_title}" nécessite votre attention.
                    
                    Raison: {rejection_reason}
                    
                    Ce que vous pouvez faire:
                    1. Examiner les commentaires fournis
                    2. Effectuer les ajustements nécessaires
                    3. Soumettre à nouveau votre demande
                    
                    Notre équipe est là pour vous aider à réussir. Contactez le support si vous avez besoin d'aide.
                    
                    Cordialement,
                    Équipe IA Influencer Agent
                    """,
                    "de": """
                    Hallo {creator_name},
                    
                    Ihr Lizenzantrag für "{content_title}" benötigt Ihre Aufmerksamkeit.
                    
                    Grund: {rejection_reason}
                    
                    Was Sie tun können:
                    1. Das bereitgestellte Feedback überprüfen
                    2. Notwendige Anpassungen vornehmen
                    3. Ihren Antrag erneut einreichen
                    
                    Unser Team ist hier, um Ihnen zum Erfolg zu verhelfen. Kontaktieren Sie den Support, wenn Sie Hilfe benötigen.
                    
                    Mit freundlichen Grüßen,
                    IA Influencer Agent Team
                    """
                },
                "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
                "priority": NotificationPriority.HIGH
            },
            
            NotificationType.USAGE_VIOLATION: {
                "subject": {
                    "en": "URGENT: License Usage Violation Detected",
                    "fr": "URGENT: Violation d'Usage de Licence Détectée",
                    "de": "DRINGEND: Lizenznutzungsverletzung Erkannt"
                },
                "body": {
                    "en": """
                    URGENT NOTICE - {creator_name}
                    
                    A potential license violation has been detected for your content "{content_title}".
                    
                    Violation Details:
                    - License ID: {license_id}
                    - Violation Type: {violation_type}
                    - Detected: {detection_date}
                    - Platform: {platform}
                    
                    Immediate Action Required:
                    1. Review the violation details
                    2. Contact the violator if possible
                    3. Report to authorities if necessary
                    
                    We're here to protect your rights. Contact our legal team immediately.
                    
                    Legal Support: legal@ia-influencer.com
                    Emergency Line: +1-800-PROTECT
                    
                    IA Influencer Agent Legal Team
                    """,
                    "fr": """
                    AVIS URGENT - {creator_name}
                    
                    Une violation potentielle de licence a été détectée pour votre contenu "{content_title}".
                    
                    Détails de la violation:
                    - ID Licence: {license_id}
                    - Type de violation: {violation_type}
                    - Détectée: {detection_date}
                    - Plateforme: {platform}
                    
                    Action immédiate requise:
                    1. Examiner les détails de la violation
                    2. Contacter le contrevenant si possible
                    3. Signaler aux autorités si nécessaire
                    
                    Nous sommes là pour protéger vos droits. Contactez notre équipe juridique immédiatement.
                    
                    Support Juridique: legal@ia-influencer.com
                    Ligne d'urgence: +1-800-PROTECT
                    
                    Équipe Juridique IA Influencer Agent
                    """,
                    "de": """
                    DRINGENDE MITTEILUNG - {creator_name}
                    
                    Ein potenzieller Lizenzverstoß wurde für Ihren Content "{content_title}" erkannt.
                    
                    Verstoß-Details:
                    - Lizenz-ID: {license_id}
                    - Verstoß-Typ: {violation_type}
                    - Erkannt: {detection_date}
                    - Plattform: {platform}
                    
                    Sofortige Maßnahmen erforderlich:
                    1. Verstoß-Details überprüfen
                    2. Verletzer kontaktieren falls möglich
                    3. Behörden melden falls notwendig
                    
                    Wir sind da, um Ihre Rechte zu schützen. Kontaktieren Sie unser Rechtsteam sofort.
                    
                    Rechtsberatung: legal@ia-influencer.com
                    Notfall-Hotline: +1-800-PROTECT
                    
                    IA Influencer Agent Rechtsteam
                    """
                },
                "channels": [NotificationChannel.EMAIL, NotificationChannel.SMS, 
                           NotificationChannel.PUSH, NotificationChannel.WEBHOOK],
                "priority": NotificationPriority.CRITICAL
            },
            
            NotificationType.REVENUE_MILESTONE: {
                "subject": {
                    "en": "🎉 Revenue Milestone Achieved!",
                    "fr": "🎉 Objectif de Revenus Atteint!",
                    "de": "🎉 Umsatzmeilenstein Erreicht!"
                },
                "body": {
                    "en": """
                    Congratulations {creator_name}! 🎉
                    
                    You've reached a significant revenue milestone with your content!
                    
                    Achievement Details:
                    - Total Revenue: ${total_revenue}
                    - Milestone: ${milestone_amount}
                    - Content: "{content_title}"
                    - Time Period: {period}
                    
                    Your success inspires us! Keep creating amazing content.
                    
                    Share your success: {share_url}
                    
                    Celebrating with you,
                    IA Influencer Agent Team
                    """,
                    "fr": """
                    Félicitations {creator_name}! 🎉
                    
                    Vous avez atteint un objectif significatif de revenus avec votre contenu!
                    
                    Détails de l'accomplissement:
                    - Revenus totaux: ${total_revenue}
                    - Objectif: ${milestone_amount}
                    - Contenu: "{content_title}"
                    - Période: {period}
                    
                    Votre succès nous inspire! Continuez à créer du contenu extraordinaire.
                    
                    Partagez votre succès: {share_url}
                    
                    Nous célébrons avec vous,
                    Équipe IA Influencer Agent
                    """,
                    "de": """
                    Herzlichen Glückwunsch {creator_name}! 🎉
                    
                    Sie haben einen bedeutenden Umsatzmeilenstein mit Ihrem Content erreicht!
                    
                    Erfolgs-Details:
                    - Gesamtumsatz: ${total_revenue}
                    - Meilenstein: ${milestone_amount}
                    - Content: "{content_title}"
                    - Zeitraum: {period}
                    
                    Ihr Erfolg inspiriert uns! Erstellen Sie weiterhin großartigen Content.
                    
                    Teilen Sie Ihren Erfolg: {share_url}
                    
                    Wir feiern mit Ihnen,
                    IA Influencer Agent Team
                    """
                },
                "channels": [NotificationChannel.EMAIL, NotificationChannel.PUSH, 
                           NotificationChannel.IN_APP],
                "priority": NotificationPriority.HIGH
            }
        }
    
    async def _setup_channel_providers(self):
        """Configure les fournisseurs de canaux."""
        self.channel_providers = {
            NotificationChannel.EMAIL: {
                "provider": "smtp",
                "config": self.config.get("email", {}),
                "enabled": True
            },
            NotificationChannel.SMS: {
                "provider": "twilio",
                "config": self.config.get("sms", {}),
                "enabled": True
            },
            NotificationChannel.PUSH: {
                "provider": "firebase",
                "config": self.config.get("push", {}),
                "enabled": True
            },
            NotificationChannel.IN_APP: {
                "provider": "internal",
                "config": {},
                "enabled": True
            },
            NotificationChannel.WEBHOOK: {
                "provider": "http",
                "config": self.config.get("webhook", {}),
                "enabled": True
            },
            NotificationChannel.SLACK: {
                "provider": "slack_api",
                "config": self.config.get("slack", {}),
                "enabled": False
            },
            NotificationChannel.DISCORD: {
                "provider": "discord_api",
                "config": self.config.get("discord", {}),
                "enabled": False
            }
        }
    
    async def _start_notification_processor(self):
        """Démarre le processeur de notifications."""
        asyncio.create_task(self._process_notification_queue())
    
    async def send_notification(self, 
                              notification_type: NotificationType,
                              recipient_id: str,
                              data: Dict[str, Any],
                              channels: List[NotificationChannel] = None,
                              priority: NotificationPriority = None) -> str:
        """
        Envoie une notification.
        
        Args:
            notification_type: Type de notification
            recipient_id: ID du destinataire
            data: Données pour le template
            channels: Canaux spécifiques (optionnel)
            priority: Priorité (optionnel)
            
        Returns:
            str: ID de la notification
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Génération de l'ID de notification
        notification_id = f"NOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{recipient_id[:8]}"
        
        # Récupération du template
        template = self.notification_templates.get(notification_type)
        if not template:
            logger.error(f"Template not found for notification type: {notification_type.value}")
            return None
        
        # Récupération des préférences utilisateur
        user_prefs = await self._get_user_preferences(recipient_id)
        
        # Détermination des canaux
        if not channels:
            channels = await self._determine_channels(notification_type, user_prefs, template)
        
        # Détermination de la priorité
        if not priority:
            priority = template.get("priority", NotificationPriority.NORMAL)
        
        # Création de la notification
        notification = {
            "id": notification_id,
            "type": notification_type.value,
            "recipient_id": recipient_id,
            "data": data,
            "channels": [ch.value for ch in channels],
            "priority": priority.value,
            "status": NotificationStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "scheduled_for": datetime.utcnow().isoformat(),
            "attempts": 0,
            "max_attempts": 3
        }
        
        # Ajout à la queue
        self.notification_queue.append(notification)
        
        logger.info(f"Notification {notification_id} queued for {recipient_id}")
        return notification_id
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les préférences de notification d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant les préférences
        """
        # Ici on récupérerait depuis la base de données
        default_prefs = {
            "language": "en",
            "timezone": "UTC",
            "channels": {
                NotificationChannel.EMAIL.value: True,
                NotificationChannel.PUSH.value: True,
                NotificationChannel.SMS.value: False,
                NotificationChannel.IN_APP.value: True
            },
            "frequency": {
                "marketing": "weekly",
                "updates": "immediate",
                "security": "immediate"
            },
            "quiet_hours": {
                "enabled": True,
                "start": "22:00",
                "end": "08:00"
            }
        }
        
        return self.user_preferences.get(user_id, default_prefs)
    
    async def _determine_channels(self, 
                                notification_type: NotificationType,
                                user_prefs: Dict[str, Any],
                                template: Dict[str, Any]) -> List[NotificationChannel]:
        """
        Détermine les canaux appropriés pour une notification.
        
        Args:
            notification_type: Type de notification
            user_prefs: Préférences utilisateur
            template: Template de notification
            
        Returns:
            Liste des canaux à utiliser
        """
        # Canaux suggérés par le template
        suggested_channels = template.get("channels", [])
        
        # Canaux activés par l'utilisateur
        user_channels = user_prefs.get("channels", {})
        
        # Filtrage selon les préférences
        final_channels = []
        for channel in suggested_channels:
            if isinstance(channel, NotificationChannel):
                channel_name = channel.value
            else:
                channel_name = channel
            
            if user_channels.get(channel_name, True):
                if isinstance(channel, NotificationChannel):
                    final_channels.append(channel)
                else:
                    final_channels.append(NotificationChannel(channel_name))
        
        # Toujours inclure les notifications critiques par email
        priority = template.get("priority", NotificationPriority.NORMAL)
        if priority == NotificationPriority.CRITICAL:
            if NotificationChannel.EMAIL not in final_channels:
                final_channels.append(NotificationChannel.EMAIL)
        
        return final_channels
    
    async def _process_notification_queue(self):
        """Traite la queue de notifications."""
        while True:
            try:
                if self.notification_queue:
                    # Tri par priorité
                    self.notification_queue.sort(
                        key=lambda x: self._get_priority_weight(x["priority"]),
                        reverse=True
                    )
                    
                    # Traitement des notifications
                    notifications_to_process = self.notification_queue[:10]  # Traiter 10 max
                    self.notification_queue = self.notification_queue[10:]
                    
                    for notification in notifications_to_process:
                        await self._process_single_notification(notification)
                
                await asyncio.sleep(5)  # Attendre 5 secondes
                
            except Exception as e:
                logger.error(f"Error processing notification queue: {str(e)}")
                await asyncio.sleep(30)
    
    def _get_priority_weight(self, priority: str) -> int:
        """
        Retourne le poids d'une priorité pour le tri.
        
        Args:
            priority: Priorité
            
        Returns:
            int: Poids de la priorité
        """
        weights = {
            NotificationPriority.CRITICAL.value: 5,
            NotificationPriority.URGENT.value: 4,
            NotificationPriority.HIGH.value: 3,
            NotificationPriority.NORMAL.value: 2,
            NotificationPriority.LOW.value: 1
        }
        return weights.get(priority, 2)
    
    async def _process_single_notification(self, notification: Dict[str, Any]):
        """
        Traite une notification individuelle.
        
        Args:
            notification: Notification à traiter
        """
        notification_id = notification["id"]
        
        try:
            # Vérification des heures silencieuses
            if await self._is_quiet_hours(notification["recipient_id"]):
                if notification["priority"] not in [
                    NotificationPriority.URGENT.value, 
                    NotificationPriority.CRITICAL.value
                ]:
                    # Reporter la notification
                    notification["scheduled_for"] = await self._calculate_next_send_time(
                        notification["recipient_id"]
                    )
                    self.notification_queue.append(notification)
                    return
            
            # Traitement par canal
            success_channels = []
            failed_channels = []
            
            for channel_name in notification["channels"]:
                channel = NotificationChannel(channel_name)
                success = await self._send_via_channel(notification, channel)
                
                if success:
                    success_channels.append(channel_name)
                else:
                    failed_channels.append(channel_name)
            
            # Mise à jour du statut
            if success_channels and not failed_channels:
                notification["status"] = NotificationStatus.SENT.value
            elif success_channels:
                notification["status"] = NotificationStatus.SENT.value
                notification["failed_channels"] = failed_channels
            else:
                notification["status"] = NotificationStatus.FAILED.value
                notification["attempts"] += 1
                
                # Retry si pas dépassé le max
                if notification["attempts"] < notification["max_attempts"]:
                    notification["scheduled_for"] = (
                        datetime.utcnow() + timedelta(minutes=notification["attempts"] * 5)
                    ).isoformat()
                    self.notification_queue.append(notification)
                    return
            
            # Stockage du résultat
            notification["processed_at"] = datetime.utcnow().isoformat()
            notification["success_channels"] = success_channels
            self.sent_notifications[notification_id] = notification
            
            logger.info(f"Notification {notification_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing notification {notification_id}: {str(e)}")
            notification["status"] = NotificationStatus.FAILED.value
            notification["error"] = str(e)
            self.sent_notifications[notification_id] = notification
    
    async def _is_quiet_hours(self, user_id: str) -> bool:
        """
        Vérifie si c'est l'heure silencieuse pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si heures silencieuses
        """
        user_prefs = await self._get_user_preferences(user_id)
        quiet_hours = user_prefs.get("quiet_hours", {})
        
        if not quiet_hours.get("enabled", False):
            return False
        
        # Ici on vérifierait l'heure dans le timezone de l'utilisateur
        # Pour l'instant, retournons False
        return False
    
    async def _calculate_next_send_time(self, user_id: str) -> str:
        """
        Calcule la prochaine heure d'envoi en dehors des heures silencieuses.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            str: Prochaine heure d'envoi en ISO format
        """
        # Ici on calculerait la prochaine heure appropriée
        # Pour l'instant, retournons dans 1 heure
        return (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    async def _send_via_channel(self, 
                              notification: Dict[str, Any],
                              channel: NotificationChannel) -> bool:
        """
        Envoie une notification via un canal spécifique.
        
        Args:
            notification: Notification à envoyer
            channel: Canal d'envoi
            
        Returns:
            bool: True si envoi réussi
        """
        try:
            provider_config = self.channel_providers.get(channel)
            if not provider_config or not provider_config.get("enabled", False):
                logger.warning(f"Channel {channel.value} not available")
                return False
            
            # Préparation du message
            message = await self._prepare_message(notification, channel)
            if not message:
                return False
            
            # Envoi selon le canal
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(notification["recipient_id"], message)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(notification["recipient_id"], message)
            elif channel == NotificationChannel.PUSH:
                return await self._send_push(notification["recipient_id"], message)
            elif channel == NotificationChannel.IN_APP:
                return await self._send_in_app(notification["recipient_id"], message)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification["recipient_id"], message)
            else:
                logger.warning(f"Unsupported channel: {channel.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending via {channel.value}: {str(e)}")
            return False
    
    async def _prepare_message(self, 
                             notification: Dict[str, Any],
                             channel: NotificationChannel) -> Optional[Dict[str, Any]]:
        """
        Prépare le message pour un canal spécifique.
        
        Args:
            notification: Notification
            channel: Canal cible
            
        Returns:
            Dict contenant le message préparé ou None
        """
        notification_type = NotificationType(notification["type"])
        template = self.notification_templates.get(notification_type)
        
        if not template:
            return None
        
        # Récupération de la langue utilisateur
        user_prefs = await self._get_user_preferences(notification["recipient_id"])
        language = user_prefs.get("language", "en")
        
        # Préparation du sujet et du corps
        subject_template = template["subject"].get(language, template["subject"]["en"])
        body_template = template["body"].get(language, template["body"]["en"])
        
        # Remplacement des variables
        subject = subject_template.format(**notification["data"])
        body = body_template.format(**notification["data"])
        
        # Adaptation selon le canal
        if channel == NotificationChannel.SMS:
            # Raccourcir pour SMS
            body = body[:160] + "..." if len(body) > 160 else body
        elif channel == NotificationChannel.PUSH:
            # Format push notification
            body = body[:100] + "..." if len(body) > 100 else body
        
        return {
            "subject": subject,
            "body": body,
            "channel": channel.value,
            "notification_id": notification["id"]
        }
    
    async def _send_email(self, recipient_id: str, message: Dict[str, Any]) -> bool:
        """Envoie un email."""
        # Ici on intégrerait le vrai service email
        logger.info(f"Email sent to {recipient_id}: {message['subject']}")
        return True
    
    async def _send_sms(self, recipient_id: str, message: Dict[str, Any]) -> bool:
        """Envoie un SMS."""
        # Ici on intégrerait le vrai service SMS
        logger.info(f"SMS sent to {recipient_id}: {message['body'][:50]}...")
        return True
    
    async def _send_push(self, recipient_id: str, message: Dict[str, Any]) -> bool:
        """Envoie une notification push."""
        # Ici on intégrerait le vrai service push
        logger.info(f"Push notification sent to {recipient_id}: {message['subject']}")
        return True
    
    async def _send_in_app(self, recipient_id: str, message: Dict[str, Any]) -> bool:
        """Envoie une notification in-app."""
        # Ici on stockerait dans la base pour affichage in-app
        logger.info(f"In-app notification sent to {recipient_id}: {message['subject']}")
        return True
    
    async def _send_webhook(self, recipient_id: str, message: Dict[str, Any]) -> bool:
        """Envoie via webhook."""
        # Ici on ferait l'appel HTTP webhook
        logger.info(f"Webhook notification sent for {recipient_id}")
        return True
    
    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'une notification.
        
        Args:
            notification_id: ID de la notification
            
        Returns:
            Dict contenant le statut ou None
        """
        return self.sent_notifications.get(notification_id)
    
    async def update_user_preferences(self, user_id: str, 
                                    preferences: Dict[str, Any]) -> bool:
        """
        Met à jour les préférences de notification d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            preferences: Nouvelles préférences
            
        Returns:
            bool: True si mise à jour réussie
        """
        try:
            current_prefs = await self._get_user_preferences(user_id)
            current_prefs.update(preferences)
            self.user_preferences[user_id] = current_prefs
            
            logger.info(f"Notification preferences updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences for {user_id}: {str(e)}")
            return False
