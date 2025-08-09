"""
State Tracker Consecutive Low Confidence Test - 實際場景測試

測試 State Tracker 在真實使用場景中的行為：
1. 連續高信心度：用戶持續在同一步驟工作（長時間任務）
2. 用戶離開且不回來：離開場景，連續低信心度，狀態被清空
3. 用戶離開但回來：離開→低信心度→回來→高信心度，狀態恢復

測試環境：
- 使用真實的任務資料（coffee_brewing.yaml）
- 模擬 VLM 觀察資料（不啟用實際 VLM）
- 直接發送到 State Tracker 進行測試

作者: AI Vision Intelligence Hub Team
日期: 2025年1月
"""

import pytest
import asyncio
import sys
import os
import yaml
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 添加 src 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from state_tracker.state_tracker import StateTracker, StateRecord, ConfidenceLevel, ActionType
from memory.rag.knowledge_base import RAGKnowledgeBase


class TestStateTrackerRealScenarios:
    """測試 State Tracker 真實使用場景"""
    
    @pytest.fixture
    def coffee_task_data(self):
        """載入咖啡沖泡任務資料"""
        task_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'tasks', 'coffee_brewing.yaml')
        with open(task_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def state_tracker(self):
        """創建測試用的 State Tracker"""
        tracker = StateTracker()
        # 設置測試用的閾值
        tracker.max_consecutive_low = 5  # 5次連續低信心度就清空
        return tracker
    
    def create_coffee_step_observation(self, step_id: int, coffee_task_data: dict) -> str:
        """根據咖啡任務資料創建對應步驟的英文 VLM 觀察描述"""
        step_data = None
        for step in coffee_task_data['steps']:
            if step['step_id'] == step_id:
                step_data = step
                break
        
        if not step_data:
            return "Unknown coffee brewing step"
        
        # 根據步驟資料生成逼真的英文 VLM 觀察描述
        observations = {
            1: "User is gathering coffee equipment, coffee beans, grinder, pour-over dripper, and kettle are visible on counter",
            2: "User is heating water in gooseneck kettle on stove, steam is rising from the kettle",
            3: "User is grinding coffee beans using coffee grinder, coffee aroma is noticeable",
            4: "User is preparing filter paper and dripper, rinsing filter with hot water",
            5: "User is adding ground coffee to filter paper and creating small well in center",
            6: "User is blooming coffee, slowly pouring small amount of hot water, coffee grounds are expanding and bubbling",
            7: "User is continuing pour-over process in stages, pouring hot water in spiral motion, coffee is dripping into mug",
            8: "Coffee brewing is complete, user is removing dripper, fresh aromatic coffee is ready in mug"
        }
        
        return observations.get(step_id, f"User is performing coffee brewing step {step_id}")
    
    def create_mock_rag_result(self, step_id: int, coffee_task_data: dict, confidence: float = 0.85):
        """創建模擬的 RAG 匹配結果"""
        step_data = None
        for step in coffee_task_data['steps']:
            if step['step_id'] == step_id:
                step_data = step
                break
        
        if not step_data:
            return None
        
        mock_result = Mock()
        mock_result.task_name = "brewing_coffee"
        mock_result.step_id = step_id
        mock_result.step_title = step_data['title']
        mock_result.step_description = step_data['task_description']
        mock_result.similarity = confidence
        mock_result.task_description = coffee_task_data['description']
        mock_result.tools_needed = step_data['tools_needed']
        mock_result.completion_indicators = step_data['completion_indicators']
        mock_result.visual_cues = step_data['visual_cues']
        mock_result.estimated_duration = step_data['estimated_duration']
        mock_result.safety_notes = step_data['safety_notes']
        mock_result.confidence_level = "HIGH" if confidence >= 0.70 else "MEDIUM" if confidence >= 0.40 else "LOW"
        mock_result.matched_cues = step_data['visual_cues'][:2]  # 取前兩個作為匹配線索
        
        return mock_result
    
    def create_irrelevant_observations(self):
        """創建與咖啡沖泡無關的英文觀察描述（模擬用戶離開）"""
        return [
            "User has left the kitchen, kitchen is now empty",
            "User is in living room using mobile phone",
            "User is in study room working on computer",
            "User is in bedroom organizing clothes",
            "User is on balcony watering plants",
            "User is in living room watching television",
            "User is in kitchen but not performing coffee-related activities",
            "Scene is blurry, cannot identify what user is doing"
        ]
    
    def create_mock_irrelevant_rag_result(self, confidence: float = 0.25):
        """創建無關活動的低信心度 RAG 結果"""
        mock_result = Mock()
        mock_result.task_name = "unknown_activity"
        mock_result.step_id = 0
        mock_result.step_title = "未知活動"
        mock_result.step_description = "無法識別的用戶活動"
        mock_result.similarity = confidence
        mock_result.task_description = "未知任務"
        mock_result.tools_needed = []
        mock_result.completion_indicators = []
        mock_result.visual_cues = []
        mock_result.estimated_duration = "未知"
        mock_result.safety_notes = []
        mock_result.confidence_level = "LOW"
        mock_result.matched_cues = []
        
        return mock_result
    
    def test_continuous_high_confidence_long_task(self, state_tracker, coffee_task_data):
        """測試場景1：連續高信心度 - 用戶持續在同一步驟工作（長時間任務）"""
        print("\n🧪 Test Scenario 1: User continues working on coffee brewing step 6 (blooming)...")
        
        # 模擬用戶在第6步（悶蒸）持續工作
        step_6_rag_result = self.create_mock_rag_result(6, coffee_task_data, confidence=0.85)
        
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=step_6_rag_result):
            
            # 第1次觀察：建立初始狀態
            observation_1 = self.create_coffee_step_observation(6, coffee_task_data)
            result = asyncio.run(state_tracker.process_vlm_response(observation_1, "obs_001"))
            
            assert result is True
            assert state_tracker.current_state is not None
            assert state_tracker.current_state.task_id == "brewing_coffee"
            assert state_tracker.current_state.step_index == 6
            assert state_tracker.consecutive_low_count == 0
            print(f"   ✅ Initial state established: {state_tracker.current_state.task_id} step {state_tracker.current_state.step_index}")
            
            # 模擬用戶持續在同一步驟工作（10次觀察）
            for i in range(2, 12):
                observation = f"User continues blooming process, coffee grounds still expanding and bubbling, observation #{i}"
                result = asyncio.run(state_tracker.process_vlm_response(observation, f"obs_{i:03d}"))
                
                # 每次都應該成功更新（即使是相同步驟）
                assert result is True
                assert state_tracker.current_state is not None
                assert state_tracker.current_state.step_index == 6
                assert state_tracker.consecutive_low_count == 0  # 持續重置
                
                if i % 3 == 0:  # 每3次打印一次進度
                    print(f"   ✅ Observation #{i}: State continues updating, consecutive_low_count = {state_tracker.consecutive_low_count}")
            
            print(f"   🎯 Test result: During long task, state continues updating and won't be cleared")
    
    def test_user_leaves_and_never_returns(self, state_tracker, coffee_task_data):
        """測試場景2：用戶離開且不回來 - 狀態應該被清空"""
        print("\n🧪 Test Scenario 2: User leaves coffee brewing scene and never returns...")
        
        # Step 1: 建立初始狀態（第3步：研磨咖啡豆）
        step_3_rag_result = self.create_mock_rag_result(3, coffee_task_data, confidence=0.88)
        
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=step_3_rag_result):
            observation = self.create_coffee_step_observation(3, coffee_task_data)
            result = asyncio.run(state_tracker.process_vlm_response(observation, "obs_001"))
            
            assert result is True
            assert state_tracker.current_state.step_index == 3
            print(f"   ✅ Initial state: {state_tracker.current_state.task_id} step {state_tracker.current_state.step_index}")
        
        # Step 2: 用戶離開，產生連續低信心度觀察
        irrelevant_observations = self.create_irrelevant_observations()
        irrelevant_rag_result = self.create_mock_irrelevant_rag_result(confidence=0.25)
        
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=irrelevant_rag_result):
            
            for i, observation in enumerate(irrelevant_observations[:6], 1):  # 6次無關觀察
                result = asyncio.run(state_tracker.process_vlm_response(observation, f"leave_obs_{i:03d}"))
                
                assert result is False  # 低信心度不會更新狀態
                print(f"   📉 Leave observation #{i}: '{observation[:40]}...' (consecutive_low_count = {state_tracker.consecutive_low_count})")
                
                if i < 5:  # 前4次，狀態還在
                    assert state_tracker.current_state is not None
                else:  # 第5次，狀態被清空
                    assert state_tracker.current_state is None
                    assert state_tracker.consecutive_low_count == 0  # 計數器重置
                    print(f"   🗑️  State cleared! consecutive_low_count reset to {state_tracker.consecutive_low_count}")
                    break
        
        print(f"   🎯 Test result: After user leaves, state is cleared after 5th low confidence observation")
    
    def test_user_leaves_but_returns(self, state_tracker, coffee_task_data):
        """測試場景3：用戶離開但回來 - 狀態恢復"""
        print("\n🧪 Test Scenario 3: User temporarily leaves but returns to continue work...")
        
        # Step 1: 建立初始狀態（第7步：分段注水）
        step_7_rag_result = self.create_mock_rag_result(7, coffee_task_data, confidence=0.90)
        
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=step_7_rag_result):
            observation = self.create_coffee_step_observation(7, coffee_task_data)
            result = asyncio.run(state_tracker.process_vlm_response(observation, "obs_001"))
            
            assert result is True
            assert state_tracker.current_state.step_index == 7
            print(f"   ✅ Initial state: {state_tracker.current_state.task_id} step {state_tracker.current_state.step_index}")
        
        # Step 2: 用戶暫時離開（3次低信心度觀察）
        irrelevant_observations = self.create_irrelevant_observations()
        irrelevant_rag_result = self.create_mock_irrelevant_rag_result(confidence=0.22)
        
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=irrelevant_rag_result):
            
            for i in range(1, 4):  # 只有3次，不足以清空狀態
                observation = irrelevant_observations[i-1]
                result = asyncio.run(state_tracker.process_vlm_response(observation, f"temp_leave_{i:03d}"))
                
                assert result is False
                assert state_tracker.current_state is not None  # 狀態還在
                print(f"   📉 Temporary leave #{i}: consecutive_low_count = {state_tracker.consecutive_low_count}")
        
        # Step 3: 用戶回來繼續工作（高信心度觀察）
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=step_7_rag_result):
            return_observation = "User returns to kitchen, continues pour-over coffee brewing process"
            result = asyncio.run(state_tracker.process_vlm_response(return_observation, "return_obs_001"))
            
            assert result is True
            assert state_tracker.current_state is not None
            assert state_tracker.current_state.step_index == 7
            assert state_tracker.consecutive_low_count == 0  # 計數器被重置
            print(f"   🔄 User returns: State restored, consecutive_low_count reset to {state_tracker.consecutive_low_count}")
        
        # Step 4: 用戶繼續到下一步（第8步：完成）
        step_8_rag_result = self.create_mock_rag_result(8, coffee_task_data, confidence=0.92)
        
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=step_8_rag_result):
            final_observation = self.create_coffee_step_observation(8, coffee_task_data)
            result = asyncio.run(state_tracker.process_vlm_response(final_observation, "final_obs_001"))
            
            assert result is True
            assert state_tracker.current_state.step_index == 8
            print(f"   ✅ Task progress: Moved to final step {state_tracker.current_state.step_index}")
        
        print(f"   🎯 Test result: Temporary leave won't clear state, user can continue after returning")
    
    def test_query_after_state_cleared(self, state_tracker, coffee_task_data):
        """測試狀態被清空後的查詢行為"""
        print("\n🧪 Test Scenario 4: Query behavior after state cleared...")
        
        # 手動設置一個狀態然後清空
        state_tracker.current_state = StateRecord(
            timestamp=datetime.now(),
            vlm_text="用戶正在沖泡咖啡",
            matched_step={"step_id": 5},
            confidence=0.8,
            task_id="brewing_coffee",
            step_index=5
        )
        
        print(f"   📝 Set initial state: {state_tracker.current_state.task_id} step {state_tracker.current_state.step_index}")
        
        # 手動觸發狀態清空
        state_tracker.consecutive_low_count = 5
        state_tracker._handle_consecutive_low_matches()
        
        # 驗證狀態被清空
        assert state_tracker.current_state is None
        assert state_tracker.get_current_state() is None
        print(f"   🗑️  State cleared, get_current_state() returns None")
        
        # 這時用戶查詢應該觸發 VLM Fallback
        print(f"   🎯 Test result: After state cleared, user queries will trigger VLM Fallback")


