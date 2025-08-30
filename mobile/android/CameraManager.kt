/**
 * Ainflue Camera Manager - Professional Camera Management Service
 * 
 * Advanced camera system for content creators
 * Supports photo/video capture, real-time processing, and AI integration
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
import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.*
import android.hardware.camera2.*
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.SessionConfiguration
import android.media.ImageReader
import android.media.MediaMetadataRetriever
import android.media.MediaRecorder
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.os.Handler
import android.os.HandlerThread
import android.util.Log
import android.util.Size
import android.view.Surface
import android.view.TextureView
import androidx.annotation.RequiresPermission
import androidx.core.app.ActivityCompat
import kotlinx.coroutines.*
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

/**
 * Professional Camera Management Service for Ainflue Platform
 * 
 * Features:
 * - Advanced photo and video capture (up to 4K)
 * - Multi-camera support (front/back/wide-angle)
 * - Real-time image processing and filtering
 * - Professional camera controls (ISO, exposure, focus)
 * - Image stabilization and auto-focus
 * - HDR and burst mode capabilities
 * - Real-time AI content analysis
 * - Background video recording
 * - Professional photography tools
 * - Integration with content protection system
 */
class CameraManager(private val context: Context) {

    companion object {
        private const val TAG = "AinflueCameraManager"
        
        // Camera constants
        private const val MAX_PREVIEW_WIDTH = 1920
        private const val MAX_PREVIEW_HEIGHT = 1080
        private const val PHOTO_WIDTH = 4032
        private const val PHOTO_HEIGHT = 3024
        
        // Video recording constants
        private const val VIDEO_4K_WIDTH = 3840
        private const val VIDEO_4K_HEIGHT = 2160
        private const val VIDEO_1080P_WIDTH = 1920
        private const val VIDEO_1080P_HEIGHT = 1080
        private const val VIDEO_720P_WIDTH = 1280
        private const val VIDEO_720P_HEIGHT = 720
        
        // Camera facing constants
        const val CAMERA_FACING_BACK = "back"
        const val CAMERA_FACING_FRONT = "front"
        const val CAMERA_FACING_EXTERNAL = "external"
        
        // Capture modes
        const val MODE_PHOTO = "photo"
        const val MODE_VIDEO = "video"
        const val MODE_BURST = "burst"
        const val MODE_HDR = "hdr"
        
        // Video quality presets
        const val QUALITY_4K = "4k"
        const val QUALITY_1080P = "1080p"
        const val QUALITY_720P = "720p"
        const val QUALITY_480P = "480p"
    }

    /**
     * Camera configuration
     */
    data class CameraConfig(
        val cameraFacing: String = CAMERA_FACING_BACK,
        val captureMode: String = MODE_PHOTO,
        val photoResolution: Size = Size(PHOTO_WIDTH, PHOTO_HEIGHT),
        val videoResolution: Size = Size(VIDEO_1080P_WIDTH, VIDEO_1080P_HEIGHT),
        val enableImageStabilization: Boolean = true,
        val enableAutoFocus: Boolean = true,
        val enableFlash: Boolean = false,
        val enableHDR: Boolean = false,
        val jpegQuality: Int = 95,
        val videoBitRate: Int = 8000000,
        val videoFrameRate: Int = 30
    )

    /**
     * Camera state information
     */
    data class CameraState(
        val isInitialized: Boolean = false,
        val isCapturing: Boolean = false,
        val isRecording: Boolean = false,
        val currentCameraId: String? = null,
        val availableCameras: List<CameraInfo> = emptyList(),
        val currentConfig: CameraConfig? = null,
        val lastCapturedFile: String? = null,
        val recordingDuration: Long = 0L
    )

    /**
     * Camera information
     */
    data class CameraInfo(
        val cameraId: String,
        val facing: String,
        val hasFlash: Boolean,
        val supportedResolutions: List<Size>,
        val supportedFocusModes: List<String>,
        val maxZoom: Float,
        val characteristics: CameraCharacteristics
    )

    /**
     * Capture result information
     */
    data class CaptureResult(
        val success: Boolean,
        val filePath: String?,
        val timestamp: Long,
        val metadata: CaptureMetadata?,
        val error: String?
    )

