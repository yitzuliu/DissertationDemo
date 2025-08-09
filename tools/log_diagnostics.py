#!/usr/bin/env python3
"""
AI Manual Assistant 日誌診斷工具

提供系統診斷功能，包括VLM處理失敗檢測、查詢分類準確度分析、
系統性能監控和異常模式檢測。
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

# 添加專案根目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.log_analyzer import LogAnalyzer

class LogDiagnostics:
    """
    日誌診斷器
    
    提供系統診斷和異常檢測功能。
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化日誌診斷器
        
        Args:
            log_dir: 日誌目錄路徑
        """
        self.log_analyzer = LogAnalyzer(log_dir)
        
        # 診斷閾值
        self.thresholds = {
            'vlm_failure_rate': 0.1,  # 10% VLM失敗率
            'query_response_time_p95': 50.0,  # 95%查詢回應時間閾值(ms)
            'error_rate': 0.05,  # 5%錯誤率
            'incomplete_flow_rate': 0.2,  # 20%不完整流程率
            'consecutive_failures': 3,  # 連續失敗次數
            'memory_usage_threshold': 0.8,  # 80%記憶體使用率
        }
    
    def detect_vlm_failures(self, start_time: datetime = None, 
                          end_time: datetime = None) -> Dict[str, Any]:
        """
        檢測VLM處理失敗
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: VLM失敗檢測結果
        """
        logs = self.log_analyzer.load_logs(start_time=start_time, end_time=end_time)
        
        vlm_analysis = {
            'total_observations': 0,
            'successful_observations': 0,
            'failed_observations': 0,
            'failure_rate': 0.0,
            'failure_patterns': [],
            'consecutive_failures': [],
            'error_details': defaultdict(list)
        }
        
        # 追蹤觀察流程
        observation_flows = defaultdict(list)
        for log in logs:
            if 'observation_id' in log['data']:
                obs_id = log['data']['observation_id']
                observation_flows[obs_id].append(log)
        
        vlm_analysis['total_observations'] = len(observation_flows)
        
        # 分析每個觀察流程
        for obs_id, events in observation_flows.items():
            event_types = {e['event_type'] for e in events}
            
            # 檢查是否包含所有必要事件
            required_events = {'EYES_CAPTURE', 'EYES_TRANSFER', 'RAG_MATCHING', 'RAG_RESULT'}
            if required_events.issubset(event_types):
                vlm_analysis['successful_observations'] += 1
            else:
                vlm_analysis['failed_observations'] += 1
                
                # 記錄失敗模式
                missing_events = required_events - event_types
                vlm_analysis['failure_patterns'].append({
                    'observation_id': obs_id,
                    'missing_events': list(missing_events),
                    'timestamp': events[0]['timestamp'].isoformat() if events else None
                })
        
        # 計算失敗率
        if vlm_analysis['total_observations'] > 0:
            vlm_analysis['failure_rate'] = vlm_analysis['failed_observations'] / vlm_analysis['total_observations']
        
        # 檢測連續失敗
        vlm_analysis['consecutive_failures'] = self._detect_consecutive_failures(
            vlm_analysis['failure_patterns']
        )
        
        # 檢查是否超過閾值
        vlm_analysis['status'] = 'NORMAL'
        if vlm_analysis['failure_rate'] > self.thresholds['vlm_failure_rate']:
            vlm_analysis['status'] = 'WARNING'
        if vlm_analysis['consecutive_failures']:
            vlm_analysis['status'] = 'CRITICAL'
        
        return vlm_analysis
    
    def analyze_query_classification_accuracy(self, start_time: datetime = None,
                                           end_time: datetime = None) -> Dict[str, Any]:
        """
        分析查詢分類準確度
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 查詢分類準確度分析結果
        """
        logs = self.log_analyzer.load_logs(start_time=start_time, end_time=end_time)
        
        classification_analysis = {
            'total_queries': 0,
            'classification_distribution': Counter(),
            'confidence_distribution': [],
            'low_confidence_queries': [],
            'classification_accuracy': 0.0,
            'average_confidence': 0.0
        }
        
        # 收集查詢分類資料
        query_data = defaultdict(dict)
        for log in logs:
            if log['event_type'] == 'QUERY_CLASSIFY':
                query_id = log['data'].get('query_id')
                if query_id:
                    query_data[query_id].update({
                        'query_type': log['data'].get('type'),
                        'confidence': float(log['data'].get('confidence', 0)),
                        'timestamp': log['timestamp']
                    })
            elif log['event_type'] == 'USER_QUERY':
                query_id = log['data'].get('query_id')
                if query_id:
                    query_data[query_id]['question'] = log['data'].get('question', '')
        
        classification_analysis['total_queries'] = len(query_data)
        
        # 分析分類結果
        confidences = []
        for query_id, data in query_data.items():
            query_type = data.get('query_type')
            confidence = data.get('confidence', 0)
            
            if query_type:
                classification_analysis['classification_distribution'][query_type] += 1
            
            confidences.append(confidence)
            
            # 記錄低信心度查詢
            if confidence < 0.7:
                classification_analysis['low_confidence_queries'].append({
                    'query_id': query_id,
                    'question': data.get('question', ''),
                    'query_type': query_type,
                    'confidence': confidence,
                    'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None
                })
        
        # 計算統計資料
        if confidences:
            classification_analysis['average_confidence'] = statistics.mean(confidences)
            classification_analysis['confidence_distribution'] = {
                'min': min(confidences),
                'max': max(confidences),
                'mean': statistics.mean(confidences),
                'median': statistics.median(confidences),
                'std': statistics.stdev(confidences) if len(confidences) > 1 else 0
            }
        
        # 評估準確度（基於信心度）
        high_confidence_count = sum(1 for c in confidences if c >= 0.8)
        if confidences:
            classification_analysis['classification_accuracy'] = high_confidence_count / len(confidences)
        
        # 狀態評估
        classification_analysis['status'] = 'NORMAL'
        if classification_analysis['classification_accuracy'] < 0.8:
            classification_analysis['status'] = 'WARNING'
        if len(classification_analysis['low_confidence_queries']) > 10:
            classification_analysis['status'] = 'ATTENTION'
        
        return classification_analysis
    
    def monitor_system_performance(self, start_time: datetime = None,
                                 end_time: datetime = None) -> Dict[str, Any]:
        """
        監控系統性能
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 系統性能監控結果
        """
        logs = self.log_analyzer.load_logs(start_time=start_time, end_time=end_time)
        
        performance_monitor = {
            'query_response_times': [],
            'vlm_processing_times': [],
            'error_counts': Counter(),
            'throughput_metrics': {},
            'performance_issues': [],
            'status': 'NORMAL'
        }
        
        # 收集性能資料
        for log in logs:
            data = log['data']
            
            # 查詢回應時間
            if log['event_type'] == 'QUERY_RESPONSE' and 'duration' in data:
                try:
                    duration = float(data['duration'].replace('ms', ''))
                    performance_monitor['query_response_times'].append(duration)
                except:
                    pass
            
            # 錯誤統計
            if log['level'] == 'ERROR':
                performance_monitor['error_counts'][log['event_type']] += 1
        
        # 計算性能指標
        if performance_monitor['query_response_times']:
            times = performance_monitor['query_response_times']
            performance_monitor['query_performance'] = {
                'count': len(times),
                'average': statistics.mean(times),
                'median': statistics.median(times),
                'p95': sorted(times)[int(len(times) * 0.95)] if times else 0,
                'p99': sorted(times)[int(len(times) * 0.99)] if times else 0,
                'min': min(times),
                'max': max(times)
            }
            
            # 檢查性能問題
            p95_time = performance_monitor['query_performance']['p95']
            if p95_time > self.thresholds['query_response_time_p95']:
                performance_monitor['performance_issues'].append({
                    'type': 'HIGH_RESPONSE_TIME',
                    'value': p95_time,
                    'threshold': self.thresholds['query_response_time_p95'],
                    'description': f'95th percentile response time ({p95_time:.1f}ms) exceeds threshold'
                })
        
        # 錯誤率分析
        total_events = len(logs)
        error_events = sum(performance_monitor['error_counts'].values())
        error_rate = error_events / total_events if total_events > 0 else 0
        
        performance_monitor['error_rate'] = error_rate
        if error_rate > self.thresholds['error_rate']:
            performance_monitor['performance_issues'].append({
                'type': 'HIGH_ERROR_RATE',
                'value': error_rate,
                'threshold': self.thresholds['error_rate'],
                'description': f'Error rate ({error_rate:.2%}) exceeds threshold'
            })
        
        # 吞吐量計算
        if start_time and end_time:
            time_span = (end_time - start_time).total_seconds()
            if time_span > 0:
                performance_monitor['throughput_metrics'] = {
                    'events_per_second': total_events / time_span,
                    'queries_per_second': len(performance_monitor['query_response_times']) / time_span,
                    'errors_per_second': error_events / time_span
                }
        
        # 狀態評估
        if performance_monitor['performance_issues']:
            performance_monitor['status'] = 'WARNING'
        if error_rate > 0.1:  # 10%錯誤率
            performance_monitor['status'] = 'CRITICAL'
        
        return performance_monitor
    
    def detect_anomaly_patterns(self, start_time: datetime = None,
                              end_time: datetime = None) -> Dict[str, Any]:
        """
        檢測異常模式
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 異常模式檢測結果
        """
        logs = self.log_analyzer.load_logs(start_time=start_time, end_time=end_time)
        
        anomaly_detection = {
            'anomalies_detected': [],
            'pattern_analysis': {},
            'temporal_anomalies': [],
            'frequency_anomalies': [],
            'status': 'NORMAL'
        }
        
        # 按時間分組分析
        hourly_events = defaultdict(int)
        event_type_frequency = Counter()
        
        for log in logs:
            hour = log['timestamp'].replace(minute=0, second=0, microsecond=0)
            hourly_events[hour] += 1
            event_type_frequency[log['event_type']] += 1
        
        # 檢測時間異常（異常高或低的活動）
        if hourly_events:
            event_counts = list(hourly_events.values())
            mean_events = statistics.mean(event_counts)
            std_events = statistics.stdev(event_counts) if len(event_counts) > 1 else 0
            
            for hour, count in hourly_events.items():
                if std_events > 0:
                    z_score = abs(count - mean_events) / std_events
                    if z_score > 2.0:  # 2個標準差
                        anomaly_detection['temporal_anomalies'].append({
                            'timestamp': hour.isoformat(),
                            'event_count': count,
                            'expected_range': f'{mean_events - 2*std_events:.1f} - {mean_events + 2*std_events:.1f}',
                            'z_score': z_score,
                            'type': 'HIGH_ACTIVITY' if count > mean_events else 'LOW_ACTIVITY'
                        })
        
        # 檢測頻率異常
        total_events = len(logs)
        for event_type, count in event_type_frequency.items():
            frequency = count / total_events if total_events > 0 else 0
            
            # 檢查異常頻率（這裡需要根據實際情況調整閾值）
            if frequency > 0.5:  # 某個事件類型佔比超過50%
                anomaly_detection['frequency_anomalies'].append({
                    'event_type': event_type,
                    'frequency': frequency,
                    'count': count,
                    'description': f'Event type {event_type} has unusually high frequency ({frequency:.2%})'
                })
        
        # 檢測連續錯誤模式
        consecutive_errors = self._detect_consecutive_errors(logs)
        if consecutive_errors:
            anomaly_detection['anomalies_detected'].extend(consecutive_errors)
        
        # 檢測系統狀態變化
        system_status_changes = self._detect_system_status_changes(logs)
        if system_status_changes:
            anomaly_detection['anomalies_detected'].extend(system_status_changes)
        
        # 狀態評估
        total_anomalies = (len(anomaly_detection['temporal_anomalies']) + 
                          len(anomaly_detection['frequency_anomalies']) + 
                          len(anomaly_detection['anomalies_detected']))
        
        if total_anomalies > 0:
            anomaly_detection['status'] = 'WARNING'
        if total_anomalies > 5:
            anomaly_detection['status'] = 'CRITICAL'
        
        return anomaly_detection
    
    def _detect_consecutive_failures(self, failure_patterns: List[Dict]) -> List[Dict]:
        """檢測連續失敗模式"""
        consecutive_failures = []
        
        if len(failure_patterns) < 2:
            return consecutive_failures
        
        # 按時間排序
        sorted_failures = sorted(failure_patterns, key=lambda x: x.get('timestamp', ''))
        
        current_consecutive = 1
        for i in range(1, len(sorted_failures)):
            prev_time = datetime.fromisoformat(sorted_failures[i-1]['timestamp'])
            curr_time = datetime.fromisoformat(sorted_failures[i]['timestamp'])
            
            # 檢查是否在短時間內（5分鐘內）
            if (curr_time - prev_time).total_seconds() < 300:
                current_consecutive += 1
            else:
                if current_consecutive >= self.thresholds['consecutive_failures']:
                    consecutive_failures.append({
                        'count': current_consecutive,
                        'start_time': sorted_failures[i-current_consecutive]['timestamp'],
                        'end_time': sorted_failures[i-1]['timestamp']
                    })
                current_consecutive = 1
        
        # 檢查最後一組
        if current_consecutive >= self.thresholds['consecutive_failures']:
            consecutive_failures.append({
                'count': current_consecutive,
                'start_time': sorted_failures[-current_consecutive]['timestamp'],
                'end_time': sorted_failures[-1]['timestamp']
            })
        
        return consecutive_failures
    
    def _detect_consecutive_errors(self, logs: List[Dict]) -> List[Dict]:
        """檢測連續錯誤"""
        consecutive_errors = []
        error_logs = [log for log in logs if log['level'] == 'ERROR']
        
        if len(error_logs) < self.thresholds['consecutive_failures']:
            return consecutive_errors
        
        current_consecutive = 1
        for i in range(1, len(error_logs)):
            prev_time = error_logs[i-1]['timestamp']
            curr_time = error_logs[i]['timestamp']
            
            # 檢查是否在短時間內（1分鐘內）
            if (curr_time - prev_time).total_seconds() < 60:
                current_consecutive += 1
            else:
                if current_consecutive >= self.thresholds['consecutive_failures']:
                    consecutive_errors.append({
                        'type': 'CONSECUTIVE_ERRORS',
                        'count': current_consecutive,
                        'start_time': error_logs[i-current_consecutive]['timestamp'].isoformat(),
                        'end_time': error_logs[i-1]['timestamp'].isoformat(),
                        'description': f'{current_consecutive} consecutive errors detected'
                    })
                current_consecutive = 1
        
        # 檢查最後一組
        if current_consecutive >= self.thresholds['consecutive_failures']:
            consecutive_errors.append({
                'type': 'CONSECUTIVE_ERRORS',
                'count': current_consecutive,
                'start_time': error_logs[-current_consecutive]['timestamp'].isoformat(),
                'end_time': error_logs[-1]['timestamp'].isoformat(),
                'description': f'{current_consecutive} consecutive errors detected'
            })
        
        return consecutive_errors
    
    def _detect_system_status_changes(self, logs: List[Dict]) -> List[Dict]:
        """檢測系統狀態變化"""
        status_changes = []
        system_events = [log for log in logs if log['event_type'] in ['SYSTEM_START', 'SYSTEM_SHUTDOWN']]
        
        if len(system_events) < 2:
            return status_changes
        
        # 檢查頻繁的系統重啟
        restart_count = 0
        for i in range(1, len(system_events)):
            prev_time = system_events[i-1]['timestamp']
            curr_time = system_events[i]['timestamp']
            
            # 檢查是否在短時間內重啟（5分鐘內）
            if (curr_time - prev_time).total_seconds() < 300:
                restart_count += 1
        
        if restart_count > 0:
            status_changes.append({
                'type': 'FREQUENT_RESTARTS',
                'count': restart_count,
                'description': f'System restarted {restart_count} times in short intervals'
            })
        
        return status_changes
    
    def run_comprehensive_diagnostics(self, start_time: datetime = None,
                                    end_time: datetime = None) -> Dict[str, Any]:
        """
        執行綜合診斷
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 綜合診斷結果
        """
        diagnostics_report = {
            'diagnostics_timestamp': datetime.now().isoformat(),
            'time_range': {
                'start': start_time.isoformat() if start_time else None,
                'end': end_time.isoformat() if end_time else None
            },
            'overall_status': 'NORMAL',
            'recommendations': []
        }
        
        # 執行各項診斷
        diagnostics_report['vlm_failure_analysis'] = self.detect_vlm_failures(start_time, end_time)
        diagnostics_report['query_classification_analysis'] = self.analyze_query_classification_accuracy(start_time, end_time)
        diagnostics_report['performance_monitoring'] = self.monitor_system_performance(start_time, end_time)
        diagnostics_report['anomaly_detection'] = self.detect_anomaly_patterns(start_time, end_time)
        
        # 綜合狀態評估
        statuses = [
            diagnostics_report['vlm_failure_analysis']['status'],
            diagnostics_report['query_classification_analysis']['status'],
            diagnostics_report['performance_monitoring']['status'],
            diagnostics_report['anomaly_detection']['status']
        ]
        
        if 'CRITICAL' in statuses:
            diagnostics_report['overall_status'] = 'CRITICAL'
        elif 'WARNING' in statuses or 'ATTENTION' in statuses:
            diagnostics_report['overall_status'] = 'WARNING'
        
        # 生成建議
        diagnostics_report['recommendations'] = self._generate_recommendations(diagnostics_report)
        
        return diagnostics_report
    
    def _generate_recommendations(self, diagnostics_report: Dict[str, Any]) -> List[str]:
        """生成診斷建議"""
        recommendations = []
        
        # VLM失敗建議
        vlm_analysis = diagnostics_report['vlm_failure_analysis']
        if vlm_analysis['status'] == 'CRITICAL':
            recommendations.append("CRITICAL: VLM processing has high failure rate. Check model server and network connectivity.")
        elif vlm_analysis['status'] == 'WARNING':
            recommendations.append("WARNING: VLM failure rate is elevated. Monitor system resources and model performance.")
        
        # 查詢分類建議
        query_analysis = diagnostics_report['query_classification_analysis']
        if query_analysis['status'] == 'WARNING':
            recommendations.append("WARNING: Query classification accuracy is below target. Review training data and classification logic.")
        
        # 性能建議
        perf_monitor = diagnostics_report['performance_monitoring']
        if perf_monitor['status'] == 'CRITICAL':
            recommendations.append("CRITICAL: System performance issues detected. Check server resources and optimize processing pipeline.")
        elif perf_monitor['status'] == 'WARNING':
            recommendations.append("WARNING: Performance metrics indicate potential issues. Monitor system load and response times.")
        
        # 異常建議
        anomaly_detection = diagnostics_report['anomaly_detection']
        if anomaly_detection['status'] == 'CRITICAL':
            recommendations.append("CRITICAL: Multiple anomalies detected. Investigate system behavior and check for external issues.")
        
        if not recommendations:
            recommendations.append("System is operating normally. Continue monitoring for any changes.")
        
        return recommendations

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='AI Manual Assistant Log Diagnostics')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--start-time', help='Start time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-time', help='End time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--diagnostic-type', choices=['vlm', 'query', 'performance', 'anomaly', 'comprehensive'],
                       default='comprehensive', help='Diagnostic type')
    parser.add_argument('--output', help='Output file for diagnostics report')
    
    args = parser.parse_args()
    
    # 解析時間
    start_time = None
    end_time = None
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
    
    # 創建診斷器
    diagnostics = LogDiagnostics(args.log_dir)
    
    # 執行診斷
    if args.diagnostic_type == 'vlm':
        report = diagnostics.detect_vlm_failures(start_time, end_time)
    elif args.diagnostic_type == 'query':
        report = diagnostics.analyze_query_classification_accuracy(start_time, end_time)
    elif args.diagnostic_type == 'performance':
        report = diagnostics.monitor_system_performance(start_time, end_time)
    elif args.diagnostic_type == 'anomaly':
        report = diagnostics.detect_anomaly_patterns(start_time, end_time)
    else:  # comprehensive
        report = diagnostics.run_comprehensive_diagnostics(start_time, end_time)
    
    # 輸出結果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Diagnostics report exported to: {args.output}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main() 