#!/usr/bin/env python3
"""
Backend VLM Processing Logging Integration Validation Script

Check if visual logging functionality is correctly integrated in backend main.py
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
        """Validate backend integration"""
        print('🔍 Validating Backend VLM Processing Logging Integration')
        print('=' * 50)
        
        try:
            # Read backend file
            with open(self.backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            # Check various integrations
            self.check_visual_logger_import(backend_content)
            self.check_observation_id_generation(backend_content)
            self.check_backend_receive_logging(backend_content)
            self.check_image_processing_logging(backend_content)
            self.check_vlm_logging(backend_content)
            self.check_rag_data_transfer_logging(backend_content)
            self.check_state_tracker_integration_logging(backend_content)
            self.check_performance_metrics_logging(backend_content)
            self.check_error_handling_logging(backend_content)
            
            # Display results
            self.display_results()
            
            return self.calculate_success_rate()
            
        except Exception as e:
            print(f'❌ Error occurred during validation: {e}')
            return False
    
    def check_visual_logger_import(self, content):
        """Check visual logger import"""
        checks = [
            'from visual_logger import get_visual_logger',
            'visual_logger = get_visual_logger()'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['visual_logger_import'] = len(passed_checks) >= 1
        
        print(f"📋 Visual logger import: {'✅' if self.validation_results['visual_logger_import'] else '❌'}")
        if not self.validation_results['visual_logger_import']:
            print(f"   Missing: {[check for check in checks if check not in content]}")
    
    def check_observation_id_generation(self, content):
        """Check observation ID generation"""
        checks = [
            'observation_id = f"obs_',
            'uuid.uuid4().hex[:8]'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['observation_id_generation'] = len(passed_checks) == len(checks)
        
        print(f"🆔 Observation ID generation: {'✅' if self.validation_results['observation_id_generation'] else '❌'}")
    
    def check_backend_receive_logging(self, content):
        """Check backend receive logging"""
        checks = [
            'log_backend_receive',
            'observation_id',
            'request_id'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['backend_receive_logging'] = len(passed_checks) == len(checks)
        
        print(f"📥 Backend receive logging: {'✅' if self.validation_results['backend_receive_logging'] else '❌'}")
    
    def check_image_processing_logging(self, content):
        """Check image processing logging"""
        checks = [
            'log_image_processing_start',
            'log_image_processing_result'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['image_processing_logging'] = len(passed_checks) == len(checks)
        
        print(f"🖼️ Image processing logging: {'✅' if self.validation_results['image_processing_logging'] else '❌'}")
    
    def check_vlm_logging(self, content):
        """Check VLM request and response logging"""
        checks = [
            'log_vlm_request',
            'log_vlm_response'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['vlm_request_logging'] = 'log_vlm_request' in content
        self.validation_results['vlm_response_logging'] = 'log_vlm_response' in content
        
        print(f"🤖 VLM request logging: {'✅' if self.validation_results['vlm_request_logging'] else '❌'}")
        print(f"🤖 VLM response logging: {'✅' if self.validation_results['vlm_response_logging'] else '❌'}")
    
    def check_rag_data_transfer_logging(self, content):
        """Check RAG data transfer logging"""
        checks = [
            'log_rag_data_transfer'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['rag_data_transfer_logging'] = len(passed_checks) > 0
        
        print(f"🔄 RAG data transfer logging: {'✅' if self.validation_results['rag_data_transfer_logging'] else '❌'}")
    
    def check_state_tracker_integration_logging(self, content):
        """Check state tracker integration logging"""
        checks = [
            'log_state_tracker_integration'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['state_tracker_integration_logging'] = len(passed_checks) > 0
        
        print(f"📊 State tracker integration logging: {'✅' if self.validation_results['state_tracker_integration_logging'] else '❌'}")
    
    def check_performance_metrics_logging(self, content):
        """Check performance metrics logging"""
        checks = [
            'log_performance_metric'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['performance_metrics_logging'] = len(passed_checks) > 0
        
        print(f"⚡ Performance metrics logging: {'✅' if self.validation_results['performance_metrics_logging'] else '❌'}")
    
    def check_error_handling_logging(self, content):
        """Check error handling logging"""
        checks = [
            'visual_logger.log_error'
        ]
        
        passed_checks = [check for check in checks if check in content]
        self.validation_results['error_handling_logging'] = len(passed_checks) > 0
        
        print(f"❌ Error handling logging: {'✅' if self.validation_results['error_handling_logging'] else '❌'}")
    
    def display_results(self):
        """Display validation results"""
        print('\n' + '=' * 50)
        print('📊 Backend VLM Processing Logging Integration Validation Results')
        print('=' * 50)
        
        total_checks = len(self.validation_results)
        passed_checks = sum(self.validation_results.values())
        success_rate = (passed_checks / total_checks * 100)
        
        print(f'Total checks: {total_checks}')
        print(f'Passed checks: {passed_checks}')
        print(f'Success rate: {success_rate:.1f}%')
        
        if passed_checks == total_checks:
            print('\n🎉 All VLM processing logging functionality correctly integrated!')
        else:
            print('\n⚠️ Some functionality needs checking, please review detailed results above.')
            
            # Display failed checks
            failed_checks = [key for key, value in self.validation_results.items() if not value]
            if failed_checks:
                print('\nFailed check items:')
                for check in failed_checks:
                    print(f'  - {check.replace("_", " ").title()}')
    
    def calculate_success_rate(self):
        """Calculate success rate"""
        total_checks = len(self.validation_results)
        passed_checks = sum(self.validation_results.values())
        return passed_checks == total_checks

# Execute validation
def main():
    validator = BackendIntegrationValidator()
    success = validator.validate_integration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()