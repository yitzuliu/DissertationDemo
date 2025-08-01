/**
 * Unified Application Module
 * 
 * Main application that integrates vision analysis and state query functionality
 */

import { UnifiedAPIClient } from './modules/api-client.js';
import { CameraManager } from './modules/camera-manager.js';
import { UIManager } from './modules/ui-manager.js';

export class UnifiedApp {
    constructor() {
        this.apiClient = new UnifiedAPIClient();
        this.cameraManager = new CameraManager();
        this.uiManager = new UIManager();
        
        this.isVisionProcessing = false;
        this.visionIntervalId = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the unified application
     */
    async initialize() {
        try {
            console.log('🚀 Initializing Unified Vision Intelligence Hub...');

            // Initialize UI manager
            this.uiManager.initialize();

            // Initialize camera manager
            await this.cameraManager.initialize(
                this.uiManager.elements.videoFeed,
                this.uiManager.elements.canvas,
                this.uiManager.elements.cameraSelect
            );

            // Check backend connection and load configuration
            await Promise.allSettled([
                this.checkBackendConnection(),
                this.loadConfig()
            ]);

            // Set up event listeners
            this.setupEventListeners();

            // Set up keyboard shortcuts
            this.setupKeyboardShortcuts();

            this.isInitialized = true;
            console.log('✅ Unified application initialized successfully');

        } catch (error) {
            console.error('❌ Failed to initialize unified application:', error);
            this.uiManager.showError('Failed to initialize application. Please refresh the page.', 'initialization');
        }
    }

    /**
     * Check backend connection status
     */
    async checkBackendConnection() {
        try {
            const status = await this.apiClient.checkStatus();
            this.uiManager.updateConnectionStatus(true, status);
            console.log('✅ Backend connected:', status);
        } catch (error) {
            this.uiManager.updateConnectionStatus(false);
            console.warn('⚠️ Backend not connected:', error.message);
        }
    }

    /**
     * Load backend configuration and set default values
     */
    async loadConfig() {
        try {
            const config = await this.apiClient.loadConfig();
            
            if (config) {
                // Set default instruction if available
                if (config.default_instruction && this.uiManager.elements.instructionText) {
                    this.uiManager.elements.instructionText.value = config.default_instruction;
                    console.log('✅ Loaded default instruction:', config.default_instruction);
                }

                // Set capture intervals if available
                if (config.capture_intervals && Array.isArray(config.capture_intervals) && this.uiManager.elements.intervalSelect) {
                    this.uiManager.elements.intervalSelect.innerHTML = config.capture_intervals.map(interval =>
                        `<option value="${interval}">${interval / 1000}s</option>`
                    ).join('');
                    console.log('✅ Loaded capture intervals:', config.capture_intervals);
                }

                // Set model help text if available
                if (config.model_help) {
                    console.log('✅ Model help available:', config.model_help);
                    // Note: We could add a help section to the UI if needed
                }

                console.log('✅ Configuration loaded successfully');
            } else {
                console.warn('⚠️ No configuration available');
            }
        } catch (error) {
            console.error('❌ Failed to load configuration:', error);
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Vision analysis start/stop button
        if (this.uiManager.elements.startButton) {
            this.uiManager.elements.startButton.addEventListener('click', () => {
                this.toggleVisionAnalysis();
            });
        }

        // Query submit button
        if (this.uiManager.elements.queryButton) {
            this.uiManager.elements.queryButton.addEventListener('click', () => {
                this.processQuery();
            });
        }

        // Camera selection change
        if (this.uiManager.elements.cameraSelect) {
            this.uiManager.elements.cameraSelect.addEventListener('change', async () => {
                const selectedDeviceId = this.uiManager.elements.cameraSelect.value;
                await this.cameraManager.startCamera(selectedDeviceId);
            });
        }

        // Example query clicks
        this.uiManager.setupExampleQueries((query) => {
            this.processQuery();
        });

        // Device change detection
        navigator.mediaDevices.addEventListener('devicechange', async () => {
            console.log('Camera devices changed');
            await this.cameraManager.populateCameraList();
        });
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        this.uiManager.setupKeyboardShortcuts({
            onQuerySubmit: () => this.processQuery(),
            onVisionToggle: () => this.toggleVisionAnalysis()
        });
    }

    /**
     * Toggle vision analysis on/off
     */
    async toggleVisionAnalysis() {
        if (this.isVisionProcessing) {
            this.stopVisionAnalysis();
        } else {
            await this.startVisionAnalysis();
        }
    }

    /**
     * Start vision analysis
     */
    async startVisionAnalysis() {
        if (this.isVisionProcessing) return;

        try {
            // Check if instruction is provided
            const instruction = this.uiManager.getInstructionText();
            if (!instruction) {
                this.uiManager.showError('Please enter a question about the image before starting.');
                return;
            }

            this.isVisionProcessing = true;
            this.uiManager.updateVisionProcessingState(true);

            // Start the vision analysis loop
            this.visionIntervalId = setInterval(() => {
                if (this.isVisionProcessing) {
                    this.processVisionAnalysis();
                }
            }, parseInt(this.uiManager.getVisionSettings().interval));

            console.log('Vision analysis started with instruction:', instruction);

        } catch (error) {
            console.error('Failed to start vision analysis:', error);
            this.uiManager.showError('Failed to start vision analysis', 'vision');
            this.stopVisionAnalysis();
        }
    }

    /**
     * Stop vision analysis
     */
    stopVisionAnalysis() {
        if (!this.isVisionProcessing) return;

        this.isVisionProcessing = false;
        this.uiManager.updateVisionProcessingState(false);

        if (this.visionIntervalId) {
            clearInterval(this.visionIntervalId);
            this.visionIntervalId = null;
        }

        console.log('Vision analysis stopped');
    }

    /**
     * Process vision analysis
     */
    async processVisionAnalysis() {
        if (!this.cameraManager.isReady()) {
            this.uiManager.showError('Camera not ready. Please check camera permissions.');
            return;
        }

        try {
            // Get instruction from textarea
            const instruction = this.uiManager.getInstructionText();
            if (!instruction) {
                this.uiManager.showError('Please enter a question about the image.');
                return;
            }

            // Capture image
            const imageResult = this.cameraManager.captureImage();
            if (!imageResult) {
                throw new Error('Failed to capture image');
            }

            // Send image for VLM analysis
            const maxTokens = parseInt(this.uiManager.getVisionSettings().maxTokens);
            const response = await this.apiClient.sendVisionAnalysis(instruction, imageResult, maxTokens);

            // Display VLM response using unified response system
            this.uiManager.showVisionResponse(response);

            console.log('VLM analysis completed:', response);

        } catch (error) {
            console.error('Vision analysis error:', error);
            this.uiManager.showError(`Vision analysis failed: ${error.message}`, 'vision');
        }
    }

    /**
     * Process state query
     */
    async processQuery() {
        const query = this.uiManager.getQueryInput();
        
        if (!query) {
            this.uiManager.showError("Please enter a query before submitting.", 'query');
            return;
        }

        this.uiManager.showQueryLoading();

        try {
            const startTime = Date.now();
            
            // Generate query ID and log user query
            const queryId = this.apiClient.generateQueryId();
            const queryData = {
                query_id: queryId,
                query: query,
                language: this.apiClient.detectLanguage(query),
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                observation_id: null // Could be linked to current vision observation
            };

            // Log user query (non-blocking)
            this.apiClient.logUserQuery(queryData);

            // Send state query
            const response = await this.apiClient.sendStateQuery(query, queryId);
            
            const processingTime = Date.now() - startTime;

            // Show response using unified response system
            const responseText = response.response_text || response.response || 'No response received';
            this.uiManager.showQueryResponse(responseText, response.query_type || 'State Query');

            console.log('✅ Query processed successfully:', response);

        } catch (error) {
            console.error('Query processing error:', error);
            this.uiManager.showError(`Query failed: ${error.message}`, 'query');
        } finally {
            this.uiManager.hideQueryLoading();
        }
    }

    /**
     * Get application status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            visionProcessing: this.isVisionProcessing,
            cameraReady: this.cameraManager.isReady(),
            uiReady: this.uiManager.isReady(),
            cameraStatus: this.cameraManager.getStatus(),
            uiStatus: this.uiManager.getStatus()
        };
    }

    /**
     * Cleanup application resources
     */
    cleanup() {
        this.stopVisionAnalysis();
        this.cameraManager.cleanup();
        console.log('🧹 Application cleanup completed');
    }
}

// Initialize application when DOM is ready
let app;

async function initializeApp() {
    try {
        console.log('🚀 Starting Unified Vision Intelligence Hub...');

        // Create main application instance
        app = new UnifiedApp();

        // Start the application
        await app.initialize();

        console.log('✅ Application started successfully');

        // Set up global error handling
        window.addEventListener('error', (event) => {
            console.error('❌ Global error:', event.error);
            if (app && app.uiManager) {
                app.uiManager.showError('An unexpected error occurred. Please refresh the page.', 'global');
            }
        });

        // Set up unload cleanup
        window.addEventListener('beforeunload', () => {
            if (app) {
                app.cleanup();
            }
        });

        // Retry backend connection periodically when offline
        setInterval(() => {
            const connectionStatus = document.getElementById('connectionStatus');
            if (connectionStatus && connectionStatus.classList.contains('status-disconnected')) {
                app.checkBackendConnection();
            }
        }, 30000);

    } catch (error) {
        console.error('❌ Failed to start application:', error);

        // Fallback error display
        const responseText = document.getElementById('responseText');
        if (responseText) {
            responseText.textContent = 'Failed to start application. Please refresh the page.';
            responseText.style.color = 'var(--error)';
        }
    }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export for debugging
window.unifiedApp = () => app; 