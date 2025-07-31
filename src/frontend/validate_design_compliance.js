#!/usr/bin/env node
/**
 * Design Specification Compliance Validation Script
 * 
 * Check if frontend logging implementation fully complies with design document 3.2 Visual Observation Logging requirements
 */

const fs = require('fs');
const path = require('path');

class DesignComplianceValidator {
    constructor() {
        this.indexHtmlPath = path.join(__dirname, 'index.html');
        this.designRequirements = {
            EYES_CAPTURE: {
                required_fields: ['observation_id', 'request_id', 'device', 'resolution', 'quality', 'format', 'size'],
                description: 'Image capture event'
            },
            EYES_PROMPT: {
                required_fields: ['observation_id', 'prompt', 'length'],
                description: 'Visual prompt event'
            },
            EYES_TRANSFER: {
                required_fields: ['observation_id', 'sent_to_backend'],
                description: 'Backend transfer event'
            }
        };
        this.validationResults = {};
    }

    async validateCompliance() {
        console.log('🔍 Validating design specification compliance');
        console.log('=' * 50);

        try {
            const htmlContent = fs.readFileSync(this.indexHtmlPath, 'utf8');

            // Check each log event type
            for (const [eventType, requirements] of Object.entries(this.designRequirements)) {
                this.validateEventType(htmlContent, eventType, requirements);
            }

            // Check ID tracking mechanism
            this.validateIdTracking(htmlContent);

            // Check timestamp format
            this.validateTimestampFormat(htmlContent);

            // Display results
            this.displayResults();

            return this.calculateOverallCompliance();

        } catch (error) {
            console.error('❌ Error occurred during validation:', error.message);
            return false;
        }
    }

    validateEventType(content, eventType, requirements) {
        console.log(`\n📋 Validating ${eventType} (${requirements.description})`);

        const results = {
            method_exists: false,
            method_called: false,
            required_fields: {},
            field_compliance: 0
        };

        // Check if method exists
        const methodName = `log${eventType.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join('')}`;

        if (content.includes(`${methodName}(`)) {
            results.method_exists = true;
            console.log(`   ✅ ${eventType} method exists`);
        } else {
            console.log(`   ❌ ${eventType} method does not exist`);
        }

        // Check if method is called
        const callPattern = `frontendLogger.${methodName}(`;

        if (content.includes(callPattern)) {
            results.method_called = true;
            console.log(`   ✅ ${eventType} method is called`);
        } else {
            console.log(`   ❌ ${eventType} method is not called`);
        }

        // Check required fields
        for (const field of requirements.required_fields) {
            if (content.includes(`${field}:`)) {
                results.required_fields[field] = true;
                console.log(`   ✅ Contains required field: ${field}`);
            } else {
                results.required_fields[field] = false;
                console.log(`   ❌ Missing required field: ${field}`);
            }
        }

        // Calculate field compliance rate
        const totalFields = requirements.required_fields.length;
        const compliantFields = Object.values(results.required_fields).filter(v => v).length;
        results.field_compliance = compliantFields / totalFields;

        console.log(`   📊 Field compliance rate: ${compliantFields}/${totalFields} (${(results.field_compliance * 100).toFixed(1)}%)`);

        this.validationResults[eventType] = results;
    }

    validateIdTracking(content) {
        console.log('\n🔗 Validating ID tracking mechanism');

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
        console.log('\n⏰ Validating timestamp format');

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
        console.log('\n' + '=' * 50);
        console.log('📊 Design Specification Compliance Validation Results');
        console.log('=' * 50);

        let totalChecks = 0;
        let passedChecks = 0;

        // Event type compliance
        for (const [eventType, results] of Object.entries(this.validationResults)) {
            if (eventType.startsWith('EYES_')) {
                const eventPassed = results.method_exists && results.method_called && results.field_compliance >= 0.8;
                console.log(`${eventType}: ${eventPassed ? '✅ Compliant' : '❌ Non-compliant'} (fields: ${(results.field_compliance * 100).toFixed(1)}%)`);
                totalChecks++;
                if (eventPassed) passedChecks++;
            }
        }

        // ID tracking compliance
        if (this.validationResults.id_tracking) {
            const idTrackingPassed = Object.values(this.validationResults.id_tracking).filter(v => v).length >= 3;
            console.log(`ID tracking mechanism: ${idTrackingPassed ? '✅ Compliant' : '❌ Non-compliant'}`);
            totalChecks++;
            if (idTrackingPassed) passedChecks++;
        }

        // Timestamp format compliance
        if (this.validationResults.timestamp_format) {
            const timestampPassed = Object.values(this.validationResults.timestamp_format).filter(v => v).length >= 2;
            console.log(`Timestamp format: ${timestampPassed ? '✅ Compliant' : '❌ Non-compliant'}`);
            totalChecks++;
            if (timestampPassed) passedChecks++;
        }

        const overallCompliance = (passedChecks / totalChecks * 100).toFixed(1);
        console.log(`\nOverall compliance rate: ${passedChecks}/${totalChecks} (${overallCompliance}%)`);

        if (passedChecks === totalChecks) {
            console.log('\n🎉 Fully compliant with design specification requirements!');
        } else {
            console.log('\n⚠️ Some features do not comply with design specifications and need correction.');
        }
    }

    calculateOverallCompliance() {
        let totalChecks = 0;
        let passedChecks = 0;

        // Check event types
        for (const [eventType, results] of Object.entries(this.validationResults)) {
            if (eventType.startsWith('EYES_')) {
                const eventPassed = results.method_exists && results.method_called && results.field_compliance >= 0.8;
                totalChecks++;
                if (eventPassed) passedChecks++;
            }
        }

        // Check ID tracking
        if (this.validationResults.id_tracking) {
            const idTrackingPassed = Object.values(this.validationResults.id_tracking).filter(v => v).length >= 3;
            totalChecks++;
            if (idTrackingPassed) passedChecks++;
        }

        // Check timestamp
        if (this.validationResults.timestamp_format) {
            const timestampPassed = Object.values(this.validationResults.timestamp_format).filter(v => v).length >= 2;
            totalChecks++;
            if (timestampPassed) passedChecks++;
        }

        return passedChecks === totalChecks;
    }
}

// Execute validation
async function main() {
    const validator = new DesignComplianceValidator();
    const success = await validator.validateCompliance();
    process.exit(success ? 0 : 1);
}

if (require.main === module) {
    main();
}