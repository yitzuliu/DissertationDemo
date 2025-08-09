# VLM Fallback 圖片傳送功能使用指南

## 📋 功能概述

VLM Fallback 圖片傳送功能是對現有 VLM Fallback 系統的增強，當查詢分類信心度 < 0.40 時，系統會自動將當前圖片一併傳送給 VLM，提供更豐富的視覺上下文支援。

## 🚀 快速開始

### 1. 功能啟用

圖片 fallback 功能預設已啟用，可以通過配置檔案控制：

```json
{
  "vlm_fallback": {
    "enable_image_fallback": true,
    "image_capture": {
      "enable_camera_capture": true,
      "enable_state_tracker_capture": true,
      "enable_image_cache": true,
      "cache_duration_seconds": 300,
      "max_image_size_bytes": 1048576
    },
    "image_processing": {
      "default_model": "smolvlm",
      "quality": 85,
      "max_size": 1024,
      "format": "jpeg"
    }
  }
}
```

### 2. 使用方式

用戶無需任何特殊操作，系統會自動：

1. **檢測低信心值查詢**：當查詢分類信心度 < 0.40 時
2. **自動獲取圖片**：從相機、狀態追蹤器或緩存獲取當前圖片
3. **傳送給 VLM**：將圖片和查詢一併傳送給 VLM 服務
4. **返回智能回應**：基於視覺內容的詳細回答

## 🔧 配置選項

### 圖片獲取配置

```json
"image_capture": {
  "enable_camera_capture": true,        // 啟用相機圖片獲取
  "enable_state_tracker_capture": true, // 啟用狀態追蹤器圖片獲取
  "enable_image_cache": true,           // 啟用圖片緩存
  "cache_duration_seconds": 300,        // 緩存時間（秒）
  "max_image_size_bytes": 1048576       // 最大圖片大小（1MB）
}
```

### 圖片處理配置

```json
"image_processing": {
  "default_model": "smolvlm",  // 預設處理模型
  "quality": 85,               // JPEG 品質
  "max_size": 1024,            // 最大尺寸
  "format": "jpeg"             // 輸出格式
}
```

## 📝 使用範例

### 範例 1：視覺查詢
```
用戶查詢：What do you see in this image?
系統回應：I can see a coffee cup sitting on a wooden table. The cup appears to be white ceramic with a dark brown liquid inside, likely coffee. There's also a small spoon resting next to the cup.
```

### 範例 2：物件識別
```
用戶查詢：What objects are visible in the image?
系統回應：In this image, I can identify several objects: a coffee cup, a wooden table, a spoon, and what appears to be a napkin or coaster underneath the cup.
```

### 範例 3：場景描述
```
用戶查詢：Describe the scene in this picture
系統回應：This appears to be a cozy coffee shop or kitchen setting. The main focus is a coffee cup placed on a wooden table, suggesting a relaxed coffee break or morning routine.
```

## 🔄 降級機制

系統具備多重降級機制，確保穩定性：

1. **圖片獲取失敗**：自動回退到純文字 fallback
2. **VLM 服務異常**：返回友好的錯誤訊息
3. **圖片處理失敗**：使用原始圖片或回退到文字模式
4. **配置錯誤**：使用預設配置

## 📊 性能考量

### 性能目標
- **圖片獲取時間**：< 500ms
- **圖片預處理時間**：< 1s
- **VLM 響應時間**：< 15s（包含圖片處理）
- **總響應時間**：< 20s
- **記憶體使用**：圖片緩存 < 50MB

### 優化策略
1. **圖片緩存**：避免重複獲取相同圖片
2. **異步處理**：並行處理圖片獲取和預處理
3. **降級機制**：圖片獲取失敗時回退到純文字
4. **資源管理**：及時清理圖片緩存

## 🧪 測試

### 運行單元測試
```bash
cd tests/vlm_fallback
python -m pytest test_image_enhancement.py -v
```

### 運行集成測試
```bash
cd tests/vlm_fallback
python -m pytest test_image_integration.py -v
```

### 測試場景
1. **正常場景**：圖片獲取成功，VLM 正常回應
2. **圖片獲取失敗**：相機不可用，回退到純文字
3. **VLM 服務異常**：圖片正常但 VLM 失敗
4. **圖片處理失敗**：圖片格式不支援
5. **並發測試**：多用戶同時使用圖片 Fallback

## 🔍 故障排除

### 常見問題

#### 1. 圖片獲取失敗
**症狀**：系統回退到純文字回應
**解決方案**：
- 檢查相機權限
- 確認狀態追蹤器圖片功能
- 檢查圖片緩存配置

#### 2. VLM 服務無回應
**症狀**：查詢超時或返回錯誤
**解決方案**：
- 檢查 VLM 服務狀態
- 確認網路連接
- 檢查服務端點配置

#### 3. 圖片處理錯誤
**症狀**：圖片格式不支援或處理失敗
**解決方案**：
- 檢查圖片格式支援
- 確認圖片大小限制
- 檢查圖片處理配置

### 日誌檢查

啟用詳細日誌來診斷問題：

```json
{
  "vlm_fallback": {
    "logging": {
      "enable_decision_logs": true,
      "enable_vlm_logs": true,
      "enable_performance_logs": true
    }
  }
}
```

## 🔄 向後兼容性

### 兼容性保證
1. **現有功能不變**：純文字 Fallback 功能保持不變
2. **配置向後兼容**：舊配置檔案仍然有效
3. **API 向後兼容**：現有 API 接口不變
4. **用戶體驗一致**：用戶無法感知內部變化

### 遷移策略
1. **漸進式啟用**：可配置啟用圖片 Fallback
2. **降級機制**：圖片功能失敗時自動降級
3. **監控告警**：及時發現和處理問題
4. **回滾計劃**：問題時快速回滾到純文字模式

## 📚 相關文檔

- [VLM Fallback 系統設計文檔](../.kiro/specs/vlm-fallback-system/design.md)
- [VLM Fallback 功能需求規格](../.kiro/specs/vlm-fallback-system/requirements.md)
- [VLM Fallback 開發任務清單](../.kiro/specs/vlm-fallback-system/tasks.md)
- [VLM Fallback 開發檢查清單](../.kiro/specs/vlm-fallback-system/development-checklist.md)

## 🤝 貢獻

如果您發現問題或有改進建議，請：

1. 檢查現有的 issue
2. 創建新的 issue 描述問題
3. 提交 pull request 包含修復或改進

## 📄 授權

本功能遵循專案的現有授權條款。 