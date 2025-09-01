"""Rights Ownership Registry - Advanced Rights Management System
Module de registre de propriété des droits avec gestion avancée
Système professionnel pour la gestion de la propriété intellectuelle
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
import hashlib

from pydantic import BaseModel, Field, validator


logger = logging.getLogger(__name__)


class OwnershipType(Enum):
    """Types de propriété"""
    SOLE = "sole"  # Propriété unique
    JOINT = "joint"  # Copropriété avec parts égales
    TENANTS_IN_COMMON = "tenants_in_common"  # Copropriété avec parts inégales
    WORK_FOR_HIRE = "work_for_hire"  # Travail commandé
    DERIVATIVE = "derivative"  # Œuvre dérivée
    COLLECTIVE = "collective"  # Œuvre collective


class OwnershipVerificationStatus(Enum):
    """Statut de vérification de propriété"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    REJECTED = "rejected"
    FRAUDULENT = "fraudulent"


class CreatorshipEvidence(BaseModel):
    """Preuves de création"""
    evidence_id: str = Field(..., description="ID unique de la preuve")
    evidence_type: str  # timestamp, witness, deposit, blockchain, notarization
    evidence_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str  # system, user, external
    verification_score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OwnershipChain(BaseModel):
    """Chaîne de propriété"""
    chain_id: str = Field(..., description="ID de la chaîne")
    content_id: str
    genesis_holder: str  # Créateur original
    current_holder: str  # Propriétaire actuel
    chain_links: List[Dict[str, Any]] = Field(default_factory=list)
    verification_hash: str = Field(default="")
    integrity_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_verified: datetime = Field(default_factory=datetime.utcnow)
    
    def add_link(self, transaction_data: Dict[str, Any]) -> bool:
        """Ajoute un maillon à la chaîne"""
        try:
            link = {
                'link_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'data': transaction_data,
                'previous_hash': self.verification_hash
            }
            
            # Calcul du hash de vérification
            link_str = json.dumps(link, sort_keys=True)
            link['hash'] = hashlib.sha256(link_str.encode()).hexdigest()
            
            self.chain_links.append(link)
            self.verification_hash = link['hash']
            self.last_verified = datetime.utcnow()
            
            return True
        except Exception as e:
            logger.error(f"Erreur ajout maillon chaîne: {e}")
            return False