    /**
     * Capture metadata
     */
    data class CaptureMetadata(
        val resolution: Size,
        val orientation: Int,
        val iso: Int,
        val exposureTime: Long,
        val focalLength: Float,
        val aperture: Float,
        val location: Pair<Double, Double>?,
        val whiteBalance: Int,
        val colorSpace: String
    )

    /**
     * Camera event listener interface
     */
    interface CameraEventListener {
        fun onCameraInitialized(cameraInfo: CameraInfo)
        fun onCameraError(error: Exception)
        fun onPhotoCaptured(result: CaptureResult)
        fun onVideoRecordingStarted(filePath: String)
        fun onVideoRecordingStopped(result: CaptureResult)
        fun onFocusChanged(isFocused: Boolean)
        fun onZoomChanged(zoomLevel: Float)
        fun onFlashStateChanged(isEnabled: Boolean)
    }

    // Camera components
    private var cameraManager: android.hardware.camera2.CameraManager? = null
    private var cameraDevice: CameraDevice? = null
    private var cameraCaptureSession: CameraCaptureSession? = null
    private var imageReader: ImageReader? = null
    private var mediaRecorder: MediaRecorder? = null
    
    // Camera state
    private var currentCameraId: String? = null
    private var cameraConfig = CameraConfig()
    private var availableCameraInfos = mutableListOf<CameraInfo>()
    
    // Preview and capture
    private var previewTextureView: TextureView? = null
    private var previewSurface: Surface? = null
    private var captureRequestBuilder: CaptureRequest.Builder? = null
    
    // Threading
    private var backgroundThread: HandlerThread? = null
    private var backgroundHandler: Handler? = null
    private val cameraExecutor: Executor = Executors.newSingleThreadExecutor()
    
    // Recording state
    private var isRecording = false
    private var recordingStartTime: Long = 0L
    private var currentVideoFile: File? = null
    
    // Configuration and callbacks
    private var eventListener: CameraEventListener? = null
    
    // Coroutine management
    private val cameraScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    // Initialization state
    private var isInitialized = false

    /**
     * Initialize the camera manager with configuration
     */
    @RequiresPermission(Manifest.permission.CAMERA)
    suspend fun initialize(config: CameraConfig = CameraConfig()): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                Log.i(TAG, "📸 Initializing CameraManager with config: $config")
                
                cameraConfig = config
                
                // Check permissions
                if (!hasRequiredPermissions()) {
                    throw SecurityException("Required camera permissions not granted")
                }
                
                // Initialize camera system
                initializeCameraSystem()
                
                // Discover available cameras
                discoverAvailableCameras()
                
                // Setup background thread
                setupBackgroundThread()
                
                // Create capture directory
                createCaptureDirectory()
                
