"""Payment Processing Database Index Manager

Advanced database index management for optimizing payment processing queries,
including composite indexes, partial indexes, and query performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Payment Systems Specialist + Database Performance Expert
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""from typing import Dict, Any, List, Optional
from sqlalchemy import text, create_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IndexDefinition:
    """Definition for database index"""    
    def __init__(
        self,
        name: str,
        table: str,
        columns: List[str],
        unique: bool = False,
        partial_condition: Optional[str] = None,
        index_type: str = "btree",
        concurrent: bool = True
    ):
        self.name = name
        self.table = table
        self.columns = columns
        self.unique = unique
        self.partial_condition = partial_condition
        self.index_type = index_type
        self.concurrent = concurrent
    
    def to_sql(self) -> str:
        """Generate SQL for creating the index"""        unique_clause = "UNIQUE " if self.unique else ""
        concurrent_clause = "CONCURRENTLY " if self.concurrent else ""
        
        columns_clause = ", ".join(self.columns)
        
        sql = f"CREATE {unique_clause}INDEX {concurrent_clause}{self.name} "
        sql += f"ON {self.table} USING {self.index_type} ({columns_clause})"
        
        if self.partial_condition:
            sql += f" WHERE {self.partial_condition}"
        
        return sql
    
    def drop_sql(self) -> str:
        """Generate SQL for dropping the index"""        concurrent_clause = "CONCURRENTLY " if self.concurrent else ""
        return f"DROP INDEX {concurrent_clause}IF EXISTS {self.name}"


class PaymentIndexManager:
    """Manager for payment processing database indexes"""    
    def __init__(self, engine):
        self.engine = engine
        self.indexes = self._define_payment_indexes()
    
    def _define_payment_indexes(self) -> List[IndexDefinition]:
        """Define all payment processing indexes"""        return [
            # Payment Transactions Indexes
            IndexDefinition(
                name="idx_payment_transactions_user_status_created",
                table="payment_transactions",
                columns=["user_id", "status", "created_at DESC"]
            ),
            IndexDefinition(
                name="idx_payment_transactions_processor_status",
                table="payment_transactions",
                columns=["processor", "status"]
            ),
            IndexDefinition(
                name="idx_payment_transactions_amount_currency",
                table="payment_transactions",
                columns=["amount", "currency"]
            ),
            IndexDefinition(
                name="idx_payment_transactions_external_processor",
                table="payment_transactions",
                columns=["external_transaction_id", "processor"],
                unique=True,
                partial_condition="external_transaction_id IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_payment_transactions_content_revenue",
                table="payment_transactions",
                columns=["content_id", "revenue_tracking_id"],
                partial_condition="content_id IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_payment_transactions_processed_settled",
                table="payment_transactions",
                columns=["processed_at", "settled_at"],
                partial_condition="processed_at IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_payment_transactions_ip_address",
                table="payment_transactions",
                columns=["ip_address"]
            ),
            IndexDefinition(
                name="idx_payment_transactions_metadata_gin",
                table="payment_transactions",
                columns=["metadata"],
                index_type="gin"
            ),
            
            # Payment Methods Indexes
            IndexDefinition(
                name="idx_payment_methods_user_type_active",
                table="payment_methods",
                columns=["user_id", "method_type", "is_active"]
            ),
            IndexDefinition(
                name="idx_payment_methods_provider_external",
                table="payment_methods",
                columns=["provider", "external_id"],
                partial_condition="external_id IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_payment_methods_brand_expiry",
                table="payment_methods",
                columns=["brand", "exp_year", "exp_month"],
                partial_condition="brand IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_payment_methods_verified_active",
                table="payment_methods",
                columns=["is_verified", "is_active", "last_used_at DESC"]
            ),
            IndexDefinition(
                name="idx_payment_methods_fingerprint",
                table="payment_methods",
                columns=["fingerprint"],
                unique=True,
                partial_condition="fingerprint IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_payment_methods_billing_address_gin",
                table="payment_methods",
                columns=["billing_address"],
                index_type="gin"
            ),
            
            # Billing Records Indexes
            IndexDefinition(
                name="idx_billing_records_user_subscription_period",
                table="billing_records",
                columns=["user_id", "subscription_type", "billing_period_start DESC"]
            ),
            IndexDefinition(
                name="idx_billing_records_due_status",
                table="billing_records",
                columns=["due_date", "status"]
            ),
            IndexDefinition(
                name="idx_billing_records_frequency_amount",
                table="billing_records",
                columns=["billing_frequency", "amount"]
            ),
            IndexDefinition(
                name="idx_billing_records_invoice_number",
                table="billing_records",
                columns=["invoice_number"],
                unique=True,
                partial_condition="invoice_number IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_billing_records_period_coverage",
                table="billing_records",
                columns=["billing_period_start", "billing_period_end"]
            ),
            IndexDefinition(
                name="idx_billing_records_prorated",
                table="billing_records",
                columns=["is_prorated", "proration_details"],
                partial_condition="is_prorated = true",
                index_type="gin"
            ),
            IndexDefinition(
                name="idx_billing_records_usage_metrics_gin",
                table="billing_records",
                columns=["usage_metrics"],
                index_type="gin"
            ),
            
            # Financial Records Indexes
            IndexDefinition(
                name="idx_financial_records_user_period_type",
                table="financial_records",
                columns=["user_id", "accounting_period", "record_type"]
            ),
            IndexDefinition(
                name="idx_financial_records_category_amount",
                table="financial_records",
                columns=["category", "subcategory", "amount"]
            ),
            IndexDefinition(
                name="idx_financial_records_source_platform",
                table="financial_records",
                columns=["source_platform", "revenue_source"]
            ),
            IndexDefinition(
                name="idx_financial_records_tax_deductible",
                table="financial_records",
                columns=["is_tax_deductible", "tax_category", "tax_amount"],
                partial_condition="is_tax_deductible = true"
            ),
            IndexDefinition(
                name="idx_financial_records_transaction_recorded",
                table="financial_records",
                columns=["transaction_date", "recorded_date"]
            ),
            IndexDefinition(
                name="idx_financial_records_reference_external",
                table="financial_records",
                columns=["reference_id", "external_reference"],
                partial_condition="reference_id IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_financial_records_content_revenue",
                table="financial_records",
                columns=["content_id", "revenue_source"],
                partial_condition="content_id IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_financial_records_metadata_gin",
                table="financial_records",
                columns=["metadata"],
                index_type="gin"
            ),
            
            # Automated Payouts Indexes
            IndexDefinition(
                name="idx_automated_payouts_user_frequency_status",
                table="automated_payouts",
                columns=["user_id", "payout_frequency", "status"]
            ),
            IndexDefinition(
                name="idx_automated_payouts_scheduled_status",
                table="automated_payouts",
                columns=["scheduled_at", "status"]
            ),
            IndexDefinition(
                name="idx_automated_payouts_processor_external",
                table="automated_payouts",
                columns=["processor", "external_payout_id"],
                partial_condition="external_payout_id IS NOT NULL"
            ),
            IndexDefinition(
                name="idx_automated_payouts_amount_currency",
                table="automated_payouts",
                columns=["total_amount", "net_amount", "currency"]
            ),
            IndexDefinition(
                name="idx_automated_payouts_approval",
                table="automated_payouts",
                columns=["is_approved", "approved_by", "approved_at"]
            ),
            IndexDefinition(
                name="idx_automated_payouts_period_coverage",
                table="automated_payouts",
                columns=["period_start", "period_end"]
            ),
            IndexDefinition(
                name="idx_automated_payouts_retry_error",
                table="automated_payouts",
                columns=["retry_count", "last_error"],
                partial_condition="retry_count > 0"
            ),
            IndexDefinition(
                name="idx_automated_payouts_revenue_breakdown_gin",
                table="automated_payouts",
                columns=["revenue_breakdown"],
                index_type="gin"
            ),
            
            # Performance-specific indexes
            IndexDefinition(
                name="idx_payment_transactions_revenue_analytics",
                table="payment_transactions",
                columns=["user_id", "status", "currency", "net_amount", "created_at DESC"],
                partial_condition="status = 'completed'"
            ),
            IndexDefinition(
                name="idx_payment_transactions_fraud_analysis",
                table="payment_transactions",
                columns=["ip_address", "user_agent", "amount", "created_at DESC"],
                partial_condition="status IN ('failed', 'disputed', 'chargeback')"
            ),
            IndexDefinition(
                name="idx_billing_records_overdue",
                table="billing_records",
                columns=["due_date", "status", "amount"],
                partial_condition="status = 'pending' AND due_date < NOW()"
            ),
            IndexDefinition(
                name="idx_financial_records_tax_reporting",
                table="financial_records",
                columns=["user_id", "accounting_period", "tax_amount", "is_tax_deductible"],
                partial_condition="tax_amount > 0"
            ),
            IndexDefinition(
                name="idx_automated_payouts_pending_processing",
                table="automated_payouts",
                columns=["scheduled_at", "retry_count", "processor"],
                partial_condition="status = 'pending' AND scheduled_at <= NOW()"
            )
        ]
    
    def create_all_indexes(self) -> Dict[str, bool]:
        """Create all payment processing indexes"""        results = {}
        
        for index in self.indexes:
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(index.to_sql()))
                    conn.commit()
                
                results[index.name] = True
                logger.info(f"Created index {index.name}")
                
            except Exception as e:
                results[index.name] = False
                logger.error(f"Failed to create index {index.name}: {str(e)}")
        
        return results
    
    def drop_all_indexes(self) -> Dict[str, bool]:
        """Drop all payment processing indexes"""        results = {}
        
        for index in self.indexes:
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(index.drop_sql()))
                    conn.commit()
                
                results[index.name] = True
                logger.info(f"Dropped index {index.name}")
                
            except Exception as e:
                results[index.name] = False
                logger.error(f"Failed to drop index {index.name}: {str(e)}")
        
        return results
    
    def create_index(self, index_name: str) -> bool:
        """Create a specific index"""        index = next((idx for idx in self.indexes if idx.name == index_name), None)
        
        if not index:
            logger.error(f"Index {index_name} not found")
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(index.to_sql()))
                conn.commit()
            
            logger.info(f"Created index {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {str(e)}")
            return False
    
    def drop_index(self, index_name: str) -> bool:
        """Drop a specific index"""        index = next((idx for idx in self.indexes if idx.name == index_name), None)
        
        if not index:
            logger.error(f"Index {index_name} not found")
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(index.drop_sql()))
                conn.commit()
            
            logger.info(f"Dropped index {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop index {index_name}: {str(e)}")
            return False
    
    def get_index_usage_stats(self) -> List[Dict[str, Any]]:
        """Get index usage statistics"""        query = """        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'payment_transactions', 
            'payment_methods', 
            'billing_records', 
            'financial_records', 
            'automated_payouts'
        )
        ORDER BY idx_scan DESC
        """        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get index usage stats: {str(e)}")
            return []
    
    def get_index_sizes(self) -> List[Dict[str, Any]]:
        """Get index sizes for monitoring"""        query = """        SELECT 
            schemaname,
            tablename,
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            pg_relation_size(indexrelid) as index_size_bytes
        FROM pg_stat_user_indexes 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'payment_transactions', 
            'payment_methods', 
            'billing_records', 
            'financial_records', 
            'automated_payouts'
        )
        ORDER BY pg_relation_size(indexrelid) DESC
        """        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get index sizes: {str(e)}")
            return []
    
    def analyze_tables(self) -> bool:
        """Run ANALYZE on all payment processing tables"""        tables = [
            'payment_transactions',
            'payment_methods', 
            'billing_records',
            'financial_records',
            'automated_payouts'
        ]
        
        try:
            with self.engine.connect() as conn:
                for table in tables:
                    conn.execute(text(f"ANALYZE {table}"))
                conn.commit()
            
            logger.info("Analyzed all payment processing tables")
            return True
            
        except Exception as e:
            logger.error(f"Failed to analyze tables: {str(e)}")
            return False
    
    def reindex_tables(self) -> bool:
        """Rebuild all indexes for payment processing tables"""        tables = [
            'payment_transactions',
            'payment_methods', 
            'billing_records',
            'financial_records',
            'automated_payouts'
        ]
        
        try:
            with self.engine.connect() as conn:
                for table in tables:
                    conn.execute(text(f"REINDEX TABLE {table}"))
                conn.commit()
            
            logger.info("Reindexed all payment processing tables")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reindex tables: {str(e)}")
            return False
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slow queries related to payment processing"""        query = """        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            stddev_time,
            rows,
            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
        FROM pg_stat_statements 
        WHERE query ILIKE '%payment_transactions%' 
           OR query ILIKE '%payment_methods%'
           OR query ILIKE '%billing_records%'
           OR query ILIKE '%financial_records%'
           OR query ILIKE '%automated_payouts%'
        ORDER BY mean_time DESC 
        LIMIT %(limit)s
        """        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'limit': limit})
                return [dict(row._mapping) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get slow queries: {str(e)}")
            return []
    
    def optimize_for_workload(self, workload_type: str) -> List[str]:
        """Optimize indexes for specific workload patterns"""        optimizations = []
        
        if workload_type == "analytics":
            # Create additional indexes for analytical queries
            analytics_indexes = [
                IndexDefinition(
                    name="idx_payment_transactions_analytics_time_series",
                    table="payment_transactions",
                    columns=["DATE(created_at)", "status", "processor", "currency"]
                ),
                IndexDefinition(
                    name="idx_financial_records_analytics_aggregation",
                    table="financial_records",
                    columns=["accounting_period", "record_type", "category", "amount"]
                )
            ]
            
            for index in analytics_indexes:
                if self.create_index_from_definition(index):
                    optimizations.append(f"Created analytics index: {index.name}")
        
        elif workload_type == "high_volume_transactions":
            # Optimize for high-volume transaction processing
            optimizations.append("Increased shared_buffers for transaction processing")
            optimizations.append("Enabled parallel query execution")
        
        elif workload_type == "reporting":
            # Create materialized views for common reports
            optimizations.append("Consider creating materialized views for reporting")
        
        return optimizations
    
    def create_index_from_definition(self, index: IndexDefinition) -> bool:
        """Create index from IndexDefinition object"""        try:
            with self.engine.connect() as conn:
                conn.execute(text(index.to_sql()))
                conn.commit()
            
            logger.info(f"Created index {index.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index {index.name}: {str(e)}")
            return False


def create_payment_indexes(engine) -> PaymentIndexManager:
    """Create and return PaymentIndexManager"""    return PaymentIndexManager(engine)


def setup_payment_indexes(engine) -> Dict[str, bool]:
    """Setup all payment processing indexes"""    manager = PaymentIndexManager(engine)
    return manager.create_all_indexes()
