/**
 * Camera Manager Module
 * 
 * Handles camera initialization, device selection, and image capture
 */

export class CameraManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.cameraSelect = null;
        this.isInitialized = false;
    }

    /**
     * Initialize camera manager with DOM elements
     */
    initialize(videoElement, canvasElement, cameraSelectElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.cameraSelect = cameraSelectElement;
        
        if (!this.video || !this.canvas || !this.cameraSelect) {
            throw new Error('Required DOM elements not found');
        }

        this.isInitialized = true;
        return this.populateCameraList();
    }

    /**
     * Populate camera selection dropdown
     */
    async populateCameraList() {
        try {
            await navigator.mediaDevices.getUserMedia({ video: true, audio: false });

            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');

            if (videoDevices.length === 0) {
                throw new Error("No cameras found");
            }

            this.cameraSelect.innerHTML = videoDevices.map(device => {
                const isIPhone = device.label.toLowerCase().includes('continuity') ||
                    device.label.toLowerCase().includes('iphone');
                const isMacBook = device.label.toLowerCase().includes('facetime') ||
                    device.label.toLowerCase().includes('built-in');
                const isExternal = device.label.toLowerCase().includes('usb') ||
                    device.label.toLowerCase().includes('capture');

                let icon = '📷 ';
                if (isIPhone) icon = '📱 ';
                else if (isMacBook) icon = '💻 ';
                else if (isExternal) icon = '🎥 ';

                const label = device.label || `Camera ${videoDevices.indexOf(device) + 1}`;
                return `<option value="${device.deviceId}">${icon}${label}</option>`;
            }).join('');

            // Auto-select MacBook camera if available
            const macBookCamera = videoDevices.find(d =>
                d.label.toLowerCase().includes('facetime') ||
                d.label.toLowerCase().includes('built-in')
            );

            const selectedCamera = macBookCamera || videoDevices[0];
            this.cameraSelect.value = selectedCamera.deviceId;
            await this.startCamera(selectedCamera.deviceId);

            return videoDevices;

        } catch (err) {
            console.error("Error accessing cameras:", err);
            throw err;
        }
    }

    /**
     * Start camera with specific device
     */
    async startCamera(deviceId) {
        try {
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }

            const constraints = {
                video: {
                    deviceId: deviceId ? { exact: deviceId } : undefined,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                    facingMode: deviceId ? undefined : "user"
                },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;

            // Wait for video metadata to load
            await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Video metadata loading timeout'));
                }, 10000); // 10 second timeout

                this.video.onloadedmetadata = () => {
                    clearTimeout(timeout);
                    this.video.classList.add('animate-fade-in');
                    console.log(`Camera started: ${this.video.videoWidth}x${this.video.videoHeight}`);
                    resolve();
                };

                this.video.onerror = (error) => {
                    clearTimeout(timeout);
                    reject(error);
                };
            });

        } catch (err) {
            console.error("Error starting camera:", err);
            throw err;
        }
    }

    /**
     * Capture image from video stream
     */
    captureImage(quality = 0.9) {
        console.log("🎥 Starting image capture...");

        // Check if camera stream exists
        if (!this.stream) {
            console.error("❌ No camera stream available");
            return null;
        }
        console.log("✅ Camera stream exists");

        // Check if video element is ready
        if (!this.video || this.video.readyState < 2) {
            console.error("❌ Video not ready, readyState:", this.video ? this.video.readyState : 'video element not found');
            return null;
        }
        console.log("✅ Video element ready, readyState:", this.video.readyState);

        // Wait for video dimensions to be available
        if (!this.video.videoWidth || !this.video.videoHeight) {
            console.error("❌ Video dimensions not available:", this.video.videoWidth, 'x', this.video.videoHeight);
            return null;
        }
        console.log("✅ Video dimensions:", this.video.videoWidth, 'x', this.video.videoHeight);

        try {
            console.log("🔄 Starting capture process...");

            // Generate observation ID and request ID
            const observationId = `obs_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;
            const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;
            console.log("✅ Generated IDs:", { observationId, requestId });

            const targetWidth = 1024;
            const aspectRatio = this.video.videoHeight / this.video.videoWidth;
            const targetHeight = Math.round(targetWidth * aspectRatio);
            console.log("✅ Target dimensions:", targetWidth, 'x', targetHeight);

            // Check canvas element
            if (!this.canvas) {
                console.error("❌ Canvas element not found");
                return null;
            }

            this.canvas.width = targetWidth;
            this.canvas.height = targetHeight;
            console.log("✅ Canvas dimensions set");

            const ctx = this.canvas.getContext('2d');
            if (!ctx) {
                console.error("❌ Failed to get canvas 2D context");
                return null;
            }
            console.log("✅ Canvas context obtained");

            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';

            // Try to draw video frame to canvas
            try {
                ctx.drawImage(this.video, 0, 0, targetWidth, targetHeight);
                console.log("✅ Video frame drawn to canvas");
            } catch (drawError) {
                console.error("❌ Failed to draw video to canvas:", drawError);
                return null;
            }

            const imageQuality = Math.max(0.92, parseFloat(quality) || 0.9);
            console.log("✅ Image quality set to:", imageQuality);

            // Try to convert to data URL
            let imageDataURL;
            try {
                imageDataURL = this.canvas.toDataURL('image/jpeg', imageQuality);
                console.log("✅ Canvas converted to data URL, length:", imageDataURL.length);
            } catch (dataUrlError) {
                console.error("❌ Failed to convert canvas to data URL:", dataUrlError);
                return null;
            }

            // Validate generated image data
            if (!imageDataURL || imageDataURL.length < 100) {
                console.error("❌ Generated image data is invalid or too small, length:", imageDataURL ? imageDataURL.length : 0);
                return null;
            }

            // Check if it's a valid JPEG data URL
            if (!imageDataURL.startsWith('data:image/jpeg;base64,')) {
                console.error("❌ Generated data URL has invalid format:", imageDataURL.substring(0, 50));
                return null;
            }
            console.log("✅ Image data validation passed");

            // Get device information
            const selectedOption = this.cameraSelect.options[this.cameraSelect.selectedIndex];
            const deviceInfo = {
                device: selectedOption ? selectedOption.text : 'Unknown Camera'
            };

            // Calculate image size
            const imageSizeBytes = Math.round((imageDataURL.length - 'data:image/jpeg;base64,'.length) * 3 / 4);

            // Create an object containing image data and ID
            const imageResult = {
                dataURL: imageDataURL,
                observationId: observationId,
                requestId: requestId,
                width: targetWidth,
                height: targetHeight,
                size: imageSizeBytes
            };

            console.log(`🎉 Image captured successfully: ${targetWidth}x${targetHeight}, ${(imageSizeBytes / 1024).toFixed(1)}KB`);
            return imageResult;

        } catch (err) {
            console.error("❌ Error in capture process:", err);
            console.error("❌ Error stack:", err.stack);
            return null;
        }
    }

    /**
     * Check if camera is ready
     */
    isReady() {
        return this.isInitialized && 
               this.stream && 
               this.video && 
               this.video.readyState >= 2 && 
               this.video.videoWidth > 0 && 
               this.video.videoHeight > 0;
    }

    /**
     * Get current camera status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            hasStream: !!this.stream,
            videoReady: this.video ? this.video.readyState >= 2 : false,
            dimensions: this.video ? `${this.video.videoWidth}x${this.video.videoHeight}` : 'N/A',
            isReady: this.isReady()
        };
    }

    /**
     * Cleanup camera resources
     */
    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.isInitialized = false;
    }
} 