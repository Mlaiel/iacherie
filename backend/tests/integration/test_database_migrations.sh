#!/bin/bash
# Database Migration Test Script
set -e

echo "🗄️ Testing Ainflue Database Migrations..."

# Start PostgreSQL if not running
echo "🔧 Starting PostgreSQL..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 30

# Test database connection
echo "🔌 Testing database connection..."
docker exec ainflue-postgres pg_isready -U ainflue -d ainflue_platform

# Run migrations
echo "📋 Running database migrations..."
python3 -c "
import asyncio
import sys
sys.path.append('.')

async def run_migrations():
    try:
        from database.schema import create_tables
        await create_tables()
        print('✅ Schema creation completed')
    except Exception as e:
        print(f'❌ Schema creation failed: {e}')
        return False
    
    # Run individual migrations if available
    try:
        from database.migrations.migration_runner import MigrationRunner
        runner = MigrationRunner()
        await runner.run_all_migrations()
        print('✅ All migrations completed')
    except ImportError:
        print('ℹ️ Migration runner not available, skipping migration tests')
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        return False
    
    return True

result = asyncio.run(run_migrations())
sys.exit(0 if result else 1)
"

# Verify database structure
echo "🔍 Verifying database structure..."
docker exec ainflue-postgres psql -U ainflue -d ainflue_platform -c "\dt"

echo "🎉 Database migration test completed!"
