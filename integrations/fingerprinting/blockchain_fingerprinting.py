"""
Blockchain Fingerprinting - Fingerprinting Module
================================================
Système avancé de fingerprinting blockchain avec NFT integration,
preuves d'ownership et smart contracts pour royalties.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Backend Senior + Security Specialist
"""

import asyncio
import logging
import hashlib
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import web3
from eth_account import Account
import base58

logger = logging.getLogger(__name__)

class BlockchainNetwork(Enum):
    """Réseaux blockchain supportés."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    SOLANA = "solana"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"

class NFTStandard(Enum):
    """Standards NFT supportés."""
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    SPL_TOKEN = "spl_token"  # Solana
    BEP721 = "bep721"  # BSC

class OwnershipStatus(Enum):
    """Status d'ownership."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    REVOKED = "revoked"
    TRANSFERRED = "transferred"

@dataclass
class BlockchainTimestamp:
    """Timestamp blockchain immutable."""
    timestamp_id: str
    content_hash: str
    blockchain_network: BlockchainNetwork
    transaction_hash: str
    block_number: int
    block_hash: str
    timestamp: datetime
    gas_used: int
    confirmation_count: int

@dataclass
class NFTCertificate:
    """Certificat NFT d'ownership."""
    certificate_id: str
    content_fingerprint: str
    token_id: str
    contract_address: str
    blockchain_network: BlockchainNetwork
    nft_standard: NFTStandard
    owner_address: str
    creator_address: str
    metadata_uri: str
    royalty_percentage: float
    created_at: datetime
    minted_at: Optional[datetime]
    current_status: OwnershipStatus

@dataclass
class SmartContract:
    """Smart contract pour royalties."""
    contract_id: str
    contract_address: str
    blockchain_network: BlockchainNetwork
    contract_type: str
    royalty_rate: float
    beneficiary_address: str
    content_fingerprints: List[str]
    deployment_hash: str
    deployment_block: int
    total_royalties_collected: float
    is_active: bool

@dataclass
class OwnershipProof:
    """Preuve d'ownership complète."""
    proof_id: str
    content_identifier: str
    owner_identity: str
    blockchain_timestamps: List[BlockchainTimestamp]
    nft_certificates: List[NFTCertificate]
    smart_contracts: List[SmartContract]
    verification_signatures: List[str]
    creation_proof: Dict[str, Any]
    ownership_chain: List[Dict[str, Any]]
    legal_validity_score: float
    created_at: datetime

