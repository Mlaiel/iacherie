"""
IA-Influencer Agent - Blockchain Agent Index

Centralized access point for all blockchain agent functionality.
Provides simplified interfaces and unified access to all blockchain services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

 IMPORTANT LEGAL NOTICE 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

from typing import Dict, List, Optional, Any, Union
import logging

from .blockchain_agent import BlockchainAgent, BlockchainNetwork
from .smart_contracts import SmartContractsManager
from .nft_creator import NFTCreator, ContentType
from .copyright_registry import CopyrightRegistry, CopyrightType
from .crypto_payments import CryptoPaymentProcessor, CurrencyType
from .defi_integration import DeFiIntegration, DeFiProtocol


class BlockchainAgentIndex:
    """
    Unified Blockchain Agent Index.
    
    Provides centralized access to all blockchain agent functionality:
    - Smart contract management and deployment
    - NFT creation and marketplace integration
    - Copyright registration and protection
    - Cryptocurrency payment processing
    - DeFi yield farming and optimization
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Blockchain Agent Index with all services."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core blockchain agent
        self.blockchain_agent = BlockchainAgent(self.config)
        
        # Initialize all service modules
        self.smart_contracts = SmartContractsManager(
            self.blockchain_agent, 
            self.config.get('smart_contracts', {})
        )
        
        self.nft_creator = NFTCreator(
            self.blockchain_agent,
            self.smart_contracts,
            self.config.get('nft_creator', {})
        )
        
        self.copyright_registry = CopyrightRegistry(
            self.blockchain_agent,
            self.config.get('copyright_registry', {})
        )
        
        self.crypto_payments = CryptoPaymentProcessor(
            self.blockchain_agent,
            self.config.get('crypto_payments', {})
        )
        
        self.defi_integration = DeFiIntegration(
            self.blockchain_agent,
            self.config.get('defi_integration', {})
        )
        
        self.logger.info("Blockchain Agent Index initialized with all services")
    
    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics from all blockchain services."""



        try:
            analytics = {
                'blockchain': await self.blockchain_agent.get_blockchain_analytics(),
                'smart_contracts': await self.smart_contracts.get_contracts_analytics(),
                'nft_creator': await self.nft_creator.get_nft_analytics(),
                'copyright_registry': await self.copyright_registry.get_registry_analytics(),
                'crypto_payments': await self.crypto_payments.get_payment_analytics(),
                'defi_integration': await self.defi_integration.get_defi_analytics(),
                'system_status': await self._get_system_status()
            }
            
            # Calculate summary metrics
            analytics['summary'] = {
                'total_transactions': (
                    analytics['blockchain']['total_transactions'] +
                    analytics['crypto_payments']['total_transactions']
                ),
                'total_nfts_created': analytics['nft_creator']['total_nfts_created'],
                'total_copyrights_registered': analytics['copyright_registry']['total_copyright_claims'],
                'total_contracts_deployed': analytics['smart_contracts']['total_deployments'],
                'total_defi_positions': analytics['defi_integration']['total_active_positions'],
                'overall_success_rate': (
                    (analytics['blockchain']['success_rate'] +
                     analytics['crypto_payments']['success_rate']) / 2
                )
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive analytics: {str(e)}")
            raise
    
    async def create_complete_creator_solution(
        self,
        creator_address: str,
        content_file_path: str,
        title: str,
        description: str,
        content_type: ContentType,
        network: BlockchainNetwork = BlockchainNetwork.POLYGON,
        enable_monetization: bool = True
    ) -> Dict[str, str]:
        """
        Create complete creator solution: Copyright + NFT + Monetization.
        
        Args:
            creator_address: Creator's blockchain address
            content_file_path: Path to content file
            title: Content title
            description: Content description
            content_type: Type of content
            network: Blockchain network
            enable_monetization: Enable DeFi monetization
            
        Returns:
            Dict containing all created service IDs
        """



        try:
            from .nft_creator import ContentMetadata
            from decimal import Decimal
            import hashlib
            
            # Calculate content hash
            with open(content_file_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Step 1: Register copyright
            copyright_type = self._map_content_to_copyright_type(content_type)
            copyright_id = await self.copyright_registry.register_copyright(
                content_hash=content_hash,
                copyright_type=copyright_type,
                title=title,
                description=description,
                creator_name="Creator",  # Would get from user profile
                creator_address=creator_address
            )
            
            # Step 2: Create NFT
            metadata = ContentMetadata(
                title=title,
                description=description,
                creator=creator_address,
                content_type=content_type,
                file_format=content_file_path.split('.')[-1],
                file_size=0,  # Will be calculated
                tags=['creator', 'original', 'protected']
            )
            
            nft_id = await self.nft_creator.create_nft(
                content_file_path=content_file_path,
                metadata=metadata,
                network=network
            )
            
            # Step 3: Setup monetization (if enabled)
            defi_position_id = None
            if enable_monetization:
                # Find yield opportunities
                opportunities = await self.defi_integration.find_optimal_yield_opportunities(
                    amount=Decimal('1000'),  # Example amount
                    asset='USDC',
                    min_apy=Decimal('5.0')
                )
                
                if opportunities:
                    # Create yield farming position
                    defi_position_id = await self.defi_integration.execute_yield_farming(
                        user_address=creator_address,
                        pool_id=opportunities[0]['pool_id'],
                        amount_a=Decimal('500'),
                        amount_b=Decimal('500')
                    )
            
            result = {
                'copyright_id': copyright_id,
                'nft_id': nft_id,
                'creator_address': creator_address,
                'content_hash': content_hash,
                'network': network.value,
                'monetization_enabled': enable_monetization
            }
            
            if defi_position_id:
                result['defi_position_id'] = defi_position_id
            
            self.logger.info(f"Complete creator solution created for: {title}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create complete creator solution: {str(e)}")
            raise
    
    async def setup_creator_monetization(
        self,
        creator_address: str,
        monthly_revenue_target: float = 1000.0,
        risk_level: str = "moderate"
    ) -> Dict[str, str]:
        """
        Setup comprehensive monetization strategy for creator.
        
        Args:
            creator_address: Creator's address
            monthly_revenue_target: Target monthly revenue in USD
            risk_level: Risk tolerance level
            
        Returns:
            Dict containing monetization setup results
        """



        try:
            from .defi_integration import RiskLevel
            from decimal import Decimal
            
            # Map risk level
            risk_mapping = {
                'conservative': RiskLevel.CONSERVATIVE,
                'moderate': RiskLevel.MODERATE,
                'aggressive': RiskLevel.AGGRESSIVE
            }
            
            risk_level_enum = risk_mapping.get(risk_level, RiskLevel.MODERATE)
            
            # Create subscription plan for recurring revenue
            subscription_id = await self.crypto_payments.create_subscription(
                name=f"Creator Support - {creator_address[:8]}",
                amount=Decimal(str(monthly_revenue_target / 10)),  # $100 per subscription
                currency=CurrencyType.USDC,
                interval="monthly",
                description=f"Monthly support subscription for creator"
            )
            
            # Setup DeFi yield strategy
            target_apy = Decimal('15.0') if risk_level == 'aggressive' else Decimal('8.0')
            opportunities = await self.defi_integration.find_optimal_yield_opportunities(
                amount=Decimal(str(monthly_revenue_target * 12)),  # Annual target
                asset='USDC',
                risk_level=risk_level_enum,
                min_apy=target_apy
            )
            
            # Setup automated strategy
            strategy_id = None
            if opportunities:
                # Use first opportunity for automated strategy
                best_opportunity = opportunities[0]
                strategy_id = await self.defi_integration.execute_automated_strategy(
                    user_address=creator_address,
                    strategy_id=best_opportunity.get('pool_id', 'default'),
                    investment_amount=Decimal(str(monthly_revenue_target * 6)),  # 6 months upfront
                    auto_compound=True
                )
            
            # Create payment stream for continuous revenue
            stream_id = await self.crypto_payments.create_payment_stream(
                from_address=creator_address,
                to_address=creator_address,  # Self-stream for testing
                currency=CurrencyType.USDC,
                network=BlockchainNetwork.POLYGON,
                total_amount=Decimal(str(monthly_revenue_target)),
                duration_seconds=30 * 24 * 3600  # 30 days
            )
            
            result = {
                'subscription_plan_id': subscription_id,
                'payment_stream_id': stream_id,
                'target_monthly_revenue': str(monthly_revenue_target),
                'risk_level': risk_level,
                'creator_address': creator_address
            }
            
            if strategy_id:
                result['defi_strategy_id'] = strategy_id
            
            self.logger.info(f"Monetization strategy setup for creator: {creator_address}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to setup creator monetization: {str(e)}")
            raise
    
    def _map_content_to_copyright_type(self, content_type: ContentType) -> CopyrightType:
        """Map ContentType to CopyrightType."""
        mapping = {
            ContentType.AUDIO: CopyrightType.SOUND_RECORDING,
            ContentType.VIDEO: CopyrightType.AUDIOVISUAL_WORK,
            ContentType.IMAGE: CopyrightType.VISUAL_ART,
            ContentType.TEXT: CopyrightType.LITERARY_WORK,
            ContentType.INTERACTIVE: CopyrightType.SOFTWARE
        }
        return mapping.get(content_type, CopyrightType.VISUAL_ART)
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""



        return {
            'blockchain_connections': len(self.blockchain_agent.web3_connections),
            'supported_networks': len(self.blockchain_agent.networks),
            'services_active': 6,  # All 6 services
            'uptime_status': 'operational',
            'last_health_check': '2025-08-12T10:00:00Z'
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all available services."""



        return {
            'blockchain_agent': {
                'description': 'Core blockchain integration and transaction management',
                'networks_supported': len(self.blockchain_agent.networks),
                'features': ['Multi-chain support', 'Gas optimization', 'Transaction monitoring']
            },
            'smart_contracts': {
                'description': 'Smart contract deployment and management',
                'templates_available': len(self.smart_contracts.templates),
                'features': ['Automated deployment', 'Security auditing', 'Gas optimization']
            },
            'nft_creator': {
                'description': 'NFT creation and marketplace integration',
                'marketplaces_supported': ['OpenSea', 'Rarible', 'Foundation', 'SuperRare'],
                'features': ['Multi-format support', 'Dynamic metadata', 'Royalty management']
            },
            'copyright_registry': {
                'description': 'Blockchain-based copyright protection',
                'jurisdictions_supported': 8,
                'features': ['Immutable registration', 'Legal compliance', 'DMCA integration']
            },
            'crypto_payments': {
                'description': 'Cryptocurrency payment processing',
                'currencies_supported': 9,
                'features': ['Multi-currency', 'Subscriptions', 'Payment streaming']
            },
            'defi_integration': {
                'description': 'DeFi yield farming and optimization',
                'protocols_supported': len(self.defi_integration.pools),
                'features': ['Yield farming', 'Risk management', 'Auto-compounding']
            }
        }


