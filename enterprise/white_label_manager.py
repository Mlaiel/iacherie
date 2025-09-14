"""White Label Management System
============================

Advanced white-label customization and multi-tenant branding management system
for enterprise deployments. Provides comprehensive brand isolation, theme
customization, asset management, and domain configuration capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import logging
import json
import uuid
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiofiles
import aiohttp
from PIL import Image, ImageColor
import colorsys
import css_parser
import jinja2
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)


class ThemeType(Enum):
    """
Theme type enumeration"""

    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"


class BrandingStatus(Enum):
    """Branding configuration status"""

    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class AssetType(Enum):
    """Brand asset type enumeration"""

    LOGO = "logo"
    FAVICON = "favicon"
    BACKGROUND = "background"
    BANNER = "banner"
    WATERMARK = "watermark"
    CUSTOM = "custom"


@dataclass
class ColorPalette:
    """Color palette configuration"""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    success: str
    warning: str
    error: str
    info: str
    
    def __post_init__(self) -> None:
        """
Validate color formats"""
        for field_name, color_value in asdict(self).items():
            if not self._is_valid_color(color_value):
                raise ValueError(f"Invalid color format for {field_name}: {color_value}")
    
    def _is_valid_color(self, color: str) -> bool:
        """Validate hex color format"""
        try:
            ImageColor.getcolor(color, "RGB")
            return True
        except ValueError:
            return False
    
    def get_contrasting_text_color(self, background_color: str) -> str:
        """Get contrasting text color for background"""
        try:
            rgb = ImageColor.getcolor(background_color, "RGB")
            luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
            return "#000000" if luminance > 0.5 else "#ffffff"
        except Exception:
            return "#000000"


@dataclass
class Typography:
    """Typography configuration"""
    font_family_primary: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    font_family_secondary: str = "Georgia, serif"
    font_family_mono: str = "Monaco, Consolas, monospace"
    font_size_base: str = "16px"
    font_size_small: str = "14px"
    font_size_large: str = "18px"
    font_size_xlarge: str = "24px"
    font_weight_light: int = 300
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_bold: int = 700
    line_height_base: float = 1.5
    line_height_tight: float = 1.25
    letter_spacing_normal: str = "0"
    letter_spacing_wide: str = "0.025em"


@dataclass
class BrandAsset:
    """Brand asset configuration"""
    asset_id: str
    asset_type: AssetType
    url: str
    alt_text: str
    dimensions: Dict[str, int]
    file_size: int
    mime_type: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_optimized(self) -> bool:
        """
Check if asset is optimized"""
        if self.asset_type == AssetType.LOGO:
            return self.file_size < 50000  # 50KB for logos
        elif self.asset_type == AssetType.BACKGROUND:
            return self.file_size < 500000  # 500KB for backgrounds
        return True


@dataclass
class BrandingTheme:
    """
Complete branding theme configuration"""
    theme_id: str
    tenant_id: str
    theme_name: str
    theme_type: ThemeType
    status: BrandingStatus
    colors: ColorPalette
    typography: Typography
    assets: Dict[str, BrandAsset] = field(default_factory=dict)
    custom_css: str = ""
    custom_javascript: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def generate_css(self) -> str:
        """Generate CSS variables from theme configuration"""
        css_vars = []
        
        # Color variables
        for color_name, color_value in asdict(self.colors).items():
            css_vars.append(f"  --color-{color_name.replace('_', '-')}: {color_value};")
        
        # Typography variables
        for typo_name, typo_value in asdict(self.typography).items():
            if isinstance(typo_value, (str, int, float)):
                css_vars.append(f"  --{typo_name.replace('_', '-')}: {typo_value};")
        
        css_content = ":root {\n" + "\n".join(css_vars) + "\n}"
        
        if self.custom_css:
            css_content += f"\n\n{self.custom_css}"
            
        return css_content


@dataclass
class CustomizationTemplate:
    """Customization template for rapid deployment"""
    template_id: str
    template_name: str
    description: str
    category: str
    theme: BrandingTheme
    preview_url: str
    is_premium: bool = False
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    rating: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WhiteLabelConfiguration:
    """
