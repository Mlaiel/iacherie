"""Payment Processing Database Migration Scripts

Advanced database migration utilities for payment processing schema management,
version control, and data migration operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Payment Systems Specialist + Database Administrator
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Any, List, Optional, Callable
from sqlalchemy import (
    text, MetaData, Table, Column, Integer, String, DateTime,
    Boolean, create_engine, inspect
)
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """
Exception for migration-related errors"""
    pass


class Migration:
    """
Base class for database migrations"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.utcnow()
        self.checksum = self._calculate_checksum()
    
    def up(self, engine) -> None:
        """
Apply migration (must be implemented by subclasses)"""
        pass
    
    def down(self, engine) -> None:
        """
Rollback migration (must be implemented by subclasses)"""
        pass
    
    def _calculate_checksum(self) -> str:
        """
Calculate migration checksum"""
        content = f"{self.version}:{self.description}:{self.__class__.__name__}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()


class MigrationManager:
    """Manager for database migration operations"""
    
    def __init__(self, engine, migration_table: str = "payment_migrations"):
        self.engine = engine
        self.migration_table = migration_table
        self.migrations: List[Migration] = []
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Ensure migration tracking table exists"""
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migration_table} (
            id SERIAL PRIMARY KEY,
            version VARCHAR(50) NOT NULL UNIQUE,
            description TEXT NOT NULL,
            checksum VARCHAR(32) NOT NULL,
            applied_at TIMESTAMP DEFAULT NOW(),
            applied_by VARCHAR(100) DEFAULT CURRENT_USER,
            execution_time_ms INTEGER,
            rollback_sql TEXT
        )
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(create_sql))
            conn.commit()
    
    def register_migration(self, migration: Migration):
        """
Register a migration"""
        self.migrations.append(migration)
        logger.info(f"Registered migration {migration.version}: {migration.description}")
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations"""
        query = f"SELECT * FROM {self.migration_table} ORDER BY applied_at"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return [dict(row._mapping) for row in result]
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        applied_versions = {
            row['version'] for row in self.get_applied_migrations()
        }
        
        return [
            migration for migration in self.migrations
            if migration.version not in applied_versions
        ]
    
    def apply_migration(self, migration: Migration) -> bool:
        """
Apply a single migration"""
        try:
            start_time = datetime.utcnow()
            
            # Execute migration
            migration.up(self.engine)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Record migration
            insert_sql = f"""
            INSERT INTO {self.migration_table} 
            (version, description, checksum, execution_time_ms)
            VALUES (%(version)s, %(description)s, %(checksum)s, %(execution_time)s)
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), {
                    'version': migration.version,
                    'description': migration.description,
                    'checksum': migration.checksum,
                    'execution_time': int(execution_time)
                })
                conn.commit()
            
            logger.info(f"Applied migration {migration.version} in {execution_time:.2f}ms")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {str(e)}")
            raise MigrationError(f"Migration {migration.version} failed: {str(e)}")
    
    def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration"""
        try:
            # Execute rollback
            migration.down(self.engine)
            
            # Remove migration record
            delete_sql = f"DELETE FROM {self.migration_table} WHERE version = %(version)s"
            
            with self.engine.connect() as conn:
                conn.execute(text(delete_sql), {'version': migration.version})
                conn.commit()
            
            logger.info(f"Rolled back migration {migration.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {str(e)}")
            raise MigrationError(f"Rollback {migration.version} failed: {str(e)}")
    
    def migrate_up(self, target_version: Optional[str] = None) -> int:
        """Apply all pending migrations up to target version"""
        pending = self.get_pending_migrations()
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        applied_count = 0
        for migration in sorted(pending, key=lambda m: m.version):
            self.apply_migration(migration)
            applied_count += 1
        
        logger.info(f"Applied {applied_count} migrations")
        return applied_count
    
    def migrate_down(self, target_version: str) -> int:
        """Rollback migrations down to target version"""
        applied = self.get_applied_migrations()
        to_rollback = [
            row for row in applied
            if row['version'] > target_version
        ]
        
        rollback_count = 0
        for migration_row in sorted(to_rollback, key=lambda r: r['version'], reverse=True):
            # Find migration object
            migration = next(
                (m for m in self.migrations if m.version == migration_row['version']),
                None
            )
            
            if migration:
                self.rollback_migration(migration)
                rollback_count += 1
            else:
                logger.warning(f"Migration {migration_row['version']} not found for rollback")
        
        logger.info(f"Rolled back {rollback_count} migrations")
        return rollback_count


