"""🧠 Transaction Intelligence - AI-Powered Transaction Analytics Engine
========================================================================

Advanced transaction pattern analysis and predictive intelligence for Creator Economy.
ML-driven insights, anomaly detection, and behavioral analytics.

Performance Targets: < 50ms transaction analysis
Enterprise AI transaction intelligence with real-time pattern recognition.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from decimal import Decimal
from collections import defaultdict, deque
import statistics
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
import pandas as pd
import structlog

logger = structlog.get_logger(__name__)

class TransactionType(Enum):
    """Transaction type classification"""
    PAYMENT = "payment"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class AnomalyType(Enum):
    """Anomaly classification types"""
    AMOUNT_ANOMALY = "amount_anomaly"
    FREQUENCY_ANOMALY = "frequency_anomaly"
    PATTERN_ANOMALY = "pattern_anomaly"
    VELOCITY_ANOMALY = "velocity_anomaly"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"

class PatternType(Enum):
    """Transaction pattern types"""
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"
    TRENDING = "trending"
    IRREGULAR = "irregular"
    BURST = "burst"
    DECLINE = "decline"

@dataclass
class Transaction:
    """Transaction data model"""
    transaction_id: str
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    timestamp: datetime
    user_id: str
    merchant_id: str
    payment_method: str
    country: str
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransactionPattern:
    """Identified transaction pattern"""
    pattern_id: str
    pattern_type: PatternType
    description: str
    confidence: float
    frequency: str
    affected_transactions: List[str]
    pattern_data: Dict[str, Any]
    first_detected: datetime
    last_updated: datetime

@dataclass
class TransactionAnomaly:
    """Detected transaction anomaly"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: str  # "low", "medium", "high", "critical"
    confidence: float
    description: str
    affected_transactions: List[str]
    detected_at: datetime
    features: Dict[str, float]
    recommended_actions: List[str]

@dataclass
class IntelligenceInsight:
    """Transaction intelligence insight"""
    insight_id: str
    category: str
    title: str
    description: str
    impact: str  # "low", "medium", "high"
    confidence: float
    data_points: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime

