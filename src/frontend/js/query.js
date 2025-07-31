/**
 * State Query System JavaScript
 * 
 * Handles instant query processing and response display
 * for the State Tracker whiteboard mechanism.
 */

class StateQuerySystem {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.isConnected = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkConnection();
        this.loadCapabilities();
    }

    bindEvents() {
        // Query input and button
        const queryInput = document.getElementById('queryInput');
        const queryButton = document.getElementById('queryButton');

        queryButton.addEventListener('click', () => this.processQuery());
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processQuery();
            }
        });

        // Example queries
        document.querySelectorAll('.example-query').forEach(example => {
            example.addEventListener('click', () => {
                const query = example.getAttribute('data-query');
                queryInput.value = query;
                this.processQuery();
            });
        });
    }

    // 新增：生成 query_id 的方法（與後端格式一致）
    generateQueryId() {
        const timestamp = Date.now(); // 毫秒級時間戳
        const random = Math.random().toString(36).substr(2, 8); // 8位隨機字符
        return `query_${timestamp}_${random}`;
    }

    // 新增：語言檢測
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

    // 新增：異步記錄使用者查詢（不阻塞主要流程）
    async logUserQuery(query_id, query) {
        try {
            const logData = {
                query_id: query_id,
                query: query,
                language: this.detectLanguage(query),
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                // 新增：嘗試關聯當前的 observation_id（如果有的話）
                observation_id: this.getCurrentObservationId()
            };

            // 使用 Promise.race 確保不會阻塞太久
            const logPromise = fetch(`${this.apiBaseUrl}/logging/user_query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logData)
            });

            // 設置超時，避免阻塞
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Log timeout')), 1000)
            );

            await Promise.race([logPromise, timeoutPromise]);
        } catch (error) {
            // 日誌記錄失敗不影響主要功能
            console.warn('Failed to log user query:', error);
        }
    }

    // 新增：獲取當前 observation_id（如果有的話）
    getCurrentObservationId() {
        // 這裡可以從全局狀態或其他地方獲取當前的 observation_id
        // 暫時返回 null，後續可以實現關聯邏輯
        return null;
    }
    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/state`);
            this.isConnected = response.ok;
        } catch (error) {
            this.isConnected = false;
        }
        
        this.updateConnectionStatus();
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('connectionStatus');
        
        if (this.isConnected) {
            statusElement.className = 'status-indicator status-connected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
        } else {
            statusElement.className = 'status-indicator status-disconnected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
        }
    }

    async loadCapabilities() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/state/query/capabilities`);
            if (response.ok) {
                const data = await response.json();
                console.log('Query capabilities loaded:', data.capabilities);
            }
        } catch (error) {
            console.warn('Could not load query capabilities:', error);
        }
    }

    async processQuery() {
        const queryInput = document.getElementById('queryInput');
        const query = queryInput.value.trim();

        if (!query) {
            this.showError('Please enter a query');
            return;
        }

        if (!this.isConnected) {
            this.showError('Not connected to backend. Please check if the server is running.');
            return;
        }

        // 生成唯一ID
        const queryId = this.generateQueryId();
        const requestId = this.generateRequestId();
        const flowId = this.generateFlowId();

        // 記錄使用者查詢日誌
        this.logUserQuery(query, queryId, requestId);

        this.showLoading();
        
        try {
            const startTime = performance.now();
            
            // 新增：生成 query_id
            const query_id = this.generateQueryId();
            
            // 新增：異步記錄使用者查詢（不等待完成）
            this.logUserQuery(query_id, query);
            
            // 修改：發送查詢時包含 query_id
            const response = await fetch(`${this.apiBaseUrl}/state/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    query_id: query_id  // 新增：傳送 query_id
                })
            });

            const endTime = performance.now();
            const totalTime = Math.round(endTime - startTime);

            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = `Server error: ${response.status}`;
                
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    errorMessage = errorText || errorMessage;
                }
                
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Validate response data
            if (!data || typeof data.response !== 'string') {
                throw new Error('Invalid response format from server');
            }
            
            this.showResponse(data, totalTime);

        } catch (error) {
            console.error('Query processing error:', error);
            
            // Provide more specific error messages
            let errorMessage = error.message;
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage = 'Network error: Unable to connect to server. Please check your connection.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Connection failed: Server may be down or unreachable.';
            }
            
            this.showError(errorMessage);
        }
    }

    showLoading() {
        const responseText = document.getElementById('responseText');
        const responseMeta = document.getElementById('responseMeta');
        const loading = document.querySelector('.loading');

        responseText.style.display = 'none';
        responseMeta.style.display = 'none';
        loading.style.display = 'flex';

        // Disable query button
        document.getElementById('queryButton').disabled = true;
    }

    showResponse(data, totalTime) {
        const responseText = document.getElementById('responseText');
        const responseMeta = document.getElementById('responseMeta');
        const loading = document.querySelector('.loading');

        // Hide loading
        loading.style.display = 'none';

        // Show response with proper formatting
        responseText.innerHTML = data.response.replace(/\n/g, '<br>');
        responseText.style.display = 'block';

        // Show metadata
        document.getElementById('processingTime').textContent = data.processing_time_ms.toFixed(1);
        document.getElementById('queryType').textContent = data.query_type.replace('_', ' ');
        document.getElementById('confidence').textContent = Math.round(data.confidence * 100);
        responseMeta.style.display = 'flex';

        // Re-enable query button
        document.getElementById('queryButton').disabled = false;

        // Log performance
        console.log(`Query processed in ${data.processing_time_ms.toFixed(1)}ms (total: ${totalTime}ms)`);
    }

    showError(message) {
        const responseText = document.getElementById('responseText');
        const responseMeta = document.getElementById('responseMeta');
        const loading = document.querySelector('.loading');

        // Hide loading
        loading.style.display = 'none';

        // Show error
        responseText.innerHTML = `<span style="color: var(--error)"><i class="fas fa-exclamation-triangle"></i> ${message}</span>`;
        responseText.style.display = 'block';

        // Hide metadata
        responseMeta.style.display = 'none';

        // Re-enable query button
        document.getElementById('queryButton').disabled = false;
    }

    // Utility method to test the system
    async runPerformanceTest() {
        const testQueries = [
            '我在哪個步驟？',
            '下一步是什麼？',
            '需要什麼工具？',
            'current step',
            'next step'
        ];

        console.log('Running performance test...');
        const results = [];

        for (const query of testQueries) {
            try {
                const startTime = performance.now();
                
                const response = await fetch(`${this.apiBaseUrl}/state/query`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                const endTime = performance.now();
                const data = await response.json();

                results.push({
                    query: query,
                    processing_time: data.processing_time_ms,
                    total_time: endTime - startTime,
                    query_type: data.query_type,
                    confidence: data.confidence
                });

            } catch (error) {
                console.error(`Test failed for query "${query}":`, error);
            }
        }

        console.table(results);
        return results;
    }
}

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.stateQuerySystem = new StateQuerySystem();
    
    // Add performance test to global scope for debugging
    window.runPerformanceTest = () => window.stateQuerySystem.runPerformanceTest();
});

// Auto-refresh connection status every 30 seconds
setInterval(() => {
    if (window.stateQuerySystem) {
        window.stateQuerySystem.checkConnection();
    }
}, 30000);