# Specific migrations for payment processing
class CreatePaymentTransactionsMigration(Migration):
    """Migration to create payment_transactions table"""
    
    def __init__(self):
        super().__init__("001", "Create payment_transactions table")
    
    def up(self, engine):
        sql = """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            payment_method_id UUID,
            transaction_type VARCHAR(50) NOT NULL,
            amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            external_transaction_id VARCHAR(255),
            platform_reference VARCHAR(100),
            gross_amount DECIMAL(15,2) NOT NULL,
            fees_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
            net_amount DECIMAL(15,2) NOT NULL,
            tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
            processor VARCHAR(50) NOT NULL,
            processor_response JSONB,
            gateway_reference VARCHAR(255),
            content_id INTEGER,
            revenue_tracking_id INTEGER,
            description TEXT,
            metadata JSONB,
            ip_address INET,
            user_agent TEXT,
            initiated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            processed_at TIMESTAMP WITH TIME ZONE,
            settled_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_payment_transactions_user_id ON payment_transactions(user_id);
        CREATE INDEX idx_payment_transactions_status ON payment_transactions(status);
        CREATE INDEX idx_payment_transactions_created_at ON payment_transactions(created_at);
        CREATE INDEX idx_payment_transactions_external_id ON payment_transactions(external_transaction_id);
        CREATE INDEX idx_payment_transactions_user_status ON payment_transactions(user_id, status);
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = "DROP TABLE IF EXISTS payment_transactions CASCADE"
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


class CreatePaymentMethodsMigration(Migration):
    """Migration to create payment_methods table"""
    
    def __init__(self):
        super().__init__("002", "Create payment_methods table")
    
    def up(self, engine):
        sql = """
        CREATE TABLE IF NOT EXISTS payment_methods (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            method_type VARCHAR(50) NOT NULL,
            provider VARCHAR(50) NOT NULL,
            external_id VARCHAR(255),
            last_four_digits VARCHAR(4),
            brand VARCHAR(50),
            exp_month INTEGER CHECK (exp_month BETWEEN 1 AND 12),
            exp_year INTEGER CHECK (exp_year BETWEEN 2024 AND 2050),
            bank_name VARCHAR(255),
            account_type VARCHAR(50),
            routing_number_last_four VARCHAR(4),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            is_default BOOLEAN NOT NULL DEFAULT FALSE,
            fingerprint VARCHAR(255),
            billing_address JSONB,
            verification_data JSONB,
            nickname VARCHAR(100),
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            verified_at TIMESTAMP WITH TIME ZONE,
            last_used_at TIMESTAMP WITH TIME ZONE,
            
            CONSTRAINT uq_user_external_provider UNIQUE(user_id, external_id, provider)
        );
        
        CREATE INDEX idx_payment_methods_user_id ON payment_methods(user_id);
        CREATE INDEX idx_payment_methods_user_active ON payment_methods(user_id, is_active);
        CREATE INDEX idx_payment_methods_user_default ON payment_methods(user_id, is_default);
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = "DROP TABLE IF EXISTS payment_methods CASCADE"
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


