#!/bin/bash
# Individual Developer Testing Environment Setup
# Allows each developer to run isolated testing environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get developer ID (can be set as environment variable or defaults to username)
DEVELOPER_ID=${DEVELOPER_ID:-$(whoami)}
echo "🧪 Setting up isolated testing environment for developer: $DEVELOPER_ID"

# Set unique ports for this developer (based on hash of developer ID)
HASH=$(echo -n "$DEVELOPER_ID" | md5sum | cut -c1-2)
HASH_DEC=$((16#$HASH))
PORT_BASE=$((9000 + $HASH_DEC))

export DEVELOPER_ID
export TEST_API_PORT=$PORT_BASE
export TEST_POSTGRES_PORT=$((5400 + $HASH_DEC))
export TEST_REDIS_PORT=$((6300 + $HASH_DEC))
export TEST_MONGODB_PORT=$((27000 + $HASH_DEC))
export TEST_REPORTS_PORT=$((8000 + $HASH_DEC))
export DEVELOPER_ID_SUBNET=$((20 + ($HASH_DEC % 10)))

print_info "Assigned ports for $DEVELOPER_ID:"
print_info "  - API: $TEST_API_PORT"
print_info "  - PostgreSQL: $TEST_POSTGRES_PORT"
print_info "  - Redis: $TEST_REDIS_PORT"
print_info "  - MongoDB: $TEST_MONGODB_PORT"
print_info "  - Reports: $TEST_REPORTS_PORT"

# Create developer-specific directories
mkdir -p "test-results-$DEVELOPER_ID"
mkdir -p "coverage-reports-$DEVELOPER_ID"
mkdir -p "performance-reports-$DEVELOPER_ID"

# Create test database initialization script
cat > scripts/init-test-db.sql << EOF
-- Test database initialization for $DEVELOPER_ID
CREATE DATABASE IF NOT EXISTS ainflue_test_${DEVELOPER_ID};
CREATE USER IF NOT EXISTS 'test_user_${DEVELOPER_ID}'@'%' IDENTIFIED BY 'test_password_${DEVELOPER_ID}';
GRANT ALL PRIVILEGES ON ainflue_test_${DEVELOPER_ID}.* TO 'test_user_${DEVELOPER_ID}'@'%';
FLUSH PRIVILEGES;
EOF

# Create nginx configuration for test reports
cat > nginx-test-reports.conf << EOF
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
    
    location /test-results/ {
        alias /usr/share/nginx/html/test-results/;
        autoindex on;
    }
    
    location /coverage/ {
        alias /usr/share/nginx/html/coverage/;
        autoindex on;
    }
    
    location /performance/ {
        alias /usr/share/nginx/html/performance/;
        autoindex on;
    }
}
EOF

# Create developer-specific environment file
cat > ".env.test.$DEVELOPER_ID" << EOF
# Testing environment for developer: $DEVELOPER_ID
DEVELOPER_ID=$DEVELOPER_ID
ENVIRONMENT=testing
DEBUG=true

# Test database configuration
TEST_POSTGRES_HOST=test-postgres-$DEVELOPER_ID
TEST_POSTGRES_PORT=$TEST_POSTGRES_PORT
TEST_POSTGRES_DB=ainflue_test_$DEVELOPER_ID
TEST_POSTGRES_USER=test_user_$DEVELOPER_ID
TEST_POSTGRES_PASSWORD=test_password_$DEVELOPER_ID

# Test Redis configuration
TEST_REDIS_HOST=test-redis-$DEVELOPER_ID
TEST_REDIS_PORT=$TEST_REDIS_PORT

# Test MongoDB configuration
TEST_MONGODB_HOST=test-mongodb-$DEVELOPER_ID
TEST_MONGODB_PORT=$TEST_MONGODB_PORT
TEST_MONGODB_DB=ainflue_test_$DEVELOPER_ID

# Test API configuration
TEST_API_PORT=$TEST_API_PORT
TEST_REPORTS_PORT=$TEST_REPORTS_PORT
EOF

print_status "Environment files created"

# Function to start test environment
start_test_env() {
    print_info "Starting isolated test environment..."
    
    # Load environment
    export $(cat ".env.test.$DEVELOPER_ID" | xargs)
    
    # Start services
    docker-compose -f docker-compose.test.yml up -d
    
    print_status "Test environment started!"
    print_info "Services available at:"
    print_info "  - Test API: http://localhost:$TEST_API_PORT"
    print_info "  - Test Reports: http://localhost:$TEST_REPORTS_PORT"
    print_info "  - PostgreSQL: localhost:$TEST_POSTGRES_PORT"
    print_info "  - Redis: localhost:$TEST_REDIS_PORT"
    print_info "  - MongoDB: localhost:$TEST_MONGODB_PORT"
}

# Function to stop test environment
stop_test_env() {
    print_info "Stopping test environment for $DEVELOPER_ID..."
    
    # Load environment
    export $(cat ".env.test.$DEVELOPER_ID" | xargs)
    
    # Stop services
    docker-compose -f docker-compose.test.yml down -v
    
    print_status "Test environment stopped"
}

# Function to run tests
run_tests() {
    print_info "Running tests in isolated environment..."
    
    # Load environment
    export $(cat ".env.test.$DEVELOPER_ID" | xargs)
    
    # Ensure environment is running
    docker-compose -f docker-compose.test.yml up -d test-postgres-$DEVELOPER_ID test-redis-$DEVELOPER_ID test-mongodb-$DEVELOPER_ID
    
    # Wait for databases to be ready
    print_info "Waiting for databases to be ready..."
    sleep 10
    
    # Run tests
    docker-compose -f docker-compose.test.yml run --rm test-api-$DEVELOPER_ID
    
    print_status "Tests completed! Check results at: http://localhost:$TEST_REPORTS_PORT"
}

# Function to cleanup test environment
cleanup_test_env() {
    print_info "Cleaning up test environment for $DEVELOPER_ID..."
    
    # Load environment
    export $(cat ".env.test.$DEVELOPER_ID" | xargs)
    
    # Stop and remove containers, volumes, networks
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
    
    # Remove developer-specific images if they exist
    docker image rm "ainflue-test-$DEVELOPER_ID" 2>/dev/null || true
    
    # Clean up files
    rm -rf "test-results-$DEVELOPER_ID"
    rm -rf "coverage-reports-$DEVELOPER_ID"  
    rm -rf "performance-reports-$DEVELOPER_ID"
    rm -f ".env.test.$DEVELOPER_ID"
    rm -f nginx-test-reports.conf
    rm -f scripts/init-test-db.sql
    
    print_status "Cleanup completed"
}

# Function to show test environment status
status_test_env() {
    print_info "Test environment status for $DEVELOPER_ID:"
    
    # Load environment if file exists
    if [ -f ".env.test.$DEVELOPER_ID" ]; then
        export $(cat ".env.test.$DEVELOPER_ID" | xargs)
        docker-compose -f docker-compose.test.yml ps
    else
        print_warning "Test environment not configured"
    fi
}

# Main command handling
case "$1" in
    start)
        start_test_env
        ;;
    stop)
        stop_test_env
        ;;
    restart)
        stop_test_env
        sleep 2
        start_test_env
        ;;
    test)
        run_tests
        ;;
    cleanup)
        cleanup_test_env
        ;;
    status)
        status_test_env
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|test|cleanup|status}"
        echo ""
        echo "Commands:"
        echo "  start    - Start isolated test environment"
        echo "  stop     - Stop test environment" 
        echo "  restart  - Restart test environment"
        echo "  test     - Run tests in isolated environment"
        echo "  cleanup  - Clean up all test resources"
        echo "  status   - Show test environment status"
        echo ""
        echo "Environment: $DEVELOPER_ID"
        exit 1
        ;;
esac