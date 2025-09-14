"""
Ainflue Platform - Payment Success Rate Tracker
===============================================

Advanced payment success rate tracking system for monitoring payment
gateway performance, failure analysis, and optimization recommendations
for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status types."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGEBACK = "chargeback"

class PaymentMethod(Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"

class FailureReason(Enum):
    """Payment failure reasons."""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_DECLINED = "card_declined"
    EXPIRED_CARD = "expired_card"
    INVALID_CVV = "invalid_cvv"
    FRAUD_DETECTION = "fraud_detection"
    NETWORK_ERROR = "network_error"
    GATEWAY_TIMEOUT = "gateway_timeout"
    AUTHENTICATION_FAILED = "authentication_failed"
    LIMIT_EXCEEDED = "limit_exceeded"
    CURRENCY_NOT_SUPPORTED = "currency_not_supported"

@dataclass
class PaymentTransaction:
    """Payment transaction record."""
    transaction_id: str
    partnership_id: str
    creator_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
    gateway: str
    status: PaymentStatus
    failure_reason: Optional[FailureReason]
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SuccessRateMetrics:
    """Payment success rate metrics."""
    time_period: Tuple[datetime, datetime]
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    success_rate: float
    failure_rate: float
    average_amount: float
    total_volume: float
    processing_time_avg: float
    gateway_breakdown: Dict[str, Dict[str, float]]
    method_breakdown: Dict[PaymentMethod, Dict[str, float]]
    failure_analysis: Dict[FailureReason, int]
    trend_direction: str
    confidence_score: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class GatewayPerformance:
    """Gateway performance analysis."""
    gateway_name: str
    success_rate: float
    failure_rate: float
    average_processing_time: float
    transaction_count: int
    total_volume: float
    uptime_percentage: float
    error_frequency: float
    cost_per_transaction: float
    reliability_score: float
    recommendation: str

class PaymentSuccessRateTracker:
    """
    Advanced payment success rate tracker for monetization monitoring.
    
    Features:
    - Real-time success rate tracking
    - Gateway performance comparison
    - Failure pattern analysis
    - Optimization recommendations
    - Trend analysis and forecasting
    - Alert system for rate drops
    - Geographic and demographic analysis
    - Cost optimization insights
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.transactions: Dict[str, List[PaymentTransaction]] = defaultdict(list)
        self.success_rate_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.gateway_performance: Dict[str, GatewayPerformance] = {}
        self.alert_thresholds = {
            'success_rate_min': 0.95,
            'processing_time_max': 5.0,
            'failure_rate_max': 0.05
        }
        
        # Performance metrics
        self.metrics = {
            'total_transactions_tracked': 0,
            'overall_success_rate': 0.0,
            'total_volume_processed': 0.0,
            'alerts_triggered': 0,
            'gateways_monitored': 0,
            'optimization_opportunities': 0
        }
        
        logger.info("PaymentSuccessRateTracker initialized")

    async def record_transaction(
        self,
        partnership_id: str,
        creator_id: str,
        amount: float,
        currency: str,
        payment_method: PaymentMethod,
        gateway: str,
        status: PaymentStatus,
        processing_time: float,
        failure_reason: Optional[FailureReason] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentTransaction:
        """Record a payment transaction."""
        try:
            transaction = PaymentTransaction(
                transaction_id=str(uuid.uuid4()),
                partnership_id=partnership_id,
                creator_id=creator_id,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                gateway=gateway,
                status=status,
                failure_reason=failure_reason,
                processing_time=processing_time,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Store transaction
            self.transactions[partnership_id].append(transaction)
            
            # Update metrics
            self.metrics['total_transactions_tracked'] += 1
            self.metrics['total_volume_processed'] += amount
            
            # Update success rate history
            is_successful = status == PaymentStatus.SUCCESS
            self.success_rate_history[partnership_id].append({
                'timestamp': transaction.timestamp,
                'success': is_successful,
                'amount': amount,
                'gateway': gateway,
                'method': payment_method
            })
            
            # Check for alerts
            await self._check_alerts(partnership_id)
            
            logger.info(f"Recorded transaction: {status.value} ${amount} via {gateway}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error recording transaction: {e}")
            raise

    async def calculate_success_rate(
        self,
        partnership_id: str,
        time_period: Optional[Tuple[datetime, datetime]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> SuccessRateMetrics:
        """Calculate success rate metrics for a partnership."""
        try:
            transactions = self.transactions.get(partnership_id, [])
            
            if not transactions:
                raise ValueError(f"No transactions found for partnership {partnership_id}")
            
            # Apply time period filter
            if time_period:
                start_date, end_date = time_period
                transactions = [t for t in transactions if start_date <= t.timestamp <= end_date]
            else:
                # Default to last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                transactions = [t for t in transactions if start_date <= t.timestamp <= end_date]
                time_period = (start_date, end_date)
            
            # Apply additional filters
            if filters:
                transactions = self._apply_filters(transactions, filters)
            
            if not transactions:
                raise ValueError("No transactions found for specified criteria")
            
            # Calculate basic metrics
            total_transactions = len(transactions)
            successful_transactions = len([t for t in transactions if t.status == PaymentStatus.SUCCESS])
            failed_transactions = total_transactions - successful_transactions
            
            success_rate = successful_transactions / total_transactions if total_transactions > 0 else 0.0
            failure_rate = failed_transactions / total_transactions if total_transactions > 0 else 0.0
            
            # Calculate financial metrics
            amounts = [t.amount for t in transactions]
            average_amount = np.mean(amounts) if amounts else 0.0
            total_volume = sum(amounts)
            
            # Calculate processing time
            processing_times = [t.processing_time for t in transactions]
            processing_time_avg = np.mean(processing_times) if processing_times else 0.0
            
            # Gateway breakdown
            gateway_breakdown = self._calculate_gateway_breakdown(transactions)
            
            # Payment method breakdown
            method_breakdown = self._calculate_method_breakdown(transactions)
            
            # Failure analysis
            failure_analysis = self._analyze_failures(transactions)
            
            # Trend analysis
            trend_direction = self._calculate_trend_direction(partnership_id)
            
            # Confidence score
            confidence_score = self._calculate_confidence_score(transactions)
            
            metrics = SuccessRateMetrics(
                time_period=time_period,
                total_transactions=total_transactions,
                successful_transactions=successful_transactions,
                failed_transactions=failed_transactions,
                success_rate=success_rate,
                failure_rate=failure_rate,
                average_amount=average_amount,
                total_volume=total_volume,
                processing_time_avg=processing_time_avg,
                gateway_breakdown=gateway_breakdown,
                method_breakdown=method_breakdown,
                failure_analysis=failure_analysis,
                trend_direction=trend_direction,
                confidence_score=confidence_score
            )
            
            # Update overall success rate
            self._update_overall_success_rate()
            
            logger.info(f"Calculated success rate: {success_rate:.3f} for partnership {partnership_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating success rate: {e}")
            raise

    def _apply_filters(self, transactions: List[PaymentTransaction], filters: Dict[str, Any]) -> List[PaymentTransaction]:
        """Apply filters to transaction list."""
        filtered = transactions
        
        if 'gateway' in filters:
            filtered = [t for t in filtered if t.gateway == filters['gateway']]
        
        if 'payment_method' in filters:
            filtered = [t for t in filtered if t.payment_method == filters['payment_method']]
        
        if 'min_amount' in filters:
            filtered = [t for t in filtered if t.amount >= filters['min_amount']]
        
        if 'max_amount' in filters:
            filtered = [t for t in filtered if t.amount <= filters['max_amount']]
        
        if 'currency' in filters:
            filtered = [t for t in filtered if t.currency == filters['currency']]
        
        return filtered

    def _calculate_gateway_breakdown(self, transactions: List[PaymentTransaction]) -> Dict[str, Dict[str, float]]:
        """Calculate success rates by gateway."""
        gateway_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'volume': 0.0})
        
        for transaction in transactions:
            gateway = transaction.gateway
            gateway_stats[gateway]['total'] += 1
            gateway_stats[gateway]['volume'] += transaction.amount
            
            if transaction.status == PaymentStatus.SUCCESS:
                gateway_stats[gateway]['success'] += 1
        
        # Calculate rates
        breakdown = {}
        for gateway, stats in gateway_stats.items():
            success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0.0
            breakdown[gateway] = {
                'success_rate': success_rate,
                'transaction_count': stats['total'],
                'total_volume': stats['volume'],
                'average_amount': stats['volume'] / stats['total'] if stats['total'] > 0 else 0.0
            }
        
        return breakdown

    def _calculate_method_breakdown(self, transactions: List[PaymentTransaction]) -> Dict[PaymentMethod, Dict[str, float]]:
        """Calculate success rates by payment method."""
        method_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'volume': 0.0})
        
        for transaction in transactions:
            method = transaction.payment_method
            method_stats[method]['total'] += 1
            method_stats[method]['volume'] += transaction.amount
            
            if transaction.status == PaymentStatus.SUCCESS:
                method_stats[method]['success'] += 1
        
        # Calculate rates
        breakdown = {}
        for method, stats in method_stats.items():
            success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0.0
            breakdown[method] = {
                'success_rate': success_rate,
                'transaction_count': stats['total'],
                'total_volume': stats['volume'],
                'average_amount': stats['volume'] / stats['total'] if stats['total'] > 0 else 0.0
            }
        
        return breakdown

    def _analyze_failures(self, transactions: List[PaymentTransaction]) -> Dict[FailureReason, int]:
        """Analyze failure patterns."""
        failure_counts = defaultdict(int)
        
        for transaction in transactions:
            if transaction.status != PaymentStatus.SUCCESS and transaction.failure_reason:
                failure_counts[transaction.failure_reason] += 1
        
        return dict(failure_counts)

    def _calculate_trend_direction(self, partnership_id: str) -> str:
        """Calculate trend direction for success rate."""
        history = list(self.success_rate_history.get(partnership_id, []))
        
        if len(history) < 5:
            return "insufficient_data"
        
        # Calculate success rates for recent periods
        recent_period = history[-10:]  # Last 10 transactions
        earlier_period = history[-20:-10] if len(history) >= 20 else history[:-10]
        
        if not earlier_period:
            return "insufficient_data"
        
        recent_success_rate = sum(1 for t in recent_period if t['success']) / len(recent_period)
        earlier_success_rate = sum(1 for t in earlier_period if t['success']) / len(earlier_period)
        
        if recent_success_rate > earlier_success_rate + 0.02:
            return "improving"
        elif recent_success_rate < earlier_success_rate - 0.02:
            return "declining"
        else:
            return "stable"

    def _calculate_confidence_score(self, transactions: List[PaymentTransaction]) -> float:
        """Calculate confidence score for metrics."""
        factors = []
        
        # Sample size factor
        sample_size = len(transactions)
        size_factor = min(sample_size / 100, 1.0)  # Normalize to 100 transactions
        factors.append(size_factor)
        
        # Time span factor
        if transactions:
            time_span = (max(t.timestamp for t in transactions) - min(t.timestamp for t in transactions)).days
            span_factor = min(time_span / 30, 1.0)  # Normalize to 30 days
            factors.append(span_factor)
        else:
            factors.append(0.0)
        
        # Data consistency factor
        if sample_size > 1:
            amounts = [t.amount for t in transactions]
            cv = np.std(amounts) / np.mean(amounts) if np.mean(amounts) > 0 else 1.0
            consistency_factor = max(0.2, 1.0 - cv)  # Lower coefficient of variation = higher consistency
            factors.append(consistency_factor)
        else:
            factors.append(0.5)
        
        return np.mean(factors)

    async def analyze_gateway_performance(self, time_period: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, GatewayPerformance]:
        """Analyze performance of all payment gateways."""
        try:
            all_transactions = []
            for partnership_transactions in self.transactions.values():
                all_transactions.extend(partnership_transactions)
            
            # Apply time filter
            if time_period:
                start_date, end_date = time_period
                all_transactions = [t for t in all_transactions if start_date <= t.timestamp <= end_date]
            
            # Group by gateway
            gateway_transactions = defaultdict(list)
            for transaction in all_transactions:
                gateway_transactions[transaction.gateway].append(transaction)
            
            # Analyze each gateway
            gateway_performances = {}
            for gateway, transactions in gateway_transactions.items():
                performance = self._analyze_single_gateway(gateway, transactions)
                gateway_performances[gateway] = performance
                
            # Update stored performance data
            self.gateway_performance.update(gateway_performances)
            self.metrics['gateways_monitored'] = len(gateway_performances)
            
            return gateway_performances
            
        except Exception as e:
            logger.error(f"Error analyzing gateway performance: {e}")
            return {}

    def _analyze_single_gateway(self, gateway_name: str, transactions: List[PaymentTransaction]) -> GatewayPerformance:
        """Analyze performance of a single gateway."""
        if not transactions:
            return GatewayPerformance(
                gateway_name=gateway_name,
                success_rate=0.0,
                failure_rate=0.0,
                average_processing_time=0.0,
                transaction_count=0,
                total_volume=0.0,
                uptime_percentage=0.0,
                error_frequency=0.0,
                cost_per_transaction=0.0,
                reliability_score=0.0,
                recommendation="No data available"
            )
        
        # Basic metrics
        total_transactions = len(transactions)
        successful_transactions = len([t for t in transactions if t.status == PaymentStatus.SUCCESS])
        success_rate = successful_transactions / total_transactions
        failure_rate = 1.0 - success_rate
        
        # Performance metrics
        processing_times = [t.processing_time for t in transactions]
        average_processing_time = np.mean(processing_times)
        
        # Volume metrics
        total_volume = sum(t.amount for t in transactions)
        
        # Reliability metrics
        network_errors = len([t for t in transactions if t.failure_reason == FailureReason.NETWORK_ERROR])
        timeout_errors = len([t for t in transactions if t.failure_reason == FailureReason.GATEWAY_TIMEOUT])
        
        uptime_percentage = 1.0 - ((network_errors + timeout_errors) / total_transactions)
        error_frequency = (network_errors + timeout_errors) / total_transactions
        
        # Cost estimation (placeholder - would be based on actual gateway fees)
        cost_per_transaction = self._estimate_gateway_cost(gateway_name, total_volume, total_transactions)
        
        # Overall reliability score
        reliability_score = (
            0.4 * success_rate +
            0.3 * uptime_percentage +
            0.2 * (1.0 - min(average_processing_time / 10, 1.0)) +  # Processing time factor
            0.1 * (1.0 - error_frequency)
        )
        
        # Generate recommendation
        recommendation = self._generate_gateway_recommendation(
            success_rate, average_processing_time, uptime_percentage, cost_per_transaction
        )
        
        return GatewayPerformance(
            gateway_name=gateway_name,
            success_rate=success_rate,
            failure_rate=failure_rate,
            average_processing_time=average_processing_time,
            transaction_count=total_transactions,
            total_volume=total_volume,
            uptime_percentage=uptime_percentage,
            error_frequency=error_frequency,
            cost_per_transaction=cost_per_transaction,
            reliability_score=reliability_score,
            recommendation=recommendation
        )

    def _estimate_gateway_cost(self, gateway_name: str, total_volume: float, transaction_count: int) -> float:
        """Estimate cost per transaction for gateway."""
        # Typical gateway fee structures (simplified)
        fee_structures = {
            'stripe': 0.029,  # 2.9% + $0.30
            'paypal': 0.031,  # 3.1% + $0.30
            'square': 0.028,  # 2.8% + $0.30
            'default': 0.030  # 3.0% average
        }
        
        percentage_fee = fee_structures.get(gateway_name.lower(), fee_structures['default'])
        fixed_fee = 0.30  # $0.30 per transaction
        
        if transaction_count == 0:
            return 0.0
        
        total_cost = (total_volume * percentage_fee) + (transaction_count * fixed_fee)
        return total_cost / transaction_count

    def _generate_gateway_recommendation(
        self,
        success_rate: float,
        processing_time: float,
        uptime: float,
        cost: float
    ) -> str:
        """Generate recommendation for gateway performance."""
        if success_rate >= 0.98 and processing_time <= 2.0 and uptime >= 0.99:
            return "Excellent performance - maintain current configuration"
        elif success_rate >= 0.95 and processing_time <= 5.0 and uptime >= 0.95:
            return "Good performance - monitor for optimization opportunities"
        elif success_rate >= 0.90:
            return "Acceptable performance - investigate failure patterns"
        elif success_rate >= 0.85:
            return "Below average performance - consider alternative gateway"
        else:
            return "Poor performance - immediate action required"

    async def _check_alerts(self, partnership_id -> None: str) -> None:
        """Check for alert conditions."""
        try:
            # Get recent success rate
            recent_history = list(self.success_rate_history[partnership_id])[-20:]  # Last 20 transactions
            
            if len(recent_history) < 10:
                return  # Not enough data for alerting
            
            recent_success_rate = sum(1 for t in recent_history if t['success']) / len(recent_history)
            
            # Check success rate threshold
            if recent_success_rate < self.alert_thresholds['success_rate_min']:
                await self._trigger_alert(
                    partnership_id,
                    "low_success_rate",
                    f"Success rate dropped to {recent_success_rate:.1%}",
                    {"current_rate": recent_success_rate, "threshold": self.alert_thresholds['success_rate_min']}
                )
            
            # Check processing time
            recent_processing_times = [t.get('processing_time', 0) for t in recent_history]
            avg_processing_time = np.mean(recent_processing_times) if recent_processing_times else 0
            
            if avg_processing_time > self.alert_thresholds['processing_time_max']:
                await self._trigger_alert(
                    partnership_id,
                    "high_processing_time",
                    f"Average processing time increased to {avg_processing_time:.2f}s",
                    {"current_time": avg_processing_time, "threshold": self.alert_thresholds['processing_time_max']}
                )
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    async def _trigger_alert(self, partnership_id -> None: str, alert_type -> None: str, message -> None: str, data -> None: Dict[str, Any]) -> None:
        """Trigger an alert for payment issues."""
        alert = {
            'partnership_id': partnership_id,
            'alert_type': alert_type,
            'message': message,
            'data': data,
            'timestamp': datetime.now(),
            'severity': self._determine_alert_severity(alert_type, data)
        }
        
        self.metrics['alerts_triggered'] += 1
        
        logger.warning(f"Payment alert triggered: {alert_type} - {message}")
        
        # Here you would typically send notifications
        # await self._send_alert_notification(alert)

    def _determine_alert_severity(self, alert_type: str, data: Dict[str, Any]) -> str:
        """Determine alert severity level."""
        if alert_type == "low_success_rate":
            rate = data.get('current_rate', 1.0)
            if rate < 0.80:
                return "critical"
            elif rate < 0.90:
                return "high"
            else:
                return "medium"
        
        elif alert_type == "high_processing_time":
            time = data.get('current_time', 0)
            if time > 10.0:
                return "critical"
            elif time > 7.0:
                return "high"
            else:
                return "medium"
        
        return "low"

    def _update_overall_success_rate(self) -> None:
        """Update overall success rate metric."""
        all_transactions = []
        for partnership_transactions in self.transactions.values():
            all_transactions.extend(partnership_transactions)
        
        if all_transactions:
            successful = len([t for t in all_transactions if t.status == PaymentStatus.SUCCESS])
            self.metrics['overall_success_rate'] = successful / len(all_transactions)

    async def get_optimization_recommendations(
        self,
        partnership_id: str,
        target_success_rate: float = 0.98
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations for payment success rate."""
        try:
            recommendations = []
            
            # Get current metrics
            current_metrics = await self.calculate_success_rate(partnership_id)
            
            if current_metrics.success_rate >= target_success_rate:
                return [{"type": "success", "message": "Target success rate already achieved"}]
            
            # Analyze failure patterns
            failure_analysis = current_metrics.failure_analysis
            top_failures = sorted(failure_analysis.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for failure_reason, count in top_failures:
                recommendation = self._get_failure_recommendation(failure_reason, count)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Gateway optimization
            gateway_breakdown = current_metrics.gateway_breakdown
            best_gateway = max(gateway_breakdown.items(), key=lambda x: x[1]['success_rate'])
            worst_gateway = min(gateway_breakdown.items(), key=lambda x: x[1]['success_rate'])
            
            if len(gateway_breakdown) > 1 and best_gateway[1]['success_rate'] - worst_gateway[1]['success_rate'] > 0.05:
                recommendations.append({
                    "type": "gateway_optimization",
                    "message": f"Consider routing more traffic to {best_gateway[0]} (success rate: {best_gateway[1]['success_rate']:.1%})",
                    "impact": "medium",
                    "current_best": best_gateway[0],
                    "current_worst": worst_gateway[0]
                })
            
            # Payment method optimization
            method_breakdown = current_metrics.method_breakdown
            if method_breakdown:
                best_method = max(method_breakdown.items(), key=lambda x: x[1]['success_rate'])
                recommendations.append({
                    "type": "method_optimization",
                    "message": f"Promote {best_method[0].value} payment method (success rate: {best_method[1]['success_rate']:.1%})",
                    "impact": "low",
                    "recommended_method": best_method[0].value
                })
            
            self.metrics['optimization_opportunities'] += len(recommendations)
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {e}")
            return []

    def _get_failure_recommendation(self, failure_reason: FailureReason, count: int) -> Optional[Dict[str, Any]]:
        """Get recommendation for specific failure reason."""
        recommendations_map = {
            FailureReason.INSUFFICIENT_FUNDS: {
                "type": "insufficient_funds",
                "message": "Implement payment plan options or retry mechanisms for insufficient funds",
                "impact": "high"
            },
            FailureReason.CARD_DECLINED: {
                "type": "card_declined",
                "message": "Add alternative payment methods and improve decline messaging",
                "impact": "high"
            },
            FailureReason.EXPIRED_CARD: {
                "type": "expired_card",
                "message": "Implement card update reminders and automatic retry systems",
                "impact": "medium"
            },
            FailureReason.FRAUD_DETECTION: {
                "type": "fraud_detection",
                "message": "Review fraud detection settings and implement manual review process",
                "impact": "medium"
            },
            FailureReason.NETWORK_ERROR: {
                "type": "network_error",
                "message": "Improve network resilience and implement automatic retry logic",
                "impact": "high"
            },
            FailureReason.GATEWAY_TIMEOUT: {
                "type": "gateway_timeout",
                "message": "Optimize gateway configuration and consider backup gateways",
                "impact": "high"
            }
        }
        
        recommendation = recommendations_map.get(failure_reason)
        if recommendation:
            recommendation["failure_count"] = count
            recommendation["failure_reason"] = failure_reason.value
        
        return recommendation

    async def get_tracker_metrics(self) -> Dict[str, Any]:
        """Get payment success rate tracker metrics."""
        try:
            return {
                'total_transactions_tracked': self.metrics['total_transactions_tracked'],
                'overall_success_rate': self.metrics['overall_success_rate'],
                'total_volume_processed': self.metrics['total_volume_processed'],
                'alerts_triggered': self.metrics['alerts_triggered'],
                'gateways_monitored': self.metrics['gateways_monitored'],
                'optimization_opportunities': self.metrics['optimization_opportunities'],
                'partnerships_monitored': len(self.transactions),
                'alert_thresholds': self.alert_thresholds,
                'gateway_performance_summary': {
                    gateway: {
                        'success_rate': perf.success_rate,
                        'reliability_score': perf.reliability_score,
                        'recommendation': perf.recommendation
                    }
                    for gateway, perf in self.gateway_performance.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting tracker metrics: {e}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    async def test_payment_tracker() -> None:
        """Test payment success rate tracker."""
        tracker = PaymentSuccessRateTracker()
        
        partnership_id = "partnership_001"
        
        try:
            # Record some transactions
            transactions_data = [
                (1000.0, PaymentMethod.CREDIT_CARD, "stripe", PaymentStatus.SUCCESS, 2.1, None),
                (500.0, PaymentMethod.PAYPAL, "paypal", PaymentStatus.SUCCESS, 3.2, None),
                (750.0, PaymentMethod.CREDIT_CARD, "stripe", PaymentStatus.FAILED, 1.8, FailureReason.CARD_DECLINED),
                (1200.0, PaymentMethod.DEBIT_CARD, "square", PaymentStatus.SUCCESS, 2.5, None),
                (300.0, PaymentMethod.APPLE_PAY, "stripe", PaymentStatus.SUCCESS, 1.9, None)
            ]
            
            for amount, method, gateway, status, processing_time, failure_reason in transactions_data:
                await tracker.record_transaction(
                    partnership_id=partnership_id,
                    creator_id="creator_001",
                    amount=amount,
                    currency="USD",
                    payment_method=method,
                    gateway=gateway,
                    status=status,
                    processing_time=processing_time,
                    failure_reason=failure_reason
                )
            
            # Calculate success rate
            metrics = await tracker.calculate_success_rate(partnership_id)
            print(f"Success Rate: {metrics.success_rate:.3f}")
            print(f"Total Volume: ${metrics.total_volume}")
            print(f"Average Processing Time: {metrics.processing_time_avg:.2f}s")
            print(f"Trend: {metrics.trend_direction}")
            
            # Analyze gateway performance
            gateway_performance = await tracker.analyze_gateway_performance()
            for gateway, perf in gateway_performance.items():
                print(f"Gateway {gateway}: {perf.success_rate:.3f} success rate")
            
            # Get optimization recommendations
            recommendations = await tracker.get_optimization_recommendations(partnership_id)
            print(f"Optimization recommendations: {len(recommendations)}")
            for rec in recommendations:
                print(f"  - {rec['message']}")
            
            # Get tracker metrics
            tracker_metrics = await tracker.get_tracker_metrics()
            print(f"Tracker metrics: {tracker_metrics}")
            
        except Exception as e:
            print(f"Error in test: {e}")
    
    # Run test
    asyncio.run(test_payment_tracker())