Complete white-label configuration"""
    tenant_id: str
    organization_name: str
    active_theme: BrandingTheme
    custom_domain: Optional[str] = None
    ssl_certificate: Optional[str] = None
    favicon_url: Optional[str] = None
    contact_info: Dict[str, str] = field(default_factory=dict)
    social_links: Dict[str, str] = field(default_factory=dict)
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None
    support_email: Optional[str] = None
    features_enabled: Set[str] = field(default_factory=set)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_valid_configuration(self) -> Tuple[bool, List[str]]:
        """
Validate white-label configuration"""
        errors = []
        
        if not self.organization_name.strip():
            errors.append("Organization name is required")
            
        if self.custom_domain and not self._is_valid_domain(self.custom_domain):
            errors.append("Invalid custom domain format")
            
        if self.support_email and not self._is_valid_email(self.support_email):
            errors.append("Invalid support email format")
            
        return len(errors) == 0, errors
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None
    
    def _is_valid_email(self, email: str) -> bool:
        """
Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class AssetProcessor:
    """
Advanced asset processing and optimization"""
    
    def __init__(self) -> None:
        try:
            logger.info(f"Executing __init__")
            
            # Initialize supported file extensions
            self.supported_extensions = {
                'image': ['png', 'jpg', 'jpeg', 'svg', 'webp'],
                'icon': ['ico', 'png', 'svg']
            }
            
            logger.info(f"__init__ completed successfully")
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        
    async def process_logo(self, file_data: bytes, output_format: str = 'png') -> Dict[str, Any]:
        """
Process and optimize logo"""
        try:
            # Create different sizes
            sizes = [32, 64, 128, 256, 512]
            processed_assets = {}
            
            with Image.open(io.BytesIO(file_data)) as img:
                # Convert to RGBA for transparency support
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                for size in sizes:
                    resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Save optimized version
                    output_buffer = io.BytesIO()
                    resized_img.save(output_buffer, format=output_format.upper(), optimize=True)
                    
                    processed_assets[f"logo_{size}x{size}"] = {
                        'data': output_buffer.getvalue(),
                        'size': len(output_buffer.getvalue()),
                        'dimensions': {'width': size, 'height': size},
                        'format': output_format
                    }
            
            return processed_assets
            
        except Exception as e:
            logger.error(f"Logo processing failed: {e}")
            raise ValueError(f"Failed to process logo: {str(e)}")
    
    async def optimize_image(self, file_data: bytes, max_size_kb: int = 500) -> bytes:
        """Optimize image file size"""
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                # Progressive optimization
                quality = 95
                while quality > 20:
                    output_buffer = io.BytesIO()
                    img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                    
                    if len(output_buffer.getvalue()) <= max_size_kb * 1024:
                        return output_buffer.getvalue()
                    
                    quality -= 5
                
                # Final fallback
                output_buffer = io.BytesIO()
                img.save(output_buffer, format='JPEG', quality=20, optimize=True)
                return output_buffer.getvalue()
                
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            raise ValueError(f"Failed to optimize image: {str(e)}")


