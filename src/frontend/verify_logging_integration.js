#!/usr/bin/env node
/**
 * 前端日誌記錄整合驗證腳本
 * 
 * 檢查前端HTML文件中是否正確整合了日誌記錄功能
 */

const fs = require('fs');
const path = require('path');

class FrontendLoggingVerifier {
    constructor() {
        this.indexHtmlPath = path.join(__dirname, 'index.html');
        this.testResults = {
            frontendLoggerClass: false,
            eyesCaptureLogging: false,
            eyesPromptLogging: false,
            eyesTransferLogging: false,
            userActionLogging: false,
            errorLogging: false,
            eventListeners: false
        };
    }
    
    async verifyIntegration() {
        console.log('🔍 驗證前端日誌記錄整合');
        console.log('=' * 50);
        
        try {
            // 讀取HTML文件
            const htmlContent = fs.readFileSync(this.indexHtmlPath, 'utf8');
            
            // 檢查各項功能
            this.checkFrontendLoggerClass(htmlContent);
            this.checkEyesCaptureLogging(htmlContent);
            this.checkEyesPromptLogging(htmlContent);
            this.checkEyesTransferLogging(htmlContent);
            this.checkUserActionLogging(htmlContent);
            this.checkErrorLogging(htmlContent);
            this.checkEventListeners(htmlContent);
            
            // 顯示結果
            this.displayResults();
            
            return this.calculateSuccessRate();
            
        } catch (error) {
            console.error('❌ 驗證過程中發生錯誤:', error.message);
            return false;
        }
    }
    
    checkFrontendLoggerClass(content) {
        const checks = [
            'class FrontendVisualLogger',
            'generateObservationId()',
            'logEyesCapture(',
            'logEyesPrompt(',
            'logEyesTransfer(',
            'logUserAction(',
            'logError('
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.frontendLoggerClass = foundChecks.length === checks.length;
        
        console.log(`📋 FrontendVisualLogger 類別: ${this.testResults.frontendLoggerClass ? '✅' : '❌'}`);
        if (!this.testResults.frontendLoggerClass) {
            console.log(`   缺少: ${checks.filter(check => !content.includes(check)).join(', ')}`);
        }
    }
    
    checkEyesCaptureLogging(content) {
        const checks = [
            'frontendLogger.logEyesCapture(',
            'observation_id:',
            'request_id:',
            'device:',
            'resolution:',
            'quality:',
            'format:',
            'size:'
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.eyesCaptureLogging = foundChecks.length >= 6; // 至少要有主要的檢查項目
        
        console.log(`📸 圖像捕獲日誌: ${this.testResults.eyesCaptureLogging ? '✅' : '❌'}`);
        if (!this.testResults.eyesCaptureLogging) {
            console.log(`   缺少: ${checks.filter(check => !content.includes(check)).join(', ')}`);
        }
    }
    
    checkEyesPromptLogging(content) {
        const checks = [
            'frontendLogger.logEyesPrompt(',
            'observationId',
            'instruction'
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.eyesPromptLogging = foundChecks.length === checks.length;
        
        console.log(`💬 視覺提示詞日誌: ${this.testResults.eyesPromptLogging ? '✅' : '❌'}`);
    }
    
    checkEyesTransferLogging(content) {
        const checks = [
            'frontendLogger.logEyesTransfer(',
            'transferData'
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.eyesTransferLogging = foundChecks.length === checks.length;
        
        console.log(`📤 後端傳輸日誌: ${this.testResults.eyesTransferLogging ? '✅' : '❌'}`);
    }
    
    checkUserActionLogging(content) {
        const checks = [
            'frontendLogger.logUserAction(',
            'start_processing',
            'stop_processing',
            'camera_change'
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.userActionLogging = foundChecks.length >= 3;
        
        console.log(`👤 用戶操作日誌: ${this.testResults.userActionLogging ? '✅' : '❌'}`);
    }
    
    checkErrorLogging(content) {
        const checks = [
            'frontendLogger.logError(',
            'vlm_request',
            'image_capture'
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.errorLogging = foundChecks.length >= 2;
        
        console.log(`❌ 錯誤日誌: ${this.testResults.errorLogging ? '✅' : '❌'}`);
    }
    
    checkEventListeners(content) {
        const checks = [
            'addEventListener(\'load\'',
            'addEventListener(\'error\'',
            'frontendLogger'
        ];
        
        const foundChecks = checks.filter(check => content.includes(check));
        this.testResults.eventListeners = foundChecks.length === checks.length;
        
        console.log(`🎧 事件監聽器: ${this.testResults.eventListeners ? '✅' : '❌'}`);
    }
    
    displayResults() {
        console.log('\n' + '=' * 50);
        console.log('📊 驗證結果摘要');
        console.log('=' * 50);
        
        const totalTests = Object.keys(this.testResults).length;
        const passedTests = Object.values(this.testResults).filter(result => result).length;
        const successRate = (passedTests / totalTests * 100).toFixed(1);
        
        console.log(`總測試項目: ${totalTests}`);
        console.log(`通過測試: ${passedTests}`);
        console.log(`成功率: ${successRate}%`);
        
        if (passedTests === totalTests) {
            console.log('\n🎉 所有日誌記錄功能都已正確整合！');
        } else {
            console.log('\n⚠️ 部分功能需要檢查，請查看上述詳細結果。');
        }
    }
    
    calculateSuccessRate() {
        const totalTests = Object.keys(this.testResults).length;
        const passedTests = Object.values(this.testResults).filter(result => result).length;
        return passedTests === totalTests;
    }
}

// 執行驗證
async function main() {
    const verifier = new FrontendLoggingVerifier();
    const success = await verifier.verifyIntegration();
    process.exit(success ? 0 : 1);
}

if (require.main === module) {
    main();
}