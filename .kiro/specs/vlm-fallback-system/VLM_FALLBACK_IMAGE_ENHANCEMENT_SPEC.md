# VLM Fallback 圖片傳送功能增強規格

## 📋 項目概述

**目標**：擴展 VLM Fallback 系統，使其能夠在查詢分類信心度 < 0.40 時，將當前圖片一併傳送給 VLM，提供更豐富的視覺上下文支援。

**核心概念**：低信心值查詢 + 當前圖片 → VLM 多模態回應 → 智能視覺感知回答

**時間線**：預計 1 週完成
**優先級**：中高
**狀態**：🔄 規劃中

## 🏗️ 系統架構設計

### 1.1 增強架構圖

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   VLM Service   │
│                 │    │                 │    │                 │
│ - Query Input   │───▶│ - Query Router  │───▶│ - Model Server  │
│ - Response UI   │    │ - State Tracker │    │ - Direct Query  │
│ - Status Display│◀───│ - VLM Fallback  │◀───│ - Response Gen  │
└─────────────────┘    │ - Image Capture │    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Image System  │
                       │                 │
                       │ - Camera        │
                       │ - Preprocessing │
                       │ - Storage       │
                       └─────────────────┘
```

### 1.2 核心組件增強

#### 1.2.1 圖片獲取管理器 (ImageCaptureManager)
```python
class ImageCaptureManager:
    """管理圖片獲取和預處理的統一接口"""
    
    def __init__(self):
        self.camera_manager = None
        self.image_processor = None
        self.last_captured_image = None
        self.image_cache = {}
    
    async def get_current_image(self, model_type: str = None) -> Optional[Dict]:
        """
        獲取當前圖片，支援多種來源
        """
        # 優先級 1：從相機獲取實時圖片
        current_image = await self._capture_from_camera()
        if current_image:
            return self._process_for_fallback(current_image, model_type)
        
        # 優先級 2：從狀態追蹤器獲取最後處理的圖片
        last_image = await self._get_last_processed_image()
        if last_image:
            return self._process_for_fallback(last_image, model_type)
        
        # 優先級 3：從緩存獲取
        cached_image = self._get_cached_image()
        if cached_image:
            return self._process_for_fallback(cached_image, model_type)
        
        return None
    
    async def _capture_from_camera(self) -> Optional[bytes]:
        """從相機系統獲取當前圖片"""
        try:
            # 調用相機管理器獲取當前畫面
            if self.camera_manager:
                return await self.camera_manager.capture_current_frame()
            return None
        except Exception as e:
            logger.warning(f"Camera capture failed: {e}")
            return None
    
    async def _get_last_processed_image(self) -> Optional[bytes]:
        """從狀態追蹤器獲取最後處理的圖片"""
        try:
            # 從狀態追蹤器獲取最後的圖片數據
            state_tracker = get_state_tracker()
            return state_tracker.get_last_processed_image()
        except Exception as e:
            logger.warning(f"Last image retrieval failed: {e}")
            return None
    
    def _process_for_fallback(self, image_data: bytes, model_type: str = None) -> Dict:
        """為 VLM Fallback 預處理圖片"""
        try:
            # 使用統一的圖片預處理
            processed_image = preprocess_for_model(
                image=image_data,
                model_type=model_type or "smolvlm",  # 默認使用 smolvlm
                config={},
                return_format='bytes'
            )
            
            # 轉換為 base64
            base64_image = base64.b64encode(processed_image).decode('utf-8')
            
            return {
                "image_data": base64_image,
                "format": "jpeg",
                "size": len(processed_image),
                "processed": True,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return None
```

#### 1.2.2 增強型 VLM Fallback 處理器
```python
class EnhancedVLMFallbackProcessor(VLMFallbackProcessor):
    """增強型 VLM Fallback 處理器，支援圖片傳送"""
    
    def __init__(self, config: Optional[VLMFallbackConfig] = None):
        super().__init__(config)
        self.image_capture_manager = ImageCaptureManager()
        self.enable_image_fallback = config.enable_image_fallback if config else True
    
    async def process_query_with_image_fallback(self, query: str, state_data: Optional[Dict]) -> Dict:
        """
        處理查詢，支援圖片傳送的 VLM Fallback
        """
        start_time = time.time()
        self.total_queries += 1
        
        try:
            # 決策：是否使用 VLM Fallback
            should_use_fallback = self.decision_engine.should_use_vlm_fallback(query, state_data)
            
            if should_use_fallback and self.enable_image_fallback:
                # 使用增強型 VLM Fallback（包含圖片）
                result = await self._execute_enhanced_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            elif should_use_fallback:
                # 使用傳統 VLM Fallback（僅文字）
                result = await self._execute_vlm_fallback(query, state_data)
                self.fallback_queries += 1
            else:
                # 使用模板回應
                result = self._execute_template_response(query, state_data)
                self.template_queries += 1
            
            # 計算處理時間
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            
            return self._format_unified_response(result)
            
        except Exception as e:
            self.error_queries += 1
            processing_time = (time.time() - start_time) * 1000
            
            logger.error(f"Enhanced fallback processing failed: {e}")
            
            return self._format_unified_response(self._create_error_result(e, processing_time))
    
    async def _execute_enhanced_vlm_fallback(self, query: str, state_data: Optional[Dict]) -> FallbackResult:
        """
        執行包含圖片的 VLM Fallback
        """
        try:
            logger.debug(f"Executing enhanced VLM fallback for query: '{query[:50]}...'")
            
            # 獲取當前圖片
            image_data = await self.image_capture_manager.get_current_image()
            
            if image_data:
                # 執行包含圖片的 VLM Fallback
                vlm_response = await self.prompt_manager.execute_fallback_with_image(
                    query, image_data
                )
                logger.info("Enhanced VLM fallback executed with image")
            else:
                # 回退到純文字 Fallback
                vlm_response = await self.prompt_manager.execute_fallback_with_prompt_switch(query)
                logger.info("Enhanced VLM fallback executed without image (fallback to text-only)")
            
            return FallbackResult(
                response_text=vlm_response,
                query_type=self._determine_apparent_query_type(query),
                response_mode="template",  # 保持透明性
                confidence=self._calculate_apparent_confidence(state_data),
                processing_time_ms=0.0,
                decision_reason="Enhanced VLM fallback (with image)",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Enhanced VLM fallback execution failed: {e}")
            return self._create_fallback_error_result(e, query)
```

#### 1.2.3 增強型提示詞管理器
```python
class EnhancedPromptManager(PromptManager):
    """增強型提示詞管理器，支援圖片傳送"""
    
    async def execute_fallback_with_image(self, query: str, image_data: Dict) -> str:
        """
        執行包含圖片的 Fallback 流程
        """
        operation_start = datetime.now()
        
        try:
            logger.info(f"Starting enhanced fallback execution with image for query: '{query[:50]}...'")
            
            # 步驟 1：保存當前狀態追蹤提示詞
            await self._save_current_prompt()
            
            # 步驟 2：切換到包含圖片的 Fallback 提示詞
            await self._switch_to_image_fallback_prompt(query, image_data)
            
            # 步驟 3：執行包含圖片的 VLM 查詢
            response = await self._execute_vlm_query_with_image(query, image_data)
            
            # 步驟 4：恢復原始提示詞（關鍵！）
            await self._restore_original_prompt()
            
            operation_time = (datetime.now() - operation_start).total_seconds()
            logger.info(f"Enhanced fallback execution completed successfully in {operation_time:.2f}s")
            
            return response
            
        except Exception as e:
            # 確保提示詞恢復
            try:
                await self._restore_original_prompt()
            except Exception as restore_error:
                logger.error(f"Failed to restore prompt after error: {restore_error}")
            
            raise VLMFallbackError(f"Enhanced fallback execution failed: {e}")
    
    async def _switch_to_image_fallback_prompt(self, query: str, image_data: Dict) -> bool:
        """
        切換到包含圖片的 Fallback 提示詞
        """
        try:
            # 格式化包含圖片的 Fallback 提示詞
            image_fallback_prompt = self.image_fallback_prompt_template.format(
                query=query,
                image_format=image_data.get('format', 'jpeg'),
                image_size=image_data.get('size', 0)
            )
            
            # 切換 VLM 到圖片 Fallback 模式
            success = await self._update_vlm_prompt(image_fallback_prompt)
            
            if success:
                self.current_state = PromptState.IMAGE_FALLBACK
                self._record_operation("switch_to_image_fallback", True, 
                                     f"Switched to image fallback prompt for query: {query[:30]}...")
                logger.debug("Successfully switched to image fallback prompt")
                return True
            else:
                raise PromptSwitchError("Failed to update VLM prompt for image fallback")
                
        except Exception as e:
            self._record_operation("switch_to_image_fallback", False, str(e))
            logger.error(f"Failed to switch to image fallback prompt: {e}")
            raise PromptSwitchError(f"Failed to switch to image fallback prompt: {e}")
    
    async def _execute_vlm_query_with_image(self, query: str, image_data: Dict) -> str:
        """
        執行包含圖片的 VLM 查詢
        """
        try:
            # 創建包含圖片的請求載荷
            request_payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": query
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_data['format']};base64,{image_data['image_data']}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # 發送請求到 VLM 服務
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.model_server_url}/v1/chat/completions",
                    json=request_payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"VLM service error: {response.status_code}")
                
                response_data = response.json()
                
                # 提取回應文字
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    
                    # 處理不同回應格式
                    if isinstance(content, str):
                        return content.strip()
                    elif isinstance(content, list):
                        # 從列表格式提取文字
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_parts.append(item.get('text', ''))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        return ' '.join(text_parts).strip()
                    else:
                        return str(content).strip()
                else:
                    raise Exception("Invalid VLM response format")
                    
        except Exception as e:
            logger.error(f"VLM query with image execution failed: {e}")
            raise Exception(f"VLM query with image failed: {e}")