class CreateBillingRecordsMigration(Migration):
    """Migration to create billing_records table"""
    
    def __init__(self):
        super().__init__("003", "Create billing_records table")
    
    def up(self, engine):
        sql = """
        CREATE TABLE IF NOT EXISTS billing_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            transaction_id UUID,
            subscription_type VARCHAR(100) NOT NULL,
            billing_frequency VARCHAR(20) NOT NULL,
            amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            billing_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
            billing_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
            due_date TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            is_prorated BOOLEAN NOT NULL DEFAULT FALSE,
            proration_details JSONB,
            invoice_number VARCHAR(100) UNIQUE,
            invoice_url VARCHAR(255),
            tax_details JSONB,
            usage_metrics JSONB,
            overage_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            billed_at TIMESTAMP WITH TIME ZONE,
            paid_at TIMESTAMP WITH TIME ZONE,
            
            CONSTRAINT check_billing_period CHECK (billing_period_end > billing_period_start)
        );
        
        CREATE INDEX idx_billing_records_user_id ON billing_records(user_id);
        CREATE INDEX idx_billing_records_user_status ON billing_records(user_id, status);
        CREATE INDEX idx_billing_records_due_date ON billing_records(due_date);
        CREATE INDEX idx_billing_records_period ON billing_records(billing_period_start, billing_period_end);
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = "DROP TABLE IF EXISTS billing_records CASCADE"
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


class CreateFinancialRecordsMigration(Migration):
    """Migration to create financial_records table"""
    
    def __init__(self):
        super().__init__("004", "Create financial_records table")
    
    def up(self, engine):
        sql = """
        CREATE TABLE IF NOT EXISTS financial_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            record_type VARCHAR(50) NOT NULL,
            category VARCHAR(100) NOT NULL,
            subcategory VARCHAR(100),
            amount DECIMAL(15,2) NOT NULL,
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            exchange_rate DECIMAL(10,6),
            base_currency_amount DECIMAL(15,2),
            source_platform VARCHAR(100),
            reference_id VARCHAR(255),
            external_reference VARCHAR(255),
            content_id INTEGER,
            revenue_source VARCHAR(100),
            tax_category VARCHAR(50),
            tax_rate DECIMAL(5,4),
            tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
            is_tax_deductible BOOLEAN NOT NULL DEFAULT FALSE,
            transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
            recorded_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            accounting_period VARCHAR(7) NOT NULL,
            description TEXT,
            metadata JSONB,
            supporting_documents TEXT[],
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_financial_records_user_id ON financial_records(user_id);
        CREATE INDEX idx_financial_records_user_type ON financial_records(user_id, record_type);
        CREATE INDEX idx_financial_records_period ON financial_records(accounting_period);
        CREATE INDEX idx_financial_records_transaction_date ON financial_records(transaction_date);
        CREATE INDEX idx_financial_records_content ON financial_records(content_id);
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = "DROP TABLE IF EXISTS financial_records CASCADE"
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


