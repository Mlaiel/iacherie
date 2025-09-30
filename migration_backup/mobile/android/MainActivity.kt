/**
 * Ainflue Android MainActivity - Primary Android Activity
 * 
 * Advanced mobile content creation platform main activity
 * Handles Android-specific lifecycle, permissions, and native service integration
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited under
 * German and international copyright law.
 */

package com.ainflue.mobile

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.hardware.fingerprint.FingerprintManager
import android.media.AudioManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.WindowManager
import androidx.annotation.RequiresApi
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.facebook.react.ReactActivity
import com.facebook.react.ReactActivityDelegate
import com.facebook.react.ReactRootView
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint.fabricEnabled
import com.facebook.react.defaults.DefaultReactActivityDelegate
import kotlinx.coroutines.*
import java.util.*

/**
 * Main Android Activity for Ainflue Mobile Application
 * 
 * Responsibilities:
 * - React Native integration and lifecycle management
 * - Native Android service initialization
 * - Permission management and security
 * - Hardware feature integration (camera, audio, biometrics)
 * - Background service management
 * - Deep linking and intent handling
 * - Performance optimization and memory management
 */
class MainActivity : ReactActivity() {

    companion object {
        private const val TAG = "AinflueMobileActivity"
        private const val PERMISSION_REQUEST_CODE = 1001
        private const val CAMERA_REQUEST_CODE = 1002
        private const val AUDIO_REQUEST_CODE = 1003
        private const val STORAGE_REQUEST_CODE = 1004
        private const val FINGERPRINT_REQUEST_CODE = 1005
        
        // Required permissions for Ainflue platform
        private val REQUIRED_PERMISSIONS = arrayOf(
            android.Manifest.permission.CAMERA,
            android.Manifest.permission.RECORD_AUDIO,
            android.Manifest.permission.WRITE_EXTERNAL_STORAGE,
            android.Manifest.permission.READ_EXTERNAL_STORAGE,
            android.Manifest.permission.ACCESS_FINE_LOCATION,
            android.Manifest.permission.ACCESS_COARSE_LOCATION,
            android.Manifest.permission.READ_CONTACTS,
            android.Manifest.permission.VIBRATE,
            android.Manifest.permission.WAKE_LOCK,
            android.Manifest.permission.INTERNET,
            android.Manifest.permission.ACCESS_NETWORK_STATE,
            android.Manifest.permission.ACCESS_WIFI_STATE,
            android.Manifest.permission.CHANGE_WIFI_STATE,
            android.Manifest.permission.BLUETOOTH,
            android.Manifest.permission.BLUETOOTH_ADMIN,
            android.Manifest.permission.USE_FINGERPRINT,
            android.Manifest.permission.USE_BIOMETRIC
        )
    }

    // Native service managers
    private lateinit var audioRecorder: AudioRecorder
    private lateinit var cameraManager: CameraManager
    private lateinit var fingerprintAuth: FingerprintAuth
    private lateinit var notificationService: NotificationService
    private lateinit var syncService: SyncService
    private lateinit var permissionManager: PermissionManager

    // Activity state
    private var isInitialized = false
    private var hasRequiredPermissions = false
    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    /**
     * Returns the name of the main component registered from JavaScript.
     * This is used to schedule rendering of the component.
     */
    override fun getMainComponentName(): String = "AinflueMobile"