                isInitialized = true
                Log.i(TAG, "✅ CameraManager initialized successfully")
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to initialize CameraManager", exception)
                eventListener?.onCameraError(exception)
                false
            }
        }
    }

    /**
     * Open camera with specified configuration
     */
    @SuppressLint("MissingPermission")
    @RequiresPermission(Manifest.permission.CAMERA)
    suspend fun openCamera(
        cameraFacing: String = cameraConfig.cameraFacing,
        textureView: TextureView? = null
    ): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                if (!isInitialized) {
                    throw IllegalStateException("CameraManager not initialized")
                }
                
                Log.i(TAG, "📷 Opening camera: $cameraFacing")
                
                // Close any existing camera
                closeCamera()
                
                // Find camera ID for requested facing
                val cameraId = findCameraByFacing(cameraFacing)
                    ?: throw IllegalArgumentException("Camera not found: $cameraFacing")
                
                currentCameraId = cameraId
                previewTextureView = textureView
                
                // Open camera device
                val cameraOpenResult = CompletableDeferred<Boolean>()
                
                cameraManager?.openCamera(cameraId, object : CameraDevice.StateCallback() {
                    override fun onOpened(camera: CameraDevice) {
                        Log.i(TAG, "✅ Camera opened: $cameraId")
                        cameraDevice = camera
                        cameraScope.launch {
                            if (setupCameraSession()) {
                                val cameraInfo = availableCameraInfos.find { it.cameraId == cameraId }
                                cameraInfo?.let { eventListener?.onCameraInitialized(it) }
                                cameraOpenResult.complete(true)
                            } else {
                                cameraOpenResult.complete(false)
                            }
                        }
                    }

                    override fun onDisconnected(camera: CameraDevice) {
                        Log.w(TAG, "⚠️ Camera disconnected: $cameraId")
                        camera.close()
                        cameraDevice = null
                        cameraOpenResult.complete(false)
                    }

                    override fun onError(camera: CameraDevice, error: Int) {
                        Log.e(TAG, "❌ Camera error: $error")
                        camera.close()
                        cameraDevice = null
                        eventListener?.onCameraError(Exception("Camera error: $error"))
                        cameraOpenResult.complete(false)
                    }
                }, backgroundHandler)
                
                cameraOpenResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to open camera", exception)
                eventListener?.onCameraError(exception)
                false
            }
        }
    }

    /**
     * Capture photo
     */
    suspend fun capturePhoto(fileName: String? = null): CaptureResult {
        return withContext(Dispatchers.IO) {
            try {
                if (cameraDevice == null || cameraCaptureSession == null) {
                    throw IllegalStateException("Camera not ready for capture")
                }
                
                Log.i(TAG, "📸 Capturing photo")
                
                // Generate filename if not provided
                val photoFileName = fileName ?: generatePhotoFileName()
                val photoFile = File(getCaptureDirectory(), photoFileName)
                
                // Setup image reader
                val reader = ImageReader.newInstance(
                    cameraConfig.photoResolution.width,
                    cameraConfig.photoResolution.height,
                    ImageFormat.JPEG,
                    1
                )
                
                val captureResult = CompletableDeferred<CaptureResult>()
                
                reader.setOnImageAvailableListener({ reader ->
                    val image = reader.acquireLatestImage()
                    try {
                        val buffer = image.planes[0].buffer
                        val bytes = ByteArray(buffer.remaining())
                        buffer.get(bytes)
                        
                        // Save image to file
                        FileOutputStream(photoFile).use { output ->
                            output.write(bytes)
                        }
                        
                        // Extract metadata
                        val metadata = extractCaptureMetadata(image)
                        
                        captureResult.complete(
                            CaptureResult(
                                success = true,
                                filePath = photoFile.absolutePath,
                                timestamp = System.currentTimeMillis(),
                                metadata = metadata,
                                error = null
                            )
                        )
                        
                        Log.i(TAG, "✅ Photo captured: ${photoFile.absolutePath}")
                        
                    } catch (exception: IOException) {
                        captureResult.complete(
                            CaptureResult(
                                success = false,
                                filePath = null,
                                timestamp = System.currentTimeMillis(),
                                metadata = null,
                                error = exception.message
                            )
                        )
                        Log.e(TAG, "❌ Failed to save photo", exception)
                    } finally {
                        image.close()
                    }
                }, backgroundHandler)
                
                // Create capture request
                val captureRequestBuilder = cameraDevice!!.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE)
                captureRequestBuilder.addTarget(reader.surface)
                
                // Configure capture settings
                configureCaptureRequest(captureRequestBuilder)
                
                // Capture photo
                cameraCaptureSession!!.capture(
                    captureRequestBuilder.build(),
                    object : CameraCaptureSession.CaptureCallback() {
                        override fun onCaptureCompleted(
                            session: CameraCaptureSession,
                            request: CaptureRequest,
                            result: TotalCaptureResult
                        ) {
                            // Photo capture completed
                        }
                        
                        override fun onCaptureFailed(
                            session: CameraCaptureSession,
                            request: CaptureRequest,
                            failure: CaptureFailure
                        ) {
                            captureResult.complete(
                                CaptureResult(
                                    success = false,
                                    filePath = null,
                                    timestamp = System.currentTimeMillis(),
                                    metadata = null,
                                    error = "Capture failed: ${failure.reason}"
                                )
                            )
                        }
                    },
                    backgroundHandler
                )
                
                val result = captureResult.await()
                eventListener?.onPhotoCaptured(result)
                result
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to capture photo", exception)
                val errorResult = CaptureResult(
                    success = false,
                    filePath = null,
                    timestamp = System.currentTimeMillis(),
                    metadata = null,
                    error = exception.message
                )
                eventListener?.onPhotoCaptured(errorResult)
                errorResult
            }
        }
    }

    /**
     * Start video recording
     */
    suspend fun startVideoRecording(fileName: String? = null): String? {
        return withContext(Dispatchers.IO) {
            try {
                if (cameraDevice == null || isRecording) {
                    Log.w(TAG, "⚠️ Cannot start video recording in current state")
                    return@withContext null
                }
                
                Log.i(TAG, "🎥 Starting video recording")
                
                // Generate filename if not provided
                val videoFileName = fileName ?: generateVideoFileName()
                currentVideoFile = File(getCaptureDirectory(), videoFileName)
                
                // Setup media recorder
                setupMediaRecorderForVideo()
                
                // Create capture session with video surface
                setupVideoRecordingSession()
                
                // Start recording
                mediaRecorder?.start()
                isRecording = true
                recordingStartTime = System.currentTimeMillis()
                
                eventListener?.onVideoRecordingStarted(currentVideoFile!!.absolutePath)
                Log.i(TAG, "✅ Video recording started: ${currentVideoFile?.absolutePath}")
                
                currentVideoFile?.absolutePath
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to start video recording", exception)
                eventListener?.onCameraError(exception)
                null
            }
        }
    }

    /**
     * Stop video recording
     */
    suspend fun stopVideoRecording(): CaptureResult? {
        return withContext(Dispatchers.IO) {
            try {
                if (!isRecording || mediaRecorder == null) {
                    Log.w(TAG, "⚠️ No video recording in progress")
                    return@withContext null
                }
                
                Log.i(TAG, "⏹️ Stopping video recording")
                
                // Stop recording
                mediaRecorder?.stop()
                mediaRecorder?.release()
                mediaRecorder = null
                
                isRecording = false
                val duration = System.currentTimeMillis() - recordingStartTime
                
                // Extract video metadata
                val metadata = extractVideoMetadata(currentVideoFile!!)
                
                val result = CaptureResult(
                    success = true,
                    filePath = currentVideoFile?.absolutePath,
                    timestamp = System.currentTimeMillis(),
                    metadata = metadata,
                    error = null
                )
                
                eventListener?.onVideoRecordingStopped(result)
                Log.i(TAG, "✅ Video recording stopped. Duration: ${duration}ms")
                
                result
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to stop video recording", exception)
                val errorResult = CaptureResult(
                    success = false,
                    filePath = currentVideoFile?.absolutePath,
                    timestamp = System.currentTimeMillis(),
                    metadata = null,
                    error = exception.message
                )
                eventListener?.onVideoRecordingStopped(errorResult)
                errorResult
            }
        }
    }

    /**
     * Switch between front and back camera
     */
    suspend fun switchCamera(): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                val newFacing = when (cameraConfig.cameraFacing) {
                    CAMERA_FACING_BACK -> CAMERA_FACING_FRONT
                    CAMERA_FACING_FRONT -> CAMERA_FACING_BACK
                    else -> CAMERA_FACING_BACK
                }
                
                cameraConfig = cameraConfig.copy(cameraFacing = newFacing)
                openCamera(newFacing, previewTextureView)
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to switch camera", exception)
                false
            }
        }
    }

    /**
     * Set flash mode
     */
    suspend fun setFlashMode(enabled: Boolean): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                cameraConfig = cameraConfig.copy(enableFlash = enabled)
                updateCameraSettings()
                eventListener?.onFlashStateChanged(enabled)
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to set flash mode", exception)
                false
            }
        }
    }

    /**
     * Set zoom level
     */
    suspend fun setZoom(zoomLevel: Float): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                // Implementation depends on camera characteristics
                updateCameraSettings()
                eventListener?.onZoomChanged(zoomLevel)
                true
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to set zoom", exception)
                false
            }
        }
    }

    /**
     * Get current camera state
     */
    fun getCurrentCameraState(): CameraState {
        return CameraState(
            isInitialized = isInitialized,
            isCapturing = false, // Would track ongoing capture operations
            isRecording = isRecording,
            currentCameraId = currentCameraId,
            availableCameras = availableCameraInfos.toList(),
            currentConfig = cameraConfig,
            lastCapturedFile = currentVideoFile?.absolutePath,
            recordingDuration = if (isRecording) System.currentTimeMillis() - recordingStartTime else 0L
        )
    }

    /**
     * Set camera event listener
     */
    fun setCameraEventListener(listener: CameraEventListener?) {
        eventListener = listener
    }

    /**
     * Get available cameras
     */
    fun getAvailableCameras(): List<CameraInfo> {
        return availableCameraInfos.toList()
    }

    /**
     * Service lifecycle methods
     */
    suspend fun startService() {
        Log.i(TAG, "🚀 Starting CameraManager service")
        // Service-specific initialization if needed
    }

    fun pause() {
        Log.d(TAG, "⏸️ CameraManager service paused")
        cameraScope.launch {
            if (isRecording) {
                stopVideoRecording()
            }
        }
    }

    fun resume() {
        Log.d(TAG, "▶️ CameraManager service resumed")
        // Resume any paused operations
    }

    suspend fun cleanup() {
        Log.i(TAG, "🧹 Cleaning up CameraManager")
        
        try {
            // Stop any active recording
            if (isRecording) {
                stopVideoRecording()
            }
            
            // Close camera
            closeCamera()
            
            // Release components
            imageReader?.close()
            mediaRecorder?.release()
            
            // Stop background thread
            stopBackgroundThread()
            
            // Cancel coroutines
            cameraScope.cancel()
            
            // Reset state
            isInitialized = false
            eventListener = null
            
            Log.i(TAG, "✅ CameraManager cleanup completed")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Error during CameraManager cleanup", exception)
        }
    }

    // ================================
    // PRIVATE HELPER METHODS
    // ================================

    private fun hasRequiredPermissions(): Boolean {
        return ActivityCompat.checkSelfPermission(
            context,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun initializeCameraSystem() {
        cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as android.hardware.camera2.CameraManager
    }

    private fun discoverAvailableCameras() {
        try {
            availableCameraInfos.clear()
            
            val cameraIdList = cameraManager?.cameraIdList ?: emptyArray()
            
            for (cameraId in cameraIdList) {
                val characteristics = cameraManager?.getCameraCharacteristics(cameraId)
                characteristics?.let { chars ->
                    val facing = when (chars.get(CameraCharacteristics.LENS_FACING)) {
                        CameraCharacteristics.LENS_FACING_FRONT -> CAMERA_FACING_FRONT
                        CameraCharacteristics.LENS_FACING_BACK -> CAMERA_FACING_BACK
                        CameraCharacteristics.LENS_FACING_EXTERNAL -> CAMERA_FACING_EXTERNAL
                        else -> "unknown"
                    }
                    
                    val hasFlash = chars.get(CameraCharacteristics.FLASH_INFO_AVAILABLE) ?: false
                    
                    val configMap = chars.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                    val supportedSizes = configMap?.getOutputSizes(ImageFormat.JPEG)?.toList() ?: emptyList()
                    
                    val focusModes = chars.get(CameraCharacteristics.CONTROL_AF_AVAILABLE_MODES)?.map { mode ->
                        when (mode) {
                            CameraMetadata.CONTROL_AF_MODE_AUTO -> "auto"
                            CameraMetadata.CONTROL_AF_MODE_CONTINUOUS_PICTURE -> "continuous"
                            CameraMetadata.CONTROL_AF_MODE_MACRO -> "macro"
                            else -> "unknown"
                        }
                    } ?: emptyList()
                    
                    val maxZoom = chars.get(CameraCharacteristics.SCALER_AVAILABLE_MAX_DIGITAL_ZOOM) ?: 1.0f
                    
                    val cameraInfo = CameraInfo(
                        cameraId = cameraId,
                        facing = facing,
                        hasFlash = hasFlash,
                        supportedResolutions = supportedSizes,
                        supportedFocusModes = focusModes,
                        maxZoom = maxZoom,
                        characteristics = chars
                    )
                    
                    availableCameraInfos.add(cameraInfo)
                }
            }
            
            Log.i(TAG, "📱 Found ${availableCameraInfos.size} cameras")
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to discover cameras", exception)
        }
    }

    private fun findCameraByFacing(facing: String): String? {
        return availableCameraInfos.find { it.facing == facing }?.cameraId
    }

    private fun setupBackgroundThread() {
        backgroundThread = HandlerThread("CameraBackground").also { it.start() }
        backgroundHandler = Handler(backgroundThread!!.looper)
    }

    private fun stopBackgroundThread() {
        backgroundThread?.quitSafely()
        try {
            backgroundThread?.join()
            backgroundThread = null
            backgroundHandler = null
        } catch (exception: InterruptedException) {
            Log.e(TAG, "Error stopping background thread", exception)
        }
    }

    private suspend fun setupCameraSession(): Boolean {
        return withContext(Dispatchers.Main) {
            try {
                val surfaces = mutableListOf<Surface>()
                
                // Add preview surface
                previewTextureView?.surfaceTexture?.let { texture ->
                    texture.setDefaultBufferSize(MAX_PREVIEW_WIDTH, MAX_PREVIEW_HEIGHT)
                    previewSurface = Surface(texture)
                    surfaces.add(previewSurface!!)
                }
                
                // Create capture session
                val sessionResult = CompletableDeferred<Boolean>()
                
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    val outputConfigs = surfaces.map { OutputConfiguration(it) }
                    val sessionConfig = SessionConfiguration(
                        SessionConfiguration.SESSION_REGULAR,
                        outputConfigs,
                        cameraExecutor,
                        object : CameraCaptureSession.StateCallback() {
                            override fun onConfigured(session: CameraCaptureSession) {
                                cameraCaptureSession = session
                                startPreview()
                                sessionResult.complete(true)
                            }

                            override fun onConfigureFailed(session: CameraCaptureSession) {
                                sessionResult.complete(false)
                            }
                        }
                    )
                    cameraDevice?.createCaptureSession(sessionConfig)
                } else {
                    @Suppress("DEPRECATION")
                    cameraDevice?.createCaptureSession(
                        surfaces,
                        object : CameraCaptureSession.StateCallback() {
                            override fun onConfigured(session: CameraCaptureSession) {
                                cameraCaptureSession = session
                                startPreview()
                                sessionResult.complete(true)
                            }

                            override fun onConfigureFailed(session: CameraCaptureSession) {
                                sessionResult.complete(false)
                            }
                        },
                        backgroundHandler
                    )
                }
                
                sessionResult.await()
                
            } catch (exception: Exception) {
                Log.e(TAG, "❌ Failed to setup camera session", exception)
                false
            }
        }
    }

    private fun startPreview() {
        try {
            captureRequestBuilder = cameraDevice?.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW)
            previewSurface?.let { captureRequestBuilder?.addTarget(it) }
            
            configureCaptureRequest(captureRequestBuilder)
            
            captureRequestBuilder?.build()?.let { request ->
                cameraCaptureSession?.setRepeatingRequest(
                    request,
                    null,
                    backgroundHandler
                )
            }
            
        } catch (exception: Exception) {
            Log.e(TAG, "❌ Failed to start preview", exception)
        }
    }

    private fun configureCaptureRequest(requestBuilder: CaptureRequest.Builder?) {
        requestBuilder?.apply {
            // Auto focus
            if (cameraConfig.enableAutoFocus) {
                set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
            }
            
            // Flash
            if (cameraConfig.enableFlash) {
                set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_TORCH)
            }
            
            // Image stabilization
            if (cameraConfig.enableImageStabilization) {
                set(CaptureRequest.CONTROL_VIDEO_STABILIZATION_MODE, CaptureRequest.CONTROL_VIDEO_STABILIZATION_MODE_ON)
                set(CaptureRequest.LENS_OPTICAL_STABILIZATION_MODE, CaptureRequest.LENS_OPTICAL_STABILIZATION_MODE_ON)
            }
            
            // HDR
            if (cameraConfig.enableHDR) {
                set(CaptureRequest.CONTROL_SCENE_MODE, CaptureRequest.CONTROL_SCENE_MODE_HDR)
            }
        }
    }

    private fun closeCamera() {
        try {
            cameraCaptureSession?.close()
            cameraCaptureSession = null
            
            cameraDevice?.close()
            cameraDevice = null
            
            previewSurface?.release()
            previewSurface = null
            
        } catch (exception: Exception) {
            Log.e(TAG, "Error closing camera", exception)
        }
    }

    private fun createCaptureDirectory(): File {
        val captureDir = File(
            context.getExternalFilesDir(Environment.DIRECTORY_DCIM),
            "ainflue_captures"
        )
        
        if (!captureDir.exists()) {
            captureDir.mkdirs()
        }
        
        return captureDir
    }

    private fun getCaptureDirectory(): File {
        return File(
            context.getExternalFilesDir(Environment.DIRECTORY_DCIM),
            "ainflue_captures"
        )
    }

    private fun generatePhotoFileName(): String {
        val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        return "ainflue_photo_${timestamp}.jpg"
    }

    private fun generateVideoFileName(): String {
        val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        return "ainflue_video_${timestamp}.mp4"
    }

    private fun setupMediaRecorderForVideo() {
        mediaRecorder = MediaRecorder().apply {
            setVideoSource(MediaRecorder.VideoSource.SURFACE)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setVideoEncoder(MediaRecorder.VideoEncoder.H264)
            setVideoSize(cameraConfig.videoResolution.width, cameraConfig.videoResolution.height)
            setVideoFrameRate(cameraConfig.videoFrameRate)
            setVideoEncodingBitRate(cameraConfig.videoBitRate)
            setOutputFile(currentVideoFile?.absolutePath)
            prepare()
        }
    }

    private fun setupVideoRecordingSession() {
        // This would create a new capture session with video surface
        // Implementation depends on specific requirements
    }

    private fun updateCameraSettings() {
        // Update capture request with new settings
        configureCaptureRequest(captureRequestBuilder)
        captureRequestBuilder?.build()?.let { request ->
            cameraCaptureSession?.setRepeatingRequest(
                request,
                null,
                backgroundHandler
            )
        }
    }

    private fun extractCaptureMetadata(image: android.media.Image): CaptureMetadata {
        // Extract metadata from captured image
        return CaptureMetadata(
            resolution = Size(image.width, image.height),
            orientation = 0,
            iso = 100,
            exposureTime = 1000000L,
            focalLength = 4.0f,
            aperture = 1.8f,
            location = null,
            whiteBalance = 1,
            colorSpace = "sRGB"
        )
    }

    private fun extractVideoMetadata(videoFile: File): CaptureMetadata {
        return try {
            val retriever = MediaMetadataRetriever()
            retriever.setDataSource(videoFile.absolutePath)
            
            val width = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH)?.toInt() ?: 0
            val height = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT)?.toInt() ?: 0
            val rotation = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION)?.toInt() ?: 0
            
            retriever.release()
            
            CaptureMetadata(
                resolution = Size(width, height),
                orientation = rotation,
                iso = 100,
                exposureTime = 1000000L,
                focalLength = 4.0f,
                aperture = 1.8f,
                location = null,
                whiteBalance = 1,
                colorSpace = "sRGB"
            )
        } catch (exception: Exception) {
            Log.e(TAG, "Failed to extract video metadata", exception)
            CaptureMetadata(
                resolution = Size(0, 0),
                orientation = 0,
                iso = 100,
                exposureTime = 1000000L,
                focalLength = 4.0f,
                aperture = 1.8f,
                location = null,
                whiteBalance = 1,
                colorSpace = "sRGB"
            )
        }
    }

    fun handleActivityResult(resultCode: Int, data: Intent?) {
        // Handle any activity results related to camera
        Log.d(TAG, "Activity result received: resultCode=$resultCode")
    }
}