#!/bin/bash

#
# Android Google Play Store Deployment Script
# Ainflue Professional Content Creation Platform
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# This script automates the Android app build and deployment process for Play Store submission
#

set -e

# Configuration
APP_NAME="Ainflue"
PACKAGE_NAME="com.ainflue.mobile"
BUILD_TYPE="release"
FLAVOR="pro"
APK_PATH="android/build/outputs/apk/${FLAVOR}/${BUILD_TYPE}"
AAB_PATH="android/build/outputs/bundle/${FLAVOR}Release"
MAPPING_PATH="android/build/outputs/mapping/${FLAVOR}Release"

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
log_info "Starting Android Play Store deployment for $APP_NAME"

# Check for required tools
if ! command_exists java; then
    log_error "Java is not installed"
    exit 1
fi

if ! command_exists node; then
    log_error "Node.js is not installed"
    exit 1
fi

if ! command_exists npm; then
    log_error "npm is not installed"
    exit 1
fi

# Check for Android SDK
if [ -z "$ANDROID_HOME" ]; then
    log_error "ANDROID_HOME environment variable is not set"
    log_info "Please set ANDROID_HOME to your Android SDK location"
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Clean previous builds
log_info "Cleaning previous builds..."
rm -rf android/build
rm -rf build/android
mkdir -p build/android

# Install React Native dependencies
log_info "Installing React Native dependencies..."
cd react_native
npm install
cd ..

# Build React Native bundle for Android
log_info "Building React Native bundle for Android..."
cd react_native
npx react-native bundle \
    --platform android \
    --dev false \
    --entry-file index.js \
    --bundle-output ../android/src/main/assets/index.android.bundle \
    --assets-dest ../android/src/main/res/
cd ..

# Generate release keystore if it doesn't exist
KEYSTORE_PATH="android/app/release-key.keystore"
if [ ! -f "$KEYSTORE_PATH" ] && [ -z "$AINFLUE_UPLOAD_STORE_FILE" ]; then
    log_warning "Release keystore not found, generating a new one..."
    log_info "Please provide keystore information:"
    
    read -p "Enter keystore password: " -s KEYSTORE_PASSWORD
    echo
    read -p "Enter key alias: " KEY_ALIAS
    read -p "Enter key password: " -s KEY_PASSWORD
    echo
    read -p "Enter your name: " DNAME_CN
    read -p "Enter organization: " DNAME_O
    read -p "Enter city: " DNAME_L
    read -p "Enter state/province: " DNAME_ST
    read -p "Enter country code (2 letters): " DNAME_C
    
    keytool -genkeypair \
        -alias "$KEY_ALIAS" \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -keystore "$KEYSTORE_PATH" \
        -storepass "$KEYSTORE_PASSWORD" \
        -keypass "$KEY_PASSWORD" \
        -dname "CN=$DNAME_CN, O=$DNAME_O, L=$DNAME_L, ST=$DNAME_ST, C=$DNAME_C"
    
    log_success "Keystore generated successfully"
    
    # Create gradle.properties for release signing
    cat > android/gradle.properties << EOF
AINFLUE_UPLOAD_STORE_FILE=$KEYSTORE_PATH
AINFLUE_UPLOAD_STORE_PASSWORD=$KEYSTORE_PASSWORD
AINFLUE_UPLOAD_KEY_ALIAS=$KEY_ALIAS
AINFLUE_UPLOAD_KEY_PASSWORD=$KEY_PASSWORD
EOF
    
    log_info "Gradle properties created for release signing"
fi

# Build Android App Bundle (AAB) for Play Store
log_info "Building Android App Bundle (AAB) for Play Store..."
cd android
./gradlew clean
./gradlew bundle${FLAVOR^}Release -PenableProguardInReleaseBuilds=true

if [ $? -eq 0 ]; then
    log_success "Android App Bundle built successfully"
else
    log_error "Failed to build Android App Bundle"
    exit 1
fi

# Build APK for testing
log_info "Building APK for testing..."
./gradlew assemble${FLAVOR^}Release -PenableProguardInReleaseBuilds=true

