/**
 * Configuration Management Module
 * Handles loading and managing application configuration
 */

class ConfigManager {
    constructor() {
        this.config = null;
        this.baseURL = "http://localhost:8000";
    }

    /**
     * Load configuration from the backend
     * @returns {Promise<Object>} Configuration object
     */
    async loadConfig() {
        try {
            const response = await fetch(`${this.baseURL}/config`);
            if (!response.ok) {
                throw new Error(`Failed to load configuration: ${response.status}`);
            }
            
            this.config = await response.json();
            return this.config;
        } catch (error) {
            console.error("Failed to load config:", error);
            throw error;
        }
    }

    /**
     * Get configuration value by key
     * @param {string} key - Configuration key
     * @param {*} defaultValue - Default value if key not found
     * @returns {*} Configuration value
     */
    get(key, defaultValue = null) {
        if (!this.config) {
            console.warn("Configuration not loaded yet");
            return defaultValue;
        }

        const keys = key.split('.');
        let value = this.config;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        
        return value;
    }

    /**
     * Get the base URL for API calls
     * @returns {string} Base URL
     */
    getBaseURL() {
        return this.baseURL;
    }

    /**
     * Get model help text
     * @returns {string} Model help text
     */
    getModelHelp() {
        return this.get('model_help', '');
    }

    /**
     * Get default instruction text
     * @returns {string} Default instruction
     */
    getDefaultInstruction() {
        return this.get('default_instruction', '');
    }

    /**
     * Get capture intervals
     * @returns {Array<number>} Array of capture intervals in milliseconds
     */
    getCaptureIntervals() {
        return this.get('capture_intervals', [500, 1000, 2000, 5000, 10000, 20000]);
    }

    /**
     * Get active model name
     * @returns {string} Active model name
     */
    getActiveModel() {
        return this.get('active_model', 'unknown');
    }

    /**
     * Check if configuration is loaded
     * @returns {boolean} True if config is loaded
     */
    isLoaded() {
        return this.config !== null;
    }
}

// Export singleton instance
export const configManager = new ConfigManager();