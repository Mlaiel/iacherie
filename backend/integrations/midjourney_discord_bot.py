"""
🤖 MIDJOURNEY DISCORD BOT HANDLER
Gère Midjourney via Discord Bot configuré
"""

import os
import discord
from discord.ext import commands
import asyncio
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MidjourneyDiscordBot:
    """
        Gestionnaire Midjourney via Discord"""
    
    def __init__(self):
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.client_id = os.getenv('DISCORD_APPLICATION_ID')
        self.midjourney_channel_id = os.getenv('MIDJOURNEY_CHANNEL_ID')  # À configurer

        
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.setup_handlers()

        
    def setup_handlers(self):
        """
        Configure les event handlers"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'✅ Bot Discord connecté: {self.bot.user}')
            
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
                
            # Log des messages Midjourney
            if message.author.id == 936929561302675456:  # Midjourney Bot ID
                logger.info(f'📨 Message Midjourney reçu: {message.content}')
                
                # Détecte les images générées
                if message.attachments:
                    for attachment in message.attachments:
                        logger.info(f'🖼️ Image générée: {attachment.url}')

                        
            await self.bot.process_commands(message)
    
    async def generate_image(self, prompt: str, wait_for_result: bool = True) -> Optional[Dict]:
        """
        Génère une image via Midjourney
        
        Args:
            prompt: Le prompt de génération
            wait_for_result: Attendre le résultat (sinon retourne immédiatement)

            
        Returns:
            Dict avec url de l'image ou None
        """
        try:
            channel = self.bot.get_channel(int(self.midjourney_channel_id))

            if not channel:
                logger.error('❌ Canal Midjourney non trouvé')

                return None
            
            # Envoie la commande /imagine
            await channel.send(f'/imagine prompt:{prompt}')

            logger.info(f'✅ Commande envoyée: {prompt[:50]}...')

            
            if not wait_for_result:
                return {'status': 'processing', 'prompt': prompt}
            
            # Attendre la réponse (timeout 60s)

            def check(m):
                return (
                    m.channel.id == channel.id and 
                    m.author.id == 936929561302675456 and  # Midjourney Bot
                    len(m.attachments) > 0
                )

            
            try:
                message = await self.bot.wait_for('message', check=check, timeout=60.0)

                
                if message.attachments:
                    image_url = message.attachments[0].url
                    logger.info(f'✅ Image générée: {image_url}')

                    
                    return {
                        'success': True,
                        'image_url': image_url,
                        'prompt': prompt,
                        'message_id': message.id
                    }
                    
            except asyncio.TimeoutError:
                logger.warning('⏰ Timeout en attendant Midjourney')

                return {
                    'success': False,
                    'error': 'Timeout',
                    'message': 'Génération en cours, vérifiez Discord'
                }
                
        except Exception as e:
            logger.error(f'❌ Erreur Midjourney: {str(e)}')

            return {
                'success': False,
                'error': str(e)
            }
    
    async def upscale_image(self, message_id: str, button: int) -> Optional[Dict]:
        """
        Upscale une image Midjourney
        
        Args:
            message_id: ID du message avec l'image
            button: Numéro du bouton (1-4 pour U1-U4)
        """
        try:
            channel = self.bot.get_channel(int(self.midjourney_channel_id))


            message = await channel.fetch_message(int(message_id))
            
            # Clic sur le bouton U{button}
            # Note: Nécessite interaction avec les composants Discord
            logger.info(f'🔍 Upscale demandé: U{button}')

            
            return {
                'status': 'processing',
                'message': f'Upscale U{button} en cours'
            }
            
        except Exception as e:
            logger.error(f'❌ Erreur upscale: {str(e)}')

            return {
                'success': False,
                'error': str(e)
            }
    
    def start(self):
        """
        Démarre le bot Discord"""
        logger.info('🚀 Démarrage bot Discord Midjourney...')
        self.bot.run(self.token)


# Instance globale
midjourney_bot = MidjourneyDiscordBot()


# Fonction FastAPI endpoint
async def generate_midjourney_discord(prompt: str) -> Dict:
    """
    Endpoint pour générer via Midjourney Discord
    
    Usage:
        POST /api/generate/midjourney-discord
        {
            "prompt": "a beautiful sunset over mountains",
            "wait": true
        }
    """
    return await midjourney_bot.generate_image(prompt, wait_for_result=True)


if __name__ == '__main__':
    # Test du bot
    midjourney_bot.start()
