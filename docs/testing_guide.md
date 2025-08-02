# Testing Guide

## 📋 Overview

This guide provides comprehensive testing procedures and validation methods for the AI Vision Intelligence Hub. It covers unit testing, integration testing, performance testing, and end-to-end validation to ensure system reliability and functionality.

### **Testing Philosophy**
- 🧪 **Comprehensive Coverage**: Test all system components and interactions
- 🔄 **Continuous Validation**: Automated testing throughout development
- 📊 **Performance Monitoring**: Track system performance and metrics
- 🛡️ **Quality Assurance**: Ensure reliability and error handling
- 🎯 **User-Centric**: Validate user experience and functionality

## 🏗️ Testing Architecture

### **Testing Pyramid**

```
                    ┌─────────────────┐
                    │   E2E Tests     │
                    │   (Few, Slow)   │
                    └─────────────────┘
                           │
                    ┌─────────────────┐
                    │ Integration     │
                    │ Tests           │
                    │ (Some, Medium)  │
                    └─────────────────┘
                           │
                    ┌─────────────────┐
                    │   Unit Tests    │
                    │ (Many, Fast)    │
                    └─────────────────┘
```

### **Test Categories**

#### **Unit Tests**
- **Purpose**: Test individual components in isolation
- **Scope**: Functions, classes, modules
- **Speed**: Fast execution (<1 second per test)
- **Frequency**: Run on every code change

#### **Integration Tests**
- **Purpose**: Test component interactions
- **Scope**: Service communication, API endpoints
- **Speed**: Medium execution (1-10 seconds per test)
- **Frequency**: Run on feature completion

#### **End-to-End Tests**
- **Purpose**: Test complete user workflows
- **Scope**: Full system functionality
- **Speed**: Slow execution (10-60 seconds per test)
- **Frequency**: Run before releases

## 🧪 Unit Testing

### **Backend Unit Tests**

#### **State Tracker Tests**
```python
# test_state_tracker.py
import pytest
from src.state_tracker.state_tracker import StateTracker

class TestStateTracker:
    def setup_method(self):
        self.state_tracker = StateTracker()
    
    def test_state_initialization(self):
        """Test state tracker initialization"""
        assert self.state_tracker.current_state is None
        assert self.state_tracker.confidence == 0.0
    
    def test_state_update(self):
        """Test state update functionality"""
        test_state = {
            "task_name": "coffee_brewing",
            "current_step": 3,
            "confidence": 0.85
        }
        
        self.state_tracker.update_state(test_state)
        
        assert self.state_tracker.current_state["task_name"] == "coffee_brewing"
        assert self.state_tracker.current_state["current_step"] == 3
        assert self.state_tracker.confidence == 0.85
    
    def test_query_processing(self):
        """Test query processing"""
        query = "What step am I on?"
        response = self.state_tracker.process_query(query)
        
        assert response["status"] == "success"
        assert "response_text" in response
        assert "processing_time_ms" in response
```

#### **RAG System Tests**
```python
# test_rag_system.py
import pytest
from src.memory.rag.knowledge_base import RAGKnowledgeBase

class TestRAGSystem:
    def setup_method(self):
        self.rag_system = RAGKnowledgeBase()
    
    def test_knowledge_loading(self):
        """Test task knowledge loading"""
        tasks = self.rag_system.load_tasks()
        
        assert len(tasks) > 0
        assert "coffee_brewing" in tasks
    
    def test_vector_search(self):
        """Test vector search functionality"""
        query = "grinding coffee beans"
        results = self.rag_system.search(query, top_k=5)
        
        assert len(results) <= 5
        assert all("similarity" in result for result in results)
        assert all("task_name" in result for result in results)
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        matches = [
            {"similarity": 0.9, "task_name": "coffee_brewing"},
            {"similarity": 0.7, "task_name": "coffee_brewing"}
        ]
        
        confidence = self.rag_system.calculate_confidence(matches)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high for good matches
```

### **Frontend Unit Tests**

