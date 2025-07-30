# 視覺日誌記錄器 (VisualLogger)

## 概述

VisualLogger 是 AI Manual Assistant 日誌系統的視覺處理組件，負責記錄所有與VLM（視覺語言模型）處理相關的後端事件。

## 主要功能

### 1. 後端接收日誌 (BACKEND_RECEIVE)
記錄後端接收到的VLM請求：
- **觀察ID**: 唯一的觀察事件標識符
- **請求ID**: 唯一的請求標識符
- **請求數據**: 清理後的請求數據（移除敏感圖像內容）
- **模型資訊**: 使用的VLM模型名稱

### 2. 圖像處理日誌
記錄圖像預處理過程：
- **處理開始**: `IMAGE_PROCESSING_START` - 記錄開始時間、圖像數量、模型
- **處理結果**: `IMAGE_PROCESSING_RESULT` - 記錄處理時間、成功狀態、詳細資訊

### 3. VLM模型交互日誌
記錄與VLM模型的交互：
- **VLM請求**: `VLM_REQUEST` - 記錄模型名稱、提示詞長度、圖像數量
- **VLM回應**: `VLM_RESPONSE` - 記錄回應長度、處理時間、成功狀態

### 4. RAG系統資料傳遞日誌 (RAG_DATA_TRANSFER)
記錄VLM輸出到RAG系統的資料傳遞：
- **傳遞狀態**: 成功或失敗
- **文本長度**: VLM輸出文本的長度
- **文本預覽**: 截斷的文本內容預覽

### 5. 狀態追蹤器整合日誌 (STATE_TRACKER_INTEGRATION)
記錄與狀態追蹤器的整合：
- **狀態更新**: 是否成功更新狀態
- **處理時間**: 狀態處理所需時間

### 6. 性能指標記錄 (VISUAL_PERFORMANCE)
記錄各種性能指標：
- **總處理時間**: 完整請求的處理時間
- **圖像處理時間**: 圖像預處理時間
- **模型推理時間**: VLM模型推理時間
- **狀態處理時間**: 狀態追蹤器處理時間

### 7. 錯誤處理 (VISUAL_ERROR)
記錄視覺處理過程中的錯誤：
- **錯誤類型**: 異常類型
- **錯誤訊息**: 詳細錯誤訊息
- **錯誤上下文**: 發生錯誤的上下文

## 使用方法

### 基本使用

```python
from logging.visual_logger import get_visual_logger

# 獲取視覺日誌記錄器
visual_logger = get_visual_logger()

# 生成觀察ID和請求ID
observation_id = f"obs_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
request_id = f"req_{int(time.time() * 1000)}"

# 記錄後端接收
visual_logger.log_backend_receive(observation_id, request_id, request_data)

# 記錄圖像處理
visual_logger.log_image_processing_start(observation_id, request_id, image_count, model)
visual_logger.log_image_processing_result(observation_id, request_id, processing_time, success, details)

# 記錄VLM交互
visual_logger.log_vlm_request(observation_id, request_id, model, prompt_length, image_count)
visual_logger.log_vlm_response(observation_id, request_id, response_length, processing_time, success, model)

# 記錄RAG資料傳遞
visual_logger.log_rag_data_transfer(observation_id, vlm_text, transfer_success)

# 記錄狀態追蹤器整合
visual_logger.log_state_tracker_integration(observation_id, state_updated, processing_time)

# 記錄性能指標
visual_logger.log_performance_metric(observation_id, "total_processing_time", 1.25, "s")

# 記錄錯誤
visual_logger.log_error(observation_id, request_id, "ConnectionError", "Failed to connect", "model_server")
```

### 在後端API中的整合

```python
@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: ChatCompletionRequest):
    request_start_time = time.time()
    request_id = f"req_{int(request_start_time * 1000)}"
    observation_id = f"obs_{int(request_start_time * 1000)}_{uuid.uuid4().hex[:8]}"
    
    visual_logger = get_visual_logger()
    
    try:
        # 記錄後端接收
        visual_logger.log_backend_receive(observation_id, request_id, {
            "model": ACTIVE_MODEL,
            "messages": request.messages,
            "max_tokens": getattr(request, 'max_tokens', None)
        })
        
        # 圖像處理
        visual_logger.log_image_processing_start(observation_id, request_id, image_count, ACTIVE_MODEL)
        # ... 圖像處理邏輯 ...
        visual_logger.log_image_processing_result(observation_id, request_id, processing_time, True, details)
        
        # VLM請求
        visual_logger.log_vlm_request(observation_id, request_id, ACTIVE_MODEL, prompt_length, image_count)
        # ... VLM請求邏輯 ...
        visual_logger.log_vlm_response(observation_id, request_id, response_length, model_time, True, ACTIVE_MODEL)
        
        # RAG和狀態追蹤器整合
        visual_logger.log_rag_data_transfer(observation_id, vlm_text, True)
        visual_logger.log_state_tracker_integration(observation_id, state_updated, state_time)
        
        # 性能指標
        total_time = time.time() - request_start_time
        visual_logger.log_performance_metric(observation_id, "total_processing_time", total_time, "s")
        
        return model_response
        
    except Exception as e:
        # 錯誤記錄
        visual_logger.log_error(observation_id, request_id, type(e).__name__, str(e), "vlm_processing")
        raise
```

