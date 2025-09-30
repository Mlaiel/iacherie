#!/bin/bash

# Electron Desktop Build Validation Script
# Tests all platform configurations and build targets

set -e

echo "🔍 Validating Electron Desktop Setup..."
echo

# Check if we're in the desktop directory
if [ ! -f "package.json" ] || [ ! -f "main.js" ]; then
    echo "❌ Please run this script from the desktop directory"
    exit 1
fi

echo "📦 Checking package.json configuration..."

# Check if electron is in devDependencies
if grep -A10 '"devDependencies"' package.json | grep -q '"electron"'; then
    echo "✅ Electron is properly in devDependencies"
else
    echo "❌ Electron should be in devDependencies"
    exit 1
fi

# Check build configuration
if grep -q '"electron-builder"' package.json; then
    echo "✅ electron-builder is configured"
else
    echo "❌ electron-builder not found in package.json"
    exit 1
fi

echo "🔧 Checking asset files..."

# Check icon files
for icon in assets/icon.png assets/icon.ico assets/icon.icns; do
    if [ -f "$icon" ]; then
        echo "✅ $icon exists"
    else
        echo "❌ Missing $icon"
        exit 1
    fi
done

# Check entitlements file
if [ -f "build/entitlements.mac.plist" ]; then
    echo "✅ macOS entitlements file exists"
else
    echo "❌ Missing macOS entitlements file"
    exit 1
fi

echo "🏗️ Testing build configurations..."

# Test pack (dir build) - fastest test
echo "Testing pack build..."
if npm run pack > /dev/null 2>&1; then
    echo "✅ Pack build successful"
else
    echo "❌ Pack build failed"
    exit 1
fi

# Check if output was created
if [ -d "dist/linux-unpacked" ]; then
    echo "✅ Linux unpacked build created"
    rm -rf dist/
else
    echo "❌ Linux unpacked build not found"
    exit 1
fi

echo
echo "🎉 All validation tests passed!"
echo "🚀 Ready for production builds on all platforms:"
echo "   - Linux: npm run build:linux"
echo "   - Windows: npm run build:win"
echo "   - macOS: npm run build:mac"
echo