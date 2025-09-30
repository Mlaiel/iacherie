/**
 * Ainflue Permission Manager - Professional Permission Management System
 * 
 * Advanced permission management system for content creators
 * Supports runtime permissions, security policies, and user education
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited under
 * German and international copyright law.
 */

package com.ainflue.mobile

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.util.Log
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

/**
 * Professional Permission Management System for Ainflue Platform
 * 
 * Features:
 * - Comprehensive runtime permission management
 * - Smart permission request strategies
 * - User education and rationale dialogs
 * - Permission state tracking and analytics
 * - Graceful degradation for denied permissions
 * - Security policy enforcement
 * - Permission group management
 * - Accessibility and compliance support
 * - Background permission handling
 * - Special permission management (overlay, device admin, etc.)
 */
class PermissionManager(private val context: Context) {

    companion object {
        private const val TAG = "AinfluePermissionManager"
        
        // Permission groups for Ainflue platform
        const val GROUP_CORE = "core"
        const val GROUP_MEDIA = "media"
        const val GROUP_LOCATION = "location"
        const val GROUP_COMMUNICATION = "communication"
        const val GROUP_STORAGE = "storage"
        const val GROUP_BIOMETRIC = "biometric"
        const val GROUP_ADVANCED = "advanced"
        
        // Permission request codes
        private const val REQUEST_CODE_PERMISSIONS = 1001
        private const val REQUEST_CODE_SETTINGS = 1002
        
        // Core permissions required for basic functionality
        val CORE_PERMISSIONS = arrayOf(
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.WAKE_LOCK,
            Manifest.permission.VIBRATE
        )
        
        // Media permissions for content creation
        val MEDIA_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.MODIFY_AUDIO_SETTINGS
        )
        
