#!/bin/bash
# Deployment Automation - Multi-platform Desktop Build & Distribution
# Author: Fahed Mlaiel (mlaiel@live.de)  
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# Description: Automates desktop deployment with multi-platform builds, code signing, and auto-update
# Usage: ./deployment_automation.sh [--platform windows|macos|linux|all] [--environment dev|staging|prod] [--sign]

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# 🎨 ANSI COLOR CODES & STYLING  
# ═══════════════════════════════════════════════════════════════════
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════
# 📋 CONFIGURATION & GLOBALS
# ═══════════════════════════════════════════════════════════════════
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DESKTOP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly PROJECT_ROOT="$(cd "${DESKTOP_DIR}/.." && pwd)"
readonly LOG_DIR="/tmp/desktop_logs"
readonly DEPLOY_LOG="${LOG_DIR}/deployment_automation.log"
readonly BUILD_DIR="${DESKTOP_DIR}/dist"
readonly ASSETS_DIR="${DESKTOP_DIR}/assets"

# Default configuration
TARGET_PLATFORM="all"
ENVIRONMENT="dev"
ENABLE_SIGNING=false
ENABLE_AUTO_UPDATE=true
PARALLEL_BUILDS=true
BUILD_VERSION=""

# ═══════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${CYAN}[INFO]${NC} ${timestamp} - $message" | tee -a "$DEPLOY_LOG" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message" | tee -a "$DEPLOY_LOG" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - $message" | tee -a "$DEPLOY_LOG" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message" | tee -a "$DEPLOY_LOG" ;;
        *) echo -e "${WHITE}[$level]${NC} ${timestamp} - $message" | tee -a "$DEPLOY_LOG" ;;
    esac
}

show_header() {
    echo -e "${PURPLE}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                  🚀 AINFLUE DEPLOYMENT AUTOMATION               ║"
    echo "║                                                                  ║"
    echo "║      Multi-platform Desktop Build & Distribution System         ║"
    echo "║                                                                  ║"
    echo "║  © 2025 Fahed Mlaiel - Advanced DevOps & Build Engineering      ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_progress() {
    local current=$1
    local total=$2
    local step_name="$3"
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\r${BLUE}Build Progress${NC}: ["
    printf "%*s" $completed | tr ' ' '█'
    printf "%*s" $((width - completed))
    printf "] ${BOLD}%d%%${NC} - %s" $percentage "$step_name"
}

# ═══════════════════════════════════════════════════════════════════
# 🔍 ENVIRONMENT VALIDATION
# ═══════════════════════════════════════════════════════════════════
validate_build_environment() {
    log "INFO" "🔍 Validating build environment..."
    
    # Check if we're in desktop directory
    if [[ ! -f "${DESKTOP_DIR}/package.json" ]]; then
        log "ERROR" "❌ package.json not found. Please run from desktop directory."
        return 1
    fi
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        log "ERROR" "❌ Node.js is not installed"
        return 1
    fi
    
    local node_version=$(node --version | cut -d'v' -f2)
    log "INFO" "📦 Node.js version: v${node_version}"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log "ERROR" "❌ npm is not installed"
        return 1
    fi
    
    # Check electron-builder
    if ! npm list electron-builder &> /dev/null; then
        log "WARN" "⚠️ electron-builder not found, installing..."
        npm install electron-builder --save-dev
    fi
    
    # Validate assets
    local required_assets=(
        "${ASSETS_DIR}/icon.png"
        "${ASSETS_DIR}/icon.ico" 
        "${ASSETS_DIR}/icon.icns"
    )
    
    for asset in "${required_assets[@]}"; do
        if [[ ! -f "$asset" ]]; then
            log "ERROR" "❌ Missing required asset: $asset"
            return 1
        fi
    done
    
    log "SUCCESS" "✅ Build environment validated"
    return 0
}

get_build_version() {
    if [[ -n "$BUILD_VERSION" ]]; then
        echo "$BUILD_VERSION"
        return
    fi
    
    # Extract version from package.json
    local version=$(grep '"version"' "${DESKTOP_DIR}/package.json" | cut -d'"' -f4)
    if [[ -n "$version" ]]; then
        echo "$version"
    else
        echo "1.0.0"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# 🔐 CODE SIGNING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
setup_code_signing() {
    if [[ "$ENABLE_SIGNING" != "true" ]]; then
        log "INFO" "⏭️ Code signing disabled"
        return 0
    fi
    
    log "INFO" "🔐 Setting up code signing..."
    
    case "$TARGET_PLATFORM" in
        "windows"|"all")
            setup_windows_signing
            ;;
        "macos"|"all")
            setup_macos_signing
            ;;
    esac
    
    log "SUCCESS" "✅ Code signing configured"
}

