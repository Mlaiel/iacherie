#!/bin/bash

#
# Multi-Platform Desktop Build Script
# Ainflue Professional Content Creation Platform
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# This script builds the Ainflue desktop application for multiple platforms
# with comprehensive configuration and optimizations.
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DESKTOP_DIR="$PROJECT_ROOT/desktop"
BUILD_DIR="$DESKTOP_DIR/dist"
LOGS_DIR="$PROJECT_ROOT/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

log_step() {
    echo -e "${PURPLE}🚀 $1${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [PLATFORMS]

Build Ainflue Desktop for multiple platforms with professional configurations.

PLATFORMS:
    mac         Build for macOS (DMG, ZIP, MAS)
    win         Build for Windows (NSIS, ZIP, Portable)
    linux       Build for Linux (AppImage, Snap, DEB, RPM)
    all         Build for all platforms (requires appropriate environment)

OPTIONS:
    --clean     Clean build directory before building
    --sign      Enable code signing (requires certificates)
    --publish   Publish to distribution channels
    --draft     Create draft release
    --help      Show this help message

EXAMPLES:
    $0 mac                    # Build for macOS only
    $0 win linux              # Build for Windows and Linux
    $0 --clean --sign all     # Clean build with signing for all platforms
    $0 --publish mac          # Build and publish macOS version

ENVIRONMENT VARIABLES:
    CSC_KEY_PASSWORD         Certificate password for code signing
    APPLE_ID                 Apple ID for notarization (macOS)
    APPLE_ID_PASSWORD        App-specific password for notarization
    GH_TOKEN                 GitHub token for releases
    SNAP_TOKEN               Snapcraft token for Snap store

EOF
}

# Function to check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check if we're in the correct directory
    if [[ ! -f "$DESKTOP_DIR/package.json" ]]; then
        log_error "Desktop package.json not found. Please run from project root."
        exit 1
    fi
    
    # Check Node.js and npm
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    
    # Check Node.js version
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    REQUIRED_VERSION="18.0.0"
    
    if ! printf '%s\n%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V -C; then
        log_error "Node.js version $REQUIRED_VERSION or higher is required (current: $NODE_VERSION)"
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

# Function to setup build environment
setup_environment() {
    log_step "Setting up build environment..."
    
    # Create logs directory
    mkdir -p "$LOGS_DIR"
    
    # Navigate to desktop directory
    cd "$DESKTOP_DIR"
    
    # Check if node_modules exists
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing dependencies..."
        npm install
    else
        log_info "Dependencies already installed"
    fi
    
    # Create assets directory if it doesn't exist
    mkdir -p assets
    
    # Create build resources directory
    mkdir -p build
    
    log_success "Build environment setup completed"
}

# Function to clean build directory
clean_build() {
    if [[ "$CLEAN_BUILD" == "true" ]]; then
        log_step "Cleaning build directory..."
        if [[ -d "$BUILD_DIR" ]]; then
            rm -rf "$BUILD_DIR"
            log_success "Build directory cleaned"
        else
            log_info "Build directory already clean"
        fi
    fi
}

# Function to create build assets
create_build_assets() {
    log_step "Creating build assets..."
    
    # Create placeholder icon if it doesn't exist
    if [[ ! -f "assets/icon.png" ]]; then
        log_warning "Icon assets not found, creating placeholders..."
        
        # Create a simple placeholder icon using ImageMagick if available
        if command -v convert &> /dev/null; then
            convert -size 512x512 xc:'#3B82F6' -fill white -pointsize 100 \
                    -gravity center -annotate +0+0 'A' assets/icon.png
            
            # Create different formats
            convert assets/icon.png -resize 256x256 assets/icon.icns 2>/dev/null || cp assets/icon.png assets/icon.icns
            convert assets/icon.png assets/icon.ico 2>/dev/null || cp assets/icon.png assets/icon.ico
        else
            log_warning "ImageMagick not available, using default icons"
        fi
    fi
    
    # Create entitlements for macOS if they don't exist
    if [[ ! -f "build/entitlements.mac.plist" ]]; then
        cat > build/entitlements.mac.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.device.audio-input</key>
    <true/>
    <key>com.apple.security.device.camera</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
</dict>
</plist>
EOF
    fi
    
    log_success "Build assets created"
}