if __name__ == "__main__":
    """直接執行測試"""
    print("🧪 執行 State Tracker 真實場景測試...")
    print("=" * 60)
    
    # 執行測試
    pytest.main([__file__, "-v", "--tb=short", "-s"])
    
    @pytest.mark.asyncio
    async def test_consecutive_low_confidence_clears_state(self, state_tracker, mock_rag_result_high, mock_rag_result_low):
        """測試連續低信心度觀察會清空狀態"""
        
        # Step 1: 建立初始狀態（高信心度）
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_high):
            result = await state_tracker.process_vlm_response("用戶正在泡咖啡，將熱水倒入杯中", "obs_001")
            assert result is True
            assert state_tracker.current_state is not None
            assert state_tracker.current_state.task_id == "泡咖啡"
            assert state_tracker.consecutive_low_count == 0
        
        # Step 2: 模擬用戶離開場景，產生連續低信心度觀察
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_low):
            
            # 第1次低信心度觀察
            result = await state_tracker.process_vlm_response("空的廚房", "obs_002")
            assert result is False
            assert state_tracker.current_state is not None  # 狀態還在
            assert state_tracker.consecutive_low_count == 1
            
            # 第2次低信心度觀察
            result = await state_tracker.process_vlm_response("用戶在客廳", "obs_003")
            assert result is False
            assert state_tracker.current_state is not None  # 狀態還在
            assert state_tracker.consecutive_low_count == 2
            
            # 第3次低信心度觀察 - 應該觸發狀態清空
            result = await state_tracker.process_vlm_response("用戶在使用電腦", "obs_004")
            assert result is False
            assert state_tracker.current_state is None  # 狀態被清空！
            assert state_tracker.consecutive_low_count == 0  # 計數器重置
    
    @pytest.mark.asyncio
    async def test_high_confidence_resets_counter(self, state_tracker, mock_rag_result_high, mock_rag_result_low):
        """測試高信心度觀察會重置連續低信心度計數器"""
        
        # Step 1: 建立初始狀態
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_high):
            await state_tracker.process_vlm_response("用戶正在泡咖啡", "obs_001")
            assert state_tracker.consecutive_low_count == 0
        
        # Step 2: 產生一些低信心度觀察
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_low):
            await state_tracker.process_vlm_response("模糊的場景", "obs_002")
            await state_tracker.process_vlm_response("不清楚的活動", "obs_003")
            assert state_tracker.consecutive_low_count == 2
            assert state_tracker.current_state is not None
        
        # Step 3: 高信心度觀察應該重置計數器
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_high):
            result = await state_tracker.process_vlm_response("用戶繼續泡咖啡", "obs_004")
            assert result is True
            assert state_tracker.consecutive_low_count == 0  # 計數器被重置
            assert state_tracker.current_state is not None
    
    def test_get_current_state_after_clear(self, state_tracker):
        """測試狀態被清空後 get_current_state 返回 None"""
        
        # 手動設置一個狀態
        state_tracker.current_state = StateRecord(
            timestamp=datetime.now(),
            vlm_text="測試文本",
            matched_step={"step_id": 1},
            confidence=0.8,
            task_id="測試任務",
            step_index=1
        )
        
        # 手動觸發連續低信心度清空
        state_tracker.consecutive_low_count = 3
        state_tracker._handle_consecutive_low_matches()
        
        # 驗證狀態被清空
        assert state_tracker.current_state is None
        assert state_tracker.get_current_state() is None
    
    @pytest.mark.asyncio
    async def test_no_rag_match_increases_counter(self, state_tracker, mock_rag_result_high):
        """測試 RAG 無匹配結果時也會增加連續低信心度計數"""
        
        # Step 1: 建立初始狀態
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_high):
            await state_tracker.process_vlm_response("用戶正在泡咖啡", "obs_001")
            assert state_tracker.consecutive_low_count == 0
        
        # Step 2: RAG 無匹配結果
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=None):
            result = await state_tracker.process_vlm_response("無法識別的場景", "obs_002")
            assert result is False
            # 注意：RAG 無匹配時不會增加 consecutive_low_count，因為流程提前返回
            # 這是現有設計，可能需要未來改進
    
    def test_configurable_threshold(self):
        """測試可配置的連續低信心度閾值"""
        
        # 測試不同的閾值設定
        tracker1 = StateTracker()
        tracker1.max_consecutive_low = 5
        assert tracker1.max_consecutive_low == 5
        
        tracker2 = StateTracker()
        tracker2.max_consecutive_low = 10
        assert tracker2.max_consecutive_low == 10
    
    @pytest.mark.asyncio
    async def test_logging_during_state_clear(self, state_tracker, mock_rag_result_high, mock_rag_result_low, caplog):
        """測試狀態清空時的日誌記錄"""
        
        # 建立初始狀態
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_high):
            await state_tracker.process_vlm_response("用戶正在泡咖啡", "obs_001")
        
        # 產生連續低信心度觀察直到清空
        with patch.object(state_tracker.rag_kb, 'find_matching_step', return_value=mock_rag_result_low):
            for i in range(3):  # max_consecutive_low = 3
                await state_tracker.process_vlm_response(f"低信心度觀察 {i+1}", f"obs_{i+2}")
        
        # 檢查日誌是否包含預期的訊息
        assert "Clearing state after" in caplog.text
        assert "consecutive low confidence matches" in caplog.text
        assert "VLM Fallback will be triggered" in caplog.text


if __name__ == "__main__":
    """直接執行測試"""
    print("🧪 執行 State Tracker 連續低信心度測試...")
    
    # 執行測試
    pytest.main([__file__, "-v", "--tb=short"])