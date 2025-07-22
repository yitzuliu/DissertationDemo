/**
 * Camera Management Module
 * Handles camera access, device selection, and image capture
 */

import { showError, hideError, addEventListenerSafe, formatTime } from '../utils/helpers.js';

class CameraManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.imagePreview = null;
        this.cameraSelect = null;
        this.captureLabel = null;
        this.isInitialized = false;
    }

    /**
     * Initialize camera manager with DOM elements
     */
    async initialize() {
        // Get DOM elements
        this.video = document.getElementById('videoFeed');
        this.canvas = document.getElementById('canvas');
        this.imagePreview = document.getElementById('imagePreview');
        this.cameraSelect = document.getElementById('cameraSelect');
        this.captureLabel = document.querySelector('.capture-label');

        if (!this.video || !this.canvas) {
            throw new Error('Required camera elements not found');
        }

        // Set up event listeners
        this.setupEventListeners();

        // Populate camera list and start default camera
        await this.populateCameraList();

        this.isInitialized = true;
    }

    /**
     * Set up event listeners for camera controls
     */
    setupEventListeners() {
        if (this.cameraSelect) {
            addEventListenerSafe(this.cameraSelect, 'change', async () => {
                const selectedDeviceId = this.cameraSelect.value;
                await this.startCamera(selectedDeviceId);
            });
        }

        // Watch for device changes (like iPhone connecting/disconnecting)
        if (navigator.mediaDevices && navigator.mediaDevices.addEventListener) {
            navigator.mediaDevices.addEventListener('devicechange', async () => {
                await this.populateCameraList();
            });
        }

        // Add video loaded event
        if (this.video) {
            addEventListenerSafe(this.video, 'loadedmetadata', () => {
                this.video.classList.add('animate-fade-in');
            });
        }
    }

    /**
     * Populate the camera selection dropdown
     */
    async populateCameraList() {
        if (!this.cameraSelect) return;

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');

            // Map devices to options with icons
            this.cameraSelect.innerHTML = videoDevices.map(device => {
                const isIPhone = device.label.toLowerCase().includes('continuity') || 
                               device.label.toLowerCase().includes('iphone');
                const isMacBook = device.label.toLowerCase().includes('facetime') ||
                                device.label.toLowerCase().includes('built-in');
                const icon = isIPhone ? '📱 ' : isMacBook ? '💻 ' : '📷 ';
                return `<option value="${device.deviceId}">${icon}${device.label || `Camera ${device.deviceId}`}</option>`;
            }).join('');

            if (videoDevices.length > 0) {
                // Try to find MacBook's built-in camera first
                const macBookCamera = videoDevices.find(d => 
                    d.label.toLowerCase().includes('facetime') || 
                    d.label.toLowerCase().includes('built-in')
                );

                if (macBookCamera) {
                    // Set MacBook camera as default
                    this.cameraSelect.value = macBookCamera.deviceId;
                    await this.startCamera(macBookCamera.deviceId);
                } else {
                    // Fallback to first available camera
                    this.cameraSelect.value = videoDevices[0].deviceId;
                    await this.startCamera(videoDevices[0].deviceId);
                }
            }
        } catch (err) {
            console.error("Error listing cameras:", err);
            showError("Failed to list cameras.");
        }
    }

    /**
     * Start camera with specified device ID
     * @param {string} deviceId - Camera device ID
     */
    async startCamera(deviceId) {
        try {
            // Stop existing stream
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }

            const constraints = {
                video: deviceId ? 
                    {
                        deviceId: { exact: deviceId },
                        width: { ideal: 1920 },
                        height: { ideal: 1080 }
                    } : 
                    {
                        facingMode: "user",  // Default to front camera if no deviceId
                        width: { ideal: 1920 },
                        height: { ideal: 1080 }
                    },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            hideError();

            // Update camera selection to match current camera
            const tracks = this.stream.getVideoTracks();
            if (tracks.length > 0) {
                const currentCamera = tracks[0].getSettings().deviceId;
                if (currentCamera && this.cameraSelect && this.cameraSelect.value !== currentCamera) {
                    this.cameraSelect.value = currentCamera;
                }
            }
        } catch (err) {
            this.handleCameraError(err);
        }
    }

    /**
     * Handle camera errors
     * @param {Error} error - Camera error
     */
    handleCameraError(error) {
        console.error("Camera error:", error);
        
        let errorMessage = "Camera access failed. ";
        
        if (error.name === 'NotAllowedError') {
            errorMessage += "Please allow camera permissions and refresh the page.";
        } else if (error.name === 'NotFoundError') {
            errorMessage += "No camera found. Please connect a camera and refresh.";
        } else if (error.name === 'NotReadableError') {
            errorMessage += "Camera is being used by another application.";
        } else {
            errorMessage += `Error: ${error.message}`;
        }
        
        showError(errorMessage);
    }

    /**
     * Capture image from video stream
     * @param {number} quality - JPEG quality (0.0 to 1.0)
     * @returns {string|null} Base64 encoded image data URL
     */
    captureImage(quality = 0.9) {
        if (!this.stream || !this.video.videoWidth || !this.isInitialized) {
            console.warn("Camera not ready for capture");
            return null;
        }
        
        try {
            // Set higher canvas resolution
            const targetWidth = 1024;  // Optimized target width
            const aspectRatio = this.video.videoHeight / this.video.videoWidth;
            const targetHeight = Math.round(targetWidth * aspectRatio);
            
            this.canvas.width = targetWidth;
            this.canvas.height = targetHeight;
            
            const ctx = this.canvas.getContext('2d');
            
            // Enable high-quality image smoothing
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            
            // Draw video frame to canvas
            ctx.drawImage(this.video, 0, 0, targetWidth, targetHeight);
            
            // Apply basic image enhancement
            const imageData = ctx.getImageData(0, 0, targetWidth, targetHeight);
            const enhancedData = this.enhanceImageData(imageData);
            ctx.putImageData(enhancedData, 0, 0);
            
            // Use specified JPEG quality
            const validQuality = Math.max(0.7, Math.min(1.0, quality));
            const dataUrl = this.canvas.toDataURL('image/jpeg', validQuality);
            
            // Update preview
            this.updateImagePreview(dataUrl);
            
            return dataUrl;
        } catch (err) {
            console.error("Error capturing image:", err);
            showError("Failed to capture image with high quality");
            return null;
        }
    }

    /**
     * Enhance image data with basic adjustments
     * @param {ImageData} imageData - Canvas image data
     * @returns {ImageData} Enhanced image data
     */
    enhanceImageData(imageData) {
        const data = imageData.data;
        const contrast = 1.1;  // Slightly increase contrast
        const brightness = 1.05;  // Slightly increase brightness
        
        for (let i = 0; i < data.length; i += 4) {
            // Apply contrast
            for (let j = 0; j < 3; j++) {
                data[i + j] = ((data[i + j] / 255 - 0.5) * contrast + 0.5) * 255;
            }
            
            // Apply brightness
            for (let j = 0; j < 3; j++) {
                data[i + j] *= brightness;
            }
            
            // Ensure values are within valid range
            for (let j = 0; j < 3; j++) {
                data[i + j] = Math.max(0, Math.min(255, data[i + j]));
            }
        }
        
        return imageData;
    }

    /**
     * Update image preview with captured image
     * @param {string} dataUrl - Base64 image data URL
     */
    updateImagePreview(dataUrl) {
        if (!dataUrl || !this.imagePreview) return;
        
        // Show the preview with animation
        this.imagePreview.src = dataUrl;
        this.imagePreview.style.display = "inline-block";
        
        // Update capture label with timestamp
        if (this.captureLabel) {
            this.captureLabel.innerHTML = `Frame sent to AI<br><span style="font-size: 0.65rem;">${formatTime()}</span>`;
            this.captureLabel.style.backgroundColor = "var(--success-light)";
            this.captureLabel.style.color = "var(--success)";
            
            // Return to normal after 2 seconds
            setTimeout(() => {
                this.captureLabel.style.backgroundColor = "";
                this.captureLabel.style.color = "";
            }, 2000);
        }
        
        // Reset animation to trigger it again
        this.imagePreview.classList.remove('animate-fade-in');
        void this.imagePreview.offsetWidth; // Trigger reflow
        this.imagePreview.classList.add('animate-fade-in');
    }

    /**
     * Update capture indicator
     */
    updateCaptureIndicator() {
        if (this.captureLabel) {
            this.captureLabel.textContent = `Captured (${formatTime()})`;
            this.captureLabel.style.backgroundColor = "var(--primary-light)";
            this.captureLabel.style.color = "var(--primary-dark)";
            
            // Reset after a short delay
            setTimeout(() => {
                this.captureLabel.style.backgroundColor = "";
                this.captureLabel.style.color = "";
            }, 500);
        }
    }

    /**
     * Check if camera is ready
     * @returns {boolean} True if camera is ready
     */
    isReady() {
        return this.stream && this.video && this.video.videoWidth > 0 && this.isInitialized;
    }

    /**
     * Stop camera stream
     */
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }

    /**
     * Get current camera info
     * @returns {Object} Camera information
     */
    getCameraInfo() {
        if (!this.stream) return null;
        
        const tracks = this.stream.getVideoTracks();
        if (tracks.length === 0) return null;
        
        const track = tracks[0];
        const settings = track.getSettings();
        
        return {
            deviceId: settings.deviceId,
            label: track.label,
            width: settings.width,
            height: settings.height,
            frameRate: settings.frameRate
        };
    }
}

// Export singleton instance
export const cameraManager = new CameraManager();