# Function to build for macOS
build_mac() {
    log_step "Building for macOS..."
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_warning "macOS builds require macOS. Skipping..."
        return 0
    fi
    
    local build_args="--mac"
    
    if [[ "$SIGN_BUILD" == "true" ]]; then
        build_args="$build_args --publish=never"
        log_info "Code signing enabled for macOS build"
    fi
    
    if [[ "$PUBLISH_BUILD" == "true" ]]; then
        build_args="$build_args --publish=always"
    fi
    
    npm run build:mac 2>&1 | tee "$LOGS_DIR/build-mac.log"
    
    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        log_success "macOS build completed successfully"
        
        # Show build artifacts
        if [[ -d "$BUILD_DIR" ]]; then
            log_info "macOS build artifacts:"
            find "$BUILD_DIR" -name "*.dmg" -o -name "*.zip" -o -name "*.pkg" | while read -r file; do
                echo "  📦 $(basename "$file") ($(du -h "$file" | cut -f1))"
            done
        fi
    else
        log_error "macOS build failed"
        return 1
    fi
}

# Function to build for Windows
build_win() {
    log_step "Building for Windows..."
    
    local build_args="--win"
    
    if [[ "$SIGN_BUILD" == "true" ]]; then
        build_args="$build_args --publish=never"
        log_info "Code signing enabled for Windows build"
    fi
    
    if [[ "$PUBLISH_BUILD" == "true" ]]; then
        build_args="$build_args --publish=always"
    fi
    
    npm run build:win 2>&1 | tee "$LOGS_DIR/build-win.log"
    
    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        log_success "Windows build completed successfully"
        
        # Show build artifacts
        if [[ -d "$BUILD_DIR" ]]; then
            log_info "Windows build artifacts:"
            find "$BUILD_DIR" -name "*.exe" -o -name "*.zip" -o -name "*.msi" | while read -r file; do
                echo "  📦 $(basename "$file") ($(du -h "$file" | cut -f1))"
            done
        fi
    else
        log_error "Windows build failed"
        return 1
    fi
}

# Function to build for Linux
build_linux() {
    log_step "Building for Linux..."
    
    local build_args="--linux"
    
    if [[ "$PUBLISH_BUILD" == "true" ]]; then
        build_args="$build_args --publish=always"
    fi
    
    npm run build:linux 2>&1 | tee "$LOGS_DIR/build-linux.log"
    
    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        log_success "Linux build completed successfully"
        
        # Show build artifacts
        if [[ -d "$BUILD_DIR" ]]; then
            log_info "Linux build artifacts:"
            find "$BUILD_DIR" -name "*.AppImage" -o -name "*.snap" -o -name "*.deb" -o -name "*.rpm" | while read -r file; do
                echo "  📦 $(basename "$file") ($(du -h "$file" | cut -f1))"
            done
        fi
    else
        log_error "Linux build failed"
        return 1
    fi
}

