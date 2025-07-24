/**
 * AI Manual Assistant - Main Application
 * Coordinates all modules and handles the main application logic
 */

// Import modules
import { cameraManager } from './components/camera.js';
import { uiManager } from './components/ui.js';
import { apiClient } from './components/api.js';
import { configManager } from './utils/config.js';
import { tabManager } from './components/tabs.js';

// Main application class
class VisionIntelligenceApp {
    constructor() {
        this.cameraManager = cameraManager;
        this.uiManager = uiManager;
        this.apiClient = apiClient;
        this.configManager = configManager;
        this.tabManager = tabManager;
        
        this.isProcessing = false;
        this.intervalId = null;
    }

    async initialize() {
        try {
            // Initialize UI components first
            this.uiManager.initialize();
            this.tabManager.initialize();
            
            // Initialize other modules
            await Promise.all([
                this.configManager.loadConfig(),
                this.apiClient.checkStatus(),
                this.cameraManager.initialize()
            ]);

            // Setup event listeners
            this.setupEventListeners();
            
            // Update UI with loaded configuration
            const config = this.configManager.get();
            if (config) {
                this.uiManager.updateConfigUI(config);
            }

            console.log('✅ Application initialized successfully');
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.uiManager.showError('Application initialization failed. Please refresh and try again.');
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
            this.cameraManager.startCamera(e.target.value);
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
            const formValues = this.uiManager.getFormValues();
            if (!formValues.instruction.trim()) {
                this.uiManager.showError('Please enter an instruction before starting.');
                return;
            }

            this.isProcessing = true;
            this.uiManager.updateProcessingState(true);

            // Send first request immediately
            await this.processFrame();

            // Setup interval for continuous processing
            const interval = this.getProcessingInterval();
            this.intervalId = setInterval(() => this.processFrame(), interval);

        } catch (error) {
            console.error('Error starting processing:', error);
            this.uiManager.showError(error.message);
            this.stopProcessing();
        }
    }

    stopProcessing() {
        this.isProcessing = false;
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        this.uiManager.updateProcessingState(false);
    }

    async processFrame() {
        if (!this.isProcessing) return;

        try {
            // Capture image
            const imageData = this.cameraManager.captureImage();
            if (!imageData) {
                throw new Error('Failed to capture image');
            }

            // Get form values
            const formValues = this.uiManager.getFormValues();

            // Send to API
            const response = await this.apiClient.sendChatCompletion(
                formValues.instruction, 
                imageData, 
                formValues.maxTokens
            );
            
            // Update UI
            this.uiManager.updateResponseText(response);
            this.cameraManager.updateImagePreview(imageData);

        } catch (error) {
            console.error('Error processing frame:', error);
            this.uiManager.showError(error.message);
        }
    }

    getProcessingInterval() {
        const intervalSelect = document.getElementById('intervalSelect');
        const interval = parseInt(intervalSelect.value) || 5000;
        return Math.max(interval, 1000); // Minimum 1 second
    }
}

// Initialize application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', async () => {
    app = new VisionIntelligenceApp();
    await app.initialize();
    
    // Export for debugging purposes
    window.visionApp = app;
});