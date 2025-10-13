#!/bin/bash
# Initialize IA2GOOD PostgreSQL Database
# This script creates the ia2good database and applies migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IA2GOOD Database Initialization${NC}"
echo -e "${BLUE}========================================${NC}"

# Configuration
DB_HOST="${DB_HOST:-postgres-service.default.svc.cluster.local}"
DB_PORT="${DB_PORT:-5432}"
DB_ADMIN_USER="${DB_ADMIN_USER:-postgres}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:-postgres}"
DB_NAME="ia2good"
DB_USER="ia2good_user"
DB_PASSWORD="${IA2GOOD_DB_PASSWORD:-ia2good_secure_password_123}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  DB Host: ${DB_HOST}"
echo "  DB Port: ${DB_PORT}"
echo "  Database: ${DB_NAME}"
echo "  User: ${DB_USER}"
echo ""

# Check PostgreSQL connection
echo -e "${YELLOW}🔍 Checking PostgreSQL connection...${NC}"
export PGPASSWORD="${DB_ADMIN_PASSWORD}"

if psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_ADMIN_USER} -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected to PostgreSQL${NC}"
else
    echo -e "${RED}❌ Cannot connect to PostgreSQL${NC}"
    echo "   Please ensure PostgreSQL is running and accessible"
    exit 1
fi

# Create database if not exists
echo ""
echo -e "${YELLOW}📦 Creating database '${DB_NAME}'...${NC}"
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_ADMIN_USER} <<EOF
-- Create database
SELECT 'CREATE DATABASE ${DB_NAME}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec

-- Create user
DO
\$\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user WHERE usename = '${DB_USER}'
   ) THEN
      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
\c ${DB_NAME}
GRANT ALL ON SCHEMA public TO ${DB_USER};
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database and user created${NC}"
else
    echo -e "${RED}❌ Failed to create database${NC}"
    exit 1
fi

# Install required extensions
echo ""
echo -e "${YELLOW}🔌 Installing PostgreSQL extensions...${NC}"
psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_ADMIN_USER} -d ${DB_NAME} <<EOF
-- PostGIS for geolocation (Guardian module)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crypto functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- HStore for key-value storage
CREATE EXTENSION IF NOT EXISTS hstore;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Extensions installed${NC}"
else
    echo -e "${YELLOW}⚠️  Some extensions may have failed (might be ok)${NC}"
fi

# Apply migrations
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Applying Database Migrations${NC}"
echo -e "${BLUE}========================================${NC}"

MIGRATIONS_DIR="../database/migrations"

if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo -e "${RED}❌ Migrations directory not found: ${MIGRATIONS_DIR}${NC}"
    exit 1
fi

# List migration files
MIGRATION_FILES=$(find ${MIGRATIONS_DIR} -name "*.sql" | sort)

if [ -z "$MIGRATION_FILES" ]; then
    echo -e "${YELLOW}⚠️  No migration files found${NC}"
else
    export PGPASSWORD="${DB_PASSWORD}"
    
    for migration_file in $MIGRATION_FILES; do
        echo ""
        echo -e "${YELLOW}📄 Applying: $(basename ${migration_file})${NC}"
        
        psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -f ${migration_file}
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Applied successfully${NC}"
        else
            echo -e "${RED}❌ Failed to apply migration${NC}"
            echo "   File: ${migration_file}"
            exit 1
        fi
    done
fi

# Verify tables
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verifying Database Tables${NC}"
echo -e "${BLUE}========================================${NC}"

export PGPASSWORD="${DB_PASSWORD}"
TABLE_COUNT=$(psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")

echo -e "${YELLOW}Tables created: ${TABLE_COUNT}${NC}"

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Table list:${NC}"
    psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "\dt"
fi

# Create initial indexes
echo ""
echo -e "${YELLOW}🔍 Creating performance indexes...${NC}"

psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} <<EOF
-- Guardian indexes (if tables exist)
DO \$\$
BEGIN
    -- Volunteers indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'volunteers') THEN
        CREATE INDEX IF NOT EXISTS idx_volunteers_skills ON volunteers USING GIN (skills);
        CREATE INDEX IF NOT EXISTS idx_volunteers_location ON volunteers USING GIST (location);
        CREATE INDEX IF NOT EXISTS idx_volunteers_status ON volunteers (status);
    END IF;
    
    -- Cases indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'cases') THEN
        CREATE INDEX IF NOT EXISTS idx_cases_status ON cases (status);
        CREATE INDEX IF NOT EXISTS idx_cases_category ON cases (category);
        CREATE INDEX IF NOT EXISTS idx_cases_location ON cases USING GIST (location);
        CREATE INDEX IF NOT EXISTS idx_cases_created ON cases (created_at DESC);
    END IF;
    
    -- EduVerify indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'content') THEN
        CREATE INDEX IF NOT EXISTS idx_content_status ON content (status);
        CREATE INDEX IF NOT EXISTS idx_content_subject ON content (subject);
        CREATE INDEX IF NOT EXISTS idx_content_search ON content USING GIN (to_tsvector('english', title || ' ' || description));
    END IF;
    
    -- MedCare indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'consultations') THEN
        CREATE INDEX IF NOT EXISTS idx_consultations_patient ON consultations (patient_id);
        CREATE INDEX IF NOT EXISTS idx_consultations_status ON consultations (status);
        CREATE INDEX IF NOT EXISTS idx_consultations_date ON consultations (consultation_date DESC);
    END IF;
END \$\$;
EOF

echo -e "${GREEN}✅ Indexes created${NC}"

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Database Initialization Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Connection details:${NC}"
echo "  Host: ${DB_HOST}"
echo "  Port: ${DB_PORT}"
echo "  Database: ${DB_NAME}"
echo "  User: ${DB_USER}"
echo "  Password: ********"
echo ""
echo -e "${YELLOW}Connection string:${NC}"
echo "  postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Update k8s/01-configmap-secrets.yaml with the connection string (base64 encoded)"
echo "  2. Deploy IA2GOOD services: ./deploy-k8s.sh"
echo "  3. Verify database: psql postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""