class BlockchainFingerprinting:
    """
    Blockchain Fingerprinting Enterprise
    ==================================
    
    Système de fingerprinting blockchain avec:
    - NFT-based ownership certificates sur multi-chains
    - Immutable timestamp proofs avec consensus validation
    - Smart contract royalty management automatisé
    - Multi-chain fingerprint storage distribué
    - Blockchain verification system complet
    - Decentralized rights registry global
    
    Expert Implementation: Backend Senior + Security Specialist
    """
    
    def __init__(self):
        self.ownership_database: Dict[str, OwnershipProof] = {}
        self.timestamp_database: Dict[str, BlockchainTimestamp] = {}
        self.nft_database: Dict[str, NFTCertificate] = {}
        self.contract_database: Dict[str, SmartContract] = {}
        
        # Configuration blockchain
        self.supported_networks = [network.value for network in BlockchainNetwork]
        self.gas_price_multiplier = 1.2
        self.confirmation_threshold = 6
        self.royalty_default_rate = 0.05  # 5%
        
        # Adresses des contrats déployés (simulation)
        self.deployed_contracts = {
            BlockchainNetwork.ETHEREUM: {
                'fingerprint_registry': '0x1234567890123456789012345678901234567890',
                'royalty_manager': '0x0987654321098765432109876543210987654321'
            },
            BlockchainNetwork.POLYGON: {
                'fingerprint_registry': '0x2345678901234567890123456789012345678901',
                'royalty_manager': '0x1987654321098765432109876543210987654321'
            }
        }
        
        logger.info("BlockchainFingerprinting engine initialisé")
    
    async def register_content(
        self,
        content_fingerprint: str,
        owner_identity: str,
        blockchain_networks: List[BlockchainNetwork],
        metadata: Dict[str, Any] = None
    ) -> OwnershipProof:
        """
        Enregistre un contenu sur la blockchain.
        
        Args:
            content_fingerprint: Empreinte du contenu
            owner_identity: Identité du propriétaire
            blockchain_networks: Réseaux à utiliser
            metadata: Métadonnées optionnelles
        
        Returns:
            OwnershipProof: Preuve d'ownership complète
        """
        try:
            # Créer timestamp immutable
            blockchain_timestamps = []
            for network in blockchain_networks:
                timestamp = await self._create_immutable_timestamp(
                    content_fingerprint, network, metadata or {}
                )
                blockchain_timestamps.append(timestamp)
            
            # Créer certificats NFT
            nft_certificates = []
            for network in blockchain_networks:
                certificate = await self._create_nft_certificate(
                    content_fingerprint, owner_identity, network, metadata or {}
                )
                nft_certificates.append(certificate)
            
            # Déployer smart contracts pour royalties
            smart_contracts = []
            for network in blockchain_networks:
                contract = await self._deploy_royalty_contract(
                    content_fingerprint, owner_identity, network
                )
                smart_contracts.append(contract)
            
            # Générer preuves de création
            creation_proof = await self._generate_creation_proof(
                content_fingerprint, owner_identity, metadata or {}
            )
            
            # Créer chaîne d'ownership
            ownership_chain = await self._initialize_ownership_chain(
                content_fingerprint, owner_identity
            )
            
            # Générer signatures de vérification
            verification_signatures = await self._generate_verification_signatures(
                content_fingerprint, blockchain_timestamps, nft_certificates
            )
            
            # Calculer score de validité légale
            legal_validity_score = self._calculate_legal_validity_score(
                blockchain_timestamps, nft_certificates, smart_contracts
            )
            
            # Créer preuve d'ownership complète
            ownership_proof = OwnershipProof(
                proof_id=str(uuid.uuid4()),
                content_identifier=content_fingerprint,
                owner_identity=owner_identity,
                blockchain_timestamps=blockchain_timestamps,
                nft_certificates=nft_certificates,
                smart_contracts=smart_contracts,
                verification_signatures=verification_signatures,
                creation_proof=creation_proof,
                ownership_chain=ownership_chain,
                legal_validity_score=legal_validity_score,
                created_at=datetime.utcnow()
            )
            
            # Stocker en base
            self.ownership_database[ownership_proof.proof_id] = ownership_proof
            
            # Indexer par composants
            for timestamp in blockchain_timestamps:
                self.timestamp_database[timestamp.timestamp_id] = timestamp
            
            for certificate in nft_certificates:
                self.nft_database[certificate.certificate_id] = certificate
            
            for contract in smart_contracts:
                self.contract_database[contract.contract_id] = contract
            
            logger.info(f"Contenu enregistré sur blockchain: {ownership_proof.proof_id}")
            return ownership_proof
            
        except Exception as e:
            logger.error(f"Erreur enregistrement blockchain: {e}")
            raise
    
    async def _create_immutable_timestamp(
        self,
        content_hash: str,
        network: BlockchainNetwork,
        metadata: Dict[str, Any]
    ) -> BlockchainTimestamp:
        """Crée un timestamp immutable sur blockchain."""
        try:
            # Simulation transaction blockchain
            timestamp_data = {
                'content_hash': content_hash,
                'timestamp': datetime.utcnow().isoformat(),
                'network': network.value,
                'metadata_hash': hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
            }
            
            # Générer hash de transaction (simulation)
            transaction_hash = hashlib.sha256(
                json.dumps(timestamp_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Données de bloc (simulation)
            block_number = 18500000 + hash(content_hash) % 100000  # Block simulé
            block_hash = hashlib.sha256(f"block_{block_number}_{network.value}".encode()).hexdigest()
            gas_used = 21000 + len(content_hash) * 100  # Gas estimation
            
            timestamp = BlockchainTimestamp(
                timestamp_id=str(uuid.uuid4()),
                content_hash=content_hash,
                blockchain_network=network,
                transaction_hash=transaction_hash,
                block_number=block_number,
                block_hash=block_hash,
                timestamp=datetime.utcnow(),
                gas_used=gas_used,
                confirmation_count=self.confirmation_threshold
            )
            
            logger.info(f"Timestamp immutable créé: {timestamp.timestamp_id} sur {network.value}")
            return timestamp
            
        except Exception as e:
            logger.error(f"Erreur création timestamp: {e}")
            raise
    
    async def _create_nft_certificate(
        self,
        content_fingerprint: str,
        owner_identity: str,
        network: BlockchainNetwork,
        metadata: Dict[str, Any]
    ) -> NFTCertificate:
        """Crée un certificat NFT d'ownership."""
        try:
            # Déterminer standard NFT selon réseau
            if network in [BlockchainNetwork.ETHEREUM, BlockchainNetwork.POLYGON, BlockchainNetwork.ARBITRUM]:
                nft_standard = NFTStandard.ERC721
            elif network == BlockchainNetwork.BSC:
                nft_standard = NFTStandard.BEP721
            elif network == BlockchainNetwork.SOLANA:
                nft_standard = NFTStandard.SPL_TOKEN
            else:
                nft_standard = NFTStandard.ERC721  # Par défaut
            
            # Générer adresses (simulation)
            contract_address = self._generate_contract_address(network)
            owner_address = self._generate_wallet_address(owner_identity, network)
            creator_address = owner_address  # Même adresse initialement
            
            # Token ID unique
            token_id = str(hash(content_fingerprint + owner_identity) % 1000000)
            
            # Métadonnées NFT
            nft_metadata = {
                'name': f"Content Certificate #{token_id}",
                'description': f"Ownership certificate for content {content_fingerprint[:16]}...",
                'image': f"https://ainflue.com/nft/{token_id}.png",
                'fingerprint': content_fingerprint,
                'creator': owner_identity,
                'created_at': datetime.utcnow().isoformat(),
                'attributes': [
                    {'trait_type': 'Network', 'value': network.value},
                    {'trait_type': 'Standard', 'value': nft_standard.value},
                    {'trait_type': 'Royalty Rate', 'value': f"{self.royalty_default_rate * 100}%"}
                ]
            }
            
            metadata_uri = await self._upload_metadata_ipfs(nft_metadata)
            
            certificate = NFTCertificate(
                certificate_id=str(uuid.uuid4()),
                content_fingerprint=content_fingerprint,
                token_id=token_id,
                contract_address=contract_address,
                blockchain_network=network,
                nft_standard=nft_standard,
                owner_address=owner_address,
                creator_address=creator_address,
                metadata_uri=metadata_uri,
                royalty_percentage=self.royalty_default_rate,
                created_at=datetime.utcnow(),
                minted_at=datetime.utcnow(),
                current_status=OwnershipStatus.CONFIRMED
            )
            
            logger.info(f"Certificat NFT créé: {certificate.certificate_id} sur {network.value}")
            return certificate
            
        except Exception as e:
            logger.error(f"Erreur création certificat NFT: {e}")
            raise
    
    def _generate_contract_address(self, network: BlockchainNetwork) -> str:
        """Génère une adresse de contrat."""
        if network == BlockchainNetwork.SOLANA:
            # Format Solana (base58)
            random_bytes = hashlib.sha256(f"contract_{network.value}_{uuid.uuid4()}".encode()).digest()[:32]
            return base58.b58encode(random_bytes).decode()
        else:
            # Format Ethereum (0x + 40 hex chars)
            contract_hash = hashlib.sha256(f"contract_{network.value}_{uuid.uuid4()}".encode()).hexdigest()
            return f"0x{contract_hash[:40]}"
    
    def _generate_wallet_address(self, identity: str, network: BlockchainNetwork) -> str:
        """Génère une adresse de wallet."""
        if network == BlockchainNetwork.SOLANA:
            # Format Solana
            random_bytes = hashlib.sha256(f"wallet_{identity}_{network.value}".encode()).digest()[:32]
            return base58.b58encode(random_bytes).decode()
        else:
            # Format Ethereum
            wallet_hash = hashlib.sha256(f"wallet_{identity}_{network.value}".encode()).hexdigest()
            return f"0x{wallet_hash[:40]}"
    
    async def _upload_metadata_ipfs(self, metadata: Dict[str, Any]) -> str:
        """Upload métadonnées sur IPFS (simulation)."""
        try:
            # Simulation upload IPFS
            metadata_json = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
            
            # Format IPFS hash (simulation)
            ipfs_hash = f"Qm{metadata_hash[:44]}"
            metadata_uri = f"ipfs://{ipfs_hash}"
            
            logger.info(f"Métadonnées uploadées sur IPFS: {metadata_uri}")
            return metadata_uri
            
        except Exception as e:
            logger.error(f"Erreur upload IPFS: {e}")
            return ""
    
    async def _deploy_royalty_contract(
        self,
        content_fingerprint: str,
        owner_identity: str,
        network: BlockchainNetwork
    ) -> SmartContract:
        """Déploie un smart contract pour les royalties."""
        try:
            contract_address = self._generate_contract_address(network)
            beneficiary_address = self._generate_wallet_address(owner_identity, network)
            
            # Simulation déploiement
            deployment_data = {
                'fingerprint': content_fingerprint,
                'owner': owner_identity,
                'royalty_rate': self.royalty_default_rate,
                'network': network.value,
                'deployed_at': datetime.utcnow().isoformat()
            }
            
            deployment_hash = hashlib.sha256(
                json.dumps(deployment_data, sort_keys=True).encode()
            ).hexdigest()
            
            deployment_block = 18500000 + hash(content_fingerprint) % 100000
            
            smart_contract = SmartContract(
                contract_id=str(uuid.uuid4()),
                contract_address=contract_address,
                blockchain_network=network,
                contract_type="royalty_distribution",
                royalty_rate=self.royalty_default_rate,
                beneficiary_address=beneficiary_address,
                content_fingerprints=[content_fingerprint],
                deployment_hash=deployment_hash,
                deployment_block=deployment_block,
                total_royalties_collected=0.0,
                is_active=True
            )
            
            logger.info(f"Smart contract déployé: {smart_contract.contract_id} sur {network.value}")
            return smart_contract
            
        except Exception as e:
            logger.error(f"Erreur déploiement smart contract: {e}")
            raise
    
    async def _generate_creation_proof(
        self,
        content_fingerprint: str,
        owner_identity: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère la preuve de création."""
        try:
            creation_timestamp = datetime.utcnow()
            
            creation_proof = {
                'content_fingerprint': content_fingerprint,
                'creator_identity': owner_identity,
                'creation_timestamp': creation_timestamp.isoformat(),
                'metadata_hash': hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest(),
                'proof_method': 'blockchain_registration',
                'evidence': {
                    'original_file_hash': content_fingerprint,
                    'creation_device': metadata.get('device_info', 'unknown'),
                    'creation_location': metadata.get('location', 'unknown'),
                    'creation_software': metadata.get('software', 'unknown')
                },
                'witness_signatures': await self._generate_witness_signatures(content_fingerprint),
                'notarization': {
                    'notary_service': 'ainflue_blockchain_notary',
                    'notary_timestamp': creation_timestamp.isoformat(),
                    'notary_signature': self._generate_notary_signature(content_fingerprint, creation_timestamp)
                }
            }
            
            return creation_proof
            
        except Exception as e:
            logger.error(f"Erreur génération preuve création: {e}")
            return {}
    
    async def _generate_witness_signatures(self, content_fingerprint: str) -> List[Dict[str, Any]]:
        """Génère des signatures de témoins."""
        try:
            witnesses = []
            
            # Simulation témoins blockchain
            witness_nodes = [
                {'node_id': 'ethereum_validator_1', 'network': 'ethereum'},
                {'node_id': 'polygon_validator_1', 'network': 'polygon'},
                {'node_id': 'ipfs_node_1', 'network': 'ipfs'}
            ]
            
            for witness in witness_nodes:
                signature_data = f"{content_fingerprint}_{witness['node_id']}_{datetime.utcnow().isoformat()}"
                signature = hashlib.sha256(signature_data.encode()).hexdigest()
                
                witnesses.append({
                    'witness_id': witness['node_id'],
                    'witness_network': witness['network'],
                    'signature': signature,
                    'timestamp': datetime.utcnow().isoformat(),
                    'witness_type': 'blockchain_validator'
                })
            
            return witnesses
            
        except Exception as e:
            logger.error(f"Erreur signatures témoins: {e}")
            return []
    
    def _generate_notary_signature(self, content_fingerprint: str, timestamp: datetime) -> str:
        """Génère une signature notariale."""
        notary_data = f"NOTARY_{content_fingerprint}_{timestamp.isoformat()}_AINFLUE"
        return hashlib.sha256(notary_data.encode()).hexdigest()
    
    async def _initialize_ownership_chain(
        self,
        content_fingerprint: str,
        owner_identity: str
    ) -> List[Dict[str, Any]]:
        """Initialise la chaîne d'ownership."""
        try:
            initial_ownership = {
                'transaction_id': str(uuid.uuid4()),
                'from_owner': None,  # Création originale
                'to_owner': owner_identity,
                'transaction_type': 'original_creation',
                'timestamp': datetime.utcnow().isoformat(),
                'blockchain_proof': {
                    'transaction_hash': hashlib.sha256(f"creation_{content_fingerprint}_{owner_identity}".encode()).hexdigest(),
                    'block_confirmations': self.confirmation_threshold
                },
                'legal_documents': [],
                'witness_signatures': await self._generate_witness_signatures(content_fingerprint)
            }
            
            return [initial_ownership]
            
        except Exception as e:
            logger.error(f"Erreur initialisation chaîne ownership: {e}")
            return []
    
    async def _generate_verification_signatures(
        self,
        content_fingerprint: str,
        timestamps: List[BlockchainTimestamp],
        certificates: List[NFTCertificate]
    ) -> List[str]:
        """Génère les signatures de vérification."""
        try:
            signatures = []
            
            # Signature globale du fingerprint
            global_data = f"VERIFY_{content_fingerprint}_{datetime.utcnow().isoformat()}"
            global_signature = hashlib.sha256(global_data.encode()).hexdigest()
            signatures.append(global_signature)
            
            # Signatures des timestamps
            for timestamp in timestamps:
                timestamp_data = f"TIMESTAMP_{timestamp.transaction_hash}_{timestamp.block_number}"
                timestamp_signature = hashlib.sha256(timestamp_data.encode()).hexdigest()
                signatures.append(timestamp_signature)
            
            # Signatures des certificats NFT
            for certificate in certificates:
                cert_data = f"NFT_{certificate.token_id}_{certificate.contract_address}"
                cert_signature = hashlib.sha256(cert_data.encode()).hexdigest()
                signatures.append(cert_signature)
            
            return signatures
            
        except Exception as e:
            logger.error(f"Erreur génération signatures vérification: {e}")
            return []
    
    def _calculate_legal_validity_score(
        self,
        timestamps: List[BlockchainTimestamp],
        certificates: List[NFTCertificate],
        contracts: List[SmartContract]
    ) -> float:
        """Calcule le score de validité légale."""
        try:
            score = 0.0
            
            # Score basé sur les timestamps (30%)
            if timestamps:
                timestamp_score = min(len(timestamps) / 3.0, 1.0)  # Max 3 réseaux
                confirmation_score = min(
                    sum(t.confirmation_count for t in timestamps) / (len(timestamps) * self.confirmation_threshold),
                    1.0
                )
                score += (timestamp_score + confirmation_score) / 2 * 0.3
            
            # Score basé sur les certificats NFT (40%)
            if certificates:
                certificate_score = min(len(certificates) / 2.0, 1.0)  # Max 2 certificats
                status_score = sum(
                    1.0 if cert.current_status == OwnershipStatus.CONFIRMED else 0.5
                    for cert in certificates
                ) / len(certificates)
                score += (certificate_score + status_score) / 2 * 0.4
            
            # Score basé sur les smart contracts (20%)
            if contracts:
                contract_score = min(len(contracts) / 2.0, 1.0)
                active_score = sum(1.0 if contract.is_active else 0.0 for contract in contracts) / len(contracts)
                score += (contract_score + active_score) / 2 * 0.2
            
            # Score de diversité des réseaux (10%)
            networks = set()
            for timestamp in timestamps:
                networks.add(timestamp.blockchain_network)
            for certificate in certificates:
                networks.add(certificate.blockchain_network)
            
            network_diversity_score = min(len(networks) / 3.0, 1.0)  # Max 3 réseaux différents
            score += network_diversity_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul validité légale: {e}")
            return 0.5
    
    async def verify_ownership(
        self,
        content_fingerprint: str,
        claimed_owner: str
    ) -> Dict[str, Any]:
        """
        Vérifie l'ownership d'un contenu.
        
        Args:
            content_fingerprint: Empreinte du contenu
            claimed_owner: Propriétaire revendiqué
        
        Returns:
            Dict[str, Any]: Résultat de vérification
        """
        try:
            verification_result = {
                'content_fingerprint': content_fingerprint,
                'claimed_owner': claimed_owner,
                'verification_timestamp': datetime.utcnow().isoformat(),
                'ownership_verified': False,
                'confidence_score': 0.0,
                'evidence': [],
                'warnings': [],
                'legal_status': 'unknown'
            }
            
            # Chercher preuves d'ownership
            matching_proofs = []
            for proof in self.ownership_database.values():
                if proof.content_identifier == content_fingerprint:
                    matching_proofs.append(proof)
            
            if not matching_proofs:
                verification_result['warnings'].append("Aucune preuve d'ownership trouvée sur blockchain")
                return verification_result
            
            # Vérifier chaque preuve
            best_proof = None
            highest_score = 0.0
            
            for proof in matching_proofs:
                # Vérifier identité du propriétaire
                owner_match = proof.owner_identity == claimed_owner
                
                # Vérifier validité des timestamps
                timestamp_validity = await self._verify_timestamps(proof.blockchain_timestamps)
                
                # Vérifier certificats NFT
                nft_validity = await self._verify_nft_certificates(proof.nft_certificates)
                
                # Vérifier smart contracts
                contract_validity = await self._verify_smart_contracts(proof.smart_contracts)
                
                # Score de confiance combiné
                confidence = (
                    (1.0 if owner_match else 0.0) * 0.4 +
                    timestamp_validity * 0.3 +
                    nft_validity * 0.2 +
                    contract_validity * 0.1
                )
                
                if confidence > highest_score:
                    highest_score = confidence
                    best_proof = proof
                
                verification_result['evidence'].append({
                    'proof_id': proof.proof_id,
                    'owner_match': owner_match,
                    'timestamp_validity': timestamp_validity,
                    'nft_validity': nft_validity,
                    'contract_validity': contract_validity,
                    'confidence': confidence,
                    'legal_validity_score': proof.legal_validity_score
                })
            
            # Résultat final
            if best_proof and highest_score >= 0.7:
                verification_result['ownership_verified'] = True
                verification_result['confidence_score'] = highest_score
                verification_result['legal_status'] = 'verified'
                verification_result['best_proof_id'] = best_proof.proof_id
            elif best_proof and highest_score >= 0.5:
                verification_result['ownership_verified'] = True
                verification_result['confidence_score'] = highest_score
                verification_result['legal_status'] = 'probable'
                verification_result['warnings'].append("Confiance modérée - vérification additionnelle recommandée")
            else:
                verification_result['warnings'].append("Preuves insuffisantes pour vérifier l'ownership")
            
            logger.info(f"Vérification ownership terminée: {verification_result['ownership_verified']} (score: {highest_score:.2f})")
            return verification_result
            
        except Exception as e:
            logger.error(f"Erreur vérification ownership: {e}")
            return verification_result
    
    async def _verify_timestamps(self, timestamps: List[BlockchainTimestamp]) -> float:
        """Vérifie la validité des timestamps blockchain."""
        try:
            if not timestamps:
                return 0.0
            
            valid_timestamps = 0
            total_confirmations = 0
            
            for timestamp in timestamps:
                # Vérifier confirmations
                if timestamp.confirmation_count >= self.confirmation_threshold:
                    valid_timestamps += 1
                
                total_confirmations += timestamp.confirmation_count
                
                # Vérifier cohérence temporelle
                time_diff = datetime.utcnow() - timestamp.timestamp
                if time_diff.total_seconds() < 0:
                    logger.warning(f"Timestamp futur détecté: {timestamp.timestamp_id}")
            
            # Score basé sur validité et confirmations
            validity_score = valid_timestamps / len(timestamps)
            confirmation_score = min(
                total_confirmations / (len(timestamps) * self.confirmation_threshold),
                1.0
            )
            
            return (validity_score + confirmation_score) / 2
            
        except Exception as e:
            logger.error(f"Erreur vérification timestamps: {e}")
            return 0.0
    
    async def _verify_nft_certificates(self, certificates: List[NFTCertificate]) -> float:
        """Vérifie la validité des certificats NFT."""
        try:
            if not certificates:
                return 0.0
            
            valid_certificates = 0
            
            for certificate in certificates:
                # Vérifier status
                if certificate.current_status == OwnershipStatus.CONFIRMED:
                    valid_certificates += 1
                
                # Vérifier métadonnées
                if certificate.metadata_uri and certificate.metadata_uri.startswith('ipfs://'):
                    # Métadonnées sur IPFS = plus fiable
                    valid_certificates += 0.5
                
                # Vérifier cohérence temporelle
                if certificate.minted_at and certificate.created_at:
                    if certificate.minted_at >= certificate.created_at:
                        valid_certificates += 0.5
            
            return min(valid_certificates / len(certificates), 1.0)
            
        except Exception as e:
            logger.error(f"Erreur vérification certificats NFT: {e}")
            return 0.0
    
    async def _verify_smart_contracts(self, contracts: List[SmartContract]) -> float:
        """Vérifie la validité des smart contracts."""
        try:
            if not contracts:
                return 0.0
            
            valid_contracts = 0
            
            for contract in contracts:
                # Vérifier activation
                if contract.is_active:
                    valid_contracts += 1
                
                # Vérifier déploiement
                if contract.deployment_hash and contract.deployment_block > 0:
                    valid_contracts += 0.5
                
                # Vérifier royalties collectées (signe d'utilisation)
                if contract.total_royalties_collected > 0:
                    valid_contracts += 0.5
            
            return min(valid_contracts / len(contracts), 1.0)
            
        except Exception as e:
            logger.error(f"Erreur vérification smart contracts: {e}")
            return 0.0
    
    async def transfer_ownership(
        self,
        content_fingerprint: str,
        current_owner: str,
        new_owner: str,
        transfer_proof: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Transfère l'ownership d'un contenu.
        
        Args:
            content_fingerprint: Empreinte du contenu
            current_owner: Propriétaire actuel
            new_owner: Nouveau propriétaire
            transfer_proof: Preuve de transfert
        
        Returns:
            Dict[str, Any]: Résultat du transfert
        """
        try:
            # Vérifier ownership actuel
            verification = await self.verify_ownership(content_fingerprint, current_owner)
            
            if not verification['ownership_verified']:
                return {
                    'transfer_success': False,
                    'error': 'Ownership actuel non vérifié',
                    'verification_result': verification
                }
            
            # Trouver la preuve d'ownership
            proof_id = verification.get('best_proof_id')
            if not proof_id or proof_id not in self.ownership_database:
                return {
                    'transfer_success': False,
                    'error': 'Preuve d\'ownership introuvable'
                }
            
            current_proof = self.ownership_database[proof_id]
            
            # Créer nouvelle entrée dans la chaîne d'ownership
            transfer_transaction = {
                'transaction_id': str(uuid.uuid4()),
                'from_owner': current_owner,
                'to_owner': new_owner,
                'transaction_type': 'ownership_transfer',
                'timestamp': datetime.utcnow().isoformat(),
                'transfer_proof': transfer_proof or {},
                'blockchain_proof': {
                    'transaction_hash': hashlib.sha256(f"transfer_{content_fingerprint}_{current_owner}_{new_owner}".encode()).hexdigest(),
                    'block_confirmations': 0  # En attente de confirmation
                },
                'legal_documents': transfer_proof.get('legal_documents', []) if transfer_proof else [],
                'witness_signatures': await self._generate_witness_signatures(f"transfer_{content_fingerprint}")
            }
            
            # Mettre à jour la chaîne d'ownership
            current_proof.ownership_chain.append(transfer_transaction)
            current_proof.owner_identity = new_owner
            
            # Mettre à jour les certificats NFT
            for certificate in current_proof.nft_certificates:
                certificate.owner_address = self._generate_wallet_address(new_owner, certificate.blockchain_network)
                certificate.current_status = OwnershipStatus.TRANSFERRED
            
            # Mettre à jour les smart contracts
            for contract in current_proof.smart_contracts:
                contract.beneficiary_address = self._generate_wallet_address(new_owner, contract.blockchain_network)
            
            # Recalculer score de validité légale
            current_proof.legal_validity_score = self._calculate_legal_validity_score(
                current_proof.blockchain_timestamps,
                current_proof.nft_certificates,
                current_proof.smart_contracts
            )
            
            logger.info(f"Ownership transféré: {current_owner} -> {new_owner} pour {content_fingerprint}")
            
            return {
                'transfer_success': True,
                'transfer_id': transfer_transaction['transaction_id'],
                'updated_proof_id': proof_id,
                'new_owner': new_owner,
                'transfer_timestamp': transfer_transaction['timestamp'],
                'legal_validity_score': current_proof.legal_validity_score
            }
            
        except Exception as e:
            logger.error(f"Erreur transfert ownership: {e}")
            return {
                'transfer_success': False,
                'error': str(e)
            }
    
    async def get_ownership_history(self, content_fingerprint: str) -> Dict[str, Any]:
        """Récupère l'historique d'ownership."""
        try:
            # Chercher toutes les preuves pour ce contenu
            matching_proofs = []
            for proof in self.ownership_database.values():
                if proof.content_identifier == content_fingerprint:
                    matching_proofs.append(proof)
            
            if not matching_proofs:
                return {
                    'content_fingerprint': content_fingerprint,
                    'ownership_found': False,
                    'message': 'Aucun historique d\'ownership trouvé'
                }
            
            # Compiler l'historique
            history = {
                'content_fingerprint': content_fingerprint,
                'ownership_found': True,
                'total_proofs': len(matching_proofs),
                'ownership_timeline': [],
                'current_owners': [],
                'blockchain_networks': set(),
                'nft_certificates': [],
                'smart_contracts': []
            }
            
            for proof in matching_proofs:
                # Timeline d'ownership
                for transaction in proof.ownership_chain:
                    history['ownership_timeline'].append({
                        'timestamp': transaction['timestamp'],
                        'from_owner': transaction['from_owner'],
                        'to_owner': transaction['to_owner'],
                        'transaction_type': transaction['transaction_type'],
                        'transaction_id': transaction['transaction_id']
                    })
                
                # Propriétaires actuels
                history['current_owners'].append(proof.owner_identity)
                
                # Réseaux utilisés
                for timestamp in proof.blockchain_timestamps:
                    history['blockchain_networks'].add(timestamp.blockchain_network.value)
                
                # Certificats NFT
                for certificate in proof.nft_certificates:
                    history['nft_certificates'].append({
                        'certificate_id': certificate.certificate_id,
                        'token_id': certificate.token_id,
                        'network': certificate.blockchain_network.value,
                        'status': certificate.current_status.value,
                        'owner_address': certificate.owner_address
                    })
                
                # Smart contracts
                for contract in proof.smart_contracts:
                    history['smart_contracts'].append({
                        'contract_id': contract.contract_id,
                        'contract_address': contract.contract_address,
                        'network': contract.blockchain_network.value,
                        'royalty_rate': contract.royalty_rate,
                        'total_royalties': contract.total_royalties_collected,
                        'is_active': contract.is_active
                    })
            
            # Trier timeline par date
            history['ownership_timeline'].sort(key=lambda x: x['timestamp'])
            
            # Convertir set en list pour JSON
            history['blockchain_networks'] = list(history['blockchain_networks'])
            
            return history
            
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return {
                'content_fingerprint': content_fingerprint,
                'ownership_found': False,
                'error': str(e)
            }
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Retourne les analytics du système blockchain."""
        try:
            total_proofs = len(self.ownership_database)
            total_timestamps = len(self.timestamp_database)
            total_nfts = len(self.nft_database)
            total_contracts = len(self.contract_database)
            
            # Répartition par réseau
            network_distribution = {}
            for timestamp in self.timestamp_database.values():
                network = timestamp.blockchain_network.value
                network_distribution[network] = network_distribution.get(network, 0) + 1
            
            # Status des NFT
            nft_status_distribution = {}
            for nft in self.nft_database.values():
                status = nft.current_status.value
                nft_status_distribution[status] = nft_status_distribution.get(status, 0) + 1
            
            # Royalties collectées
            total_royalties = sum(contract.total_royalties_collected for contract in self.contract_database.values())
            active_contracts = sum(1 for contract in self.contract_database.values() if contract.is_active)
            
            # Score de validité légale moyen
            legal_scores = [proof.legal_validity_score for proof in self.ownership_database.values()]
            avg_legal_validity = sum(legal_scores) / len(legal_scores) if legal_scores else 0.0
            
            return {
                'total_ownership_proofs': total_proofs,
                'total_blockchain_timestamps': total_timestamps,
                'total_nft_certificates': total_nfts,
                'total_smart_contracts': total_contracts,
                'network_distribution': network_distribution,
                'nft_status_distribution': nft_status_distribution,
                'total_royalties_collected': total_royalties,
                'active_contracts': active_contracts,
                'average_legal_validity_score': avg_legal_validity,
                'supported_networks': self.supported_networks,
                'confirmation_threshold': self.confirmation_threshold,
                'default_royalty_rate': self.royalty_default_rate
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics blockchain: {e}")
            return {}

# Utilitaires pour la blockchain
try:
    import web3
    from eth_account import Account
except ImportError:
    # Fallback si web3 n'est pas installé
    logger.warning("web3.py non installé - utilisation mode simulation")
    pass

try:
    import base58
except ImportError:
    # Fallback pour Solana
    logger.warning("base58 non installé - support Solana limité")
    
    def b58encode(data):
        return hashlib.sha256(data).hexdigest()
    
    class base58:
        @staticmethod
        def b58encode(data):
            return hashlib.sha256(data).hexdigest()[:32].encode()