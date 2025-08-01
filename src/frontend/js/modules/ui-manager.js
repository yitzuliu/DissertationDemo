/**
 * Unified UI Manager Module
 * 
 * Handles all UI updates and user interactions for the unified interface
 */

export class UIManager {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.responseHistory = [];
        this.maxHistoryItems = 8;
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
        this.elements.responseContainer = document.getElementById('responseContainer');
        this.elements.responseLoading = document.getElementById('responseLoading');

        // Status elements
        this.elements.connectionStatus = document.getElementById('connectionStatus');

        // Validate all required elements exist
        const requiredElements = [
            'videoFeed', 'canvas', 'cameraSelect', 'startButton',
            'queryInput', 'queryButton', 'responseContainer', 'connectionStatus'
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
     * Add a new response item to the unified response area
     */
    addResponseItem(type, title, content, metadata = {}) {
        if (!this.elements.responseContainer) return;

        const responseItem = this.createResponseItem(type, title, content, metadata);
        
        // Add to history
        this.responseHistory.unshift(responseItem);
        
        // Limit history size
        if (this.responseHistory.length > this.maxHistoryItems) {
            this.responseHistory = this.responseHistory.slice(0, this.maxHistoryItems);
        }
        
        // Update display
        this.updateResponseDisplay();
        
        // Auto-scroll to top
        this.scrollToTop();
    }

    /**
     * Create a response item element
     */
    createResponseItem(type, title, content, metadata = {}) {
        const timestamp = new Date().toLocaleTimeString();
        
        return {
            type,
            title,
            content,
            timestamp,
            metadata,
            id: `response_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }

    /**
     * Update the response display with current history
     */
    updateResponseDisplay() {
        if (!this.elements.responseContainer) return;

        this.elements.responseContainer.innerHTML = this.responseHistory
            .map(item => this.renderResponseItem(item))
            .join('');
    }

    /**
     * Render a single response item as HTML
     */
    renderResponseItem(item) {
        const iconMap = {
            'vision': 'fas fa-robot',
            'query': 'fas fa-chart-line',
            'system': 'fas fa-info-circle',
            'error': 'fas fa-exclamation-triangle'
        };

        const icon = iconMap[item.type] || 'fas fa-comment';
        
        return `
            <div class="response-item ${item.type}-response" data-id="${item.id}">
                <div class="response-header">
                    <i class="${icon}"></i>
                    <span class="response-title">${item.title}</span>
                    <span class="response-time">${item.timestamp}</span>
                </div>
                <div class="response-content-text">
                    ${this.escapeHtml(item.content)}
                </div>
                ${this.renderMetadata(item.metadata)}
            </div>
        `;
    }

    /**
     * Render metadata if available
     */
    renderMetadata(metadata) {
        if (!metadata || Object.keys(metadata).length === 0) return '';

        const metaItems = [];
        if (metadata.processingTime) {
            metaItems.push(`<span><i class="fas fa-clock"></i> ${metadata.processingTime}ms</span>`);
        }
        if (metadata.confidence) {
            metaItems.push(`<span><i class="fas fa-percentage"></i> ${metadata.confidence}% confidence</span>`);
        }
        if (metadata.queryType) {
            metaItems.push(`<span><i class="fas fa-tag"></i> ${metadata.queryType}</span>`);
        }

        if (metaItems.length === 0) return '';

        return `
            <div class="response-meta" style="margin-top: 0.5rem; font-size: 0.7rem; color: var(--text-light);">
                ${metaItems.join(' • ')}
            </div>
        `;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Scroll response area to top
     */
    scrollToTop() {
        const responseContent = document.querySelector('.response-content');
        if (responseContent) {
            responseContent.scrollTop = 0;
        }
    }

    /**
     * Show vision analysis response
     */
    showVisionResponse(response) {
        this.addResponseItem(
            'vision',
            'Vision Analysis',
            response,
            { processingTime: Date.now() }
        );
    }

    /**
     * Show query response
     */
    showQueryResponse(response, type = 'State Query') {
        this.addResponseItem(
            'query',
            type,
            response,
            { queryType: type }
        );
    }

    /**
     * Show system message
     */
    showSystemMessage(message, title = 'System') {
        this.addResponseItem('system', title, message);
    }

    /**
     * Show error message
     */
    showError(message, type = 'general') {
        this.addResponseItem(
            'error',
            'Error',
            message,
            { errorType: type }
        );
    }

    /**
     * Show loading state
     */
    showQueryLoading() {
        if (this.elements.responseLoading) {
            this.elements.responseLoading.style.display = 'flex';
        }
    }

    /**
     * Hide loading state
     */
    hideQueryLoading() {
        if (this.elements.responseLoading) {
            this.elements.responseLoading.style.display = 'none';
        }
    }

    /**
     * Clear all responses
     */
    clearResponses() {
        this.responseHistory = [];
        if (this.elements.responseContainer) {
            this.elements.responseContainer.innerHTML = `
                <div class="response-item system-message">
                    <div class="response-header">
                        <i class="fas fa-info-circle"></i>
                        <span class="response-title">Welcome</span>
                        <span class="response-time">Now</span>
                    </div>
                    <div class="response-content-text">
                        Welcome to the unified interface! Use the left panel for vision analysis and the right panel for queries and responses.
                    </div>
                </div>
            `;
        }
    }

    /**
     * Get query input value
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
            interval: this.elements.intervalSelect ? this.elements.intervalSelect.value : '2000',
            quality: this.elements.qualitySelect ? this.elements.qualitySelect.value : '0.9',
            maxTokens: this.elements.tokensSelect ? this.elements.tokensSelect.value : '100'
        };
    }

    /**
     * Get instruction text
     */
    getInstructionText() {
        return this.elements.instructionText ? this.elements.instructionText.value.trim() : '';
    }

    /**
     * Setup example query click handlers
     */
    setupExampleQueries(callback) {
        const examples = document.querySelectorAll('.example-query');
        examples.forEach(example => {
            example.addEventListener('click', () => {
                const query = example.getAttribute('data-query');
                if (query && this.elements.queryInput) {
                    this.elements.queryInput.value = query;
                    if (callback) callback(query);
                }
            });
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts(callbacks) {
        // Enter key for query input
        if (this.elements.queryInput) {
            this.elements.queryInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (callbacks.onQuerySubmit) {
                        callbacks.onQuerySubmit();
                    }
                }
            });
        }

        // Ctrl+Enter for vision analysis
        if (this.elements.instructionText) {
            this.elements.instructionText.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    if (callbacks.onVisionToggle) {
                        callbacks.onVisionToggle();
                    }
                }
            });
        }
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
        return this.isInitialized;
    }

    /**
     * Get UI status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            responseCount: this.responseHistory.length,
            elements: Object.keys(this.elements).filter(key => this.elements[key] !== null).length
        };
    }
} 