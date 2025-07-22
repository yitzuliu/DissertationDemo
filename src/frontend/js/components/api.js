/**
 * API Communication Module
 * Handles all communication with the backend API
 */

import { configManager } from '../utils/config.js';

class APIClient {
    constructor() {
        this.baseURL = configManager.getBaseURL();
        this.currentRequestProcessing = false;
    }

    /**
     * Check API status
     * @returns {Promise<Object>} API status information
     */
    async checkStatus() {
        try {
            const response = await fetch(`${this.baseURL}/status`);
            if (response.ok) {
                return {
                    online: true,
                    data: await response.json()
                };
            } else {
                return {
                    online: false,
                    error: `HTTP ${response.status}`
                };
            }
        } catch (error) {
            return {
                online: false,
                error: error.message
            };
        }
    }

    /**
     * Send chat completion request to the backend
     * @param {string} instruction - User text instruction
     * @param {string} imageBase64URL - Base64 encoded image URL
     * @param {number} maxTokens - Maximum tokens for response
     * @returns {Promise<string>} The model's response text
     */
    async sendChatCompletion(instruction, imageBase64URL, maxTokens = 100) {
        // Check if a request is already being processed
        if (this.currentRequestProcessing) {
            console.log("⏳ Previous request still processing, skipping this one");
            throw new Error("Previous request still processing");
        }

        // Set processing flag
        this.currentRequestProcessing = true;

        try {
            const response = await fetch(`${this.baseURL}/v1/chat/completions`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({
                    max_tokens: maxTokens,
                    messages: [
                        { 
                            role: 'user', 
                            content: [
                                { type: 'text', text: instruction },
                                { type: 'image_url', image_url: { url: imageBase64URL } }
                            ]
                        }
                    ]
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            return data.choices[0].message.content;
        } finally {
            // Clear processing flag
            this.currentRequestProcessing = false;
        }
    }

    /**
     * Load configuration from backend
     * @returns {Promise<Object>} Configuration object
     */
    async loadConfig() {
        const response = await fetch(`${this.baseURL}/config`);
        if (!response.ok) {
            throw new Error(`Failed to load configuration: ${response.status}`);
        }
        return await response.json();
    }

    /**
     * Update configuration on backend
     * @param {Object} updates - Configuration updates
     * @returns {Promise<Object>} Updated configuration
     */
    async updateConfig(updates) {
        const response = await fetch(`${this.baseURL}/api/v1/config`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to update configuration: ${response.status} - ${errorText}`);
        }

        return await response.json();
    }

    /**
     * Get full system configuration
     * @returns {Promise<Object>} Full configuration object
     */
    async getFullConfig() {
        const response = await fetch(`${this.baseURL}/api/v1/config`);
        if (!response.ok) {
            throw new Error(`Failed to get full configuration: ${response.status}`);
        }
        return await response.json();
    }

    /**
     * Health check endpoint
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        const response = await fetch(`${this.baseURL}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.status}`);
        }
        return await response.json();
    }

    /**
     * Check if a request is currently being processed
     * @returns {boolean} True if processing
     */
    isProcessing() {
        return this.currentRequestProcessing;
    }

    /**
     * Set the base URL for API calls
     * @param {string} url - New base URL
     */
    setBaseURL(url) {
        this.baseURL = url;
    }

    /**
     * Get the current base URL
     * @returns {string} Current base URL
     */
    getBaseURL() {
        return this.baseURL;
    }
}

// Export singleton instance
export const apiClient = new APIClient();