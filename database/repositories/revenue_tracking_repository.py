"""Revenue Tracking Repository Module

Enterprise-grade repository for revenue tracking and monetization management
with advanced analytics, payment processing, and financial compliance.

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

from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, extract
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from ..models.revenue_tracking import (
    RevenueTracking,
    RevenueType,
    RevenueSource,
    RevenueStatus,
    Currency,
    PaymentMethod,
    TaxStatus
)
from ..models.content_fingerprints import ContentFingerprint
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class RevenueTrackingRepository(BaseRepository[RevenueTracking]):
    """
    Repository for revenue tracking operations with comprehensive financial analytics,
    multi-currency support, tax compliance, and automated payment processing.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize revenue tracking repository"""
        super().__init__(db_session, RevenueTracking)
        
    def create_revenue_entry(self,
                           user_id: int,
                           content_id: Optional[int],
                           platform: str,
                           revenue_amount: Decimal,
                           revenue_type: RevenueType,
                           revenue_source: RevenueSource,
                           currency: Currency = Currency.EUR,
                           period_start: Optional[datetime] = None,
                           period_end: Optional[datetime] = None,
                           tax_status: TaxStatus = TaxStatus.PENDING,
                           metadata: Optional[Dict[str, Any]] = None) -> RevenueTracking:
        """
        Create revenue tracking entry with validation and compliance checks
        
        Args:
            user_id: User/creator ID
            content_id: Associated content fingerprint ID
            platform: Platform generating revenue
            revenue_amount: Revenue amount
            revenue_type: Type of revenue
            revenue_source: Source of revenue
            currency: Currency code
            period_start: Revenue period start date
            period_end: Revenue period end date
            tax_status: Tax compliance status
            metadata: Additional revenue metadata
            
        Returns:
            Created RevenueTracking instance
        """
        try:
            # Validate revenue amount
            if revenue_amount <= 0:
                raise RepositoryException("Revenue amount must be positive")
            
            # Set default period if not provided
            if not period_start:
                period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if not period_end:
                # End of current month
                next_month = period_start.replace(day=28) + timedelta(days=4)
                period_end = next_month - timedelta(days=next_month.day)
            
            # Generate transaction ID
            transaction_id = str(uuid.uuid4())
            
            revenue_data = {
                'user_id': user_id,
                'content_id': content_id,
                'platform': platform,
                'revenue_amount': revenue_amount,
                'revenue_type': revenue_type,
                'revenue_source': revenue_source,
                'currency': currency,
                'period_start': period_start,
                'period_end': period_end,
                'status': RevenueStatus.PENDING,
                'tax_status': tax_status,
                'transaction_id': transaction_id,
                'metadata': metadata or {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            revenue_entry = self.create(**revenue_data)
            
            self.logger.info(
                f"Created revenue entry: {revenue_amount} {currency.value} from {platform}"
            )
            
            return revenue_entry
            
        except Exception as e:
            self.logger.error(f"Failed to create revenue entry: {str(e)}")
            raise RepositoryException(f"Revenue entry creation failed: {str(e)}")
            
    def get_user_revenue(self,
                        user_id: int,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        currency: Optional[Currency] = None,
                        platform: Optional[str] = None,
                        revenue_type: Optional[RevenueType] = None,
                        status: Optional[RevenueStatus] = None) -> List[RevenueTracking]:
        """
        Get revenue entries for a user with comprehensive filtering
        
        Args:
            user_id: User ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            currency: Optional currency filter
            platform: Optional platform filter
            revenue_type: Optional revenue type filter
            status: Optional status filter
            
        Returns:
            List of RevenueTracking instances
        """
        try:
            query = self.db_session.query(RevenueTracking).filter(
                RevenueTracking.user_id == user_id
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(RevenueTracking.period_start >= start_date)
            if end_date:
                query = query.filter(RevenueTracking.period_end <= end_date)
            
            # Apply other filters
            if currency:
                query = query.filter(RevenueTracking.currency == currency)
            if platform:
                query = query.filter(RevenueTracking.platform.ilike(f"%{platform}%"))
            if revenue_type:
                query = query.filter(RevenueTracking.revenue_type == revenue_type)
            if status:
                query = query.filter(RevenueTracking.status == status)
            
            # Order by period start (most recent first)
            query = query.order_by(RevenueTracking.period_start.desc())
            
            revenue_entries = query.all()
            
            self.logger.debug(
                f"Retrieved {len(revenue_entries)} revenue entries for user {user_id}"
            )
            
            return revenue_entries
            
        except Exception as e:
            self.logger.error(f"Failed to get user revenue: {str(e)}")
            return []
            
    def calculate_total_revenue(self,
                              user_id: int,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              currency: Currency = Currency.EUR,
                              exclude_pending: bool = True) -> Dict[str, Any]:
        """
        Calculate total revenue for user with breakdown by various dimensions
        
        Args:
            user_id: User ID to calculate revenue for
            start_date: Optional start date filter
            end_date: Optional end date filter
            currency: Currency to calculate in
            exclude_pending: Whether to exclude pending revenue
            
        Returns:
            Dictionary containing revenue calculations
        """
        try:
            query = self.db_session.query(RevenueTracking).filter(
                and_(
                    RevenueTracking.user_id == user_id,
                    RevenueTracking.currency == currency
                )
            )
            
            # Apply date filters
            if start_date:
                query = query.filter(RevenueTracking.period_start >= start_date)
            if end_date:
                query = query.filter(RevenueTracking.period_end <= end_date)
            
            # Exclude pending if requested
            if exclude_pending:
                query = query.filter(RevenueTracking.status != RevenueStatus.PENDING)
            
            revenue_entries = query.all()
            
            if not revenue_entries:
                return {
                    'total_revenue': Decimal('0.00'),
                    'currency': currency.value,
                    'entry_count': 0,
                    'breakdown_by_platform': {},
                    'breakdown_by_type': {},
                    'breakdown_by_source': {},
                    'period_start': start_date.isoformat() if start_date else None,
                    'period_end': end_date.isoformat() if end_date else None
                }
            
            # Calculate totals
            total_revenue = sum(entry.revenue_amount for entry in revenue_entries)
            
            # Breakdown by platform
            platform_breakdown = {}
            for entry in revenue_entries:
                platform = entry.platform
                platform_breakdown[platform] = platform_breakdown.get(platform, Decimal('0.00'))
                platform_breakdown[platform] += entry.revenue_amount
            
            # Breakdown by revenue type
            type_breakdown = {}
            for entry in revenue_entries:
                rev_type = entry.revenue_type.value
                type_breakdown[rev_type] = type_breakdown.get(rev_type, Decimal('0.00'))
                type_breakdown[rev_type] += entry.revenue_amount
            
            # Breakdown by revenue source
            source_breakdown = {}
            for entry in revenue_entries:
                source = entry.revenue_source.value
                source_breakdown[source] = source_breakdown.get(source, Decimal('0.00'))
                source_breakdown[source] += entry.revenue_amount
            
            # Convert Decimal to float for JSON serialization
            result = {
                'total_revenue': float(total_revenue),
                'currency': currency.value,
                'entry_count': len(revenue_entries),
                'breakdown_by_platform': {k: float(v) for k, v in platform_breakdown.items()},
                'breakdown_by_type': {k: float(v) for k, v in type_breakdown.items()},
                'breakdown_by_source': {k: float(v) for k, v in source_breakdown.items()},
                'period_start': start_date.isoformat() if start_date else None,
                'period_end': end_date.isoformat() if end_date else None,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to calculate total revenue: {str(e)}")
            return {'error': str(e)}
            
    def get_monthly_revenue_trends(self,
                                  user_id: int,
                                  months_back: int = 12,
                                  currency: Currency = Currency.EUR) -> List[Dict[str, Any]]:
        """
        Get monthly revenue trends for analytics and forecasting
        
        Args:
            user_id: User ID to get trends for
            months_back: Number of months to include
            currency: Currency to calculate in
            
        Returns:
            List of monthly revenue data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months_back * 30)
            
            # Query revenue grouped by month
            monthly_data = self.db_session.query(
                extract('year', RevenueTracking.period_start).label('year'),
                extract('month', RevenueTracking.period_start).label('month'),
                func.sum(RevenueTracking.revenue_amount).label('total_revenue'),
                func.count(RevenueTracking.id).label('transaction_count'),
                func.avg(RevenueTracking.revenue_amount).label('avg_revenue')
            ).filter(
                and_(
                    RevenueTracking.user_id == user_id,
                    RevenueTracking.currency == currency,
                    RevenueTracking.period_start >= start_date,
                    RevenueTracking.status != RevenueStatus.PENDING
                )
            ).group_by(
                extract('year', RevenueTracking.period_start),
                extract('month', RevenueTracking.period_start)
            ).order_by(
                extract('year', RevenueTracking.period_start),
                extract('month', RevenueTracking.period_start)
            ).all()
            
            # Format results
            trends = []
            for year, month, total, count, avg in monthly_data:
                trends.append({
                    'year': int(year),
                    'month': int(month),
                    'month_name': datetime(int(year), int(month), 1).strftime('%B'),
                    'total_revenue': float(total or 0),
                    'transaction_count': int(count),
                    'average_revenue': float(avg or 0),
                    'currency': currency.value
                })
            
            # Calculate growth rates
            for i in range(1, len(trends)):
                prev_revenue = trends[i-1]['total_revenue']
                curr_revenue = trends[i]['total_revenue']
                
                if prev_revenue > 0:
                    growth_rate = ((curr_revenue - prev_revenue) / prev_revenue) * 100
                    trends[i]['growth_rate_percent'] = round(growth_rate, 2)
                else:
                    trends[i]['growth_rate_percent'] = 0.0
            
            # Set first month growth rate to 0
            if trends:
                trends[0]['growth_rate_percent'] = 0.0
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get monthly revenue trends: {str(e)}")
            return []
            
    def get_platform_performance(self,
                               user_id: int,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get platform performance analytics
        
        Args:
            user_id: User ID to analyze
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of platform performance data
        """
        try:
            query = self.db_session.query(
                RevenueTracking.platform,
                func.sum(RevenueTracking.revenue_amount).label('total_revenue'),
                func.count(RevenueTracking.id).label('transaction_count'),
                func.avg(RevenueTracking.revenue_amount).label('avg_revenue'),
                func.max(RevenueTracking.revenue_amount).label('max_revenue'),
                func.min(RevenueTracking.revenue_amount).label('min_revenue')
            ).filter(RevenueTracking.user_id == user_id)
            
            # Apply date filters
            if start_date:
                query = query.filter(RevenueTracking.period_start >= start_date)
            if end_date:
                query = query.filter(RevenueTracking.period_end <= end_date)
            
            # Group by platform and order by total revenue
            platform_data = query.group_by(RevenueTracking.platform).order_by(
                desc(func.sum(RevenueTracking.revenue_amount))
            ).all()
            
            # Calculate total for percentage calculations
            total_revenue = sum(float(data.total_revenue or 0) for data in platform_data)
            
            # Format results
            performance_data = []
            for data in platform_data:
                revenue = float(data.total_revenue or 0)
                percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                
                performance_data.append({
                    'platform': data.platform,
                    'total_revenue': revenue,
                    'transaction_count': int(data.transaction_count),
                    'average_revenue': float(data.avg_revenue or 0),
                    'max_revenue': float(data.max_revenue or 0),
                    'min_revenue': float(data.min_revenue or 0),
                    'revenue_percentage': round(percentage, 2)
                })
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Failed to get platform performance: {str(e)}")
            return []
            
    def update_revenue_status(self,
                            revenue_id: int,
                            new_status: RevenueStatus,
                            payment_method: Optional[PaymentMethod] = None,
                            transaction_reference: Optional[str] = None,
                            notes: Optional[str] = None) -> Optional[RevenueTracking]:
        """
        Update revenue status with payment processing information
        
        Args:
            revenue_id: Revenue entry ID
            new_status: New status to set
            payment_method: Payment method used
            transaction_reference: External transaction reference
            notes: Additional notes
            
        Returns:
            Updated RevenueTracking instance
        """
        try:
            revenue_entry = self.get_by_id(revenue_id)
            if not revenue_entry:
                return None
            
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow()
            }
            
            # Add payment information
            if payment_method:
                update_data['payment_method'] = payment_method
                
            # Update metadata with processing info
            metadata = revenue_entry.metadata or {}
            
            if transaction_reference:
                metadata['transaction_reference'] = transaction_reference
                
            if notes:
                metadata['processing_notes'] = notes
                
            # Add status history
            metadata['status_history'] = metadata.get('status_history', [])
            metadata['status_history'].append({
                'previous_status': revenue_entry.status.value,
                'new_status': new_status.value,
                'timestamp': datetime.utcnow().isoformat(),
                'notes': notes
            })
            
            # Set processed timestamp for paid status
            if new_status == RevenueStatus.PAID:
                metadata['paid_at'] = datetime.utcnow().isoformat()
                
            update_data['metadata'] = metadata
            
            updated_revenue = self.update(revenue_id, **update_data)
            
            self.logger.info(
                f"Updated revenue {revenue_id} status: {revenue_entry.status.value} → {new_status.value}"
            )
            
            return updated_revenue
            
        except Exception as e:
            self.logger.error(f"Failed to update revenue status: {str(e)}")
            raise RepositoryException(f"Revenue status update failed: {str(e)}")
            
    def get_pending_payments(self,
                           user_id: Optional[int] = None,
                           minimum_amount: Optional[Decimal] = None,
                           currency: Optional[Currency] = None) -> List[RevenueTracking]:
        """
        Get pending payment entries for processing
        
        Args:
            user_id: Optional user ID filter
            minimum_amount: Optional minimum amount filter
            currency: Optional currency filter
            
        Returns:
            List of pending RevenueTracking instances
        """
        try:
            query = self.db_session.query(RevenueTracking).filter(
                RevenueTracking.status == RevenueStatus.PENDING
            )
            
            if user_id:
                query = query.filter(RevenueTracking.user_id == user_id)
                
            if minimum_amount:
                query = query.filter(RevenueTracking.revenue_amount >= minimum_amount)
                
            if currency:
                query = query.filter(RevenueTracking.currency == currency)
            
            # Order by amount (highest first) then by creation date
            query = query.order_by(
                desc(RevenueTracking.revenue_amount),
                asc(RevenueTracking.created_at)
            )
            
            pending_payments = query.all()
            
            self.logger.debug(f"Retrieved {len(pending_payments)} pending payments")
            
            return pending_payments
            
        except Exception as e:
            self.logger.error(f"Failed to get pending payments: {str(e)}")
            return []
            
    def generate_revenue_report(self,
                              user_id: int,
                              start_date: datetime,
                              end_date: datetime,
                              currency: Currency = Currency.EUR) -> Dict[str, Any]:
        """
        Generate comprehensive revenue report for a user
        
        Args:
            user_id: User ID to generate report for
            start_date: Report start date
            end_date: Report end date
            currency: Currency for calculations
            
        Returns:
            Comprehensive revenue report
        """
        try:
            # Get revenue entries for period
            revenue_entries = self.get_user_revenue(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                currency=currency
            )
            
            if not revenue_entries:
                return {
                    'user_id': user_id,
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat(),
                    'currency': currency.value,
                    'total_revenue': 0.0,
                    'transaction_count': 0,
                    'message': 'No revenue data found for the specified period'
                }
            
            # Calculate basic metrics
            total_revenue = sum(entry.revenue_amount for entry in revenue_entries)
            transaction_count = len(revenue_entries)
            avg_revenue = total_revenue / transaction_count
            
            # Status breakdown
            status_breakdown = {}
            for entry in revenue_entries:
                status = entry.status.value
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            # Platform breakdown
            platform_revenue = {}
            for entry in revenue_entries:
                platform = entry.platform
                platform_revenue[platform] = platform_revenue.get(platform, Decimal('0.00'))
                platform_revenue[platform] += entry.revenue_amount
            
            # Revenue type breakdown
            type_breakdown = {}
            for entry in revenue_entries:
                rev_type = entry.revenue_type.value
                type_breakdown[rev_type] = type_breakdown.get(rev_type, Decimal('0.00'))
                type_breakdown[rev_type] += entry.revenue_amount
            
            # Top earning content
            content_revenue = {}
            for entry in revenue_entries:
                if entry.content_id:
                    content_id = entry.content_id
                    content_revenue[content_id] = content_revenue.get(content_id, Decimal('0.00'))
                    content_revenue[content_id] += entry.revenue_amount
            
            # Sort top content by revenue
            top_content = sorted(
                content_revenue.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10
            
            # Tax status summary
            tax_breakdown = {}
            for entry in revenue_entries:
                tax_status = entry.tax_status.value
                tax_breakdown[tax_status] = tax_breakdown.get(tax_status, 0) + 1
            
            report = {
                'user_id': user_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'currency': currency.value,
                'summary': {
                    'total_revenue': float(total_revenue),
                    'transaction_count': transaction_count,
                    'average_revenue': float(avg_revenue),
                    'highest_single_revenue': float(max(entry.revenue_amount for entry in revenue_entries)),
                    'lowest_single_revenue': float(min(entry.revenue_amount for entry in revenue_entries))
                },
                'breakdowns': {
                    'by_status': status_breakdown,
                    'by_platform': {k: float(v) for k, v in platform_revenue.items()},
                    'by_type': {k: float(v) for k, v in type_breakdown.items()},
                    'by_tax_status': tax_breakdown
                },
                'top_earning_content': [
                    {'content_id': content_id, 'revenue': float(revenue)}
                    for content_id, revenue in top_content
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate revenue report: {str(e)}")
            return {'error': str(e), 'user_id': user_id}
            
    def get_revenue_forecasting_data(self,
                                   user_id: int,
                                   months_back: int = 6) -> Dict[str, Any]:
        """
        Get data for revenue forecasting and trend analysis
        
        Args:
            user_id: User ID to analyze
            months_back: Number of months of historical data
            
        Returns:
            Forecasting data and trends
        """
        try:
            # Get monthly trends
            monthly_trends = self.get_monthly_revenue_trends(
                user_id=user_id,
                months_back=months_back
            )
            
            if len(monthly_trends) < 3:
                return {
                    'user_id': user_id,
                    'insufficient_data': True,
                    'message': 'Insufficient data for forecasting (minimum 3 months required)'
                }
            
            # Calculate trend metrics
            revenues = [month['total_revenue'] for month in monthly_trends]
            
            # Simple linear trend calculation
            n = len(revenues)
            x_values = list(range(n))
            
            # Calculate linear regression coefficients
            x_mean = sum(x_values) / n
            y_mean = sum(revenues) / n
            
            numerator = sum((x_values[i] - x_mean) * (revenues[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Calculate next month forecast
                next_month_forecast = slope * n + intercept
                
                # Calculate trend direction
                trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                
                # Calculate R-squared (coefficient of determination)
                y_pred = [slope * x + intercept for x in x_values]
                ss_res = sum((revenues[i] - y_pred[i]) ** 2 for i in range(n))
                ss_tot = sum((revenues[i] - y_mean) ** 2 for i in range(n))
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
            else:
                slope = 0
                intercept = y_mean
                next_month_forecast = y_mean
                trend_direction = 'stable'
                r_squared = 0
            
            # Calculate volatility (standard deviation)
            if n > 1:
                variance = sum((rev - y_mean) ** 2 for rev in revenues) / (n - 1)
                volatility = variance ** 0.5
            else:
                volatility = 0
            
            forecasting_data = {
                'user_id': user_id,
                'historical_data': monthly_trends,
                'trend_analysis': {
                    'direction': trend_direction,
                    'slope': round(slope, 2),
                    'monthly_growth_rate': round(slope, 2),
                    'r_squared': round(r_squared, 3),
                    'volatility': round(volatility, 2)
                },
                'forecast': {
                    'next_month_estimate': round(max(0, next_month_forecast), 2),
                    'confidence_level': 'high' if r_squared > 0.8 else 'medium' if r_squared > 0.5 else 'low',
                    'forecast_range': {
                        'optimistic': round(max(0, next_month_forecast + volatility), 2),
                        'pessimistic': round(max(0, next_month_forecast - volatility), 2)
                    }
                },
                'metrics': {
                    'average_monthly_revenue': round(y_mean, 2),
                    'best_month': max(revenues),
                    'worst_month': min(revenues),
                    'consistency_score': round((1 - volatility / y_mean) * 100, 2) if y_mean > 0 else 0
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return forecasting_data
            
        except Exception as e:
            self.logger.error(f"Failed to get forecasting data: {str(e)}")
            return {'error': str(e), 'user_id': user_id}

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