class OwnershipRegistry:
    """Registre avancé de propriété des droits"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ownership_records: Dict[str, OwnershipChain] = {}
        self.creator_evidence: Dict[str, List[CreatorshipEvidence]] = {}
        self.verification_queue: List[str] = []
        self.fraud_alerts: List[Dict[str, Any]] = []
        
        # Configuration
        self.verification_threshold = config.get('verification_threshold', 0.8)
        self.fraud_detection_enabled = config.get('fraud_detection', True)
        self.blockchain_integration = config.get('blockchain_enabled', False)
        
    async def register_original_creation(
        self,
        content_id: str,
        creator_id: str,
        title: str,
        creation_evidence: List[CreatorshipEvidence],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Enregistre une création originale avec preuves"""
        try:
            chain_id = self._generate_chain_id()
            
            # Création de la chaîne de propriété initiale
            ownership_chain = OwnershipChain(
                chain_id=chain_id,
                content_id=content_id,
                genesis_holder=creator_id,
                current_holder=creator_id
            )
            
            # Ajout du lien de création initial
            genesis_data = {
                'action': 'original_creation',
                'creator_id': creator_id,
                'title': title,
                'creation_timestamp': datetime.utcnow().isoformat(),
                'metadata': content_metadata or {}
            }
            
            ownership_chain.add_link(genesis_data)
            
            # Stockage des preuves de création
            self.creator_evidence[content_id] = creation_evidence
            
            # Ajout à la queue de vérification
            self.verification_queue.append(content_id)
            
            # Enregistrement de la chaîne
            self.ownership_records[content_id] = ownership_chain
            
            logger.info(f"Création originale enregistrée: {chain_id}")
            return chain_id
            
        except Exception as e:
            logger.error(f"Erreur enregistrement création: {e}")
            raise
    
    async def transfer_ownership(
        self,
        content_id: str,
        from_holder: str,
        to_holder: str,
        transfer_type: str,
        transfer_data: Dict[str, Any],
        evidence: Optional[List[CreatorshipEvidence]] = None
    ) -> bool:
        """Transfère la propriété avec vérification"""
        try:
            if content_id not in self.ownership_records:
                raise ValueError(f"Contenu {content_id} non trouvé dans le registre")
            
            ownership_chain = self.ownership_records[content_id]
            
            # Vérification du propriétaire actuel
            if ownership_chain.current_holder != from_holder:
                raise ValueError(f"Propriétaire actuel incorrect: {ownership_chain.current_holder} vs {from_holder}")
            
            # Préparation des données de transfert
            transfer_link_data = {
                'action': 'ownership_transfer',
                'transfer_type': transfer_type,
                'from_holder': from_holder,
                'to_holder': to_holder,
                'transfer_data': transfer_data,
                'evidence_count': len(evidence) if evidence else 0
            }
            
            # Ajout du lien de transfert
            if ownership_chain.add_link(transfer_link_data):
                ownership_chain.current_holder = to_holder
                
                # Stockage des preuves si fournies
                if evidence:
                    if content_id not in self.creator_evidence:
                        self.creator_evidence[content_id] = []
                    self.creator_evidence[content_id].extend(evidence)
                
                logger.info(f"Propriété transférée: {from_holder} -> {to_holder}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur transfert propriété: {e}")
            return False
    
    async def verify_ownership(
        self,
        content_id: str,
        claimed_holder: str,
        verification_evidence: Optional[List[CreatorshipEvidence]] = None
    ) -> Dict[str, Any]:
        """Vérifie la propriété d'un contenu"""
        try:
            if content_id not in self.ownership_records:
                return {
                    'verified': False,
                    'reason': 'Content not found in registry',
                    'confidence': 0.0
                }
            
            ownership_chain = self.ownership_records[content_id]
            
            # Vérification de base
            is_current_owner = ownership_chain.current_holder == claimed_holder
            
            # Calcul du score de confiance
            confidence_score = await self._calculate_ownership_confidence(
                content_id, 
                claimed_holder, 
                verification_evidence
            )
            
            # Vérification de l'intégrité de la chaîne
            chain_integrity = await self._verify_chain_integrity(ownership_chain)
            
            # Détection de fraude
            fraud_risk = await self._assess_fraud_risk(content_id, claimed_holder)
            
            result = {
                'verified': is_current_owner and confidence_score >= self.verification_threshold,
                'current_owner': ownership_chain.current_holder,
                'claimed_owner': claimed_holder,
                'confidence_score': confidence_score,
                'chain_integrity': chain_integrity,
                'fraud_risk': fraud_risk,
                'genesis_holder': ownership_chain.genesis_holder,
                'verification_timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur vérification propriété: {e}")
            return {
                'verified': False,
                'reason': f'Verification error: {str(e)}',
                'confidence': 0.0
            }
    
    async def get_ownership_history(
        self,
        content_id: str,
        include_evidence: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Récupère l'historique complet de propriété"""
        try:
            if content_id not in self.ownership_records:
                return None
            
            ownership_chain = self.ownership_records[content_id]
            
            history = {
                'chain_id': ownership_chain.chain_id,
                'content_id': content_id,
                'genesis_holder': ownership_chain.genesis_holder,
                'current_holder': ownership_chain.current_holder,
                'chain_length': len(ownership_chain.chain_links),
                'creation_date': ownership_chain.created_at.isoformat(),
                'last_modified': ownership_chain.last_verified.isoformat(),
                'chain_integrity': ownership_chain.integrity_verified,
                'ownership_transfers': []
            }
            
            # Reconstruction de l'historique des transferts
            for link in ownership_chain.chain_links:
                transfer_info = {
                    'link_id': link['link_id'],
                    'timestamp': link['timestamp'],
                    'action': link['data'].get('action'),
                    'hash': link['hash']
                }
                
                if link['data'].get('action') == 'ownership_transfer':
                    transfer_info.update({
                        'from_holder': link['data'].get('from_holder'),
                        'to_holder': link['data'].get('to_holder'),
                        'transfer_type': link['data'].get('transfer_type')
                    })
                
                history['ownership_transfers'].append(transfer_info)
            
            # Ajout des preuves si demandé
            if include_evidence and content_id in self.creator_evidence:
                history['evidence'] = [
                    {
                        'evidence_id': evidence.evidence_id,
                        'evidence_type': evidence.evidence_type,
                        'timestamp': evidence.timestamp.isoformat(),
                        'verification_score': evidence.verification_score
                    }
                    for evidence in self.creator_evidence[content_id]
                ]
            
            return history
            
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return None
    
    async def detect_ownership_conflicts(
        self,
        content_id: str
    ) -> List[Dict[str, Any]]:
        """Détecte les conflits de propriété potentiels"""
        try:
            conflicts = []
            
            if content_id not in self.ownership_records:
                return conflicts
            
            # Recherche de réclamations multiples
            similar_contents = await self._find_similar_content_claims(content_id)
            
            for similar_content in similar_contents:
                if similar_content['content_id'] != content_id:
                    conflict = {
                        'conflict_type': 'duplicate_claim',
                        'conflicting_content': similar_content['content_id'],
                        'similarity_score': similar_content['similarity'],
                        'potential_dispute': True
                    }
                    conflicts.append(conflict)
            
            # Vérification des transferts suspects
            ownership_chain = self.ownership_records[content_id]
            
            for i, link in enumerate(ownership_chain.chain_links):
                if link['data'].get('action') == 'ownership_transfer':
                    # Vérification de la rapidité des transferts
                    if i > 0:
                        prev_link = ownership_chain.chain_links[i-1]
                        time_diff = (
                            datetime.fromisoformat(link['timestamp']) - 
                            datetime.fromisoformat(prev_link['timestamp'])
                        ).total_seconds()
                        
                        if time_diff < 3600:  # Transfert en moins d'1 heure
                            conflicts.append({
                                'conflict_type': 'rapid_transfer',
                                'link_id': link['link_id'],
                                'time_diff_seconds': time_diff,
                                'suspicious': True
                            })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Erreur détection conflits: {e}")
            return []
    
    async def generate_ownership_certificate(
        self,
        content_id: str,
        certificate_type: str = "standard"
    ) -> Optional[Dict[str, Any]]:
        """Génère un certificat de propriété officiel"""
        try:
            if content_id not in self.ownership_records:
                return None
            
            ownership_chain = self.ownership_records[content_id]
            
            # Vérification de l'intégrité avant génération
            integrity_check = await self._verify_chain_integrity(ownership_chain)
            
            if not integrity_check:
                logger.warning(f"Intégrité chaîne compromise pour {content_id}")
                return None
            
            certificate_id = self._generate_certificate_id()
            
            certificate = {
                'certificate_id': certificate_id,
                'certificate_type': certificate_type,
                'content_id': content_id,
                'current_owner': ownership_chain.current_holder,
                'genesis_creator': ownership_chain.genesis_holder,
                'issue_date': datetime.utcnow().isoformat(),
                'validity_period': '1_year',  # Certificats valides 1 an
                'chain_verification': {
                    'chain_id': ownership_chain.chain_id,
                    'chain_length': len(ownership_chain.chain_links),
                    'integrity_verified': True,
                    'verification_hash': ownership_chain.verification_hash
                },
                'digital_signature': self._generate_digital_signature(
                    certificate_id, 
                    content_id, 
                    ownership_chain.current_holder
                )
            }
            
            # Ajout d'informations supplémentaires selon le type
            if certificate_type == "detailed":
                certificate['ownership_history'] = await self.get_ownership_history(
                    content_id, 
                    include_evidence=True
                )
            
            logger.info(f"Certificat de propriété généré: {certificate_id}")
            return certificate
            
        except Exception as e:
            logger.error(f"Erreur génération certificat: {e}")
            return None
    
    async def _calculate_ownership_confidence(
        self,
        content_id: str,
        claimed_holder: str,
        verification_evidence: Optional[List[CreatorshipEvidence]] = None
    ) -> float:
        """Calcule le score de confiance de propriété"""
        try:
            confidence_factors = []
            
            # Facteur 1: Présence dans la chaîne officielle
            ownership_chain = self.ownership_records[content_id]
            if ownership_chain.current_holder == claimed_holder:
                confidence_factors.append(0.4)  # 40% pour propriété officielle
            
            # Facteur 2: Preuves de création
            if content_id in self.creator_evidence:
                evidence_scores = [
                    evidence.verification_score 
                    for evidence in self.creator_evidence[content_id]
                ]
                avg_evidence_score = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0
                confidence_factors.append(avg_evidence_score * 0.3)  # 30% pour preuves existantes
            
            # Facteur 3: Nouvelles preuves fournies
            if verification_evidence:
                new_evidence_scores = [
                    evidence.verification_score 
                    for evidence in verification_evidence
                ]
                avg_new_evidence = sum(new_evidence_scores) / len(new_evidence_scores) if new_evidence_scores else 0
                confidence_factors.append(avg_new_evidence * 0.2)  # 20% pour nouvelles preuves
            
            # Facteur 4: Intégrité de la chaîne
            chain_integrity = await self._verify_chain_integrity(ownership_chain)
            if chain_integrity:
                confidence_factors.append(0.1)  # 10% pour intégrité
            
            return min(sum(confidence_factors), 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul confiance: {e}")
            return 0.0
    
    async def _verify_chain_integrity(self, ownership_chain: OwnershipChain) -> bool:
        """Vérifie l'intégrité de la chaîne de propriété"""
        try:
            if not ownership_chain.chain_links:
                return True
            
            previous_hash = ""
            
            for link in ownership_chain.chain_links:
                # Vérification du hash précédent
                if link['previous_hash'] != previous_hash:
                    return False
                
                # Recalcul du hash pour vérification
                link_copy = link.copy()
                stored_hash = link_copy.pop('hash')
                
                link_str = json.dumps(link_copy, sort_keys=True)
                calculated_hash = hashlib.sha256(link_str.encode()).hexdigest()
                
                if stored_hash != calculated_hash:
                    return False
                
                previous_hash = stored_hash
            
            ownership_chain.integrity_verified = True
            return True
            
        except Exception as e:
            logger.error(f"Erreur vérification intégrité: {e}")
            return False
    
    async def _assess_fraud_risk(self, content_id: str, claimed_holder: str) -> float:
        """Évalue le risque de fraude"""
        try:
            risk_factors = []
            
            # Vérification des patterns suspects
            recent_transfers = 0
            if content_id in self.ownership_records:
                ownership_chain = self.ownership_records[content_id]
                
                # Compter les transferts récents (dernières 24h)
                now = datetime.utcnow()
                for link in ownership_chain.chain_links:
                    link_time = datetime.fromisoformat(link['timestamp'])
                    if (now - link_time).total_seconds() < 86400:  # 24 heures
                        if link['data'].get('action') == 'ownership_transfer':
                            recent_transfers += 1
            
            # Facteur de risque basé sur les transferts récents
            if recent_transfers > 3:
                risk_factors.append(0.7)  # Risque élevé
            elif recent_transfers > 1:
                risk_factors.append(0.3)  # Risque modéré
            
            # Vérification contre la liste des comptes suspects
            # (À implémenter avec une base de données de comptes frauduleux)
            
            return min(sum(risk_factors), 1.0)
            
        except Exception as e:
            logger.error(f"Erreur évaluation fraude: {e}")
            return 0.0
    
    async def _find_similar_content_claims(self, content_id: str) -> List[Dict[str, Any]]:
        """Trouve les réclamations de contenu similaire"""
        try:
            # Placeholder pour recherche de similarité
            # À implémenter avec une base de données vectorielle
            similar_contents = []
            
            # Logique de comparaison basée sur métadonnées, hashes, etc.
            
            return similar_contents
            
        except Exception as e:
            logger.error(f"Erreur recherche contenu similaire: {e}")
            return []
    
    def _generate_chain_id(self) -> str:
        """Génère un ID unique pour la chaîne de propriété"""
        return f"OWN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_certificate_id(self) -> str:
        """Génère un ID unique pour le certificat"""
        return f"CERT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_digital_signature(
        self,
        certificate_id: str,
        content_id: str,
        owner_id: str
    ) -> str:
        """Génère une signature numérique pour le certificat"""
        try:
            signature_data = f"{certificate_id}:{content_id}:{owner_id}:{datetime.utcnow().isoformat()}"
            return hashlib.sha256(signature_data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Erreur génération signature: {e}")
            return ""
    
    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du registre"""
        try:
            total_contents = len(self.ownership_records)
            total_transfers = 0
            verified_chains = 0
            
            for chain in self.ownership_records.values():
                total_transfers += len([
                    link for link in chain.chain_links 
                    if link['data'].get('action') == 'ownership_transfer'
                ])
                
                if chain.integrity_verified:
                    verified_chains += 1
            
            return {
                'total_registered_contents': total_contents,
                'total_ownership_transfers': total_transfers,
                'verified_chains': verified_chains,
                'verification_rate': verified_chains / total_contents if total_contents > 0 else 0,
                'pending_verifications': len(self.verification_queue),
                'fraud_alerts': len(self.fraud_alerts),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur statistiques registre: {e}")
            return {}


__all__ = [
    'OwnershipRegistry',
    'OwnershipChain',
    'CreatorshipEvidence',
    'OwnershipType',
    'OwnershipVerificationStatus'
]