class CreateAutomatedPayoutsMigration(Migration):
    """Migration to create automated_payouts table"""
    
    def __init__(self):
        super().__init__("005", "Create automated_payouts table")
    
    def up(self, engine):
        sql = """
        CREATE TABLE IF NOT EXISTS automated_payouts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            payment_method_id UUID NOT NULL,
            payout_frequency VARCHAR(20) NOT NULL,
            minimum_amount DECIMAL(15,2) NOT NULL DEFAULT 50.00,
            currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
            total_amount DECIMAL(15,2) NOT NULL CHECK (total_amount > 0),
            fees_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
            net_amount DECIMAL(15,2) NOT NULL,
            period_start TIMESTAMP WITH TIME ZONE NOT NULL,
            period_end TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            processor VARCHAR(50) NOT NULL,
            external_payout_id VARCHAR(255),
            revenue_breakdown JSONB,
            content_items_count INTEGER NOT NULL DEFAULT 0,
            platforms_count INTEGER NOT NULL DEFAULT 0,
            is_approved BOOLEAN NOT NULL DEFAULT FALSE,
            approved_by INTEGER,
            approved_at TIMESTAMP WITH TIME ZONE,
            scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
            processed_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
            last_error TEXT,
            error_details JSONB,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            
            CONSTRAINT check_payout_period CHECK (period_end > period_start)
        );
        
        CREATE INDEX idx_automated_payouts_user_id ON automated_payouts(user_id);
        CREATE INDEX idx_automated_payouts_user_status ON automated_payouts(user_id, status);
        CREATE INDEX idx_automated_payouts_scheduled ON automated_payouts(scheduled_at);
        CREATE INDEX idx_automated_payouts_period ON automated_payouts(period_start, period_end);
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = "DROP TABLE IF EXISTS automated_payouts CASCADE"
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


class AddForeignKeysMigration(Migration):
    """Migration to add foreign key constraints"""
    
    def __init__(self):
        super().__init__("006", "Add foreign key constraints")
    
    def up(self, engine):
        sql = """
        -- Add foreign key from payment_transactions to payment_methods
        ALTER TABLE payment_transactions 
        ADD CONSTRAINT fk_payment_transactions_payment_method 
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id);
        
        -- Add foreign key from billing_records to payment_transactions
        ALTER TABLE billing_records 
        ADD CONSTRAINT fk_billing_records_transaction 
        FOREIGN KEY (transaction_id) REFERENCES payment_transactions(id);
        
        -- Add foreign key from automated_payouts to payment_methods
        ALTER TABLE automated_payouts 
        ADD CONSTRAINT fk_automated_payouts_payment_method 
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id);
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = """
        ALTER TABLE payment_transactions DROP CONSTRAINT IF EXISTS fk_payment_transactions_payment_method;
        ALTER TABLE billing_records DROP CONSTRAINT IF EXISTS fk_billing_records_transaction;
        ALTER TABLE automated_payouts DROP CONSTRAINT IF EXISTS fk_automated_payouts_payment_method;
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


class AddUpdateTriggersMigration(Migration):
    """
Migration to add update timestamp triggers"""
    
    def __init__(self):
        super().__init__("007", "Add update timestamp triggers")
    
    def up(self, engine):
        sql = """
        -- Create trigger function for updating timestamp
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Add triggers for all tables
        CREATE TRIGGER update_payment_transactions_updated_at 
            BEFORE UPDATE ON payment_transactions 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        
        CREATE TRIGGER update_payment_methods_updated_at 
            BEFORE UPDATE ON payment_methods 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        
        CREATE TRIGGER update_billing_records_updated_at 
            BEFORE UPDATE ON billing_records 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        
        CREATE TRIGGER update_financial_records_updated_at 
            BEFORE UPDATE ON financial_records 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        
        CREATE TRIGGER update_automated_payouts_updated_at 
            BEFORE UPDATE ON automated_payouts 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
    
    def down(self, engine):
        sql = """
        DROP TRIGGER IF EXISTS update_payment_transactions_updated_at ON payment_transactions;
        DROP TRIGGER IF EXISTS update_payment_methods_updated_at ON payment_methods;
        DROP TRIGGER IF EXISTS update_billing_records_updated_at ON billing_records;
        DROP TRIGGER IF EXISTS update_financial_records_updated_at ON financial_records;
        DROP TRIGGER IF EXISTS update_automated_payouts_updated_at ON automated_payouts;
        DROP FUNCTION IF EXISTS update_updated_at_column();
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()


def create_migration_manager(engine) -> MigrationManager:
    """
Create and configure migration manager with all migrations"""
    manager = MigrationManager(engine)
    
    # Register all migrations in order
    manager.register_migration(CreatePaymentTransactionsMigration())
    manager.register_migration(CreatePaymentMethodsMigration())
    manager.register_migration(CreateBillingRecordsMigration())
    manager.register_migration(CreateFinancialRecordsMigration())
    manager.register_migration(CreateAutomatedPayoutsMigration())
    manager.register_migration(AddForeignKeysMigration())
    manager.register_migration(AddUpdateTriggersMigration())
    
    return manager


def run_migrations(engine, target_version: Optional[str] = None) -> int:
    """
Run all pending migrations"""
    manager = create_migration_manager(engine)
    return manager.migrate_up(target_version)


def rollback_migrations(engine, target_version: str) -> int:
    """
Rollback migrations to target version"""
    manager = create_migration_manager(engine)
    return manager.migrate_down(target_version)
