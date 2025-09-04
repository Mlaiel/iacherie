# Essential Scripts Directory

This directory contains only the 5 most essential scripts for the Ainflue platform, following the project consolidation guidelines.

## Essential Scripts

### 1. `deploy.sh`
**Purpose**: Main deployment script for production environments
- Handles full application deployment
- Configures services and dependencies
- Manages deployment rollback if needed

### 2. `health_check.sh`
**Purpose**: Comprehensive health monitoring and validation
- Checks service availability
- Validates system resources
- Monitors application health endpoints

### 3. `setup_production.sh`
**Purpose**: Production environment setup and configuration
- Initializes production environment
- Configures security settings
- Sets up monitoring and logging

### 4. `install_spacy_models.sh`
**Purpose**: Install required spaCy NLP models
- Downloads and installs spaCy language models
- Required for AI/NLP functionality
- Supports multiple languages

### 5. `check_critical_dependencies.py`
**Purpose**: Validate critical system dependencies
- Checks Python package availability
- Validates system requirements
- Reports dependency status

## Usage

Make sure scripts are executable:
```bash
chmod +x scripts/*.sh
```

Run scripts from the project root:
```bash
# Check dependencies
python scripts/check_critical_dependencies.py

# Setup production environment
./scripts/setup_production.sh

# Deploy application
./scripts/deploy.sh

# Check system health
./scripts/health_check.sh

# Install NLP models
./scripts/install_spacy_models.sh
```

## Note

All non-essential scripts have been removed as part of the project consolidation. For historical versions, refer to git history or create new scripts as needed following the project's development standards.