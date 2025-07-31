# AI Manual Assistant Logging System Usage Guide

## 📋 Overview

The AI Manual Assistant logging system provides complete system tracking and analysis capabilities, including:

- **Unified Log Management**: Unified recording and management of multiple log types
- **Flow Tracking**: Complete end-to-end flow tracking
- **Performance Monitoring**: Real-time system performance monitoring
- **Anomaly Detection**: Automatic detection of system anomalies and issues
- **Analysis Tools**: Powerful log analysis and diagnostic tools

## 🏗️ System Architecture

### Core Components

1. **LogManager** (`src/logging/log_manager.py`)
   - Unified log manager
   - Unique ID generation
   - Multi-type log recording

2. **FlowTracker** (`src/logging/flow_tracker.py`)
   - Flow tracker
   - End-to-end flow management
   - Timeline recording

3. **LogAnalyzer** (`tools/log_analyzer.py`)
   - Log analysis tools
   - Event correlation analysis
   - Data integrity checking

4. **LogDiagnostics** (`tools/log_diagnostics.py`)
   - System diagnostic tools
   - Performance monitoring
   - Anomaly detection

### Log Types

- **System Logs** (`system_*.log`): System startup, shutdown, errors, etc.
- **Visual Logs** (`visual_*.log`): VLM processing, image capture, etc.
- **User Logs** (`user_*.log`): User queries, responses, etc.
- **Flow Tracking** (`flow_tracking_*.log`): Flow start, steps, end

## 🚀 Quick Start

### 1. Basic Usage

```python
from src.logging.log_manager import get_log_manager

# Get log manager
log_manager = get_log_manager()

# Log user query
query_id = log_manager.generate_query_id()
request_id = log_manager.generate_request_id()

log_manager.log_user_query(
    query_id=query_id,
    request_id=request_id,
    question="What tools do I need?",
    language="en"
)

# Log query classification
log_manager.log_query_classify(
    query_id=query_id,
    query_type="required_tools",
    confidence=0.95
)

# Log query response
log_manager.log_query_response(
    query_id=query_id,
    response="You need: filter paper, drip coffee maker, hot water, cup.",
    duration=1.2
)
```

### 2. Flow Tracking

```python
from src.logging.flow_tracker import get_flow_tracker, FlowType, FlowStep, FlowStatus

# Get flow tracker
flow_tracker = get_flow_tracker()

# Start flow
flow_id = flow_tracker.start_flow(
    FlowType.USER_QUERY,
    metadata={"user_id": "user123"}
)

# Add flow steps
flow_tracker.add_flow_step(
    flow_id=flow_id,
    step=FlowStep.QUERY_RECEIVED,
    related_ids={"query_id": query_id}
)

flow_tracker.add_flow_step(
    flow_id=flow_id,
    step=FlowStep.QUERY_CLASSIFICATION,
    related_ids={"query_id": query_id},
    metadata={"confidence": 0.95}
)

# End flow
flow_tracker.end_flow(
    flow_id=flow_id,
    status=FlowStatus.SUCCESS,
    final_metadata={"response_time": 1.2}
)
```

## 📊 Log Analysis

### 1. Basic Analysis

```bash
# Generate comprehensive report
python tools/log_analyzer.py --report-type comprehensive --output report.json

# Analyze specific time range
python tools/log_analyzer.py --start-time "2025-01-30 09:00:00" --end-time "2025-01-30 18:00:00"

# Analyze specific query
python tools/log_analyzer.py --query-id query_1234567890_abcdef12
```

### 2. System Diagnostics

```bash
# Run comprehensive diagnostics
python tools/log_diagnostics.py --diagnostic-type comprehensive --output diagnostics.json

# Check only VLM failures
python tools/log_diagnostics.py --diagnostic-type vlm

# Check query classification accuracy
python tools/log_diagnostics.py --diagnostic-type query
```

### 3. Programmatic Analysis

```python
from tools.log_analyzer import LogAnalyzer
from tools.log_diagnostics import LogDiagnostics

# Create analyzers
analyzer = LogAnalyzer("logs")
diagnostics = LogDiagnostics("logs")

# Analyze event flow
flow_analysis = analyzer.analyze_event_flow(query_id="query_123")
print(f"Event count: {flow_analysis['total_events']}")
print(f"Time span: {flow_analysis['time_span']} seconds")

# Check data integrity
integrity_report = analyzer.check_data_integrity()
print(f"Total queries: {integrity_report['total_queries']}")
print(f"Incomplete queries: {len(integrity_report['incomplete_queries'])}")

# Run diagnostics
diagnostics_report = diagnostics.run_comprehensive_diagnostics()
print(f"Overall status: {diagnostics_report['overall_status']}")
for recommendation in diagnostics_report['recommendations']:
    print(f"Recommendation: {recommendation}")
```

## 🔧 Configuration and Customization

### 1. Log Directory Configuration

```python
# Custom log directory
log_manager = get_log_manager("custom_logs")

# Analyze custom directory
analyzer = LogAnalyzer("custom_logs")
```

### 2. Diagnostic Threshold Adjustment

```python
from tools.log_diagnostics import LogDiagnostics

# Create custom diagnostics
diagnostics = LogDiagnostics("logs")

# Adjust thresholds
diagnostics.thresholds['vlm_failure_rate'] = 0.05  # 5% failure rate
diagnostics.thresholds['query_response_time_p95'] = 30.0  # 30ms response time
diagnostics.thresholds['error_rate'] = 0.02  # 2% error rate
```

### 3. Log Format Customization

Log format is defined in `LogManager`, you can modify the `_format_log_message` method:

