# AI Manual Assistant - Test Suite

This directory contains comprehensive tests for the AI Manual Assistant system, organized by functionality and development stages.

## 📁 Test Structure

```
tests/
├── README.md                           # This file
├── test_backend_api.py                 # Backend API endpoint tests
├── test_stage_1_3.py                   # Vector optimization tests
├── stage_2_integrated_tests.py         # Combined Stage 2 tests
├── test_task_knowledge.py              # Task knowledge system tests
├── stage_3_1/                          # Service startup and communication tests
├── stage_3_2/                          # Dual loop coordination tests
├── stage_3_3/                          # Cross-service functionality tests
└── logging_system_tests/               # Logging system validation tests
    ├── unified_logging_tests.py        # Combined logging tests (NEW)
    ├── performance_test.py             # Performance benchmarking
    ├── end_to_end_test.py              # End-to-end validation
    └── [other logging tests]           # Individual logging tests
```

## 🧪 Test Categories

### **Core System Tests**
- **`test_backend_api.py`**: Tests all backend API endpoints
- **`test_task_knowledge.py`**: Validates task knowledge data and loading
- **`test_stage_1_3.py`**: Vector optimization and caching tests

### **Stage 2 Tests (State Management)**
- **`stage_2_integrated_tests.py`**: Combined Stage 2 tests including:
  - Task 2.1: Core State Tracker
  - Task 2.2: Intelligent Matching and Fault Tolerance
  - Task 2.3: Sliding Window Memory Management
  - Task 2.4: Instant Response Whiteboard Mechanism

### **Stage 3 Tests (Service Integration)**
- **`stage_3_1/`**: Service startup, communication, and sequence tests
- **`stage_3_2/`**: Dual loop coordination between services
- **`stage_3_3/`**: Cross-service functionality and recovery tests

### **System Validation Tests**
- **`logging_system_tests/`**: Comprehensive logging system validation
  - **`unified_logging_tests.py`**: Combined logging tests (end-to-end, performance, stage-specific)
  - **`performance_test.py`**: Performance benchmarking
  - **`end_to_end_test.py`**: End-to-end validation

## 🚀 Quick Start

### Running Individual Tests

```bash
# Backend API tests
python test_backend_api.py

# Task knowledge validation
python test_task_knowledge.py

# Vector optimization tests
python test_stage_1_3.py

# Stage 2 integrated tests
python stage_2_integrated_tests.py
```

### Running Stage 3 Tests

```bash
# Stage 3.1 - Service startup tests
cd stage_3_1/
python run_stage_3_1_tests.py

# Stage 3.2 - Dual loop coordination
cd stage_3_2/
python test_dual_loop_coordination.py

# Stage 3.3 - Cross-service functionality
cd stage_3_3/
python test_stage_3_3_final.py
```

### Running Logging Tests

```bash
cd logging_system_tests/
# Unified logging tests (recommended)
python unified_logging_tests.py

# Individual logging tests
python end_to_end_test.py
python performance_test.py
```

## 📊 Test Results

### Expected Outcomes

#### **Core System Tests**
- **Backend API**: All endpoints respond correctly
- **Task Knowledge**: Coffee brewing task loads and validates properly
- **Vector Optimization**: Precomputed embeddings work efficiently

#### **Stage 2 Tests**
- **State Tracker**: Successfully processes VLM responses
- **Intelligent Matching**: Handles various input types with fault tolerance
- **Memory Management**: Sliding window keeps memory usage under limits
- **Instant Response**: Correctly identifies and responds to user queries

#### **Stage 3 Tests**
- **Service Startup**: All services start and communicate properly
- **Dual Loop**: Model observation and frontend queries work together
- **Cross-Service**: End-to-end functionality with recovery mechanisms

## 🔧 Test Configuration

### Prerequisites
- Python 3.11+ with virtual environment activated
- All required dependencies installed
- Backend services available (for integration tests)

### Environment Setup
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Set up test environment
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Test Data
- Coffee brewing task data in `data/tasks/coffee_brewing.yaml`
- Test images in `data/test_images/`
- Log files in `logs/` directory

## 📈 Performance Benchmarks

### Memory Usage Targets
- **Stage 2 Memory Management**: < 1MB sliding window
- **Vector Cache**: Efficient precomputed embeddings
- **Service Memory**: Stable memory usage during operation

### Response Time Targets
- **API Endpoints**: < 100ms for simple queries
- **State Updates**: < 50ms for VLM response processing
- **Cross-Service**: < 200ms end-to-end response

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=$PYTHONPATH:$(pwd)/src
   ```

2. **Service Not Available**
   ```bash
   # Start required services first
   python src/backend/main.py &
   python src/models/smolvlm/run_smolvlm.py &
   ```

3. **Test Data Missing**
   ```bash
   # Check if test data exists
   ls -la data/tasks/coffee_brewing.yaml
   ls -la data/test_images/
   ```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python stage_2_integrated_tests.py
```

## 📋 Test Maintenance

### Adding New Tests
1. Create test file in appropriate directory
2. Follow naming convention: `test_*.py`
3. Include comprehensive docstring
4. Add to this README if needed

### Updating Tests
- Keep tests synchronized with code changes
- Update expected results when functionality changes
- Maintain backward compatibility when possible

### Test Data Management
- Keep test data minimal and focused
- Use realistic but simple test cases
- Document any special test data requirements

## 🔄 Recent Changes

### **January 2025 - Test Suite Cleanup**
- **✅ Removed Duplicates**: Deleted redundant Stage 3.3 test files
- **✅ Merged Stage 2**: Combined all Stage 2 tests into single file
- **✅ Cleaned Structure**: Removed empty directories and cache files
- **✅ Improved Organization**: Better file organization and documentation

### **Deleted Files**
- `stage_3_3/test_stage_3_3_complete_comprehensive.py` (1597 lines)
- `stage_3_3/test_simulated_steps.py` (708 lines)
- `test_stage_2_integration.py` (merged into `stage_2_integrated_tests.py`)
- `stage_3_1/quick_test.py` (merged into `run_stage_3_1_tests.py`)
- `stage_2_1/`, `stage_2_2/`, `stage_2_3/`, `stage_2_4/` (merged into `stage_2_integrated_tests.py`)
- Empty directories: `integration_tests/`, `memory_system_tests/`
- All `__pycache__/` directories

### **New Files**
- `stage_2_integrated_tests.py`: Combined Stage 2 test suite
- `logging_system_tests/unified_logging_tests.py`: Combined logging test suite
- `README.md`: This comprehensive test documentation

---

**For detailed test results and reports, check the individual test directories and their README files.**

**Last Updated**: January 2025 | **Status**: ✅ **Test Suite Cleaned & Organized** 