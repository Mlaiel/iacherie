# Ainflue Desktop - Troubleshooting Guide

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This software and concept are the exclusive intellectual property of Fahed Mlaiel.  
Any unauthorized use, copying, distribution, or reverse engineering is strictly prohibited.  
Legal action will be taken against violators under German and international copyright law.  
Contact: mlaiel@live.de for licensing inquiries.

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Installation Problems](#installation-problems)
4. [Performance Issues](#performance-issues)
5. [Audio/Video Problems](#audiovideo-problems)
6. [File Upload Issues](#file-upload-issues)
7. [AI Processing Problems](#ai-processing-problems)
8. [Network Connectivity](#network-connectivity)
9. [Security & Authentication](#security--authentication)
10. [Platform Integration](#platform-integration)
11. [Advanced Diagnostics](#advanced-diagnostics)
12. [Log Analysis](#log-analysis)
13. [Recovery Procedures](#recovery-procedures)
14. [Contact Support](#contact-support)

---

## Quick Diagnostics

### Automated Diagnostic Tool

Run the built-in diagnostic tool to quickly identify common issues:

```bash
# Run comprehensive diagnostics
npm run diagnose

# Or specific category diagnostics
npm run diagnose:system
npm run diagnose:audio
npm run diagnose:network
npm run diagnose:security
```

### System Information Check

```bash
# Get detailed system information
npm run system-info

# Output includes:
# - Operating system and version
# - Node.js and Electron versions
# - Available memory and storage
# - Graphics and audio hardware
# - Network configuration
```

### Quick Health Check

```bash
# Verify application health
npm run health-check

# Returns:
# ✅ Application Status: Running
# ✅ Database Connection: Connected
# ✅ API Endpoints: Accessible
# ✅ Security: Active
# ⚠️ Warnings: 1 (see detailed report)
```

---

## Common Issues

### 1. Application Won't Start

#### Symptoms
- Application fails to launch
- White screen on startup
- Immediate crash after launch

#### Solutions

**Check System Requirements:**
```bash
# Verify system compatibility
node --version  # Should be 18.0.0+
npm --version   # Should be 9.0.0+

# Check available resources
free -h         # Linux
vm_stat         # macOS
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows
```

**Clear Application Data:**
```bash
# Remove corrupted user data
rm -rf ~/Library/Application\ Support/Ainflue  # macOS
rm -rf ~/.config/Ainflue                       # Linux
del /q "%APPDATA%\Ainflue"                     # Windows

# Restart application
npm start
```

**Reinstall Dependencies:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### 2. Slow Performance

#### Symptoms
- Sluggish UI response
- Long loading times
- High CPU/memory usage

#### Solutions

**Check Resource Usage:**
```bash
# Monitor application performance
npm run monitor

# View resource usage
top -p $(pgrep -f ainflue)  # Linux
Activity Monitor            # macOS
Task Manager               # Windows
```

**Optimize Settings:**
```javascript
// Disable resource-intensive features temporarily
Settings → Performance → {
  enableGPUAcceleration: false,
  enableAIProcessing: false,
  maxConcurrentUploads: 1,
  enableRealTimePreview: false
}
```

**Clear Cache:**
```bash
# Clear application cache
npm run clear-cache

# Or manually:
rm -rf ~/Library/Caches/Ainflue     # macOS
rm -rf ~/.cache/Ainflue             # Linux
del /q "%LOCALAPPDATA%\Ainflue\Cache" # Windows
```

### 3. Audio Not Working

#### Symptoms
- No audio playback
- Microphone not detected
- Audio distortion or crackling

#### Solutions

**Check Audio Permissions:**
```bash
# Verify microphone permissions (macOS)
tccutil reset Microphone com.ainflue.desktop

# Check audio devices
npm run check-audio-devices
```

**Reset Audio Settings:**
```javascript
// Reset to default audio configuration
Settings → Audio → {
  sampleRate: 48000,
  bufferSize: 512,
  inputDevice: "default",
  outputDevice: "default"
}
```

**Update Audio Drivers:**
```bash
# Check audio system status
pulseaudio --check    # Linux
system_profiler SPAudioDataType  # macOS
# Windows: Device Manager → Sound controllers
```

### 4. Video Processing Fails

#### Symptoms
- Video files won't process
- Corrupted output files
- Processing gets stuck

#### Solutions

**Check File Format Support:**
```bash
# List supported formats
npm run supported-formats

# Convert unsupported files
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

**Free Up Storage Space:**
```bash
# Check available space
df -h .              # Linux/macOS
dir /-c              # Windows

# Clean temporary files
npm run clean-temp
```

**Reset Processing Engine:**
```bash
# Restart processing services
npm run restart-processing

# Or reset configuration
rm -f ~/Library/Application\ Support/Ainflue/processing.json
```

---

## Installation Problems

### Failed Installation

#### Windows Issues

**Antivirus Interference:**
```batch
REM Temporarily disable real-time protection
REM Add Ainflue to antivirus exclusions:
REM - Installation directory
REM - %APPDATA%\Ainflue
REM - %LOCALAPPDATA%\Ainflue
```

**Insufficient Permissions:**
```batch
REM Run installer as administrator
REM Right-click installer → "Run as administrator"

REM Or use command line:
powershell -Command "Start-Process 'AinfluStudio-Setup.exe' -Verb RunAs"
```

**Windows Defender SmartScreen:**
```batch
REM Click "More info" → "Run anyway"
REM Or temporarily disable SmartScreen:
REM Settings → Security → Windows Defender → SmartScreen → Off
```

#### macOS Issues

**Gatekeeper Prevention:**
```bash
# Allow unsigned application (development only)
sudo spctl --master-disable

# Or add specific exception:
sudo spctl --add /Applications/Ainflue\ Studio.app
sudo xattr -rd com.apple.quarantine /Applications/Ainflue\ Studio.app
```

**Notarization Issues:**
```bash
# Check notarization status
spctl -a -vvv -t install /Applications/Ainflue\ Studio.app

# Manual verification:
codesign -dv --verbose=4 /Applications/Ainflue\ Studio.app
```

#### Linux Issues

**Missing Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libgconf-2-4 libxss1 libgconf2-dev libxtst6 libxrandr2 libasound2-dev libpangocairo-1.0-0 libatk1.0-dev libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0

# CentOS/RHEL
sudo yum install gtk3 libXScrnSaver GConf2 alsa-lib
```

**AppImage Permissions:**
```bash
# Make AppImage executable
chmod +x Ainflue-Studio-*.AppImage

# Install FUSE if needed
sudo apt-get install fuse
```

### Update Failures

**Auto-update Stuck:**
```bash
# Force manual update
npm run force-update

# Or download latest version manually
curl -L https://releases.ainflue.com/latest/download
```

**Rollback Failed Update:**
```bash
# Restore previous version
npm run rollback

# Or manual restoration:
cp ~/Library/Application\ Support/Ainflue/backup/app.asar resources/
```

---

## Performance Issues

### High CPU Usage

#### Symptoms
- CPU usage above 80%
- System becomes unresponsive
- Fan noise increases significantly

#### Diagnosis
```bash
# Monitor CPU usage by component
npm run monitor:cpu

# Profile application performance
npm run profile:start
# Use application normally for 2-3 minutes
npm run profile:stop
npm run profile:analyze
```

#### Solutions

**Disable Resource-Intensive Features:**
```javascript
// Temporary performance mode
const performanceMode = {
  aiProcessing: false,
  realTimePreview: false,
  backgroundAnalysis: false,
  automaticBackup: false,
  cloudSync: false
};
```

**Optimize Processing Settings:**
```javascript
// Reduce processing quality for better performance
const processingSettings = {
  videoQuality: "medium",      // instead of "high"
  audioSampleRate: 44100,      // instead of 48000
  maxConcurrentTasks: 2,       // instead of 4
  enableGPUAcceleration: true, // if available
  chunkSize: "small"           // process in smaller chunks
};
```

### Memory Leaks

#### Symptoms
- Memory usage continuously increasing
- Application becomes slower over time
- System runs out of memory

#### Diagnosis
```bash
# Monitor memory usage over time
npm run monitor:memory

# Generate memory report
npm run memory:report

# Detect memory leaks
npm run memory:leak-detection
```

#### Solutions

**Restart Application Periodically:**
```bash
# Set up automatic restart (development)
npm run schedule-restart --interval=4h
```

**Clear Memory Manually:**
```javascript
// Force garbage collection (development mode)
if (process.env.NODE_ENV === 'development') {
  global.gc();
}

// Clear caches
clearImageCache();
clearAudioCache();
clearAnalyticsCache();
```

### Storage Issues

#### Symptoms
- "Disk full" errors
- Cannot save projects
- Slow file operations

#### Solutions

**Clean Up Storage:**
```bash
# Automated cleanup
npm run cleanup:storage

# Manual cleanup
npm run cleanup:cache
npm run cleanup:temp
npm run cleanup:logs
npm run cleanup:thumbnails
```

**Change Storage Locations:**
```javascript
// Redirect temporary files to external drive
Settings → Storage → {
  tempDirectory: "/external/drive/ainflue/temp",
  cacheDirectory: "/external/drive/ainflue/cache",
  projectsDirectory: "/external/drive/ainflue/projects"
}
```

---

## Audio/Video Problems

### Audio Issues

#### No Audio Output

**Check Audio System:**
```bash
# Linux
pulseaudio --check
pactl list sinks

# macOS
system_profiler SPAudioDataType
sudo kextstat | grep -i audio

# Windows
dxdiag /t dxdiag_output.txt
```

**Reset Audio Configuration:**
```javascript
// Reset audio settings to defaults
const defaultAudioSettings = {
  sampleRate: 48000,
  bufferSize: 512,
  channels: 2,
  inputLatency: 0,
  outputLatency: 0,
  enableEchoCancellation: false,
  enableNoiseSuppression: false
};
```

#### Audio Latency Problems

**Optimize Audio Settings:**
```javascript
// Low-latency configuration
const lowLatencySettings = {
  bufferSize: 128,        // Smaller buffer for lower latency
  sampleRate: 44100,      // Standard sample rate
  enableAsioDriver: true, // Windows only
  exclusiveMode: true,    // Prevent other apps from using audio device
  priorityBoost: true     // Increase audio thread priority
};
```

**Check Audio Driver:**
```bash
# Update audio drivers
# Windows: Device Manager → Audio devices → Update driver
# macOS: Check for system updates
# Linux: sudo apt-get install pavucontrol alsa-utils
```

### Video Issues

#### Video Won't Play

**Check Codec Support:**
```bash
# List supported video codecs
npm run codecs:list

# Convert to supported format
ffmpeg -i input.mov -c:v libx264 -c:a aac -preset fast output.mp4
```

**Hardware Acceleration:**
```javascript
// Enable hardware acceleration
Settings → Video → {
  enableHardwareAcceleration: true,
  decoder: "hardware",  // or "software"
  renderer: "gpu"       // or "cpu"
}
```

#### Poor Video Quality

**Adjust Quality Settings:**
```javascript
// High-quality processing
const qualitySettings = {
  videoCodec: "h264",
  bitrate: "10M",           // 10 Mbps
  resolution: "1920x1080",
  frameRate: 30,
  colorSpace: "rec709",
  pixelFormat: "yuv420p"
};
```

**Check Graphics Drivers:**
```bash
# Update graphics drivers
# NVIDIA: nvidia-smi
# AMD: amdgpu-info
# Intel: intel-gpu-tools
```

---

## File Upload Issues

### Upload Failures

#### Large File Uploads

**Symptoms:**
- Upload stops at specific percentage
- "Request timeout" errors
- Connection resets

**Solutions:**

**Increase Timeout Settings:**
```javascript
// Extend timeout for large files
const uploadSettings = {
  timeout: 600000,        // 10 minutes
  chunkSize: 5 * 1024 * 1024,  // 5MB chunks
  maxRetries: 5,
  retryDelay: 2000
};
```

**Use Chunked Upload:**
```javascript
// Enable chunked upload for large files
const chunkUploader = {
  enableChunking: true,
  chunkSize: 10 * 1024 * 1024,  // 10MB chunks
  parallelChunks: 3,
  resumableUpload: true
};
```

#### Network Interruptions

**Enable Resume Capability:**
```javascript
// Resumable upload configuration
const resumeSettings = {
  enableResume: true,
  checkpointInterval: 30000,  // Save progress every 30s
  maxResumeAttempts: 10,
  resumeTimeout: 60000
};
```

### Format Not Supported

#### Check Supported Formats

**List All Supported Formats:**
```bash
npm run formats:supported

# Output example:
# Video: mp4, mov, avi, mkv, webm, wmv
# Audio: mp3, wav, flac, aac, m4a, ogg
# Image: jpg, png, gif, bmp, webp, tiff
```

**Convert Unsupported Files:**
```bash
# Video conversion examples
ffmpeg -i input.flv -c:v libx264 -c:a aac output.mp4
ffmpeg -i input.mkv -c:v copy -c:a copy output.mp4

# Audio conversion examples
ffmpeg -i input.wma -c:a libmp3lame output.mp3
ffmpeg -i input.opus -c:a aac output.m4a

# Image conversion examples
convert input.tga output.png
magick input.psd output.jpg
```

---

## AI Processing Problems

### AI Analysis Fails

#### Symptoms
- AI processing gets stuck
- "AI service unavailable" errors
- Analysis returns empty results

#### Solutions

**Check AI Service Status:**
```bash
# Verify AI service connectivity
npm run ai:status

# Test AI endpoints
npm run ai:test-endpoints

# Reset AI service connection
npm run ai:reset
```

**Optimize Input Data:**
```javascript
// Prepare content for AI analysis
const optimizeForAI = {
  // Reduce file size for faster processing
  maxFileSize: 100 * 1024 * 1024,  // 100MB
  
  // Optimize video for AI
  videoSettings: {
    resolution: "720p",    // Reduce from 4K
    frameRate: 15,         // Reduce from 60fps
    duration: 300          // Limit to 5 minutes
  },
  
  // Optimize audio for AI
  audioSettings: {
    sampleRate: 22050,     // Reduce from 48kHz
    channels: 1,           // Mono instead of stereo
    bitrate: 128           // kbps
  }
};
```

### Performance Prediction Issues

#### Inaccurate Predictions

**Calibrate AI Models:**
```bash
# Update AI models with latest data
npm run ai:update-models

# Recalibrate prediction algorithms
npm run ai:recalibrate

# Clear prediction cache
npm run ai:clear-cache
```

**Provide More Context:**
```javascript
// Improve prediction accuracy with additional context
const enhancedContext = {
  targetAudience: "18-34",
  contentCategory: "music",
  platform: "tiktok",
  language: "en",
  timeOfDay: "evening",
  seasonality: "summer",
  trendingTopics: ["viral", "dance", "challenge"]
};
```

---

## Network Connectivity

### Connection Issues

#### Cannot Connect to Services

**Check Network Status:**
```bash
# Test connectivity
ping api.ainflue.com
curl -I https://api.ainflue.com/health

# Check DNS resolution
nslookup api.ainflue.com
dig api.ainflue.com
```

**Verify Firewall Settings:**
```bash
# Common ports used by Ainflue:
# 443 (HTTPS API)
# 80 (HTTP redirect)
# 8080 (Development server)
# 5000 (AI services)

# Windows Firewall
netsh advfirewall firewall add rule name="Ainflue" dir=in action=allow program="path\to\ainflue.exe"

# macOS Firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Ainflue\ Studio.app

# Linux iptables
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

#### Proxy Configuration

**Configure Proxy Settings:**
```javascript
// Proxy configuration
const proxySettings = {
  proxyType: "http",      // http, https, socks5
  proxyHost: "proxy.company.com",
  proxyPort: 8080,
  username: "user",       // if required
  password: "pass",       // if required
  bypassList: [           // domains to bypass proxy
    "localhost",
    "127.0.0.1",
    "*.local"
  ]
};
```

**Test Proxy Connection:**
```bash
# Test proxy connectivity
curl --proxy http://proxy.company.com:8080 https://api.ainflue.com/health

# Set system proxy for testing
export http_proxy=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080
```

### SSL/TLS Issues

#### Certificate Errors

**Trust Custom Certificates:**
```bash
# Add custom CA certificate
# macOS
sudo security add-trusted-cert -d root -r trustRoot -k /System/Library/Keychains/SystemRootCertificates.keychain certificate.crt

# Linux
sudo cp certificate.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Windows
certmgr.msc → Trusted Root Certification Authorities → Import certificate.crt
```

**Disable SSL Verification (Development Only):**
```javascript
// WARNING: Only for development/testing
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

// Better: Use custom certificate validation
const https = require('https');
const agent = new https.Agent({
  rejectUnauthorized: false,
  checkServerIdentity: function(host, cert) {
    // Custom certificate validation logic
    return undefined;
  }
});
```

---

## Security & Authentication

### Login Problems

#### Authentication Failures

**Clear Stored Credentials:**
```bash
# Remove stored authentication data
rm -f ~/Library/Application\ Support/Ainflue/credentials.json  # macOS
rm -f ~/.config/Ainflue/credentials.json                       # Linux
del "%APPDATA%\Ainflue\credentials.json"                       # Windows
```

**Reset OAuth Flow:**
```javascript
// Reinitialize OAuth authentication
const resetOAuth = {
  clearTokens: true,
  clearRefreshToken: true,
  clearUserSession: true,
  redirectToLogin: true
};
```

#### Permission Errors

**Check User Permissions:**
```bash
# Verify user has necessary permissions
ls -la ~/Library/Application\ Support/Ainflue/  # macOS
ls -la ~/.config/Ainflue/                        # Linux
icacls "%APPDATA%\Ainflue"                       # Windows
```

**Fix Permission Issues:**
```bash
# Fix file permissions
chmod -R 755 ~/Library/Application\ Support/Ainflue/  # macOS
chmod -R 755 ~/.config/Ainflue/                       # Linux
# Windows: Right-click folder → Properties → Security → Full Control
```

### Two-Factor Authentication Issues

#### 2FA Code Not Working

**Check Time Synchronization:**
```bash
# Sync system time
sudo ntpdate -s time.nist.gov  # macOS/Linux
w32tm /resync                  # Windows
```

**Generate Backup Codes:**
```bash
# Use backup authentication codes
# Settings → Security → Two-Factor Authentication → Backup Codes
```

---

## Platform Integration

### Social Media Connection Issues

#### Platform Authentication Fails

**Check API Credentials:**
```javascript
// Verify platform API credentials
const platformCredentials = {
  youtube: {
    clientId: "check_youtube_console",
    clientSecret: "check_youtube_console",
    redirectUri: "https://ainflue.com/auth/youtube/callback"
  },
  tiktok: {
    clientKey: "check_tiktok_developers",
    clientSecret: "check_tiktok_developers"
  },
  instagram: {
    appId: "check_facebook_developers",
    appSecret: "check_facebook_developers"
  }
};
```

**Refresh Platform Tokens:**
```bash
# Refresh expired platform tokens
npm run platform:refresh-tokens

# Or individually:
npm run platform:refresh --platform=youtube
npm run platform:refresh --platform=tiktok
npm run platform:refresh --platform=instagram
```

#### Upload to Platform Fails

**Check Platform Limits:**
```javascript
// Common platform limitations
const platformLimits = {
  youtube: {
    maxFileSize: "256GB",
    maxDuration: "12 hours",
    supportedFormats: [".mp4", ".mov", ".avi", ".wmv", ".flv", ".webm"]
  },
  tiktok: {
    maxFileSize: "4GB",
    maxDuration: "10 minutes",
    supportedFormats: [".mp4", ".mov", ".webm"]
  },
  instagram: {
    maxFileSize: "4GB",
    maxDuration: "60 minutes",
    aspectRatio: "1.91:1 to 9:16"
  }
};
```

**Optimize for Platform:**
```bash
# YouTube optimization
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k youtube_optimized.mp4

# TikTok optimization
ffmpeg -i input.mp4 -vf "scale=1080:1920" -c:v libx264 -preset fast -crf 23 tiktok_optimized.mp4

# Instagram optimization
ffmpeg -i input.mp4 -vf "scale=1080:1080" -c:v libx264 -preset medium -crf 20 instagram_optimized.mp4
```

---

## Advanced Diagnostics

### Debug Mode

#### Enable Debug Logging

**Comprehensive Debug Mode:**
```bash
# Start with full debug logging
DEBUG=* npm start

# Or specific components:
DEBUG=ainflue:audio,ainflue:video,ainflue:ai npm start

# Windows:
set DEBUG=* && npm start
```

**Debug Configuration:**
```javascript
// Enable debug features
const debugConfig = {
  enableDevTools: true,
  enableInspector: true,
  enableProfiler: true,
  logLevel: "debug",
  enableCrashReporter: true,
  enablePerformanceMonitoring: true
};
```

### Performance Profiling

#### CPU Profiling

**Generate CPU Profile:**
```bash
# Start CPU profiling
npm run profile:cpu:start

# Use application normally for 2-3 minutes

# Stop and analyze
npm run profile:cpu:stop
npm run profile:cpu:analyze
```

#### Memory Profiling

**Generate Memory Profile:**
```bash
# Memory usage snapshot
npm run profile:memory:snapshot

# Memory leak detection
npm run profile:memory:leaks

# Heap analysis
npm run profile:memory:heap
```

### Network Diagnostics

#### Network Traffic Analysis

**Monitor Network Requests:**
```bash
# Log all network requests
npm run network:monitor

# Analyze API response times
npm run network:analyze-latency

# Check bandwidth usage
npm run network:bandwidth
```

---

## Log Analysis

### Log Locations

#### Default Log Directories

```bash
# macOS
~/Library/Logs/Ainflue/
~/Library/Application Support/Ainflue/logs/

# Windows
%USERPROFILE%\AppData\Roaming\Ainflue\logs\
%LOCALAPPDATA%\Ainflue\logs\

# Linux
~/.config/Ainflue/logs/
/tmp/ainflue-logs/
```

#### Log Types

```bash
# Main application logs
main.log              # Main process events
renderer.log           # Renderer process events
ipc.log               # IPC communication
security.log          # Security events
performance.log       # Performance metrics

# Component-specific logs
audio.log             # Audio processing
video.log             # Video processing
ai.log                # AI service interactions
upload.log            # File uploads
platform.log          # Platform integrations

# Error logs
error.log             # Application errors
crash.log             # Crash reports
```

### Log Analysis Tools

#### Built-in Log Viewer

```bash
# View recent logs
npm run logs:view

# Filter by level
npm run logs:view --level=error
npm run logs:view --level=warn

# Filter by component
npm run logs:view --component=audio
npm run logs:view --component=ai

# Search logs
npm run logs:search --query="upload failed"
npm run logs:search --query="memory" --since="1h"
```

#### Export Logs for Support

```bash
# Create support package
npm run support:create-package

# Includes:
# - Application logs (last 7 days)
# - System information
# - Performance metrics
# - Error reports
# - Configuration (sanitized)
```

---

## Recovery Procedures

### Application Recovery

#### Corrupted Installation

**Repair Installation:**
```bash
# Verify installation integrity
npm run verify:installation

# Repair corrupted files
npm run repair:installation

# Reinstall if necessary
npm run reinstall:clean
```

#### Lost Configuration

**Restore Default Configuration:**
```bash
# Backup current config
cp ~/Library/Application\ Support/Ainflue/config.json ~/Desktop/config.backup.json

# Restore defaults
npm run config:reset

# Or restore from backup
npm run config:restore --from=backup.json
```

### Data Recovery

#### Recover Lost Projects

**Project Recovery:**
```bash
# Scan for recoverable projects
npm run recovery:scan-projects

# Recover from automatic backups
npm run recovery:restore-projects

# Recover from temporary files
npm run recovery:temp-files
```

#### Recover Upload Queue

**Resume Interrupted Uploads:**
```bash
# Check upload queue status
npm run uploads:status

# Resume interrupted uploads
npm run uploads:resume

# Clear failed uploads
npm run uploads:clear-failed
```

### Emergency Procedures

#### Complete Application Reset

**Nuclear Option - Complete Reset:**
```bash
# WARNING: This will delete ALL user data
# Backup important data first!

# Stop application
pkill -f ainflue

# Remove all application data
rm -rf ~/Library/Application\ Support/Ainflue    # macOS
rm -rf ~/.config/Ainflue                         # Linux
rd /s /q "%APPDATA%\Ainflue"                     # Windows

# Reinstall application
npm run install:fresh
```

---

## Contact Support

### Before Contacting Support

#### Information to Gather

1. **System Information**
   ```bash
   npm run system-info > system_info.txt
   ```

2. **Error Logs**
   ```bash
   npm run logs:export --last=24h > error_logs.txt
   ```

3. **Reproduction Steps**
   - Exact steps that led to the issue
   - When the issue first occurred
   - How frequently it occurs

4. **Screenshots/Videos**
   - Screenshots of error messages
   - Screen recording of the issue (if possible)

#### Support Package

**Create Complete Support Package:**
```bash
# Generates comprehensive support package
npm run support:package

# Package includes:
# - System information
# - Application logs (sanitized)
# - Performance metrics
# - Error reports
# - Configuration (sensitive data removed)
# - Crash dumps (if any)
```

### Support Channels

#### Authorized Support Only

**⚠️ IMPORTANT: Support is only provided to authorized users**

- **Email:** mlaiel@live.de (include license key)
- **Include:** Support package generated above
- **Response Time:** 24-48 hours for licensed users

#### Enterprise Support

For enterprise customers with priority support agreements:
- **Dedicated Support:** Available via private channels
- **Response Time:** 4-8 hours during business hours
- **Phone Support:** Available for critical issues

### Legal Notice

This software is proprietary and protected by international copyright law. Support is only provided to legitimate license holders. Any unauthorized use, reverse engineering, or distribution is strictly prohibited and will result in legal action.

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
This troubleshooting guide contains proprietary diagnostic procedures and must not be distributed without authorization.