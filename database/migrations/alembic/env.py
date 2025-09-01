"""Alembic environment script for Ainflue production database.

This script sets up the database migration environment with production-ready
configurations including SSL, connection pooling, and monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our models
sys.path.insert(0, str(Path(__file__).parents[3]))

# Import all models to ensure they're registered with SQLAlchemy
from data.models.content_model import ContentMetadata
from data.models.user_model import User, Creator
from data.models.analytics_model import AnalyticsEvent
from data.models.protection_model import ContentProtection
from data.models.revenue_model import Revenue
from data.models.licensing_model import License
from protection.rights_tracking.models import (
    ContentMetadata as ProtectionContentMetadata,
    RightsRecord,
    LicenseAgreement,
    PaymentRecord
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the base metadata from our models
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Set target metadata for autogenerate support
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment variables with production defaults."""
    return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}?sslmode=require".format(
        user=os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
        password=os.getenv('POSTGRES_PASSWORD_PRODUCTION', ''),
        host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
        port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
        database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
    )

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        transaction_per_migration=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_url()
    
    # Production connection configuration
    configuration.update({
        'pool_size': '20',
        'max_overflow': '30',
        'pool_pre_ping': 'true',
        'pool_recycle': '3600',
        'connect_args': '{"sslmode": "require", "connect_timeout": 10}'
    })
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            transaction_per_migration=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()