# Function to verify builds
verify_builds() {
    log_step "Verifying builds..."
    
    if [[ ! -d "$BUILD_DIR" ]]; then
        log_error "Build directory not found"
        return 1
    fi
    
    local total_size=0
    local file_count=0
    
    while IFS= read -r -d '' file; do
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        total_size=$((total_size + size))
        file_count=$((file_count + 1))
    done < <(find "$BUILD_DIR" -type f \( -name "*.dmg" -o -name "*.zip" -o -name "*.exe" -o -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" -o -name "*.snap" \) -print0)
    
    if [[ $file_count -gt 0 ]]; then
        local total_size_mb=$((total_size / 1024 / 1024))
        log_success "Build verification completed: $file_count files, ${total_size_mb}MB total"
    else
        log_error "No build artifacts found"
        return 1
    fi
}

# Function to create checksums
create_checksums() {
    log_step "Creating checksums..."
    
    if [[ -d "$BUILD_DIR" ]]; then
        cd "$BUILD_DIR"
        
        # Create SHA256 checksums
        find . -type f \( -name "*.dmg" -o -name "*.zip" -o -name "*.exe" -o -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" -o -name "*.snap" \) -exec sha256sum {} \; > checksums.sha256
        
        if [[ -f "checksums.sha256" ]]; then
            log_success "Checksums created: checksums.sha256"
        fi
        
        cd "$DESKTOP_DIR"
    fi
}

# Function to show build summary
show_summary() {
    log_step "Build Summary"
    
    echo ""
    echo "🏗️  Build Configuration:"
    echo "   Project: Ainflue Desktop"
    echo "   Version: $(npm pkg get version | tr -d '"')"
    echo "   Platforms: ${PLATFORMS[*]}"
    echo "   Clean Build: $CLEAN_BUILD"
    echo "   Code Signing: $SIGN_BUILD"
    echo "   Publish: $PUBLISH_BUILD"
    echo ""
    
    if [[ -d "$BUILD_DIR" ]]; then
        echo "📦 Build Artifacts:"
        find "$BUILD_DIR" -type f \( -name "*.dmg" -o -name "*.zip" -o -name "*.exe" -o -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" -o -name "*.snap" \) | while read -r file; do
            local size=$(du -h "$file" | cut -f1)
            echo "   $(basename "$file") ($size)"
        done
        echo ""
    fi
    
    echo "📊 System Information:"
    echo "   OS: $(uname -s) $(uname -r)"
    echo "   Architecture: $(uname -m)"
    echo "   Node.js: $(node --version)"
    echo "   npm: $(npm --version)"
    echo ""
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    log_success "Build completed in ${minutes}m ${seconds}s"
}

# Main function
main() {
    local start_time=$(date +%s)
    
    # Default values
    PLATFORMS=()
    CLEAN_BUILD=false
    SIGN_BUILD=false
    PUBLISH_BUILD=false
    DRAFT_RELEASE=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                CLEAN_BUILD=true
                shift
                ;;
            --sign)
                SIGN_BUILD=true
                shift
                ;;
            --publish)
                PUBLISH_BUILD=true
                shift
                ;;
            --draft)
                DRAFT_RELEASE=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            mac|win|linux)
                PLATFORMS+=("$1")
                shift
                ;;
            all)
                PLATFORMS=("mac" "win" "linux")
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check if platforms are specified
    if [[ ${#PLATFORMS[@]} -eq 0 ]]; then
        log_error "No platforms specified"
        show_usage
        exit 1
    fi
    
    # Header
    echo ""
    echo -e "${CYAN}🎵 Ainflue Desktop - Multi-Platform Build Script${NC}"
    echo -e "${CYAN}=================================================${NC}"
    echo ""
    
    # Run build process
    check_prerequisites
    setup_environment
    clean_build
    create_build_assets
    
    # Build for each platform
    local failed_builds=()
    
    for platform in "${PLATFORMS[@]}"; do
        case $platform in
            mac)
                if ! build_mac; then
                    failed_builds+=("macOS")
                fi
                ;;
            win)
                if ! build_win; then
                    failed_builds+=("Windows")
                fi
                ;;
            linux)
                if ! build_linux; then
                    failed_builds+=("Linux")
                fi
                ;;
        esac
    done
    
    # Verify builds and create checksums
    if verify_builds; then
        create_checksums
    fi
    
    # Show summary
    show_summary
    
    # Check for failed builds
    if [[ ${#failed_builds[@]} -gt 0 ]]; then
        log_error "Some builds failed: ${failed_builds[*]}"
        exit 1
    fi
    
    log_success "All builds completed successfully! 🎉"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi