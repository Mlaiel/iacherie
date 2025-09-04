# Essential Scripts for Ainflue Platform

This directory contains the 5 most essential scripts for operating the Ainflue platform.

## Scripts Overview

### 1. `deploy.sh`
**Purpose**: Complete automated deployment script for all environments
- Handles production, staging, and development deployments
- Includes health checks and rollback capabilities
- **Usage**: `./scripts/deploy.sh [environment] [options]`

### 2. `health-check.sh`
**Purpose**: Comprehensive system health monitoring and diagnostics
- Checks all services, databases, and dependencies
- Generates detailed health reports
- **Usage**: `./scripts/health-check.sh`

### 3. `setup_production.sh`
**Purpose**: Production environment setup and configuration
- Configures Kubernetes namespaces and resources
- Sets up monitoring and logging infrastructure
- **Usage**: `./scripts/setup_production.sh`

### 4. `check_critical_dependencies.py`
**Purpose**: Validates all critical dependencies and packages
- Checks Python packages, system dependencies
- Validates AI/ML model availability
- **Usage**: `python scripts/check_critical_dependencies.py`

### 5. `run_tests.py`
**Purpose**: Comprehensive test execution framework
- Runs backend and frontend tests
- Provides detailed test reports and coverage
- **Usage**: `python scripts/run_tests.py [test_type]`

## Script Consolidation

**Previous**: 118+ scripts
**Current**: 5 essential scripts
**Reduction**: 95%+ reduction while maintaining all critical functionality

All other scripts have been consolidated or removed as they were:
- Redundant functionality
- Development-only utilities
- Obsolete or deprecated scripts
- Backup scripts (functionality moved to git)