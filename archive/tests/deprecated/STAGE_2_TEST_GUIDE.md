# Stage 2 Integrated Tests Guide

## 🚀 Quick Start

### Option 1: Mock Mode (Structure Testing)
```bash
# From tests directory
python stage_2_integrated_tests.py
```
This will run in mock mode, testing the test structure without requiring full dependencies.

### Option 2: Full Mode (Real Testing)
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run from project root
cd /Users/ytzzzz/Documents/destination_code
python tests/stage_2_integrated_tests.py
```

## 🔧 Test Structure

The test file includes four main test categories:

### Task 2.1: Core State Tracker
- Tests VLM response processing
- Validates state updates
- Checks confidence scoring

### Task 2.2: Intelligent Matching and Fault Tolerance
- Tests various input types
- Validates error handling
- Checks processing metrics

### Task 2.3: Sliding Window Memory Management
- Tests memory usage limits
- Validates cleanup operations
- Checks sliding window functionality

### Task 2.4: Instant Response Whiteboard Mechanism
- Tests query type identification
- Validates response generation
- Checks multilingual support

## 📊 Expected Results

### Mock Mode Results
- All tests will pass with simulated data
- Results marked as "MOCK" mode
- Used for structure validation only

### Full Mode Results
- Real system testing with actual StateTracker
- Performance metrics and actual data
- Comprehensive validation of all features

## 🚨 Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'src'`:
1. Ensure you're running from the correct directory
2. Check that PYTHONPATH includes the src directory
3. Verify virtual environment is activated

### Missing Dependencies
If you see `ModuleNotFoundError: No module named 'chromadb'`:
1. Activate virtual environment: `source ai_vision_env/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Verify all dependencies are installed

### Test Failures
If tests fail in full mode:
1. Check that backend services are running
2. Verify StateTracker is properly initialized
3. Check system resources (memory, etc.)

## 📈 Performance Expectations

### Memory Usage
- Task 2.3 should maintain memory usage under 1MB
- Sliding window should limit records to ≤10
- Cleanup operations should occur regularly

### Response Times
- Task 2.1: VLM processing < 100ms
- Task 2.4: Query processing < 50ms
- Overall test suite: < 30 seconds

### Success Rates
- Task 2.1: ≥ 60% successful state updates
- Task 2.2: ≥ 75% successful processing
- Task 2.4: ≥ 70% correct query identification

## 🔄 Continuous Integration

For CI/CD environments:
```bash
# Run in headless mode
python tests/stage_2_integrated_tests.py > test_results.log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "Stage 2 tests passed"
else
    echo "Stage 2 tests failed"
    exit 1
fi
```

## 📝 Test Results

Results are automatically saved to `stage_2_integrated_results.json` with:
- Individual test status
- Performance metrics
- Detailed statistics
- Mode information (mock/full)

---

**Last Updated**: January 2025
**Status**: ✅ **Test Structure Validated** 