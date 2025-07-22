/**
 * UI Management Module
 * Handles user interface updates and interactions
 */

import { showError, hideError, setLoadingState, removeLoadingState, addEventListenerSafe } from '../utils/helpers.js';

class UIManager {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
    }

    /**
     * Initialize UI manager with DOM elements
     */
    initialize() {
        // Get all required DOM elements
        this.elements = {
            // Form elements
            instructionText: document.getElementById('instructionText'),
            responseText: document.getElementById('responseText'),
            intervalSelect: document.getElementById('intervalSelect'),
            qualitySelect: document.getElementById('qualitySelect'),
            tokensSelect: document.getElementById('tokensSelect'),
            startButton: document.getElementById('startButton'),
            
            // Status elements
            errorMsg: document.getElementById('errorMsg'),
            modelHelp: document.getElementById('modelHelp'),
            activeModel: document.getElementById('activeModel'),
            apiStatusDot: document.getElementById('apiStatusDot'),
            apiStatusText: document.getElementById('apiStatusText'),
            systemStatus: document.getElementById('systemStatus'),
            modelDesc: document.getElementById('modelDesc'),
            
            // Other elements
            captureLabel: document.querySelector('.capture-label')
        };

        // Set up event listeners
        this.setupEventListeners();

        this.isInitialized = true;
    }

    /**
     * Set up UI event listeners
     */
    setupEventListeners() {
        // Keyboard shortcuts
        if (this.elements.instructionText) {
            addEventListenerSafe(this.elements.instructionText, 'keydown', (e) => {
                // Ctrl+Enter to start/stop processing
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.triggerStartStop();
                }
            });
        }
    }

    /**
     * Update API status display
     * @param {boolean} isOnline - Whether API is online
     * @param {Object} data - Status data (if online)
     * @param {Error} error - Error object (if offline)
     */
    updateApiStatus(isOnline, data = null, error = null) {
        if (isOnline && data) {
            this.updateApiStatusOnline(data);
        } else {
            this.updateApiStatusOffline(error);
        }
    }

    /**
     * Update UI for online API status
     * @param {Object} data - API status data
     */
    updateApiStatusOnline(data) {
        // Update status indicators
        if (this.elements.apiStatusDot) {
            this.elements.apiStatusDot.className = "status-dot online";
        }
        if (this.elements.apiStatusText) {
            this.elements.apiStatusText.textContent = "API Online";
        }
        
        // Use model's display name
        const modelName = data.model_status?.name || data.active_model || "Unknown";
        if (this.elements.activeModel) {
            this.elements.activeModel.textContent = modelName;
        }
        
        // Create a nicely formatted status display
        const availableModels = data.available_models && data.available_models.length 
            ? data.available_models.join(", ") 
            : "None";
            
        if (this.elements.systemStatus) {
            this.elements.systemStatus.innerHTML = `
                <div style="margin-bottom: 0.75rem;"><strong>Status:</strong> <span style="color: var(--success);">Connected</span></div>
                <div style="margin-bottom: 0.75rem;"><strong>Active Model:</strong> ${modelName}</div>
                <div style="margin-bottom: 0.75rem;"><strong>Version:</strong> ${data.model_status?.version || "N/A"}</div>
                <div><strong>Available Models:</strong> ${availableModels}</div>
            `;
        }

        // Update model description if available
        if (this.elements.modelDesc && data.model_status?.description) {
            this.elements.modelDesc.innerHTML = `
                <div style="margin-bottom: 0.75rem;">${data.model_status.description}</div>
            `;
        }
    }

    /**
     * Update UI for offline API status
     * @param {Error} error - Error object
     */
    updateApiStatusOffline(error = null) {
        // Update status indicators
        if (this.elements.apiStatusDot) {
            this.elements.apiStatusDot.className = "status-dot offline";
        }
        if (this.elements.apiStatusText) {
            this.elements.apiStatusText.textContent = "API Offline";
        }
        
        // Create error message
        let errorMessage = error ? `Unable to connect to the backend API: ${error.message}` 
            : "Unable to connect to the backend API. Please check if the server is running.";
        
        if (this.elements.systemStatus) {
            this.elements.systemStatus.innerHTML = `
                <div style="color: var(--error);"><i class="fas fa-exclamation-triangle"></i> Connection Error</div>
                <div style="margin-top: 0.75rem;">${errorMessage}</div>
                <div style="margin-top: 0.5rem;">Please ensure the server is running</div>
            `;
        }
    }

    /**
     * Update configuration-based UI elements
     * @param {Object} config - Configuration object
     */
    updateConfigUI(config) {
        // Update model help
        if (config.model_help && this.elements.modelHelp) {
            this.elements.modelHelp.style.display = "block";
            this.elements.modelHelp.textContent = config.model_help;
        } else if (this.elements.modelHelp) {
            this.elements.modelHelp.style.display = "none";
        }
        
        // Update default instruction
        if (config.default_instruction && this.elements.instructionText) {
            this.elements.instructionText.value = config.default_instruction;
        }
        
        // Update interval options if available
        if (config.capture_intervals && Array.isArray(config.capture_intervals) && this.elements.intervalSelect) {
            this.elements.intervalSelect.innerHTML = config.capture_intervals.map(interval => 
                `<option value="${interval}">${interval/1000}s</option>`
            ).join('');
        }
    }

    /**
     * Update UI for processing state
     * @param {boolean} isProcessing - Whether processing is active
     */
    updateProcessingState(isProcessing) {
        if (!this.elements.startButton) return;

        if (isProcessing) {
            // Update button to show stop state
            this.elements.startButton.innerHTML = '<i class="fas fa-stop"></i><span>Stop Processing</span>';
            this.elements.startButton.classList.add('btn-danger');
            this.elements.startButton.classList.remove('btn-primary');
            
            // Disable controls during processing
            this.setControlsEnabled(false);
            
            // Clear any previous response text
            if (this.elements.responseText) {
                this.elements.responseText.value = "";
            }
        } else {
            // Update button to show start state
            this.elements.startButton.innerHTML = '<i class="fas fa-play"></i><span>Start Processing</span>';
            this.elements.startButton.classList.add('btn-primary');
            this.elements.startButton.classList.remove('btn-danger');
            
            // Re-enable controls
            this.setControlsEnabled(true);
        }
    }

    /**
     * Enable or disable form controls
     * @param {boolean} enabled - Whether controls should be enabled
     */
    setControlsEnabled(enabled) {
        const controls = [
            this.elements.instructionText,
            this.elements.intervalSelect,
            this.elements.qualitySelect,
            this.elements.tokensSelect
        ];

        controls.forEach(control => {
            if (control) {
                control.disabled = !enabled;
            }
        });
    }

    /**
     * Update response text
     * @param {string} content - Response content
     */
    updateResponseText(content) {
        if (this.elements.responseText) {
            this.elements.responseText.value = content || "No response received";
        }
    }

    /**
     * Show processing indicator in header
     * @param {boolean} isProcessing - Whether to show processing indicator
     */
    showProcessingIndicator(isProcessing) {
        const statusItem = document.querySelector('.status-item:first-child');
        const processingIndicator = document.getElementById('processingIndicator');
        
        if (isProcessing) {
            // Create indicator if it doesn't exist
            if (!processingIndicator) {
                const indicator = document.createElement('div');
                indicator.id = 'processingIndicator';
                indicator.innerHTML = '<i class="fas fa-sync fa-spin"></i> Processing';
                indicator.style.marginLeft = '15px';
                indicator.style.color = 'var(--warning)';
                indicator.style.fontSize = '0.8rem';
                indicator.style.display = 'flex';
                indicator.style.alignItems = 'center';
                indicator.style.gap = '5px';
                
                if (statusItem) {
                    statusItem.parentNode.insertBefore(indicator, statusItem.nextSibling);
                }
            }
        } else if (processingIndicator) {
            // Remove indicator when processing is complete
            processingIndicator.remove();
        }
    }

    /**
     * Update capture label with status
     * @param {string} status - Status message
     * @param {string} type - Status type ('processing', 'success', 'error', 'info')
     */
    updateCaptureLabel(status, type = 'info') {
        if (!this.elements.captureLabel) return;

        const colors = {
            processing: { bg: 'var(--warning-light)', color: 'var(--warning)' },
            success: { bg: 'var(--success-light)', color: 'var(--success)' },
            error: { bg: 'var(--error-light)', color: 'var(--error)' },
            info: { bg: '', color: '' }
        };

        const colorScheme = colors[type] || colors.info;
        
        this.elements.captureLabel.innerHTML = status;
        this.elements.captureLabel.style.backgroundColor = colorScheme.bg;
        this.elements.captureLabel.style.color = colorScheme.color;

        // Auto-reset after delay for non-info messages
        if (type !== 'info') {
            setTimeout(() => {
                this.elements.captureLabel.style.backgroundColor = '';
                this.elements.captureLabel.style.color = '';
            }, 2000);
        }
    }

    /**
     * Get form values
     * @returns {Object} Form values
     */
    getFormValues() {
        return {
            instruction: this.elements.instructionText?.value.trim() || '',
            interval: parseInt(this.elements.intervalSelect?.value) || 2000,
            quality: parseFloat(this.elements.qualitySelect?.value) || 0.9,
            maxTokens: parseInt(this.elements.tokensSelect?.value) || 100
        };
    }

    /**
     * Validate form inputs
     * @returns {Object} Validation result
     */
    validateForm() {
        const values = this.getFormValues();
        const errors = [];

        if (!values.instruction) {
            errors.push("Please enter an instruction before starting.");
        }

        if (values.interval < 100) {
            errors.push("Capture interval must be at least 100ms.");
        }

        if (values.quality < 0.1 || values.quality > 1.0) {
            errors.push("Image quality must be between 0.1 and 1.0.");
        }

        if (values.maxTokens < 1 || values.maxTokens > 1000) {
            errors.push("Max tokens must be between 1 and 1000.");
        }

        return {
            valid: errors.length === 0,
            errors,
            values
        };
    }

    /**
     * Set loading state for status elements
     */
    setStatusLoading() {
        setLoadingState(this.elements.systemStatus, this.elements.modelDesc);
    }

    /**
     * Remove loading state from status elements
     */
    removeStatusLoading() {
        removeLoadingState(this.elements.systemStatus, this.elements.modelDesc);
    }

    /**
     * Trigger start/stop button click (for keyboard shortcuts)
     */
    triggerStartStop() {
        if (this.elements.startButton) {
            this.elements.startButton.click();
        }
    }

    /**
     * Check if UI is initialized
     * @returns {boolean} True if initialized
     */
    isReady() {
        return this.isInitialized;
    }

    /**
     * Get element by key
     * @param {string} key - Element key
     * @returns {HTMLElement|null} Element or null
     */
    getElement(key) {
        return this.elements[key] || null;
    }
}

// Export singleton instance
export const uiManager = new UIManager();