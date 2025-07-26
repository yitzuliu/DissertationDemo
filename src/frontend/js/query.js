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

        this.showLoading();
        
        try {
            const startTime = performance.now();
            
            const response = await fetch(`${this.apiBaseUrl}/state/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const endTime = performance.now();
            const totalTime = Math.round(endTime - startTime);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.showResponse(data, totalTime);

        } catch (error) {
            console.error('Query processing error:', error);
            this.showError(`Error: ${error.message}`);
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

        // Show response
        responseText.textContent = data.response;
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