class TransactionAnalyzer:
    """Core transaction analysis engine"""
    
    def __init__(self):
        self.transaction_buffer = deque(maxlen=50000)
        self.patterns_cache = {}
        self.anomaly_models = self._initialize_anomaly_models()
        
    def _initialize_anomaly_models(self) -> Dict[str, Any]:
        """Initialize ML models for anomaly detection"""
        return {
            'isolation_forest': IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            ),
            'dbscan': DBSCAN(eps=0.5, min_samples=5),
            'kmeans': KMeans(n_clusters=8, random_state=42)
        }
    
    async def analyze_transaction_patterns(
        self,
        transactions: List[Transaction],
        analysis_window: timedelta = timedelta(hours=24)
    ) -> List[TransactionPattern]:
        """Analyze transaction patterns using ML"""
        try:
            start_time = time.perf_counter()
            
            if not transactions:
                return []
            
            # Convert to DataFrame for analysis
            df = await self._transactions_to_dataframe(transactions)
            
            # Detect temporal patterns
            temporal_patterns = await self._detect_temporal_patterns(df)
            
            # Detect amount patterns
            amount_patterns = await self._detect_amount_patterns(df)
            
            # Detect frequency patterns
            frequency_patterns = await self._detect_frequency_patterns(df)
            
            # Detect behavioral patterns
            behavioral_patterns = await self._detect_behavioral_patterns(df)
            
            # Combine all patterns
            all_patterns = temporal_patterns + amount_patterns + frequency_patterns + behavioral_patterns
            
            # Filter and rank patterns
            significant_patterns = await self._filter_significant_patterns(all_patterns)
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Transaction patterns analyzed",
                transactions_count=len(transactions),
                patterns_found=len(significant_patterns),
                duration_ms=duration_ms
            )
            
            return significant_patterns
            
        except Exception as e:
            logger.error(f"Error analyzing transaction patterns: {e}")
            raise
    
    async def _transactions_to_dataframe(self, transactions: List[Transaction]) -> pd.DataFrame:
        """Convert transaction list to pandas DataFrame"""
        data = []
        for txn in transactions:
            data.append({
                'transaction_id': txn.transaction_id,
                'amount': float(txn.amount),
                'currency': txn.currency,
                'type': txn.transaction_type.value,
                'status': txn.status.value,
                'timestamp': txn.timestamp,
                'user_id': txn.user_id,
                'merchant_id': txn.merchant_id,
                'payment_method': txn.payment_method,
                'country': txn.country,
                'hour': txn.timestamp.hour,
                'day_of_week': txn.timestamp.weekday(),
                'day_of_month': txn.timestamp.day
            })
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    async def _detect_temporal_patterns(self, df: pd.DataFrame) -> List[TransactionPattern]:
        """Detect temporal transaction patterns"""
        patterns = []
        
        # Hourly patterns
        hourly_counts = df.groupby('hour').size()
        peak_hours = hourly_counts.nlargest(3).index.tolist()
        
        if len(peak_hours) > 0:
            patterns.append(TransactionPattern(
                pattern_id=f"temporal_hourly_{int(time.time())}",
                pattern_type=PatternType.CYCLICAL,
                description=f"Peak transaction hours: {', '.join(map(str, peak_hours))}",
                confidence=0.85,
                frequency="daily",
                affected_transactions=df[df['hour'].isin(peak_hours)]['transaction_id'].tolist(),
                pattern_data={'peak_hours': peak_hours, 'hourly_distribution': hourly_counts.to_dict()},
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow()
            ))
        
        # Weekly patterns
        weekly_counts = df.groupby('day_of_week').size()
        peak_days = weekly_counts.nlargest(2).index.tolist()
        
        if len(peak_days) > 0:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            peak_day_names = [day_names[day] for day in peak_days]
            
            patterns.append(TransactionPattern(
                pattern_id=f"temporal_weekly_{int(time.time())}",
                pattern_type=PatternType.CYCLICAL,
                description=f"Peak transaction days: {', '.join(peak_day_names)}",
                confidence=0.80,
                frequency="weekly",
                affected_transactions=df[df['day_of_week'].isin(peak_days)]['transaction_id'].tolist(),
                pattern_data={'peak_days': peak_days, 'weekly_distribution': weekly_counts.to_dict()},
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow()
            ))
        
        return patterns
    
    async def _detect_amount_patterns(self, df: pd.DataFrame) -> List[TransactionPattern]:
        """Detect amount-based transaction patterns"""
        patterns = []
        
        if df.empty:
            return patterns
        
        # Amount clustering
        amounts = df['amount'].values.reshape(-1, 1)
        scaler = StandardScaler()
        scaled_amounts = scaler.fit_transform(amounts)
        
        # K-means clustering for amount groups
        kmeans = KMeans(n_clusters=min(5, len(df)), random_state=42)
        clusters = kmeans.fit_predict(scaled_amounts)
        
        # Analyze clusters
        df_with_clusters = df.copy()
        df_with_clusters['amount_cluster'] = clusters
        
        for cluster_id in np.unique(clusters):
            cluster_data = df_with_clusters[df_with_clusters['amount_cluster'] == cluster_id]
            if len(cluster_data) >= 3:  # Minimum cluster size
                avg_amount = cluster_data['amount'].mean()
                std_amount = cluster_data['amount'].std()
                
                patterns.append(TransactionPattern(
                    pattern_id=f"amount_cluster_{cluster_id}_{int(time.time())}",
                    pattern_type=PatternType.CYCLICAL,
                    description=f"Amount cluster: ${avg_amount:.2f} ± ${std_amount:.2f}",
                    confidence=0.75,
                    frequency="ongoing",
                    affected_transactions=cluster_data['transaction_id'].tolist(),
                    pattern_data={
                        'cluster_id': int(cluster_id),
                        'avg_amount': float(avg_amount),
                        'std_amount': float(std_amount),
                        'transaction_count': len(cluster_data)
                    },
                    first_detected=datetime.utcnow(),
                    last_updated=datetime.utcnow()
                ))
        
        return patterns
    
    async def _detect_frequency_patterns(self, df: pd.DataFrame) -> List[TransactionPattern]:
        """Detect transaction frequency patterns"""
        patterns = []
        
        # User frequency patterns
        user_counts = df.groupby('user_id').size()
        high_frequency_users = user_counts[user_counts >= 5].index.tolist()
        
        if high_frequency_users:
            patterns.append(TransactionPattern(
                pattern_id=f"frequency_high_users_{int(time.time())}",
                pattern_type=PatternType.TRENDING,
                description=f"High-frequency users: {len(high_frequency_users)} users with 5+ transactions",
                confidence=0.90,
                frequency="ongoing",
                affected_transactions=df[df['user_id'].isin(high_frequency_users)]['transaction_id'].tolist(),
                pattern_data={
                    'high_frequency_users': high_frequency_users[:10],  # Top 10
                    'user_transaction_counts': user_counts.nlargest(10).to_dict()
                },
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow()
            ))
        
        # Merchant frequency patterns
        merchant_counts = df.groupby('merchant_id').size()
        top_merchants = merchant_counts.nlargest(5).index.tolist()
        
        if top_merchants:
            patterns.append(TransactionPattern(
                pattern_id=f"frequency_merchants_{int(time.time())}",
                pattern_type=PatternType.TRENDING,
                description=f"Top merchants by transaction volume",
                confidence=0.85,
                frequency="ongoing",
                affected_transactions=df[df['merchant_id'].isin(top_merchants)]['transaction_id'].tolist(),
                pattern_data={
                    'top_merchants': top_merchants,
                    'merchant_transaction_counts': merchant_counts.nlargest(5).to_dict()
                },
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow()
            ))
        
        return patterns
    
    async def _detect_behavioral_patterns(self, df: pd.DataFrame) -> List[TransactionPattern]:
        """Detect behavioral transaction patterns"""
        patterns = []
        
        # Payment method preferences
        payment_method_counts = df.groupby('payment_method').size()
        dominant_method = payment_method_counts.idxmax()
        dominant_percentage = (payment_method_counts.max() / len(df)) * 100
        
        if dominant_percentage > 60:  # Dominant payment method
            patterns.append(TransactionPattern(
                pattern_id=f"behavior_payment_method_{int(time.time())}",
                pattern_type=PatternType.TRENDING,
                description=f"Dominant payment method: {dominant_method} ({dominant_percentage:.1f}%)",
                confidence=0.80,
                frequency="ongoing",
                affected_transactions=df[df['payment_method'] == dominant_method]['transaction_id'].tolist(),
                pattern_data={
                    'dominant_method': dominant_method,
                    'percentage': float(dominant_percentage),
                    'method_distribution': payment_method_counts.to_dict()
                },
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow()
            ))
        
        # Geographic patterns
        country_counts = df.groupby('country').size()
        top_countries = country_counts.nlargest(3).index.tolist()
        
        if top_countries:
            patterns.append(TransactionPattern(
                pattern_id=f"behavior_geographic_{int(time.time())}",
                pattern_type=PatternType.TRENDING,
                description=f"Top transaction countries: {', '.join(top_countries)}",
                confidence=0.75,
                frequency="ongoing",
                affected_transactions=df[df['country'].isin(top_countries)]['transaction_id'].tolist(),
                pattern_data={
                    'top_countries': top_countries,
                    'country_distribution': country_counts.nlargest(5).to_dict()
                },
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow()
            ))
        
        return patterns
    
    async def _filter_significant_patterns(
        self,
        patterns: List[TransactionPattern]
    ) -> List[TransactionPattern]:
        """Filter and rank significant patterns"""
        # Filter by confidence threshold
        significant_patterns = [p for p in patterns if p.confidence >= 0.7]
        
        # Sort by confidence and affected transactions count
        significant_patterns.sort(
            key=lambda p: (p.confidence, len(p.affected_transactions)),
            reverse=True
        )
        
        return significant_patterns[:20]  # Top 20 patterns
    
    async def detect_transaction_anomalies(
        self,
        transactions: List[Transaction],
        sensitivity: float = 0.1
    ) -> List[TransactionAnomaly]:
        """Detect transaction anomalies using ML models"""
        try:
            start_time = time.perf_counter()
            
            if len(transactions) < 10:  # Need minimum data
                return []
            
            # Convert to feature matrix
            feature_matrix, feature_names, transaction_ids = await self._extract_features(transactions)
            
            # Detect anomalies using multiple methods
            isolation_anomalies = await self._detect_isolation_anomalies(
                feature_matrix, feature_names, transaction_ids, sensitivity
            )
            
            statistical_anomalies = await self._detect_statistical_anomalies(
                transactions, feature_matrix, feature_names, transaction_ids
            )
            
            # Combine and deduplicate anomalies
            all_anomalies = isolation_anomalies + statistical_anomalies
            unique_anomalies = await self._deduplicate_anomalies(all_anomalies)
            
            # Rank by severity and confidence
            ranked_anomalies = sorted(
                unique_anomalies,
                key=lambda a: (a.severity == "critical", a.confidence),
                reverse=True
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Transaction anomalies detected",
                transactions_count=len(transactions),
                anomalies_found=len(ranked_anomalies),
                duration_ms=duration_ms
            )
            
            return ranked_anomalies[:50]  # Top 50 anomalies
            
        except Exception as e:
            logger.error(f"Error detecting transaction anomalies: {e}")
            raise
    
    async def _extract_features(
        self,
        transactions: List[Transaction]
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """Extract features for anomaly detection"""
        features = []
        transaction_ids = []
        
        for txn in transactions:
            feature_vector = [
                float(txn.amount),
                txn.timestamp.hour,
                txn.timestamp.weekday(),
                len(txn.user_id),  # User ID length as proxy for user type
                hash(txn.payment_method) % 100,  # Payment method encoded
                hash(txn.country) % 100,  # Country encoded
                1 if txn.status == TransactionStatus.COMPLETED else 0,
                1 if txn.transaction_type == TransactionType.PAYMENT else 0
            ]
            
            features.append(feature_vector)
            transaction_ids.append(txn.transaction_id)
        
        feature_names = [
            'amount', 'hour', 'day_of_week', 'user_id_length',
            'payment_method_encoded', 'country_encoded',
            'is_completed', 'is_payment'
        ]
        
        return np.array(features), feature_names, transaction_ids
    
    async def _detect_isolation_anomalies(
        self,
        feature_matrix: np.ndarray,
        feature_names: List[str],
        transaction_ids: List[str],
        sensitivity: float
    ) -> List[TransactionAnomaly]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_matrix)
        
        # Fit isolation forest
        isolation_forest = IsolationForest(
            contamination=sensitivity,
            random_state=42,
            n_estimators=100
        )
        
        anomaly_labels = isolation_forest.fit_predict(scaled_features)
        anomaly_scores = isolation_forest.score_samples(scaled_features)
        
        # Process anomalies
        for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
            if label == -1:  # Anomaly detected
                confidence = min(0.95, abs(score) * 2)  # Convert score to confidence
                severity = self._determine_anomaly_severity(confidence, feature_matrix[i])
                
                # Identify most anomalous features
                feature_contributions = abs(scaled_features[i])
                top_features = np.argsort(feature_contributions)[-3:]
                
                anomaly = TransactionAnomaly(
                    anomaly_id=f"isolation_{transaction_ids[i]}_{int(time.time())}",
                    anomaly_type=AnomalyType.PATTERN_ANOMALY,
                    severity=severity,
                    confidence=confidence,
                    description=f"Isolation Forest anomaly - unusual pattern detected",
                    affected_transactions=[transaction_ids[i]],
                    detected_at=datetime.utcnow(),
                    features={
                        feature_names[j]: float(feature_matrix[i][j])
                        for j in top_features
                    },
                    recommended_actions=self._get_anomaly_recommendations(
                        AnomalyType.PATTERN_ANOMALY, severity
                    )
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_statistical_anomalies(
        self,
        transactions: List[Transaction],
        feature_matrix: np.ndarray,
        feature_names: List[str],
        transaction_ids: List[str]
    ) -> List[TransactionAnomaly]:
        """Detect statistical anomalies"""
        anomalies = []
        
        # Amount-based anomalies
        amounts = [float(txn.amount) for txn in transactions]
        if amounts:
            mean_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            for i, txn in enumerate(transactions):
                amount = float(txn.amount)
                z_score = abs((amount - mean_amount) / std_amount) if std_amount > 0 else 0
                
                if z_score > 3:  # Significant outlier
                    severity = "critical" if z_score > 5 else "high" if z_score > 4 else "medium"
                    confidence = min(0.95, z_score / 5)
                    
                    anomaly = TransactionAnomaly(
                        anomaly_id=f"amount_{transaction_ids[i]}_{int(time.time())}",
                        anomaly_type=AnomalyType.AMOUNT_ANOMALY,
                        severity=severity,
                        confidence=confidence,
                        description=f"Unusual transaction amount: ${amount:.2f} (z-score: {z_score:.2f})",
                        affected_transactions=[transaction_ids[i]],
                        detected_at=datetime.utcnow(),
                        features={'amount': amount, 'z_score': z_score, 'mean_amount': mean_amount},
                        recommended_actions=self._get_anomaly_recommendations(
                            AnomalyType.AMOUNT_ANOMALY, severity
                        )
                    )
                    
                    anomalies.append(anomaly)
        
        # Frequency-based anomalies
        user_transaction_counts = defaultdict(int)
        user_timestamps = defaultdict(list)
        
        for txn in transactions:
            user_transaction_counts[txn.user_id] += 1
            user_timestamps[txn.user_id].append(txn.timestamp)
        
        # Detect velocity anomalies
        for user_id, timestamps in user_timestamps.items():
            if len(timestamps) >= 5:  # Minimum for velocity analysis
                timestamps.sort()
                intervals = [
                    (timestamps[i+1] - timestamps[i]).total_seconds()
                    for i in range(len(timestamps)-1)
                ]
                
                avg_interval = statistics.mean(intervals)
                if avg_interval < 60:  # Less than 1 minute between transactions
                    severity = "critical" if avg_interval < 10 else "high"
                    confidence = max(0.7, 1 - (avg_interval / 60))
                    
                    user_transactions = [txn.transaction_id for txn in transactions if txn.user_id == user_id]
                    
                    anomaly = TransactionAnomaly(
                        anomaly_id=f"velocity_{user_id}_{int(time.time())}",
                        anomaly_type=AnomalyType.VELOCITY_ANOMALY,
                        severity=severity,
                        confidence=confidence,
                        description=f"High transaction velocity: {len(timestamps)} transactions, avg {avg_interval:.1f}s apart",
                        affected_transactions=user_transactions,
                        detected_at=datetime.utcnow(),
                        features={
                            'transaction_count': len(timestamps),
                            'avg_interval_seconds': avg_interval,
                            'user_id': user_id
                        },
                        recommended_actions=self._get_anomaly_recommendations(
                            AnomalyType.VELOCITY_ANOMALY, severity
                        )
                    )
                    
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _determine_anomaly_severity(self, confidence: float, features: np.ndarray) -> str:
        """Determine anomaly severity based on confidence and features"""
        if confidence > 0.9:
            return "critical"
        elif confidence > 0.8:
            return "high"
        elif confidence > 0.7:
            return "medium"
        else:
            return "low"
    
    def _get_anomaly_recommendations(
        self,
        anomaly_type: AnomalyType,
        severity: str
    ) -> List[str]:
        """Get recommendations for handling anomalies"""
        base_recommendations = {
            AnomalyType.AMOUNT_ANOMALY: [
                "Review transaction for potential fraud",
                "Verify customer identity",
                "Check payment method validity"
            ],
            AnomalyType.VELOCITY_ANOMALY: [
                "Implement rate limiting",
                "Verify user behavior",
                "Check for automated attacks"
            ],
            AnomalyType.PATTERN_ANOMALY: [
                "Investigate transaction pattern",
                "Review user behavior history",
                "Check for system irregularities"
            ]
        }
        
        recommendations = base_recommendations.get(anomaly_type, ["Review transaction"])
        
        if severity in ["critical", "high"]:
            recommendations.extend([
                "Consider temporary account suspension",
                "Alert fraud team immediately",
                "Increase monitoring frequency"
            ])
        
        return recommendations
    
    async def _deduplicate_anomalies(
        self,
        anomalies: List[TransactionAnomaly]
    ) -> List[TransactionAnomaly]:
        """Remove duplicate anomalies"""
        seen_transactions = set()
        unique_anomalies = []
        
        for anomaly in anomalies:
            transaction_key = tuple(sorted(anomaly.affected_transactions))
            if transaction_key not in seen_transactions:
                seen_transactions.add(transaction_key)
                unique_anomalies.append(anomaly)
        
        return unique_anomalies

class PatternRecognizer:
    """Advanced pattern recognition engine"""
    
    def __init__(self):
        self.pattern_models = {}
        self.pattern_history = deque(maxlen=1000)
        
    async def recognize_transaction_patterns(
        self,
        transactions: List[Transaction],
        pattern_types: List[PatternType] = None
    ) -> Dict[str, Any]:
        """Recognize complex transaction patterns"""
        try:
            start_time = time.perf_counter()
            
            pattern_types = pattern_types or list(PatternType)
            
            # Convert to time series data
            time_series = await self._create_time_series(transactions)
            
            recognized_patterns = {}
            
            # Recognize each pattern type
            for pattern_type in pattern_types:
                patterns = await self._recognize_pattern_type(
                    time_series, pattern_type, transactions
                )
                if patterns:
                    recognized_patterns[pattern_type.value] = patterns
            
            # Cross-pattern analysis
            cross_patterns = await self._analyze_cross_patterns(recognized_patterns)
            
            result = {
                "patterns_by_type": recognized_patterns,
                "cross_patterns": cross_patterns,
                "pattern_summary": await self._create_pattern_summary(recognized_patterns),
                "confidence_scores": await self._calculate_pattern_confidence(recognized_patterns)
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Transaction patterns recognized",
                pattern_types=len(recognized_patterns),
                cross_patterns=len(cross_patterns),
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error recognizing transaction patterns: {e}")
            raise
    
    async def _create_time_series(self, transactions: List[Transaction]) -> pd.DataFrame:
        """Create time series data from transactions"""
        if not transactions:
            return pd.DataFrame()
        
        # Group transactions by time periods
        df = pd.DataFrame([
            {
                'timestamp': txn.timestamp,
                'amount': float(txn.amount),
                'count': 1,
                'type': txn.transaction_type.value,
                'status': txn.status.value
            }
            for txn in transactions
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample to hourly data
        hourly_data = df.resample('H').agg({
            'amount': ['sum', 'mean', 'count'],
            'count': 'sum'
        }).fillna(0)
        
        # Flatten column names
        hourly_data.columns = ['_'.join(col).strip() for col in hourly_data.columns]
        
        return hourly_data
    
    async def _recognize_pattern_type(
        self,
        time_series: pd.DataFrame,
        pattern_type: PatternType,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Recognize specific pattern type"""
        if time_series.empty:
            return []
        
        patterns = []
        
        if pattern_type == PatternType.SEASONAL:
            patterns.extend(await self._detect_seasonal_patterns(time_series, transactions))
        elif pattern_type == PatternType.TRENDING:
            patterns.extend(await self._detect_trending_patterns(time_series, transactions))
        elif pattern_type == PatternType.CYCLICAL:
            patterns.extend(await self._detect_cyclical_patterns(time_series, transactions))
        elif pattern_type == PatternType.BURST:
            patterns.extend(await self._detect_burst_patterns(time_series, transactions))
        elif pattern_type == PatternType.DECLINE:
            patterns.extend(await self._detect_decline_patterns(time_series, transactions))
        
        return patterns
    
    async def _detect_seasonal_patterns(
        self,
        time_series: pd.DataFrame,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Detect seasonal transaction patterns"""
        patterns = []
        
        if len(time_series) < 24:  # Need at least 24 hours of data
            return patterns
        
        # Analyze hourly seasonality
        hourly_amounts = time_series['amount_sum'].groupby(time_series.index.hour).mean()
        
        # Find peak hours
        peak_threshold = hourly_amounts.mean() + hourly_amounts.std()
        peak_hours = hourly_amounts[hourly_amounts > peak_threshold].index.tolist()
        
        if peak_hours:
            patterns.append({
                'pattern_name': 'hourly_seasonality',
                'description': f'Peak transaction hours: {peak_hours}',
                'confidence': 0.8,
                'data': {
                    'peak_hours': peak_hours,
                    'hourly_distribution': hourly_amounts.to_dict()
                }
            })
        
        return patterns
    
    async def _detect_trending_patterns(
        self,
        time_series: pd.DataFrame,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Detect trending patterns"""
        patterns = []
        
        if len(time_series) < 12:  # Need minimum data points
            return patterns
        
        # Calculate trend in transaction amounts
        amounts = time_series['amount_sum'].values
        x = np.arange(len(amounts))
        
        # Linear regression for trend
        coeffs = np.polyfit(x, amounts, 1)
        slope = coeffs[0]
        
        # Determine trend significance
        amount_std = np.std(amounts)
        trend_significance = abs(slope) / amount_std if amount_std > 0 else 0
        
        if trend_significance > 0.1:  # Significant trend
            trend_direction = "increasing" if slope > 0 else "decreasing"
            confidence = min(0.95, trend_significance)
            
            patterns.append({
                'pattern_name': f'{trend_direction}_trend',
                'description': f'Transaction amounts are {trend_direction}',
                'confidence': confidence,
                'data': {
                    'slope': float(slope),
                    'trend_significance': float(trend_significance),
                    'direction': trend_direction
                }
            })
        
        return patterns
    
    async def _detect_cyclical_patterns(
        self,
        time_series: pd.DataFrame,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Detect cyclical patterns"""
        patterns = []
        
        # Simple cyclical detection based on peaks and valleys
        amounts = time_series['amount_sum'].values
        
        if len(amounts) < 24:  # Need enough data
            return patterns
        
        # Find local maxima and minima
        from scipy.signal import find_peaks
        
        peaks, _ = find_peaks(amounts, height=np.mean(amounts))
        valleys, _ = find_peaks(-amounts, height=-np.mean(amounts))
        
        if len(peaks) >= 2 and len(valleys) >= 2:
            # Calculate average cycle length
            peak_intervals = np.diff(peaks)
            valley_intervals = np.diff(valleys)
            
            if len(peak_intervals) > 0 and len(valley_intervals) > 0:
                avg_cycle_length = (np.mean(peak_intervals) + np.mean(valley_intervals)) / 2
                
                patterns.append({
                    'pattern_name': 'cyclical_pattern',
                    'description': f'Cyclical pattern with {avg_cycle_length:.1f} hour cycle',
                    'confidence': 0.75,
                    'data': {
                        'cycle_length_hours': float(avg_cycle_length),
                        'peaks': peaks.tolist(),
                        'valleys': valleys.tolist()
                    }
                })
        
        return patterns
    
    async def _detect_burst_patterns(
        self,
        time_series: pd.DataFrame,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Detect burst patterns (sudden spikes)"""
        patterns = []
        
        amounts = time_series['amount_sum'].values
        counts = time_series['count_sum'].values
        
        if len(amounts) < 6:
            return patterns
        
        # Detect spikes in transaction count
        mean_count = np.mean(counts)
        std_count = np.std(counts)
        
        burst_threshold = mean_count + 2 * std_count
        burst_indices = np.where(counts > burst_threshold)[0]
        
        if len(burst_indices) > 0:
            patterns.append({
                'pattern_name': 'transaction_burst',
                'description': f'Transaction bursts detected at {len(burst_indices)} time periods',
                'confidence': 0.85,
                'data': {
                    'burst_indices': burst_indices.tolist(),
                    'burst_threshold': float(burst_threshold),
                    'max_burst_count': float(np.max(counts[burst_indices]))
                }
            })
        
        return patterns
    
    async def _detect_decline_patterns(
        self,
        time_series: pd.DataFrame,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Detect decline patterns"""
        patterns = []
        
        amounts = time_series['amount_sum'].values
        
        if len(amounts) < 12:
            return patterns
        
        # Check for sustained decline
        recent_period = amounts[-6:]  # Last 6 hours
        earlier_period = amounts[-12:-6]  # Previous 6 hours
        
        if len(recent_period) == 6 and len(earlier_period) == 6:
            recent_avg = np.mean(recent_period)
            earlier_avg = np.mean(earlier_period)
            
            decline_percentage = (earlier_avg - recent_avg) / earlier_avg * 100 if earlier_avg > 0 else 0
            
            if decline_percentage > 20:  # 20% decline
                patterns.append({
                    'pattern_name': 'transaction_decline',
                    'description': f'Transaction decline of {decline_percentage:.1f}% detected',
                    'confidence': 0.80,
                    'data': {
                        'decline_percentage': float(decline_percentage),
                        'recent_avg': float(recent_avg),
                        'earlier_avg': float(earlier_avg)
                    }
                })
        
        return patterns
    
    async def _analyze_cross_patterns(
        self,
        recognized_patterns: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Analyze relationships between different pattern types"""
        cross_patterns = []
        
        # Check for correlation between trending and seasonal patterns
        if 'trending' in recognized_patterns and 'seasonal' in recognized_patterns:
            cross_patterns.append({
                'pattern_combination': 'trending_seasonal',
                'description': 'Trending pattern combined with seasonal behavior',
                'confidence': 0.7,
                'insight': 'Growth is occurring within established seasonal patterns'
            })
        
        # Check for burst patterns during specific times
        if 'burst' in recognized_patterns and 'cyclical' in recognized_patterns:
            cross_patterns.append({
                'pattern_combination': 'burst_cyclical',
                'description': 'Burst patterns occurring in cyclical intervals',
                'confidence': 0.75,
                'insight': 'Predictable high-activity periods identified'
            })
        
        return cross_patterns
    
    async def _create_pattern_summary(
        self,
        recognized_patterns: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Create summary of recognized patterns"""
        total_patterns = sum(len(patterns) for patterns in recognized_patterns.values())
        
        pattern_types = list(recognized_patterns.keys())
        high_confidence_patterns = sum(
            1 for patterns in recognized_patterns.values()
            for pattern in patterns
            if pattern.get('confidence', 0) > 0.8
        )
        
        return {
            'total_patterns': total_patterns,
            'pattern_types': pattern_types,
            'high_confidence_patterns': high_confidence_patterns,
            'most_common_type': max(recognized_patterns.keys(), 
                                   key=lambda k: len(recognized_patterns[k])) if recognized_patterns else None
        }
    
    async def _calculate_pattern_confidence(
        self,
        recognized_patterns: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Calculate confidence scores for each pattern type"""
        confidence_scores = {}
        
        for pattern_type, patterns in recognized_patterns.items():
            if patterns:
                avg_confidence = sum(p.get('confidence', 0) for p in patterns) / len(patterns)
                confidence_scores[pattern_type] = avg_confidence
            else:
                confidence_scores[pattern_type] = 0.0
        
        return confidence_scores

class IntelligenceEngine:
    """Advanced transaction intelligence orchestrator"""
    
    def __init__(self):
        self.transaction_analyzer = TransactionAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.insights_cache = {}
        
    async def generate_transaction_insights(
        self,
        transactions: List[Transaction],
        analysis_scope: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate comprehensive transaction intelligence insights"""
        try:
            start_time = time.perf_counter()
            
            # Analyze patterns
            patterns = await self.transaction_analyzer.analyze_transaction_patterns(transactions)
            
            # Detect anomalies
            anomalies = await self.transaction_analyzer.detect_transaction_anomalies(transactions)
            
            # Recognize complex patterns
            recognized_patterns = await self.pattern_recognizer.recognize_transaction_patterns(transactions)
            
            # Generate business insights
            business_insights = await self._generate_business_insights(
                transactions, patterns, anomalies, recognized_patterns
            )
            
            # Create actionable recommendations
            recommendations = await self._create_actionable_recommendations(
                patterns, anomalies, business_insights
            )
            
            # Calculate intelligence score
            intelligence_score = await self._calculate_intelligence_score(
                patterns, anomalies, recognized_patterns
            )
            
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_scope": analysis_scope,
                "transaction_count": len(transactions),
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "type": p.pattern_type.value,
                        "description": p.description,
                        "confidence": p.confidence,
                        "affected_count": len(p.affected_transactions)
                    }
                    for p in patterns
                ],
                "anomalies": [
                    {
                        "anomaly_id": a.anomaly_id,
                        "type": a.anomaly_type.value,
                        "severity": a.severity,
                        "confidence": a.confidence,
                        "description": a.description,
                        "affected_count": len(a.affected_transactions)
                    }
                    for a in anomalies
                ],
                "recognized_patterns": recognized_patterns,
                "business_insights": business_insights,
                "recommendations": recommendations,
                "intelligence_score": intelligence_score
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Transaction intelligence generated",
                patterns_count=len(patterns),
                anomalies_count=len(anomalies),
                intelligence_score=intelligence_score,
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating transaction insights: {e}")
            raise
    
    async def _generate_business_insights(
        self,
        transactions: List[Transaction],
        patterns: List[TransactionPattern],
        anomalies: List[TransactionAnomaly],
        recognized_patterns: Dict[str, Any]
    ) -> List[IntelligenceInsight]:
        """Generate business intelligence insights"""
        insights = []
        
        if not transactions:
            return insights
        
        # Revenue insights
        total_revenue = sum(float(t.amount) for t in transactions if t.status == TransactionStatus.COMPLETED)
        avg_transaction = total_revenue / len(transactions) if transactions else 0
        
        insights.append(IntelligenceInsight(
            insight_id=f"revenue_{int(time.time())}",
            category="revenue",
            title="Revenue Analysis",
            description=f"Total revenue: ${total_revenue:.2f}, Average transaction: ${avg_transaction:.2f}",
            impact="high",
            confidence=0.95,
            data_points={
                "total_revenue": total_revenue,
                "average_transaction": avg_transaction,
                "transaction_count": len(transactions)
            },
            recommendations=[
                "Monitor revenue trends for optimization opportunities",
                "Analyze high-value transactions for upselling potential"
            ],
            created_at=datetime.utcnow()
        ))
        
        # User behavior insights
        unique_users = len(set(t.user_id for t in transactions))
        repeat_customers = len([
            user_id for user_id, count in 
            defaultdict(int, {t.user_id: defaultdict(int).__setitem__(t.user_id, 
                            defaultdict(int)[t.user_id] + 1) or defaultdict(int)[t.user_id] for t in transactions}).items()
            if count > 1
        ])
        
        if unique_users > 0:
            repeat_rate = (repeat_customers / unique_users) * 100
            
            insights.append(IntelligenceInsight(
                insight_id=f"behavior_{int(time.time())}",
                category="behavior",
                title="Customer Behavior",
                description=f"Repeat customer rate: {repeat_rate:.1f}% ({repeat_customers}/{unique_users})",
                impact="medium",
                confidence=0.85,
                data_points={
                    "unique_users": unique_users,
                    "repeat_customers": repeat_customers,
                    "repeat_rate": repeat_rate
                },
                recommendations=[
                    "Implement customer retention programs",
                    "Analyze repeat customer preferences"
                ],
                created_at=datetime.utcnow()
            ))
        
        # Risk insights based on anomalies
        high_risk_anomalies = [a for a in anomalies if a.severity in ["critical", "high"]]
        if high_risk_anomalies:
            insights.append(IntelligenceInsight(
                insight_id=f"risk_{int(time.time())}",
                category="risk",
                title="Risk Assessment",
                description=f"{len(high_risk_anomalies)} high-risk anomalies detected",
                impact="critical" if any(a.severity == "critical" for a in high_risk_anomalies) else "high",
                confidence=0.90,
                data_points={
                    "high_risk_count": len(high_risk_anomalies),
                    "anomaly_types": [a.anomaly_type.value for a in high_risk_anomalies]
                },
                recommendations=[
                    "Immediate review of high-risk transactions",
                    "Enhance fraud detection mechanisms",
                    "Implement additional verification steps"
                ],
                created_at=datetime.utcnow()
            ))
        
        return insights
    
    async def _create_actionable_recommendations(
        self,
        patterns: List[TransactionPattern],
        anomalies: List[TransactionAnomaly],
        business_insights: List[IntelligenceInsight]
    ) -> List[Dict[str, Any]]:
        """Create actionable recommendations based on analysis"""
        recommendations = []
        
        # Pattern-based recommendations
        for pattern in patterns[:5]:  # Top 5 patterns
            if pattern.pattern_type == PatternType.CYCLICAL:
                recommendations.append({
                    "category": "optimization",
                    "priority": "medium",
                    "title": "Optimize for Cyclical Patterns",
                    "description": f"Detected cyclical pattern: {pattern.description}",
                    "actions": [
                        "Adjust staffing for peak periods",
                        "Optimize infrastructure scaling",
                        "Prepare targeted marketing campaigns"
                    ],
                    "expected_impact": "15-25% efficiency improvement"
                })
            
            elif pattern.pattern_type == PatternType.TRENDING:
                recommendations.append({
                    "category": "growth",
                    "priority": "high",
                    "title": "Capitalize on Growth Trends",
                    "description": f"Growth trend detected: {pattern.description}",
                    "actions": [
                        "Scale infrastructure proactively",
                        "Increase marketing investment",
                        "Optimize conversion funnels"
                    ],
                    "expected_impact": "20-30% revenue increase"
                })
        
        # Anomaly-based recommendations
        critical_anomalies = [a for a in anomalies if a.severity == "critical"]
        if critical_anomalies:
            recommendations.append({
                "category": "security",
                "priority": "critical",
                "title": "Address Critical Anomalies",
                "description": f"{len(critical_anomalies)} critical anomalies require immediate attention",
                "actions": [
                    "Implement emergency fraud checks",
                    "Review and update security protocols",
                    "Conduct thorough transaction audits"
                ],
                "expected_impact": "Prevent potential losses and fraud"
            })
        
        # Business insight recommendations
        for insight in business_insights:
            if insight.impact == "critical":
                recommendations.append({
                    "category": insight.category,
                    "priority": "high",
                    "title": f"Act on {insight.title}",
                    "description": insight.description,
                    "actions": insight.recommendations,
                    "expected_impact": "Critical business impact"
                })
        
        return recommendations
    
    async def _calculate_intelligence_score(
        self,
        patterns: List[TransactionPattern],
        anomalies: List[TransactionAnomaly],
        recognized_patterns: Dict[str, Any]
    ) -> float:
        """Calculate overall transaction intelligence score (0-100)"""
        try:
            score = 0.0
            
            # Base score from pattern recognition
            pattern_score = min(40, len(patterns) * 2)  # Max 40 points
            score += pattern_score
            
            # Anomaly detection quality
            high_confidence_anomalies = [a for a in anomalies if a.confidence > 0.8]
            anomaly_score = min(20, len(high_confidence_anomalies) * 2)  # Max 20 points
            score += anomaly_score
            
            # Pattern diversity
            unique_pattern_types = len(set(p.pattern_type for p in patterns))
            diversity_score = min(15, unique_pattern_types * 3)  # Max 15 points
            score += diversity_score
            
            # Recognized pattern complexity
            pattern_complexity = len(recognized_patterns.get('patterns_by_type', {}))
            complexity_score = min(15, pattern_complexity * 2)  # Max 15 points
            score += complexity_score
            
            # Data quality bonus
            if len(patterns) > 5 and len(anomalies) > 0:
                score += 10  # Quality bonus
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating intelligence score: {e}")
            return 0.0

class TransactionIntelligence:
    """Main transaction intelligence orchestrator"""
    
    def __init__(self):
        self.intelligence_engine = IntelligenceEngine()
        self.performance_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def analyze_transaction_patterns(
        self,
        transactions: List[Transaction]
    ) -> Dict[str, Any]:
        """Main entry point for transaction pattern analysis"""
        return await self.intelligence_engine.transaction_analyzer.analyze_transaction_patterns(transactions)
    
    async def detect_transaction_anomalies(
        self,
        transactions: List[Transaction],
        sensitivity: float = 0.1
    ) -> List[TransactionAnomaly]:
        """Main entry point for anomaly detection"""
        return await self.intelligence_engine.transaction_analyzer.detect_transaction_anomalies(
            transactions, sensitivity
        )
    
    async def generate_transaction_insights(
        self,
        transactions: List[Transaction],
        analysis_scope: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Main entry point for comprehensive transaction intelligence"""
        return await self.intelligence_engine.generate_transaction_insights(
            transactions, analysis_scope
        )
    
    async def predict_transaction_behavior(
        self,
        historical_transactions: List[Transaction],
        prediction_horizon: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Predict future transaction behavior based on historical patterns"""
        try:
            start_time = time.perf_counter()
            
            # Analyze current patterns
            patterns = await self.analyze_transaction_patterns(historical_transactions)
            
            # Generate predictions based on patterns
            predictions = await self._generate_predictions(
                historical_transactions, patterns, prediction_horizon
            )
            
            # Calculate prediction confidence
            confidence = await self._calculate_prediction_confidence(
                historical_transactions, patterns
            )
            
            result = {
                "prediction_horizon_hours": prediction_horizon.total_seconds() / 3600,
                "predictions": predictions,
                "confidence": confidence,
                "based_on_patterns": len(patterns),
                "historical_transactions": len(historical_transactions)
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Transaction behavior predicted",
                predictions_count=len(predictions),
                confidence=confidence,
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting transaction behavior: {e}")
            raise
    
    async def _generate_predictions(
        self,
        transactions: List[Transaction],
        patterns: List[TransactionPattern],
        horizon: timedelta
    ) -> List[Dict[str, Any]]:
        """Generate specific predictions based on patterns"""
        predictions = []
        
        if not transactions:
            return predictions
        
        # Volume prediction based on patterns
        recent_hourly_volume = len([
            t for t in transactions 
            if t.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]) / 24
        
        # Find cyclical patterns for volume prediction
        cyclical_patterns = [p for p in patterns if p.pattern_type == PatternType.CYCLICAL]
        if cyclical_patterns:
            # Use cyclical pattern to predict peaks
            predictions.append({
                "type": "volume_prediction",
                "description": f"Expected {recent_hourly_volume * 1.2:.0f} transactions/hour during peak periods",
                "confidence": 0.8,
                "timeframe": "next 24 hours"
            })
        
        # Amount prediction based on trends
        recent_avg_amount = statistics.mean([
            float(t.amount) for t in transactions[-100:]  # Last 100 transactions
        ]) if len(transactions) >= 100 else 0
        
        trending_patterns = [p for p in patterns if p.pattern_type == PatternType.TRENDING]
        if trending_patterns and recent_avg_amount > 0:
            trend_direction = "increase" if "increasing" in trending_patterns[0].description else "decrease"
            predicted_change = 5 if trend_direction == "increase" else -5  # 5% change
            
            predictions.append({
                "type": "amount_prediction", 
                "description": f"Average transaction amount expected to {trend_direction} by {abs(predicted_change)}%",
                "confidence": 0.75,
                "current_average": recent_avg_amount,
                "predicted_average": recent_avg_amount * (1 + predicted_change/100)
            })
        
        return predictions
    
    async def _calculate_prediction_confidence(
        self,
        transactions: List[Transaction],
        patterns: List[TransactionPattern]
    ) -> float:
        """Calculate overall prediction confidence"""
        if not patterns:
            return 0.0
        
        # Base confidence from pattern strength
        avg_pattern_confidence = statistics.mean([p.confidence for p in patterns])
        
        # Adjust for data quantity
        data_quality_factor = min(1.0, len(transactions) / 1000)  # More data = higher confidence
        
        # Adjust for pattern consistency
        pattern_types = set(p.pattern_type for p in patterns)
        consistency_factor = len(pattern_types) / len(PatternType)  # More pattern types = higher confidence
        
        final_confidence = avg_pattern_confidence * data_quality_factor * consistency_factor
        return min(0.95, final_confidence)

if __name__ == "__main__":
    # Enterprise testing and validation
    async def test_transaction_intelligence():
        """Test transaction intelligence functionality"""
        intelligence = TransactionIntelligence()
        
        # Create test transactions
        test_transactions = []
        base_time = datetime.utcnow() - timedelta(hours=48)
        
        for i in range(1000):
            txn = Transaction(
                transaction_id=f"txn_{i}",
                amount=Decimal(str(50 + (i % 200))),  # Varying amounts
                currency="USD",
                transaction_type=TransactionType.PAYMENT,
                status=TransactionStatus.COMPLETED,
                timestamp=base_time + timedelta(minutes=i * 3),  # Every 3 minutes
                user_id=f"user_{i % 100}",  # 100 unique users
                merchant_id=f"merchant_{i % 10}",  # 10 merchants
                payment_method="credit_card",
                country="US"
            )
            test_transactions.append(txn)
        
        # Analyze patterns
        patterns = await intelligence.analyze_transaction_patterns(test_transactions)
        print(f"Patterns found: {len(patterns)}")
        
        # Detect anomalies
        anomalies = await intelligence.detect_transaction_anomalies(test_transactions)
        print(f"Anomalies detected: {len(anomalies)}")
        
        # Generate insights
        insights = await intelligence.generate_transaction_insights(test_transactions)
        print(f"Intelligence insights: {json.dumps(insights, indent=2, default=str)}")
        
        # Predict behavior
        predictions = await intelligence.predict_transaction_behavior(test_transactions)
        print(f"Behavior predictions: {json.dumps(predictions, indent=2, default=str)}")
    
    # Run tests
    asyncio.run(test_transaction_intelligence())