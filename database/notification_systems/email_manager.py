"""
Email Notification Manager

Gestionnaire avancé des notifications email pour la plateforme IA Influencer Agent.
Gestion des templates, campagnes, deliverabilité et analytics email.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, ML Engineer, DBA Expert
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
from jinja2 import Template, Environment, FileSystemLoader
import boto3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import aioredis
import asyncpg

logger = logging.getLogger(__name__)


class EmailPriority(Enum):
    """Priorités des emails"""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(Enum):
    """Statuts des emails"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    REJECTED = "rejected"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"


class EmailProvider(Enum):
    """Fournisseurs d'email"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    MAILGUN = "mailgun"


@dataclass
class EmailTemplate:
    """Template d'email"""
    id: str
    name: str
    subject: str
    html_content: str
    text_content: str
    category: str
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailMessage:
    """Message email"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    to_email: str = ""
    to_name: str = ""
    from_email: str = ""
    from_name: str = ""
    subject: str = ""
    html_content: str = ""
    text_content: str = ""
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    priority: EmailPriority = EmailPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    provider: EmailProvider = EmailProvider.SMTP
    tracking_enabled: bool = True
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmailDelivery:
    """Livraison d'email"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_id: str = ""
    provider_message_id: str = ""
    status: EmailStatus = EmailStatus.PENDING
    provider: EmailProvider = EmailProvider.SMTP
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    bounce_reason: Optional[str] = None
    tracking_data: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class EmailDeliverabilityManager:
    """Gestionnaire de délivrabilité email"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.reputation_key = "email:reputation"
        self.bounce_key = "email:bounces"
        self.complaint_key = "email:complaints"
        
    async def check_reputation(self, domain: str) -> Dict[str, Any]:
        """Vérifier la réputation d'un domaine"""



        try:
            # Récupérer les métriques du domaine
            reputation_data = await self.redis.hgetall(f"{self.reputation_key}:{domain}")
            
            if not reputation_data:
                return {
                    "domain": domain,
                    "reputation_score": 100.0,
                    "bounce_rate": 0.0,
                    "complaint_rate": 0.0,
                    "delivery_rate": 100.0,
                    "status": "good"
                }
            
            # Calculer le score de réputation
            bounce_rate = float(reputation_data.get("bounce_rate", 0))
            complaint_rate = float(reputation_data.get("complaint_rate", 0))
            delivery_rate = float(reputation_data.get("delivery_rate", 100))
            
            reputation_score = max(0, 100 - (bounce_rate * 2) - (complaint_rate * 5))
            
            # Déterminer le statut
            if reputation_score >= 80:
                status = "good"
            elif reputation_score >= 60:
                status = "warning"
            else:
                status = "poor"
            
            return {
                "domain": domain,
                "reputation_score": reputation_score,
                "bounce_rate": bounce_rate,
                "complaint_rate": complaint_rate,
                "delivery_rate": delivery_rate,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification réputation {domain}: {e}")
            return {"domain": domain, "status": "unknown", "error": str(e)}
    
    async def update_delivery_stats(self, domain: str, event: str):
        """Mettre à jour les statistiques de livraison"""



        try:
            key = f"{self.reputation_key}:{domain}"
            
            # Incrémenter les compteurs
            await self.redis.hincrby(key, f"{event}_count", 1)
            await self.redis.hincrby(key, "total_sent", 1)
            
            # Calculer les taux
            stats = await self.redis.hgetall(key)
            total_sent = int(stats.get("total_sent", 1))
            
            for metric in ["bounce", "complaint", "delivery"]:
                count = int(stats.get(f"{metric}_count", 0))
                rate = (count / total_sent) * 100
                await self.redis.hset(key, f"{metric}_rate", rate)
            
            # Expiration après 30 jours
            await self.redis.expire(key, 30 * 24 * 3600)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats {domain}: {e}")


class EmailProviderSMTP:
    """Fournisseur SMTP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.use_tls = config.get("use_tls", True)
        self.use_ssl = config.get("use_ssl", False)
    
    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """Envoyer un email via SMTP"""



        try:
            # Créer le message MIME
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{message.from_name} <{message.from_email}>"
            msg['To'] = f"{message.to_name} <{message.to_email}>"
            
            # Ajouter les headers personnalisés
            for header, value in message.headers.items():
                msg[header] = value
            
            # Ajouter le contenu texte
            if message.text_content:
                text_part = MIMEText(message.text_content, 'plain')
                msg.attach(text_part)
            
            # Ajouter le contenu HTML
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html')
                msg.attach(html_part)
            
            # Ajouter les pièces jointes
            for attachment in message.attachments:
                self._add_attachment(msg, attachment)
            
            # Envoyer l'email
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                elif self.use_ssl:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(self.host, self.port, context=context)
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            return {
                "success": True,
                "message_id": message.id,
                "provider_message_id": f"smtp_{message.id}",
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Erreur envoi SMTP: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_id": message.id
            }
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Ajouter une pièce jointe"""



        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Erreur ajout pièce jointe: {e}")


class EmailProviderSendGrid:
    """Fournisseur SendGrid"""
    
    def __init__(self, api_key: str):
        self.client = SendGridAPIClient(api_key)
    
    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """Envoyer un email via SendGrid"""



        try:
            mail = Mail(
                from_email=(message.from_email, message.from_name),
                to_emails=(message.to_email, message.to_name),
                subject=message.subject
            )
            
            if message.text_content:
                mail.content = message.text_content
            
            if message.html_content:
                mail.content = message.html_content
            
            # Ajouter le tracking
            if message.tracking_enabled:
                mail.tracking_settings = {
                    "click_tracking": {"enable": True},
                    "open_tracking": {"enable": True}
                }
            
            # Envoyer
            response = self.client.send(mail)
            
            return {
                "success": True,
                "message_id": message.id,
                "provider_message_id": response.headers.get('X-Message-Id'),
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Erreur envoi SendGrid: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_id": message.id
            }


class EmailTemplateEngine:
    """Moteur de templates email"""
    
    def __init__(self, template_dir: str = "templates/email"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.templates: Dict[str, EmailTemplate] = {}
    
    def register_template(self, template: EmailTemplate):
        """Enregistrer un template"""
        self.templates[template.id] = template
    
    def render_template(self, template_id: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Rendre un template avec les données"""



        try:
            template = self.templates.get(template_id)
            if not template:
                raise ValueError(f"Template {template_id} non trouvé")
            
            # Rendre le sujet
            subject_template = Template(template.subject)
            subject = subject_template.render(**data)
            
            # Rendre le contenu HTML
            html_template = Template(template.html_content)
            html_content = html_template.render(**data)
            
            # Rendre le contenu texte
            text_template = Template(template.text_content)
            text_content = text_template.render(**data)
            
            return {
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content
            }
            
        except Exception as e:
            logger.error(f"Erreur rendu template {template_id}: {e}")
            raise


class EmailManager:
    """Gestionnaire principal des emails"""
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis, config: Dict[str, Any]):
        self.db_pool = db_pool
        self.redis = redis_client
        self.config = config
        self.template_engine = EmailTemplateEngine()
        self.deliverability = EmailDeliverabilityManager(redis_client)
        self.providers = self._init_providers()
        self.default_provider = EmailProvider.SMTP
        
    def _init_providers(self) -> Dict[EmailProvider, Any]:
        """Initialiser les fournisseurs d'email"""
        providers = {}
        
        # SMTP
        if smtp_config := self.config.get("smtp"):
            providers[EmailProvider.SMTP] = EmailProviderSMTP(smtp_config)
        
        # SendGrid
        if sendgrid_key := self.config.get("sendgrid", {}).get("api_key"):
            providers[EmailProvider.SENDGRID] = EmailProviderSendGrid(sendgrid_key)
        
        return providers
    
    async def send_email(self, message: EmailMessage) -> str:
        """Envoyer un email"""



        try:
            # Vérifier la réputation du domaine
            domain = message.to_email.split("@")[1]
            reputation = await self.deliverability.check_reputation(domain)
            
            if reputation["status"] == "poor":
                logger.warning(f"Réputation faible pour {domain}, email en attente")
                message.scheduled_at = datetime.utcnow() + timedelta(hours=1)
            
            # Rendre le template si nécessaire
            if message.template_id:
                rendered = self.template_engine.render_template(
                    message.template_id, 
                    message.template_data
                )
                message.subject = rendered["subject"]
                message.html_content = rendered["html_content"]
                message.text_content = rendered["text_content"]
            
            # Sauvegarder le message
            message_id = await self._save_message(message)
            
            # Envoyer immédiatement ou programmer
            if message.scheduled_at and message.scheduled_at > datetime.utcnow():
                await self._schedule_email(message)
            else:
                await self._send_now(message)
            
            return message_id
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            raise
    
    async def _send_now(self, message: EmailMessage):
        """Envoyer immédiatement un email"""



        try:
            provider = self.providers.get(message.provider, self.providers[self.default_provider])
            result = await provider.send_email(message)
            
            # Créer l'enregistrement de livraison
            delivery = EmailDelivery(
                message_id=message.id,
                provider_message_id=result.get("provider_message_id"),
                status=EmailStatus.SENT if result["success"] else EmailStatus.FAILED,
                provider=message.provider,
                sent_at=datetime.utcnow() if result["success"] else None
            )
            
            await self._save_delivery(delivery)
            
            # Mettre à jour les stats de délivrabilité
            domain = message.to_email.split("@")[1]
            event = "delivery" if result["success"] else "bounce"
            await self.deliverability.update_delivery_stats(domain, event)
            
        except Exception as e:
            logger.error(f"Erreur envoi immédiat: {e}")
            
            # Enregistrer l'échec
            delivery = EmailDelivery(
                message_id=message.id,
                status=EmailStatus.FAILED,
                provider=message.provider
            )
            await self._save_delivery(delivery)
    
    async def _schedule_email(self, message: EmailMessage):
        """Programmer un email"""



        try:
            # Ajouter à la queue Redis avec délai
            delay = (message.scheduled_at - datetime.utcnow()).total_seconds()
            
            await self.redis.zadd(
                "email:scheduled",
                {message.id: message.scheduled_at.timestamp()}
            )
            
            logger.info(f"Email {message.id} programmé pour {message.scheduled_at}")
            
        except Exception as e:
            logger.error(f"Erreur programmation email: {e}")
    
    async def process_scheduled_emails(self):
        """Traiter les emails programmés"""



        try:
            now = datetime.utcnow().timestamp()
            
            # Récupérer les emails à envoyer
            scheduled = await self.redis.zrangebyscore(
                "email:scheduled", 
                0, 
                now, 
                withscores=True
            )
            
            for message_id, timestamp in scheduled:
                # Charger le message
                message = await self._load_message(message_id.decode())
                if message:
                    await self._send_now(message)
                
                # Supprimer de la queue
                await self.redis.zrem("email:scheduled", message_id)
            
        except Exception as e:
            logger.error(f"Erreur traitement emails programmés: {e}")
    
    async def _save_message(self, message: EmailMessage) -> str:
        """Sauvegarder un message en base"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO email_messages (
                    id, to_email, to_name, from_email, from_name,
                    subject, html_content, text_content, template_id,
                    template_data, priority, scheduled_at, provider,
                    tracking_enabled, attachments, headers, metadata,
                    created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                RETURNING id
            """
            
            result = await conn.fetchval(
                query,
                message.id, message.to_email, message.to_name,
                message.from_email, message.from_name, message.subject,
                message.html_content, message.text_content, message.template_id,
                json.dumps(message.template_data), message.priority.value,
                message.scheduled_at, message.provider.value,
                message.tracking_enabled, json.dumps(message.attachments),
                json.dumps(message.headers), json.dumps(message.metadata),
                message.created_at
            )
            
            return result
    
    async def _save_delivery(self, delivery: EmailDelivery):
        """Sauvegarder une livraison en base"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO email_deliveries (
                    id, message_id, provider_message_id, status,
                    provider, sent_at, delivered_at, opened_at,
                    clicked_at, bounced_at, bounce_reason,
                    tracking_data, retry_count, max_retries,
                    next_retry_at, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """
            
            await conn.execute(
                query,
                delivery.id, delivery.message_id, delivery.provider_message_id,
                delivery.status.value, delivery.provider.value, delivery.sent_at,
                delivery.delivered_at, delivery.opened_at, delivery.clicked_at,
                delivery.bounced_at, delivery.bounce_reason,
                json.dumps(delivery.tracking_data), delivery.retry_count,
                delivery.max_retries, delivery.next_retry_at, delivery.created_at
            )
    
    async def _load_message(self, message_id: str) -> Optional[EmailMessage]:
        """Charger un message depuis la base"""
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM email_messages WHERE id = $1"
            row = await conn.fetchrow(query, message_id)
            
            if not row:
                return None
            
            return EmailMessage(
                id=row["id"],
                to_email=row["to_email"],
                to_name=row["to_name"],
                from_email=row["from_email"],
                from_name=row["from_name"],
                subject=row["subject"],
                html_content=row["html_content"],
                text_content=row["text_content"],
                template_id=row["template_id"],
                template_data=json.loads(row["template_data"] or "{}"),
                priority=EmailPriority(row["priority"]),
                scheduled_at=row["scheduled_at"],
                provider=EmailProvider(row["provider"]),
                tracking_enabled=row["tracking_enabled"],
                attachments=json.loads(row["attachments"] or "[]"),
                headers=json.loads(row["headers"] or "{}"),
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"]
            )
    
    async def get_delivery_stats(self, message_id: str) -> Optional[EmailDelivery]:
        """Récupérer les stats de livraison"""
        async with self.db_pool.acquire() as conn:
            query = "SELECT * FROM email_deliveries WHERE message_id = $1"
            row = await conn.fetchrow(query, message_id)
            
            if not row:
                return None
            
            return EmailDelivery(
                id=row["id"],
                message_id=row["message_id"],
                provider_message_id=row["provider_message_id"],
                status=EmailStatus(row["status"]),
                provider=EmailProvider(row["provider"]),
                sent_at=row["sent_at"],
                delivered_at=row["delivered_at"],
                opened_at=row["opened_at"],
                clicked_at=row["clicked_at"],
                bounced_at=row["bounced_at"],
                bounce_reason=row["bounce_reason"],
                tracking_data=json.loads(row["tracking_data"] or "{}"),
                retry_count=row["retry_count"],
                max_retries=row["max_retries"],
                next_retry_at=row["next_retry_at"],
                created_at=row["created_at"]
            )
    
    async def get_email_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Récupérer les analytics email"""
        async with self.db_pool.acquire() as conn:
            # Statistiques générales
            stats_query = """
                SELECT 
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN d.status = 'delivered' THEN 1 END) as delivered,
                    COUNT(CASE WHEN d.status = 'bounced' THEN 1 END) as bounced,
                    COUNT(CASE WHEN d.status = 'opened' THEN 1 END) as opened,
                    COUNT(CASE WHEN d.status = 'clicked' THEN 1 END) as clicked
                FROM email_messages m
                LEFT JOIN email_deliveries d ON m.id = d.message_id
                WHERE m.created_at BETWEEN $1 AND $2
            """
            
            stats = await conn.fetchrow(stats_query, start_date, end_date)
            
            # Taux de conversion
            total_sent = stats["total_sent"] or 1
            delivery_rate = (stats["delivered"] / total_sent) * 100
            bounce_rate = (stats["bounced"] / total_sent) * 100
            open_rate = (stats["opened"] / total_sent) * 100
            click_rate = (stats["clicked"] / total_sent) * 100
            
            return {
                "period": {"start": start_date, "end": end_date},
                "totals": dict(stats),
                "rates": {
                    "delivery_rate": round(delivery_rate, 2),
                    "bounce_rate": round(bounce_rate, 2),
                    "open_rate": round(open_rate, 2),
                    "click_rate": round(click_rate, 2)
                }
            }
