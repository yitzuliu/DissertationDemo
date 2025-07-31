# AI Manual Assistant 日誌系統使用指南

## 📋 概述

AI Manual Assistant 日誌系統提供完整的系統追蹤和分析功能，包括：

- **統一日誌管理**：多類型日誌的統一記錄和管理
- **流程追蹤**：端到端流程的完整追蹤
- **性能監控**：系統性能的實時監控
- **異常檢測**：自動檢測系統異常和問題
- **分析工具**：強大的日誌分析和診斷工具

## 🏗️ 系統架構

### 核心組件

1. **LogManager** (`src/logging/log_manager.py`)
   - 統一日誌管理器
   - 唯一ID生成
   - 多類型日誌記錄

2. **FlowTracker** (`src/logging/flow_tracker.py`)
   - 流程追蹤器
   - 端到端流程管理
   - 時間線記錄

3. **LogAnalyzer** (`tools/log_analyzer.py`)
   - 日誌分析工具
   - 事件關聯分析
   - 資料完整性檢查

4. **LogDiagnostics** (`tools/log_diagnostics.py`)
   - 系統診斷工具
   - 性能監控
   - 異常檢測

### 日誌類型

- **系統日誌** (`system_*.log`)：系統啟動、關閉、錯誤等
- **視覺日誌** (`visual_*.log`)：VLM處理、圖像捕獲等
- **使用者日誌** (`user_*.log`)：使用者查詢、回應等
- **流程追蹤** (`flow_tracking_*.log`)：流程開始、步驟、結束

## 🚀 快速開始

### 1. 基本使用

```python
from src.logging.log_manager import get_log_manager

# 獲取日誌管理器
log_manager = get_log_manager()

# 記錄使用者查詢
query_id = log_manager.generate_query_id()
request_id = log_manager.generate_request_id()

log_manager.log_user_query(
    query_id=query_id,
    request_id=request_id,
    question="我需要什麼工具？",
    language="zh"
)

# 記錄查詢分類
log_manager.log_query_classify(
    query_id=query_id,
    query_type="required_tools",
    confidence=0.95
)

# 記錄查詢回應
log_manager.log_query_response(
    query_id=query_id,
    response="您需要：濾紙、滴濾器、熱水、杯子。",
    duration=1.2
)
```

### 2. 流程追蹤

```python
from src.logging.flow_tracker import get_flow_tracker, FlowType, FlowStep, FlowStatus

# 獲取流程追蹤器
flow_tracker = get_flow_tracker()

# 開始流程
flow_id = flow_tracker.start_flow(
    FlowType.USER_QUERY,
    metadata={"user_id": "user123"}
)

# 添加流程步驟
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

# 結束流程
flow_tracker.end_flow(
    flow_id=flow_id,
    status=FlowStatus.SUCCESS,
    final_metadata={"response_time": 1.2}
)
```

## 📊 日誌分析

### 1. 基本分析

```bash
# 生成綜合報告
python tools/log_analyzer.py --report-type comprehensive --output report.json

# 分析特定時間範圍
python tools/log_analyzer.py --start-time "2025-01-30 09:00:00" --end-time "2025-01-30 18:00:00"

# 分析特定查詢
python tools/log_analyzer.py --query-id query_1234567890_abcdef12
```

### 2. 系統診斷

```bash
# 執行綜合診斷
python tools/log_diagnostics.py --diagnostic-type comprehensive --output diagnostics.json

# 只檢查VLM失敗
python tools/log_diagnostics.py --diagnostic-type vlm

# 檢查查詢分類準確度
python tools/log_diagnostics.py --diagnostic-type query
```

### 3. 程式化分析

```python
from tools.log_analyzer import LogAnalyzer
from tools.log_diagnostics import LogDiagnostics

# 創建分析器
analyzer = LogAnalyzer("logs")
diagnostics = LogDiagnostics("logs")

# 分析事件流程
flow_analysis = analyzer.analyze_event_flow(query_id="query_123")
print(f"事件數量: {flow_analysis['total_events']}")
print(f"時間跨度: {flow_analysis['time_span']}秒")

# 檢查資料完整性
integrity_report = analyzer.check_data_integrity()
print(f"總查詢數: {integrity_report['total_queries']}")
print(f"不完整查詢: {len(integrity_report['incomplete_queries'])}")

# 執行診斷
diagnostics_report = diagnostics.run_comprehensive_diagnostics()
print(f"整體狀態: {diagnostics_report['overall_status']}")
for recommendation in diagnostics_report['recommendations']:
    print(f"建議: {recommendation}")
```

## 🔧 配置和自定義

### 1. 日誌目錄配置

```python
# 自定義日誌目錄
log_manager = get_log_manager("custom_logs")

# 分析自定義目錄
analyzer = LogAnalyzer("custom_logs")
```

### 2. 診斷閾值調整

```python
from tools.log_diagnostics import LogDiagnostics

# 創建自定義診斷器
diagnostics = LogDiagnostics("logs")

# 調整閾值
diagnostics.thresholds['vlm_failure_rate'] = 0.05  # 5%失敗率
diagnostics.thresholds['query_response_time_p95'] = 30.0  # 30ms回應時間
diagnostics.thresholds['error_rate'] = 0.02  # 2%錯誤率
```

### 3. 日誌格式自定義

日誌格式在 `LogManager` 中定義，可以修改 `_format_log_message` 方法：

```python
def _format_log_message(self, event_type: str, **kwargs) -> str:
    """自定義日誌格式"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    data_str = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    return f"{timestamp} [INFO] [{event_type}] {data_str}"
```

## 📈 監控和警報

### 1. 實時監控

