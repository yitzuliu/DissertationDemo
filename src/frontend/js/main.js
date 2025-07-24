/**
 * AI Manual Assistant - Main Application
 * Coordinates all modules and handles the main application logic
 */

// Import modules
import { CameraManager } from './modules/camera.js';
import { UIController } from './modules/ui.js';
import { APIClient } from './modules/api.js';
import { ConfigManager } from './modules/config.js';

// Main application class
class VisionIntelligenceApp {
    constructor() {
        this.cameraManager = new CameraManager();
        this.uiController = new UIController();
        this.apiClient = new APIClient();
        this.configManager = new ConfigManager();
        
        this.isProcessing = false;
        this.intervalId = null;
    }

    async initialize() {
        try {
            // Initialize all modules
            await Promise.all([
                this.configManager.loadConfig(),
                this.apiClient.checkStatus(),
                this.cameraManager.initialize()
            ]);

            // Setup UI
            this.uiController.setupTabs();
            this.setupEventListeners();

            console.log('✅ Application initialized successfully');
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.uiController.showError('Application initialization failed. Please refresh and try again.');
        }
    }

    setupEventListeners() {
        // Start/stop button
        document.getElementById('startButton').addEventListener('click', () => {
            this.toggleProcessing();
        });

        // Keyboard shortcuts
        document.getElementById('instructionText').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.toggleProcessing();
            }
        });

        // Camera selection
        document.getElementById('cameraSelect').addEventListener('change', (e) => {
            this.cameraManager.switchCamera(e.target.value);
        });
    }

    toggleProcessing() {
        if (this.isProcessing) {
            this.stopProcessing();
        } else {
            this.startProcessing();
        }
    }

    async startProcessing() {
        try {
            const instruction = document.getElementById('instructionText').value.trim();
            if (!instruction) {
                this.uiController.showError('Please enter an instruction before starting.');
                return;
            }

            this.isProcessing = true;
            this.uiController.updateProcessingState(true);

            // Send first request immediately
            await this.processFrame();

            // Setup interval for continuous processing
            const interval = this.getProcessingInterval();
            this.intervalId = setInterval(() => this.processFrame(), interval);

        } catch (error) {
            console.error('Error starting processing:', error);
            this.uiController.showError(error.message);
            this.stopProcessing();
        }
    }

    stopProcessing() {
        this.isProcessing = false;
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        this.uiController.updateProcessingState(false);
    }

    async processFrame() {
        if (!this.isProcessing) return;

        try {
            // Capture image
            const imageData = this.cameraManager.captureFrame();
            if (!imageData) {
                throw new Error('Failed to capture image');
            }

            // Get instruction
            const instruction = document.getElementById('instructionText').value.trim();

            // Send to API
            const response = await this.apiClient.sendChatCompletion(instruction, imageData);
            
            // Update UI
            this.uiController.updateResponse(response);
            this.uiController.updateImagePreview(imageData);

        } catch (error) {
            console.error('Error processing frame:', error);
            this.uiController.showError(error.message);
        }
    }

    getProcessingInterval() {
        const intervalSelect = document.getElementById('intervalSelect');
        const interval = parseInt(intervalSelect.value) || 5000;
        return Math.max(interval, 1000); // Minimum 1 second
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    const app = new VisionIntelligenceApp();
    await app.initialize();
});

// Export for debugging purposes
window.visionApp = app;

export default app;