```

## 📝 實現計劃

### 階段 1：核心功能實現 (3-4 天)

#### Task 1.1: 圖片獲取管理器實現
- **文件**: `src/vlm_fallback/image_capture_manager.py`
- **子任務**:
  - [ ] 實現 `ImageCaptureManager` 類
  - [ ] 實現相機圖片獲取功能
  - [ ] 實現狀態追蹤器圖片獲取功能
  - [ ] 實現圖片預處理和緩存
  - [ ] 添加錯誤處理和降級機制
- **估計時間**: 6 小時
- **依賴**: 現有的圖片處理系統

#### Task 1.2: 增強型 VLM Fallback 處理器
- **文件**: `src/vlm_fallback/enhanced_fallback_processor.py`
- **子任務**:
  - [ ] 擴展 `VLMFallbackProcessor` 類
  - [ ] 實現 `process_query_with_image_fallback()` 方法
  - [ ] 實現 `_execute_enhanced_vlm_fallback()` 方法
  - [ ] 集成圖片獲取管理器
  - [ ] 保持向後兼容性
- **估計時間**: 4 小時
- **依賴**: Task 1.1

#### Task 1.3: 增強型提示詞管理器
- **文件**: `src/vlm_fallback/enhanced_prompt_manager.py`
- **子任務**:
  - [ ] 擴展 `PromptManager` 類
  - [ ] 實現 `execute_fallback_with_image()` 方法
  - [ ] 實現 `_switch_to_image_fallback_prompt()` 方法
  - [ ] 實現 `_execute_vlm_query_with_image()` 方法
  - [ ] 添加圖片 Fallback 提示詞模板
- **估計時間**: 5 小時
- **依賴**: Task 1.1

### 階段 2：系統集成 (2-3 天)

#### Task 2.1: 修改 QueryProcessor
- **文件**: `src/state_tracker/query_processor.py`
- **子任務**:
  - [ ] 導入增強型 VLM Fallback 處理器
  - [ ] 修改 `process_query()` 方法支援圖片 Fallback
  - [ ] 添加圖片 Fallback 配置選項
  - [ ] 保持現有功能不變
- **估計時間**: 3 小時
- **依賴**: Task 1.2

#### Task 2.2: 配置管理增強
- **文件**: `src/vlm_fallback/config.py`
- **子任務**:
  - [ ] 添加圖片 Fallback 配置選項
  - [ ] 添加圖片獲取配置
  - [ ] 添加圖片處理配置
  - [ ] 實現配置驗證
- **估計時間**: 2 小時
- **依賴**: Task 1.1

### 階段 3：測試驗證 (2-3 天)

#### Task 3.1: 單元測試
- **文件**: `tests/vlm_fallback/test_image_enhancement.py`
- **子任務**:
  - [ ] 測試圖片獲取管理器
  - [ ] 測試增強型 Fallback 處理器
  - [ ] 測試增強型提示詞管理器
  - [ ] 測試錯誤處理和降級
- **估計時間**: 4 小時

#### Task 3.2: 集成測試
- **文件**: `tests/vlm_fallback/test_image_integration.py`
- **子任務**:
  - [ ] 測試完整的圖片 Fallback 流程
  - [ ] 測試與現有系統的兼容性
  - [ ] 測試性能影響
  - [ ] 測試並發處理
- **估計時間**: 5 小時

#### Task 3.3: 端到端測試
- **文件**: `tests/e2e/test_image_fallback_e2e.py`
- **子任務**:
  - [ ] 測試真實場景的圖片 Fallback
  - [ ] 測試用戶體驗
  - [ ] 測試錯誤恢復
  - [ ] 測試性能基準
- **估計時間**: 4 小時

## 🔧 配置規格

### 配置文件增強
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
    },
    "fallback_prompts": {
      "image_fallback_template": "You are a helpful AI assistant with visual capabilities. Please analyze the provided image and answer the user's question.\n\nUser Question: {query}\n\nImage Format: {image_format}\nImage Size: {image_size} bytes\n\nPlease provide a clear, accurate, and helpful response based on both the image content and the user's question. Focus on:\n- Visual analysis of the image\n- Answering the specific question\n- Providing practical guidance when appropriate\n- Being concise but complete\n- Using a friendly and supportive tone\n\nAnswer:"
    }
  }
}
```

