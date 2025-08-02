# State Tracker User Guide

## 📋 Overview

The State Tracker is the core component of the AI Manual Assistant, responsible for **intelligently tracking user task progress** and providing **instant status queries**. It works like an intelligent assistant that can:

- 🎯 **Automatically identify** the current task step you're executing
- 💾 **Remember** your task progress and historical states
- ⚡ **Instantly respond** to your status queries (millisecond-level response)
- 🛡️ **Intelligently filter** inaccurate observations to ensure state accuracy

## 🏗️ System Architecture

### **Dual-Loop Design**

```
🔄 Unconscious Loop (continuously running)
VLM Observation → Intelligent Matching → State Update → Memory Storage

⚡ Instant Response Loop (triggered on demand)  
User Query → Direct Read → Instant Response
```

### **Core Components**

- **State Tracker**: Main controller that coordinates all functions
- **RAG Knowledge Base**: Task knowledge matching engine
- **Query Processor**: Intelligent query processor
- **Sliding Window Memory**: Efficient state storage system

## 🎯 Main Features

### **1. Automatic State Tracking**

The State Tracker automatically:
- Receives VLM visual observations
- Performs intelligent matching with task knowledge base
- Evaluates matching confidence
- Updates current task state

**Example Scenario:**
```
VLM Observation: "User is grinding coffee beans"
↓
State Tracker Match: Coffee brewing task - Step 3
↓
Update State: Currently on step 3 of coffee brewing task
```

### **2. Intelligent Confidence Assessment**

The system uses a three-tier confidence assessment:

| Confidence | Score Range | Update Strategy |
|------------|-------------|-----------------|
| 🟢 **High** | ≥ 0.70 | Direct state update |
| 🟡 **Medium** | 0.40-0.69 | Update after consistency check |
| 🔴 **Low** | < 0.40 | Don't update, wait for better match |

### **3. Instant Query Response**

Supports multiple query types:

#### **Basic Queries**
- **Current Step**: "What step am I on?", "What am I doing now?"
- **Next Step**: "What's next?", "What's the next step?"
- **Required Tools**: "What tools do I need?", "What equipment should I use?"

#### **Progress Queries**
- **Completion Status**: "How much is done?", "How much is left?"
- **Progress Overview**: "How's the overall progress?", "What's the task overview?"

#### **Help Queries**
- **Operation Guidance**: "How do I do this?", "I need help"

## 🚀 Usage

### **1. System Startup**

The State Tracker automatically initializes when the system starts:

```python
# Automatic initialization
state_tracker = StateTracker()
# Load RAG knowledge base
# Prepare query processor
# Start sliding window memory
```

### **2. Automatic State Tracking**

No manual operation required, the system automatically:

```python
# Receive VLM observation
await state_tracker.process_vlm_response(vlm_text)

# Automatically executes:
# 1. Text cleaning
# 2. RAG matching
# 3. Confidence assessment
# 4. State update
```

### **3. Query Response**

Users can ask questions at any time:

```python
# User query
response = await state_tracker.query("What step am I on?")

# Response format
{
  "status": "success",
  "response_text": "You are currently on step 3 of the coffee brewing task",
  "query_type": "CURRENT_STEP",
  "confidence": 0.85,
  "processing_time_ms": 45
}
```

## 🔧 Technical Details

### **Memory Management**

The system uses a sliding window memory approach:

```python
# Memory structure
{
  "current_state": {
    "task_name": "coffee_brewing",
    "current_step": 3,
    "confidence": 0.85,
    "timestamp": "2025-02-08T10:30:00Z"
  },
  "history": [
    # Last 10 state changes
  ],
  "metadata": {
    "total_queries": 150,
    "average_confidence": 0.78
  }
}
```

### **RAG Integration**

The system integrates with RAG for intelligent matching:

```python
# RAG matching process
def match_task_knowledge(observation):
    # 1. Text preprocessing
    cleaned_text = preprocess_text(observation)
    
    # 2. Vector search
    matches = rag_search(cleaned_text)
    
    # 3. Confidence calculation
    confidence = calculate_confidence(matches)
    
    # 4. State determination
    return determine_state(matches, confidence)
```

