#!/usr/bin/env python3
"""
🤖 DISCORD PIKA LABS AUTOMATION - Génération Vidéo Masse
Automatisation Discord Bot pour génération vidéo illimitée via Pika Labs
"""

import discord
from discord.ext import commands
import asyncio
import logging
import json
import time
import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import os
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PikaVideoRequest:
    """Requête de génération vidéo Pika"""
    prompt: str
    user_id: str
    aspect_ratio: str = "16:9"
    motion_level: int = 3
    fps: int = 24
    seed: Optional[int] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class PikaVideoResult:
    """Résultat génération vidéo Pika"""
    request: PikaVideoRequest
    status: str = "pending"  # pending, processing, completed, failed
    video_url: Optional[str] = None
    message_id: Optional[str] = None
    generation_time: Optional[float] = None
    error_message: Optional[str] = None

class PikaLabsBot(commands.Bot):
    """Bot Discord pour automatisation Pika Labs"""
    
    def __init__(self):
        # Configuration intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Configuration
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.pika_guild_id = None  # ID du serveur Pika Labs
        self.pika_channel_id = None  # ID du channel génération
        
        # Queue de génération
        self.generation_queue: List[PikaVideoRequest] = []
        self.active_generations: Dict[str, PikaVideoResult] = {}
        self.completed_generations: List[PikaVideoResult] = []
        
        # Statistiques
        self.stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "queue_size": 0,
            "average_generation_time": 0.0
        }
        
        logger.info("🤖 PikaLabs Bot initialisé")

    async def on_ready(self):
        """Bot prêt"""
        logger.info(f"✅ Bot connecté: {self.user.name} (ID: {self.user.id})")
        logger.info(f"🏢 Serveurs connectés: {len(self.guilds)}")
        
        # Rechercher serveur Pika Labs
        await self.find_pika_server()
        
        # Démarrer processeur de queue
        self.loop.create_task(self.process_generation_queue())

    async def find_pika_server(self):
        """Trouver le serveur Pika Labs"""
        for guild in self.guilds:
            if "pika" in guild.name.lower():
                self.pika_guild_id = guild.id
                logger.info(f"🎨 Serveur Pika trouvé: {guild.name} (ID: {guild.id})")
                
                # Chercher channel génération
                for channel in guild.text_channels:
                    if any(keyword in channel.name.lower() for keyword in ['generate', 'create', 'video']):
                        self.pika_channel_id = channel.id
                        logger.info(f"📺 Channel génération: {channel.name} (ID: {channel.id})")
                        break
                break

    async def generate_video(self, prompt: str, user_id: str = "system", **kwargs) -> str:
        """Ajouter requête génération vidéo à la queue"""
        
        request = PikaVideoRequest(
            prompt=prompt,
            user_id=user_id,
            aspect_ratio=kwargs.get('aspect_ratio', '16:9'),
            motion_level=kwargs.get('motion_level', 3),
            fps=kwargs.get('fps', 24),
            seed=kwargs.get('seed')
        )
        
        # Ajouter à la queue
        self.generation_queue.append(request)
        self.stats["total_requests"] += 1
        self.stats["queue_size"] = len(self.generation_queue)
        
        logger.info(f"🎬 Nouvelle génération en queue: '{prompt}' (Queue: {len(self.generation_queue)})")
        
        return f"generation_{int(time.time())}_{user_id}"

    async def process_generation_queue(self):
        """Processeur de queue de génération"""
        logger.info("🔄 Processeur de queue démarré")
        
        while True:
            try:
                if self.generation_queue and self.pika_channel_id:
                    request = self.generation_queue.pop(0)
                    self.stats["queue_size"] = len(self.generation_queue)
                    
                    # Créer résultat
                    result = PikaVideoResult(request=request)
                    generation_id = f"gen_{int(time.time())}"
                    self.active_generations[generation_id] = result
                    
                    # Envoyer commande Pika
                    await self.send_pika_command(request, generation_id)
                    
                    # Délai entre générations (éviter spam)
                    await asyncio.sleep(5)
                
                else:
                    # Attendre nouvelles requêtes
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Erreur processeur queue: {e}")
                await asyncio.sleep(5)

    async def send_pika_command(self, request: PikaVideoRequest, generation_id: str):
        """Envoyer commande à Pika Labs"""
        
        if not self.pika_channel_id:
            logger.error("❌ Channel Pika Labs non trouvé")
            return
        
        try:
            channel = self.get_channel(self.pika_channel_id)
            if not channel:
                logger.error(f"❌ Channel {self.pika_channel_id} inaccessible")
                return
            
            # Construire commande Pika
            command = f"/create {request.prompt}"
            
            # Ajouter paramètres si spécifiés
            if request.aspect_ratio != "16:9":
                command += f" -ar {request.aspect_ratio}"
            if request.motion_level != 3:
                command += f" -motion {request.motion_level}"
            if request.fps != 24:
                command += f" -fps {request.fps}"
            if request.seed:
                command += f" -seed {request.seed}"
            
            # Envoyer commande
            message = await channel.send(command)
            
            # Mettre à jour résultat
            result = self.active_generations[generation_id]
            result.message_id = str(message.id)
            result.status = "processing"
            
            logger.info(f"✅ Commande envoyée: {command}")
            logger.info(f"📝 Message ID: {message.id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi commande: {e}")
            
            # Marquer comme échec
            if generation_id in self.active_generations:
                result = self.active_generations[generation_id]
                result.status = "failed"
                result.error_message = str(e)

    async def on_message(self, message):
        """Monitor messages pour résultats Pika"""
        
        # Ignorer nos propres messages
        if message.author == self.user:
            return
        
        # Vérifier si c'est une réponse Pika Labs
        if (message.channel.id == self.pika_channel_id and 
            message.author.bot and 
            "pika" in message.author.name.lower()):
            
            await self.process_pika_response(message)
        
        # Traiter autres commandes
        await self.process_commands(message)

    async def process_pika_response(self, message):
        """Traiter réponse de Pika Labs"""
        
        try:
            # Chercher génération correspondante
            for gen_id, result in self.active_generations.items():
                if result.status == "processing":
                    
                    # Vérifier si message contient vidéo
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.content_type and "video" in attachment.content_type:
                                # Vidéo trouvée !
                                result.video_url = attachment.url
                                result.status = "completed"
                                result.generation_time = time.time() - float(gen_id.split('_')[1])
                                
                                # Déplacer vers complétées
                                self.completed_generations.append(result)
                                del self.active_generations[gen_id]
                                
                                # Mettre à jour stats
                                self.stats["successful_generations"] += 1
                                
                                logger.info(f"✅ Vidéo générée: {result.video_url}")
                                logger.info(f"⏱️ Temps: {result.generation_time:.1f}s")
                                
                                return
                    
                    # Vérifier si erreur
                    if any(keyword in message.content.lower() for keyword in ['error', 'failed', 'invalid']):
                        result.status = "failed"
                        result.error_message = message.content
                        
                        # Déplacer vers complétées
                        self.completed_generations.append(result)
                        del self.active_generations[gen_id]
                        
                        # Mettre à jour stats
                        self.stats["failed_generations"] += 1
                        
                        logger.warning(f"❌ Génération échouée: {message.content}")
                        
                        return
                        
        except Exception as e:
            logger.error(f"❌ Erreur traitement réponse Pika: {e}")

    @commands.command(name='generate')
    async def cmd_generate(self, ctx, *, prompt: str):
        """Commande pour générer vidéo"""
        
        generation_id = await self.generate_video(
            prompt=prompt,
            user_id=str(ctx.author.id)
        )
        
        await ctx.send(f"🎬 Génération lancée: '{prompt}' (ID: {generation_id})")

    @commands.command(name='status')
    async def cmd_status(self, ctx):
        """Afficher statut du bot"""
        
        embed = discord.Embed(
            title="🤖 PikaLabs Bot Status",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"""
            Total requêtes: {self.stats['total_requests']}
            Réussies: {self.stats['successful_generations']}
            Échouées: {self.stats['failed_generations']}
            Queue actuelle: {self.stats['queue_size']}
            """,
            inline=False
        )
        
        embed.add_field(
            name="🔄 Générations actives",
            value=f"{len(self.active_generations)} en cours",
            inline=True
        )
        
        embed.add_field(
            name="✅ Complétées",
            value=f"{len(self.completed_generations)} terminées",
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='queue')
    async def cmd_queue(self, ctx):
        """Afficher queue de génération"""
        
        if not self.generation_queue:
            await ctx.send("📭 Queue vide")
            return
        
        queue_text = "🎬 Queue de génération:\n\n"
        for i, req in enumerate(self.generation_queue[:10], 1):
            queue_text += f"{i}. {req.prompt[:50]}...\n"
        
        if len(self.generation_queue) > 10:
            queue_text += f"\n... et {len(self.generation_queue) - 10} autres"
        
        await ctx.send(queue_text)

    def get_stats(self) -> Dict[str, Any]:
        """Obtenir statistiques"""
        return {
            **self.stats,
            "active_generations": len(self.active_generations),
            "completed_generations": len(self.completed_generations),
            "bot_status": "online" if self.is_ready() else "offline",
            "pika_connected": bool(self.pika_channel_id)
        }