## 📊 性能考量

### 性能目標
- **圖片獲取時間**: < 500ms
- **圖片預處理時間**: < 1s
- **VLM 響應時間**: < 15s (包含圖片處理)
- **總響應時間**: < 20s
- **記憶體使用**: 圖片緩存 < 50MB

### 優化策略
1. **圖片緩存**: 避免重複獲取相同圖片
2. **異步處理**: 並行處理圖片獲取和預處理
3. **降級機制**: 圖片獲取失敗時回退到純文字
4. **資源管理**: 及時清理圖片緩存

## 🧪 測試策略

### 測試場景
1. **正常場景**: 圖片獲取成功，VLM 正常回應
2. **圖片獲取失敗**: 相機不可用，回退到純文字
3. **VLM 服務異常**: 圖片正常但 VLM 失敗
4. **圖片處理失敗**: 圖片格式不支援
5. **並發測試**: 多用戶同時使用圖片 Fallback

### 測試數據
- **測試圖片**: 各種格式和大小
- **測試查詢**: 視覺相關和非視覺相關
- **性能基準**: 響應時間和資源使用

## 🚀 部署計劃

### 部署階段
1. **開發環境**: 功能開發和單元測試
2. **測試環境**: 集成測試和性能測試
3. **預生產環境**: 端到端測試和用戶驗收
4. **生產環境**: 逐步部署和監控

### 監控指標
- **圖片 Fallback 使用率**
- **圖片獲取成功率**
- **VLM 響應時間**
- **錯誤率和降級率**
- **用戶滿意度**

## 📚 文檔更新

### 需要更新的文檔
1. **VLM Fallback 用戶指南**: 添加圖片功能說明
2. **開發者文檔**: 添加圖片 Fallback API 文檔
3. **配置文檔**: 添加圖片相關配置說明
4. **故障排除指南**: 添加圖片相關問題解決方案

## 🔄 向後兼容性

### 兼容性保證
1. **現有功能不變**: 純文字 Fallback 功能保持不變
2. **配置向後兼容**: 舊配置檔案仍然有效
3. **API 向後兼容**: 現有 API 接口不變
4. **用戶體驗一致**: 用戶無法感知內部變化

### 遷移策略
1. **漸進式啟用**: 可配置啟用圖片 Fallback
2. **降級機制**: 圖片功能失敗時自動降級
3. **監控告警**: 及時發現和處理問題
4. **回滾計劃**: 問題時快速回滾到純文字模式

---

**總結**: 這個增強功能將顯著提升 VLM Fallback 系統的能力，使其能夠提供基於視覺上下文的智能回應，同時保持系統的穩定性和向後兼容性。 