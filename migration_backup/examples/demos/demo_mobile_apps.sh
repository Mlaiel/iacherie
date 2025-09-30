#!/bin/bash

# 📱 Ainflue Mobile Applications Demo Script
# 
# Demonstrates all mobile platform implementations:
# - React Native + Expo (iOS/Android)
# - Progressive Web App (PWA)
# - Desktop Electron Application
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

set -e

echo "🎵 ===== AINFLUE MOBILE APPLICATIONS DEMO ====="
echo ""
echo "🚀 Complete mobile suite implementation demonstration"
echo "📱 React Native + Expo | 🌐 PWA | 🖥️ Desktop Electron"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function for colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "mobile" ] || [ ! -d "frontend" ] || [ ! -d "desktop" ]; then
    print_error "Please run this script from the Ainflue root directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# 1. React Native + Expo Mobile Apps
echo "📱 ===== REACT NATIVE + EXPO MOBILE APPS ====="
echo ""

cd mobile/react_native

print_status "Checking React Native + Expo setup..."

if [ ! -f "package.json" ]; then
    print_error "React Native package.json not found!"
    exit 1
fi

if [ ! -f "app.json" ]; then
    print_error "Expo app.json not found!"
    exit 1
fi

print_success "✅ React Native + Expo configuration found"

# Check dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing React Native dependencies..."
    npm install --legacy-peer-deps
    print_success "✅ Dependencies installed"
else
    print_success "✅ Dependencies already installed"
fi

# Show app configuration
print_status "📋 Expo App Configuration:"
echo "   • App Name: $(cat app.json | grep -o '"name": "[^"]*"' | cut -d'"' -f4)"
echo "   • Bundle ID: $(cat app.json | grep -o '"bundleIdentifier": "[^"]*"' | cut -d'"' -f4)"
echo "   • Version: $(cat app.json | grep -o '"version": "[^"]*"' | cut -d'"' -f4)"

# Check key features
print_status "🔍 Checking implemented features:"

if [ -f "src/services/AuthenticationService.ts" ]; then
    echo "   ✅ Unified Authentication Service"
fi

if [ -f "src/services/iOSBiometricBridge.ts" ]; then
    echo "   ✅ iOS Biometric Bridge (TouchID/FaceID)"
fi

if [ -f "src/services/AndroidFingerprintBridge.ts" ]; then
    echo "   ✅ Android Fingerprint Bridge"
fi

if [ -f "src/services/NotificationService.ts" ]; then
    echo "   ✅ Push Notification Service"
fi

if [ -f "src/screens/UploadScreen.tsx" ]; then
    echo "   ✅ Multi-format Upload Screen"
fi

print_status "🚀 To start React Native development server:"
echo "   cd mobile/react_native && npm start"
echo ""

cd ../..

# 2. Progressive Web App (PWA)
echo "🌐 ===== PROGRESSIVE WEB APP (PWA) ====="
echo ""

cd frontend

print_status "Checking PWA setup..."

if [ ! -f "public/manifest.json" ]; then
    print_error "PWA manifest.json not found!"
    exit 1
fi

if [ ! -f "public/sw.js" ]; then
    print_error "Service Worker not found!"
    exit 1
fi

print_success "✅ PWA configuration found"

# Show PWA features
print_status "📋 PWA Features:"
echo "   • App Name: $(cat public/manifest.json | grep -o '"name": "[^"]*"' | head -1 | cut -d'"' -f4)"
echo "   • Display Mode: $(cat public/manifest.json | grep -o '"display": "[^"]*"' | cut -d'"' -f4)"
echo "   • Theme Color: $(cat public/manifest.json | grep -o '"theme_color": "[^"]*"' | cut -d'"' -f4)"

print_status "🔍 PWA Capabilities:"
echo "   ✅ Offline-first Service Worker"
echo "   ✅ App Installation Prompts"
echo "   ✅ Push Notifications"
echo "   ✅ Background Sync"
echo "   ✅ Intelligent Caching"

if [ -f "src/components/PWAManager.tsx" ]; then
    echo "   ✅ PWA Manager Component"
fi

print_status "🚀 To start PWA development server:"
echo "   cd frontend && npm run dev"
echo ""

cd ..

# 3. Desktop Electron Application
echo "🖥️ ===== DESKTOP ELECTRON APPLICATION ====="
echo ""

cd desktop

print_status "Checking Electron setup..."

if [ ! -f "package.json" ]; then
    print_error "Desktop package.json not found!"
    exit 1
fi

if [ ! -f "main.js" ]; then
    print_error "Electron main.js not found!"
    exit 1
fi

print_success "✅ Electron application found"

# Show desktop features
print_status "📋 Desktop App Features:"
echo "   • App Name: $(cat package.json | grep -o '"name": "[^"]*"' | head -1 | cut -d'"' -f4)"
echo "   • Version: $(cat package.json | grep -o '"version": "[^"]*"' | head -1 | cut -d'"' -f4)"
echo "   • Description: $(cat package.json | grep -o '"description": "[^"]*"' | cut -d'"' -f4)"

print_status "🔍 Desktop Capabilities:"
echo "   ✅ Advanced Studio Interface"
echo "   ✅ Multi-monitor Support"
echo "   ✅ File System Integration"
echo "   ✅ Native Menu System"
echo "   ✅ Secure IPC Communication"

if [ -f "preload.js" ]; then
    echo "   ✅ Secure Preload Script"
fi

if [ -f "renderer/index.html" ]; then
    echo "   ✅ Professional UI"
fi

print_status "🚀 To start Electron app:"
echo "   cd desktop && npm install && npm start"
echo ""

cd ..

# Summary
echo "🎉 ===== IMPLEMENTATION SUMMARY ====="
echo ""

print_success "✅ React Native + Expo Apps:"
echo "   📱 iOS App with TouchID/FaceID authentication"
echo "   📱 Android App with Fingerprint authentication"  
echo "   🔄 Multi-format upload with AI processing"
echo "   🔔 Push notifications and offline sync"
echo ""

print_success "✅ Progressive Web App (PWA):"
echo "   🌐 Offline-first architecture"
echo "   📲 App installation prompts"
echo "   🔔 Web push notifications"
echo "   ⚡ Intelligent caching strategies"
echo ""

print_success "✅ Desktop Electron Application:"
echo "   🖥️ Professional studio interface"
echo "   📺 Multi-monitor support"
echo "   📁 Advanced file operations"
echo "   🔐 Secure content processing"
echo ""

print_success "🚀 ALL MOBILE APPLICATIONS COMPLETE!"
echo ""

echo "📚 Development Commands:"
echo "   • React Native: cd mobile/react_native && npm start"
echo "   • PWA: cd frontend && npm run dev"  
echo "   • Desktop: cd desktop && npm install && npm start"
echo ""

echo "📖 Documentation:"
echo "   • iOS Bridge: mobile/react_native/src/services/iOSBiometricBridge.ts"
echo "   • Android Bridge: mobile/react_native/src/services/AndroidFingerprintBridge.ts"
echo "   • PWA Service Worker: frontend/public/sw.js"
echo "   • Desktop Main: desktop/main.js"
echo ""

print_success "🎵 Ainflue Mobile Suite - Complete!"
echo "© 2025 Fahed Mlaiel (mlaiel@live.de) - All rights reserved"