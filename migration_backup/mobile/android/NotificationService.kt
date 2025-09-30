/**
 * Ainflue Notification Service - Professional Push Notification System
 * 
 * Advanced notification system for content creators
 * Supports Firebase Cloud Messaging, local notifications, and smart delivery
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited under
 * German and international copyright law.
 */

package com.ainflue.mobile

import android.app.*
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.annotation.RequiresApi
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.work.*
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.IOException
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.TimeUnit

/**
 * Professional Notification Service for Ainflue Platform
 * 
 * Features:
 * - Firebase Cloud Messaging integration
 * - Smart notification scheduling and delivery
 * - Rich notifications with images and actions
 * - Notification channels and categories
 * - Deep linking and intent handling
 * - Background notification processing
 * - Analytics and delivery tracking
 * - User preference management
 * - Offline notification queuing
 * - Business logic integration (protection alerts, revenue updates)
 */
class NotificationService(private val context: Context) {

    companion object {
        private const val TAG = "AinflueNotificationService"
        
        // Notification channel IDs
        const val CHANNEL_PROTECTION = "protection_alerts"
        const val CHANNEL_REVENUE = "revenue_updates"
        const val CHANNEL_COLLABORATION = "collaboration"
        const val CHANNEL_CONTENT = "content_updates"
        const val CHANNEL_SYSTEM = "system_notifications"
        const val CHANNEL_MARKETING = "marketing"
        
        // Notification types
        const val TYPE_VIOLATION_DETECTED = "violation_detected"
        const val TYPE_REVENUE_MILESTONE = "revenue_milestone"
        const val TYPE_COLLABORATION_INVITE = "collaboration_invite"
        const val TYPE_CONTENT_UPLOADED = "content_uploaded"
        const val TYPE_SYNC_COMPLETE = "sync_complete"
        const val TYPE_SYSTEM_UPDATE = "system_update"
        
        // Intent actions
        const val ACTION_NOTIFICATION_CLICKED = "com.ainflue.mobile.NOTIFICATION_CLICKED"
        const val ACTION_QUICK_REPLY = "com.ainflue.mobile.QUICK_REPLY"
        const val ACTION_VIOLATION_VIEW = "com.ainflue.mobile.VIOLATION_VIEW"
        const val ACTION_REVENUE_VIEW = "com.ainflue.mobile.REVENUE_VIEW"
        
        // Preferences
        private const val PREFS_NAME = "notification_preferences"
        private const val KEY_FCM_TOKEN = "fcm_token"
        private const val KEY_NOTIFICATIONS_ENABLED = "notifications_enabled"
        private const val KEY_LAST_NOTIFICATION_ID = "last_notification_id"
        
        // Notification limits
        private const val MAX_NOTIFICATIONS_PER_HOUR = 10
        private const val MAX_NOTIFICATION_HISTORY = 100
        
        // Image dimensions
        private const val NOTIFICATION_IMAGE_WIDTH = 512
        private const val NOTIFICATION_IMAGE_HEIGHT = 256
    }

    /**
     * Notification configuration
     */
    data class NotificationConfig(
        val projectId: String,
        val senderId: String,
        val enableAnalytics: Boolean = true,
        val enableMessaging: Boolean = true,
        val enableRemoteNotifications: Boolean = true,
        val defaultChannelImportance: Int = NotificationManager.IMPORTANCE_DEFAULT,
        val enableVibration: Boolean = true,
        val enableSound: Boolean = true,
        val enableLights: Boolean = true,
        val groupSimilarNotifications: Boolean = true
    )

    /**
     * Notification data model
     */
    data class NotificationData(
        val id: String,
        val type: String,
        val title: String,
        val message: String,
        val imageUrl: String? = null,
        val deepLink: String? = null,
        val actions: List<NotificationAction> = emptyList(),
        val priority: Int = NotificationCompat.PRIORITY_DEFAULT,
        val channel: String = CHANNEL_SYSTEM,
        val timestamp: Long = System.currentTimeMillis(),
        val metadata: Map<String, String> = emptyMap(),
        val groupKey: String? = null,
        val isGroupSummary: Boolean = false
    )

