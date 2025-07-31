#!/usr/bin/env python3
"""
後端VLM處理日誌記錄整合驗證腳本

檢查後端main.py中是否正確整合了視覺日誌記錄功能
"""

import os
import sys
from pathlib import Path

class BackendIntegrationValidator:
    def __init__(self):
        self.backend_path = Path(__file__).parent.parent / "backend" / "main.py"
        self.validation_results = {
            'visual_logger_import': False,
            'observation_id_generation': False,
            'backend_receive_logging': False,
            'image_processing_logging': False,
            'vlm_request_logging': False,
            'vlm_response_logging': False,
            'rag_data_transfer_logging': False,
            'state_tracker_integration_logging': False,
            'performance_metrics_logging': False,
            'error_handling_logging': False
        }
    
    def validate_integration(self):
        """驗證後端整合"""
        print('🔍 驗證後端VLM處理日誌記錄整合')
        print('=' * 50)
        
        try:
            # 讀取後端文件
            with open(self.backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            # 檢查各項整合
            self.check_visual_logger_import(backend_content)
            self.check_observation_id_generation(backend_content)
            self.check_backend_receive_logging(backend_content)
            self.check_image_processing_logging(backend_content)
            self.check_vlm_logging(backend_content)
            self.check_rag_data_transfer_logging(backend_content)
            self.check_state_tracker_integration_logging(backend_content)
            self.check_performance_metrics_logging(backend_content)
            self.check_error_handling_logging(backend_content)
            
            # 顯示結果
            self.display_results()
            
            return self.calculate_success_rate()
            
        except Exception as e:
            print(f'❌ 驗證過程中發生錯誤: {e}')
            return False
    
    def check_visual_logger_import(self, content):
        """檢查視覺日誌記錄器導入"""
        checks = [
            'from visual_logger import get_visual_logger',
            'visual_logger = get_visual_logger()'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['visual_logger_import'] = len(passed_checks) >= 1
        
        print(f"📋 視覺日誌記錄器導入: {'✅' if self.validation_results['visual_logger_import'] else '❌'}")
        if not self.validation_results['visual_logger_import']:
            print(f"   缺少: {[check for check in checks if check not in content]}")
    
    def check_observation_id_generation(self, content):
        """檢查觀察ID生成"""
        checks = [
            'observation_id = f"obs_',
            'uuid.uuid4().hex[:8]'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['observation_id_generation'] = len(passed_checks) == len(checks)
        
        print(f"🆔 觀察ID生成: {'✅' if self.validation_results['observation_id_generation'] else '❌'}")
    
    def check_backend_receive_logging(self, content):
        """檢查後端接收日誌記錄"""
        checks = [
            'log_backend_receive',
            'observation_id',
            'request_id'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['backend_receive_logging'] = len(passed_checks) == len(checks)
        
        print(f"📥 後端接收日誌: {'✅' if self.validation_results['backend_receive_logging'] else '❌'}")
    
    def check_image_processing_logging(self, content):
        """檢查圖像處理日誌記錄"""
        checks = [
            'log_image_processing_start',
            'log_image_processing_result'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['image_processing_logging'] = len(passed_checks) == len(checks)
        
        print(f"🖼️ 圖像處理日誌: {'✅' if self.validation_results['image_processing_logging'] else '❌'}")
    
    def check_vlm_logging(self, content):
        """檢查VLM請求和回應日誌記錄"""
        checks = [
            'log_vlm_request',
            'log_vlm_response'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['vlm_request_logging'] = 'log_vlm_request' in content
        self.validation_results['vlm_response_logging'] = 'log_vlm_response' in content
        
        print(f"🤖 VLM請求日誌: {'✅' if self.validation_results['vlm_request_logging'] else '❌'}")
        print(f"🤖 VLM回應日誌: {'✅' if self.validation_results['vlm_response_logging'] else '❌'}")
    
    def check_rag_data_transfer_logging(self, content):
        """檢查RAG資料傳遞日誌記錄"""
        checks = [
            'log_rag_data_transfer'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['rag_data_transfer_logging'] = len(passed_checks) > 0
        
        print(f"🔄 RAG資料傳遞日誌: {'✅' if self.validation_results['rag_data_transfer_logging'] else '❌'}")
    
    def check_state_tracker_integration_logging(self, content):
        """檢查狀態追蹤器整合日誌記錄"""
        checks = [
            'log_state_tracker_integration'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['state_tracker_integration_logging'] = len(passed_checks) > 0
        
        print(f"📊 狀態追蹤器整合日誌: {'✅' if self.validation_results['state_tracker_integration_logging'] else '❌'}")
    
    def check_performance_metrics_logging(self, content):
        """檢查性能指標日誌記錄"""
        checks = [
            'log_performance_metric'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['performance_metrics_logging'] = len(passed_checks) > 0
        
        print(f"⚡ 性能指標日誌: {'✅' if self.validation_results['performance_metrics_logging'] else '❌'}")
    
    def check_error_handling_logging(self, content):
        """檢查錯誤處理日誌記錄"""
        checks = [
            'visual_logger.log_error'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['error_handling_logging'] = len(passed_checks) > 0
        
        print(f"❌ 錯誤處理日誌: {'✅' if self.validation_results['error_handling_logging'] else '❌'}")
    
    def display_results(self):
        """顯示驗證結果"""
        print('\n' + '=' * 50)
        print('📊 後端VLM處理日誌記錄整合驗證結果')
        print('=' * 50)
        
        total_checks = len(self.validation_results)
        passed_checks = sum(self.validation_results.values())
        success_rate = (passed_checks / total_checks * 100)
        
        print(f'總檢查項目: {total_checks}')
        print(f'通過檢查: {passed_checks}')
        print(f'成功率: {success_rate:.1f}%')
        
        if passed_checks == total_checks:
            print('\n🎉 所有VLM處理日誌記錄功能都已正確整合！')
        else:
            print('\n⚠️ 部分功能需要檢查，請查看上述詳細結果。')
            
            # 顯示未通過的檢查
            failed_checks = [key for key, value in self.validation_results.items() if not value]
            if failed_checks:
                print('\n未通過的檢查項目:')
                for check in failed_checks:
                    print(f'  - {check.replace("_", " ").title()}')
    
    def calculate_success_rate(self):
        """計算成功率"""
        total_checks = len(self.validation_results)
        passed_checks = sum(self.validation_results.values())
        return passed_checks == total_checks

# 執行驗證
def main():
    validator = BackendIntegrationValidator()
    success = validator.validate_integration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()