"""📊 Indexing Strategies Manager - Advanced Index Management & ML-Driven Optimization
==================================================================================

ML-driven indexing strategies for optimal query performance with intelligent index
creation, maintenance, and optimization recommendations.

Expert Roles Implementation:
🧠 ML Engineer: ML-driven index recommendations + pattern analysis + predictive modeling
🗄️ DBA Senior: Index optimization + maintenance strategies + performance tuning
🏗️ Backend Senior: Index integration + query optimization + performance patterns
⚡ Performance: Index monitoring + performance metrics + optimization analytics
🤖 Lead Dev IA: AI-powered index selection + automated optimization + smart recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0 Enterprise Production
Date: December 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture indexing strategies est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import hashlib
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import math

logger = logging.getLogger(__name__)

class IndexType(Enum):
    """Types d'index supportés pour l'optimisation."""
    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    BRIN = "brin"
    PARTIAL = "partial"
    COMPOSITE = "composite"
    COVERING = "covering"
    UNIQUE = "unique"
    FUNCTIONAL = "functional"

class IndexCategory(Enum):
    """Catégories d'index selon l'usage."""
    PRIMARY = "primary"
    FOREIGN_KEY = "foreign_key"
    SEARCH = "search"
    SORTING = "sorting"
    FILTERING = "filtering"
    AGGREGATION = "aggregation"
    JOIN_OPTIMIZATION = "join_optimization"
    FULL_TEXT = "full_text"

class IndexPriority(Enum):
    """Priorités de création d'index."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MAINTENANCE = "maintenance"

class MaintenanceAction(Enum):
    """Actions de maintenance sur les index."""
    REBUILD = "rebuild"
    REORGANIZE = "reorganize"
    ANALYZE = "analyze"
    DROP = "drop"
    MODIFY = "modify"

@dataclass
class TableSchema:
    """Schéma d'une table pour l'analyse d'index."""
    table_name: str
    columns: Dict[str, str]  # column_name -> data_type
    row_count: int
    table_size_mb: float
    primary_keys: List[str]
    foreign_keys: Dict[str, str]  # column -> referenced_table.column
    constraints: List[str]

@dataclass
class QueryPattern:
    """Pattern de requête pour l'analyse d'index."""
    pattern_id: str
    query_type: str
    tables: List[str]
    where_columns: List[str]
    order_by_columns: List[str]
    join_columns: List[str]
    group_by_columns: List[str]
    frequency: int
    avg_execution_time: float
    selectivity: float  # Pourcentage de lignes retournées

@dataclass
class ExistingIndex:
    """Index existant dans la base de données."""
    index_name: str
    table_name: str
    columns: List[str]
    index_type: IndexType
    is_unique: bool
    size_mb: float
    usage_count: int
    last_used: Optional[datetime]
    creation_date: datetime
    fragmentation_percent: float
    maintenance_needed: bool

@dataclass
class IndexRecommendation:
    """Recommandation d'index avec justification ML."""
    table_name: str
    columns: List[str]
    index_type: IndexType
    index_category: IndexCategory
    priority: IndexPriority
    estimated_benefit: float  # 0-1 score
    estimated_cost: float    # Storage cost in MB
    impact_queries: List[str]  # Query patterns impacted
    confidence_score: float  # 0-1 ML confidence
    justification: str
    sql_statement: str

@dataclass
class IndexPerformanceMetrics:
    """Métriques de performance d'un index."""
    index_name: str
    table_name: str
    total_scans: int
    total_seeks: int
    total_lookups: int
    user_updates: int
    system_updates: int
    hit_ratio: float
    avg_fragment_percent: float
    page_count: int
    size_kb: float
    last_user_seek: Optional[datetime]
    last_user_scan: Optional[datetime]