#### **Component Tests**
```javascript
// test_camera_component.js
import { render, fireEvent } from '@testing-library/react';
import CameraComponent from '../components/CameraComponent';

describe('CameraComponent', () => {
    test('renders camera interface', () => {
        const { getByTestId } = render(<CameraComponent />);
        
        expect(getByTestId('camera-interface')).toBeInTheDocument();
        expect(getByTestId('capture-button')).toBeInTheDocument();
    });
    
    test('handles image capture', async () => {
        const mockOnCapture = jest.fn();
        const { getByTestId } = render(
            <CameraComponent onCapture={mockOnCapture} />
        );
        
        fireEvent.click(getByTestId('capture-button'));
        
        expect(mockOnCapture).toHaveBeenCalled();
    });
    
    test('displays error message on camera failure', () => {
        const { getByTestId } = render(
            <CameraComponent hasError={true} />
        );
        
        expect(getByTestId('error-message')).toBeInTheDocument();
    });
});
```

#### **API Client Tests**
```javascript
// test_api_client.js
import { APIClient } from '../utils/api-client';

describe('APIClient', () => {
    beforeEach(() => {
        fetch.resetMocks();
    });
    
    test('sends state query successfully', async () => {
        const mockResponse = {
            status: 'success',
            response_text: 'You are on step 3',
            confidence: 0.85
        };
        
        fetch.mockResponseOnce(JSON.stringify(mockResponse));
        
        const client = new APIClient();
        const result = await client.queryState('What step am I on?');
        
        expect(result).toEqual(mockResponse);
        expect(fetch).toHaveBeenCalledWith(
            'http://localhost:8000/api/v1/state/query',
            expect.objectContaining({
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
        );
    });
    
    test('handles API errors gracefully', async () => {
        fetch.mockRejectOnce(new Error('Network error'));
        
        const client = new APIClient();
        
        await expect(client.queryState('test')).rejects.toThrow('Network error');
    });
});
```

## 🔄 Integration Testing

### **API Integration Tests**

#### **Backend API Tests**
```python
# test_backend_api.py
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

class TestBackendAPI:
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
    
    def test_state_query_endpoint(self):
        """Test state query endpoint"""
        query_data = {"query": "What step am I on?"}
        response = client.post("/api/v1/state/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "response_text" in data
        assert "confidence" in data
    
    def test_vlm_system_completion_endpoint(self):
    """Test VLM System completion endpoint with multi-model support"""
        completion_data = {
            "model": "moondream2",
            "messages": [
                {
                    "role": "user",
                    "content": "What do you see in this image?"
                }
            ]
        }
        response = client.post("/v1/chat/completions", json=completion_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
```

#### **Service Communication Tests**
```python
# test_service_communication.py
import pytest
import asyncio
from src.state_tracker.state_tracker import StateTracker
from src.memory.rag.knowledge_base import RAGKnowledgeBase

class TestServiceCommunication:
    @pytest.mark.asyncio
    async def test_state_tracker_rag_integration(self):
        """Test integration between state tracker and RAG system"""
        state_tracker = StateTracker()
        rag_system = RAGKnowledgeBase()
        
        # Simulate VLM observation
        vlm_observation = "User is grinding coffee beans"
        
        # Process through state tracker
        await state_tracker.process_vlm_response(vlm_observation)
        
        # Verify state was updated
        assert state_tracker.current_state is not None
        assert state_tracker.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_vlm_system_fallback_integration(self):
    """Test VLM System fallback integration with multi-model support"""
    from src.vlm_fallback.vlm_client import VLMClient
        
        vlm_client = VLMClient()
        
        # Test fallback query
        query = "Explain quantum physics"
        response = await vlm_client.process_query(query)
        
        assert response is not None
        assert "response_text" in response
        assert len(response["response_text"]) > 0
```

### **Frontend-Backend Integration Tests**

#### **End-to-End API Tests**
```javascript
// test_e2e_api.js
import { APIClient } from '../utils/api-client';

describe('E2E API Integration', () => {
    let apiClient;
    
    beforeEach(() => {
        apiClient = new APIClient('http://localhost:8000');
    });
    
    test('complete workflow: image capture to state query', async () => {
        // 1. Capture image
        const imageData = await captureTestImage();
        
        // 2. Send to VLM
        const vlmResponse = await apiClient.sendImage(imageData);
        expect(vlmResponse.status).toBe('success');
        
        // 3. Query state
        const stateResponse = await apiClient.queryState('What step am I on?');
        expect(stateResponse.status).toBe('success');
        expect(stateResponse.confidence).toBeGreaterThan(0.0);
    });
    
    test('error handling workflow', async () => {
        // Test with invalid data
        const invalidQuery = '';
        
        await expect(apiClient.queryState(invalidQuery))
            .rejects.toThrow('Invalid query');
    });
});
```

