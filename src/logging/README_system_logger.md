# 系統日誌記錄器 (SystemLogger)

## 概述

SystemLogger 是 AI Manual Assistant 日誌系統的核心組件，負責記錄所有系統級事件和狀態資訊。

## 主要功能

### 1. 系統生命週期記錄
- **系統啟動**: 記錄主機、端口、模型等啟動參數
- **系統關閉**: 記錄運行時間和最終資源使用情況

### 2. 資源監控
- **記憶體使用**: 實時記錄記憶體使用情況
- **CPU使用**: 記錄CPU使用百分比
- **性能指標**: 記錄各種自定義性能指標

### 3. API請求追蹤
- **端點呼叫**: 記錄HTTP請求的方法、路徑、狀態碼、處理時間
- **請求ID**: 自動生成唯一請求ID進行追蹤
- **客戶端資訊**: 記錄客戶端IP等額外資訊

### 4. 連線狀態監控
- **服務連線**: 記錄各種服務的連線狀態
- **健康檢查**: 記錄組件健康狀態和響應時間

### 5. 錯誤處理
- **錯誤記錄**: 詳細記錄錯誤類型、訊息和上下文
- **請求關聯**: 將錯誤與特定請求ID關聯

## 使用方法

### 基本使用

```python
from logging.system_logger import initialize_system_logger, get_system_logger

# 初始化系統日誌記錄器
system_logger = initialize_system_logger("my_app_001")

# 記錄系統啟動
system_logger.log_system_startup(
    host="0.0.0.0",
    port=8000,
    model="smolvlm",
    framework="FastAPI"
)

# 記錄API請求
system_logger.log_endpoint_call(
    method="POST",
    path="/api/process",
    status_code=200,
    duration=0.125,
    client_ip="127.0.0.1"
)

# 記錄錯誤
system_logger.log_error(
    error_type="ValidationError",
    error_message="Invalid input format",
    context={"expected": "image", "received": "text"},
    request_id="req_123456"
)

# 記錄系統關閉
system_logger.log_system_shutdown()
```

### 便捷函數

```python
from logging.system_logger import log_startup, log_request, log_error, log_memory

# 使用便捷函數
log_startup(host="localhost", port=8000, model="test_model")
log_request("GET", "/api/health", 200, 0.005)
log_error("TimeoutError", "Request timeout", {"timeout": 30})
log_memory()
```

### 在 FastAPI 中整合

```python
from fastapi import FastAPI, Request
from logging.system_logger import initialize_system_logger
import time

app = FastAPI()
system_logger = initialize_system_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        system_logger.log_endpoint_call(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration=duration
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        system_logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"path": str(request.url.path)}
        )
        raise

@app.on_event("startup")
async def startup_event():
    system_logger.log_system_startup(
        host="0.0.0.0",
        port=8000,
        model="smolvlm"
    )

@app.on_event("shutdown")
async def shutdown_event():
    system_logger.log_system_shutdown()
```

## 日誌格式

所有日誌都使用統一格式：

```
2025-07-30 18:27:57,674 [INFO] [SYSTEM_START] system_id=test_system_001 host=localhost port=8000 model=smolvlm
2025-07-30 18:27:57,674 [INFO] [ENDPOINT] request_id=req_1753896477674_143eb05f method=POST path=/api/process status=200 duration=0.12s
2025-07-30 18:27:57,674 [ERROR] [ERROR] system_id=test_system_001 type=ValidationError message=Invalid format request_id=req_123456
```

## 日誌類型

- `[SYSTEM_START]`: 系統啟動事件
- `[SYSTEM_SHUTDOWN]`: 系統關閉事件
- `[MEMORY]`: 記憶體使用記錄
- `[CPU_USAGE]`: CPU使用記錄
- `[ENDPOINT]`: API端點呼叫
- `[CONNECTION]`: 連線狀態變更
- `[ERROR]`: 錯誤事件
- `[PERFORMANCE]`: 性能指標
- `[HEALTH_CHECK]`: 健康檢查結果

## 配置

系統日誌記錄器會自動：
- 生成唯一的系統ID
- 創建日誌目錄 (`logs/`)
- 按日期輪轉日誌文件
- 使用統一的時間戳格式

## 性能考量

- 所有日誌操作都是異步的，不會阻塞主程序
- 記憶體使用監控使用 `psutil` 庫，開銷很小
- 日誌記錄對系統性能影響 < 1%

## 測試

運行測試腳本驗證功能：

```bash
python src/logging/test_system_logger.py
python src/logging/integration_example.py
```

## 依賴

- `psutil`: 系統資源監控
- `uuid`: 唯一ID生成
- `logging`: Python標準日誌庫
- `log_manager`: 統一日誌管理器

## 注意事項

1. 系統日誌記錄器是單例模式，整個應用共享一個實例
2. 所有時間戳都使用 ISO 8601 格式
3. 錯誤日誌會同時記錄到系統日誌和錯誤日誌
4. 建議在應用啟動時初始化，在關閉時記錄關閉事件