class IndexingStrategiesManager:
    """📊 Gestionnaire intelligent des stratégies d'indexation avec ML."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire d'indexation."""
        self.config = config or {}
        
        # Configuration ML
        self.ml_enabled = self.config.get("ml_enabled", True)
        self.learning_threshold = self.config.get("learning_threshold", 100)
        self.min_confidence_score = self.config.get("min_confidence_score", 0.7)
        
        # Stores
        self.table_schemas: Dict[str, TableSchema] = {}
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.existing_indexes: Dict[str, ExistingIndex] = {}
        self.performance_metrics: Dict[str, IndexPerformanceMetrics] = {}
        
        # ML Models (simplified for demonstration)
        self.pattern_weights = {
            "frequency_weight": 0.3,
            "execution_time_weight": 0.25,
            "selectivity_weight": 0.2,
            "table_size_weight": 0.15,
            "cardinality_weight": 0.1
        }
        
        # Statistics
        self.analytics = {
            "recommendations_generated": 0,
            "indexes_analyzed": 0,
            "performance_improvements": 0.0,
            "storage_optimization": 0.0
        }
        
        logger.info("Indexing Strategies Manager initialized with ML capabilities")

    async def analyze_table_schema(self, table_info: Dict[str, Any]) -> TableSchema:
        """🔍 Analyse le schéma d'une table pour l'optimisation d'index."""
        table_name = table_info["table_name"]
        
        schema = TableSchema(
            table_name=table_name,
            columns=table_info.get("columns", {}),
            row_count=table_info.get("row_count", 0),
            table_size_mb=table_info.get("table_size_mb", 0.0),
            primary_keys=table_info.get("primary_keys", []),
            foreign_keys=table_info.get("foreign_keys", {}),
            constraints=table_info.get("constraints", [])
        )
        
        self.table_schemas[table_name] = schema
        
        logger.debug(f"Table schema analyzed: {table_name} ({schema.row_count} rows)")
        return schema

    async def analyze_query_patterns(self, query_data: List[Dict[str, Any]]) -> List[QueryPattern]:
        """🧠 Analyse les patterns de requêtes avec ML pour identifier les besoins d'index."""
        patterns = []
        
        for query_info in query_data:
            pattern_id = self._generate_pattern_id(query_info)
            
            pattern = QueryPattern(
                pattern_id=pattern_id,
                query_type=query_info.get("query_type", "SELECT"),
                tables=query_info.get("tables", []),
                where_columns=query_info.get("where_columns", []),
                order_by_columns=query_info.get("order_by_columns", []),
                join_columns=query_info.get("join_columns", []),
                group_by_columns=query_info.get("group_by_columns", []),
                frequency=query_info.get("frequency", 1),
                avg_execution_time=query_info.get("avg_execution_time", 0.0),
                selectivity=query_info.get("selectivity", 0.5)
            )
            
            self.query_patterns[pattern_id] = pattern
            patterns.append(pattern)
        
        logger.info(f"Analyzed {len(patterns)} query patterns")
        return patterns

    async def generate_index_recommendations(self, 
                                           table_name: Optional[str] = None) -> List[IndexRecommendation]:
        """🎯 Génère des recommandations d'index basées sur l'analyse ML."""
        recommendations = []
        
        # Determine tables to analyze
        tables_to_analyze = [table_name] if table_name else list(self.table_schemas.keys())
        
        for table in tables_to_analyze:
            if table not in self.table_schemas:
                continue
                
            table_recommendations = await self._analyze_table_index_needs(table)
            recommendations.extend(table_recommendations)
        
        # Sort by priority and benefit
        recommendations.sort(key=lambda x: (x.priority.value, -x.estimated_benefit))
        
        self.analytics["recommendations_generated"] += len(recommendations)
        
        logger.info(f"Generated {len(recommendations)} index recommendations")
        return recommendations

    async def analyze_existing_indexes(self, index_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """📈 Analyse les index existants pour l'optimisation et la maintenance."""
        analysis_results = {
            "total_indexes": len(index_data),
            "unused_indexes": [],
            "fragmented_indexes": [],
            "duplicate_indexes": [],
            "maintenance_recommendations": [],
            "optimization_opportunities": []
        }
        
        # Process existing indexes
        for idx_info in index_data:
            index = ExistingIndex(
                index_name=idx_info["index_name"],
                table_name=idx_info["table_name"],
                columns=idx_info["columns"],
                index_type=IndexType(idx_info.get("index_type", "btree")),
                is_unique=idx_info.get("is_unique", False),
                size_mb=idx_info.get("size_mb", 0.0),
                usage_count=idx_info.get("usage_count", 0),
                last_used=idx_info.get("last_used"),
                creation_date=idx_info.get("creation_date", datetime.now()),
                fragmentation_percent=idx_info.get("fragmentation_percent", 0.0),
                maintenance_needed=idx_info.get("maintenance_needed", False)
            )
            
            self.existing_indexes[idx_info["index_name"]] = index
            
            # Analyze for issues
            if index.usage_count == 0:
                analysis_results["unused_indexes"].append(index.index_name)
            
            if index.fragmentation_percent > 30:
                analysis_results["fragmented_indexes"].append({
                    "index_name": index.index_name,
                    "fragmentation": index.fragmentation_percent
                })
        
        # Find duplicate indexes
        analysis_results["duplicate_indexes"] = self._find_duplicate_indexes()
        
        # Generate maintenance recommendations
        analysis_results["maintenance_recommendations"] = await self._generate_maintenance_recommendations()
        
        self.analytics["indexes_analyzed"] += len(index_data)
        
        return analysis_results

    async def optimize_index_usage(self, 
                                 performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """⚡ Optimise l'utilisation des index basé sur les métriques de performance."""
        optimization_results = {
            "performance_analysis": {},
            "usage_optimization": [],
            "storage_optimization": [],
            "query_performance_impact": {}
        }
        
        # Process performance metrics
        for perf_data in performance_data:
            metrics = IndexPerformanceMetrics(
                index_name=perf_data["index_name"],
                table_name=perf_data["table_name"],
                total_scans=perf_data.get("total_scans", 0),
                total_seeks=perf_data.get("total_seeks", 0),
                total_lookups=perf_data.get("total_lookups", 0),
                user_updates=perf_data.get("user_updates", 0),
                system_updates=perf_data.get("system_updates", 0),
                hit_ratio=perf_data.get("hit_ratio", 0.0),
                avg_fragment_percent=perf_data.get("avg_fragment_percent", 0.0),
                page_count=perf_data.get("page_count", 0),
                size_kb=perf_data.get("size_kb", 0.0),
                last_user_seek=perf_data.get("last_user_seek"),
                last_user_scan=perf_data.get("last_user_scan")
            )
            
            self.performance_metrics[perf_data["index_name"]] = metrics
            
            # Analyze performance
            optimization_results["performance_analysis"][metrics.index_name] = {
                "efficiency_score": self._calculate_index_efficiency(metrics),
                "usage_pattern": self._analyze_usage_pattern(metrics),
                "optimization_potential": self._calculate_optimization_potential(metrics)
            }
        
        # Generate optimization recommendations
        optimization_results["usage_optimization"] = self._generate_usage_optimizations()
        optimization_results["storage_optimization"] = self._generate_storage_optimizations()
        
        return optimization_results

    async def create_index_strategy(self, 
                                  recommendations: List[IndexRecommendation],
                                  auto_implement: bool = False) -> Dict[str, Any]:
        """🚀 Crée une stratégie d'implémentation d'index avec planification."""
        strategy = {
            "implementation_plan": [],
            "resource_requirements": {},
            "timeline_estimate": {},
            "risk_assessment": {},
            "rollback_plan": []
        }
        
        # Sort recommendations by priority and impact
        sorted_recs = sorted(recommendations, 
                           key=lambda x: (x.priority.value, -x.estimated_benefit))
        
        total_storage_mb = 0
        total_implementation_time = 0
        
        for i, rec in enumerate(sorted_recs):
            # Estimate implementation details
            impl_time = self._estimate_implementation_time(rec)
            storage_req = rec.estimated_cost
            
            implementation_step = {
                "step": i + 1,
                "index_name": f"ix_{rec.table_name}_{'_'.join(rec.columns)}",
                "table_name": rec.table_name,
                "columns": rec.columns,
                "index_type": rec.index_type.value,
                "priority": rec.priority.value,
                "estimated_benefit": rec.estimated_benefit,
                "storage_mb": storage_req,
                "implementation_time_minutes": impl_time,
                "sql_statement": rec.sql_statement,
                "dependencies": self._find_dependencies(rec),
                "risks": self._assess_risks(rec)
            }
            
            strategy["implementation_plan"].append(implementation_step)
            total_storage_mb += storage_req
            total_implementation_time += impl_time
        
        # Resource requirements
        strategy["resource_requirements"] = {
            "total_storage_mb": total_storage_mb,
            "peak_cpu_usage": "moderate",
            "io_impact": "high" if total_storage_mb > 1000 else "moderate",
            "maintenance_window_required": total_implementation_time > 30
        }
        
        # Timeline
        strategy["timeline_estimate"] = {
            "total_time_minutes": total_implementation_time,
            "phases": self._create_implementation_phases(sorted_recs),
            "recommended_schedule": "off_peak_hours"
        }
        
        return strategy

    def get_indexing_analytics(self) -> Dict[str, Any]:
        """📊 Retourne les analytics complètes d'indexation."""
        analytics = {
            "summary": self.analytics.copy(),
            "table_analysis": self._get_table_analytics(),
            "query_pattern_analysis": self._get_query_pattern_analytics(),
            "index_health": self._get_index_health_metrics(),
            "optimization_opportunities": self._identify_optimization_opportunities(),
            "performance_trends": self._calculate_performance_trends()
        }
        
        return analytics

    # Méthodes privées d'analyse ML

    async def _analyze_table_index_needs(self, table_name: str) -> List[IndexRecommendation]:
        """Analyse les besoins d'index pour une table spécifique."""
        recommendations = []
        table_schema = self.table_schemas[table_name]
        
        # Find relevant query patterns
        relevant_patterns = [
            pattern for pattern in self.query_patterns.values()
            if table_name in pattern.tables
        ]
        
        if not relevant_patterns:
            return recommendations
        
        # Analyze different types of index needs
        recommendations.extend(await self._analyze_where_clause_indexes(table_name, relevant_patterns))
        recommendations.extend(await self._analyze_join_indexes(table_name, relevant_patterns))
        recommendations.extend(await self._analyze_sorting_indexes(table_name, relevant_patterns))
        recommendations.extend(await self._analyze_covering_indexes(table_name, relevant_patterns))
        
        return recommendations

    async def _analyze_where_clause_indexes(self, 
                                          table_name: str, 
                                          patterns: List[QueryPattern]) -> List[IndexRecommendation]:
        """Analyse les besoins d'index pour les clauses WHERE."""
        recommendations = []
        column_usage = Counter()
        
        # Count usage of columns in WHERE clauses
        for pattern in patterns:
            for column in pattern.where_columns:
                column_usage[column] += pattern.frequency
        
        # Generate recommendations for most used columns
        for column, frequency in column_usage.most_common(5):
            if frequency >= self.config.get("min_where_frequency", 10):
                benefit_score = self._calculate_where_clause_benefit(column, frequency, patterns)
                
                if benefit_score > 0.3:
                    recommendation = IndexRecommendation(
                        table_name=table_name,
                        columns=[column],
                        index_type=self._recommend_index_type(column, "where"),
                        index_category=IndexCategory.FILTERING,
                        priority=self._calculate_priority(benefit_score),
                        estimated_benefit=benefit_score,
                        estimated_cost=self._estimate_index_storage_cost(table_name, [column]),
                        impact_queries=[p.pattern_id for p in patterns if column in p.where_columns],
                        confidence_score=min(0.9, frequency / 100),
                        justification=f"High frequency WHERE clause usage: {frequency} queries",
                        sql_statement=self._generate_create_index_sql(table_name, [column], "btree")
                    )
                    recommendations.append(recommendation)
        
        return recommendations

    async def _analyze_join_indexes(self, 
                                  table_name: str, 
                                  patterns: List[QueryPattern]) -> List[IndexRecommendation]:
        """Analyse les besoins d'index pour les JOINs."""
        recommendations = []
        join_columns = Counter()
        
        for pattern in patterns:
            for column in pattern.join_columns:
                join_columns[column] += pattern.frequency
        
        for column, frequency in join_columns.most_common(3):
            if frequency >= self.config.get("min_join_frequency", 5):
                benefit_score = self._calculate_join_benefit(column, frequency, patterns)
                
                recommendation = IndexRecommendation(
                    table_name=table_name,
                    columns=[column],
                    index_type=IndexType.BTREE,
                    index_category=IndexCategory.JOIN_OPTIMIZATION,
                    priority=self._calculate_priority(benefit_score),
                    estimated_benefit=benefit_score,
                    estimated_cost=self._estimate_index_storage_cost(table_name, [column]),
                    impact_queries=[p.pattern_id for p in patterns if column in p.join_columns],
                    confidence_score=min(0.8, frequency / 50),
                    justification=f"JOIN optimization for {frequency} query patterns",
                    sql_statement=self._generate_create_index_sql(table_name, [column], "btree")
                )
                recommendations.append(recommendation)
        
        return recommendations

    async def _analyze_sorting_indexes(self, 
                                     table_name: str, 
                                     patterns: List[QueryPattern]) -> List[IndexRecommendation]:
        """Analyse les besoins d'index pour les ORDER BY."""
        recommendations = []
        order_combinations = Counter()
        
        for pattern in patterns:
            if pattern.order_by_columns:
                combo_key = tuple(pattern.order_by_columns)
                order_combinations[combo_key] += pattern.frequency
        
        for columns, frequency in order_combinations.most_common(3):
            if frequency >= self.config.get("min_order_frequency", 5):
                benefit_score = self._calculate_sorting_benefit(columns, frequency, patterns)
                
                recommendation = IndexRecommendation(
                    table_name=table_name,
                    columns=list(columns),
                    index_type=IndexType.BTREE,
                    index_category=IndexCategory.SORTING,
                    priority=self._calculate_priority(benefit_score),
                    estimated_benefit=benefit_score,
                    estimated_cost=self._estimate_index_storage_cost(table_name, list(columns)),
                    impact_queries=[p.pattern_id for p in patterns if p.order_by_columns == list(columns)],
                    confidence_score=min(0.7, frequency / 30),
                    justification=f"ORDER BY optimization for {frequency} query patterns",
                    sql_statement=self._generate_create_index_sql(table_name, list(columns), "btree")
                )
                recommendations.append(recommendation)
        
        return recommendations

    async def _analyze_covering_indexes(self, 
                                      table_name: str, 
                                      patterns: List[QueryPattern]) -> List[IndexRecommendation]:
        """Analyse les opportunités d'index couvrants."""
        recommendations = []
        
        # Complex analysis for covering indexes would go here
        # This is a simplified version
        
        return recommendations

    def _calculate_where_clause_benefit(self, 
                                      column: str, 
                                      frequency: int, 
                                      patterns: List[QueryPattern]) -> float:
        """Calcule le bénéfice d'un index pour les clauses WHERE."""
        # Base benefit from frequency
        frequency_score = min(1.0, frequency / 100)
        
        # Selectivity consideration
        avg_selectivity = statistics.mean([
            p.selectivity for p in patterns 
            if column in p.where_columns
        ])
        selectivity_score = 1.0 - avg_selectivity  # Lower selectivity = higher benefit
        
        # Execution time impact
        avg_exec_time = statistics.mean([
            p.avg_execution_time for p in patterns 
            if column in p.where_columns
        ])
        time_score = min(1.0, avg_exec_time / 1000)  # Normalize to seconds
        
        # Weighted combination
        benefit = (
            frequency_score * self.pattern_weights["frequency_weight"] +
            selectivity_score * self.pattern_weights["selectivity_weight"] +
            time_score * self.pattern_weights["execution_time_weight"]
        )
        
        return min(1.0, benefit)

    def _calculate_join_benefit(self, 
                              column: str, 
                              frequency: int, 
                              patterns: List[QueryPattern]) -> float:
        """Calcule le bénéfice d'un index pour les JOINs."""
        frequency_score = min(1.0, frequency / 50)
        
        # Join complexity factor
        avg_join_complexity = statistics.mean([
            len(p.join_columns) for p in patterns 
            if column in p.join_columns
        ])
        complexity_score = min(1.0, avg_join_complexity / 5)
        
        return (frequency_score * 0.6 + complexity_score * 0.4)

    def _calculate_sorting_benefit(self, 
                                 columns: Tuple[str, ...], 
                                 frequency: int, 
                                 patterns: List[QueryPattern]) -> float:
        """Calcule le bénéfice d'un index pour le tri."""
        frequency_score = min(1.0, frequency / 30)
        
        # Column count factor (more columns = higher benefit for composite index)
        column_score = min(1.0, len(columns) / 3)
        
        return (frequency_score * 0.7 + column_score * 0.3)

    def _recommend_index_type(self, column: str, usage_type: str) -> IndexType:
        """Recommande le type d'index optimal."""
        # Simplified logic - in practice would consider data types, cardinality, etc.
        if usage_type == "where":
            return IndexType.BTREE
        elif usage_type == "text_search":
            return IndexType.GIN
        elif usage_type == "equality_only":
            return IndexType.HASH
        else:
            return IndexType.BTREE

    def _calculate_priority(self, benefit_score: float) -> IndexPriority:
        """Calcule la priorité basée sur le score de bénéfice."""
        if benefit_score >= 0.8:
            return IndexPriority.CRITICAL
        elif benefit_score >= 0.6:
            return IndexPriority.HIGH
        elif benefit_score >= 0.4:
            return IndexPriority.MEDIUM
        else:
            return IndexPriority.LOW

    def _estimate_index_storage_cost(self, table_name: str, columns: List[str]) -> float:
        """Estime le coût de stockage d'un index."""
        if table_name not in self.table_schemas:
            return 10.0  # Default estimate
        
        table = self.table_schemas[table_name]
        
        # Base cost calculation
        row_count = table.row_count
        column_count = len(columns)
        
        # Estimate bytes per row for index
        bytes_per_row = column_count * 8  # Simplified
        
        # Total size in MB
        total_bytes = row_count * bytes_per_row
        size_mb = total_bytes / (1024 * 1024)
        
        return max(1.0, size_mb)

    def _generate_create_index_sql(self, 
                                 table_name: str, 
                                 columns: List[str], 
                                 index_type: str) -> str:
        """Génère le SQL de création d'index."""
        index_name = f"ix_{table_name}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        
        sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
        
        if index_type.lower() != "btree":
            sql += f" USING {index_type.upper()}"
        
        return sql

    def _generate_pattern_id(self, query_info: Dict[str, Any]) -> str:
        """Génère un ID unique pour un pattern de requête."""
        pattern_str = f"{query_info.get('query_type', '')}_{','.join(query_info.get('tables', []))}"
        return hashlib.md5(pattern_str.encode()).hexdigest()[:12]

    def _find_duplicate_indexes(self) -> List[Dict[str, Any]]:
        """Trouve les index dupliqués ou redondants."""
        duplicates = []
        
        # Group indexes by table and columns
        index_groups = defaultdict(list)
        for index in self.existing_indexes.values():
            key = (index.table_name, tuple(sorted(index.columns)))
            index_groups[key].append(index)
        
        # Find groups with multiple indexes
        for key, indexes in index_groups.items():
            if len(indexes) > 1:
                duplicates.append({
                    "table_name": key[0],
                    "columns": list(key[1]),
                    "duplicate_indexes": [idx.index_name for idx in indexes]
                })
        
        return duplicates

    async def _generate_maintenance_recommendations(self) -> List[Dict[str, Any]]:
        """Génère des recommandations de maintenance."""
        recommendations = []
        
        for index in self.existing_indexes.values():
            if index.fragmentation_percent > 30:
                action = MaintenanceAction.REBUILD if index.fragmentation_percent > 50 else MaintenanceAction.REORGANIZE
                
                recommendations.append({
                    "index_name": index.index_name,
                    "table_name": index.table_name,
                    "action": action.value,
                    "reason": f"Fragmentation: {index.fragmentation_percent}%",
                    "priority": "high" if index.fragmentation_percent > 50 else "medium"
                })
        
        return recommendations

    def _calculate_index_efficiency(self, metrics: IndexPerformanceMetrics) -> float:
        """Calcule l'efficacité d'un index."""
        total_operations = metrics.total_scans + metrics.total_seeks
        if total_operations == 0:
            return 0.0
        
        seek_ratio = metrics.total_seeks / total_operations
        hit_ratio = metrics.hit_ratio
        
        efficiency = (seek_ratio * 0.6 + hit_ratio * 0.4)
        return min(1.0, efficiency)

    def _analyze_usage_pattern(self, metrics: IndexPerformanceMetrics) -> str:
        """Analyse le pattern d'utilisation d'un index."""
        total_ops = metrics.total_scans + metrics.total_seeks
        
        if total_ops == 0:
            return "unused"
        elif metrics.total_seeks > metrics.total_scans * 3:
            return "seek_heavy"
        elif metrics.total_scans > metrics.total_seeks * 3:
            return "scan_heavy"
        else:
            return "balanced"

    def _calculate_optimization_potential(self, metrics: IndexPerformanceMetrics) -> float:
        """Calcule le potentiel d'optimisation."""
        efficiency = self._calculate_index_efficiency(metrics)
        return 1.0 - efficiency

    def _generate_usage_optimizations(self) -> List[Dict[str, Any]]:
        """Génère des optimisations d'utilisation."""
        optimizations = []
        
        for metrics in self.performance_metrics.values():
            potential = self._calculate_optimization_potential(metrics)
            
            if potential > 0.3:
                optimizations.append({
                    "index_name": metrics.index_name,
                    "optimization_type": "usage_pattern",
                    "potential_improvement": potential,
                    "recommendation": self._get_usage_recommendation(metrics)
                })
        
        return optimizations

    def _generate_storage_optimizations(self) -> List[Dict[str, Any]]:
        """Génère des optimisations de stockage."""
        optimizations = []
        
        # Find large, rarely used indexes
        for metrics in self.performance_metrics.values():
            if metrics.size_kb > 10000:  # > 10MB
                total_ops = metrics.total_scans + metrics.total_seeks
                if total_ops < 100:  # Low usage
                    optimizations.append({
                        "index_name": metrics.index_name,
                        "optimization_type": "storage",
                        "size_kb": metrics.size_kb,
                        "usage_count": total_ops,
                        "recommendation": "Consider dropping or archiving"
                    })
        
        return optimizations

    def _get_usage_recommendation(self, metrics: IndexPerformanceMetrics) -> str:
        """Recommande des améliorations d'utilisation."""
        pattern = self._analyze_usage_pattern(metrics)
        
        if pattern == "unused":
            return "Consider dropping this index"
        elif pattern == "scan_heavy":
            return "Review queries using this index - may need covering index"
        elif metrics.avg_fragment_percent > 30:
            return "Rebuild index to reduce fragmentation"
        else:
            return "Monitor performance trends"

    def _estimate_implementation_time(self, recommendation: IndexRecommendation) -> int:
        """Estime le temps d'implémentation en minutes."""
        base_time = 5  # 5 minutes base
        
        # Add time based on table size
        if recommendation.table_name in self.table_schemas:
            table = self.table_schemas[recommendation.table_name]
            size_factor = math.log10(max(1, table.row_count)) / 2
            base_time += int(size_factor * 10)
        
        # Add time for complex indexes
        if len(recommendation.columns) > 2:
            base_time += 10
        
        return base_time

    def _find_dependencies(self, recommendation: IndexRecommendation) -> List[str]:
        """Trouve les dépendances pour un index."""
        dependencies = []
        
        # Check for foreign key dependencies
        if recommendation.table_name in self.table_schemas:
            table = self.table_schemas[recommendation.table_name]
            for column in recommendation.columns:
                if column in table.foreign_keys:
                    dependencies.append(f"Foreign key: {column}")
        
        return dependencies

    def _assess_risks(self, recommendation: IndexRecommendation) -> List[str]:
        """Évalue les risques d'implémentation."""
        risks = []
        
        if recommendation.estimated_cost > 1000:  # > 1GB
            risks.append("Large storage requirement")
        
        if recommendation.priority == IndexPriority.CRITICAL:
            risks.append("High impact on system performance during creation")
        
        return risks

    def _create_implementation_phases(self, recommendations: List[IndexRecommendation]) -> List[Dict[str, Any]]:
        """Crée des phases d'implémentation."""
        phases = []
        
        # Phase 1: Critical indexes
        critical_recs = [r for r in recommendations if r.priority == IndexPriority.CRITICAL]
        if critical_recs:
            phases.append({
                "phase": 1,
                "name": "Critical Performance Indexes",
                "recommendations": len(critical_recs),
                "estimated_duration": sum(self._estimate_implementation_time(r) for r in critical_recs)
            })
        
        # Phase 2: High priority indexes
        high_recs = [r for r in recommendations if r.priority == IndexPriority.HIGH]
        if high_recs:
            phases.append({
                "phase": 2,
                "name": "High Priority Optimization",
                "recommendations": len(high_recs),
                "estimated_duration": sum(self._estimate_implementation_time(r) for r in high_recs)
            })
        
        return phases

    def _get_table_analytics(self) -> Dict[str, Any]:
        """Analytics par table."""
        analytics = {}
        
        for table_name, schema in self.table_schemas.items():
            analytics[table_name] = {
                "row_count": schema.row_count,
                "size_mb": schema.table_size_mb,
                "columns": len(schema.columns),
                "indexes_count": len([idx for idx in self.existing_indexes.values() 
                                    if idx.table_name == table_name]),
                "query_patterns": len([p for p in self.query_patterns.values() 
                                     if table_name in p.tables])
            }
        
        return analytics

    def _get_query_pattern_analytics(self) -> Dict[str, Any]:
        """Analytics des patterns de requêtes."""
        if not self.query_patterns:
            return {}
        
        patterns = list(self.query_patterns.values())
        
        return {
            "total_patterns": len(patterns),
            "avg_frequency": statistics.mean([p.frequency for p in patterns]),
            "avg_execution_time": statistics.mean([p.avg_execution_time for p in patterns]),
            "most_frequent_tables": Counter([
                table for p in patterns for table in p.tables
            ]).most_common(5)
        }

    def _get_index_health_metrics(self) -> Dict[str, Any]:
        """Métriques de santé des index."""
        if not self.existing_indexes:
            return {}
        
        indexes = list(self.existing_indexes.values())
        
        return {
            "total_indexes": len(indexes),
            "avg_fragmentation": statistics.mean([idx.fragmentation_percent for idx in indexes]),
            "unused_indexes": len([idx for idx in indexes if idx.usage_count == 0]),
            "large_indexes": len([idx for idx in indexes if idx.size_mb > 100]),
            "maintenance_needed": len([idx for idx in indexes if idx.maintenance_needed])
        }

    def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identifie les opportunités d'optimisation."""
        opportunities = []
        
        # High-frequency queries without indexes
        for pattern in self.query_patterns.values():
            if pattern.frequency > 20 and pattern.avg_execution_time > 100:
                opportunities.append({
                    "type": "missing_index",
                    "pattern_id": pattern.pattern_id,
                    "frequency": pattern.frequency,
                    "execution_time": pattern.avg_execution_time,
                    "recommendation": "Create indexes for high-frequency slow queries"
                })
        
        # Fragmented indexes
        for index in self.existing_indexes.values():
            if index.fragmentation_percent > 40:
                opportunities.append({
                    "type": "fragmented_index",
                    "index_name": index.index_name,
                    "fragmentation": index.fragmentation_percent,
                    "recommendation": "Rebuild or reorganize index"
                })
        
        return opportunities

    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calcule les tendances de performance."""
        # Simplified implementation
        return {
            "trend": "stable",
            "prediction": "maintain_current_strategy",
            "confidence": 0.7
        }


# Fonction d'initialisation
async def initialize_indexing_strategies_manager(config: Optional[Dict[str, Any]] = None) -> IndexingStrategiesManager:
    """🚀 Initialise le gestionnaire de stratégies d'indexation."""
    manager = IndexingStrategiesManager(config)
    logger.info("Indexing Strategies Manager ready for ML-driven index optimization")
    return manager


# Export des classes principales
__all__ = [
    "IndexingStrategiesManager",
    "IndexType",
    "IndexCategory",
    "IndexPriority",
    "MaintenanceAction",
    "TableSchema",
    "QueryPattern",
    "ExistingIndex",
    "IndexRecommendation",
    "IndexPerformanceMetrics",
    "initialize_indexing_strategies_manager"
]