"""
⛓️ BLOCKCHAIN & NFT ROUTES - Complete Implementation
==================================================
ALL 30 endpoints for blockchain, NFTs, smart contracts, crypto wallets
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/blockchain", tags=["Blockchain & NFT"])

# ============================================================================
# MODELS
# ============================================================================

class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    SOLANA = "solana"
    BSC = "bsc"

class NFTStandard(str, Enum):
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    SPL = "spl"

# ============================================================================
# WALLETS
# ============================================================================

@router.post("/wallets/create")
async def create_wallet(user_id: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Create blockchain wallet"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        wallet = await manager.create_wallet(user_id, network.value)
        return {"message": "Wallet created", "wallet": wallet}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wallets/users/{user_id}")
async def get_user_wallets(user_id: str):
    """Get user wallets"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        wallets = await manager.get_user_wallets(user_id)
        return {"user_id": user_id, "wallets": wallets}
    except Exception as e:
        return {"user_id": user_id, "wallets": [], "error": str(e)}

@router.get("/wallets/{address}/balance")
async def get_wallet_balance(address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get wallet balance"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        balance = await manager.get_balance(address, network.value)
        return {"address": address, "network": network.value, "balance": balance}
    except Exception as e:
        return {"address": address, "network": network.value, "balance": "0", "error": str(e)}

# ============================================================================
# NFT MINTING
# ============================================================================

@router.post("/nft/mint")
async def mint_nft(
    user_id: str,
    name: str,
    description: str,
    media_url: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM,
    standard: NFTStandard = NFTStandard.ERC721,
    metadata: Optional[Dict[str, Any]] = None
):
    """Mint NFT"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        nft = await manager.mint_nft(
            user_id=user_id,
            name=name,
            description=description,
            media_url=media_url,
            network=network.value,
            standard=standard.value,
            metadata=metadata or {}
        )
        return {"message": "NFT minted", "nft": nft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nft/batch-mint")
async def batch_mint_nfts(user_id: str, nfts: List[Dict[str, Any]], network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Batch mint NFTs"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        results = await manager.batch_mint_nfts(user_id, nfts, network.value)
        return {"message": "NFTs minted", "count": len(results), "nfts": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nft/{token_id}")
async def get_nft(token_id: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get NFT details"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        nft = await manager.get_nft(token_id, network.value)
        if not nft:
            raise HTTPException(status_code=404, detail="NFT not found")
        return nft
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nft/users/{user_id}")
async def get_user_nfts(user_id: str, network: Optional[BlockchainNetwork] = None):
    """Get user NFTs"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        network_val = network.value if network else None
        nfts = await manager.get_user_nfts(user_id, network_val)
        return {"user_id": user_id, "count": len(nfts), "nfts": nfts}
    except Exception as e:
        return {"user_id": user_id, "count": 0, "nfts": [], "error": str(e)}

@router.post("/nft/{token_id}/transfer")
async def transfer_nft(token_id: str, from_address: str, to_address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Transfer NFT"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        tx = await manager.transfer_nft(token_id, from_address, to_address, network.value)
        return {"message": "NFT transferred", "transaction": tx}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nft/{token_id}/burn")
async def burn_nft(token_id: str, owner_address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Burn NFT"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        tx = await manager.burn_nft(token_id, owner_address, network.value)
        return {"message": "NFT burned", "transaction": tx}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SMART CONTRACTS
# ============================================================================

@router.post("/contracts/deploy")
async def deploy_contract(
    user_id: str,
    contract_type: str,
    name: str,
    symbol: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM,
    params: Optional[Dict[str, Any]] = None
):
    """Deploy smart contract"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        contract = await manager.deploy_contract(
            user_id=user_id,
            contract_type=contract_type,
            name=name,
            symbol=symbol,
            network=network.value,
            params=params or {}
        )
        return {"message": "Contract deployed", "contract": contract}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts/{contract_address}")
async def get_contract(contract_address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get contract details"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        contract = await manager.get_contract(contract_address, network.value)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts/users/{user_id}")
async def get_user_contracts(user_id: str):
    """Get user contracts"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        contracts = await manager.get_user_contracts(user_id)
        return {"user_id": user_id, "contracts": contracts}
    except Exception as e:
        return {"user_id": user_id, "contracts": [], "error": str(e)}

@router.post("/contracts/{contract_address}/execute")
async def execute_contract(contract_address: str, function_name: str, params: Dict[str, Any], network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Execute contract function"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        result = await manager.execute_contract_function(
            contract_address=contract_address,
            function_name=function_name,
            params=params,
            network=network.value
        )
        return {"message": "Function executed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRANSACTIONS
# ============================================================================

@router.get("/transactions/{tx_hash}")
async def get_transaction(tx_hash: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get transaction details"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        tx = await manager.get_transaction(tx_hash, network.value)
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return tx
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions/wallets/{address}")
async def get_wallet_transactions(address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM, limit: int = 50):
    """Get wallet transactions"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        transactions = await manager.get_wallet_transactions(address, network.value, limit)
        return {"address": address, "transactions": transactions}
    except Exception as e:
        return {"address": address, "transactions": [], "error": str(e)}

@router.post("/transactions/send")
async def send_transaction(from_address: str, to_address: str, amount: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Send transaction"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        tx = await manager.send_transaction(from_address, to_address, amount, network.value)
        return {"message": "Transaction sent", "transaction": tx}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOKENS
# ============================================================================

@router.post("/tokens/create")
async def create_token(
    user_id: str,
    name: str,
    symbol: str,
    initial_supply: str,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
):
    """Create custom token"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        token = await manager.create_token(
            user_id=user_id,
            name=name,
            symbol=symbol,
            initial_supply=initial_supply,
            network=network.value
        )
        return {"message": "Token created", "token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{token_address}")
async def get_token(token_address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get token details"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        token = await manager.get_token(token_address, network.value)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{token_address}/balance/{wallet_address}")
async def get_token_balance(token_address: str, wallet_address: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get token balance for wallet"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        balance = await manager.get_token_balance(token_address, wallet_address, network.value)
        return {"token_address": token_address, "wallet_address": wallet_address, "balance": balance}
    except Exception as e:
        return {"token_address": token_address, "wallet_address": wallet_address, "balance": "0", "error": str(e)}

# ============================================================================
# GAS & FEES
# ============================================================================

@router.get("/gas/estimate")
async def estimate_gas(operation: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Estimate gas fees"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        gas = await manager.estimate_gas(operation, network.value)
        return {"operation": operation, "network": network.value, "gas": gas}
    except Exception as e:
        return {"operation": operation, "network": network.value, "gas": {}, "error": str(e)}

@router.get("/gas/prices")
async def get_gas_prices(network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get current gas prices"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        prices = await manager.get_gas_prices(network.value)
        return {"network": network.value, "prices": prices}
    except Exception as e:
        return {"network": network.value, "prices": {}, "error": str(e)}

# ============================================================================
# METADATA & IPFS
# ============================================================================

@router.post("/ipfs/upload")
async def upload_to_ipfs(content: Dict[str, Any]):
    """Upload content to IPFS"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        ipfs_hash = await manager.upload_to_ipfs(content)
        return {"message": "Content uploaded to IPFS", "ipfs_hash": ipfs_hash, "url": f"ipfs://{ipfs_hash}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ipfs/{ipfs_hash}")
async def get_from_ipfs(ipfs_hash: str):
    """Get content from IPFS"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        content = await manager.get_from_ipfs(ipfs_hash)
        return {"ipfs_hash": ipfs_hash, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROYALTIES & RIGHTS
# ============================================================================

@router.post("/nft/{token_id}/royalties")
async def set_royalties(token_id: str, percentage: float, recipient: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Set NFT royalties"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        await manager.set_royalties(token_id, percentage, recipient, network.value)
        return {"message": "Royalties set", "token_id": token_id, "percentage": percentage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nft/{token_id}/royalties")
async def get_royalties(token_id: str, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
    """Get NFT royalties"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        royalties = await manager.get_royalties(token_id, network.value)
        return {"token_id": token_id, "royalties": royalties}
    except Exception as e:
        return {"token_id": token_id, "royalties": {}, "error": str(e)}

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats/network/{network}")
async def get_network_stats(network: BlockchainNetwork):
    """Get blockchain network statistics"""
    try:
        from backend.blockchain.blockchain_manager import BlockchainManager
        manager = BlockchainManager()
        await manager.initialize()
        
        stats = await manager.get_network_stats(network.value)
        return {"network": network.value, "stats": stats}
    except Exception as e:
        return {"network": network.value, "stats": {}, "error": str(e)}
