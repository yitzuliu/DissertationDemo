# AI Manual Assistant 日誌系統

## LogManager 使用指南

### 基本使用

```python
from logging.log_manager import LogManager, get_log_manager

# 方法1: 直接創建實例
log_manager = LogManager("logs")

# 方法2: 使用全域實例
log_manager = get_log_manager()
```

### 唯一ID生成

```python
# 生成各種類型的唯一ID
observation_id = log_manager.generate_observation_id()  # obs_1753891534519_db0775ed
query_id = log_manager.generate_query_id()            # query_1753891534519_987f9c84
request_id = log_manager.generate_request_id()        # req_1753891534519_b70f3798
state_update_id = log_manager.generate_state_update_id()  # state_1753891534519_00ac8f4e
flow_id = log_manager.generate_flow_id()              # flow_1753891534519_5d551d89
```

### 系統日誌記錄

```python
# 系統啟動
log_manager.log_system_start("sys_001", "localhost", 8000, "smolvlm")

# 記憶體使用
log_manager.log_memory_usage("sys_001", "22.1MB")

# 端點呼叫
log_manager.log_endpoint_call(request_id, "POST", "/v1/chat/completions", 200, 2.31)

# 系統關閉
log_manager.log_system_shutdown("sys_001", "22.5MB", "30min")
```

### 視覺處理日誌記錄

```python
# 圖像捕獲
log_manager.log_eyes_capture(observation_id, request_id, "MacBook FaceTime HD", 
                            "1920x1080", 0.9, "JPEG", "1.2MB")

# 視覺提示詞
log_manager.log_eyes_prompt(observation_id, "描述製作咖啡的步驟...", 48)

# 後端傳輸
log_manager.log_eyes_transfer(observation_id, {"question": "如何製作咖啡?", "tokens": 100})

# RAG匹配過程
log_manager.log_rag_matching(observation_id, "桌上有咖啡濾紙和滴濾器。", 
                           ["step1", "step2", "step3"], [0.82, 0.65, 0.12])

# RAG匹配結果
log_manager.log_rag_result(observation_id, "step2", "沖洗濾紙", 0.82)

# 狀態追蹤器決策
log_manager.log_state_tracker(observation_id, state_update_id, 0.82, "UPDATE", 
                            {"task": "brewing_coffee", "step": 2})
```

### 使用者查詢日誌記錄

```python
# 使用者查詢
log_manager.log_user_query(query_id, request_id, "我需要什麼工具?", "zh", observation_id)

# 查詢分類
log_manager.log_query_classify(query_id, "required_tools", 0.95)

# 查詢處理
log_manager.log_query_process(query_id, {"task": "brewing_coffee", "step": 2})

# 查詢回應
log_manager.log_query_response(query_id, "您需要: 濾紙、滴濾器、熱水、杯子。", 1.2)
```

### 流程追蹤日誌記錄

```python
# 流程開始
log_manager.log_flow_start(flow_id, "EYES_OBSERVATION")

# 流程步驟
log_manager.log_flow_step(flow_id, "image_capture", observation_id=observation_id)
log_manager.log_flow_step(flow_id, "backend_transfer", request_id=request_id)
log_manager.log_flow_step(flow_id, "user_query", query_id=query_id)

# 流程結束
log_manager.log_flow_end(flow_id, "SUCCESS", 5.0)
```

## 日誌檔案格式

### 檔案命名規則
- 系統日誌: `logs/system_YYYYMMDD.log`
- 視覺日誌: `logs/visual_YYYYMMDD.log`
- 使用者日誌: `logs/user_YYYYMMDD.log`
- 流程追蹤: `logs/flow_tracking_YYYYMMDD.log`

### 日誌格式
```
YYYY-MM-DD HH:MM:SS,mmm [INFO] [EVENT_TYPE] key1=value1 key2=value2 ...
```

### 範例日誌內容
```
2025-07-30 17:05:34,519 [INFO] [SYSTEM_START] system_id=sys_001 host=localhost port=8000 model=smolvlm
2025-07-30 17:05:34,519 [INFO] [EYES_CAPTURE] observation_id=obs_1753891534519_db0775ed request_id=req_1753891534519_b70f3798 device=MacBook FaceTime HD resolution=1920x1080 quality=0.9 format=JPEG size=1.2MB
2025-07-30 17:05:34,519 [INFO] [USER_QUERY] query_id=query_1753891534519_987f9c84 request_id=req_1753891534519_b70f3798 question="我需要什麼工具?" language=zh used_observation_id=obs_1753891534519_db0775ed
```

## 特性

- ✅ 統一的時間戳格式 (`YYYY-MM-DD HH:MM:SS,mmm`)
- ✅ 唯一ID追蹤機制 (observation_id, query_id, request_id, state_update_id, flow_id)
- ✅ 多種日誌類型支援 (system, visual, user, flow_tracking)
- ✅ 結構化日誌格式 (key=value pairs)
- ✅ 自動日誌檔案管理 (按日分檔)
- ✅ 全域實例管理
- ✅ 完整的可追蹤性支援