## 🎯 End-to-End Testing

### **Complete System Tests**

#### **Full Workflow Tests**
```python
# test_complete_system.py
import pytest
import asyncio
from src.backend.main import app
from fastapi.testclient import TestClient

class TestCompleteSystem:
    def setup_method(self):
        self.client = TestClient(app)
        self.test_image = self.load_test_image()
    
    def test_complete_user_workflow(self):
        """Test complete user workflow from start to finish"""
        # 1. System startup
        health_response = self.client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Image analysis
        image_data = {"image": self.test_image, "query": "What do you see?"}
        vlm_response = self.client.post("/v1/chat/completions", json=image_data)
        assert vlm_response.status_code == 200
        
        # 3. State tracking
        state_query = {"query": "What step am I on?"}
        state_response = self.client.post("/api/v1/state/query", json=state_query)
        assert state_response.status_code == 200
        
        # 4. Verify system consistency
        state_data = state_response.json()
        assert state_data["status"] == "success"
        assert "current_state" in state_data
    
    def test_error_recovery_workflow(self):
        """Test system error recovery"""
        # 1. Simulate service failure
        # 2. Verify graceful degradation
        # 3. Test recovery mechanisms
        pass
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        # 1. Send multiple concurrent requests
        # 2. Monitor response times
        # 3. Verify system stability
        pass
```

### **User Experience Tests**

#### **Frontend E2E Tests**
```javascript
// test_user_experience.js
import { render, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

describe('User Experience', () => {
    test('complete user journey', async () => {
        const { getByTestId, getByText } = render(<App />);
        
        // 1. User opens application
        expect(getByTestId('app-container')).toBeInTheDocument();
        
        // 2. User captures image
        fireEvent.click(getByTestId('capture-button'));
        await waitFor(() => {
            expect(getByTestId('image-preview')).toBeInTheDocument();
        });
        
        // 3. User asks question
        const queryInput = getByTestId('query-input');
        fireEvent.change(queryInput, { target: { value: 'What step am I on?' } });
        fireEvent.click(getByTestId('send-button'));
        
        // 4. User receives response
        await waitFor(() => {
            expect(getByTestId('response-container')).toBeInTheDocument();
        });
        
        // 5. Verify response quality
        const responseText = getByTestId('response-text').textContent;
        expect(responseText.length).toBeGreaterThan(0);
    });
    
    test('error handling user experience', async () => {
        const { getByTestId, getByText } = render(<App />);
        
        // Simulate network error
        // Verify user sees helpful error message
        // Verify user can retry operation
    });
});
```

## 📊 Performance Testing

### **Load Testing**

#### **Concurrent Request Testing**
```python
# test_performance.py
import asyncio
import time
import aiohttp
import pytest

class TestPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test system performance under concurrent load"""
        async def make_request(session, request_id):
            start_time = time.time()
            
            async with session.post(
                "http://localhost:8000/api/v1/state/query",
                json={"query": f"Test query {request_id}"}
            ) as response:
                await response.json()
            
            duration = time.time() - start_time
            return duration
        
        # Make 50 concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = [
                make_request(session, i) for i in range(50)
            ]
            durations = await asyncio.gather(*tasks)
        
        # Analyze performance
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        
        assert avg_duration < 0.1  # Average < 100ms
        assert max_duration < 0.5  # Max < 500ms
        assert all(d < 1.0 for d in durations)  # All < 1 second
```

#### **Memory Usage Testing**
```python
# test_memory_usage.py
import psutil
import os
import time

class TestMemoryUsage:
    def test_memory_efficiency(self):
        """Test memory usage efficiency"""
        process = psutil.Process(os.getpid())
        
        # Record initial memory
        initial_memory = process.memory_info().rss
        
        # Perform operations
        for i in range(100):
            # Simulate typical operations
            pass
        
        # Record final memory
        final_memory = process.memory_info().rss
        
        # Calculate memory increase
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage is reasonable
        assert memory_increase < 100 * 1024 * 1024  # < 100MB increase
```

### **Response Time Testing**

