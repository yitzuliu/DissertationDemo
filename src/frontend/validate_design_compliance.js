#!/usr/bin/env node
/**
 * 設計規格合規性驗證腳本
 * 
 * 檢查前端日誌記錄實現是否完全符合設計文檔 3.2 視覺觀察日誌的要求
 */

const fs = require('fs');
const path = require('path');

class DesignComplianceValidator {
    constructor() {
        this.indexHtmlPath = path.join(__dirname, 'index.html');
        this.designRequirements = {
            EYES_CAPTURE: {
                required_fields: ['observation_id', 'request_id', 'device', 'resolution', 'quality', 'format', 'size'],
                description: '圖像捕獲事件'
            },
            EYES_PROMPT: {
                required_fields: ['observation_id', 'prompt', 'length'],
                description: '視覺提示詞事件'
            },
            EYES_TRANSFER: {
                required_fields: ['observation_id', 'sent_to_backend'],
                description: '後端傳輸事件'
            }
        };
        this.validationResults = {};
    }

    async validateCompliance() {
        console.log('🔍 驗證設計規格合規性');
        console.log('=' * 50);

        try {
            const htmlContent = fs.readFileSync(this.indexHtmlPath, 'utf8');

            // 檢查每個日誌事件類型
            for (const [eventType, requirements] of Object.entries(this.designRequirements)) {
                this.validateEventType(htmlContent, eventType, requirements);
            }

            // 檢查ID追蹤機制
            this.validateIdTracking(htmlContent);

            // 檢查時間戳格式
            this.validateTimestampFormat(htmlContent);

            // 顯示結果
            this.displayResults();

            return this.calculateOverallCompliance();

        } catch (error) {
            console.error('❌ 驗證過程中發生錯誤:', error.message);
            return false;
        }
    }

    validateEventType(content, eventType, requirements) {
        console.log(`\\n📋 驗證 ${eventType} (${requirements.description})`);

        const results = {
            method_exists: false,
            method_called: false,
            required_fields: {},
            field_compliance: 0
        };

        // 檢查方法是否存在
        const methodName = `log${eventType.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join('')}`;

        if (content.includes(`${methodName}(`)) {
            results.method_exists = true;
            console.log(`   ✅ ${eventType} 方法存在`);
        } else {
            console.log(`   ❌ ${eventType} 方法不存在`);
        }

        // 檢查方法是否被調用
        const callPattern = `frontendLogger.${methodName}(`;

        if (content.includes(callPattern)) {
            results.method_called = true;
            console.log(`   ✅ ${eventType} 方法被調用`);
        } else {
            console.log(`   ❌ ${eventType} 方法未被調用`);
        }

        // 檢查必需字段
        for (const field of requirements.required_fields) {
            if (content.includes(`${field}:`)) {
                results.required_fields[field] = true;
                console.log(`   ✅ 包含必需字段: ${field}`);
            } else {
                results.required_fields[field] = false;
                console.log(`   ❌ 缺少必需字段: ${field}`);
            }
        }

        // 計算字段合規率
        const totalFields = requirements.required_fields.length;
        const compliantFields = Object.values(results.required_fields).filter(v => v).length;
        results.field_compliance = compliantFields / totalFields;

        console.log(`   📊 字段合規率: ${compliantFields}/${totalFields} (${(results.field_compliance * 100).toFixed(1)}%)`);

        this.validationResults[eventType] = results;
    }

    validateIdTracking(content) {
        console.log('\\n🔗 驗證ID追蹤機制');

        const checks = {
            observation_id_generation: content.includes('generateObservationId()'),
            request_id_generation: content.includes('req_') && content.includes('Date.now()'),
            id_consistency: content.includes('observationId') && content.includes('requestId'),
            id_attachment: content.includes('observationId') && content.includes('requestId')
        };

        for (const [check, passed] of Object.entries(checks)) {
            console.log(`   ${passed ? '✅' : '❌'} ${check.replace(/_/g, ' ')}`);
        }

        this.validationResults.id_tracking = checks;
    }

    validateTimestampFormat(content) {
        console.log('\\n⏰ 驗證時間戳格式');

        const checks = {
            iso_timestamp: content.includes('new Date().toISOString()'),
            unix_timestamp: content.includes('Date.now()'),
            timestamp_in_logs: content.includes('timestamp:')
        };

        for (const [check, passed] of Object.entries(checks)) {
            console.log(`   ${passed ? '✅' : '❌'} ${check.replace(/_/g, ' ')}`);
        }

        this.validationResults.timestamp_format = checks;
    }

    displayResults() {
        console.log('\\n' + '=' * 50);
        console.log('📊 設計規格合規性驗證結果');
        console.log('=' * 50);

        let totalChecks = 0;
        let passedChecks = 0;

        // 事件類型合規性
        for (const [eventType, results] of Object.entries(this.validationResults)) {
            if (eventType.startsWith('EYES_')) {
                const eventPassed = results.method_exists && results.method_called && results.field_compliance >= 0.8;
                console.log(`${eventType}: ${eventPassed ? '✅ 合規' : '❌ 不合規'} (字段: ${(results.field_compliance * 100).toFixed(1)}%)`);
                totalChecks++;
                if (eventPassed) passedChecks++;
            }
        }

        // ID追蹤合規性
        if (this.validationResults.id_tracking) {
            const idTrackingPassed = Object.values(this.validationResults.id_tracking).filter(v => v).length >= 3;
            console.log(`ID追蹤機制: ${idTrackingPassed ? '✅ 合規' : '❌ 不合規'}`);
            totalChecks++;
            if (idTrackingPassed) passedChecks++;
        }

        // 時間戳格式合規性
        if (this.validationResults.timestamp_format) {
            const timestampPassed = Object.values(this.validationResults.timestamp_format).filter(v => v).length >= 2;
            console.log(`時間戳格式: ${timestampPassed ? '✅ 合規' : '❌ 不合規'}`);
            totalChecks++;
            if (timestampPassed) passedChecks++;
        }

        const overallCompliance = (passedChecks / totalChecks * 100).toFixed(1);
        console.log(`\\n總體合規率: ${passedChecks}/${totalChecks} (${overallCompliance}%)`);

        if (passedChecks === totalChecks) {
            console.log('\\n🎉 完全符合設計規格要求！');
        } else {
            console.log('\\n⚠️ 部分功能不符合設計規格，需要修正。');
        }
    }

    calculateOverallCompliance() {
        let totalChecks = 0;
        let passedChecks = 0;

        // 檢查事件類型
        for (const [eventType, results] of Object.entries(this.validationResults)) {
            if (eventType.startsWith('EYES_')) {
                const eventPassed = results.method_exists && results.method_called && results.field_compliance >= 0.8;
                totalChecks++;
                if (eventPassed) passedChecks++;
            }
        }

        // 檢查ID追蹤
        if (this.validationResults.id_tracking) {
            const idTrackingPassed = Object.values(this.validationResults.id_tracking).filter(v => v).length >= 3;
            totalChecks++;
            if (idTrackingPassed) passedChecks++;
        }

        // 檢查時間戳
        if (this.validationResults.timestamp_format) {
            const timestampPassed = Object.values(this.validationResults.timestamp_format).filter(v => v).length >= 2;
            totalChecks++;
            if (timestampPassed) passedChecks++;
        }

        return passedChecks === totalChecks;
    }
}

// 執行驗證
async function main() {
    const validator = new DesignComplianceValidator();
    const success = await validator.validateCompliance();
    process.exit(success ? 0 : 1);
}

if (require.main === module) {
    main();
}