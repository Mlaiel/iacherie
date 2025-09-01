#!/bin/bash

#
# Universal Mobile App Deployment Script
# Ainflue Professional Content Creation Platform
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# This script provides a unified interface for deploying to both iOS and Android app stores
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logo and header
echo -e "${PURPLE}"
cat << "EOF"
    ___    _            ____            
   /   |  (_)___  _____/ __/___  _____
  / /| | / / __ \/ ___/ /_/ / / / / _ \
 / ___ |/ / / / / /  / __/ / /_/ /  __/
/_/  |_/_/_/ /_/_/  /_/ /_/\__,_/\___/ 
                                      
Professional Content Creation Platform
Mobile App Store Deployment System
EOF
echo -e "${NC}"

echo -e "${BLUE}Author: Fahed Mlaiel (mlaiel@live.de)${NC}"
echo -e "${BLUE}Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.${NC}"
echo ""

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [PLATFORM] [OPTIONS]"
    echo ""
    echo "PLATFORMS:"
    echo "  ios      Deploy to iOS App Store"
    echo "  android  Deploy to Google Play Store"
    echo "  both     Deploy to both platforms (sequential)"
    echo ""
    echo "OPTIONS:"
    echo "  --help, -h    Show this help message"
    echo "  --version     Show version information"
    echo "  --dry-run     Perform a dry run without actual deployment"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 ios                 # Deploy to iOS App Store"
    echo "  $0 android             # Deploy to Google Play Store"
    echo "  $0 both                # Deploy to both platforms"
    echo "  $0 ios --dry-run       # Test iOS deployment without uploading"
    echo ""
}

# Function to show version
show_version() {
    echo "Ainflue Mobile Deployment System v1.0.0"
    echo "Author: Fahed Mlaiel"
    echo "Platform: Multi-platform (iOS/Android)"
    echo "Build System: React Native + Native"
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node >/dev/null 2>&1; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm >/dev/null 2>&1; then
        log_error "npm is not installed"
        exit 1
    fi
    
    # Check git
    if ! command -v git >/dev/null 2>&1; then
        log_error "git is not installed"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Function to deploy iOS
deploy_ios() {
    log_info "Starting iOS deployment..."
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "iOS deployment requires macOS"
        return 1
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN: Would execute iOS deployment script"
        return 0
    fi
    
    ./scripts/deploy-ios.sh
    return $?
}

# Function to deploy Android
deploy_android() {
    log_info "Starting Android deployment..."
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN: Would execute Android deployment script"
        return 0
    fi
    
    ./scripts/deploy-android.sh
    return $?
}

# Function to deploy both platforms
deploy_both() {
    log_info "Starting deployment to both platforms..."
    
    local ios_success=false
    local android_success=false
    
    # Deploy iOS first
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if deploy_ios; then
            ios_success=true
            log_success "iOS deployment completed successfully"
        else
            log_error "iOS deployment failed"
        fi
    else
        log_warning "Skipping iOS deployment (requires macOS)"
    fi
    
    # Deploy Android
    if deploy_android; then
        android_success=true
        log_success "Android deployment completed successfully"
    else
        log_error "Android deployment failed"
    fi
    
    # Summary
    echo ""
    log_info "Deployment Summary:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ "$ios_success" = true ]; then
            echo -e "${GREEN}  ✅ iOS: Success${NC}"
        else
            echo -e "${RED}  ❌ iOS: Failed${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠️  iOS: Skipped (requires macOS)${NC}"
    fi
    
    if [ "$android_success" = true ]; then
        echo -e "${GREEN}  ✅ Android: Success${NC}"
    else
        echo -e "${RED}  ❌ Android: Failed${NC}"
    fi
    
    # Return success only if at least one platform succeeded
    if [ "$ios_success" = true ] || [ "$android_success" = true ]; then
        return 0
    else
        return 1
    fi
}

# Main script logic
PLATFORM=""
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        ios|android|both)
            PLATFORM="$1"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        --version)
            show_version
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if platform is specified
if [ -z "$PLATFORM" ]; then
    log_error "Please specify a platform"
    show_usage
    exit 1
fi

# Navigate to script directory
cd "$(dirname "$0")"

# Check prerequisites
check_prerequisites

# Display deployment information
echo ""
log_info "Deployment Configuration:"
echo "  Platform: $PLATFORM"
echo "  Dry Run: $DRY_RUN"
echo "  Working Directory: $(pwd)"
echo ""

# Execute deployment based on platform
case $PLATFORM in
    ios)
        deploy_ios
        ;;
    android)
        deploy_android
        ;;
    both)
        deploy_both
        ;;
    *)
        log_error "Invalid platform: $PLATFORM"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    if [ "$PLATFORM" = "ios" ] || [ "$PLATFORM" = "both" ]; then
        echo "📱 iOS: Check App Store Connect for review status"
    fi
    if [ "$PLATFORM" = "android" ] || [ "$PLATFORM" = "both" ]; then
        echo "🤖 Android: Check Google Play Console for review status"
    fi
    echo ""
else
    log_error "Deployment failed!"
    exit 1
fi