#### **Latency Testing**
```python
# test_latency.py
import time
import statistics
from src.backend.main import app
from fastapi.testclient import TestClient

class TestLatency:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_response_time_consistency(self):
        """Test response time consistency"""
        response_times = []
        
        for i in range(100):
            start_time = time.time()
            
            response = self.client.post(
                "/api/v1/state/query",
                json={"query": f"Test query {i}"}
            )
            
            end_time = time.time()
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times)
        
        # Verify performance requirements
        assert avg_time < 0.1  # Average < 100ms
        assert std_dev < 0.05  # Low variance
        assert max(response_times) < 0.2  # Max < 200ms
```

## 🛡️ Error Handling Tests

### **Fault Tolerance Testing**

#### **Service Failure Tests**
```python
# test_fault_tolerance.py
import pytest
from unittest.mock import patch

class TestFaultTolerance:
    def test_vlm_system_service_failure(self):
    """Test system behavior when VLM System service fails"""
    with patch('src.vlm_fallback.vlm_client.VLMClient.process_query') as mock_vlm:
            mock_vlm.side_effect = Exception("VLM service unavailable")
            
            # System should still function with fallback
            response = self.client.post(
                "/api/v1/state/query",
                json={"query": "What step am I on?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_database_connection_failure(self):
        """Test system behavior when database fails"""
        with patch('src.memory.rag.knowledge_base.RAGKnowledgeBase.search') as mock_search:
            mock_search.side_effect = Exception("Database connection failed")
            
            # System should handle gracefully
            response = self.client.post(
                "/api/v1/state/query",
                json={"query": "What step am I on?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
```

### **Input Validation Tests**

#### **Malformed Input Tests**
```python
# test_input_validation.py
class TestInputValidation:
    def test_invalid_query_format(self):
        """Test handling of invalid query formats"""
        invalid_queries = [
            "",  # Empty query
            None,  # Null query
            {"invalid": "format"},  # Wrong format
            "a" * 10000,  # Very long query
        ]
        
        for query in invalid_queries:
            response = self.client.post(
                "/api/v1/state/query",
                json={"query": query}
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400]
    
    def test_invalid_image_data(self):
        """Test handling of invalid image data"""
        invalid_images = [
            "",  # Empty image
            "not_base64",  # Invalid base64
            "data:image/jpeg;base64,invalid",  # Invalid base64
        ]
        
        for image in invalid_images:
            response = self.client.post(
                "/v1/chat/completions",
                json={"image": image}
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 400]
```

## 🔧 Test Automation

### **Continuous Integration**

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ --cov=src --cov-report=xml
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ --timeout=300
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### **Test Reporting**

#### **Coverage Reports**
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
```

## 📈 Test Metrics

### **Quality Metrics**

#### **Coverage Tracking**
```python
# test_metrics.py
class TestMetrics:
    def test_coverage_requirements(self):
        """Ensure adequate test coverage"""
        # Unit test coverage should be > 80%
        # Integration test coverage should be > 60%
        # E2E test coverage should be > 40%
        pass
    
    def test_performance_benchmarks(self):
        """Track performance benchmarks"""
        # Response time should be < 100ms average
        # Memory usage should be < 100MB
        # Throughput should be > 100 requests/second
        pass
```

### **Monitoring and Alerting**

#### **Test Result Monitoring**
```python
# test_monitoring.py
class TestMonitoring:
    def test_result_tracking(self):
        """Track test results over time"""
        # Record test results
        # Track trends
        # Alert on regressions
        pass
    
    def test_performance_tracking(self):
        """Track performance metrics"""
        # Record response times
        # Track memory usage
        # Monitor error rates
        pass
```

## 🔮 Future Testing Enhancements

### **Planned Improvements**

- **Automated Visual Testing**: Screenshot comparison and visual regression testing
- **Load Testing**: Automated load testing with realistic scenarios
- **Security Testing**: Automated security vulnerability scanning
- **Accessibility Testing**: Automated accessibility compliance testing
- **Mobile Testing**: Automated mobile device testing

### **Advanced Testing Features**

- **AI-Powered Testing**: Use AI to generate test cases
- **Predictive Testing**: Predict potential issues before they occur
- **Behavioral Testing**: Test system behavior under various conditions
- **Chaos Engineering**: Deliberately introduce failures to test resilience

---

**Last Updated**: August 2, 2025  
**Version**: 2.0 (VLM System Integration)  
**Maintainer**: AI Vision Intelligence Hub Team