    /**
     * Returns the instance of the ReactActivityDelegate. Here we use a util class
     * DefaultReactActivityDelegate which allows you to easily enable Fabric and Concurrent React
     * (aka React 18) with two boolean flags.
     */
    override fun createReactActivityDelegate(): ReactActivityDelegate =
        DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)

    /**
     * Called when the activity is starting. This is where most initialization should go.
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        Log.i(TAG, "🚀 Ainflue MainActivity onCreate - Starting initialization")
        
        try {
            setupSecurityConfiguration()
            initializeNativeServices()
            setupActivityConfiguration()
            requestRequiredPermissions()
            
            Log.i(TAG, "✅ MainActivity onCreate completed successfully")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ MainActivity onCreate failed", exception)
            handleInitializationError(exception)
        }
    }

    /**
     * Setup security configuration for the activity
     */
    private fun setupSecurityConfiguration() {
        Log.d(TAG, "🔒 Setting up security configuration")
        
        // Prevent screenshots in production
        if (!BuildConfig.DEBUG) {
            window.setFlags(
                WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE
            )
        }
        
        // Set audio mode for high-quality audio recording
        val audioManager = getSystemService(AUDIO_SERVICE) as AudioManager
        audioManager.mode = AudioManager.MODE_NORMAL
        
        Log.d(TAG, "✅ Security configuration completed")
    }

    /**
     * Initialize all native Android services
     */
    private fun initializeNativeServices() {
        Log.d(TAG, "🔧 Initializing native services")
        
        serviceScope.launch {
            try {
                // Initialize Permission Manager first
                permissionManager = PermissionManager(this@MainActivity)
                Log.d(TAG, "✅ PermissionManager initialized")

                // Initialize Audio Recorder
                audioRecorder = AudioRecorder(this@MainActivity)
                audioRecorder.initialize()
                Log.d(TAG, "✅ AudioRecorder initialized")

                // Initialize Camera Manager
                cameraManager = CameraManager(this@MainActivity)
                cameraManager.initialize()
                Log.d(TAG, "✅ CameraManager initialized")

                // Initialize Fingerprint Authentication
                fingerprintAuth = FingerprintAuth(this@MainActivity)
                fingerprintAuth.initialize()
                Log.d(TAG, "✅ FingerprintAuth initialized")

                // Initialize Notification Service
                notificationService = NotificationService(this@MainActivity)
                notificationService.initialize()
                Log.d(TAG, "✅ NotificationService initialized")

                // Initialize Sync Service
                syncService = SyncService(this@MainActivity)
                syncService.initialize()
                Log.d(TAG, "✅ SyncService initialized")

                isInitialized = true
                Log.i(TAG, "🎉 All native services initialized successfully")
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to initialize native services", exception)
                throw exception
            }
        }
    }

    /**
     * Setup activity-specific configuration
     */
    private fun setupActivityConfiguration() {
        Log.d(TAG, "⚙️ Setting up activity configuration")
        
        // Keep screen on during active use
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        
        // Setup hardware acceleration
        window.setFlags(
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED
        )
        
        Log.d(TAG, "✅ Activity configuration completed")
    }

    /**
     * Request all required permissions for the application
     */
    private fun requestRequiredPermissions() {
        Log.d(TAG, "📱 Requesting required permissions")
        
        val missingPermissions = REQUIRED_PERMISSIONS.filter { permission ->
            ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED
        }

        if (missingPermissions.isNotEmpty()) {
            Log.d(TAG, "⚠️ Missing permissions: ${missingPermissions.joinToString(", ")}")
            ActivityCompat.requestPermissions(
                this,
                missingPermissions.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        } else {
            hasRequiredPermissions = true
            Log.d(TAG, "✅ All required permissions already granted")
            onPermissionsGranted()
        }
    }

    /**
     * Handle permission request results
     */
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        Log.d(TAG, "📋 Permission request result: code=$requestCode")
        
        when (requestCode) {
            PERMISSION_REQUEST_CODE -> {
                val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
                hasRequiredPermissions = allGranted
                
                if (allGranted) {
                    Log.i(TAG, "✅ All permissions granted")
                    onPermissionsGranted()
                } else {
                    Log.w(TAG, "⚠️ Some permissions denied")
                    handlePermissionsDenied(permissions, grantResults)
                }
            }
            else -> {
                Log.w(TAG, "🤷 Unknown permission request code: $requestCode")
            }
        }
    }

    /**
     * Called when all required permissions are granted
     */
    private fun onPermissionsGranted() {
        Log.i(TAG, "🎉 All permissions granted - starting services")
        
        serviceScope.launch {
            try {
                // Start native services that require permissions
                if (::audioRecorder.isInitialized) {
                    audioRecorder.startService()
                }
                
                if (::cameraManager.isInitialized) {
                    cameraManager.startService()
                }
                
                if (::fingerprintAuth.isInitialized) {
                    fingerprintAuth.startService()
                }
                
                if (::notificationService.isInitialized) {
                    notificationService.startService()
                }
                
                if (::syncService.isInitialized) {
                    syncService.startService()
                }
                
                Log.i(TAG, "🚀 All services started successfully")
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to start services", exception)
                handleServiceStartError(exception)
            }
        }
    }

    /**
     * Handle denied permissions
     */
    private fun handlePermissionsDenied(permissions: Array<out String>, grantResults: IntArray) {
        Log.w(TAG, "⚠️ Handling denied permissions")
        
        val deniedPermissions = permissions.filterIndexed { index, _ ->
            grantResults[index] != PackageManager.PERMISSION_GRANTED
        }
        
        Log.w(TAG, "❌ Denied permissions: ${deniedPermissions.joinToString(", ")}")
        
        // Show explanation dialog or redirect to settings
        if (::permissionManager.isInitialized) {
            permissionManager.handleDeniedPermissions(deniedPermissions)
        }
    }

    /**
     * Called when the activity becomes visible to the user
     */
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "▶️ MainActivity onResume")
        
        serviceScope.launch {
            try {
                // Resume native services
                if (isInitialized && hasRequiredPermissions) {
                    resumeNativeServices()
                }
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to resume services", exception)
            }
        }
    }

    /**
     * Called when the activity is no longer visible to the user
     */
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "⏸️ MainActivity onPause")
        
        serviceScope.launch {
            try {
                // Pause native services to conserve resources
                if (isInitialized) {
                    pauseNativeServices()
                }
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to pause services", exception)
            }
        }
    }

    /**
     * Called when the activity is finishing or being destroyed
     */
    override fun onDestroy() {
        Log.d(TAG, "🧹 MainActivity onDestroy - Cleaning up")
        
        serviceScope.launch {
            try {
                // Cleanup native services
                if (isInitialized) {
                    cleanupNativeServices()
                }
                
                // Cancel all coroutines
                serviceScope.cancel()
                
                Log.i(TAG, "✅ MainActivity cleanup completed")
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to cleanup services", exception)
            }
        }
        
        super.onDestroy()
    }

    /**
     * Handle activity results (camera, file picker, etc.)
     */
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        Log.d(TAG, "📤 Activity result: code=$requestCode, result=$resultCode")
        
        when (requestCode) {
            CAMERA_REQUEST_CODE -> {
                if (::cameraManager.isInitialized) {
                    cameraManager.handleActivityResult(resultCode, data)
                }
            }
            AUDIO_REQUEST_CODE -> {
                if (::audioRecorder.isInitialized) {
                    audioRecorder.handleActivityResult(resultCode, data)
                }
            }
            else -> {
                Log.d(TAG, "🤷 Unhandled activity result code: $requestCode")
            }
        }
    }

    /**
     * Resume all native services
     */
    private suspend fun resumeNativeServices() {
        Log.d(TAG, "▶️ Resuming native services")
        
        withContext(Dispatchers.IO) {
            arrayOf(
                { if (::audioRecorder.isInitialized) audioRecorder.resume() },
                { if (::cameraManager.isInitialized) cameraManager.resume() },
                { if (::fingerprintAuth.isInitialized) fingerprintAuth.resume() },
                { if (::notificationService.isInitialized) notificationService.resume() },
                { if (::syncService.isInitialized) syncService.resume() }
            ).forEach { resumeAction ->
                try {
                    resumeAction()
                } catch (exception: Exception) {
                    Log.w(TAG, "⚠️ Failed to resume service", exception)
                }
            }
        }
        
        Log.d(TAG, "✅ Native services resumed")
    }

    /**
     * Pause all native services
     */
    private suspend fun pauseNativeServices() {
        Log.d(TAG, "⏸️ Pausing native services")
        
        withContext(Dispatchers.IO) {
            arrayOf(
                { if (::audioRecorder.isInitialized) audioRecorder.pause() },
                { if (::cameraManager.isInitialized) cameraManager.pause() },
                { if (::fingerprintAuth.isInitialized) fingerprintAuth.pause() },
                { if (::notificationService.isInitialized) notificationService.pause() },
                { if (::syncService.isInitialized) syncService.pause() }
            ).forEach { pauseAction ->
                try {
                    pauseAction()
                } catch (exception: Exception) {
                    Log.w(TAG, "⚠️ Failed to pause service", exception)
                }
            }
        }
        
        Log.d(TAG, "✅ Native services paused")
    }

    /**
     * Cleanup all native services
     */
    private suspend fun cleanupNativeServices() {
        Log.d(TAG, "🧹 Cleaning up native services")
        
        withContext(Dispatchers.IO) {
            arrayOf(
                { if (::audioRecorder.isInitialized) audioRecorder.cleanup() },
                { if (::cameraManager.isInitialized) cameraManager.cleanup() },
                { if (::fingerprintAuth.isInitialized) fingerprintAuth.cleanup() },
                { if (::notificationService.isInitialized) notificationService.cleanup() },
                { if (::syncService.isInitialized) syncService.cleanup() },
                { if (::permissionManager.isInitialized) permissionManager.cleanup() }
            ).forEach { cleanupAction ->
                try {
                    cleanupAction()
                } catch (exception: Exception) {
                    Log.w(TAG, "⚠️ Failed to cleanup service", exception)
                }
            }
        }
        
        Log.d(TAG, "✅ Native services cleanup completed")
    }

    /**
     * Handle initialization errors
     */
    private fun handleInitializationError(exception: Exception) {
        Log.e(TAG, "💥 Initialization error occurred", exception)
        
        // In production, would show user-friendly error dialog
        // and possibly restart the activity or exit gracefully
    }

    /**
     * Handle service start errors
     */
    private fun handleServiceStartError(exception: Exception) {
        Log.e(TAG, "💥 Service start error occurred", exception)
        
        // In production, would show user-friendly error dialog
        // and attempt recovery or graceful degradation
    }
}