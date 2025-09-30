#!/bin/bash

#
# iOS App Store Deployment Script
# Ainflue Professional Content Creation Platform
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# This script automates the iOS app build and deployment process for App Store submission
#

set -e

# Configuration
APP_NAME="Ainflue"
BUNDLE_ID="com.fahedmlaiel.ainflue"
SCHEME="Ainflue"
WORKSPACE_PATH="ios/Ainflue.xcworkspace"
PROJECT_PATH="ios/Ainflue.xcodeproj"
BUILD_CONFIG="Release"
ARCHIVE_PATH="build/ios/Ainflue.xcarchive"
IPA_PATH="build/ios/Ainflue.ipa"
EXPORT_OPTIONS_PLIST="ios/ExportOptions.plist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Pre-flight checks
log_info "Starting iOS App Store deployment for $APP_NAME"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    log_error "This script must be run on macOS for iOS app deployment"
    exit 1
fi

# Check for required tools
if ! command_exists xcodebuild; then
    log_error "Xcode is not installed or xcodebuild is not in PATH"
    exit 1
fi

if ! command_exists xcrun; then
    log_error "Xcode command line tools are not installed"
    exit 1
fi

# Check for Node.js and npm for React Native build
if ! command_exists node; then
    log_error "Node.js is not installed"
    exit 1
fi

if ! command_exists npm; then
    log_error "npm is not installed"
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Clean previous builds
log_info "Cleaning previous builds..."
rm -rf build/ios
mkdir -p build/ios

# Install React Native dependencies
log_info "Installing React Native dependencies..."
cd react_native
npm install
cd ..

# Install iOS dependencies (CocoaPods)
log_info "Installing iOS dependencies with CocoaPods..."
cd ios
if command_exists pod; then
    pod install
else
    log_warning "CocoaPods not installed, skipping pod install"
fi
cd ..

# Build React Native bundle
log_info "Building React Native bundle for iOS..."
cd react_native
npx react-native bundle \
    --platform ios \
    --dev false \
    --entry-file index.js \
    --bundle-output ../ios/main.jsbundle \
    --assets-dest ../ios/
cd ..

# Create export options plist
log_info "Creating export options plist..."
cat > "$EXPORT_OPTIONS_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>destination</key>
    <string>upload</string>
    <key>uploadBitcode</key>
    <true/>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <true/>
    <key>teamID</key>
    <string>FAHED_MLAIEL_TEAM_ID</string>
    <key>signingStyle</key>
    <string>manual</string>
    <key>provisioningProfiles</key>
    <dict>
        <key>$BUNDLE_ID</key>
        <string>Ainflue App Store Distribution</string>
    </dict>
</dict>
</plist>
EOF

# Build and archive the app
log_info "Building and archiving iOS app..."

if [ -f "$WORKSPACE_PATH" ]; then
    PROJECT_FLAG="-workspace $WORKSPACE_PATH"
else
    PROJECT_FLAG="-project $PROJECT_PATH"
fi

xcodebuild -scheme "$SCHEME" \
    $PROJECT_FLAG \
    -configuration "$BUILD_CONFIG" \
    -destination "generic/platform=iOS" \
    -archivePath "$ARCHIVE_PATH" \
    clean archive \
    CODE_SIGNING_REQUIRED=YES \
    CODE_SIGNING_ALLOWED=YES

if [ $? -eq 0 ]; then
    log_success "iOS app archived successfully"
else
    log_error "Failed to archive iOS app"
    exit 1
fi

# Export IPA for App Store
log_info "Exporting IPA for App Store submission..."
xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportOptionsPlist "$EXPORT_OPTIONS_PLIST" \
    -exportPath "build/ios/" \
    -allowProvisioningUpdates

if [ $? -eq 0 ]; then
    log_success "IPA exported successfully: $IPA_PATH"
else
    log_error "Failed to export IPA"
    exit 1
fi

# Validate the app
log_info "Validating app for App Store submission..."
xcrun altool --validate-app \
    --file "$IPA_PATH" \
    --type ios \
    --username "$APPLE_ID_EMAIL" \
    --password "$APPLE_ID_PASSWORD"

if [ $? -eq 0 ]; then
    log_success "App validation successful"
else
    log_warning "App validation failed or credentials not provided"
fi

# Upload to App Store Connect (if credentials are provided)
if [ -n "$APPLE_ID_EMAIL" ] && [ -n "$APPLE_ID_PASSWORD" ]; then
    log_info "Uploading to App Store Connect..."
    xcrun altool --upload-app \
        --file "$IPA_PATH" \
        --type ios \
        --username "$APPLE_ID_EMAIL" \
        --password "$APPLE_ID_PASSWORD"
    
    if [ $? -eq 0 ]; then
        log_success "App uploaded to App Store Connect successfully!"
        log_info "You can now submit your app for review in App Store Connect"
    else
        log_error "Failed to upload app to App Store Connect"
        exit 1
    fi
else
    log_warning "Apple ID credentials not provided, skipping upload"
    log_info "To upload manually, use:"
    log_info "xcrun altool --upload-app --file $IPA_PATH --type ios --username YOUR_APPLE_ID --password YOUR_APP_SPECIFIC_PASSWORD"
fi

# Cleanup
log_info "Cleaning up temporary files..."
rm -f "$EXPORT_OPTIONS_PLIST"

log_success "iOS deployment completed!"
log_info "Archive location: $ARCHIVE_PATH"
log_info "IPA location: $IPA_PATH"

echo ""
log_info "Next steps:"
echo "1. Go to App Store Connect (https://appstoreconnect.apple.com)"
echo "2. Navigate to your app"
echo "3. Submit for review"
echo "4. Monitor the review process"