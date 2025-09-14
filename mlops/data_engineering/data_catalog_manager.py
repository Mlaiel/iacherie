"""
📊 Data Catalog Manager - Enterprise MLOps
Expert DBA + Data Engineering: Catalogue enterprise avec governance et lineage

🎯 EXPERTISE DÉMONTRÉ:
- DBA: Gestion catalogue données enterprise + métadonnées
- Data Engineering: Architecture catalog distribué + discovery
- Backend Senior: Performance catalog <100ms + cache intelligent
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from pathlib import Path

# Configuration et logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAssetType(Enum):
    """Types d'assets de données"""
    TABLE = "table"
    VIEW = "view"
    DATASET = "dataset"
    MODEL = "model"
    PIPELINE = "pipeline"
    SCHEMA = "schema"
    API = "api"
    FILE = "file"

class DataClassification(Enum):
    """Classification de données selon sensitivity"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PERSONAL = "personal"  # GDPR

class DataQuality(Enum):
    """Niveaux de qualité des données"""
    EXCELLENT = "excellent"  # 95-100%
    GOOD = "good"           # 80-94%
    FAIR = "fair"           # 60-79%
    POOR = "poor"           # <60%

@dataclass
class DataAsset:
    """Asset de données dans le catalogue"""
    id: str
    name: str
    asset_type: DataAssetType
    description: str
    owner: str
    classification: DataClassification
    
    # Métadonnées techniques
    schema: Dict[str, Any] = field(default_factory=dict)
    location: str = ""
    size_bytes: int = 0
    row_count: int = 0
    column_count: int = 0
    
    # Métadonnées qualité
    quality_score: float = 0.0
    quality_level: DataQuality = DataQuality.FAIR
    last_validation: Optional[datetime] = None
    
    # Métadonnées business
    business_terms: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    domain: str = ""
    
    # Métadonnées lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    # Governance
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    retention_policy: Optional[str] = None
    data_lineage: List[str] = field(default_factory=list)
    
    # Relations
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataCatalogManager:
    """
    📊 Gestionnaire Enterprise de Catalogue de Données
    
    Expertise DBA + Data Engineering:
    - Catalogue centralisé avec métadonnées riches
    - Discovery et search avancés
    - Governance et compliance automatiques
    - Lineage tracking complet
    """
    
    def __init__(self, storage_path: str = "/tmp/data_catalog"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.assets: Dict[str, DataAsset] = {}
        self.search_index: Dict[str, List[str]] = {}  # terme -> asset_ids
        self.domain_index: Dict[str, List[str]] = {}  # domain -> asset_ids
        self.owner_index: Dict[str, List[str]] = {}   # owner -> asset_ids
        self.lineage_graph: Dict[str, Dict[str, List[str]]] = {}  # asset_id -> {upstream, downstream}
        
        # Cache pour performances
        self.search_cache: Dict[str, List[str]] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update: Dict[str, datetime] = {}
    
    async def register_asset(self, asset: DataAsset) -> bool:
        """
        Enregistre un asset dans le catalogue
        
        Expertise DBA: Validation schéma + contraintes intégrité
        """
        try:
            # Validation de l'asset
            if not asset.id or not asset.name:
                raise ValueError("Asset ID and name are required")
            
            if asset.id in self.assets:
                logger.warning(f"Asset {asset.id} already exists, updating")
            
            # Enrichissement automatique
            await self._enrich_asset_metadata(asset)
            
            # Enregistrement
            self.assets[asset.id] = asset
            
            # Indexation pour search
            await self._index_asset(asset)
            
            # Mise à jour du graphe de lineage
            await self._update_lineage_graph(asset)
            
            # Persistance
            await self._persist_asset(asset)
            
            logger.info(f"Registered data asset: {asset.id} ({asset.name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register asset {asset.id}: {str(e)}")
            return False
    
    async def get_asset(self, asset_id: str) -> Optional[DataAsset]:
        """Récupère un asset par ID avec cache"""
        if asset_id in self.assets:
            # Mise à jour de l'accès
            asset = self.assets[asset_id]
            asset.last_accessed = datetime.utcnow()
            asset.access_count += 1
            return asset
        
        # Tentative de chargement depuis le stockage
        return await self._load_asset(asset_id)
    
    async def search_assets(
        self,
        query: str,
        asset_type: Optional[DataAssetType] = None,
        domain: Optional[str] = None,
        owner: Optional[str] = None,
        classification: Optional[DataClassification] = None,
        limit: int = 50
    ) -> List[DataAsset]:
        """
        Recherche avancée d'assets avec filtres
        
        Expertise Backend Senior: Performance search <100ms
        """
        cache_key = f"{query}_{asset_type}_{domain}_{owner}_{classification}_{limit}"
        
        # Vérification du cache
        if cache_key in self.search_cache:
            if (datetime.utcnow() - self.last_cache_update.get(cache_key, datetime.min)).total_seconds() < self.cache_ttl:
                asset_ids = self.search_cache[cache_key]
                return [self.assets[aid] for aid in asset_ids if aid in self.assets]
        
        matching_assets = []
        query_terms = query.lower().split() if query else []
        
        for asset in self.assets.values():
            match_score = 0
            
            # Correspondance texte
            if query_terms:
                text_content = f"{asset.name} {asset.description} {' '.join(asset.tags)} {' '.join(asset.business_terms)}".lower()
                for term in query_terms:
                    if term in text_content:
                        match_score += 1
            else:
                match_score = 1  # Pas de query = match pour filtres
            
            # Filtres
            if asset_type and asset.asset_type != asset_type:
                continue
            if domain and asset.domain != domain:
                continue
            if owner and asset.owner != owner:
                continue
            if classification and asset.classification != classification:
                continue
            
            if match_score > 0:
                matching_assets.append((asset, match_score))
        
        # Tri par score et limitation
        matching_assets.sort(key=lambda x: x[1], reverse=True)
        results = [asset for asset, _ in matching_assets[:limit]]
        
        # Mise en cache
        self.search_cache[cache_key] = [asset.id for asset in results]
        self.last_cache_update[cache_key] = datetime.utcnow()
        
        return results
    
    async def get_asset_lineage(
        self, 
        asset_id: str, 
        depth: int = 3,
        direction: str = "both"  # upstream, downstream, both
    ) -> Dict[str, Any]:
        """
        Récupère le lineage d'un asset
        
        Expertise Data Engineering: Graphe lineage complet
        """
        if asset_id not in self.assets:
            return {}
        
        lineage = {
            "asset_id": asset_id,
            "upstream": [],
            "downstream": [],
            "depth": depth
        }
        
        if direction in ["upstream", "both"]:
            lineage["upstream"] = await self._get_lineage_direction(
                asset_id, "upstream", depth
            )
        
        if direction in ["downstream", "both"]:
            lineage["downstream"] = await self._get_lineage_direction(
                asset_id, "downstream", depth
            )
        
        return lineage
    
    async def update_asset_quality(
        self, 
        asset_id: str, 
        quality_score: float,
        quality_details: Optional[Dict] = None
    ) -> bool:
        """Met à jour la qualité d'un asset"""
        if asset_id not in self.assets:
            return False
        
        asset = self.assets[asset_id]
        asset.quality_score = quality_score
        asset.last_validation = datetime.utcnow()
        
        # Déterminer le niveau de qualité
        if quality_score >= 0.95:
            asset.quality_level = DataQuality.EXCELLENT
        elif quality_score >= 0.80:
            asset.quality_level = DataQuality.GOOD
        elif quality_score >= 0.60:
            asset.quality_level = DataQuality.FAIR
        else:
            asset.quality_level = DataQuality.POOR
        
        if quality_details:
            asset.metadata["quality_details"] = quality_details
        
        await self._persist_asset(asset)
        logger.info(f"Updated quality for asset {asset_id}: {quality_score:.2f}")
        return True
    
    async def get_domain_overview(self, domain: str) -> Dict[str, Any]:
        """Vue d'ensemble d'un domaine de données"""
        domain_assets = [
            asset for asset in self.assets.values() 
            if asset.domain == domain
        ]
        
        if not domain_assets:
            return {}
        
        # Statistiques du domaine
        total_size = sum(asset.size_bytes for asset in domain_assets)
        avg_quality = sum(asset.quality_score for asset in domain_assets) / len(domain_assets)
        
        # Distribution par type
        type_distribution = {}
        for asset in domain_assets:
            asset_type = asset.asset_type.value
            type_distribution[asset_type] = type_distribution.get(asset_type, 0) + 1
        
        # Distribution par classification
        classification_distribution = {}
        for asset in domain_assets:
            classification = asset.classification.value
            classification_distribution[classification] = classification_distribution.get(classification, 0) + 1
        
        # Assets récents
        recent_assets = sorted(
            domain_assets, 
            key=lambda x: x.updated_at, 
            reverse=True
        )[:10]
        
        return {
            "domain": domain,
            "total_assets": len(domain_assets),
            "total_size_bytes": total_size,
            "average_quality_score": avg_quality,
            "type_distribution": type_distribution,
            "classification_distribution": classification_distribution,
            "recent_assets": [
                {"id": asset.id, "name": asset.name, "updated_at": asset.updated_at}
                for asset in recent_assets
            ]
        }
    
    async def get_catalog_metrics(self) -> Dict[str, Any]:
        """Métriques globales du catalogue"""
        total_assets = len(self.assets)
        
        if total_assets == 0:
            return {"total_assets": 0}
        
        # Distribution par type
        type_distribution = {}
        quality_distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        classification_distribution = {}
        domain_distribution = {}
        
        total_size = 0
        total_quality = 0
        
        for asset in self.assets.values():
            # Type
            asset_type = asset.asset_type.value
            type_distribution[asset_type] = type_distribution.get(asset_type, 0) + 1
            
            # Quality
            quality_distribution[asset.quality_level.value] += 1
            total_quality += asset.quality_score
            
            # Classification
            classification = asset.classification.value
            classification_distribution[classification] = classification_distribution.get(classification, 0) + 1
            
            # Domain
            if asset.domain:
                domain_distribution[asset.domain] = domain_distribution.get(asset.domain, 0) + 1
            
            # Size
            total_size += asset.size_bytes
        
        # Assets les plus accédés
        most_accessed = sorted(
            self.assets.values(),
            key=lambda x: x.access_count,
            reverse=True
        )[:10]
        
        return {
            "total_assets": total_assets,
            "total_size_bytes": total_size,
            "average_quality_score": total_quality / total_assets,
            "type_distribution": type_distribution,
            "quality_distribution": quality_distribution,
            "classification_distribution": classification_distribution,
            "domain_distribution": domain_distribution,
            "most_accessed_assets": [
                {
                    "id": asset.id,
                    "name": asset.name,
                    "access_count": asset.access_count,
                    "last_accessed": asset.last_accessed
                }
                for asset in most_accessed
            ]
        }
    
    async def validate_compliance(
        self, 
        regulations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Validation de conformité pour regulations
        
        Expertise Sécurité: Conformité GDPR/SOX/PCI
        """
        if not regulations:
            regulations = ["GDPR", "SOX", "PCI"]
        
        compliance_report = {
            "total_assets": len(self.assets),
            "regulations": {},
            "non_compliant_assets": [],
            "overall_compliance": True
        }
        
        for regulation in regulations:
            compliant_count = 0
            non_compliant_assets = []
            
            for asset in self.assets.values():
                is_compliant = asset.compliance_status.get(regulation, False)
                
                if is_compliant:
                    compliant_count += 1
                else:
                    non_compliant_assets.append({
                        "id": asset.id,
                        "name": asset.name,
                        "classification": asset.classification.value,
                        "reason": self._get_compliance_reason(asset, regulation)
                    })
            
            compliance_rate = compliant_count / len(self.assets) if self.assets else 0
            
            compliance_report["regulations"][regulation] = {
                "compliant_assets": compliant_count,
                "compliance_rate": compliance_rate,
                "non_compliant_assets": non_compliant_assets
            }
            
            if compliance_rate < 1.0:
                compliance_report["overall_compliance"] = False
        
        return compliance_report
    
    async def _enrich_asset_metadata(self, asset: DataAsset) -> None:
        """Enrichit automatiquement les métadonnées d'un asset"""
        # Auto-classification basée sur le nom et description
        if asset.classification == DataClassification.INTERNAL:  # Valeur par défaut
            content = f"{asset.name} {asset.description}".lower()
            
            if any(term in content for term in ["personal", "user", "customer", "email"]):
                asset.classification = DataClassification.PERSONAL
            elif any(term in content for term in ["secret", "key", "password", "token"]):
                asset.classification = DataClassification.RESTRICTED
            elif any(term in content for term in ["confidential", "sensitive", "private"]):
                asset.classification = DataClassification.CONFIDENTIAL
            elif any(term in content for term in ["public", "open", "general"]):
                asset.classification = DataClassification.PUBLIC
        
        # Auto-tagging basé sur le contenu
        content = f"{asset.name} {asset.description}".lower()
        auto_tags = []
        
        if "ml" in content or "model" in content:
            auto_tags.append("machine-learning")
        if "user" in content or "customer" in content:
            auto_tags.append("user-data")
        if "transaction" in content or "payment" in content:
            auto_tags.append("financial")
        if "log" in content or "event" in content:
            auto_tags.append("logging")
        
        asset.tags.extend([tag for tag in auto_tags if tag not in asset.tags])
        
        # Détermination du domaine si pas défini
        if not asset.domain:
            if any(term in content for term in ["user", "customer", "profile"]):
                asset.domain = "customer"
            elif any(term in content for term in ["product", "catalog", "inventory"]):
                asset.domain = "product"
            elif any(term in content for term in ["order", "transaction", "payment"]):
                asset.domain = "commerce"
            elif any(term in content for term in ["ml", "model", "prediction"]):
                asset.domain = "machine-learning"
            else:
                asset.domain = "general"
    
    async def _index_asset(self, asset: DataAsset) -> None:
        """Indexe un asset pour la recherche"""
        # Index par terme
        searchable_terms = (
            asset.name.lower().split() +
            asset.description.lower().split() +
            [tag.lower() for tag in asset.tags] +
            [term.lower() for term in asset.business_terms]
        )
        
        for term in searchable_terms:
            if term not in self.search_index:
                self.search_index[term] = []
            if asset.id not in self.search_index[term]:
                self.search_index[term].append(asset.id)
        
        # Index par domaine
        if asset.domain:
            if asset.domain not in self.domain_index:
                self.domain_index[asset.domain] = []
            if asset.id not in self.domain_index[asset.domain]:
                self.domain_index[asset.domain].append(asset.id)
        
        # Index par owner
        if asset.owner not in self.owner_index:
            self.owner_index[asset.owner] = []
        if asset.id not in self.owner_index[asset.owner]:
            self.owner_index[asset.owner].append(asset.id)
    
    async def _update_lineage_graph(self, asset: DataAsset) -> None:
        """Met à jour le graphe de lineage"""
        if asset.id not in self.lineage_graph:
            self.lineage_graph[asset.id] = {"upstream": [], "downstream": []}
        
        # Upstream dependencies
        for dep_id in asset.dependencies:
            if dep_id not in self.lineage_graph:
                self.lineage_graph[dep_id] = {"upstream": [], "downstream": []}
            
            # asset dépend de dep_id
            if dep_id not in self.lineage_graph[asset.id]["upstream"]:
                self.lineage_graph[asset.id]["upstream"].append(dep_id)
            
            # dep_id a asset comme downstream
            if asset.id not in self.lineage_graph[dep_id]["downstream"]:
                self.lineage_graph[dep_id]["downstream"].append(asset.id)
    
    async def _get_lineage_direction(
        self, 
        asset_id: str, 
        direction: str, 
        depth: int,
        visited: set = None
    ) -> List[Dict[str, Any]]:
        """Récupère le lineage dans une direction avec protection contre les cycles"""
        if visited is None:
            visited = set()
        
        if depth == 0 or asset_id in visited or asset_id not in self.lineage_graph:
            return []
        
        visited.add(asset_id)
        lineage = []
        
        related_ids = self.lineage_graph[asset_id].get(direction, [])
        
        for related_id in related_ids:
            if related_id in self.assets:
                related_asset = self.assets[related_id]
                lineage_item = {
                    "id": related_id,
                    "name": related_asset.name,
                    "type": related_asset.asset_type.value,
                    "depth": depth
                }
                
                # Récursion pour les niveaux suivants
                if depth > 1:
                    lineage_item[direction] = await self._get_lineage_direction(
                        related_id, direction, depth - 1, visited.copy()
                    )
                
                lineage.append(lineage_item)
        
        return lineage
    
    def _get_compliance_reason(self, asset: DataAsset, regulation: str) -> str:
        """Détermine la raison de non-conformité"""
        if regulation == "GDPR" and asset.classification == DataClassification.PERSONAL:
            if not asset.retention_policy:
                return "Missing retention policy for personal data"
            if "consent" not in asset.metadata:
                return "Missing consent information"
        
        elif regulation == "SOX" and asset.domain == "financial":
            if not asset.metadata.get("audit_trail", False):
                return "Missing audit trail for financial data"
        
        elif regulation == "PCI" and "payment" in asset.name.lower():
            if asset.classification != DataClassification.RESTRICTED:
                return "Payment data should be classified as restricted"
        
        return "General compliance check failed"
    
    async def _persist_asset(self, asset: DataAsset) -> None:
        """Persiste un asset sur disque"""
        asset_file = self.storage_path / f"{asset.id}.json"
        
        # Sérialisation avec gestion des types spéciaux
        asset_data = {
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type.value,
            "description": asset.description,
            "owner": asset.owner,
            "classification": asset.classification.value,
            "schema": asset.schema,
            "location": asset.location,
            "size_bytes": asset.size_bytes,
            "row_count": asset.row_count,
            "column_count": asset.column_count,
            "quality_score": asset.quality_score,
            "quality_level": asset.quality_level.value,
            "last_validation": asset.last_validation.isoformat() if asset.last_validation else None,
            "business_terms": asset.business_terms,
            "tags": asset.tags,
            "domain": asset.domain,
            "created_at": asset.created_at.isoformat(),
            "updated_at": asset.updated_at.isoformat(),
            "last_accessed": asset.last_accessed.isoformat() if asset.last_accessed else None,
            "access_count": asset.access_count,
            "compliance_status": asset.compliance_status,
            "retention_policy": asset.retention_policy,
            "data_lineage": asset.data_lineage,
            "dependencies": asset.dependencies,
            "dependents": asset.dependents,
            "metadata": asset.metadata
        }
        
        with open(asset_file, 'w') as f:
            json.dump(asset_data, f, indent=2)
    
    async def _load_asset(self, asset_id: str) -> Optional[DataAsset]:
        """Charge un asset depuis le disque"""
        asset_file = self.storage_path / f"{asset_id}.json"
        
        if not asset_file.exists():
            return None
        
        try:
            with open(asset_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruction de l'asset
            asset = DataAsset(
                id=data["id"],
                name=data["name"],
                asset_type=DataAssetType(data["asset_type"]),
                description=data["description"],
                owner=data["owner"],
                classification=DataClassification(data["classification"]),
                schema=data["schema"],
                location=data["location"],
                size_bytes=data["size_bytes"],
                row_count=data["row_count"],
                column_count=data["column_count"],
                quality_score=data["quality_score"],
                quality_level=DataQuality(data["quality_level"]),
                business_terms=data["business_terms"],
                tags=data["tags"],
                domain=data["domain"],
                access_count=data["access_count"],
                compliance_status=data["compliance_status"],
                retention_policy=data["retention_policy"],
                data_lineage=data["data_lineage"],
                dependencies=data["dependencies"],
                dependents=data["dependents"],
                metadata=data["metadata"]
            )
            
            # Reconstruction des dates
            asset.created_at = datetime.fromisoformat(data["created_at"])
            asset.updated_at = datetime.fromisoformat(data["updated_at"])
            if data["last_validation"]:
                asset.last_validation = datetime.fromisoformat(data["last_validation"])
            if data["last_accessed"]:
                asset.last_accessed = datetime.fromisoformat(data["last_accessed"])
            
            self.assets[asset_id] = asset
            await self._index_asset(asset)
            
            return asset
            
        except Exception as e:
            logger.error(f"Failed to load asset {asset_id}: {str(e)}")
            return None

# Exemple d'utilisation enterprise
async def demo_data_catalog():
    """Démo du catalogue de données enterprise"""
    catalog = DataCatalogManager()
    
    # Créer des assets d'exemple
    user_table = DataAsset(
        id="users_table",
        name="Users Table",
        asset_type=DataAssetType.TABLE,
        description="Main users table with personal information",
        owner="data-team@company.com",
        classification=DataClassification.PERSONAL,
        domain="customer",
        schema={"id": "int", "email": "string", "name": "string"},
        row_count=1000000,
        column_count=3,
        quality_score=0.92,
        tags=["users", "personal", "customer"],
        business_terms=["customer", "profile"]
    )
    
    ml_model = DataAsset(
        id="recommendation_model",
        name="Product Recommendation Model",
        asset_type=DataAssetType.MODEL,
        description="ML model for product recommendations",
        owner="ml-team@company.com",
        classification=DataClassification.INTERNAL,
        domain="machine-learning",
        dependencies=["users_table", "products_table"],
        quality_score=0.89,
        tags=["ml", "recommendation", "model"],
        business_terms=["recommendation", "personalization"]
    )
    
    # Enregistrer les assets
    await catalog.register_asset(user_table)
    await catalog.register_asset(ml_model)
    
    # Recherche
    search_results = await catalog.search_assets("user", limit=10)
    print(f"Search results: {len(search_results)} assets found")
    
    # Lineage
    lineage = await catalog.get_asset_lineage("recommendation_model")
    print(f"Model lineage: {json.dumps(lineage, indent=2, default=str)}")
    
    # Métriques
    metrics = await catalog.get_catalog_metrics()
    print(f"Catalog metrics: {json.dumps(metrics, indent=2, default=str)}")
    
    # Compliance
    compliance = await catalog.validate_compliance(["GDPR"])
    print(f"GDPR compliance: {compliance['overall_compliance']}")

if __name__ == "__main__":
    asyncio.run(demo_data_catalog())