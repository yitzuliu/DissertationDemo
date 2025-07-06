class CameraManager {
    constructor() {
        this.videoElement = null;
        this.stream = null;
        this.availableCameras = [];
        this.currentDeviceId = null;
    }

    async initialize(videoElementId) {
        this.videoElement = document.getElementById(videoElementId);
        await this.loadAvailableCameras();
        await this.startCamera();
        
        // Watch for device changes (like iPhone connecting/disconnecting)
        navigator.mediaDevices.addEventListener('devicechange', async () => {
            await this.loadAvailableCameras();
            this.updateCameraList();
        });
    }

    async loadAvailableCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            this.availableCameras = devices.filter(device => device.kind === 'videoinput');
            
            // Log available cameras for debugging
            console.log('Available cameras:', this.availableCameras.map(cam => ({
                label: cam.label,
                id: cam.deviceId
            })));
            
            return this.availableCameras;
        } catch (error) {
            console.error('Error loading cameras:', error);
            return [];
        }
    }

    async startCamera(deviceId = null) {
        try {
            if (this.stream) {
                this.stopCamera();
            }

            const constraints = {
                video: deviceId ? { deviceId: { exact: deviceId } } : true,
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.videoElement.srcObject = this.stream;
            await this.videoElement.play();
            
            // Store current device ID
            const videoTrack = this.stream.getVideoTracks()[0];
            this.currentDeviceId = videoTrack.getSettings().deviceId;
            
            // Update camera selection if it exists
            const selector = document.getElementById('camera-select');
            if (selector) {
                selector.value = this.currentDeviceId;
            }
        } catch (error) {
            console.error('Error starting camera:', error);
            throw error;
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.videoElement) {
            this.videoElement.srcObject = null;
        }
    }

    updateCameraList() {
        const selector = document.getElementById('camera-select');
        if (!selector) return;

        // Clear existing options
        selector.innerHTML = '';

        // Add options for each camera
        this.availableCameras.forEach(camera => {
            const option = document.createElement('option');
            option.value = camera.deviceId;
            option.text = camera.label || `Camera ${this.availableCameras.indexOf(camera) + 1}`;
            
            // Check if this is an iPhone camera
            if (camera.label.includes('iPhone') || camera.label.includes('iOS')) {
                option.text = '📱 ' + option.text;
            }
            
            selector.appendChild(option);
        });

        // Select current camera
        if (this.currentDeviceId) {
            selector.value = this.currentDeviceId;
        }
    }

    async switchToCamera(deviceId) {
        await this.startCamera(deviceId);
    }

    async captureImage() {
        if (!this.videoElement) return null;

        const canvas = document.createElement('canvas');
        canvas.width = this.videoElement.videoWidth;
        canvas.height = this.videoElement.videoHeight;
        
        const context = canvas.getContext('2d');
        context.drawImage(this.videoElement, 0, 0);
        
        return canvas.toDataURL('image/jpeg', 0.9);
    }

    isInitialized() {
        return !!this.stream;
    }

    hasIPhoneCamera() {
        return this.availableCameras.some(camera => 
            camera.label.includes('iPhone') || camera.label.includes('iOS')
        );
    }
}

// Add module exports for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CameraManager;
} else if (typeof window !== 'undefined') {
    window.CameraManager = CameraManager;
} 