class ThemeGenerator:
    """Intelligent theme generation and color palette creation"""
    
    def __init__(self) -> None:
        self._color_harmony_rules = {
            'monochromatic': self._generate_monochromatic,
            'analogous': self._generate_analogous,
            'complementary': self._generate_complementary,
            'triadic': self._generate_triadic,
            'tetradic': self._generate_tetradic
        }
    
    async def generate_theme_from_color(self, base_color: str, harmony_type: str = 'monochromatic') -> ColorPalette:
        """
Generate complete color palette from base color"""
        try:
            rgb = ImageColor.getcolor(base_color, "RGB")
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            if harmony_type in self._color_harmony_rules:
                colors = self._color_harmony_rules[harmony_type](hsv)
            else:
                colors = self._generate_monochromatic(hsv)
            
            return ColorPalette(
                primary=colors['primary'],
                secondary=colors['secondary'],
                accent=colors['accent'],
                background=colors['background'],
                surface=colors['surface'],
                text_primary=colors['text_primary'],
                text_secondary=colors['text_secondary'],
                success="#10b981",
                warning="#f59e0b",
                error="#ef4444",
                info="#3b82f6"
            )
            
        except Exception as e:
            logger.error(f"Theme generation failed: {e}")
            raise ValueError(f"Failed to generate theme: {str(e)}")
    
    def _generate_monochromatic(self, base_hsv: Tuple[float, float, float]) -> Dict[str, str]:
        """Generate monochromatic color scheme"""
        h, s, v = base_hsv
        
        return {
            'primary': self._hsv_to_hex(h, s, v),
            'secondary': self._hsv_to_hex(h, s * 0.7, v * 0.9),
            'accent': self._hsv_to_hex(h, s * 1.2, min(v * 1.1, 1.0)),
            'background': self._hsv_to_hex(h, s * 0.1, 0.98),
            'surface': self._hsv_to_hex(h, s * 0.05, 1.0),
            'text_primary': "#1a1a1a",
            'text_secondary': "#6b7280"
        }
    
    def _generate_complementary(self, base_hsv: Tuple[float, float, float]) -> Dict[str, str]:
        """Generate complementary color scheme"""
        h, s, v = base_hsv
        comp_h = (h + 0.5) % 1.0
        
        return {
            'primary': self._hsv_to_hex(h, s, v),
            'secondary': self._hsv_to_hex(comp_h, s * 0.8, v * 0.9),
            'accent': self._hsv_to_hex(comp_h, s, v),
            'background': self._hsv_to_hex(h, s * 0.1, 0.98),
            'surface': self._hsv_to_hex(h, s * 0.05, 1.0),
            'text_primary': "#1a1a1a",
            'text_secondary': "#6b7280"
        }
    
    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        """Convert HSV to hex color"""
        rgb = colorsys.hsv_to_rgb(h, min(s, 1.0), min(v, 1.0))
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"


class WhiteLabelManager:
    """Advanced white-label management system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self._configurations: Dict[str, WhiteLabelConfiguration] = {}
        self._themes: Dict[str, BrandingTheme] = {}
        self._templates: Dict[str, CustomizationTemplate] = {}
        self._asset_processor = AssetProcessor()
        self._theme_generator = ThemeGenerator()
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        
        # Initialize default templates
        asyncio.create_task(self._initialize_default_templates())
    
    async def _initialize_default_templates(self) -> None:
        """