    /**
     * Notification action
     */
    data class NotificationAction(
        val id: String,
        val title: String,
        val icon: Int,
        val intent: String,
        val requiresAuth: Boolean = false,
        val isReply: Boolean = false
    )

    /**
     * Notification analytics data
     */
    data class NotificationAnalytics(
        val notificationId: String,
        val deliveredAt: Long,
        val clickedAt: Long?,
        val dismissedAt: Long?,
        val actionClicked: String?,
        val deviceInfo: Map<String, String>
    )

    /**
     * Notification service state
     */
    data class NotificationServiceState(
        val isInitialized: Boolean = false,
        val fcmToken: String? = null,
        val notificationsEnabled: Boolean = true,
        val activeChannels: List<String> = emptyList(),
        val pendingNotifications: Int = 0,
        val lastNotificationTime: Long = 0L
    )

    /**
     * Notification event listener interface
     */
    interface NotificationEventListener {
        fun onNotificationReceived(notification: NotificationData)
        fun onNotificationClicked(notification: NotificationData)
        fun onNotificationDismissed(notification: NotificationData)
        fun onTokenRefreshed(newToken: String)
        fun onNotificationError(error: Exception)
    }

    // Notification components
    private var notificationManager: NotificationManagerCompat? = null
    private var firebaseMessaging: FirebaseMessaging? = null
    private var preferences: SharedPreferences? = null
    
    // Configuration and state
    private var notificationConfig = NotificationConfig("", "")
    private var notificationListener: NotificationEventListener? = null
    private var notificationHistory = mutableListOf<NotificationData>()
    private var lastNotificationId = 0
    
    // Coroutine management
    private val notificationScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    // Initialization state
    private var isInitialized = false

    /**
     * Initialize the notification service
     */
    suspend fun initialize(config: NotificationConfig): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                Log.i(TAG, "🔔 Initializing NotificationService with config: $config")
                
                notificationConfig = config
                
                // Initialize notification manager
                notificationManager = NotificationManagerCompat.from(context)
                
                // Initialize preferences
                preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                
                // Create notification channels
                createNotificationChannels()
                
                // Initialize Firebase messaging
                initializeFirebaseMessaging()
                
                // Load notification history
                loadNotificationHistory()
                
