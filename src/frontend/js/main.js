/**
 * AI Manual Assistant - Main Application
 * Coordinates all modules and handles the main application logic
 */

import { configManager } from './utils/config.js';
import { showError, hideError, getOptimalInterval, addEventListenerSafe } from './utils/helpers.js';
import { apiClient } from './components/api.js';
import { cameraManager } from './components/camera.js';
import { uiManager } from './components/ui.js';
import { tabManager } from './components/tabs.js';

class VisionApp {
    constructor() {
        this.isProcessing = false;
        this.intervalId = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the application
     */
    async initialize() {
        try {
            console.log('🚀 Initializing Vision Intelligence Hub...');

            // Initialize UI manager first
            uiManager.initialize();
            
            // Initialize tab manager
            tabManager.initialize();

            // Initialize camera manager
            await cameraManager.initialize();

            // Load configuration and check API status
            await Promise.all([
                this.loadConfiguration(),
                this.checkApiStatus()
            ]);

            // Set up main event listeners
            this.setupEventListeners();

            // Initialize capture label
            this.initializeCaptureLabel();

            this.isInitialized = true;
            console.log('✅ Application initialized successfully');

        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            showError("Application initialization failed. Please refresh and try again.");
        }
    }

    /**
     * Load configuration from backend
     */
    async loadConfiguration() {
        try {
            const config = await configManager.loadConfig();
            uiManager.updateConfigUI(config);
            console.log('✅ Configuration loaded');
        } catch (error) {
            console.error('Failed to load configuration:', error);
            showError("Failed to load configuration. Please refresh the page.");
        }
    }

    /**
     * Check API status and update UI
     */
    async checkApiStatus() {
        uiManager.setStatusLoading();
        
        try {
            const status = await apiClient.checkStatus();
            uiManager.updateApiStatus(status.online, status.data, status.error);
            
            if (status.online) {
                console.log('✅ API connection established');
            } else {
                console.warn('⚠️ API connection failed:', status.error);
            }
        } catch (error) {
            console.error('Error checking API status:', error);
            uiManager.updateApiStatus(false, null, error);
        } finally {
            uiManager.removeStatusLoading();
        }
    }

    /**
     * Set up main event listeners
     */
    setupEventListeners() {
        const startButton = uiManager.getElement('startButton');
        if (startButton) {
            addEventListenerSafe(startButton, 'click', () => {
                this.toggleProcessing();
            });
        }

        // Listen for tab changes
        document.addEventListener('tabchange', (event) => {
            console.log('Tab changed to:', event.detail.activeTab);
        });

        // Listen for window beforeunload to cleanup
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    /**
     * Initialize capture label with helpful information
     */
    initializeCaptureLabel() {
        uiManager.updateCaptureLabel(
            `<span style="color: var(--text);">Click Start to begin<br>This will show captured images</span>`,
            'info'
        );
    }

    /**
     * Toggle between processing and stopped states
     */
    toggleProcessing() {
        if (this.isProcessing) {
            this.stopProcessing();
        } else {
            this.startProcessing();
        }
    }

    /**
     * Start processing
     */
    async startProcessing() {
        // Validate form inputs
        const validation = uiManager.validateForm();
        if (!validation.valid) {
            showError(validation.errors[0]);
            return;
        }

        // Check camera readiness
        if (!cameraManager.isReady()) {
            showError("Camera not available. Please check permissions.");
            return;
        }

        // Set processing state
        this.isProcessing = true;
        uiManager.updateProcessingState(true);
        hideError();

        console.log('🎬 Starting processing...');

        // Get form values
        const { interval, quality, maxTokens } = validation.values;

        // Calculate optimal interval with model-specific adjustments
        const activeModel = configManager.getActiveModel();
        const optimalInterval = getOptimalInterval(activeModel, interval);

        // Show processing start message
        uiManager.updateCaptureLabel(
            `Processing starts<br>Capture every ${optimalInterval/1000}s`,
            'info'
        );

        // Send first request immediately
        await this.processFrame(quality, maxTokens);

        // Start interval for continuous processing
        this.intervalId = setInterval(() => {
            this.processFrame(quality, maxTokens);
        }, optimalInterval);

        console.log(`🔄 Processing started with ${optimalInterval}ms interval`);
    }

    /**
     * Stop processing
     */
    stopProcessing() {
        console.log('⏹️ Stopping processing...');

        // Clear processing state
        this.isProcessing = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        // Update UI
        uiManager.updateProcessingState(false);
        uiManager.showProcessingIndicator(false);

        // Reset capture label
        uiManager.updateCaptureLabel(
            `<span style="color: var(--text);">Click Start to begin<br>This will show captured images</span>`,
            'info'
        );

        console.log('✅ Processing stopped');
    }

    /**
     * Process a single frame
     * @param {number} quality - Image quality
     * @param {number} maxTokens - Maximum tokens for response
     */
    async processFrame(quality, maxTokens) {
        if (!this.isProcessing) return;

        // Skip if API is already processing a request
        if (apiClient.isProcessing()) {
            console.log("⏳ Previous request still processing, skipping frame");
            return;
        }

        try {
            // Get instruction text
            const { instruction } = uiManager.getFormValues();
            if (!instruction) {
                showError("Please enter an instruction before starting.");
                this.stopProcessing();
                return;
            }

            // Capture image
            const imageBase64URL = cameraManager.captureImage(quality);
            if (!imageBase64URL) {
                showError("Unable to capture image. Please check camera status.");
                return;
            }

            // Update capture indicator (flash effect)
            cameraManager.updateCaptureIndicator();

            // Update UI to show processing
            uiManager.updateCaptureLabel(
                `Processing...<br><span style="font-size: 0.65rem;">Please wait</span>`,
                'processing'
            );
            uiManager.showProcessingIndicator(true);

            // Send request to API
            const response = await apiClient.sendChatCompletion(
                instruction, 
                imageBase64URL, 
                maxTokens
            );

            // Update UI with response
            uiManager.updateResponseText(response);
            uiManager.showProcessingIndicator(false);

            // Show success message with next capture info
            uiManager.updateCaptureLabel(
                `Response received<br><span style="font-size: 0.65rem;">${new Date().toLocaleTimeString()}</span>`,
                'success'
            );

            // After 2 seconds, show next capture countdown
            setTimeout(() => {
                const { interval } = uiManager.getFormValues();
                const activeModel = configManager.getActiveModel();
                const nextInterval = getOptimalInterval(activeModel, interval);
                uiManager.updateCaptureLabel(
                    `Next capture in ${nextInterval/1000}s`,
                    'info'
                );
            }, 2000);

            console.log('✅ Frame processed successfully');

        } catch (error) {
            console.error('❌ Error processing frame:', error);
            uiManager.showProcessingIndicator(false);
            
            // Show error but don't stop processing for temporary errors
            if (error.message.includes('Previous request still processing')) {
                // This is expected, just log it
                console.log('⏳ Skipping frame due to ongoing processing');
            } else {
                showError(`Processing error: ${error.message}`);
                
                // Stop processing for serious errors
                if (error.message.includes('Server error') || 
                    error.message.includes('Failed to fetch')) {
                    this.stopProcessing();
                }
            }
        }
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        console.log('🧹 Cleaning up application...');
        
        this.stopProcessing();
        cameraManager.stop();
    }

    /**
     * Check if application is ready
     * @returns {boolean} True if initialized
     */
    isReady() {
        return this.isInitialized;
    }

    /**
     * Get application status
     * @returns {Object} Status information
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            processing: this.isProcessing,
            cameraReady: cameraManager.isReady(),
            apiReady: !apiClient.isProcessing(),
            configLoaded: configManager.isLoaded()
        };
    }

    /**
     * Restart the application
     */
    async restart() {
        console.log('🔄 Restarting application...');
        
        this.cleanup();
        await this.initialize();
    }
}

// Create and initialize the application
const app = new VisionApp();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        app.initialize();
    });
} else {
    // DOM is already ready
    app.initialize();
}

// Export for debugging purposes
window.visionApp = app;

export default app;