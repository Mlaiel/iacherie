"""Rarity Calculator - IA-Influencer-Agent Platform

Intelligent rarity calculation system for NFT collections with
statistical analysis and market-driven rarity scoring.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import math

logger = logging.getLogger(__name__)


@dataclass
class RarityAnalysis:
    token_id: str
    rarity_score: float
    rarity_rank: int
    trait_rarities: Dict[str, float]
    total_traits: int
    unique_traits: int


class RarityCalculator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.trait_frequencies: Dict[str, Dict[str, int]] = {}
        self.collection_size = 0
    
    async def calculate_collection_rarity(
        self,
        collection_metadata: List[Dict[str, Any]]
    ) -> List[RarityAnalysis]:
        try:
            self.collection_size = len(collection_metadata)
            self.logger.info(f"Calculating rarity for {self.collection_size} NFTs")
            
            # Analyze trait frequencies
            self._analyze_trait_frequencies(collection_metadata)
            
            # Calculate rarity scores
            rarity_analyses = []
            for nft in collection_metadata:
                analysis = self._calculate_nft_rarity(nft)
                rarity_analyses.append(analysis)
            
            # Sort by rarity score and assign ranks
            rarity_analyses.sort(key=lambda x: x.rarity_score, reverse=True)
            for i, analysis in enumerate(rarity_analyses):
                analysis.rarity_rank = i + 1
            
            return rarity_analyses
            
        except Exception as e:
            self.logger.error(f"Rarity calculation failed: {e}")
            raise
    
    def _analyze_trait_frequencies(self, collection_metadata: List[Dict[str, Any]]):
        """Analyze frequency of each trait value"""
        self.trait_frequencies = {}
        
        for nft in collection_metadata:
            attributes = nft.get("attributes", [])
            for attr in attributes:
                trait_type = attr.get("trait_type")
                value = str(attr.get("value"))
                
                if trait_type not in self.trait_frequencies:
                    self.trait_frequencies[trait_type] = {}
                
                if value not in self.trait_frequencies[trait_type]:
                    self.trait_frequencies[trait_type][value] = 0
                
                self.trait_frequencies[trait_type][value] += 1
    
    def _calculate_nft_rarity(self, nft_metadata: Dict[str, Any]) -> RarityAnalysis:
        """Calculate rarity score for individual NFT"""
        token_id = nft_metadata.get("token_id", "unknown")
        attributes = nft_metadata.get("attributes", [])
        
        trait_rarities = {}
        rarity_score = 0
        
        for attr in attributes:
            trait_type = attr.get("trait_type")
            value = str(attr.get("value"))
            
            if trait_type in self.trait_frequencies and value in self.trait_frequencies[trait_type]:
                frequency = self.trait_frequencies[trait_type][value]
                trait_rarity = 1 / (frequency / self.collection_size)
                trait_rarities[f"{trait_type}:{value}"] = trait_rarity
                rarity_score += trait_rarity
        
        return RarityAnalysis(
            token_id=token_id,
            rarity_score=rarity_score,
            rarity_rank=0,  # Will be set later
            trait_rarities=trait_rarities,
            total_traits=len(attributes),
            unique_traits=len([t for t in trait_rarities.values() if t > 10])
        )