        // Storage permissions for file management
        val STORAGE_PERMISSIONS = arrayOf(
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        ).let { permissions ->
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                permissions + arrayOf(
                    Manifest.permission.READ_MEDIA_IMAGES,
                    Manifest.permission.READ_MEDIA_VIDEO,
                    Manifest.permission.READ_MEDIA_AUDIO
                )
            } else {
                permissions
            }
        }
        
        // Location permissions for content metadata
        val LOCATION_PERMISSIONS = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_BACKGROUND_LOCATION
        )
        
        // Communication permissions for collaboration
        val COMMUNICATION_PERMISSIONS = arrayOf(
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.GET_ACCOUNTS
        )
        
        // Biometric permissions for security
        val BIOMETRIC_PERMISSIONS = arrayOf(
            Manifest.permission.USE_FINGERPRINT,
            Manifest.permission.USE_BIOMETRIC
        )
        
        // Advanced permissions for power features
        val ADVANCED_PERMISSIONS = arrayOf(
            Manifest.permission.SYSTEM_ALERT_WINDOW,
            Manifest.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
            Manifest.permission.FOREGROUND_SERVICE
        )
    }

    /**
     * Permission status enum
     */
    enum class PermissionStatus {
        GRANTED,
        DENIED,
        PERMANENTLY_DENIED,
        NOT_REQUESTED,
        UNKNOWN
    }

    /**
     * Permission request configuration
     */
    data class PermissionRequestConfig(
        val permissions: Array<String>,
        val title: String,
        val message: String,
        val positiveButton: String = "Grant",
        val negativeButton: String = "Deny",
        val showRationale: Boolean = true,
        val allowSkip: Boolean = false,
        val isRequired: Boolean = true,
        val group: String = GROUP_CORE
    ) {
        override fun equals(other: Any?): Boolean {
            if (this === other) return true
            if (javaClass != other?.javaClass) return false

            other as PermissionRequestConfig

            if (!permissions.contentEquals(other.permissions)) return false
            if (title != other.title) return false
            if (message != other.message) return false
            if (positiveButton != other.positiveButton) return false
            if (negativeButton != other.negativeButton) return false
            if (showRationale != other.showRationale) return false
            if (allowSkip != other.allowSkip) return false
            if (isRequired != other.isRequired) return false
            if (group != other.group) return false

            return true
        }

        override fun hashCode(): Int {
            var result = permissions.contentHashCode()
            result = 31 * result + title.hashCode()
            result = 31 * result + message.hashCode()
            result = 31 * result + positiveButton.hashCode()
            result = 31 * result + negativeButton.hashCode()
            result = 31 * result + showRationale.hashCode()
            result = 31 * result + allowSkip.hashCode()
            result = 31 * result + isRequired.hashCode()
            result = 31 * result + group.hashCode()
            return result
        }
    }

    /**
     * Permission state information
     */
    data class PermissionState(
        val permission: String,
        val status: PermissionStatus,
        val requestCount: Int = 0,
        val lastRequestTime: Long = 0L,
        val lastDeniedTime: Long = 0L,
        val rationaleShown: Boolean = false,
        val isPermanentlyDenied: Boolean = false
    )

    /**
     * Permission result callback
     */
    interface PermissionResultCallback {
        fun onPermissionGranted(permissions: Array<String>)
        fun onPermissionDenied(permissions: Array<String>, permanentlyDenied: Array<String>)
        fun onPermissionRationale(permissions: Array<String>, rationale: String)
        fun onPermissionError(error: Exception)
    }

    // Permission state tracking
    private val permissionStates = ConcurrentHashMap<String, PermissionState>()
    private val permissionCallbacks = ConcurrentHashMap<Int, PermissionResultCallback>()
    private var requestCounter = 0
    
    // Permission launchers for modern approach
    private var permissionLauncher: ActivityResultLauncher<Array<String>>? = null
    private var currentCallback: PermissionResultCallback? = null
    
    // Coroutine management
    private val permissionScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    // Initialization state
    private var isInitialized = false

    /**
     * Initialize the permission manager
     */
    fun initialize(activity: FragmentActivity? = null): Boolean {
        try {
            Log.i(TAG, "🔐 Initializing PermissionManager")
            
            // Setup modern permission launcher if activity provided
            activity?.let { fragmentActivity ->
                permissionLauncher = fragmentActivity.registerForActivityResult(
                    ActivityResultContracts.RequestMultiplePermissions()
                ) { permissions ->
                    handlePermissionResult(permissions)
                }
            }
            
            // Initialize permission states
            initializePermissionStates()
            
            isInitialized = true
            Log.i(TAG, "✅ PermissionManager initialized successfully")
            return true
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to initialize PermissionManager", exception)
            return false
        }
    }

    /**
     * Request all required permissions for Ainflue
     */
    suspend fun requestAllPermissions(): Map<String, String> {
        return withContext(Dispatchers.Main) {
            val allPermissions = CORE_PERMISSIONS + 
                               MEDIA_PERMISSIONS + 
                               STORAGE_PERMISSIONS + 
                               LOCATION_PERMISSIONS + 
                               COMMUNICATION_PERMISSIONS + 
                               BIOMETRIC_PERMISSIONS
            
            val permissionResults = mutableMapOf<String, String>()
            
            // Group permissions by type for better UX
            val permissionGroups = mapOf(
                GROUP_CORE to PermissionRequestConfig(
                    permissions = CORE_PERMISSIONS,
                    title = "Core Permissions",
                    message = "Ainflue needs these permissions for basic functionality including network access and notifications.",
                    group = GROUP_CORE
                ),
                GROUP_MEDIA to PermissionRequestConfig(
                    permissions = MEDIA_PERMISSIONS,
                    title = "Media Permissions",
                    message = "Ainflue needs camera and microphone access to capture and protect your creative content.",
                    group = GROUP_MEDIA
                ),
                GROUP_STORAGE to PermissionRequestConfig(
                    permissions = STORAGE_PERMISSIONS,
                    title = "Storage Permissions",
                    message = "Ainflue needs storage access to save and manage your content files securely.",
                    group = GROUP_STORAGE
                ),
                GROUP_LOCATION to PermissionRequestConfig(
                    permissions = LOCATION_PERMISSIONS,
                    title = "Location Permissions",
                    message = "Ainflue uses location data to enhance content metadata and improve protection accuracy.",
                    isRequired = false,
                    allowSkip = true,
                    group = GROUP_LOCATION
                ),
                GROUP_COMMUNICATION to PermissionRequestConfig(
                    permissions = COMMUNICATION_PERMISSIONS,
                    title = "Communication Permissions",
                    message = "Ainflue accesses contacts to help you collaborate with other creators more easily.",
                    isRequired = false,
                    allowSkip = true,
                    group = GROUP_COMMUNICATION
                ),
                GROUP_BIOMETRIC to PermissionRequestConfig(
                    permissions = BIOMETRIC_PERMISSIONS,
                    title = "Biometric Permissions",
                    message = "Ainflue uses biometric authentication to secure your account and content.",
                    isRequired = false,
                    allowSkip = true,
                    group = GROUP_BIOMETRIC
                )
            )
            
            // Request permissions group by group
            for ((groupName, config) in permissionGroups) {
                try {
                    Log.i(TAG, "🔑 Requesting permission group: $groupName")
                    
                    val groupResults = requestPermissionsWithRationale(config)
                    permissionResults.putAll(groupResults.mapValues { entry ->
                        when (entry.value) {
                            true -> "granted"
                            false -> "denied"
                        }
                    })
                    
                    // Check if required permissions were denied
                    if (config.isRequired) {
                        val deniedPermissions = groupResults.filterValues { !it }
                        if (deniedPermissions.isNotEmpty()) {
                            Log.w(TAG, "⚠️ Required permissions denied: ${deniedPermissions.keys}")
                            handleRequiredPermissionsDenied(deniedPermissions.keys.toTypedArray())
                        }
                    }
                    
                } catch (exception: Exception) {
                    Log.e(TAG, "❌ Failed to request permission group: $groupName", exception)
                    config.permissions.forEach { permission ->
                        permissionResults[permission] = "error"
                    }
                }
            }
            
            Log.i(TAG, "✅ Permission request completed. Results: $permissionResults")
            permissionResults
        }
    }

    /**
     * Request specific permissions with rationale
     */
    suspend fun requestPermissionsWithRationale(config: PermissionRequestConfig): Map<String, Boolean> {
        return withContext(Dispatchers.Main) {
            val permissionResults = mutableMapOf<String, Boolean>()
            
            try {
                // Check current permission status
                val (granted, denied) = checkPermissionStatus(config.permissions)
                
                // Add already granted permissions
                granted.forEach { permission ->
                    permissionResults[permission] = true
                }
                
                if (denied.isEmpty()) {
                    Log.d(TAG, "✅ All permissions already granted")
                    return@withContext permissionResults
                }
                
                // Show rationale if needed
                if (config.showRationale && shouldShowRationale(denied)) {
                    val userAccepted = showPermissionRationale(config)
                    if (!userAccepted && !config.allowSkip) {
                        // User rejected rationale for required permissions
                        denied.forEach { permission ->
                            permissionResults[permission] = false
                        }
                        return@withContext permissionResults
                    }
                }
                
                // Request permissions
                val requestResult = requestPermissions(denied, config)
                permissionResults.putAll(requestResult)
                
                // Update permission states
                updatePermissionStates(requestResult)
                
                permissionResults
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to request permissions", exception)
                config.permissions.forEach { permission ->
                    permissionResults[permission] = false
                }
                permissionResults
            }
        }
    }

    /**
     * Check single permission status
     */
    fun checkPermission(permission: String): PermissionStatus {
        return when {
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED -> {
                PermissionStatus.GRANTED
            }
            shouldShowRequestPermissionRationale(permission) -> {
                PermissionStatus.DENIED
            }
            permissionStates[permission]?.requestCount ?: 0 > 0 -> {
                PermissionStatus.PERMANENTLY_DENIED
            }
            else -> {
                PermissionStatus.NOT_REQUESTED
            }
        }
    }

    /**
     * Check multiple permissions status
     */
    fun checkPermissionStatus(permissions: Array<String>): Pair<List<String>, List<String>> {
        val granted = mutableListOf<String>()
        val denied = mutableListOf<String>()
        
        permissions.forEach { permission ->
            if (ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED) {
                granted.add(permission)
            } else {
                denied.add(permission)
            }
        }
        
        return Pair(granted, denied)
    }

    /**
     * Get all permission states
     */
    fun getAllPermissionStates(): Map<String, PermissionState> {
        return permissionStates.toMap()
    }

    /**
     * Open app settings for manual permission management
     */
    fun openSettings() {
        try {
            val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = Uri.fromParts("package", context.packageName, null)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
            
            Log.i(TAG, "📱 Opened app settings for permission management")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to open app settings", exception)
            
            // Fallback to general settings
            try {
                val fallbackIntent = Intent(Settings.ACTION_SETTINGS).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                context.startActivity(fallbackIntent)
            } catch (fallbackException: Exception) {
                Log.e(TAG, "❌ Failed to open fallback settings", fallbackException)
            }
        }
    }

    /**
     * Handle denied permissions with user education
     */
    fun handleDeniedPermissions(deniedPermissions: List<String>) {
        Log.w(TAG, "⚠️ Handling denied permissions: $deniedPermissions")
        
        permissionScope.launch {
            try {
                // Update permission states
                deniedPermissions.forEach { permission ->
                    val currentState = permissionStates[permission] ?: PermissionState(
                        permission = permission,
                        status = PermissionStatus.DENIED
                    )
                    
                    permissionStates[permission] = currentState.copy(
                        status = PermissionStatus.DENIED,
                        lastDeniedTime = System.currentTimeMillis(),
                        isPermanentlyDenied = !shouldShowRequestPermissionRationale(permission)
                    )
                }
                
                // Show educational dialog for critical permissions
                val criticalPermissions = deniedPermissions.filter { permission ->
                    permission in CORE_PERMISSIONS || permission in MEDIA_PERMISSIONS
                }
                
                if (criticalPermissions.isNotEmpty()) {
                    showPermissionEducationDialog(criticalPermissions)
                }
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Error handling denied permissions", exception)
            }
        }
    }

    /**
     * Check if permissions are sufficient for operation
     */
    fun hasRequiredPermissions(requiredPermissions: Array<String>): Boolean {
        return requiredPermissions.all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
    }

    /**
     * Get missing permissions from required list
     */
    fun getMissingPermissions(requiredPermissions: Array<String>): List<String> {
        return requiredPermissions.filter { permission ->
            ContextCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED
        }
    }

    /**
     * Service lifecycle methods
     */
    suspend fun startService() {
        Log.i(TAG, "🚀 Starting PermissionManager service")
        // Service-specific initialization if needed
    }

    fun pause() {
        Log.d(TAG, "⏸️ PermissionManager service paused")
        // Pause any ongoing operations
    }

    fun resume() {
        Log.d(TAG, "▶️ PermissionManager service resumed")
        // Resume operations
    }

    suspend fun cleanup() {
        Log.i(TAG, "🧹 Cleaning up PermissionManager")
        
        try {
            // Cancel coroutines
            permissionScope.cancel()
            
            // Clear callbacks
            permissionCallbacks.clear()
            currentCallback = null
            
            // Reset state
            isInitialized = false
            
            Log.i(TAG, "✅ PermissionManager cleanup completed")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Error during PermissionManager cleanup", exception)
        }
    }

    // ================================
    // PRIVATE HELPER METHODS
    // ================================

    private fun initializePermissionStates() {
        val allPermissions = CORE_PERMISSIONS + 
                           MEDIA_PERMISSIONS + 
                           STORAGE_PERMISSIONS + 
                           LOCATION_PERMISSIONS + 
                           COMMUNICATION_PERMISSIONS + 
                           BIOMETRIC_PERMISSIONS + 
                           ADVANCED_PERMISSIONS
        
        allPermissions.forEach { permission ->
            permissionStates[permission] = PermissionState(
                permission = permission,
                status = checkPermission(permission)
            )
        }
        
        Log.d(TAG, "✅ Permission states initialized for ${allPermissions.size} permissions")
    }

    private suspend fun requestPermissions(permissions: Array<String>, config: PermissionRequestConfig): Map<String, Boolean> {
        return withContext(Dispatchers.Main) {
            val permissionResult = CompletableDeferred<Map<String, Boolean>>()
            
            try {
                if (context is Activity) {
                    // Use traditional approach for Activity context
                    val requestId = ++requestCounter
                    permissionCallbacks[requestId] = object : PermissionResultCallback {
                        override fun onPermissionGranted(permissions: Array<String>) {
                            val results = permissions.associateWith { true }
                            permissionResult.complete(results)
                        }
                        
                        override fun onPermissionDenied(permissions: Array<String>, permanentlyDenied: Array<String>) {
                            val results = permissions.associateWith { false }
                            permissionResult.complete(results)
                        }
                        
                        override fun onPermissionRationale(permissions: Array<String>, rationale: String) {
                            // Handle rationale if needed
                        }
                        
                        override fun onPermissionError(error: Exception) {
                            val results = permissions.associateWith { false }
                            permissionResult.complete(results)
                        }
                    }
                    
                    ActivityCompat.requestPermissions(context, permissions, requestId)
                    
                } else if (permissionLauncher != null) {
                    // Use modern approach with ActivityResultLauncher
                    currentCallback = object : PermissionResultCallback {
                        override fun onPermissionGranted(permissions: Array<String>) {
                            val results = permissions.associateWith { true }
                            permissionResult.complete(results)
                        }
                        
                        override fun onPermissionDenied(permissions: Array<String>, permanentlyDenied: Array<String>) {
                            val results = permissions.associateWith { false }
                            permissionResult.complete(results)
                        }
                        
                        override fun onPermissionRationale(permissions: Array<String>, rationale: String) {
                            // Handle rationale if needed
                        }
                        
                        override fun onPermissionError(error: Exception) {
                            val results = permissions.associateWith { false }
                            permissionResult.complete(results)
                        }
                    }
                    
                    permissionLauncher?.launch(permissions)
                    
                } else {
                    throw IllegalStateException("No valid permission request method available")
                }
                
                permissionResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to request permissions", exception)
                permissions.associateWith { false }
            }
        }
    }

    private suspend fun showPermissionRationale(config: PermissionRequestConfig): Boolean {
        return withContext(Dispatchers.Main) {
            val dialogResult = CompletableDeferred<Boolean>()
            
            try {
                AlertDialog.Builder(context)
                    .setTitle(config.title)
                    .setMessage(config.message)
                    .setPositiveButton(config.positiveButton) { _, _ ->
                        dialogResult.complete(true)
                    }
                    .setNegativeButton(config.negativeButton) { _, _ ->
                        dialogResult.complete(false)
                    }
                    .setCancelable(false)
                    .show()
                
                dialogResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to show permission rationale", exception)
                false
            }
        }
    }

    private suspend fun showPermissionEducationDialog(deniedPermissions: List<String>) {
        withContext(Dispatchers.Main) {
            try {
                val permissionNames = deniedPermissions.map { permission ->
                    getPermissionDisplayName(permission)
                }.joinToString(", ")
                
                AlertDialog.Builder(context)
                    .setTitle("Important Permissions Required")
                    .setMessage("Ainflue needs $permissionNames to provide the best content creation and protection experience. You can grant these permissions in Settings.")
                    .setPositiveButton("Open Settings") { _, _ ->
                        openSettings()
                    }
                    .setNegativeButton("Continue Limited") { _, _ ->
                        // Continue with limited functionality
                    }
                    .show()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to show education dialog", exception)
            }
        }
    }

    private fun handleRequiredPermissionsDenied(deniedPermissions: Array<String>) {
        Log.w(TAG, "⚠️ Required permissions denied: ${deniedPermissions.joinToString()}")
        
        // In a real implementation, this might show a blocking dialog
        // or redirect to a limited functionality mode
    }

    private fun shouldShowRationale(permissions: Array<String>): Boolean {
        return permissions.any { permission ->
            shouldShowRequestPermissionRationale(permission)
        }
    }

    private fun shouldShowRequestPermissionRationale(permission: String): Boolean {
        return if (context is Activity) {
            ActivityCompat.shouldShowRequestPermissionRationale(context, permission)
        } else {
            false
        }
    }

    private fun updatePermissionStates(permissionResults: Map<String, Boolean>) {
        permissionResults.forEach { (permission, granted) ->
            val currentState = permissionStates[permission] ?: PermissionState(
                permission = permission,
                status = PermissionStatus.NOT_REQUESTED
            )
            
            permissionStates[permission] = currentState.copy(
                status = if (granted) PermissionStatus.GRANTED else PermissionStatus.DENIED,
                requestCount = currentState.requestCount + 1,
                lastRequestTime = System.currentTimeMillis(),
                isPermanentlyDenied = !granted && !shouldShowRequestPermissionRationale(permission)
            )
        }
    }

    private fun handlePermissionResult(permissions: Map<String, Boolean>) {
        Log.d(TAG, "📋 Permission result received: $permissions")
        
        val granted = permissions.filterValues { it }.keys.toTypedArray()
        val denied = permissions.filterValues { !it }.keys.toTypedArray()
        val permanentlyDenied = denied.filter { permission ->
            !shouldShowRequestPermissionRationale(permission)
        }.toTypedArray()
        
        currentCallback?.let { callback ->
            if (granted.isNotEmpty()) {
                callback.onPermissionGranted(granted)
            }
            if (denied.isNotEmpty()) {
                callback.onPermissionDenied(denied, permanentlyDenied)
            }
        }
        
        // Update permission states
        updatePermissionStates(permissions)
        
        currentCallback = null
    }

    private fun getPermissionDisplayName(permission: String): String {
        return when (permission) {
            Manifest.permission.CAMERA -> "Camera"
            Manifest.permission.RECORD_AUDIO -> "Microphone"
            Manifest.permission.READ_EXTERNAL_STORAGE -> "Storage"
            Manifest.permission.WRITE_EXTERNAL_STORAGE -> "Storage"
            Manifest.permission.ACCESS_FINE_LOCATION -> "Location"
            Manifest.permission.ACCESS_COARSE_LOCATION -> "Location"
            Manifest.permission.READ_CONTACTS -> "Contacts"
            Manifest.permission.USE_FINGERPRINT -> "Fingerprint"
            Manifest.permission.USE_BIOMETRIC -> "Biometric"
            else -> permission.removePrefix("android.permission.")
                .replace("_", " ")
                .toLowerCase()
                .capitalize()
        }
    }
}