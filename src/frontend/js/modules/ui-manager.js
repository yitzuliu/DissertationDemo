/**
 * Unified UI Manager Module
 * 
 * Handles all UI updates and user interactions for the unified interface
 */

export class UIManager {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
    }

    /**
     * Initialize UI manager with DOM elements
     */
    initialize() {
        // Vision elements
        this.elements.videoFeed = document.getElementById('videoFeed');
        this.elements.canvas = document.getElementById('canvas');
        this.elements.cameraSelect = document.getElementById('cameraSelect');
        this.elements.intervalSelect = document.getElementById('intervalSelect');
        this.elements.qualitySelect = document.getElementById('qualitySelect');
        this.elements.tokensSelect = document.getElementById('tokensSelect');
        this.elements.startButton = document.getElementById('startButton');
        this.elements.instructionText = document.getElementById('instructionText');

        // Query panel elements
        this.elements.queryInput = document.getElementById('queryInput');
        this.elements.queryButton = document.getElementById('queryButton');
        this.elements.responseText = document.getElementById('responseText');
        this.elements.responseLoading = document.getElementById('responseLoading');
        this.elements.responseMeta = document.getElementById('responseMeta');
        this.elements.processingTime = document.getElementById('processingTime');
        this.elements.queryType = document.getElementById('queryType');
        this.elements.confidence = document.getElementById('confidence');

        // Status elements
        this.elements.connectionStatus = document.getElementById('connectionStatus');

        // Validate all required elements exist
        const requiredElements = [
            'videoFeed', 'canvas', 'cameraSelect', 'startButton',
            'queryInput', 'queryButton', 'responseText', 'connectionStatus'
        ];

        for (const elementName of requiredElements) {
            if (!this.elements[elementName]) {
                throw new Error(`Required element not found: ${elementName}`);
            }
        }

        this.isInitialized = true;
        console.log('✅ UI Manager initialized successfully');
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(isConnected, data = null) {
        if (!this.elements.connectionStatus) return;

        const statusDot = this.elements.connectionStatus.querySelector('.status-dot');
        const statusText = this.elements.connectionStatus.querySelector('span:last-child');

        if (isConnected) {
            this.elements.connectionStatus.classList.remove('status-disconnected');
            this.elements.connectionStatus.classList.add('status-connected');
            if (statusDot) statusDot.classList.add('online');
            if (statusDot) statusDot.classList.remove('offline');
            if (statusText) statusText.textContent = 'Connected';
        } else {
            this.elements.connectionStatus.classList.remove('status-connected');
            this.elements.connectionStatus.classList.add('status-disconnected');
            if (statusDot) statusDot.classList.add('offline');
            if (statusDot) statusDot.classList.remove('online');
            if (statusText) statusText.textContent = 'Disconnected';
        }
    }

    /**
     * Update vision analysis processing state
     */
    updateVisionProcessingState(isProcessing) {
        if (!this.elements.startButton) return;

        if (isProcessing) {
            this.elements.startButton.innerHTML = '<i class="fas fa-stop"></i><span>Stop Vision Analysis</span>';
            this.elements.startButton.classList.add('danger');
        } else {
            this.elements.startButton.innerHTML = '<i class="fas fa-play"></i><span>Start Vision Analysis</span>';
            this.elements.startButton.classList.remove('danger');
        }
    }

    /**
     * Show vision analysis response
     */
    showVisionResponse(response) {
        // Display VLM response in the query response area
        if (this.elements.responseText) {
            this.elements.responseText.textContent = response;
            this.elements.responseText.style.color = 'var(--text)';
        }

        // Hide loading if it's showing
        this.hideQueryLoading();

        // Show meta information for vision analysis
        if (this.elements.responseMeta) {
            this.elements.responseMeta.style.display = 'flex';
        }

        // Update meta information to show it's a vision response
        if (this.elements.queryType) {
            this.elements.queryType.textContent = 'Vision Analysis';
        }
        if (this.elements.processingTime) {
            this.elements.processingTime.textContent = 'Real-time';
        }
        if (this.elements.confidence) {
            this.elements.confidence.textContent = '100';
        }
    }

    /**
     * Show query response
     */
    showQueryResponse(response, type = 'State Query') {
        if (!this.elements.responseText) return;

        // Hide loading
        this.hideQueryLoading();

        // Show response
        this.elements.responseText.textContent = response;

        // Show meta information if available
        if (this.elements.responseMeta) {
            this.elements.responseMeta.style.display = 'flex';
        }
    }

    /**
     * Show query loading state
     */
    showQueryLoading() {
        if (this.elements.responseLoading) {
            this.elements.responseLoading.style.display = 'flex';
        }
        if (this.elements.responseText) {
            this.elements.responseText.textContent = '';
        }
        if (this.elements.responseMeta) {
            this.elements.responseMeta.style.display = 'none';
        }
    }

    /**
     * Hide query loading state
     */
    hideQueryLoading() {
        if (this.elements.responseLoading) {
            this.elements.responseLoading.style.display = 'none';
        }
    }

    /**
     * Update query response meta information
     */
    updateQueryMeta(processingTime, queryType, confidence) {
        if (this.elements.processingTime) {
            this.elements.processingTime.textContent = processingTime;
        }
        if (this.elements.queryType) {
            this.elements.queryType.textContent = queryType;
        }
        if (this.elements.confidence) {
            this.elements.confidence.textContent = confidence;
        }
    }

    /**
     * Show error message
     */
    showError(message, type = 'general') {
        console.error(`[${type}] Error:`, message);

        // For now, show errors in the response area
        if (this.elements.responseText) {
            this.elements.responseText.textContent = `Error: ${message}`;
            this.elements.responseText.style.color = 'var(--error)';
        }

        // Hide loading
        this.hideQueryLoading();
    }

    /**
     * Clear error state
     */
    clearError() {
        if (this.elements.responseText) {
            this.elements.responseText.style.color = '';
        }
    }

    /**
     * Get current query input value
     */
    getQueryInput() {
        return this.elements.queryInput ? this.elements.queryInput.value.trim() : '';
    }

    /**
     * Clear query input
     */
    clearQueryInput() {
        if (this.elements.queryInput) {
            this.elements.queryInput.value = '';
        }
    }

    /**
     * Get vision analysis settings
     */
    getVisionSettings() {
        return {
            quality: parseFloat(this.elements.qualitySelect?.value || 0.9),
            maxTokens: parseInt(this.elements.tokensSelect?.value || 100),
            interval: parseInt(this.elements.intervalSelect?.value || 3000)
        };
    }

    /**
     * Get instruction text
     */
    getInstructionText() {
        return this.elements.instructionText?.value || '';
    }

    /**
     * Set up example query click handlers
     */
    setupExampleQueries(callback) {
        const examples = document.querySelectorAll('.example-query');
        examples.forEach(example => {
            example.addEventListener('click', () => {
                const query = example.getAttribute('data-query');
                if (query && this.elements.queryInput) {
                    this.elements.queryInput.value = query;
                    if (callback) {
                        callback(query);
                    }
                }
            });
        });
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts(callbacks) {
        // Enter key in query input
        if (this.elements.queryInput) {
            this.elements.queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && callbacks.onQuerySubmit) {
                    callbacks.onQuerySubmit();
                }
            });
        }

        // Ctrl+Enter for vision analysis
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter' && callbacks.onVisionToggle) {
                callbacks.onVisionToggle();
            }
        });
    }

    /**
     * Update camera selection
     */
    updateCameraSelection(deviceId) {
        if (this.elements.cameraSelect) {
            this.elements.cameraSelect.value = deviceId;
        }
    }

    /**
     * Get current camera selection
     */
    getCurrentCamera() {
        return this.elements.cameraSelect ? this.elements.cameraSelect.value : null;
    }

    /**
     * Check if UI is ready
     */
    isReady() {
        return this.isInitialized && this.elements.queryInput && this.elements.startButton;
    }

    /**
     * Get UI status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            elementsReady: this.isReady(),
            queryInput: !!this.elements.queryInput,
            startButton: !!this.elements.startButton,
            responseArea: !!this.elements.responseText
        };
    }
} 