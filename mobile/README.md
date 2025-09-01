# 📱 Ainflue Mobile App Store Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Ainflue mobile application to both the iOS App Store and Google Play Store. The deployment system supports React Native with native iOS and Android integrations.

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.

## 🏗️ Project Structure

```
mobile/
├── android/                 # Android native code and configuration
│   ├── build.gradle        # Android build configuration
│   ├── App.tsx             # Android-specific React Native code
│   └── *.kt                # Kotlin native modules
├── ios/                    # iOS native code and configuration
│   ├── Ainflue.xcodeproj/  # Xcode project
│   ├── App.tsx             # iOS-specific React Native code
│   ├── Info.plist          # iOS app configuration
│   ├── Podfile             # CocoaPods dependencies
│   └── *.swift             # Swift native modules
├── react_native/           # Shared React Native code
│   ├── package.json        # React Native dependencies
│   ├── app.json           # Expo configuration
│   └── src/               # Application source code
├── scripts/               # Deployment scripts
│   ├── deploy.sh          # Universal deployment script
│   ├── deploy-ios.sh      # iOS-specific deployment
│   └── deploy-android.sh  # Android-specific deployment
└── store_assets/          # App store metadata and assets
    ├── ios/               # iOS App Store assets
    ├── android/           # Google Play Store assets
    └── privacy_policy.md  # Privacy policy
```

## 🚀 Quick Start

### Prerequisites

- **macOS** (required for iOS deployment)
- **Node.js** 18.0.0 or later
- **npm** or **yarn**
- **Git**
- **Android SDK** (for Android deployment)
- **Xcode** (for iOS deployment)
- **CocoaPods** (for iOS dependencies)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue/mobile
```

2. Install dependencies:
```bash
cd react_native
npm install
cd ..
```

3. Setup platform-specific dependencies:
```bash
# iOS (macOS only)
cd ios
pod install
cd ..

# Android
# Ensure ANDROID_HOME is set
export ANDROID_HOME=/path/to/android-sdk
```

### Deployment Commands

```bash
# Deploy to iOS App Store (macOS only)
./scripts/deploy.sh ios

# Deploy to Google Play Store
./scripts/deploy.sh android

# Deploy to both platforms
./scripts/deploy.sh both

# Dry run (test without deploying)
./scripts/deploy.sh ios --dry-run
```

## 📱 iOS App Store Deployment

### Prerequisites for iOS

1. **Apple Developer Account** ($99/year)
2. **Xcode** 15.0 or later
3. **macOS** Ventura or later
4. **iOS Distribution Certificate**
5. **App Store Provisioning Profile**

### iOS Setup Steps

1. **Configure Xcode Project:**
   - Open `ios/Ainflue.xcodeproj` in Xcode
   - Set your Team ID in project settings
   - Configure signing certificates

2. **Set Environment Variables:**
```bash
export APPLE_ID_EMAIL="your-apple-id@example.com"
export APPLE_ID_PASSWORD="your-app-specific-password"
export FAHED_MLAIEL_TEAM_ID="your-team-id"
```

3. **Build and Deploy:**
```bash
./scripts/deploy-ios.sh
```

### iOS Deployment Process

The iOS deployment script will:
1. Install React Native dependencies
2. Install iOS dependencies (CocoaPods)
3. Build React Native bundle
4. Archive the iOS app
5. Export IPA for App Store
6. Validate the app
7. Upload to App Store Connect (optional)

### iOS Troubleshooting

- **Code Signing Issues:** Ensure certificates and provisioning profiles are properly configured
- **Build Errors:** Check Xcode version compatibility and dependencies
- **Upload Failures:** Verify Apple ID credentials and app-specific password

## 🤖 Android Google Play Store Deployment

### Prerequisites for Android

1. **Google Play Developer Account** ($25 one-time fee)
2. **Android SDK** 
3. **Java Development Kit** 8 or later
4. **Release Keystore** for app signing

### Android Setup Steps

1. **Configure Build Environment:**
```bash
export ANDROID_HOME=/path/to/android-sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

2. **Create Release Keystore:**
```bash
keytool -genkeypair -alias ainflue-key -keyalg RSA -keysize 2048 \
        -validity 10000 -keystore android/app/release-key.keystore
```

3. **Configure Gradle Properties:**
Create `android/gradle.properties`:
```properties
AINFLUE_UPLOAD_STORE_FILE=release-key.keystore
AINFLUE_UPLOAD_STORE_PASSWORD=your-keystore-password
AINFLUE_UPLOAD_KEY_ALIAS=ainflue-key
AINFLUE_UPLOAD_KEY_PASSWORD=your-key-password
```