Initialize default customization templates"""
        try:
            default_templates = [
                {
                    'template_id': 'corporate_blue',
                    'template_name': 'Corporate Blue',
                    'description': 'Professional blue theme for corporate environments',
                    'category': 'Corporate',
                    'colors': {
                        'primary': '#1e40af',
                        'secondary': '#3b82f6',
                        'accent': '#60a5fa',
                        'background': '#f8fafc',
                        'surface': '#ffffff',
                        'text_primary': '#1e293b',
                        'text_secondary': '#64748b',
                        'success': '#10b981',
                        'warning': '#f59e0b',
                        'error': '#ef4444',
                        'info': '#3b82f6'
                    }
                },
                {
                    'template_id': 'creative_purple',
                    'template_name': 'Creative Purple',
                    'description': 'Vibrant purple theme for creative industries',
                    'category': 'Creative',
                    'colors': {
                        'primary': '#7c3aed',
                        'secondary': '#a855f7',
                        'accent': '#c084fc',
                        'background': '#faf5ff',
                        'surface': '#ffffff',
                        'text_primary': '#1e293b',
                        'text_secondary': '#64748b',
                        'success': '#10b981',
                        'warning': '#f59e0b',
                        'error': '#ef4444',
                        'info': '#3b82f6'
                    }
                }
            ]
            
            for template_data in default_templates:
                colors = ColorPalette(**template_data['colors'])
                typography = Typography()
                
                theme = BrandingTheme(
                    theme_id=f"theme_{template_data['template_id']}",
                    tenant_id="default",
                    theme_name=template_data['template_name'],
                    theme_type=ThemeType.CUSTOM,
                    status=BrandingStatus.ACTIVE,
                    colors=colors,
                    typography=typography
                )
                
                template = CustomizationTemplate(
                    template_id=template_data['template_id'],
                    template_name=template_data['template_name'],
                    description=template_data['description'],
                    category=template_data['category'],
                    theme=theme,
                    preview_url=f"/previews/{template_data['template_id']}.png"
                )
                
                self._templates[template_data['template_id']] = template
                
        except Exception as e:
            logger.error(f"Failed to initialize default templates: {e}")
    
    async def create_tenant_configuration(
        self,
        tenant_id: str,
        organization_name: str,
        template_id: Optional[str] = None
    ) -> WhiteLabelConfiguration:
        """Create new tenant white-label configuration"""
        try:
            # Use template or create default theme
            if template_id and template_id in self._templates:
                template = self._templates[template_id]
                theme = template.theme
                theme.tenant_id = tenant_id
                theme.theme_id = f"theme_{tenant_id}_{uuid.uuid4().hex[:8]}"
            else:
                # Create default theme
                default_colors = await self._theme_generator.generate_theme_from_color("#3b82f6")
                theme = BrandingTheme(
                    theme_id=f"theme_{tenant_id}_{uuid.uuid4().hex[:8]}",
                    tenant_id=tenant_id,
                    theme_name="Default Theme",
                    theme_type=ThemeType.LIGHT,
                    status=BrandingStatus.ACTIVE,
                    colors=default_colors,
                    typography=Typography()
                )
            
            # Create configuration
            configuration = WhiteLabelConfiguration(
                tenant_id=tenant_id,
                organization_name=organization_name,
                active_theme=theme
            )
            
            # Validate configuration
            is_valid, errors = configuration.is_valid_configuration()
            if not is_valid:
                raise ValueError(f"Invalid configuration: {', '.join(errors)}")
            
            # Store configuration
            self._configurations[tenant_id] = configuration
            self._themes[theme.theme_id] = theme
            
            logger.info(f"Created white-label configuration for tenant: {tenant_id}")
            return configuration
            
        except Exception as e:
            logger.error(f"Failed to create tenant configuration: {e}")
            raise
    
    async def update_branding_theme(
        self,
        tenant_id: str,
        theme_updates: Dict[str, Any]
    ) -> BrandingTheme:
        """Update branding theme for tenant"""
        try:
            if tenant_id not in self._configurations:
                raise ValueError(f"Tenant configuration not found: {tenant_id}")
            
            configuration = self._configurations[tenant_id]
            theme = configuration.active_theme
            
            # Update colors if provided
            if 'colors' in theme_updates:
                color_data = theme_updates['colors']
                if isinstance(color_data, dict):
                    # Update individual colors
                    for color_name, color_value in color_data.items():
                        if hasattr(theme.colors, color_name):
                            setattr(theme.colors, color_name, color_value)
                elif isinstance(color_data, ColorPalette):
                    theme.colors = color_data
            
            # Update typography if provided
            if 'typography' in theme_updates:
                typo_data = theme_updates['typography']
                if isinstance(typo_data, dict):
                    for typo_name, typo_value in typo_data.items():
                        if hasattr(theme.typography, typo_name):
                            setattr(theme.typography, typo_name, typo_value)
                elif isinstance(typo_data, Typography):
                    theme.typography = typo_data
            
            # Update custom CSS/JS
            if 'custom_css' in theme_updates:
                theme.custom_css = theme_updates['custom_css']
            
            if 'custom_javascript' in theme_updates:
                theme.custom_javascript = theme_updates['custom_javascript']
            
            # Update metadata
            theme.updated_at = datetime.now(timezone.utc)
            configuration.updated_at = datetime.now(timezone.utc)
            
            # Regenerate CSS
            theme.generate_css()
            
            logger.info(f"Updated branding theme for tenant: {tenant_id}")
            return theme
            
        except Exception as e:
            logger.error(f"Failed to update branding theme: {e}")
            raise
    
    async def upload_brand_asset(
        self,
        tenant_id: str,
        asset_type: AssetType,
        file_data: bytes,
        filename: str,
        alt_text: str = ""
    ) -> BrandAsset:
        """Upload and process brand asset"""
        try:
            if tenant_id not in self._configurations:
                raise ValueError(f"Tenant configuration not found: {tenant_id}")
            
            # Process asset based on type
            if asset_type == AssetType.LOGO:
                processed_assets = await self._asset_processor.process_logo(file_data)
                # Use the largest size as main asset
                main_asset_key = max(processed_assets.keys(), key=lambda k: int(k.split('_')[1].split('x')[0]))
                processed_data = processed_assets[main_asset_key]
            else:
                # Optimize other image types
                processed_data = {
                    'data': await self._asset_processor.optimize_image(file_data),
                    'size': len(file_data),
                    'dimensions': {'width': 0, 'height': 0},  # Would be detected in real implementation
                    'format': filename.split('.')[-1].lower()
                }
            
            # Create asset record
            asset = BrandAsset(
                asset_id=f"asset_{uuid.uuid4().hex}",
                asset_type=asset_type,
                url=f"/assets/{tenant_id}/{asset_type.value}/{filename}",
                alt_text=alt_text or f"{asset_type.value} for {tenant_id}",
                dimensions=processed_data['dimensions'],
                file_size=processed_data['size'],
                mime_type=f"image/{processed_data['format']}"
            )
            
            # Store asset in theme
            configuration = self._configurations[tenant_id]
            theme = configuration.active_theme
            theme.assets[asset_type.value] = asset
            theme.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Uploaded {asset_type.value} asset for tenant: {tenant_id}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to upload brand asset: {e}")
            raise
    
    async def configure_custom_domain(
        self,
        tenant_id: str,
        domain: str,
        ssl_certificate: Optional[str] = None
    ) -> bool:
        """Configure custom domain for tenant"""
        try:
            if tenant_id not in self._configurations:
                raise ValueError(f"Tenant configuration not found: {tenant_id}")
            
            configuration = self._configurations[tenant_id]
            
            # Validate domain
            if not configuration._is_valid_domain(domain):
                raise ValueError(f"Invalid domain format: {domain}")
            
            # Update configuration
            configuration.custom_domain = domain
            configuration.ssl_certificate = ssl_certificate
            configuration.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Configured custom domain {domain} for tenant: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure custom domain: {e}")
            raise
    
    async def get_tenant_configuration(self, tenant_id: str) -> Optional[WhiteLabelConfiguration]:
        """Get tenant white-label configuration"""
        return self._configurations.get(tenant_id)
    
    async def get_available_templates(self) -> List[CustomizationTemplate]:
        """
Get available customization templates"""
        return list(self._templates.values())
    
    async def export_theme_configuration(self, tenant_id: str) -> Dict[str, Any]:
        """
Export theme configuration for backup/migration"""
        try:
            if tenant_id not in self._configurations:
                raise ValueError(f"Tenant configuration not found: {tenant_id}")
            
            configuration = self._configurations[tenant_id]
            
            export_data = {
                'tenant_id': tenant_id,
                'configuration': asdict(configuration),
                'theme': asdict(configuration.active_theme),
                'exported_at': datetime.now(timezone.utc).isoformat(),
                'version': '1.0'
            }
            
            # Encrypt sensitive data
            encrypted_data = self._cipher.encrypt(json.dumps(export_data).encode())
            
            return {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'export_info': {
                    'tenant_id': tenant_id,
                    'exported_at': export_data['exported_at'],
                    'version': export_data['version']
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to export theme configuration: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for white-label manager"""
        try:
            return {
                'status': 'healthy',
                'active_tenants': len(self._configurations),
                'available_templates': len(self._templates),
                'total_themes': len(self._themes),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 1.0
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 0.0
            }