### **Performance Optimization**

- **Caching**: Frequently accessed states are cached
- **Parallel Processing**: Multiple queries processed concurrently
- **Memory Optimization**: Efficient memory usage with sliding window
- **Response Time**: <100ms for most queries

## 📊 Monitoring and Analytics

### **Performance Metrics**

The system tracks various performance metrics:

- **Response Time**: Average query response time
- **Confidence Distribution**: Distribution of confidence scores
- **Query Volume**: Number of queries per time period
- **Error Rate**: Rate of failed queries or updates

### **Health Monitoring**

```python
# System health check
health_status = state_tracker.get_health_status()

{
  "status": "healthy",
  "memory_usage": "45%",
  "response_time_avg": "67ms",
  "confidence_avg": "0.82",
  "last_update": "2025-02-08T10:30:00Z"
}
```

## 🛠️ Configuration

### **System Settings**

The State Tracker can be configured through configuration files:

```json
{
  "state_tracker": {
    "confidence_threshold": 0.40,
    "memory_window_size": 10,
    "max_response_time_ms": 100,
    "enable_caching": true,
    "cache_ttl_seconds": 300
  }
}
```

### **RAG Configuration**

```json
{
  "rag": {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "similarity_threshold": 0.7,
    "max_results": 5,
    "enable_semantic_search": true
  }
}
```

## 🔍 Troubleshooting

### **Common Issues**

#### Issue: Low Confidence Scores
**Symptoms**: Most queries return low confidence (<0.4)
**Solutions**:
- Check RAG knowledge base quality
- Verify task knowledge is up to date
- Review VLM observation quality

#### Issue: Slow Response Times
**Symptoms**: Query response time >100ms
**Solutions**:
- Check system resource usage
- Verify RAG service performance
- Review caching configuration

#### Issue: Inconsistent States
**Symptoms**: State changes unexpectedly or incorrectly
**Solutions**:
- Review confidence threshold settings
- Check VLM observation consistency
- Verify task knowledge accuracy

### **Debugging Tools**

```python
# Enable debug mode
state_tracker.enable_debug_mode()

# Get detailed logs
logs = state_tracker.get_debug_logs()

# Check internal state
internal_state = state_tracker.get_internal_state()
```

## 📈 Best Practices

### **For Users**

1. **Ask Clear Questions**: Be specific about what you want to know
2. **Provide Context**: Include relevant task information in queries
3. **Be Patient**: Complex queries may take a moment to process

### **For Developers**

1. **Monitor Performance**: Regularly check response times and confidence scores
2. **Update Knowledge Base**: Keep task knowledge current and accurate
3. **Test Edge Cases**: Regularly test with unusual queries or states

### **For Administrators**

1. **System Monitoring**: Monitor system health and performance metrics
2. **Configuration Management**: Regularly review and optimize settings
3. **Backup and Recovery**: Ensure proper backup of state data

## 🔮 Future Enhancements

### **Planned Features**

- **Multi-task Support**: Support for multiple concurrent tasks
- **Advanced Analytics**: Detailed usage analytics and insights
- **Custom Confidence Models**: User-defined confidence calculation
- **Integration APIs**: APIs for external system integration

### **Performance Improvements**

- **Advanced Caching**: Intelligent caching with predictive loading
- **Distributed Processing**: Support for distributed state tracking
- **Real-time Updates**: WebSocket-based real-time state updates
- **Mobile Optimization**: Optimized for mobile device usage

## 📞 Support

### **Getting Help**

1. **Check Documentation**: Review this guide and related documentation
2. **Run Diagnostics**: Use built-in diagnostic tools
3. **Check Logs**: Review system logs for error information
4. **Contact Support**: Reach out to the development team

### **Maintenance Schedule**

- **Daily**: Monitor system performance and error rates
- **Weekly**: Review usage analytics and optimize settings
- **Monthly**: Update knowledge base and test edge cases
- **Quarterly**: Comprehensive system review and optimization

---

**Last Updated**: August 2, 2025  
**Version**: 2.0 (VLM System Integration)  
**Maintainer**: AI Vision Intelligence Hub Team 