```python
def _format_log_message(self, event_type: str, **kwargs) -> str:
    """Custom log format"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    data_str = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    return f"{timestamp} [INFO] [{event_type}] {data_str}"
```

## 📈 Monitoring and Alerts

### 1. Real-time Monitoring

```python
import time
from tools.log_diagnostics import LogDiagnostics

diagnostics = LogDiagnostics("logs")

while True:
    # Check every minute
    report = diagnostics.run_comprehensive_diagnostics()
    
    if report['overall_status'] == 'CRITICAL':
        print("🚨 System status critical!")
        for recommendation in report['recommendations']:
            print(f"  - {recommendation}")
    
    elif report['overall_status'] == 'WARNING':
        print("⚠️ System status warning")
        for recommendation in report['recommendations']:
            print(f"  - {recommendation}")
    
    time.sleep(60)  # Wait 60 seconds
```

### 2. Performance Monitoring

```python
from tools.log_diagnostics import LogDiagnostics

diagnostics = LogDiagnostics("logs")

# Monitor query performance
performance = diagnostics.monitor_system_performance()
print(f"Average response time: {performance['query_performance']['average']:.1f}ms")
print(f"95% response time: {performance['query_performance']['p95']:.1f}ms")
print(f"Error rate: {performance['error_rate']:.2%}")

# Check performance issues
for issue in performance['performance_issues']:
    print(f"Performance issue: {issue['description']}")
```

## 🐛 Troubleshooting

### 1. Common Issues

**Issue: Cannot write to log files**
```bash
# Check permissions
ls -la logs/
chmod 755 logs/
chmod 644 logs/*.log
```

**Issue: Log analysis tools cannot find files**
```bash
# Check log directory
python tools/log_analyzer.py --log-dir /path/to/logs

# Check file existence
ls -la logs/
```

**Issue: Diagnostic tools report errors**
```bash
# Check log format
head -5 logs/user_20250130.log

# Regenerate report
python tools/log_diagnostics.py --diagnostic-type comprehensive
```

### 2. Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test logging
from src.logging.log_manager import get_log_manager
log_manager = get_log_manager()

# Log test entry
log_manager.log_user_query(
    query_id="test_query",
    request_id="test_request",
    question="Test query",
    language="en"
)
```

### 3. Performance Tuning

```python
# Batch log recording
import time

start_time = time.time()
for i in range(1000):
    log_manager.log_user_query(
        query_id=f"query_{i}",
        request_id=f"req_{i}",
        question=f"Query {i}",
        language="en"
    )

end_time = time.time()
print(f"1000 log entries took: {end_time - start_time:.3f} seconds")
```

## 📚 Advanced Features

### 1. Custom Analysis

```python
from tools.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")

# Custom event filtering
def custom_filter(log_entry):
    return log_entry['event_type'] == 'USER_QUERY' and 'error' in log_entry['data'].get('question', '').lower()

# Load and filter logs
logs = analyzer.load_logs()
filtered_logs = [log for log in logs if custom_filter(log)]

print(f"Found {len(filtered_logs)} queries containing errors")
```

### 2. Statistical Analysis

```python
from collections import Counter
from tools.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")
logs = analyzer.load_logs()

# Count event types
event_types = Counter(log['event_type'] for log in logs)
print("Event type statistics:")
for event_type, count in event_types.most_common():
    print(f"  {event_type}: {count}")

# Count errors
errors = [log for log in logs if log['level'] == 'ERROR']
print(f"Total errors: {len(errors)}")
```

### 3. Report Generation

```python
from tools.log_analyzer import LogAnalyzer
from datetime import datetime, timedelta

analyzer = LogAnalyzer("logs")

# Generate daily report
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

report = analyzer.generate_report(
    report_type='comprehensive',
    start_time=start_time,
    end_time=end_time
)

# Export report
analyzer.export_report(report, f"daily_report_{end_time.strftime('%Y%m%d')}.json")
```

## 🔗 Integration Guide

### 1. Integration with Existing Systems

```python
# Add logging to existing query processing
from src.logging.log_manager import get_log_manager

log_manager = get_log_manager()

def process_user_query(query: str):
    query_id = log_manager.generate_query_id()
    request_id = log_manager.generate_request_id()
    
    # Log query start
    log_manager.log_user_query(
        query_id=query_id,
        request_id=request_id,
        question=query,
        language="en"
    )
    
    try:
        # Process query
        result = your_query_processor(query)
        
        # Log classification
        log_manager.log_query_classify(
            query_id=query_id,
            query_type=result.type,
            confidence=result.confidence
        )
        
        # Log response
        log_manager.log_query_response(
            query_id=query_id,
            response=result.response,
            duration=result.processing_time
        )
        
        return result
        
    except Exception as e:
        # Log error
        log_manager.get_logger(LogType.SYSTEM).error(f"Query processing failed: {e}")
        raise
```

### 2. Integration with Monitoring Systems

```python
# Periodic health checks
import schedule
import time
from tools.log_diagnostics import LogDiagnostics

def health_check():
    diagnostics = LogDiagnostics("logs")
    report = diagnostics.run_comprehensive_diagnostics()
    
    if report['overall_status'] != 'NORMAL':
        # Send alert
        send_alert(report)
    
    return report

# Run health check every 5 minutes
schedule.every(5).minutes.do(health_check)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 📞 Support and Contact

If you encounter issues while using the logging system, please:

1. Check the troubleshooting section of this guide
2. Review error messages in log files
3. Run diagnostic tools for detailed reports
4. Contact the development team with detailed error information

---

**Version**: 1.0  
**Last Updated**: 2025-01-30  
**Author**: AI Manual Assistant Development Team 