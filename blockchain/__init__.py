"""
🔗 Blockchain Integration Module - Ainflue Platform
=================================================

Basic blockchain integration for NFT creation, smart contracts,
and cryptocurrency payments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .utils import (
    BlockchainManager,
    CryptocurrencyManager,
    SmartContractManager,
    BlockchainNetwork,
    TokenStandard,
    ContentNFT,
    SmartContract,
    blockchain_manager,
    crypto_manager,
    contract_manager,
    mint_content_nft_simple,
    process_crypto_payment_simple
)

import logging

logger = logging.getLogger(__name__)

# Initialize blockchain services
logger.info("Blockchain integration module initialized")

__version__ = "1.0.0"
__all__ = [
    "BlockchainManager",
    "CryptocurrencyManager",
    "SmartContractManager",
    "BlockchainNetwork",
    "TokenStandard",
    "ContentNFT",
    "SmartContract",
    "blockchain_manager",
    "crypto_manager",
    "contract_manager",
    "mint_content_nft_simple",
    "process_crypto_payment_simple"
]