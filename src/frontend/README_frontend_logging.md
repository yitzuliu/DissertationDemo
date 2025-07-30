# 前端視覺日誌記錄系統

## 概述

前端視覺日誌記錄系統是 AI Manual Assistant 日誌系統的前端組件，負責記錄所有與視覺處理相關的前端事件。

## 主要功能

### 1. 圖像捕獲日誌 (EYES_CAPTURE)
記錄每次圖像捕獲的詳細資訊：
- **觀察ID**: 唯一的觀察事件標識符
- **請求ID**: 唯一的請求標識符
- **設備資訊**: 使用的攝像頭設備名稱
- **解析度**: 捕獲圖像的解析度
- **品質**: 圖像壓縮品質
- **格式**: 圖像格式（JPEG）
- **大小**: 圖像文件大小

### 2. 視覺提示詞日誌 (EYES_PROMPT)
記錄發送給VLM的提示詞：
- **觀察ID**: 關聯的觀察事件ID
- **提示詞內容**: 完整的提示詞文本
- **長度**: 提示詞字符數
- **時間戳**: 記錄時間

### 3. 後端傳輸日誌 (EYES_TRANSFER)
記錄發送到後端的數據：
- **觀察ID**: 關聯的觀察事件ID
- **傳輸數據**: 發送到後端的數據摘要
- **參數**: 包括max_tokens、quality等參數
- **時間戳**: 傳輸時間

### 4. 用戶操作日誌 (USER_ACTION)
記錄用戶的操作行為：
- **開始處理**: 用戶點擊開始按鈕
- **停止處理**: 用戶點擊停止按鈕
- **攝像頭切換**: 用戶選擇不同的攝像頭
- **設置變更**: 用戶修改品質、間隔等設置

### 5. 錯誤日誌 (FRONTEND_ERROR)
記錄前端發生的錯誤：
- **圖像捕獲錯誤**: 攝像頭訪問失敗等
- **VLM請求錯誤**: 後端通信失敗等
- **未捕獲錯誤**: 全域錯誤處理

## 技術實現

### FrontendVisualLogger 類別

```javascript
class FrontendVisualLogger {
    constructor() {
        this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        this.logToConsole = true;
        this.observationId = null;
    }
    
    generateObservationId() {
        const timestamp = Date.now();
        this.observationId = `obs_${timestamp}_${Math.random().toString(36).substr(2, 8)}`;
        return this.observationId;
    }
    
    logEyesCapture(observationId, requestId, deviceInfo, imageData) { ... }
    logEyesPrompt(observationId, prompt) { ... }
    logEyesTransfer(observationId, transferData) { ... }
    logUserAction(action, details) { ... }
    logError(error, context) { ... }
}
```

### 整合點

#### 1. 圖像捕獲整合
在 `CameraManager.captureImage()` 方法中：
```javascript
// 生成觀察ID和請求ID
const observationId = frontendLogger.generateObservationId();
const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;

// 記錄圖像捕獲事件
frontendLogger.logEyesCapture(observationId, requestId, deviceInfo, {
    resolution: `${targetWidth}x${targetHeight}`,
    quality: imageQuality,
    format: 'jpeg',
    size: `${(imageSizeBytes / 1024).toFixed(1)}KB`
});
```

#### 2. 視覺提示詞整合
在 `VisionApp.sendData()` 方法中：
```javascript
// 記錄視覺提示詞
frontendLogger.logEyesPrompt(observationId, instruction);
```

#### 3. 後端傳輸整合
在發送API請求前：
```javascript
// 準備發送到後端的數據
const transferData = {
    instruction: instruction,
    image_data: imageBase64URL.substring(0, 100) + '...[truncated]',
    max_tokens: maxTokens,
    quality: quality,
    observation_id: observationId,
    request_id: requestId
};

// 記錄後端傳輸
frontendLogger.logEyesTransfer(observationId, transferData);
```

#### 4. 用戶操作整合
在各種用戶操作處理中：
```javascript
// 開始處理
frontendLogger.logUserAction('start_processing', {
    instruction: instruction,
    capture_interval: intervalTime,
    quality: quality,
    max_tokens: maxTokens
});

// 停止處理
frontendLogger.logUserAction('stop_processing', {
    reason: 'user_initiated'
});

// 攝像頭切換
frontendLogger.logUserAction('camera_change', {
    device_id: selectedDeviceId,
    device_name: deviceName
});
```

## 日誌格式

所有前端日誌都使用統一格式：

```javascript
{
    timestamp: "2025-07-30T10:27:57.674Z",
    sessionId: "session_1753896477674_abc123def",
    eventType: "EYES_CAPTURE",
    data: {
        observation_id: "obs_1753896477674_143eb05f",
        request_id: "req_1753896477674_143eb05f",
        device: "📱 iPhone Camera",
        resolution: "1024x768",
        quality: 0.9,
        format: "jpeg",
        size: "156.7KB",
        timestamp: 1753896477674
    }
}
```

## 日誌事件類型

- `EYES_CAPTURE`: 圖像捕獲事件
- `EYES_PROMPT`: 視覺提示詞事件
- `EYES_TRANSFER`: 後端傳輸事件
- `USER_ACTION`: 用戶操作事件
- `FRONTEND_ERROR`: 前端錯誤事件
- `PAGE_LOAD`: 頁面載入事件

## 測試

### 1. 功能測試
打開 `test_frontend_logging.html` 進行互動式測試：
- 測試各種日誌記錄功能
- 查看實時日誌輸出
- 驗證日誌格式和內容

### 2. 整合驗證
運行驗證腳本：
```bash
node src/frontend/verify_logging_integration.js
```

## 配置

### 日誌輸出控制
```javascript
const frontendLogger = new FrontendVisualLogger();
frontendLogger.logToConsole = true;  // 控制台輸出
frontendLogger.logToServer = false;  // 服務器發送（未來功能）
```

### 觀察ID管理
每次圖像捕獲都會生成新的觀察ID，並在整個處理流程中保持一致：
```javascript
const observationId = frontendLogger.generateObservationId();
// 在後續的提示詞和傳輸日誌中使用相同的observationId
```

## 性能考量

- 日誌記錄是同步的，但開銷很小
- 圖像數據在日誌中會被截斷以避免過大的日誌條目
- 使用時間戳和隨機字符串生成唯一ID，確保不重複

## 未來擴展

1. **服務器發送**: 將日誌發送到後端進行集中存儲
2. **日誌過濾**: 根據日誌級別過濾輸出
3. **批量發送**: 批量發送日誌以提高性能
4. **離線存儲**: 在網路不可用時本地存儲日誌

## 注意事項

1. 觀察ID在整個視覺處理流程中保持一致
2. 圖像數據在日誌中會被截斷以保護隱私和減少存儲
3. 所有時間戳都使用 ISO 8601 格式
4. 日誌記錄不會影響主要功能的性能