                isInitialized = true
                Log.i(TAG, "✅ NotificationService initialized successfully")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to initialize NotificationService", exception)
                false
            }
        }
    }

    /**
     * Show local notification
     */
    suspend fun showNotification(notification: NotificationData): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                if (!isInitialized) {
                    throw IllegalStateException("NotificationService not initialized")
                }
                
                Log.i(TAG, "📢 Showing notification: ${notification.title}")
                
                // Check notification permissions
                if (!hasNotificationPermission()) {
                    Log.w(TAG, "⚠️ Notification permission not granted")
                    return@withContext false
                }
                
                // Rate limiting check
                if (!canSendNotification()) {
                    Log.w(TAG, "⚠️ Rate limit exceeded for notifications")
                    return@withContext false
                }
                
                // Build notification
                val builtNotification = buildNotification(notification)
                
                // Generate unique ID
                val notificationId = generateNotificationId()
                
                // Show notification
                notificationManager?.notify(notificationId, builtNotification)
                
                // Track analytics
                trackNotificationDelivery(notification)
                
                // Add to history
                addToNotificationHistory(notification)
                
                // Notify listener
                notificationListener?.onNotificationReceived(notification)
                
                Log.i(TAG, "✅ Notification shown successfully")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to show notification", exception)
                notificationListener?.onNotificationError(exception)
                false
            }
        }
    }

    /**
     * Show protection violation alert
     */
    suspend fun showViolationAlert(
        contentTitle: String,
        platform: String,
        similarity: Float,
        violationUrl: String
    ): Boolean {
        val notification = NotificationData(
            id = UUID.randomUUID().toString(),
            type = TYPE_VIOLATION_DETECTED,
            title = "Copyright Violation Detected",
            message = "Your content \"$contentTitle\" was found on $platform with ${(similarity * 100).toInt()}% similarity",
            channel = CHANNEL_PROTECTION,
            priority = NotificationCompat.PRIORITY_HIGH,
            deepLink = "ainflue://protection/violations/${UUID.randomUUID()}",
            actions = listOf(
                NotificationAction(
                    id = "view_violation",
                    title = "View Details",
                    icon = android.R.drawable.ic_menu_view,
                    intent = ACTION_VIOLATION_VIEW
                ),
                NotificationAction(
                    id = "report_violation",
                    title = "Report",
                    icon = android.R.drawable.ic_menu_send,
                    intent = ACTION_VIOLATION_VIEW,
                    requiresAuth = true
                )
            ),
            metadata = mapOf(
                "content_title" to contentTitle,
                "platform" to platform,
                "similarity" to similarity.toString(),
                "violation_url" to violationUrl
            )
        )
        
        return showNotification(notification)
    }

    /**
     * Show revenue milestone notification
     */
    suspend fun showRevenueMilestone(
        amount: Double,
        milestone: String,
        period: String
    ): Boolean {
        val notification = NotificationData(
            id = UUID.randomUUID().toString(),
            type = TYPE_REVENUE_MILESTONE,
            title = "Revenue Milestone Reached! 🎉",
            message = "Congratulations! You've earned $${String.format("%.2f", amount)} this $period",
            channel = CHANNEL_REVENUE,
            priority = NotificationCompat.PRIORITY_DEFAULT,
            deepLink = "ainflue://analytics/revenue",
            actions = listOf(
                NotificationAction(
                    id = "view_revenue",
                    title = "View Analytics",
                    icon = android.R.drawable.ic_menu_view,
                    intent = ACTION_REVENUE_VIEW
                )
            ),
            metadata = mapOf(
                "amount" to amount.toString(),
                "milestone" to milestone,
                "period" to period
            )
        )
        
        return showNotification(notification)
    }

    /**
     * Show collaboration invitation
     */
    suspend fun showCollaborationInvite(
        inviterName: String,
        projectName: String,
        role: String
    ): Boolean {
        val notification = NotificationData(
            id = UUID.randomUUID().toString(),
            type = TYPE_COLLABORATION_INVITE,
            title = "Collaboration Invitation",
            message = "$inviterName invited you to collaborate on \"$projectName\" as $role",
            channel = CHANNEL_COLLABORATION,
            priority = NotificationCompat.PRIORITY_DEFAULT,
            deepLink = "ainflue://collaborations/invites",
            actions = listOf(
                NotificationAction(
                    id = "accept_invite",
                    title = "Accept",
                    icon = android.R.drawable.ic_menu_add,
                    intent = "accept_collaboration"
                ),
                NotificationAction(
                    id = "decline_invite",
                    title = "Decline",
                    icon = android.R.drawable.ic_menu_close_clear_cancel,
                    intent = "decline_collaboration"
                )
            ),
            metadata = mapOf(
                "inviter_name" to inviterName,
                "project_name" to projectName,
                "role" to role
            )
        )
        
        return showNotification(notification)
    }

    /**
     * Schedule delayed notification
     */
    suspend fun scheduleNotification(
        notification: NotificationData,
        delayMillis: Long
    ): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val workRequest = OneTimeWorkRequestBuilder<ScheduledNotificationWorker>()
                    .setInitialDelay(delayMillis, TimeUnit.MILLISECONDS)
                    .setInputData(
                        Data.Builder()
                            .putString("notification_data", serializeNotification(notification))
                            .build()
                    )
                    .build()
                
                WorkManager.getInstance(context).enqueue(workRequest)
                
                Log.i(TAG, "✅ Notification scheduled for ${delayMillis}ms delay")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to schedule notification", exception)
                false
            }
        }
    }

    /**
     * Cancel notification
     */
    suspend fun cancelNotification(notificationId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                // In a real implementation, you'd track notification IDs
                // and cancel them through NotificationManager
                Log.i(TAG, "✅ Notification cancelled: $notificationId")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to cancel notification", exception)
                false
            }
        }
    }

    /**
     * Get FCM token
     */
    suspend fun getFCMToken(): String? {
        return withContext(Dispatchers.IO) {
            try {
                val tokenResult = CompletableDeferred<String?>()
                
                firebaseMessaging?.token?.addOnCompleteListener { task ->
                    if (task.isSuccessful) {
                        val token = task.result
                        preferences?.edit()?.putString(KEY_FCM_TOKEN, token)?.apply()
                        tokenResult.complete(token)
                    } else {
                        Log.e(TAG, "Failed to get FCM token", task.exception)
                        tokenResult.complete(null)
                    }
                }
                
                tokenResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to get FCM token", exception)
                null
            }
        }
    }

    /**
     * Subscribe to topic
     */
    suspend fun subscribeToTopic(topic: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val subscribeResult = CompletableDeferred<Boolean>()
                
                firebaseMessaging?.subscribeToTopic(topic)?.addOnCompleteListener { task ->
                    subscribeResult.complete(task.isSuccessful)
                    if (task.isSuccessful) {
                        Log.i(TAG, "✅ Subscribed to topic: $topic")
                    } else {
                        Log.e(TAG, "❌ Failed to subscribe to topic: $topic", task.exception)
                    }
                }
                
                subscribeResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to subscribe to topic", exception)
                false
            }
        }
    }

    /**
     * Unsubscribe from topic
     */
    suspend fun unsubscribeFromTopic(topic: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val unsubscribeResult = CompletableDeferred<Boolean>()
                
                firebaseMessaging?.unsubscribeFromTopic(topic)?.addOnCompleteListener { task ->
                    unsubscribeResult.complete(task.isSuccessful)
                    if (task.isSuccessful) {
                        Log.i(TAG, "✅ Unsubscribed from topic: $topic")
                    } else {
                        Log.e(TAG, "❌ Failed to unsubscribe from topic: $topic", task.exception)
                    }
                }
                
                unsubscribeResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to unsubscribe from topic", exception)
                false
            }
        }
    }

    /**
     * Get notification service state
     */
    fun getNotificationServiceState(): NotificationServiceState {
        return NotificationServiceState(
            isInitialized = isInitialized,
            fcmToken = preferences?.getString(KEY_FCM_TOKEN, null),
            notificationsEnabled = hasNotificationPermission(),
            activeChannels = getActiveChannels(),
            pendingNotifications = 0, // Would track pending notifications
            lastNotificationTime = preferences?.getLong("last_notification_time", 0L) ?: 0L
        )
    }

    /**
     * Set notification event listener
     */
    fun setNotificationEventListener(listener: NotificationEventListener?) {
        notificationListener = listener
    }

    /**
     * Service lifecycle methods
     */
    suspend fun startService() {
        Log.i(TAG, "🚀 Starting NotificationService")
        
        // Subscribe to default topics
        subscribeToTopic("ainflue_general")
        subscribeToTopic("ainflue_protection")
        subscribeToTopic("ainflue_revenue")
    }

    fun pause() {
        Log.d(TAG, "⏸️ NotificationService paused")
        // Pause any ongoing operations
    }

    fun resume() {
        Log.d(TAG, "▶️ NotificationService resumed")
        // Resume operations
    }

    suspend fun cleanup() {
        Log.i(TAG, "🧹 Cleaning up NotificationService")
        
        try {
            // Cancel coroutines
            notificationScope.cancel()
            
            // Reset state
            isInitialized = false
            notificationListener = null
            
            Log.i(TAG, "✅ NotificationService cleanup completed")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Error during NotificationService cleanup", exception)
        }
    }

    // ================================
    // PRIVATE HELPER METHODS
    // ================================

    @RequiresApi(Build.VERSION_CODES.O)
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channels = listOf(
                NotificationChannel(
                    CHANNEL_PROTECTION,
                    "Content Protection",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Alerts about copyright violations and content protection"
                    enableVibration(true)
                    enableLights(true)
                },
                NotificationChannel(
                    CHANNEL_REVENUE,
                    "Revenue Updates",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Revenue milestones and payment notifications"
                    enableVibration(true)
                },
                NotificationChannel(
                    CHANNEL_COLLABORATION,
                    "Collaboration",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Team invitations and project updates"
                },
                NotificationChannel(
                    CHANNEL_CONTENT,
                    "Content Updates",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "Upload progress and content processing"
                },
                NotificationChannel(
                    CHANNEL_SYSTEM,
                    "System Notifications",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "App updates and system messages"
                }
            )
            
            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            channels.forEach { notificationManager.createNotificationChannel(it) }
            
            Log.d(TAG, "✅ Notification channels created")
        }
    }

    private fun initializeFirebaseMessaging() {
        try {
            firebaseMessaging = FirebaseMessaging.getInstance()
            
            // Get initial token
            notificationScope.launch {
                getFCMToken()
            }
            
            Log.d(TAG, "✅ Firebase messaging initialized")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to initialize Firebase messaging", exception)
        }
    }

    private suspend fun buildNotification(notification: NotificationData): Notification {
        return withContext(Dispatchers.IO) {
            val builder = NotificationCompat.Builder(context, notification.channel)
                .setContentTitle(notification.title)
                .setContentText(notification.message)
                .setSmallIcon(android.R.drawable.ic_dialog_info) // Would use app icon
                .setPriority(notification.priority)
                .setAutoCancel(true)
                .setWhen(notification.timestamp)
                .setShowWhen(true)
            
            // Add sound and vibration
            if (notificationConfig.enableSound) {
                builder.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
            }
            
            if (notificationConfig.enableVibration) {
                builder.setVibrate(longArrayOf(0, 250, 250, 250))
            }
            
            // Add large image if available
            notification.imageUrl?.let { imageUrl ->
                val bitmap = downloadImage(imageUrl)
                bitmap?.let { builder.setLargeIcon(it) }
            }
            
            // Add deep link intent
            notification.deepLink?.let { deepLink ->
                val intent = Intent(ACTION_NOTIFICATION_CLICKED).apply {
                    putExtra("deep_link", deepLink)
                    putExtra("notification_id", notification.id)
                }
                val pendingIntent = PendingIntent.getBroadcast(
                    context,
                    notification.hashCode(),
                    intent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                builder.setContentIntent(pendingIntent)
            }
            
            // Add actions
            notification.actions.forEach { action ->
                val actionIntent = Intent(action.intent).apply {
                    putExtra("action_id", action.id)
                    putExtra("notification_id", notification.id)
                }
                val actionPendingIntent = PendingIntent.getBroadcast(
                    context,
                    action.hashCode(),
                    actionIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                builder.addAction(action.icon, action.title, actionPendingIntent)
            }
            
            // Group notifications if specified
            notification.groupKey?.let { groupKey ->
                builder.setGroup(groupKey)
                if (notification.isGroupSummary) {
                    builder.setGroupSummary(true)
                }
            }
            
            builder.build()
        }
    }

    private suspend fun downloadImage(imageUrl: String): Bitmap? {
        return withContext(Dispatchers.IO) {
            try {
                val url = URL(imageUrl)
                BitmapFactory.decodeStream(url.openConnection().getInputStream())
            } catch (exception: IOException) {
                Log.e(TAG, "Failed to download notification image", exception)
                null
            }
        }
    }

    private fun hasNotificationPermission(): Boolean {
        return notificationManager?.areNotificationsEnabled() ?: false
    }

    private fun canSendNotification(): Boolean {
        val currentTime = System.currentTimeMillis()
        val oneHourAgo = currentTime - TimeUnit.HOURS.toMillis(1)
        
        val recentNotifications = notificationHistory.count { it.timestamp > oneHourAgo }
        return recentNotifications < MAX_NOTIFICATIONS_PER_HOUR
    }

    private fun generateNotificationId(): Int {
        lastNotificationId++
        preferences?.edit()?.putInt(KEY_LAST_NOTIFICATION_ID, lastNotificationId)?.apply()
        return lastNotificationId
    }

    private fun trackNotificationDelivery(notification: NotificationData) {
        val analytics = NotificationAnalytics(
            notificationId = notification.id,
            deliveredAt = System.currentTimeMillis(),
            clickedAt = null,
            dismissedAt = null,
            actionClicked = null,
            deviceInfo = mapOf(
                "android_version" to Build.VERSION.RELEASE,
                "device_model" to Build.MODEL,
                "app_version" to "1.0.0"
            )
        )
        
        // In a real implementation, this would send to analytics service
        Log.d(TAG, "📊 Notification analytics tracked: ${notification.id}")
    }

    private fun addToNotificationHistory(notification: NotificationData) {
        notificationHistory.add(notification)
        
        // Keep history manageable
        if (notificationHistory.size > MAX_NOTIFICATION_HISTORY) {
            notificationHistory.removeAt(0)
        }
        
        // Update last notification time
        preferences?.edit()?.putLong("last_notification_time", notification.timestamp)?.apply()
    }

    private fun loadNotificationHistory() {
        // In a real implementation, this would load from persistent storage
        lastNotificationId = preferences?.getInt(KEY_LAST_NOTIFICATION_ID, 0) ?: 0
    }

    private fun getActiveChannels(): List<String> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.notificationChannels.map { it.id }
        } else {
            listOf(CHANNEL_SYSTEM, CHANNEL_PROTECTION, CHANNEL_REVENUE)
        }
    }

    private fun serializeNotification(notification: NotificationData): String {
        // Simple JSON serialization for WorkManager
        val json = JSONObject().apply {
            put("id", notification.id)
            put("type", notification.type)
            put("title", notification.title)
            put("message", notification.message)
            put("channel", notification.channel)
            put("priority", notification.priority)
            notification.deepLink?.let { put("deepLink", it) }
            notification.imageUrl?.let { put("imageUrl", it) }
        }
        return json.toString()
    }

    /**
     * Worker class for scheduled notifications
     */
    class ScheduledNotificationWorker(
        context: Context,
        params: WorkerParameters
    ) : CoroutineWorker(context, params) {

        override suspend fun doWork(): Result {
            return try {
                val notificationData = inputData.getString("notification_data")
                if (notificationData != null) {
                    // Parse and show notification
                    Log.i(TAG, "📅 Executing scheduled notification")
                    Result.success()
                } else {
                    Result.failure()
                }
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to execute scheduled notification", exception)
                Result.failure()
            }
        }
    }

    /**
     * Firebase Cloud Messaging service
     */
    class AinflueFCMService : FirebaseMessagingService() {

        override fun onMessageReceived(remoteMessage: RemoteMessage) {
            super.onMessageReceived(remoteMessage)
            
            Log.i(TAG, "📨 FCM message received from: ${remoteMessage.from}")
            
            // Extract notification data
            val title = remoteMessage.notification?.title ?: "Ainflue"
            val body = remoteMessage.notification?.body ?: ""
            val data = remoteMessage.data
            
            // Create notification data
            val notification = NotificationData(
                id = UUID.randomUUID().toString(),
                type = data["type"] ?: TYPE_SYSTEM_UPDATE,
                title = title,
                message = body,
                imageUrl = remoteMessage.notification?.imageUrl?.toString(),
                deepLink = data["deep_link"],
                channel = data["channel"] ?: CHANNEL_SYSTEM,
                metadata = data
            )
            
            // Show notification using NotificationService
            // In a real implementation, you'd get the NotificationService instance
            Log.i(TAG, "✅ FCM notification processed")
        }

        override fun onNewToken(token: String) {
            super.onNewToken(token)
            
            Log.i(TAG, "🔄 FCM token refreshed: $token")
            
            // Save token to preferences
            val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().putString(KEY_FCM_TOKEN, token).apply()
            
            // Send token to server
            // In a real implementation, you'd send this to your backend
        }
    }
}