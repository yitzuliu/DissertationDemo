/**
 * Unified API Client Module
 * 
 * Handles all API communication for the unified interface
 */

export class UnifiedAPIClient {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.apiBaseUrl = `${this.baseURL}/api/v1`;
    }

    /**
     * Check backend connection status
     */
    async checkStatus() {
        try {
            const response = await fetch(`${this.baseURL}/status`, {
                signal: AbortSignal.timeout(5000)
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            throw error;
        }
    }

    /**
     * Load backend configuration
     */
    async loadConfig() {
        try {
            const response = await fetch(`${this.baseURL}/config`, {
                signal: AbortSignal.timeout(3000)
            });

            if (!response.ok) {
                throw new Error("Failed to load configuration");
            }

            return await response.json();
        } catch (error) {
            console.error("Failed to load config:", error);
            return null;
        }
    }

    /**
     * Send state query
     */
    async sendStateQuery(query, queryId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/state/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    query_id: queryId
                }),
                signal: AbortSignal.timeout(10000)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Log user query
     */
    async logUserQuery(queryData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/logging/user_query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(queryData),
                signal: AbortSignal.timeout(2000)
            });

            if (!response.ok) {
                console.warn('Failed to log user query:', response.status);
            }
        } catch (error) {
            console.warn('Failed to log user query:', error);
        }
    }

    /**
     * Generate query ID
     */
    generateQueryId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substr(2, 8);
        return `query_${timestamp}_${random}`;
    }

    /**
     * Send vision analysis request
     */
    async sendVisionAnalysis(instruction, imageResult, maxTokens = 100) {
        try {
            const requestBody = {
                max_tokens: maxTokens,
                messages: [
                    {
                        role: 'user',
                        content: [
                            { type: 'text', text: instruction },
                            { type: 'image_url', image_url: { url: imageResult.dataURL } }
                        ]
                    }
                ]
            };

            const response = await fetch(`${this.baseURL}/v1/chat/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
                signal: AbortSignal.timeout(30000)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();

            // Validate API response format
            if (!data || !data.choices || !Array.isArray(data.choices) || data.choices.length === 0) {
                throw new Error('Invalid API response format');
            }

            if (!data.choices[0].message || !data.choices[0].message.content) {
                throw new Error('Invalid message format in API response');
            }

            return data.choices[0].message.content;

        } catch (error) {
            throw error;
        }
    }

    /**
     * Detect language
     */
    detectLanguage(text) {
        const chinesePattern = /[\u4e00-\u9fff]/;
        const englishPattern = /[a-zA-Z]/;
        
        if (chinesePattern.test(text)) {
            return 'zh';
        } else if (englishPattern.test(text)) {
            return 'en';
        } else {
            return 'unknown';
        }
    }
} 