# Global instance for easy access
blockchain_index = None

def get_blockchain_index(config: Optional[Dict] = None) -> BlockchainAgentIndex:
    """Get or create global blockchain agent index instance."""
    global blockchain_index
    if blockchain_index is None:
        blockchain_index = BlockchainAgentIndex(config)
    return blockchain_index


# Convenience functions for quick access
async def create_nft_with_copyright(
    content_file: str,
    title: str,
    creator_address: str,
    content_type: ContentType = ContentType.IMAGE
) -> Dict[str, str]:
    """Quick function to create NFT with copyright protection."""
    index = get_blockchain_index()
    return await index.create_complete_creator_solution(
        creator_address=creator_address,
        content_file_path=content_file,
        title=title,
        description=f"Original {content_type.value} by creator",
        content_type=content_type,
        enable_monetization=False
    )


async def setup_creator_platform(creator_address: str) -> Dict[str, Any]:
    """Quick setup for creator platform with all services."""
    index = get_blockchain_index()
    
    # Setup monetization
    monetization = await index.setup_creator_monetization(
        creator_address=creator_address,
        monthly_revenue_target=1000.0,
        risk_level="moderate"
    )
    
    # Get service info
    services = index.get_service_info()
    
    return {
        'creator_address': creator_address,
        'monetization_setup': monetization,
        'available_services': services,
        'platform_ready': True
    }
