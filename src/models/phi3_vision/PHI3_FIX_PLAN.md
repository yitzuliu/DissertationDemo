# Phi-3 Vision 模型整合修正計畫

本文件旨在詳細說明整合 Phi-3 Vision 模型時所發現的問題，並提供一個清晰、分步驟的修正計畫。

## 第一部分：核心問題分析

### 問題一：`RuntimeError: shape mismatch` (執行時錯誤)

- **根本原因**：對 Hugging Face `processor` 物件的使用方式不正確。目前的程式碼同時進行了手動的輸入預處理 (呼叫 `apply_chat_template`) 和自動處理 (將結果再次傳遞給 `processor`)。這種重複處理導致了輸入模型的資料張量 (tensor) 形狀毀損，從而引發執行時錯誤。
- **問題位置**：此錯誤的根源在於 `src/models/phi3_vision/main.py` 和 `run_phi3_vision.py` 中準備模型輸入的邏輯。

### 問題二：架構不一致與設定缺失

- **根本原因**：
    1.  **入口點混亂**：專案中存在多個可以執行 `phi3` 模型的檔案（如 `run_phi3_vision.py`, `main.py`），缺乏一個統一、標準的服務啟動方式，這使得測試和部署變得複雜且不可靠。
    2.  **設定檔不完整**：`src/config/model_configs/phi3_vision.json` 檔案中缺少關鍵的 `"server"` 區塊。主後端依賴此區塊來管理和啟動模型微服務。

## 第二部分：分步驟修正計畫

我們將依序執行以下步驟，以確保問題得到穩定且可驗證的修復。

### 步驟一：統一模型服務的入口點

- **行動**：明確指定 `src/models/phi3_vision/main.py` 為 **唯一且官方** 的 `phi3` 模型服務啟動檔案。它將作為一個獨立的 FastAPI 伺服器運行。
- **預期成果**：消除架構上的模糊性。`run_phi3_vision.py` 將被視為一個用於本地除錯或展示的獨立腳本，不參與後端的正式服務流程。

### 步驟二：完善模型的設定檔

- **行動**：編輯 `src/config/model_configs/phi3_vision.json`，參考 `yolo8.json` 的格式，為其加入 `"server"` 區塊。
- **範例**：
  ```json
  "server": {
    "command": "python",
    "args": ["src/models/phi3_vision/main.py"],
    "port": 8082,
    "health_endpoint": "/health"
  }
  ```
- **預期成果**：讓主後端的服務管理器能夠正確地啟動、監控 `phi3` 模型服務，並與其通訊。

### 步驟三：重構並修正模型伺服器

- **行動**：
    1.  修改 `src/models/phi3_vision/main.py`，修正導致 `RuntimeError` 的輸入準備邏輯。我們將簡化程式碼，將輸入準備工作完全交給 `processor` 物件。
    2.  在此檔案的 `/analyze` 端點中，加入您要求的**日誌記錄功能**，將每次請求的輸入 (prompt) 和模型的輸出 (response) 記錄到 `src/models/phi3_vision/logs/phi3_io.log`。
- **預期成果**：一個功能正常、運作穩定的模型伺服器，並且所有重要的資料交換都有日誌可查。

### 步驟四：建立一個真實的整合測試

- **行動**：在專案根目錄建立一個新的測試腳本 `test_phi3_integration.py`。此腳本將：
    1.  使用 `subprocess` 在背景啟動 `phi3` 模型伺服器。
    2.  透過輪詢其 `/health` 端點，等待伺服器完全就緒。
    3.  使用 `httpx` 函式庫，向伺服器的 `/analyze` 端點發送一個包含模擬圖片和提示的**真實 HTTP POST 請求**。
    4.  驗證收到的 HTTP 回應是否成功，且內容符合預期。
    5.  檢查 `phi3_io.log` 日誌檔案是否已生成並包含正確的記錄。
    6.  在測試結束後，可靠地終止背景伺服器進程。
- **預期成果**：一個能夠驗證端到端流程（包含網路通訊）的整合測試，確保模型服務在真實環境下的可靠性。

### 步驟五：與主後端進行最終對接

- **行動**：在模型服務通過整合測試後，微調 `src/backend/main.py`。主要是更新 `proxy_chat_completions` 函式，使其能夠從 `phi3_vision.json` 設定檔中動態讀取正確的埠號（`8082`），並將請求正確地轉發到 `phi3` 服務。
- **預期成果**：完成從前端 -> 主後端 -> `phi3` 模型服務的無縫整合。