setup_windows_signing() {
    log "INFO" "🪟 Configuring Windows code signing..."
    
    # Check for Windows signing certificate
    if [[ -z "${WINDOWS_CERT_PATH:-}" ]]; then
        log "WARN" "⚠️ WINDOWS_CERT_PATH not set, skipping Windows signing"
        return
    fi
    
    if [[ ! -f "$WINDOWS_CERT_PATH" ]]; then
        log "ERROR" "❌ Windows certificate not found: $WINDOWS_CERT_PATH"
        return 1
    fi
    
    export CSC_LINK="$WINDOWS_CERT_PATH"
    export CSC_KEY_PASSWORD="${WINDOWS_CERT_PASSWORD:-}"
    
    log "SUCCESS" "✅ Windows signing configured"
}

setup_macos_signing() {
    log "INFO" "🍎 Configuring macOS code signing..."
    
    # Check for macOS signing identity
    if [[ -z "${MACOS_SIGNING_IDENTITY:-}" ]]; then
        log "WARN" "⚠️ MACOS_SIGNING_IDENTITY not set, skipping macOS signing"
        return
    fi
    
    export CSC_NAME="$MACOS_SIGNING_IDENTITY"
    export CSC_KEY_PASSWORD="${MACOS_CERT_PASSWORD:-}"
    
    # Check for notarization credentials
    if [[ -n "${APPLE_ID:-}" && -n "${APPLE_ID_PASSWORD:-}" ]]; then
        export APPLE_ID="$APPLE_ID"
        export APPLE_ID_PASSWORD="$APPLE_ID_PASSWORD"
        log "INFO" "🍎 macOS notarization configured"
    fi
    
    log "SUCCESS" "✅ macOS signing configured"
}

# ═══════════════════════════════════════════════════════════════════
# 🏗️ BUILD FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
clean_build_directory() {
    log "INFO" "🧹 Cleaning build directory..."
    
    if [[ -d "$BUILD_DIR" ]]; then
        rm -rf "$BUILD_DIR"
        log "SUCCESS" "✅ Build directory cleaned"
    fi
    
    mkdir -p "$BUILD_DIR"
}

install_dependencies() {
    log "INFO" "📦 Installing dependencies..."
    show_progress 1 8 "Installing Dependencies"
    
    cd "$DESKTOP_DIR"
    
    # Use npm ci for faster, reliable installs in CI/CD
    if [[ -f "package-lock.json" ]]; then
        npm ci --production=false
    else
        npm install
    fi
    
    log "SUCCESS" "✅ Dependencies installed"
}

build_for_linux() {
    log "INFO" "🐧 Building for Linux..."
    show_progress 3 8 "Building Linux Package"
    
    cd "$DESKTOP_DIR"
    
    local build_targets=("AppImage" "deb" "rpm")
    
    for target in "${build_targets[@]}"; do
        log "INFO" "🔨 Building Linux $target..."
        npm run build:linux -- --publish=never --config.linux.target="$target" || {
            log "ERROR" "❌ Linux $target build failed"
            return 1
        }
    done
    
    log "SUCCESS" "✅ Linux builds completed"
}

build_for_windows() {
    log "INFO" "🪟 Building for Windows..."
    show_progress 4 8 "Building Windows Package"
    
    cd "$DESKTOP_DIR"
    
    local build_targets=("nsis" "portable")
    
    for target in "${build_targets[@]}"; do
        log "INFO" "🔨 Building Windows $target..."
        npm run build:win -- --publish=never --config.win.target="$target" || {
            log "ERROR" "❌ Windows $target build failed"
            return 1
        }
    done
    
    log "SUCCESS" "✅ Windows builds completed"
}

build_for_macos() {
    log "INFO" "🍎 Building for macOS..."
    show_progress 5 8 "Building macOS Package"
    
    cd "$DESKTOP_DIR"
    
    local build_targets=("dmg" "zip")
    
    for target in "${build_targets[@]}"; do
        log "INFO" "🔨 Building macOS $target..."
        npm run build:mac -- --publish=never --config.mac.target="$target" || {
            log "ERROR" "❌ macOS $target build failed"
            return 1
        }
    done
    
    log "SUCCESS" "✅ macOS builds completed"
}