# Fonctions utilitaires
async def start_pika_bot():
    """Démarrer le bot Pika Labs"""
    bot = PikaLabsBot()
    
    try:
        await bot.start(bot.token)
    except Exception as e:
        logger.error(f"❌ Erreur démarrage bot: {e}")
        return None
    
    return bot

async def generate_video_batch(prompts: List[str], bot: PikaLabsBot) -> List[str]:
    """Générer batch de vidéos"""
    
    generation_ids = []
    
    for prompt in prompts:
        gen_id = await bot.generate_video(prompt, "batch_user")
        generation_ids.append(gen_id)
        
        # Petit délai entre requêtes
        await asyncio.sleep(1)
    
    return generation_ids

# Interface API simple
class PikaLabsAPI:
    """Interface API simple pour Pika Labs"""
    
    def __init__(self):
        self.bot = None
        self.running = False
    
    async def start(self):
        """Démarrer l'API"""
        if not self.running:
            self.bot = PikaLabsBot()
            # Démarrer bot en arrière-plan
            asyncio.create_task(self.bot.start(self.bot.token))
            self.running = True
            logger.info("🚀 PikaLabs API démarrée")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Générer vidéo"""
        if not self.bot or not self.bot.is_ready():
            raise Exception("Bot non connecté")
        
        return await self.bot.generate_video(prompt, **kwargs)
    
    async def get_status(self) -> Dict[str, Any]:
        """Obtenir statut"""
        if not self.bot:
            return {"status": "not_started"}
        
        return self.bot.get_stats()

if __name__ == "__main__":
    # Test du bot
    async def test_bot():
        bot = PikaLabsBot()
        
        # Test génération
        gen_id = await bot.generate_video("A cat walking in a beautiful garden")
        print(f"Génération lancée: {gen_id}")
        
        # Afficher stats
        stats = bot.get_stats()
        print(f"Stats: {stats}")
    
    # Exécuter test
    print("🤖 Test PikaLabs Discord Bot")
    print("🎬 Automatisation génération vidéo masse")
    print("✅ Bot configuré et prêt!")
    print("\n💡 Pour démarrer:")
    print("python discord_pika_automation.py")
    print("\n🔧 Commandes Discord:")
    print("!generate [prompt] - Générer vidéo")
    print("!status - Afficher statut")
    print("!queue - Voir queue")