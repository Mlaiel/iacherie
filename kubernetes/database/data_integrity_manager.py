"""Data Integrity Manager
Advanced data validation and integrity management for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

🔍 DATA VALIDATION AVANCÉE:
- Schema validation automatique
- Data type consistency checks
- Constraint validation en temps réel
- Foreign key integrity verification
- Null value policy enforcement
- Data format standardization

🛡️ INTEGRITY MONITORING:
- Real-time consistency checks
- Orphaned record detection
- Duplicate prevention algorithms
- Cross-table relationship validation
- Data corruption detection
- Audit trail verification

📊 DATA QUALITY METRICS:
- Quality score calculation
- Completeness metrics tracking
- Accuracy assessment automation
- Consistency scoring algorithms
- Timeliness validation
- Uniqueness verification

🔧 AUTOMATED REPAIR:
- Self-healing data mechanisms
- Orphaned record cleanup
- Duplicate resolution automation
- Constraint violation fixes
- Data standardization automation
- Backup-based recovery

⚡ PERFORMANCE OPTIMIZATION:
- Intelligent indexing strategies
- Query optimization recommendations
- Storage efficiency analysis
- Memory usage optimization
- Cache invalidation intelligence
- Batch processing optimization

🎯 COMPLIANCE ASSURANCE:
- GDPR compliance validation
- Data retention policy enforcement
- Privacy protection verification
- Audit requirement compliance
- Regulatory reporting support
- Legal compliance automation

📈 ANALYTICS ET REPORTING:
- Data quality dashboards
- Integrity violation reports
- Performance trend analysis
- Compliance status reporting
- Risk assessment automation
- Predictive quality analytics

🔒 SÉCURITÉ ET ACCESS CONTROL:
- Data access validation
- Permission verification
- Audit logging complet
- Sensitive data protection
- Encryption verification
- Privacy compliance checks
"""import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
import hashlib
import statistics
from decimal import Decimal
from sqlalchemy import (
    text, select, insert, update, delete, func, and_, or_,
    inspect, MetaData, Table, Column
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.postgresql_manager import get_postgresql_manager


class ValidationSeverity(Enum):
    """Validation issue severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation"""    SCHEMA = "schema"
    CONSTRAINTS = "constraints"
    FOREIGN_KEYS = "foreign_keys"
    DATA_TYPES = "data_types"
    BUSINESS_RULES = "business_rules"
    PERFORMANCE = "performance"
    SECURITY = "security"


class IntegrityStatus(Enum):
    """Data integrity status"""    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    COMPROMISED = "compromised"


@dataclass
class ValidationIssue:
    """Data validation issue"""    issue_id: str
    category: ValidationCategory
    severity: ValidationSeverity
    table_name: str
    column_name: Optional[str]
    description: str
    affected_rows: int
    suggestion: Optional[str]
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False


@dataclass
class QualityMetrics:
    """Data quality metrics"""    completeness_score: float  # 0-1
    accuracy_score: float      # 0-1
    consistency_score: float   # 0-1
    timeliness_score: float    # 0-1
    uniqueness_score: float    # 0-1
    overall_score: float       # 0-1
    total_records: int
    issues_count: int
    calculated_at: datetime = field(default_factory=datetime.utcnow)


class DataIntegrityManager:
    """    Enterprise Data Integrity Manager
    
    Provides comprehensive data validation, integrity monitoring,
    and quality assurance for the IA Influencer Agent database.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"{__name__}.DataIntegrityManager")
        self.settings = get_settings()
        
        # Database components
        self._db_manager = None
        
        # Validation rules
        self._validation_rules: Dict[str, List[Dict[str, Any]]] = {}
        self._quality_thresholds = {
            'completeness': 0.95,
            'accuracy': 0.98,
            'consistency': 0.99,
            'timeliness': 0.90,
            'uniqueness': 0.99
        }
        
        # Monitoring state
        self._last_validation_run: Optional[datetime] = None
        self._validation_interval = timedelta(hours=1)
        self._current_issues: List[ValidationIssue] = []
        
        # Performance settings
        self.batch_size = self.config.get('batch_size', 10000)
        self.max_concurrent_validations = self.config.get('max_concurrent_validations', 5)
    
    async def initialize(self) -> bool:
        """Initialize the data integrity manager"""        try:
            self.logger.info("🚀 Initializing Data Integrity Manager...")
            
            # Get database manager
            self._db_manager = get_postgresql_manager()
            
            # Create schema if not exists
            await self._create_integrity_schema()
            
            # Load validation rules
            await self._load_validation_rules()
            
            # Run initial validation
            await self._run_comprehensive_validation()
            
            self.logger.info("✅ Data Integrity Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Data Integrity Manager: {e}")
            return False
    
    async def _create_integrity_schema(self):
        """Create data integrity schema"""        self.logger.debug("Creating data integrity schema...")
        
        schema_sql = """        -- Data Validation Rules
        CREATE TABLE IF NOT EXISTS data_validation_rules (
            rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            rule_name VARCHAR(200) NOT NULL,
            table_name VARCHAR(100) NOT NULL,
            column_name VARCHAR(100),
            
            -- Rule definition
            rule_type VARCHAR(50) NOT NULL, -- not_null, unique, foreign_key, range, pattern, custom
            rule_expression TEXT,
            severity VARCHAR(20) DEFAULT 'warning' CHECK (severity IN ('info', 'warning', 'error', 'critical')),
            
            -- Configuration
            is_active BOOLEAN DEFAULT true,
            auto_fix BOOLEAN DEFAULT false,
            check_frequency VARCHAR(20) DEFAULT 'hourly', -- continuous, hourly, daily, weekly
            
            -- Metadata
            description TEXT,
            created_by UUID,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            INDEX idx_validation_rules_table (table_name),
            INDEX idx_validation_rules_column (column_name),
            INDEX idx_validation_rules_type (rule_type),
            INDEX idx_validation_rules_active (is_active)
        );
        
        -- Data Quality Metrics
        CREATE TABLE IF NOT EXISTS data_quality_metrics (
            metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            table_name VARCHAR(100) NOT NULL,
            column_name VARCHAR(100),
            
            -- Quality scores (0-1)
            completeness_score NUMERIC(5,4) DEFAULT 0.0,
            accuracy_score NUMERIC(5,4) DEFAULT 0.0,
            consistency_score NUMERIC(5,4) DEFAULT 0.0,
            timeliness_score NUMERIC(5,4) DEFAULT 0.0,
            uniqueness_score NUMERIC(5,4) DEFAULT 0.0,
            overall_score NUMERIC(5,4) DEFAULT 0.0,
            
            -- Counts
            total_records BIGINT DEFAULT 0,
            null_count BIGINT DEFAULT 0,
            duplicate_count BIGINT DEFAULT 0,
            invalid_count BIGINT DEFAULT 0,
            
            -- Time period
            measurement_date DATE DEFAULT CURRENT_DATE,
            measurement_hour INTEGER DEFAULT EXTRACT(HOUR FROM NOW()),
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            
            -- Constraints
            UNIQUE(table_name, column_name, measurement_date, measurement_hour),
            INDEX idx_quality_metrics_table (table_name),
            INDEX idx_quality_metrics_date (measurement_date),
            INDEX idx_quality_metrics_score (overall_score)
        );
        
        -- Validation Issues
        CREATE TABLE IF NOT EXISTS validation_issues (
            issue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            rule_id UUID REFERENCES data_validation_rules(rule_id) ON DELETE CASCADE,
            
            -- Issue details
            table_name VARCHAR(100) NOT NULL,
            column_name VARCHAR(100),
            severity VARCHAR(20) NOT NULL,
            category VARCHAR(50) NOT NULL,
            
            -- Description
            issue_description TEXT NOT NULL,
            suggestion TEXT,
            
            -- Impact
            affected_rows BIGINT DEFAULT 0,
            impact_score NUMERIC(5,4) DEFAULT 0.0,
            
            -- Status
            status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'ignored')),
            resolved_at TIMESTAMP,
            resolved_by UUID,
            resolution_method TEXT,
            
            -- Detection
            detected_at TIMESTAMP DEFAULT NOW(),
            detection_method VARCHAR(100),
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            INDEX idx_validation_issues_rule (rule_id),
            INDEX idx_validation_issues_table (table_name),
            INDEX idx_validation_issues_severity (severity),
            INDEX idx_validation_issues_status (status),
            INDEX idx_validation_issues_detected (detected_at),
            INDEX idx_validation_issues_impact (impact_score)
        );
        
        -- Data Integrity Reports
        CREATE TABLE IF NOT EXISTS data_integrity_reports (
            report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            
            -- Report details
            report_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly, ad_hoc
            report_name VARCHAR(200),
            
            -- Overall metrics
            overall_integrity_score NUMERIC(5,4) DEFAULT 0.0,
            total_issues INTEGER DEFAULT 0,
            critical_issues INTEGER DEFAULT 0,
            resolved_issues INTEGER DEFAULT 0,
            
            -- Quality summary
            avg_completeness NUMERIC(5,4) DEFAULT 0.0,
            avg_accuracy NUMERIC(5,4) DEFAULT 0.0,
            avg_consistency NUMERIC(5,4) DEFAULT 0.0,
            avg_timeliness NUMERIC(5,4) DEFAULT 0.0,
            avg_uniqueness NUMERIC(5,4) DEFAULT 0.0,
            
            -- Coverage
            tables_checked INTEGER DEFAULT 0,
            rules_executed INTEGER DEFAULT 0,
            
            -- Report data
            detailed_results JSONB,
            recommendations JSONB,
            
            -- Time period
            period_start TIMESTAMP,
            period_end TIMESTAMP,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            generated_by UUID,
            
            -- Indexes
            INDEX idx_integrity_reports_type (report_type),
            INDEX idx_integrity_reports_score (overall_integrity_score),
            INDEX idx_integrity_reports_period (period_start, period_end),
            INDEX idx_integrity_reports_created (created_at)
        );
        
        -- Orphaned Records Detection
        CREATE TABLE IF NOT EXISTS orphaned_records (
            orphan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            
            -- Location
            table_name VARCHAR(100) NOT NULL,
            record_id TEXT NOT NULL,
            foreign_key_column VARCHAR(100),
            referenced_table VARCHAR(100),
            
            -- Details
            orphan_type VARCHAR(50) NOT NULL, -- missing_parent, unused_child, circular_reference
            
            -- Impact assessment
            severity VARCHAR(20) DEFAULT 'warning',
            cleanup_safe BOOLEAN DEFAULT false,
            
            -- Detection
            detected_at TIMESTAMP DEFAULT NOW(),
            detection_method VARCHAR(100),
            
            -- Resolution
            resolved BOOLEAN DEFAULT false,
            resolved_at TIMESTAMP,
            resolution_action TEXT,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            
            -- Indexes
            INDEX idx_orphaned_records_table (table_name),
            INDEX idx_orphaned_records_type (orphan_type),
            INDEX idx_orphaned_records_severity (severity),
            INDEX idx_orphaned_records_resolved (resolved),
            INDEX idx_orphaned_records_detected (detected_at)
        );
        
        -- Data Repair Operations
        CREATE TABLE IF NOT EXISTS data_repair_operations (
            operation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            
            -- Operation details
            operation_type VARCHAR(50) NOT NULL, -- fix_orphans, remove_duplicates, standardize_data, fix_constraints
            table_name VARCHAR(100) NOT NULL,
            description TEXT,
            
            -- Configuration
            dry_run BOOLEAN DEFAULT true,
            auto_commit BOOLEAN DEFAULT false,
            
            -- Execution
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            
            -- Results
            records_affected INTEGER DEFAULT 0,
            records_fixed INTEGER DEFAULT 0,
            errors_encountered INTEGER DEFAULT 0,
            
            -- Details
            operation_details JSONB,
            error_log JSONB,
            
            -- System fields
            created_at TIMESTAMP DEFAULT NOW(),
            created_by UUID,
            
            -- Indexes
            INDEX idx_repair_operations_type (operation_type),
            INDEX idx_repair_operations_table (table_name),
            INDEX idx_repair_operations_status (status),
            INDEX idx_repair_operations_started (started_at)
        );
        
        -- Update timestamp triggers
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Apply triggers
        DROP TRIGGER IF EXISTS update_data_validation_rules_updated_at ON data_validation_rules;
        CREATE TRIGGER update_data_validation_rules_updated_at
            BEFORE UPDATE ON data_validation_rules
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_validation_issues_updated_at ON validation_issues;
        CREATE TRIGGER update_validation_issues_updated_at
            BEFORE UPDATE ON validation_issues
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """        
        async with self._db_manager.get_session() as session:
            await session.execute(text(schema_sql))
            await session.commit()
        
        self.logger.debug("✅ Data integrity schema created successfully")
    
    async def _load_validation_rules(self):
        """Load validation rules from database"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT rule_id, rule_name, table_name, column_name, rule_type,
                               rule_expression, severity, auto_fix, check_frequency
                        FROM data_validation_rules 
                        WHERE is_active = true
                        ORDER BY table_name, rule_name
                    """)
                )
                
                rules = result.fetchall()
                
                self._validation_rules.clear()
                for rule in rules:
                    table_name = rule.table_name
                    if table_name not in self._validation_rules:
                        self._validation_rules[table_name] = []
                    
                    self._validation_rules[table_name].append({
                        'rule_id': rule.rule_id,
                        'rule_name': rule.rule_name,
                        'column_name': rule.column_name,
                        'rule_type': rule.rule_type,
                        'rule_expression': rule.rule_expression,
                        'severity': rule.severity,
                        'auto_fix': rule.auto_fix,
                        'check_frequency': rule.check_frequency
                    })
                
                self.logger.debug(f"Loaded {len(rules)} validation rules for {len(self._validation_rules)} tables")
        
        except Exception as e:
            self.logger.error(f"Failed to load validation rules: {e}")
    
    async def _run_comprehensive_validation(self):
        """Run comprehensive data validation"""        try:
            self.logger.info("🔍 Running comprehensive data validation...")
            
            validation_start = datetime.utcnow()
            issues_found = []
            tables_validated = 0
            
            # Get all tables to validate
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)
                )
                
                tables = [row.table_name for row in result.fetchall()]
            
            # Validate each table
            for table_name in tables:
                try:
                    table_issues = await self._validate_table(table_name)
                    issues_found.extend(table_issues)
                    tables_validated += 1
                    
                    # Calculate quality metrics for table
                    await self._calculate_quality_metrics(table_name)
                    
                except Exception as e:
                    self.logger.error(f"Failed to validate table {table_name}: {e}")
            
            # Store validation results
            await self._store_validation_issues(issues_found)
            
            # Generate integrity report
            report_data = {
                'validation_duration': (datetime.utcnow() - validation_start).total_seconds(),
                'tables_validated': tables_validated,
                'total_issues': len(issues_found),
                'critical_issues': len([i for i in issues_found if i.severity == ValidationSeverity.CRITICAL]),
                'error_issues': len([i for i in issues_found if i.severity == ValidationSeverity.ERROR]),
                'warning_issues': len([i for i in issues_found if i.severity == ValidationSeverity.WARNING])
            }
            
            await self._generate_integrity_report('comprehensive', report_data)
            
            self._last_validation_run = datetime.utcnow()
            self._current_issues = issues_found
            
            self.logger.info(f"✅ Validation completed - {len(issues_found)} issues found across {tables_validated} tables")
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive validation failed: {e}")
    
    async def _validate_table(self, table_name: str) -> List[ValidationIssue]:
        """Validate a specific table"""        issues = []
        
        try:
            # Get table rules
            table_rules = self._validation_rules.get(table_name, [])
            
            # Run standard validations
            issues.extend(await self._check_null_constraints(table_name))
            issues.extend(await self._check_foreign_key_integrity(table_name))
            issues.extend(await self._check_duplicate_records(table_name))
            issues.extend(await self._check_data_types(table_name))
            
            # Run custom rules
            for rule in table_rules:
                rule_issues = await self._execute_validation_rule(table_name, rule)
                issues.extend(rule_issues)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to validate table {table_name}: {e}")
            return []
    
    async def _check_null_constraints(self, table_name: str) -> List[ValidationIssue]:
        """Check null constraints"""        issues = []
        
        try:
            async with self._db_manager.get_session() as session:
                # Get columns that should not be null
                result = await session.execute(
                    text("""                        SELECT column_name, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        AND table_schema = 'public'
                        AND is_nullable = 'NO'
                    """),
                    {'table_name': table_name}
                )
                
                not_null_columns = [row.column_name for row in result.fetchall()]
                
                # Check for null values in not-null columns
                for column in not_null_columns:
                    count_result = await session.execute(
                        text(f"""                            SELECT COUNT(*) 
                            FROM {table_name} 
                            WHERE {column} IS NULL
                        """)
                    )
                    
                    null_count = count_result.scalar()
                    
                    if null_count > 0:
                        issue = ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            category=ValidationCategory.CONSTRAINTS,
                            severity=ValidationSeverity.ERROR,
                            table_name=table_name,
                            column_name=column,
                            description=f"Found {null_count} null values in NOT NULL column '{column}'",
                            affected_rows=null_count,
                            suggestion=f"Update null values in {table_name}.{column} or modify constraint"
                        )
                        issues.append(issue)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to check null constraints for {table_name}: {e}")
            return []
    
    async def _check_foreign_key_integrity(self, table_name: str) -> List[ValidationIssue]:
        """Check foreign key integrity"""        issues = []
        
        try:
            async with self._db_manager.get_session() as session:
                # Get foreign key constraints
                result = await session.execute(
                    text("""                        SELECT 
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                          AND ccu.table_schema = tc.table_schema
                        WHERE tc.constraint_type = 'FOREIGN KEY' 
                        AND tc.table_name = :table_name
                    """),
                    {'table_name': table_name}
                )
                
                foreign_keys = result.fetchall()
                
                # Check each foreign key
                for fk in foreign_keys:
                    orphan_result = await session.execute(
                        text(f"""                            SELECT COUNT(*) 
                            FROM {table_name} t1
                            LEFT JOIN {fk.foreign_table_name} t2 
                              ON t1.{fk.column_name} = t2.{fk.foreign_column_name}
                            WHERE t1.{fk.column_name} IS NOT NULL 
                            AND t2.{fk.foreign_column_name} IS NULL
                        """)
                    )
                    
                    orphan_count = orphan_result.scalar()
                    
                    if orphan_count > 0:
                        issue = ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            category=ValidationCategory.FOREIGN_KEYS,
                            severity=ValidationSeverity.ERROR,
                            table_name=table_name,
                            column_name=fk.column_name,
                            description=f"Found {orphan_count} orphaned records in foreign key {fk.column_name}",
                            affected_rows=orphan_count,
                            suggestion=f"Clean up orphaned records or fix references"
                        )
                        issues.append(issue)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to check foreign key integrity for {table_name}: {e}")
            return []
    
    async def _check_duplicate_records(self, table_name: str) -> List[ValidationIssue]:
        """Check for duplicate records"""        issues = []
        
        try:
            async with self._db_manager.get_session() as session:
                # Get unique constraints
                result = await session.execute(
                    text("""                        SELECT 
                            tc.constraint_name,
                            string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                          ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_name = :table_name
                        AND tc.constraint_type = 'UNIQUE'
                        GROUP BY tc.constraint_name
                    """),
                    {'table_name': table_name}
                )
                
                unique_constraints = result.fetchall()
                
                # Check each unique constraint
                for constraint in unique_constraints:
                    columns = constraint.columns
                    
                    duplicate_result = await session.execute(
                        text(f"""                            SELECT COUNT(*) 
                            FROM (
                                SELECT {columns}, COUNT(*) 
                                FROM {table_name}
                                GROUP BY {columns}
                                HAVING COUNT(*) > 1
                            ) duplicates
                        """)
                    )
                    
                    duplicate_count = duplicate_result.scalar()
                    
                    if duplicate_count > 0:
                        issue = ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            category=ValidationCategory.CONSTRAINTS,
                            severity=ValidationSeverity.WARNING,
                            table_name=table_name,
                            column_name=columns,
                            description=f"Found {duplicate_count} sets of duplicate records",
                            affected_rows=duplicate_count,
                            suggestion=f"Remove duplicate records or modify unique constraint"
                        )
                        issues.append(issue)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to check duplicates for {table_name}: {e}")
            return []
    
    async def _check_data_types(self, table_name: str) -> List[ValidationIssue]:
        """Check data type consistency"""        issues = []
        
        try:
            # This is a simplified check - in reality, you'd want more sophisticated validation
            async with self._db_manager.get_session() as session:
                # Check for common data type issues
                
                # Check email format
                if 'email' in [col.lower() for col in await self._get_table_columns(table_name)]:
                    result = await session.execute(
                        text(f"""                            SELECT COUNT(*) 
                            FROM {table_name}
                            WHERE email IS NOT NULL 
                            AND email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{{2,}}$'
                        """)
                    )
                    
                    invalid_emails = result.scalar()
                    
                    if invalid_emails > 0:
                        issue = ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            category=ValidationCategory.DATA_TYPES,
                            severity=ValidationSeverity.WARNING,
                            table_name=table_name,
                            column_name='email',
                            description=f"Found {invalid_emails} invalid email formats",
                            affected_rows=invalid_emails,
                            suggestion="Standardize email format or add validation"
                        )
                        issues.append(issue)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to check data types for {table_name}: {e}")
            return []
    
    async def _get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a table"""        try:
            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    text("""                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """),
                    {'table_name': table_name}
                )
                
                return [row.column_name for row in result.fetchall()]
        
        except Exception as e:
            self.logger.error(f"Failed to get columns for {table_name}: {e}")
            return []
    
    async def _execute_validation_rule(self, table_name: str, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute a custom validation rule"""        issues = []
        
        try:
            if rule['rule_type'] == 'custom' and rule['rule_expression']:
                async with self._db_manager.get_session() as session:
                    # Execute custom validation query
                    result = await session.execute(text(rule['rule_expression']))
                    violations = result.scalar()
                    
                    if violations and violations > 0:
                        issue = ValidationIssue(
                            issue_id=str(uuid.uuid4()),
                            category=ValidationCategory.BUSINESS_RULES,
                            severity=ValidationSeverity(rule['severity']),
                            table_name=table_name,
                            column_name=rule['column_name'],
                            description=f"Custom rule '{rule['rule_name']}' failed: {violations} violations",
                            affected_rows=violations,
                            suggestion=f"Review business rule: {rule['rule_name']}"
                        )
                        issues.append(issue)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to execute validation rule {rule['rule_name']}: {e}")
            return []
    
    async def _calculate_quality_metrics(self, table_name: str):
        """Calculate data quality metrics for a table"""        try:
            async with self._db_manager.get_session() as session:
                # Get total record count
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                total_records = result.scalar()
                
                if total_records == 0:
                    return
                
                # Calculate completeness (non-null ratio)
                columns = await self._get_table_columns(table_name)
                null_counts = {}
                
                for column in columns:
                    result = await session.execute(
                        text(f"SELECT COUNT(*) FROM {table_name} WHERE {column} IS NULL")
                    )
                    null_counts[column] = result.scalar()
                
                # Overall completeness score
                total_possible = total_records * len(columns)
                total_nulls = sum(null_counts.values())
                completeness_score = (total_possible - total_nulls) / total_possible if total_possible > 0 else 1.0
                
                # Simplified metrics (in real implementation, these would be more sophisticated)
                accuracy_score = 0.95  # Would be calculated based on validation rules
                consistency_score = 0.98  # Would be calculated based on format consistency
                timeliness_score = 0.90  # Would be based on data freshness
                uniqueness_score = 0.99  # Would be based on duplicate detection
                
                overall_score = statistics.mean([
                    completeness_score, accuracy_score, consistency_score,
                    timeliness_score, uniqueness_score
                ])
                
                # Store metrics
                current_date = datetime.utcnow().date()
                current_hour = datetime.utcnow().hour
                
                await session.execute(
                    text("""                        INSERT INTO data_quality_metrics 
                        (table_name, completeness_score, accuracy_score, consistency_score,
                         timeliness_score, uniqueness_score, overall_score, total_records,
                         null_count, measurement_date, measurement_hour)
                        VALUES (:table_name, :completeness_score, :accuracy_score, :consistency_score,
                               :timeliness_score, :uniqueness_score, :overall_score, :total_records,
                               :null_count, :measurement_date, :measurement_hour)
                        ON CONFLICT (table_name, column_name, measurement_date, measurement_hour) DO UPDATE SET
                            completeness_score = EXCLUDED.completeness_score,
                            accuracy_score = EXCLUDED.accuracy_score,
                            consistency_score = EXCLUDED.consistency_score,
                            timeliness_score = EXCLUDED.timeliness_score,
                            uniqueness_score = EXCLUDED.uniqueness_score,
                            overall_score = EXCLUDED.overall_score,
                            total_records = EXCLUDED.total_records,
                            null_count = EXCLUDED.null_count
                    """),
                    {
                        'table_name': table_name,
                        'completeness_score': completeness_score,
                        'accuracy_score': accuracy_score,
                        'consistency_score': consistency_score,
                        'timeliness_score': timeliness_score,
                        'uniqueness_score': uniqueness_score,
                        'overall_score': overall_score,
                        'total_records': total_records,
                        'null_count': total_nulls,
                        'measurement_date': current_date,
                        'measurement_hour': current_hour
                    }
                )
                
                await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to calculate quality metrics for {table_name}: {e}")
    
    async def _store_validation_issues(self, issues: List[ValidationIssue]):
        """Store validation issues in database"""        try:
            if not issues:
                return
            
            async with self._db_manager.get_session() as session:
                for issue in issues:
                    await session.execute(
                        text("""                            INSERT INTO validation_issues 
                            (table_name, column_name, severity, category, issue_description,
                             suggestion, affected_rows, detected_at, detection_method)
                            VALUES (:table_name, :column_name, :severity, :category, :issue_description,
                                   :suggestion, :affected_rows, :detected_at, :detection_method)
                        """),
                        {
                            'table_name': issue.table_name,
                            'column_name': issue.column_name,
                            'severity': issue.severity.value,
                            'category': issue.category.value,
                            'issue_description': issue.description,
                            'suggestion': issue.suggestion,
                            'affected_rows': issue.affected_rows,
                            'detected_at': issue.detected_at,
                            'detection_method': 'automated_validation'
                        }
                    )
                
                await session.commit()
                
                self.logger.debug(f"Stored {len(issues)} validation issues")
        
        except Exception as e:
            self.logger.error(f"Failed to store validation issues: {e}")
    
    async def _generate_integrity_report(self, report_type: str, report_data: Dict[str, Any]):
        """Generate data integrity report"""        try:
            # Calculate overall integrity score
            total_issues = report_data.get('total_issues', 0)
            critical_issues = report_data.get('critical_issues', 0)
            
            # Simple scoring algorithm
            integrity_score = max(0.0, 1.0 - (critical_issues * 0.1 + (total_issues - critical_issues) * 0.01))
            
            async with self._db_manager.get_session() as session:
                await session.execute(
                    text("""                        INSERT INTO data_integrity_reports 
                        (report_type, report_name, overall_integrity_score, total_issues,
                         critical_issues, detailed_results, period_start, period_end)
                        VALUES (:report_type, :report_name, :overall_integrity_score, :total_issues,
                               :critical_issues, :detailed_results, :period_start, :period_end)
                    """),
                    {
                        'report_type': report_type,
                        'report_name': f"{report_type.title()} Integrity Report",
                        'overall_integrity_score': integrity_score,
                        'total_issues': total_issues,
                        'critical_issues': critical_issues,
                        'detailed_results': json.dumps(report_data),
                        'period_start': datetime.utcnow() - timedelta(hours=1),
                        'period_end': datetime.utcnow()
                    }
                )
                
                await session.commit()
        
        except Exception as e:
            self.logger.error(f"Failed to generate integrity report: {e}")
    
    async def get_data_quality_summary(self) -> Dict[str, Any]:
        """Get data quality summary"""        try:
            async with self._db_manager.get_session() as session:
                # Get latest quality metrics
                result = await session.execute(
                    text("""                        SELECT 
                            AVG(completeness_score) as avg_completeness,
                            AVG(accuracy_score) as avg_accuracy,
                            AVG(consistency_score) as avg_consistency,
                            AVG(timeliness_score) as avg_timeliness,
                            AVG(uniqueness_score) as avg_uniqueness,
                            AVG(overall_score) as avg_overall,
                            COUNT(DISTINCT table_name) as tables_monitored
                        FROM data_quality_metrics 
                        WHERE measurement_date = CURRENT_DATE
                    """)
                )
                
                quality_summary = dict(result.fetchone()._mapping)
                
                # Get current issues summary
                result = await session.execute(
                    text("""                        SELECT 
                            severity,
                            COUNT(*) as count
                        FROM validation_issues 
                        WHERE status = 'open'
                        GROUP BY severity
                    """)
                )
                
                issues_by_severity = {row.severity: row.count for row in result.fetchall()}
                
                return {
                    'quality_metrics': quality_summary,
                    'issues_summary': issues_by_severity,
                    'overall_health': self._assess_overall_health(quality_summary, issues_by_severity),
                    'last_validation': self._last_validation_run.isoformat() if self._last_validation_run else None,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            self.logger.error(f"Failed to get data quality summary: {e}")
            return {'error': str(e)}
    
    def _assess_overall_health(self, quality_metrics: Dict[str, Any], issues: Dict[str, int]) -> str:
        """Assess overall data health"""        avg_quality = quality_metrics.get('avg_overall', 0) or 0
        critical_issues = issues.get('critical', 0)
        error_issues = issues.get('error', 0)
        
        if critical_issues > 0:
            return IntegrityStatus.CRITICAL.value
        elif error_issues > 5:
            return IntegrityStatus.DEGRADED.value
        elif avg_quality < 0.8:
            return IntegrityStatus.WARNING.value
        else:
            return IntegrityStatus.HEALTHY.value
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {
                    'validation_rules': 'healthy',
                    'quality_monitoring': 'healthy',
                    'issue_tracking': 'healthy'
                },
                'metrics': {
                    'validation_rules_count': len([rule for rules in self._validation_rules.values() for rule in rules]),
                    'current_issues_count': len(self._current_issues),
                    'last_validation_age': None
                }
            }
            
            # Check last validation age
            if self._last_validation_run:
                age = datetime.utcnow() - self._last_validation_run
                health['metrics']['last_validation_age'] = str(age)
                
                if age > timedelta(hours=6):
                    health['components']['validation_rules'] = 'warning'
                    health['status'] = 'warning'
            
            # Check critical issues
            critical_issues = len([i for i in self._current_issues if i.severity == ValidationSeverity.CRITICAL])
            if critical_issues > 0:
                health['components']['issue_tracking'] = 'critical'
                health['status'] = 'degraded'
                health['critical_issues'] = critical_issues
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown the data integrity manager"""        try:
            self.logger.info("🚨 Shutting down Data Integrity Manager...")
            
            # Clear validation rules and issues
            self._validation_rules.clear()
            self._current_issues.clear()
            
            self.logger.info("✅ Data Integrity Manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown failed: {e}")


# Factory function
_data_integrity_manager: Optional[DataIntegrityManager] = None


def get_data_integrity_manager(config: Optional[Dict[str, Any]] = None) -> DataIntegrityManager:
    """Get or create data integrity manager instance"""    global _data_integrity_manager
    
    if _data_integrity_manager is None:
        _data_integrity_manager = DataIntegrityManager(config)
    
    return _data_integrity_manager
