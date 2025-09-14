"""Advanced Badge Generator - NFT Badge Creation and Management System
===================================================================

Sophisticated NFT badge generation system providing dynamic badge creation,
blockchain integration, rarity algorithms, and comprehensive badge
management for content creators with Web3 integration.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/badge_generator.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + Blockchain + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Badge Generation → NFT Minting → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import random

logger = logging.getLogger(__name__)


class BadgeType(str, Enum):
    """Types of badges."""
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    TIER = "tier"
    SPECIAL_EVENT = "special_event"
    COLLABORATION = "collaboration"
    SKILL = "skill"
    COMMEMORATIVE = "commemorative"
    EXCLUSIVE = "exclusive"


class BadgeRarity(str, Enum):
    """Badge rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class BadgeStatus(str, Enum):
    """Badge status."""
    DRAFT = "draft"
    ACTIVE = "active"
    MINTED = "minted"
    TRANSFERRED = "transferred"
    BURNED = "burned"


class BlockchainNetwork(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    AVALANCHE = "avalanche"
    SOLANA = "solana"


@dataclass
class BadgeMetadata:
    """Badge NFT metadata."""
    name: str
    description: str
    image_url: str
    external_url: Optional[str] = None
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    animation_url: Optional[str] = None
    youtube_url: Optional[str] = None


@dataclass
class BadgeDesign:
    """Badge visual design configuration."""
    template_id: str
    background_color: str
    border_color: str
    text_color: str
    icon_type: str
    shape: str = "circle"  # circle, hexagon, shield, star
    size: Tuple[int, int] = (512, 512)
    effects: List[str] = field(default_factory=list)  # glow, sparkle, gradient
    font_family: str = "Arial"
    custom_elements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BadgeContract:
    """Smart contract configuration for badge."""
    network: BlockchainNetwork
    contract_address: str
    token_standard: str = "ERC721"  # ERC721, ERC1155
    royalty_percentage: float = 0.0
    max_supply: Optional[int] = None
    metadata_frozen: bool = False


@dataclass
class Badge:
    """Complete badge definition."""
    id: str
    name: str
    description: str
    badge_type: BadgeType
    rarity: BadgeRarity
    status: BadgeStatus
    design: BadgeDesign
    metadata: BadgeMetadata
    contract: Optional[BadgeContract] = None
    owner_id: Optional[str] = None
    minted_at: Optional[datetime] = None
    token_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    rarity_score: float = 0.0
    total_supply: int = 1
    current_supply: int = 0
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


@dataclass
class BadgeTemplate:
    """Template for generating badges."""
    id: str
    name: str
    badge_type: BadgeType
    design_template: Dict[str, Any]
    metadata_template: Dict[str, Any]
    rarity_distribution: Dict[BadgeRarity, float]
    unlock_conditions_template: Dict[str, Any]
    variations: List[Dict[str, Any]] = field(default_factory=list)


class BadgeGenerator:
    """
    Advanced NFT badge generation system providing dynamic badge creation,
    blockchain integration, and comprehensive badge management.
    """
    
    def __init__(self, database_connection=None, cache_client=None, blockchain_client=None) -> None:
        """Initialize the badge generator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.blockchain = blockchain_client
        self.badge_templates = self._initialize_badge_templates()
        self.generated_badges: Dict[str, Badge] = {}
        self.user_badges: Dict[str, List[str]] = {}
        self.rarity_multipliers = self._initialize_rarity_multipliers()
        
        self.logger.info("BadgeGenerator initialized")
    
    def _initialize_badge_templates(self) -> Dict[str, BadgeTemplate]:
        """Initialize default badge templates."""
        templates = {}
        
        # Achievement badges
        templates["first_upload"] = BadgeTemplate(
            id="first_upload",
            name="First Upload Badge",
            badge_type=BadgeType.ACHIEVEMENT,
            design_template={
                "background_color": "#4CAF50",
                "border_color": "#388E3C",
                "text_color": "#FFFFFF",
                "icon_type": "upload",
                "shape": "circle",
                "effects": ["glow"]
            },
            metadata_template={
                "name": "First Steps",
                "description": "Awarded for uploading your first piece of content",
                "attributes": [
                    {"trait_type": "Achievement Type", "value": "First Upload"},
                    {"trait_type": "Category", "value": "Content Creation"}
                ]
            },
            rarity_distribution={
                BadgeRarity.COMMON: 1.0
            },
            unlock_conditions_template={
                "metric": "total_uploads",
                "threshold": 1
            }
        )
        
        templates["viral_master"] = BadgeTemplate(
            id="viral_master",
            name="Viral Master Badge",
            badge_type=BadgeType.MILESTONE,
            design_template={
                "background_color": "#FF6B35",
                "border_color": "#E91E63",
                "text_color": "#FFFFFF",
                "icon_type": "fire",
                "shape": "star",
                "effects": ["sparkle", "gradient"]
            },
            metadata_template={
                "name": "Viral Sensation",
                "description": "Achieved viral status with exceptional content",
                "attributes": [
                    {"trait_type": "Milestone", "value": "Viral Content"},
                    {"trait_type": "Rarity", "value": "Epic"}
                ]
            },
            rarity_distribution={
                BadgeRarity.EPIC: 0.8,
                BadgeRarity.LEGENDARY: 0.2
            },
            unlock_conditions_template={
                "metric": "max_content_views",
                "threshold": 1000000
            }
        )
        
        templates["collaboration_champion"] = BadgeTemplate(
            id="collaboration_champion",
            name="Collaboration Champion Badge",
            badge_type=BadgeType.COLLABORATION,
            design_template={
                "background_color": "#9C27B0",
                "border_color": "#7B1FA2",
                "text_color": "#FFFFFF",
                "icon_type": "handshake",
                "shape": "hexagon",
                "effects": ["glow"]
            },
            metadata_template={
                "name": "Team Player",
                "description": "Master of collaboration and teamwork",
                "attributes": [
                    {"trait_type": "Skill", "value": "Collaboration"},
                    {"trait_type": "Team Work", "value": "Expert"}
                ]
            },
            rarity_distribution={
                BadgeRarity.UNCOMMON: 0.6,
                BadgeRarity.RARE: 0.4
            },
            unlock_conditions_template={
                "metric": "successful_collaborations",
                "threshold": 10
            }
        )
        
        templates["tier_legend"] = BadgeTemplate(
            id="tier_legend",
            name="Legend Tier Badge",
            badge_type=BadgeType.TIER,
            design_template={
                "background_color": "#FFD700",
                "border_color": "#FFA000",
                "text_color": "#000000",
                "icon_type": "crown",
                "shape": "shield",
                "effects": ["sparkle", "glow", "gradient"]
            },
            metadata_template={
                "name": "Legend",
                "description": "Reached the prestigious Legend tier",
                "attributes": [
                    {"trait_type": "Tier", "value": "Legend"},
                    {"trait_type": "Prestige", "value": "Maximum"}
                ]
            },
            rarity_distribution={
                BadgeRarity.LEGENDARY: 1.0
            },
            unlock_conditions_template={
                "metric": "user_tier",
                "threshold": "legend"
            }
        )
        
        templates["quality_excellence"] = BadgeTemplate(
            id="quality_excellence",
            name="Quality Excellence Badge",
            badge_type=BadgeType.SKILL,
            design_template={
                "background_color": "#2196F3",
                "border_color": "#1976D2",
                "text_color": "#FFFFFF",
                "icon_type": "diamond",
                "shape": "circle",
                "effects": ["sparkle"]
            },
            metadata_template={
                "name": "Quality Master",
                "description": "Demonstrated exceptional content quality",
                "attributes": [
                    {"trait_type": "Skill", "value": "Quality"},
                    {"trait_type": "Excellence", "value": "Proven"}
                ]
            },
            rarity_distribution={
                BadgeRarity.RARE: 0.7,
                BadgeRarity.EPIC: 0.3
            },
            unlock_conditions_template={
                "metric": "average_quality_score",
                "threshold": 9.0
            }
        )
        
        return templates
    
    def _initialize_rarity_multipliers(self) -> Dict[BadgeRarity, float]:
        """Initialize rarity score multipliers."""
        return {
            BadgeRarity.COMMON: 1.0,
            BadgeRarity.UNCOMMON: 2.0,
            BadgeRarity.RARE: 5.0,
            BadgeRarity.EPIC: 10.0,
            BadgeRarity.LEGENDARY: 25.0,
            BadgeRarity.MYTHIC: 100.0
        }
    
    async def generate_badge_from_template(
        self,
        template_id: str,
        user_id: str,
        trigger_data: Dict[str, Any],
        customizations: Optional[Dict[str, Any]] = None
    ) -> Optional[Badge]:
        """Generate a badge from a template."""
        try:
            if template_id not in self.badge_templates:
                self.logger.error(f"Template not found: {template_id}")
                return None
            
            template = self.badge_templates[template_id]
            customizations = customizations or {}
            
            # Generate badge ID
            badge_id = str(uuid4())
            
            # Determine rarity
            rarity = self._determine_badge_rarity(template, trigger_data)
            
            # Create design
            design = self._create_badge_design(template, rarity, customizations)
            
            # Create metadata
            metadata = self._create_badge_metadata(template, rarity, trigger_data)
            
            # Calculate rarity score
            rarity_score = self._calculate_rarity_score(rarity, trigger_data)
            
            # Create badge
            badge = Badge(
                id=badge_id,
                name=metadata.name,
                description=metadata.description,
                badge_type=template.badge_type,
                rarity=rarity,
                status=BadgeStatus.DRAFT,
                design=design,
                metadata=metadata,
                rarity_score=rarity_score,
                unlock_conditions=template.unlock_conditions_template.copy(),
                created_by="system"
            )
            
            # Generate badge image
            image_data = await self._generate_badge_image(badge)
            if image_data:
                # In a real implementation, would upload to IPFS or cloud storage
                badge.metadata.image_url = f"https://badges.ainflue.com/{badge_id}.png"
            
            # Store badge
            self.generated_badges[badge_id] = badge
            
            self.logger.info(f"✅ Badge generated: {badge.name} ({rarity.value}) for {user_id}")
            
            return badge
            
        except Exception as e:
            self.logger.error(f"Error generating badge from template: {e}")
            return None
    
    def _determine_badge_rarity(
        self,
        template: BadgeTemplate,
        trigger_data: Dict[str, Any]
    ) -> BadgeRarity:
        """Determine badge rarity based on template and trigger data."""
        try:
            # Get base rarity distribution
            rarity_dist = template.rarity_distribution
            
            # Apply bonuses based on trigger data
            bonus_multipliers = {}
            
            # Quality bonus
            quality_score = trigger_data.get("quality_score", 0)
            if quality_score >= 9.5:
                bonus_multipliers[BadgeRarity.LEGENDARY] = 2.0
            elif quality_score >= 9.0:
                bonus_multipliers[BadgeRarity.EPIC] = 1.5
            
            # Performance bonus
            views = trigger_data.get("views", 0)
            if views >= 10000000:  # 10M+ views
                bonus_multipliers[BadgeRarity.MYTHIC] = 1.5
            elif views >= 1000000:  # 1M+ views
                bonus_multipliers[BadgeRarity.LEGENDARY] = 1.3
            
            # Speed bonus (for time-sensitive achievements)
            time_bonus = trigger_data.get("time_bonus", 1.0)
            if time_bonus > 1.5:
                for rarity in [BadgeRarity.EPIC, BadgeRarity.LEGENDARY]:
                    bonus_multipliers[rarity] = bonus_multipliers.get(rarity, 1.0) * 1.2
            
            # Apply bonuses to distribution
            adjusted_dist = {}
            for rarity, probability in rarity_dist.items():
                multiplier = bonus_multipliers.get(rarity, 1.0)
                adjusted_dist[rarity] = probability * multiplier
            
            # Normalize probabilities
            total_prob = sum(adjusted_dist.values())
            if total_prob > 0:
                adjusted_dist = {k: v / total_prob for k, v in adjusted_dist.items()}
            
            # Select rarity based on adjusted distribution
            rand_value = random.random()
            cumulative = 0.0
            
            for rarity, probability in adjusted_dist.items():
                cumulative += probability
                if rand_value <= cumulative:
                    return rarity
            
            # Fallback to first rarity
            return list(rarity_dist.keys())[0]
            
        except Exception as e:
            self.logger.error(f"Error determining badge rarity: {e}")
            return BadgeRarity.COMMON
    
    def _create_badge_design(
        self,
        template: BadgeTemplate,
        rarity: BadgeRarity,
        customizations: Dict[str, Any]
    ) -> BadgeDesign:
        """Create badge design configuration."""
        try:
            design_template = template.design_template.copy()
            
            # Apply rarity-based modifications
            rarity_modifications = {
                BadgeRarity.COMMON: {
                    "effects": ["glow"]
                },
                BadgeRarity.UNCOMMON: {
                    "effects": ["glow", "gradient"]
                },
                BadgeRarity.RARE: {
                    "effects": ["glow", "gradient", "sparkle"]
                },
                BadgeRarity.EPIC: {
                    "effects": ["glow", "gradient", "sparkle", "pulse"]
                },
                BadgeRarity.LEGENDARY: {
                    "effects": ["glow", "gradient", "sparkle", "pulse", "rainbow"]
                },
                BadgeRarity.MYTHIC: {
                    "effects": ["glow", "gradient", "sparkle", "pulse", "rainbow", "cosmic"]
                }
            }
            
            rarity_mods = rarity_modifications.get(rarity, {})
            design_template.update(rarity_mods)
            
            # Apply customizations
            design_template.update(customizations.get("design", {}))
            
            return BadgeDesign(
                template_id=template.id,
                background_color=design_template.get("background_color", "#4CAF50"),
                border_color=design_template.get("border_color", "#388E3C"),
                text_color=design_template.get("text_color", "#FFFFFF"),
                icon_type=design_template.get("icon_type", "star"),
                shape=design_template.get("shape", "circle"),
                size=tuple(design_template.get("size", [512, 512])),
                effects=design_template.get("effects", []),
                font_family=design_template.get("font_family", "Arial"),
                custom_elements=design_template.get("custom_elements", {})
            )
            
        except Exception as e:
            self.logger.error(f"Error creating badge design: {e}")
            return BadgeDesign(
                template_id=template.id,
                background_color="#4CAF50",
                border_color="#388E3C",
                text_color="#FFFFFF",
                icon_type="star"
            )
    
    def _create_badge_metadata(
        self,
        template: BadgeTemplate,
        rarity: BadgeRarity,
        trigger_data: Dict[str, Any]
    ) -> BadgeMetadata:
        """Create badge NFT metadata."""
        try:
            metadata_template = template.metadata_template.copy()
            
            # Build attributes
            attributes = metadata_template.get("attributes", []).copy()
            
            # Add rarity attribute
            attributes.append({
                "trait_type": "Rarity",
                "value": rarity.value.title()
            })
            
            # Add timestamp attribute
            attributes.append({
                "trait_type": "Created",
                "value": datetime.utcnow().isoformat()
            })
            
            # Add trigger-specific attributes
            if "quality_score" in trigger_data:
                attributes.append({
                    "trait_type": "Quality Score",
                    "value": trigger_data["quality_score"]
                })
            
            if "views" in trigger_data:
                attributes.append({
                    "trait_type": "Views at Unlock",
                    "value": trigger_data["views"]
                })
            
            # Create metadata
            return BadgeMetadata(
                name=metadata_template.get("name", "Badge"),
                description=metadata_template.get("description", "Achievement badge"),
                image_url="",  # Will be set after image generation
                attributes=attributes,
                properties={
                    "rarity": rarity.value,
                    "badge_type": template.badge_type.value,
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating badge metadata: {e}")
            return BadgeMetadata(
                name="Badge",
                description="Achievement badge",
                image_url="",
                attributes=[]
            )
    
    def _calculate_rarity_score(
        self,
        rarity: BadgeRarity,
        trigger_data: Dict[str, Any]
    ) -> float:
        """Calculate numerical rarity score."""
        try:
            base_score = self.rarity_multipliers[rarity]
            
            # Apply bonus modifiers
            bonus_score = 0.0
            
            # Quality bonus
            quality_score = trigger_data.get("quality_score", 0)
            if quality_score > 0:
                bonus_score += (quality_score - 5) * 0.1  # Bonus for quality > 5
            
            # Performance bonus
            views = trigger_data.get("views", 0)
            if views > 0:
                import math
                view_bonus = math.log10(views) * 0.5  # Logarithmic view bonus
                bonus_score += view_bonus
            
            # Time bonus
            time_bonus = trigger_data.get("time_bonus", 1.0)
            if time_bonus > 1.0:
                bonus_score += (time_bonus - 1.0) * 0.3
            
            total_score = base_score + bonus_score
            return max(1.0, total_score)  # Minimum score of 1.0
            
        except Exception as e:
            self.logger.error(f"Error calculating rarity score: {e}")
            return 1.0
    
    async def _generate_badge_image(self, badge: Badge) -> Optional[bytes]:
        """Generate badge image based on design."""
        try:
            design = badge.design
            size = design.size
            
            # Create image
            image = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Parse colors
            bg_color = self._hex_to_rgb(design.background_color)
            border_color = self._hex_to_rgb(design.border_color)
            text_color = self._hex_to_rgb(design.text_color)
            
            center = (size[0] // 2, size[1] // 2)
            radius = min(size[0], size[1]) // 2 - 20
            
            # Draw shape
            if design.shape == "circle":
                # Draw background circle
                draw.ellipse([
                    center[0] - radius, center[1] - radius,
                    center[0] + radius, center[1] + radius
                ], fill=bg_color)
                
                # Draw border
                border_width = 8
                draw.ellipse([
                    center[0] - radius, center[1] - radius,
                    center[0] + radius, center[1] + radius
                ], outline=border_color, width=border_width)
            
            elif design.shape == "hexagon":
                # Calculate hexagon points
                import math
                points = []
                for i in range(6):
                    angle = i * math.pi / 3
                    x = center[0] + radius * math.cos(angle)
                    y = center[1] + radius * math.sin(angle)
                    points.append((x, y))
                
                draw.polygon(points, fill=bg_color, outline=border_color, width=8)
            
            elif design.shape == "shield":
                # Shield shape (simplified)
                points = [
                    (center[0], center[1] - radius),
                    (center[0] + radius * 0.8, center[1] - radius * 0.6),
                    (center[0] + radius * 0.8, center[1] + radius * 0.2),
                    (center[0], center[1] + radius),
                    (center[0] - radius * 0.8, center[1] + radius * 0.2),
                    (center[0] - radius * 0.8, center[1] - radius * 0.6)
                ]
                draw.polygon(points, fill=bg_color, outline=border_color, width=8)
            
            elif design.shape == "star":
                # Star shape (simplified 5-point star)
                import math
                outer_radius = radius
                inner_radius = radius * 0.4
                points = []
                
                for i in range(10):
                    angle = i * math.pi / 5
                    if i % 2 == 0:
                        r = outer_radius
                    else:
                        r = inner_radius
                    x = center[0] + r * math.cos(angle - math.pi / 2)
                    y = center[1] + r * math.sin(angle - math.pi / 2)
                    points.append((x, y))
                
                draw.polygon(points, fill=bg_color, outline=border_color, width=6)
            
            # Add icon (simplified - would use actual icon fonts/images)
            icon_text = self._get_icon_text(design.icon_type)
            try:
                # Try to use a larger font size
                font_size = radius // 3
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Get text size for centering
            bbox = draw.textbbox((0, 0), icon_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = center[0] - text_width // 2
            text_y = center[1] - text_height // 2 - radius // 4
            
            draw.text((text_x, text_y), icon_text, fill=text_color, font=font)
            
            # Add badge name
            name_y = center[1] + radius // 3
            name_bbox = draw.textbbox((0, 0), badge.name, font=font)
            name_width = name_bbox[2] - name_bbox[0]
            name_x = center[0] - name_width // 2
            
            draw.text((name_x, name_y), badge.name, fill=text_color, font=font)
            
            # Apply effects (simplified)
            if "glow" in design.effects:
                # Add glow effect (simplified)
                pass
            
            if "sparkle" in design.effects:
                # Add sparkle effect (simplified)
                for _ in range(10):
                    sparkle_x = random.randint(center[0] - radius, center[0] + radius)
                    sparkle_y = random.randint(center[1] - radius, center[1] + radius)
                    draw.ellipse([
                        sparkle_x - 3, sparkle_y - 3,
                        sparkle_x + 3, sparkle_y + 3
                    ], fill=(255, 255, 255, 200))
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error generating badge image: {e}")
            return None
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (76, 175, 80)  # Default green
    
    def _get_icon_text(self, icon_type: str) -> str:
        """Get text representation of icon."""
        icons = {
            "upload": "↑",
            "fire": "🔥",
            "handshake": "🤝",
            "crown": "👑",
            "diamond": "💎",
            "star": "⭐",
            "trophy": "🏆",
            "medal": "🏅",
            "rocket": "🚀",
            "lightning": "⚡"
        }
        return icons.get(icon_type, "⭐")
    
    async def mint_badge_as_nft(
        self,
        badge: Badge,
        owner_id: str,
        network: BlockchainNetwork = BlockchainNetwork.POLYGON
    ) -> bool:
        """Mint badge as NFT on blockchain."""
        try:
            if not self.blockchain:
                self.logger.warning("Blockchain client not available")
                return False
            
            # Create contract configuration
            contract = BadgeContract(
                network=network,
                contract_address="0x...",  # Would be actual contract address
                token_standard="ERC721",
                royalty_percentage=2.5,  # 2.5% royalty
                metadata_frozen=True
            )
            
            # Mint NFT (mock implementation)
            token_id = f"{badge.id}_{int(datetime.utcnow().timestamp())}"
            transaction_hash = f"0x{hashlib.sha256(token_id.encode()).hexdigest()}"
            
            # Update badge
            badge.contract = contract
            badge.owner_id = owner_id
            badge.status = BadgeStatus.MINTED
            badge.minted_at = datetime.utcnow()
            badge.token_id = token_id
            badge.transaction_hash = transaction_hash
            badge.current_supply = 1
            
            # Track user badge
            if owner_id not in self.user_badges:
                self.user_badges[owner_id] = []
            self.user_badges[owner_id].append(badge.id)
            
            self.logger.info(f"✅ Badge minted as NFT: {badge.name} for {owner_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error minting badge as NFT: {e}")
            return False
    
    async def award_badge_to_user(
        self,
        user_id: str,
        trigger_data: Dict[str, Any],
        template_id: Optional[str] = None,
        auto_mint: bool = True
    ) -> Optional[Badge]:
        """Award a badge to a user based on trigger data."""
        try:
            # Determine template if not specified
            if not template_id:
                template_id = self._determine_badge_template(trigger_data)
            
            if not template_id:
                self.logger.warning("No suitable badge template found")
                return None
            
            # Generate badge
            badge = await self.generate_badge_from_template(
                template_id, user_id, trigger_data
            )
            
            if not badge:
                return None
            
            # Mint as NFT if requested
            if auto_mint:
                success = await self.mint_badge_as_nft(badge, user_id)
                if not success:
                    self.logger.warning(f"Failed to mint badge {badge.id}")
            
            self.logger.info(f"🏅 Badge awarded: {badge.name} to {user_id}")
            
            return badge
            
        except Exception as e:
            self.logger.error(f"Error awarding badge to user: {e}")
            return None
    
    def _determine_badge_template(self, trigger_data: Dict[str, Any]) -> Optional[str]:
        """Determine appropriate badge template based on trigger data."""
        try:
            trigger_type = trigger_data.get("trigger_type")
            
            template_mapping = {
                "first_upload": "first_upload",
                "viral_content": "viral_master",
                "collaboration_success": "collaboration_champion",
                "tier_promotion": "tier_legend",
                "quality_milestone": "quality_excellence"
            }
            
            return template_mapping.get(trigger_type)
            
        except Exception as e:
            self.logger.error(f"Error determining badge template: {e}")
            return None
    
    async def get_user_badges(
        self,
        user_id: str,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all badges owned by a user."""
        try:
            if user_id not in self.user_badges:
                return []
            
            user_badge_data = []
            
            for badge_id in self.user_badges[user_id]:
                if badge_id not in self.generated_badges:
                    continue
                
                badge = self.generated_badges[badge_id]
                
                badge_data = {
                    "badge": badge,
                    "owned_since": badge.minted_at,
                    "token_id": badge.token_id,
                    "rarity_score": badge.rarity_score
                }
                
                if include_metadata:
                    badge_data["metadata"] = badge.metadata
                
                user_badge_data.append(badge_data)
            
            # Sort by rarity score (highest first)
            user_badge_data.sort(key=lambda x: x["rarity_score"], reverse=True)
            
            return user_badge_data
            
        except Exception as e:
            self.logger.error(f"Error getting user badges: {e}")
            return []
    
    async def get_badge_analytics(self, badge_id: str) -> Dict[str, Any]:
        """Get analytics for a specific badge."""
        try:
            if badge_id not in self.generated_badges:
                return {}
            
            badge = self.generated_badges[badge_id]
            
            # Count total holders
            total_holders = sum(
                1 for user_badges in self.user_badges.values()
                if badge_id in user_badges
            )
            
            analytics = {
                "badge_id": badge_id,
                "name": badge.name,
                "rarity": badge.rarity.value,
                "rarity_score": badge.rarity_score,
                "total_supply": badge.total_supply,
                "current_supply": badge.current_supply,
                "total_holders": total_holders,
                "minted_at": badge.minted_at,
                "network": badge.contract.network.value if badge.contract else None,
                "transaction_hash": badge.transaction_hash
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting badge analytics: {e}")
            return {}
    
    async def create_badge_collection(
        self,
        collection_name: str,
        badge_ids: List[str],
        collection_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a collection of badges."""
        try:
            collection_id = str(uuid4())
            
            # Validate badge IDs
            valid_badges = [
                bid for bid in badge_ids 
                if bid in self.generated_badges
            ]
            
            collection = {
                "id": collection_id,
                "name": collection_name,
                "badge_ids": valid_badges,
                "metadata": collection_metadata,
                "created_at": datetime.utcnow(),
                "total_badges": len(valid_badges),
                "rarity_distribution": self._calculate_collection_rarity_distribution(valid_badges)
            }
            
            self.logger.info(f"✅ Badge collection created: {collection_name}")
            
            return collection
            
        except Exception as e:
            self.logger.error(f"Error creating badge collection: {e}")
            return {}
    
    def _calculate_collection_rarity_distribution(
        self,
        badge_ids: List[str]
    ) -> Dict[str, int]:
        """Calculate rarity distribution for a badge collection."""
        try:
            distribution = {}
            
            for badge_id in badge_ids:
                if badge_id not in self.generated_badges:
                    continue
                
                badge = self.generated_badges[badge_id]
                rarity = badge.rarity.value
                
                distribution[rarity] = distribution.get(rarity, 0) + 1
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Error calculating collection rarity distribution: {e}")
            return {}


# Global badge generator instance
_badge_generator: Optional[BadgeGenerator] = None


async def get_badge_generator() -> BadgeGenerator:
    """Get global badge generator instance."""
    global _badge_generator
    
    if _badge_generator is None:
        _badge_generator = BadgeGenerator()
    
    return _badge_generator


async def award_badge_to_user(
    user_id: str,
    trigger_data: Dict[str, Any],
    template_id: Optional[str] = None,
    auto_mint: bool = True
) -> Optional[Badge]:
    """Convenience function to award a badge to a user."""
    generator = await get_badge_generator()
    return await generator.award_badge_to_user(user_id, trigger_data, template_id, auto_mint)