"""Blockchain Rights Repository

Enterprise-grade repository for blockchain-based rights management,
NFT integration, and smart contract automation.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, asc, and_, or_, func, text

from .base_repository import BaseRepository
from ..models.blockchain_rights import (
    BlockchainRights, 
    ViolationReport, 
    LicenseAutomation,
    BlockchainNetwork,
    RightsType,
    SmartContractStatus
)
from ..connections.manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class BlockchainRightsRepository(BaseRepository[BlockchainRights]):
    """
    Enterprise Blockchain Rights Repository
    
    Manages blockchain-based intellectual property rights, NFT integration,
    and automated licensing for content creators.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(BlockchainRights, db_session)
        self.model = BlockchainRights
    
    async def create_blockchain_rights(
        self,
        content_fingerprint_id: str,
        user_id: str,
        blockchain_network: BlockchainNetwork,
        rights_type: RightsType,
        ownership_proof_hash: str,
        **kwargs
    ) -> BlockchainRights:
        """
        Create new blockchain rights registration
        
        Args:
            content_fingerprint_id: Content fingerprint UUID
            user_id: Owner user UUID
            blockchain_network: Target blockchain network
            rights_type: Type of rights being registered
            ownership_proof_hash: Cryptographic proof of ownership
            **kwargs: Additional rights parameters
            
        Returns:
            Created BlockchainRights instance
        """
        try:
            rights_data = {
                "content_fingerprint_id": content_fingerprint_id,
                "user_id": user_id,
                "blockchain_network": blockchain_network,
                "rights_type": rights_type,
                "ownership_proof_hash": ownership_proof_hash,
                "timestamp_proof": datetime.now(timezone.utc),
                "contract_status": SmartContractStatus.PENDING_DEPLOYMENT,
                **kwargs
            }
            
            blockchain_rights = BlockchainRights(**rights_data)
            
            self.db_session.add(blockchain_rights)
            await self.db_session.commit()
            await self.db_session.refresh(blockchain_rights)
            
            logger.info(f"Created blockchain rights: {blockchain_rights.id} for user: {user_id}")
            return blockchain_rights
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create blockchain rights: {str(e)}")
            raise
    
    async def update_smart_contract_status(
        self,
        rights_id: str,
        contract_address: str,
        transaction_hash: str,
        block_number: int,
        gas_used: int,
        status: SmartContractStatus
    ) -> BlockchainRights:
        """
        Update smart contract deployment status
        
        Args:
            rights_id: BlockchainRights UUID
            contract_address: Deployed smart contract address
            transaction_hash: Deployment transaction hash
            block_number: Block number of deployment
            gas_used: Gas consumed for deployment
            status: New contract status
            
        Returns:
            Updated BlockchainRights instance
        """
        try:
            blockchain_rights = await self.get_by_id(rights_id)
            if not blockchain_rights:
                raise ValueError(f"Blockchain rights not found: {rights_id}")
            
            blockchain_rights.smart_contract_address = contract_address
            blockchain_rights.transaction_hash = transaction_hash
            blockchain_rights.block_number = block_number
            blockchain_rights.gas_used = gas_used
            blockchain_rights.contract_status = status
            blockchain_rights.deployed_at = datetime.now(timezone.utc)
            blockchain_rights.total_transactions += 1
            
            await self.db_session.commit()
            
            logger.info(f"Updated smart contract status for rights: {rights_id} to {status.value}")
            return blockchain_rights
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update smart contract status: {str(e)}")
            raise
    
    async def mint_nft(
        self,
        rights_id: str,
        nft_token_id: str,
        metadata_uri: str,
        royalty_percentage: float = 10.0
    ) -> BlockchainRights:
        """
        Record NFT minting for blockchain rights
        
        Args:
            rights_id: BlockchainRights UUID
            nft_token_id: Unique NFT token identifier
            metadata_uri: URI for NFT metadata
            royalty_percentage: Royalty percentage for secondary sales
            
        Returns:
            Updated BlockchainRights instance
        """
        try:
            blockchain_rights = await self.get_by_id(rights_id)
            if not blockchain_rights:
                raise ValueError(f"Blockchain rights not found: {rights_id}")
            
            blockchain_rights.nft_token_id = nft_token_id
            blockchain_rights.nft_metadata_uri = metadata_uri
            blockchain_rights.nft_royalty_percentage = royalty_percentage
            blockchain_rights.is_nft_minted = True
            blockchain_rights.total_transactions += 1
            
            await self.db_session.commit()
            
            logger.info(f"NFT minted for rights: {rights_id} with token ID: {nft_token_id}")
            return blockchain_rights
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to mint NFT: {str(e)}")
            raise
    
    async def get_rights_by_user(
        self,
        user_id: str,
        blockchain_network: Optional[BlockchainNetwork] = None,
        rights_type: Optional[RightsType] = None,
        active_only: bool = True
    ) -> List[BlockchainRights]:
        """
        Get blockchain rights by user with optional filters
        
        Args:
            user_id: User UUID
            blockchain_network: Optional network filter
            rights_type: Optional rights type filter
            active_only: Only return active rights
            
        Returns:
            List of BlockchainRights instances
        """
        try:
            query = self.db_session.query(self.model).filter(
                self.model.user_id == user_id
            )
            
            if blockchain_network:
                query = query.filter(self.model.blockchain_network == blockchain_network)
            
            if rights_type:
                query = query.filter(self.model.rights_type == rights_type)
            
            if active_only:
                query = query.filter(self.model.is_active == True)
            
            rights_list = query.order_by(desc(self.model.created_at)).all()
            
            logger.info(f"Retrieved {len(rights_list)} blockchain rights for user: {user_id}")
            return rights_list
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get rights by user: {str(e)}")
            raise
    
    async def get_rights_by_contract_address(
        self,
        contract_address: str
    ) -> Optional[BlockchainRights]:
        """
        Get blockchain rights by smart contract address
        
        Args:
            contract_address: Smart contract address
            
        Returns:
            BlockchainRights instance or None
        """
        try:
            blockchain_rights = self.db_session.query(self.model).filter(
                self.model.smart_contract_address == contract_address
            ).first()
            
            if blockchain_rights:
                logger.info(f"Found blockchain rights for contract: {contract_address}")
            
            return blockchain_rights
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get rights by contract address: {str(e)}")
            raise
    
    async def record_violation(
        self,
        rights_id: str,
        violation_type: str,
        detected_platform: str,
        infringing_url: str,
        similarity_score: float,
        evidence_hash: str
    ) -> ViolationReport:
        """
        Record a content violation for blockchain rights
        
        Args:
            rights_id: BlockchainRights UUID
            violation_type: Type of violation detected
            detected_platform: Platform where violation was found
            infringing_url: URL of infringing content
            similarity_score: Similarity score of the match
            evidence_hash: Hash of collected evidence
            
        Returns:
            Created ViolationReport instance
        """
        try:
            violation_data = {
                "blockchain_rights_id": rights_id,
                "violation_type": violation_type,
                "detected_platform": detected_platform,
                "infringing_url": infringing_url,
                "similarity_score": similarity_score,
                "evidence_hash": evidence_hash,
                "blockchain_timestamp": datetime.now(timezone.utc)
            }
            
            violation_report = ViolationReport(**violation_data)
            
            self.db_session.add(violation_report)
            
            # Update rights violation count
            blockchain_rights = await self.get_by_id(rights_id)
            if blockchain_rights:
                blockchain_rights.violation_count += 1
                blockchain_rights.last_violation_detected = datetime.now(timezone.utc)
            
            await self.db_session.commit()
            await self.db_session.refresh(violation_report)
            
            logger.info(f"Recorded violation for rights: {rights_id} on platform: {detected_platform}")
            return violation_report
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to record violation: {str(e)}")
            raise
    
    async def create_license_automation(
        self,
        rights_id: str,
        licensee_wallet_address: str,
        usage_type: str,
        proposed_price: Decimal,
        duration_days: int
    ) -> LicenseAutomation:
        """
        Create automated licensing request
        
        Args:
            rights_id: BlockchainRights UUID
            licensee_wallet_address: Wallet address of license requester
            usage_type: Type of usage requested
            proposed_price: Proposed license price
            duration_days: License duration in days
            
        Returns:
            Created LicenseAutomation instance
        """
        try:
            license_data = {
                "blockchain_rights_id": rights_id,
                "licensee_wallet_address": licensee_wallet_address,
                "requested_usage_type": usage_type,
                "proposed_price": proposed_price,
                "license_duration_days": duration_days
            }
            
            license_automation = LicenseAutomation(**license_data)
            
            self.db_session.add(license_automation)
            await self.db_session.commit()
            await self.db_session.refresh(license_automation)
            
            logger.info(f"Created license automation for rights: {rights_id}")
            return license_automation
            
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create license automation: {str(e)}")
            raise
    
    async def get_portfolio_analytics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive portfolio analytics for user's blockchain rights
        
        Args:
            user_id: User UUID
            
        Returns:
            Dictionary containing portfolio analytics
        """
        try:
            # Total rights registered
            total_rights = self.db_session.query(func.count(self.model.id)).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).scalar()
            
            # Rights by network
            network_distribution = self.db_session.query(
                self.model.blockchain_network,
                func.count(self.model.id)
            ).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).group_by(self.model.blockchain_network).all()
            
            # Rights by type
            rights_type_distribution = self.db_session.query(
                self.model.rights_type,
                func.count(self.model.id)
            ).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).group_by(self.model.rights_type).all()
            
            # NFT statistics
            nft_stats = self.db_session.query(
                func.count(self.model.id).label('total_nfts'),
                func.avg(self.model.nft_royalty_percentage).label('avg_royalty')
            ).filter(
                self.model.user_id == user_id,
                self.model.is_nft_minted == True,
                self.model.is_active == True
            ).first()
            
            # Violation statistics
            violation_stats = self.db_session.query(
                func.sum(self.model.violation_count).label('total_violations'),
                func.sum(self.model.damages_recovered).label('total_damages_recovered')
            ).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).first()
            
            # Revenue statistics
            revenue_stats = self.db_session.query(
                func.sum(self.model.network_fees_paid).label('total_fees_paid'),
                func.count(self.model.id).filter(
                    self.model.automatic_licensing_enabled == True
                ).label('automated_licensing_count')
            ).filter(
                self.model.user_id == user_id,
                self.model.is_active == True
            ).first()
            
            analytics = {
                "portfolio_overview": {
                    "total_rights_registered": total_rights or 0,
                    "active_smart_contracts": len([r for r in await self.get_rights_by_user(user_id) if r.contract_status == SmartContractStatus.ACTIVE]),
                    "total_nfts_minted": nft_stats.total_nfts or 0 if nft_stats else 0,
                    "average_nft_royalty": float(nft_stats.avg_royalty or 0) if nft_stats else 0
                },
                "network_distribution": {
                    network.value: count for network, count in network_distribution
                },
                "rights_type_distribution": {
                    rights_type.value: count for rights_type, count in rights_type_distribution
                },
                "protection_metrics": {
                    "total_violations_detected": int(violation_stats.total_violations or 0) if violation_stats else 0,
                    "total_damages_recovered": float(violation_stats.total_damages_recovered or 0) if violation_stats else 0,
                    "automated_licensing_contracts": revenue_stats.automated_licensing_count or 0 if revenue_stats else 0
                },
                "financial_summary": {
                    "total_network_fees_paid": float(revenue_stats.total_fees_paid or 0) if revenue_stats else 0,
                    "estimated_portfolio_value": 0.0,  # To be calculated based on market data
                    "monthly_passive_income": 0.0  # To be calculated from licensing
                }
            }
            
            logger.info(f"Generated portfolio analytics for user: {user_id}")
            return analytics
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get portfolio analytics: {str(e)}")
            raise
    
    async def get_rights_requiring_action(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get blockchain rights that require user attention or action
        
        Args:
            user_id: User UUID
            
        Returns:
            List of rights requiring action with context
        """
        try:
            action_items = []
            
            # Rights with failed deployments
            failed_deployments = self.db_session.query(self.model).filter(
                self.model.user_id == user_id,
                self.model.contract_status == SmartContractStatus.FAILED,
                self.model.is_active == True
            ).all()
            
            for rights in failed_deployments:
                action_items.append({
                    "rights_id": str(rights.id),
                    "action_type": "retry_deployment",
                    "priority": "high",
                    "description": f"Smart contract deployment failed for {rights.rights_type.value} rights",
                    "blockchain_network": rights.blockchain_network.value,
                    "created_at": rights.created_at.isoformat()
                })
            
            # Rights with recent violations
            recent_violations = self.db_session.query(self.model).filter(
                self.model.user_id == user_id,
                self.model.violation_count > 0,
                self.model.last_violation_detected >= datetime.now(timezone.utc) - timedelta(days=7),
                self.model.is_active == True
            ).all()
            
            for rights in recent_violations:
                action_items.append({
                    "rights_id": str(rights.id),
                    "action_type": "review_violations",
                    "priority": "medium",
                    "description": f"{rights.violation_count} violations detected in the last 7 days",
                    "violation_count": rights.violation_count,
                    "last_violation": rights.last_violation_detected.isoformat()
                })
            
            # Rights approaching expiration
            expiring_rights = self.db_session.query(self.model).filter(
                self.model.user_id == user_id,
                self.model.expires_at <= datetime.now(timezone.utc) + timedelta(days=30),
                self.model.expires_at > datetime.now(timezone.utc),
                self.model.is_active == True
            ).all()
            
            for rights in expiring_rights:
                action_items.append({
                    "rights_id": str(rights.id),
                    "action_type": "renew_rights",
                    "priority": "medium",
                    "description": f"Rights expiring in {(rights.expires_at - datetime.now(timezone.utc)).days} days",
                    "expires_at": rights.expires_at.isoformat()
                })
            
            logger.info(f"Found {len(action_items)} action items for user: {user_id}")
            return action_items
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get rights requiring action: {str(e)}")
            raise