## 日誌格式

所有視覺日誌都使用統一格式，記錄到 `logs/visual_YYYYMMDD.log` 文件中：

```
2025-07-30 21:17:49,139 [INFO] [BACKEND_RECEIVE] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 data={"model": "smolvlm", "messages": [...], "max_tokens": 150}

2025-07-30 21:17:49,240 [INFO] [IMAGE_PROCESSING_START] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 image_count=1 model=smolvlm

2025-07-30 21:17:49,441 [INFO] [IMAGE_PROCESSING_RESULT] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 status=SUCCESS processing_time=0.200s image_count=1 model=smolvlm

2025-07-30 21:17:49,442 [INFO] [VLM_REQUEST] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 model=smolvlm prompt_length=45 image_count=1

2025-07-30 21:17:50,243 [INFO] [VLM_RESPONSE] observation_id=obs_flow_1753906669 request_id=req_flow_1753906669 model=smolvlm status=SUCCESS response_length=180 processing_time=0.800s

2025-07-30 21:17:50,243 [INFO] [RAG_DATA_TRANSFER] observation_id=obs_flow_1753906669 status=SUCCESS text_length=226 text_preview="I can see coffee brewing equipment..."

2025-07-30 21:17:50,294 [INFO] [STATE_TRACKER_INTEGRATION] observation_id=obs_flow_1753906669 state_updated=True processing_time=0.050s

2025-07-30 21:17:50,294 [INFO] [VISUAL_PERFORMANCE] observation_id=obs_flow_1753906669 metric=total_processing_time value=1.050s
```

## 日誌事件類型

- `[BACKEND_RECEIVE]`: 後端接收VLM請求
- `[IMAGE_PROCESSING_START]`: 圖像處理開始
- `[IMAGE_PROCESSING_RESULT]`: 圖像處理結果
- `[VLM_REQUEST]`: VLM模型請求
- `[VLM_RESPONSE]`: VLM模型回應
- `[RAG_DATA_TRANSFER]`: RAG系統資料傳遞
- `[STATE_TRACKER_INTEGRATION]`: 狀態追蹤器整合
- `[VISUAL_PERFORMANCE]`: 視覺處理性能指標
- `[VISUAL_ERROR]`: 視覺處理錯誤

## 數據安全和隱私

### 敏感數據處理
1. **圖像數據**: 完整的base64圖像數據會被替換為 `[IMAGE_DATA_REMOVED]`
2. **長文本**: 超過200字符的文本會被截斷並添加 `...` 標記
3. **文本預覽**: RAG傳遞的長文本只記錄前100字符的預覽

### 數據清理功能
```python
def _sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """清理請求數據，移除敏感或過大的內容"""
    # 自動移除圖像數據
    # 截斷過長的文本內容
    # 保留重要的元數據
```

## 性能考量

- **異步記錄**: 所有日誌記錄都是異步的，不會阻塞主處理流程
- **數據截斷**: 自動截斷大型數據以控制日誌文件大小
- **觀察ID追蹤**: 使用唯一的觀察ID在整個處理流程中保持一致性
- **性能開銷**: 日誌記錄對系統性能影響 < 1%

## 測試

運行測試腳本驗證功能：

```bash
python src/logging/test_visual_logger.py
```

測試包括：
- 基本功能測試
- 錯誤處理測試
- 數據清理測試
- 性能監控測試
- 完整VLM流程測試

## 配置

視覺日誌記錄器會自動：
- 使用統一的日誌管理器
- 記錄到 `logs/visual_YYYYMMDD.log` 文件
- 按日期輪轉日誌文件
- 使用統一的時間戳格式

## 依賴

- `log_manager`: 統一日誌管理器
- `uuid`: 唯一ID生成
- `json`: JSON數據處理
- `time`: 時間戳和性能測量

## 注意事項

1. **觀察ID一致性**: 在整個VLM處理流程中使用相同的觀察ID
2. **數據隱私**: 敏感數據會被自動清理和截斷
3. **性能監控**: 記錄詳細的性能指標用於分析和優化
4. **錯誤追蹤**: 完整的錯誤上下文記錄便於調試
5. **時間戳精度**: 使用毫秒級時間戳確保事件順序的準確性