# AI Manual Assistant - Getting Started Guide

This guide helps new users quickly get up and running with the AI Manual Assistant project.

## 🚀 Quick Start for New Users

### 1. First Steps
1. **Setup Development Environment**: Follow the [Developer Setup Guide](./docs/DEVELOPER_SETUP.md)
2. **Understand the System**: Read the [System Architecture](./docs/ARCHITECTURE.md)
3. **Choose Your Model**: Check the [Model Comparison Guide](./docs/MODEL_COMPARISON.md)
4. **Review Latest Results**: See [Test Results Summary](./TEST_RESULTS_SUMMARY.md)

### 2. Advanced Configuration
- **Integration Planning**: Review [RAG & State Tracker Integration](./docs/RAG_STATE_TRACKER_INTEGRATION_APPROACHES.md)
- **Model Optimization**: Follow the [VLM Enhancement Guide](./docs/VLM_ENHANCEMENT_GUIDE.md)

## 📚 Complete Documentation

### System Documentation (`/docs`)
- **[System Architecture](./docs/ARCHITECTURE.md)** - Complete system design and component overview
- **[Developer Setup Guide](./docs/DEVELOPER_SETUP.md)** - Step-by-step development environment setup
- **[Model Comparison Guide](./docs/MODEL_COMPARISON.md)** - Detailed comparison of all supported models
- **[API Documentation](./docs/API.md)** - Complete API reference and examples
- **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[FAQ](./docs/FAQ.md)** - Frequently asked questions
- **[RAG & State Tracker Integration](./docs/RAG_STATE_TRACKER_INTEGRATION_APPROACHES.md)** - Three approaches for integrating RAG and State Tracker
- **[VLM Enhancement Guide](./docs/VLM_ENHANCEMENT_GUIDE.md)** - Optimization guide for vision models

### Project Status
- **[Test Results Summary](./TEST_RESULTS_SUMMARY.md)** - Latest VQA 2.0 performance results

## 🔧 Development Resources

### Configuration Files
- `src/config/app_config.json` - Main application configuration
- `src/config/model_configs/` - Individual model configurations
- `src/models/README.md` - Model structure overview

### Testing Framework
- `src/testing/` - Comprehensive VQA 2.0 testing framework
- `TEST_RESULTS_SUMMARY.md` - Latest performance benchmarks

### Troubleshooting
- **Issues**: Check [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
- **Common Questions**: See [FAQ](./docs/FAQ.md)
- **API Problems**: Refer to [API Documentation](./docs/API.md)

## 📊 Project Status

The AI Manual Assistant is actively developed with:
- ✅ **Working 3-layer architecture** (Frontend, Backend, Model Server)
- ✅ **Multiple VLM support** with hot-swapping capabilities
- ✅ **Comprehensive testing framework** (VQA 2.0 compliant)
- ✅ **Performance optimization** for Apple Silicon
- ✅ **Dual-loop memory system** (Subconscious + Instant Response loops)
- ✅ **RAG knowledge base** with intelligent vector search
- ✅ **State Tracker** with 100% query classification accuracy
- ✅ **Service communication validation** with 100% success rate
- ✅ **High-priority fixes** (frontend format, query classification, error handling)
- 🔄 **Static image testing** (Stage 4.5 - next priority)

## 🧠 **Dual-Loop Memory System**

The AI Manual Assistant features a revolutionary dual-loop memory system:

### **🔄 Subconscious Loop (Background)**
- Continuous VLM observation of your workspace
- Automatic state tracking and progress monitoring
- RAG knowledge base matching for step identification
- Sliding window memory management

### **⚡ Instant Response Loop (On-Demand)**
- Immediate answers to user queries (< 50ms)
- Direct state lookup without re-processing
- Intelligent query classification (100% accuracy)
- Detailed tool lists and step information

### **🎯 Key Features**
- **Query Types Supported**: "What step am I on?", "What tools do I need?", "How much progress?", "Help me with this step"
- **Response Quality**: Complete information including tools, descriptions, time estimates, safety notes
- **System Language**: Fully English-based for consistency
- **Performance**: 100% success rate, < 50ms response time

## 🚀 **Quick Start Commands**

### **1. Start the System**
```bash
# Activate virtual environment
source ai_vision_env/bin/activate

# Start Model Server (choose one)
cd src/models/smolvlm
python run_smolvlm.py

# Start Backend Server (new terminal)
cd src/backend
python main.py

# Start Frontend Server (new terminal)
cd src/frontend
python -m http.server 5500
```

### **2. Access Interfaces**
- **Main Interface**: `http://localhost:5500` - Camera-based VLM interaction
- **Query Interface**: `http://localhost:5500/query.html` - State tracking queries

### **3. Test the System**
```bash
# Run comprehensive tests
python tests/stage_3_3/test_stage_3_3_final.py

# Test specific components
python tests/test_backend_api.py
python tests/stage_3_3/test_simulated_steps.py
```

## 🎯 **Current Development Stage**

### **✅ Completed Stages**
- **Stage 1**: RAG Knowledge Base (3/3 tasks)
- **Stage 2**: State Tracker Dual-Loop System (4/4 tasks)
- **Stage 3**: Service Integration & Testing (3/3 tasks)
- **Stage 3.5**: High-Priority Fixes (3/3 tasks)

### **🚧 Current Priority: Stage 4.5**
- **Static Image Testing System**
  - Implement test framework for static images
  - Prepare coffee brewing test image set
  - Validate system accuracy with static images

### **📋 Future Stages**
- **Stage 5**: Demo Integration and Visualization
- **Stage 4.1-4.3**: Performance Monitoring and Optimization

## 🔍 **Testing Results**

### **Performance Metrics**
- **Dual-Loop Success Rate**: 100%
- **Query Classification Accuracy**: 100%
- **Service Communication**: 100% success
- **Response Time**: < 50ms for instant queries
- **Memory Usage**: Optimized sliding window < 1MB
- **Error Recovery**: 100% recovery rate

### **Test Coverage**
- **Service Startup**: 6/6 tests passed
- **Dual-Loop Coordination**: 6/6 tests passed
- **Cross-Service Functionality**: 4/4 tests passed
- **Simulated Steps**: 3/3 steps 100% accurate
- **Query Classification**: 17/17 query types 100% accurate

## 🛠️ **Troubleshooting**

### **Common Issues**
1. **Model Server Not Starting**: Check virtual environment and dependencies
2. **Frontend Connection Errors**: Ensure all three services are running
3. **Query Response Issues**: Verify State Tracker and RAG are loaded

### **Quick Diagnostics**
```bash
# Check all services
python tests/stage_3_1/quick_test.py

# Test specific functionality
python tests/stage_3_3/test_stage_3_3_final.py
```

## 📈 **What's New**

### **Latest Updates**
- ✅ **Dual-loop memory system** fully operational
- ✅ **Query classification** with 100% accuracy
- ✅ **Service communication** validated
- ✅ **High-priority fixes** completed
- ✅ **English language** standardization
- ✅ **Detailed response content** with tools and safety notes

### **Key Improvements**
- **Frontend Response Format**: Fixed newline display and formatting
- **Query Classification**: Refined regex patterns for 100% accuracy
- **Error Handling**: Enhanced user-friendly error messages
- **System Stability**: Robust fault tolerance and recovery

For the latest updates and ongoing work, see the project's GitHub repository and stage completion reports.