if [ $? -eq 0 ]; then
    log_success "APK built successfully"
else
    log_error "Failed to build APK"
    exit 1
fi

cd ..

# Copy artifacts to build directory
log_info "Copying build artifacts..."
cp "$AAB_PATH/app-${FLAVOR}-release.aab" "build/android/"
cp "$APK_PATH/app-${FLAVOR}-release.apk" "build/android/"

# Copy ProGuard mapping files if they exist
if [ -d "$MAPPING_PATH" ]; then
    cp -r "$MAPPING_PATH" "build/android/mapping/"
    log_success "ProGuard mapping files copied"
fi

# Verify AAB file
log_info "Verifying AAB file..."
AAB_FILE="build/android/app-${FLAVOR}-release.aab"
if [ -f "$AAB_FILE" ]; then
    FILE_SIZE=$(du -h "$AAB_FILE" | cut -f1)
    log_success "AAB file created: $AAB_FILE (Size: $FILE_SIZE)"
else
    log_error "AAB file not found"
    exit 1
fi

# Verify APK file
APK_FILE="build/android/app-${FLAVOR}-release.apk"
if [ -f "$APK_FILE" ]; then
    FILE_SIZE=$(du -h "$APK_FILE" | cut -f1)
    log_success "APK file created: $APK_FILE (Size: $FILE_SIZE)"
else
    log_error "APK file not found"
    exit 1
fi

# Check for Google Play Console CLI (optional)
if command_exists gcloud; then
    log_info "Google Cloud SDK detected"
    
    if [ -n "$GOOGLE_PLAY_SERVICE_ACCOUNT_KEY" ]; then
        log_info "Authenticating with Google Play Console..."
        gcloud auth activate-service-account --key-file="$GOOGLE_PLAY_SERVICE_ACCOUNT_KEY"
        
        # Note: This requires additional setup with Google Play Developer API
        log_warning "Automated upload to Play Console requires Google Play Developer API setup"
        log_info "Visit: https://developers.google.com/android-publisher/getting_started"
    else
        log_warning "GOOGLE_PLAY_SERVICE_ACCOUNT_KEY not set, skipping automated upload"
    fi
else
    log_warning "Google Cloud SDK not found, skipping automated upload"
fi

# Generate release notes template
log_info "Generating release notes template..."
cat > "build/android/release-notes.txt" << EOF
# Release Notes for Ainflue v1.0.0

## New Features
- Professional content creation platform
- AI-powered content protection
- Multi-platform distribution
- Advanced biometric security
- Real-time collaboration tools

## Improvements
- Enhanced performance and stability
- Improved user interface
- Better security measures
- Optimized for latest Android versions

## Bug Fixes
- Various stability improvements
- Performance optimizations

## Technical Details
- Minimum Android version: API 26 (Android 8.0)
- Target Android version: API 34 (Android 14)
- Build type: Release
- ProGuard enabled: Yes
- Signing: Release keystore

## Contact
Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
EOF

log_success "Android deployment completed!"

echo ""
log_info "Build artifacts:"
echo "📱 AAB file: $AAB_FILE"
echo "📱 APK file: $APK_FILE"
echo "🗂️ Build directory: build/android/"

echo ""
log_info "Next steps for Play Store submission:"
echo "1. Go to Google Play Console (https://play.google.com/console)"
echo "2. Create a new app or select existing app"
echo "3. Upload the AAB file: $AAB_FILE"
echo "4. Fill in store listing information"
echo "5. Add screenshots and app description"
echo "6. Set pricing and distribution"
echo "7. Submit for review"

echo ""
log_info "Testing instructions:"
echo "1. Install the APK on a test device: adb install $APK_FILE"
echo "2. Test all functionality thoroughly"
echo "3. Verify app signing and security features"

echo ""
log_warning "Important reminders:"
echo "- Keep your keystore file secure and backed up"
echo "- Upload mapping files to Play Console for crash reporting"
echo "- Test on multiple devices and Android versions"
echo "- Ensure compliance with Play Store policies"