```python
import time
from tools.log_diagnostics import LogDiagnostics

diagnostics = LogDiagnostics("logs")

while True:
    # 每分鐘檢查一次
    report = diagnostics.run_comprehensive_diagnostics()
    
    if report['overall_status'] == 'CRITICAL':
        print("🚨 系統狀態危急！")
        for recommendation in report['recommendations']:
            print(f"  - {recommendation}")
    
    elif report['overall_status'] == 'WARNING':
        print("⚠️ 系統狀態警告")
        for recommendation in report['recommendations']:
            print(f"  - {recommendation}")
    
    time.sleep(60)  # 等待60秒
```

### 2. 性能監控

```python
from tools.log_diagnostics import LogDiagnostics

diagnostics = LogDiagnostics("logs")

# 監控查詢性能
performance = diagnostics.monitor_system_performance()
print(f"平均回應時間: {performance['query_performance']['average']:.1f}ms")
print(f"95%回應時間: {performance['query_performance']['p95']:.1f}ms")
print(f"錯誤率: {performance['error_rate']:.2%}")

# 檢查性能問題
for issue in performance['performance_issues']:
    print(f"性能問題: {issue['description']}")
```

## 🐛 故障排除

### 1. 常見問題

**問題：日誌檔案無法寫入**
```bash
# 檢查權限
ls -la logs/
chmod 755 logs/
chmod 644 logs/*.log
```

**問題：日誌分析工具無法找到檔案**
```bash
# 檢查日誌目錄
python tools/log_analyzer.py --log-dir /path/to/logs

# 檢查檔案存在
ls -la logs/
```

**問題：診斷工具報告錯誤**
```bash
# 檢查日誌格式
head -5 logs/user_20250130.log

# 重新生成報告
python tools/log_diagnostics.py --diagnostic-type comprehensive
```

### 2. 調試模式

```python
import logging

# 啟用調試日誌
logging.basicConfig(level=logging.DEBUG)

# 測試日誌記錄
from src.logging.log_manager import get_log_manager
log_manager = get_log_manager()

# 記錄測試日誌
log_manager.log_user_query(
    query_id="test_query",
    request_id="test_request",
    question="測試查詢",
    language="zh"
)
```

### 3. 性能調優

```python
# 批量日誌記錄
import time

start_time = time.time()
for i in range(1000):
    log_manager.log_user_query(
        query_id=f"query_{i}",
        request_id=f"req_{i}",
        question=f"查詢 {i}",
        language="zh"
    )

end_time = time.time()
print(f"1000次日誌記錄耗時: {end_time - start_time:.3f}秒")
```

## 📚 進階功能

### 1. 自定義分析

```python
from tools.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")

# 自定義事件過濾
def custom_filter(log_entry):
    return log_entry['event_type'] == 'USER_QUERY' and 'error' in log_entry['data'].get('question', '').lower()

# 載入並過濾日誌
logs = analyzer.load_logs()
filtered_logs = [log for log in logs if custom_filter(log)]

print(f"找到 {len(filtered_logs)} 個包含錯誤的查詢")
```

### 2. 統計分析

```python
from collections import Counter
from tools.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")
logs = analyzer.load_logs()

# 統計事件類型
event_types = Counter(log['event_type'] for log in logs)
print("事件類型統計:")
for event_type, count in event_types.most_common():
    print(f"  {event_type}: {count}")

# 統計錯誤
errors = [log for log in logs if log['level'] == 'ERROR']
print(f"總錯誤數: {len(errors)}")
```

### 3. 報告生成

```python
from tools.log_analyzer import LogAnalyzer
from datetime import datetime, timedelta

analyzer = LogAnalyzer("logs")

# 生成每日報告
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

report = analyzer.generate_report(
    report_type='comprehensive',
    start_time=start_time,
    end_time=end_time
)

# 導出報告
analyzer.export_report(report, f"daily_report_{end_time.strftime('%Y%m%d')}.json")
```

## 🔗 整合指南

### 1. 與現有系統整合

```python
# 在現有的查詢處理中添加日誌
from src.logging.log_manager import get_log_manager

log_manager = get_log_manager()

def process_user_query(query: str):
    query_id = log_manager.generate_query_id()
    request_id = log_manager.generate_request_id()
    
    # 記錄查詢開始
    log_manager.log_user_query(
        query_id=query_id,
        request_id=request_id,
        question=query,
        language="zh"
    )
    
    try:
        # 處理查詢
        result = your_query_processor(query)
        
        # 記錄分類
        log_manager.log_query_classify(
            query_id=query_id,
            query_type=result.type,
            confidence=result.confidence
        )
        
        # 記錄回應
        log_manager.log_query_response(
            query_id=query_id,
            response=result.response,
            duration=result.processing_time
        )
        
        return result
        
    except Exception as e:
        # 記錄錯誤
        log_manager.get_logger(LogType.SYSTEM).error(f"查詢處理失敗: {e}")
        raise
```

### 2. 與監控系統整合

```python
# 定期健康檢查
import schedule
import time
from tools.log_diagnostics import LogDiagnostics

def health_check():
    diagnostics = LogDiagnostics("logs")
    report = diagnostics.run_comprehensive_diagnostics()
    
    if report['overall_status'] != 'NORMAL':
        # 發送警報
        send_alert(report)
    
    return report

# 每5分鐘執行一次健康檢查
schedule.every(5).minutes.do(health_check)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 📞 支援和聯繫

如果您在使用日誌系統時遇到問題，請：

1. 檢查本指南的故障排除部分
2. 查看日誌檔案中的錯誤信息
3. 運行診斷工具獲取詳細報告
4. 聯繫開發團隊提供詳細的錯誤信息

---

**版本**: 1.0  
**最後更新**: 2025-01-30  
**作者**: AI Manual Assistant 開發團隊 