4. **Build and Deploy:**
```bash
./scripts/deploy-android.sh
```

### Android Deployment Process

The Android deployment script will:
1. Install React Native dependencies
2. Build React Native bundle
3. Generate release keystore (if needed)
4. Build Android App Bundle (AAB)
5. Build APK for testing
6. Prepare mapping files
7. Generate release notes

### Android Troubleshooting

- **Build Errors:** Check Android SDK and Gradle versions
- **Signing Issues:** Verify keystore configuration
- **Upload Problems:** Ensure Google Play Console access

## 🛠️ Build Configuration

### iOS Build Settings

- **Deployment Target:** iOS 14.0+
- **Supported Devices:** iPhone, iPad
- **Architecture:** arm64, x86_64 (simulator)
- **Swift Version:** 5.0
- **Bitcode:** Enabled for release builds

### Android Build Settings

- **Minimum SDK:** API 26 (Android 8.0)
- **Target SDK:** API 34 (Android 14)
- **Supported ABIs:** arm64-v8a, armeabi-v7a, x86, x86_64
- **ProGuard:** Enabled for release builds
- **App Bundle:** AAB format for Play Store

## 📋 App Store Requirements

### iOS App Store

- **App Icons:** Multiple sizes (1024x1024 for store)
- **Screenshots:** iPhone and iPad variants
- **Privacy Policy:** Required URL
- **App Review Information:** Demo account if needed
- **Content Rating:** Appropriate for all ages
- **Export Compliance:** Encryption usage disclosure

### Google Play Store

- **App Icons:** Adaptive icon support
- **Screenshots:** Phone and tablet variants
- **Feature Graphic:** 1024x500 promotional image
- **Privacy Policy:** Required URL
- **Content Rating:** ESRB/PEGI equivalent
- **Target Audience:** Age-appropriate settings

## 🔐 Security and Compliance

### Code Signing

- **iOS:** Distribution certificate and provisioning profile
- **Android:** Release keystore with strong passwords

### Privacy Compliance

- **GDPR:** European data protection compliance
- **CCPA:** California privacy law compliance
- **COPPA:** Children's privacy protection

### Content Protection

- **Encryption:** App Transport Security (iOS), Network Security (Android)
- **Biometric Auth:** Face ID, Touch ID, Fingerprint
- **Data Protection:** Local and cloud encryption

## 📊 Analytics and Monitoring

### Crash Reporting

- **iOS:** Xcode Organizer, Firebase Crashlytics
- **Android:** Google Play Console, Firebase Crashlytics

### Performance Monitoring

- **React Native:** Flipper debugging
- **Native:** Platform-specific profiling tools

### User Analytics

- **Privacy-first:** Optional analytics with user consent
- **GDPR Compliant:** Data minimization principles

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check dependency versions
   - Clean build directories
   - Update development tools

2. **Signing Errors:**
   - Verify certificate validity
   - Check provisioning profiles
   - Ensure keystore accessibility

3. **Upload Issues:**
   - Validate app metadata
   - Check network connectivity
   - Verify credentials

### Debug Commands

```bash
# Clean React Native cache
npx react-native start --reset-cache

# Clean iOS build
cd ios && xcodebuild clean && cd ..

# Clean Android build
cd android && ./gradlew clean && cd ..

# Check iOS certificates
security find-identity -v -p codesigning

# Check Android keystore
keytool -list -v -keystore android/app/release-key.keystore
```

## 📞 Support

### Getting Help

- **Documentation:** https://ainflue.com/docs
- **Community:** https://community.ainflue.com  
- **Support:** support@ainflue.com
- **Developer:** mlaiel@live.de

### Contributing

Please read our contributing guidelines before submitting pull requests.

## 📄 License

This project is proprietary software owned by Fahed Mlaiel. All rights reserved.

**Copyright © 2025 Fahed Mlaiel**

Unauthorized use, copying, modification, or distribution is strictly prohibited.

---

## 🎯 Next Steps

After successful deployment:

1. **Monitor App Store Reviews:** Respond to user feedback
2. **Track Analytics:** Monitor app performance and usage
3. **Plan Updates:** Regular feature updates and bug fixes
4. **Marketing:** Promote your app through various channels
5. **User Support:** Provide excellent customer service

Happy deploying! 🚀