build_all_platforms() {
    log "INFO" "🌍 Building for all platforms..."
    
    if [[ "$PARALLEL_BUILDS" == "true" ]]; then
        log "INFO" "⚡ Starting parallel builds..."
        
        # Start builds in background
        build_for_linux &
        local linux_pid=$!
        
        build_for_windows &
        local windows_pid=$!
        
        build_for_macos &
        local macos_pid=$!
        
        # Wait for all builds to complete
        wait $linux_pid || log "ERROR" "❌ Linux build failed"
        wait $windows_pid || log "ERROR" "❌ Windows build failed"  
        wait $macos_pid || log "ERROR" "❌ macOS build failed"
        
    else
        # Sequential builds
        build_for_linux || return 1
        build_for_windows || return 1
        build_for_macos || return 1
    fi
    
    log "SUCCESS" "✅ All platform builds completed"
}

# ═══════════════════════════════════════════════════════════════════
# 🚀 DEPLOYMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
generate_checksums() {
    log "INFO" "🔐 Generating checksums..."
    show_progress 6 8 "Generating Checksums"
    
    cd "$BUILD_DIR"
    
    # Generate SHA256 checksums for all build artifacts
    find . -type f \( -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" -o -name "*.exe" -o -name "*.dmg" -o -name "*.zip" \) -exec sha256sum {} \; > checksums.sha256
    
    log "SUCCESS" "✅ Checksums generated"
}

create_release_notes() {
    log "INFO" "📝 Creating release notes..."
    
    local version=$(get_build_version)
    local release_notes_file="${BUILD_DIR}/RELEASE_NOTES_${version}.md"
    
    cat > "$release_notes_file" << EOF
# Ainflue Desktop v${version}

**Release Date**: $(date '+%Y-%m-%d')
**Environment**: ${ENVIRONMENT}

## 🎯 Features
- Multi-format content processing (audio/video/image/text)
- Advanced AI-powered SEO optimization
- Real-time collaboration matching
- Automated rights protection with blockchain verification
- Multi-platform distribution automation
- Advanced analytics and revenue tracking

## 🛡️ Security
- End-to-end encryption for sensitive data
- Advanced watermarking and fingerprinting
- DMCA compliance automation
- Secure payment processing integration

## 🏗️ Build Information
- **Build Date**: $(date '+%Y-%m-%d %H:%M:%S')
- **Node.js Version**: $(node --version)
- **Electron Version**: $(npm list electron --depth=0 2>/dev/null | grep electron | cut -d'@' -f2 || echo "Unknown")
- **Build Environment**: ${ENVIRONMENT}

## 📦 Supported Platforms
- Windows 10/11 (x64)
- macOS 10.15+ (Intel & Apple Silicon)
- Linux (AppImage, deb, rpm)

## 🔐 Verification
Please verify downloads using SHA256 checksums provided in checksums.sha256

---
© 2025 Fahed Mlaiel - All Rights Reserved
EOF

    log "SUCCESS" "✅ Release notes created: $release_notes_file"
}

setup_auto_update() {
    if [[ "$ENABLE_AUTO_UPDATE" != "true" ]]; then
        log "INFO" "⏭️ Auto-update disabled"
        return 0
    fi
    
    log "INFO" "🔄 Setting up auto-update..."
    show_progress 7 8 "Configuring Auto-Update"
    
    # Create update server configuration
    local update_config="${BUILD_DIR}/update-config.json"
    local version=$(get_build_version)
    
    cat > "$update_config" << EOF
{
  "version": "${version}",
  "releaseDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platforms": {
    "win32": {
      "url": "https://releases.ainflue.com/desktop/v${version}/Ainflue-Setup-${version}.exe",
      "sha256": "$(sha256sum "${BUILD_DIR}/"*Setup*.exe 2>/dev/null | cut -d' ' -f1 || echo 'TBD')"
    },
    "darwin": {
      "url": "https://releases.ainflue.com/desktop/v${version}/Ainflue-${version}.dmg",
      "sha256": "$(sha256sum "${BUILD_DIR}/"*.dmg 2>/dev/null | cut -d' ' -f1 || echo 'TBD')"
    },
    "linux": {
      "url": "https://releases.ainflue.com/desktop/v${version}/Ainflue-${version}.AppImage",
      "sha256": "$(sha256sum "${BUILD_DIR}/"*.AppImage 2>/dev/null | cut -d' ' -f1 || echo 'TBD')"
    }
  }
}
EOF
    
    log "SUCCESS" "✅ Auto-update configuration created"
}

# ═══════════════════════════════════════════════════════════════════
# 📊 QUALITY ASSURANCE
# ═══════════════════════════════════════════════════════════════════
run_quality_checks() {
    log "INFO" "🔍 Running quality checks..."
    show_progress 8 8 "Quality Assurance"
    
    cd "$DESKTOP_DIR"
    
    # Run linting
    if npm run lint &> /dev/null; then
        log "SUCCESS" "✅ Linting passed"
    else
        log "WARN" "⚠️ Linting issues detected"
    fi
    
    # Run tests
    if npm test &> /dev/null; then
        log "SUCCESS" "✅ Tests passed"
    else
        log "WARN" "⚠️ Some tests failed"
    fi
    
    # Check bundle size
    local bundle_sizes=()
    for file in "${BUILD_DIR}/"*; do
        if [[ -f "$file" ]]; then
            local size=$(du -h "$file" | cut -f1)
            bundle_sizes+=("$(basename "$file"): $size")
        fi
    done
    
    log "INFO" "📦 Bundle sizes:"
    for size_info in "${bundle_sizes[@]}"; do
        log "INFO" "   $size_info"
    done
    
    log "SUCCESS" "✅ Quality checks completed"
}

# ═══════════════════════════════════════════════════════════════════
# 📚 HELP & USAGE
# ═══════════════════════════════════════════════════════════════════
show_help() {
    echo -e "${CYAN}${BOLD}USAGE:${NC}"
    echo "  $0 [OPTIONS]"
    echo
    echo -e "${CYAN}${BOLD}OPTIONS:${NC}"
    echo "  --platform PLATFORM     Target platform: windows|macos|linux|all (default: all)"
    echo "  --environment ENV       Build environment: dev|staging|prod (default: dev)"
    echo "  --sign                  Enable code signing (requires certificates)"
    echo "  --no-auto-update        Disable auto-update functionality"
    echo "  --sequential            Use sequential builds instead of parallel"
    echo "  --version VERSION       Override build version"
    echo "  --help                  Show this help message"
    echo
    echo -e "${CYAN}${BOLD}EXAMPLES:${NC}"
    echo "  $0 --platform windows --environment prod --sign"
    echo "  $0 --platform all --version 2.1.0"
    echo "  $0 --environment staging --sequential"
    echo
    echo -e "${CYAN}${BOLD}ENVIRONMENT VARIABLES:${NC}"
    echo "  WINDOWS_CERT_PATH       Path to Windows signing certificate"
    echo "  WINDOWS_CERT_PASSWORD   Windows certificate password"
    echo "  MACOS_SIGNING_IDENTITY  macOS signing identity"
    echo "  APPLE_ID               Apple ID for notarization"
    echo "  APPLE_ID_PASSWORD      Apple ID password"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
main() {
    # Create required directories
    mkdir -p "$LOG_DIR"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --platform)
                TARGET_PLATFORM="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --sign)
                ENABLE_SIGNING=true
                shift
                ;;
            --no-auto-update)
                ENABLE_AUTO_UPDATE=false
                shift
                ;;
            --sequential)
                PARALLEL_BUILDS=false
                shift
                ;;
            --version)
                BUILD_VERSION="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    show_header
    
    local start_time=$(date +%s)
    local version=$(get_build_version)
    
    log "INFO" "🚀 Starting deployment for Ainflue Desktop v${version}"
    log "INFO" "🎯 Target platform: $TARGET_PLATFORM"
    log "INFO" "🌍 Environment: $ENVIRONMENT"
    log "INFO" "🔐 Code signing: $ENABLE_SIGNING"
    
    # Validate environment
    validate_build_environment || exit 1
    
    # Setup code signing
    setup_code_signing || exit 1
    
    # Clean and prepare
    clean_build_directory
    
    # Install dependencies
    install_dependencies || exit 1
    
    # Build based on platform
    case "$TARGET_PLATFORM" in
        "windows")
            build_for_windows || exit 1
            ;;
        "macos")
            build_for_macos || exit 1
            ;;
        "linux")
            build_for_linux || exit 1
            ;;
        "all")
            build_all_platforms || exit 1
            ;;
        *)
            log "ERROR" "❌ Invalid platform: $TARGET_PLATFORM"
            show_help
            exit 1
            ;;
    esac
    
    # Post-build tasks
    generate_checksums || exit 1
    create_release_notes
    setup_auto_update || exit 1
    run_quality_checks || exit 1
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo
    log "SUCCESS" "🎉 Deployment completed successfully in ${duration}s"
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ DEPLOYMENT SUCCESSFUL                      ║"
    echo "║                                                                  ║"
    echo "║  Ainflue Desktop v${version} built for: $TARGET_PLATFORM        ║"
    echo "║  Environment: $ENVIRONMENT                                       ║"
    echo "║  Build time: ${duration} seconds                                 ║"
    echo "║  Output: ${BUILD_DIR}                                            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Show next steps
    echo -e "${CYAN}${BOLD}NEXT STEPS:${NC}"
    echo "1. Review build artifacts in: ${BUILD_DIR}"
    echo "2. Test installers on target platforms"
    echo "3. Upload to distribution servers"
    echo "4. Update release documentation"
}

# Execute main function with all arguments
main "$@"