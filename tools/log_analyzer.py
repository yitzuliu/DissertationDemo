#!/usr/bin/env python3
"""
AI Manual Assistant 日誌分析工具

提供日誌查詢、分析和診斷功能，實現基於時間戳的事件關聯分析
和資料流完整性檢查。
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import glob

# 添加專案根目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.app_logging.log_manager import get_log_manager
from src.app_logging.flow_tracker import get_flow_tracker, FlowType, FlowStatus

class LogAnalyzer:
    """
    日誌分析器
    
    提供日誌查詢、分析和診斷功能。
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化日誌分析器
        
        Args:
            log_dir: 日誌目錄路徑
        """
        self.log_dir = log_dir
        self.log_manager = get_log_manager()
        self.flow_tracker = get_flow_tracker()
        
        # 日誌檔案模式
        self.log_patterns = {
            'system': 'system_*.log',
            'visual': 'visual_*.log',
            'user': 'user_*.log',
            'flow_tracking': 'flow_tracking_*.log'
        }
    
    def get_log_files(self, log_type: str = None, date: str = None) -> List[str]:
        """
        獲取日誌檔案列表
        
        Args:
            log_type: 日誌類型 (system, visual, user, flow_tracking)
            date: 日期格式 YYYYMMDD
            
        Returns:
            List: 日誌檔案路徑列表
        """
        files = []
        
        if log_type and log_type in self.log_patterns:
            pattern = self.log_patterns[log_type]
            if date:
                pattern = pattern.replace('*', date)
            files.extend(glob.glob(os.path.join(self.log_dir, pattern)))
        else:
            # 獲取所有日誌檔案
            for pattern in self.log_patterns.values():
                files.extend(glob.glob(os.path.join(self.log_dir, pattern)))
        
        return sorted(files)
    
    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        解析日誌行
        
        Args:
            line: 日誌行內容
            
        Returns:
            Dict: 解析後的日誌資料或None
        """
        try:
            # 標準格式: YYYY-MM-DD HH:MM:SS,mmm [INFO] [EVENT_TYPE] key1=value1 key2=value2
            pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d{3}) \[(\w+)\] \[(\w+)\] (.+)'
            match = re.match(pattern, line.strip())
            
            if not match:
                return None
            
            timestamp_str, millis, level, event_type, data_str = match.groups()
            timestamp = datetime.strptime(f"{timestamp_str},{millis}", "%Y-%m-%d %H:%M:%S,%f")
            
            # 解析資料欄位
            data = {}
            for item in data_str.split():
                if '=' in item:
                    key, value = item.split('=', 1)
                    # 移除引號
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    data[key] = value
            
            return {
                'timestamp': timestamp,
                'level': level,
                'event_type': event_type,
                'data': data,
                'raw_line': line.strip()
            }
        except Exception as e:
            print(f"Error parsing log line: {e}")
            return None
    
    def load_logs(self, log_type: str = None, start_time: datetime = None, 
                 end_time: datetime = None) -> List[Dict[str, Any]]:
        """
        載入日誌資料
        
        Args:
            log_type: 日誌類型
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            List: 日誌記錄列表
        """
        logs = []
        files = self.get_log_files(log_type)
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        log_entry = self.parse_log_line(line)
                        if log_entry:
                            # 時間過濾
                            if start_time and log_entry['timestamp'] < start_time:
                                continue
                            if end_time and log_entry['timestamp'] > end_time:
                                continue
                            logs.append(log_entry)
            except Exception as e:
                print(f"Error reading log file {file_path}: {e}")
        
        return sorted(logs, key=lambda x: x['timestamp'])
    
    def analyze_event_flow(self, observation_id: str = None, query_id: str = None, 
                          flow_id: str = None) -> Dict[str, Any]:
        """
        分析事件流程
        
        Args:
            observation_id: 觀察ID
            query_id: 查詢ID
            flow_id: 流程ID
            
        Returns:
            Dict: 事件流程分析結果
        """
        # 載入所有相關日誌
        logs = self.load_logs()
        
        # 根據ID過濾
        filtered_logs = []
        for log in logs:
            data = log['data']
            if observation_id and data.get('observation_id') == observation_id:
                filtered_logs.append(log)
            elif query_id and data.get('query_id') == query_id:
                filtered_logs.append(log)
            elif flow_id and data.get('flow_id') == flow_id:
                filtered_logs.append(log)
        
        # 按時間排序
        filtered_logs.sort(key=lambda x: x['timestamp'])
        
        # 分析事件流程
        flow_analysis = {
            'total_events': len(filtered_logs),
            'time_span': None,
            'events': [],
            'event_types': Counter(),
            'related_ids': set(),
            'performance_metrics': {}
        }
        
        if filtered_logs:
            start_time = filtered_logs[0]['timestamp']
            end_time = filtered_logs[-1]['timestamp']
            flow_analysis['time_span'] = (end_time - start_time).total_seconds()
            
            for log in filtered_logs:
                flow_analysis['events'].append({
                    'timestamp': log['timestamp'].isoformat(),
                    'event_type': log['event_type'],
                    'data': log['data']
                })
                flow_analysis['event_types'][log['event_type']] += 1
                
                # 收集相關ID
                for key, value in log['data'].items():
                    if key.endswith('_id'):
                        flow_analysis['related_ids'].add(f"{key}={value}")
        
        return flow_analysis
    
    def check_data_integrity(self, start_time: datetime = None, 
                           end_time: datetime = None) -> Dict[str, Any]:
        """
        檢查資料流完整性
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 完整性檢查結果
        """
        logs = self.load_logs(start_time=start_time, end_time=end_time)
        
        # 按ID分組
        observation_flows = defaultdict(list)
        query_flows = defaultdict(list)
        
        for log in logs:
            data = log['data']
            if 'observation_id' in data:
                observation_flows[data['observation_id']].append(log)
            if 'query_id' in data:
                query_flows[data['query_id']].append(log)
        
        # 檢查完整性
        integrity_report = {
            'total_observations': len(observation_flows),
            'total_queries': len(query_flows),
            'incomplete_observations': [],
            'incomplete_queries': [],
            'orphaned_events': [],
            'performance_issues': []
        }
        
        # 檢查觀察流程完整性
        expected_observation_events = {'EYES_CAPTURE', 'EYES_PROMPT', 'EYES_TRANSFER', 
                                     'RAG_MATCHING', 'RAG_RESULT', 'STATE_TRACKER'}
        
        for obs_id, events in observation_flows.items():
            event_types = {e['event_type'] for e in events}
            missing_events = expected_observation_events - event_types
            
            if missing_events:
                integrity_report['incomplete_observations'].append({
                    'observation_id': obs_id,
                    'missing_events': list(missing_events),
                    'present_events': list(event_types)
                })
        
        # 檢查查詢流程完整性
        expected_query_events = {'USER_QUERY', 'QUERY_CLASSIFY', 'QUERY_PROCESS', 'QUERY_RESPONSE'}
        
        for query_id, events in query_flows.items():
            event_types = {e['event_type'] for e in events}
            missing_events = expected_query_events - event_types
            
            if missing_events:
                integrity_report['incomplete_queries'].append({
                    'query_id': query_id,
                    'missing_events': list(missing_events),
                    'present_events': list(event_types)
                })
        
        return integrity_report
    
    def analyze_performance(self, start_time: datetime = None, 
                          end_time: datetime = None) -> Dict[str, Any]:
        """
        分析系統性能
        
        Args:
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 性能分析結果
        """
        logs = self.load_logs(start_time=start_time, end_time=end_time)
        
        performance_data = {
            'query_response_times': [],
            'vlm_processing_times': [],
            'rag_matching_times': [],
            'state_update_times': [],
            'error_counts': defaultdict(int),
            'throughput_metrics': {}
        }
        
        for log in logs:
            data = log['data']
            
            # 收集處理時間
            if log['event_type'] == 'QUERY_RESPONSE' and 'duration' in data:
                try:
                    duration = float(data['duration'].replace('ms', ''))
                    performance_data['query_response_times'].append(duration)
                except:
                    pass
            
            # 收集錯誤
            if log['level'] == 'ERROR':
                performance_data['error_counts'][log['event_type']] += 1
        
        # 計算統計資料
        if performance_data['query_response_times']:
            times = performance_data['query_response_times']
            performance_data['query_performance'] = {
                'count': len(times),
                'average': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'p95': sorted(times)[int(len(times) * 0.95)]
            }
        
        return performance_data
    
    def generate_report(self, report_type: str = 'comprehensive', 
                       start_time: datetime = None, end_time: datetime = None) -> Dict[str, Any]:
        """
        生成分析報告
        
        Args:
            report_type: 報告類型 (comprehensive, performance, integrity)
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            Dict: 分析報告
        """
        report = {
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'time_range': {
                'start': start_time.isoformat() if start_time else None,
                'end': end_time.isoformat() if end_time else None
            }
        }
        
        if report_type in ['comprehensive', 'integrity']:
            report['integrity_check'] = self.check_data_integrity(start_time, end_time)
        
        if report_type in ['comprehensive', 'performance']:
            report['performance_analysis'] = self.analyze_performance(start_time, end_time)
        
        if report_type == 'comprehensive':
            # 載入基本統計
            logs = self.load_logs(start_time=start_time, end_time=end_time)
            report['basic_stats'] = {
                'total_log_entries': len(logs),
                'event_type_distribution': Counter(log['event_type'] for log in logs),
                'log_level_distribution': Counter(log['level'] for log in logs)
            }
        
        return report
    
    def export_report(self, report: Dict[str, Any], output_file: str):
        """
        導出報告到檔案
        
        Args:
            report: 分析報告
            output_file: 輸出檔案路徑
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Report exported to: {output_file}")
        except Exception as e:
            print(f"Error exporting report: {e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='AI Manual Assistant Log Analyzer')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--start-time', help='Start time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-time', help='End time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--report-type', choices=['comprehensive', 'performance', 'integrity'], 
                       default='comprehensive', help='Report type')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--observation-id', help='Analyze specific observation ID')
    parser.add_argument('--query-id', help='Analyze specific query ID')
    parser.add_argument('--flow-id', help='Analyze specific flow ID')
    
    args = parser.parse_args()
    
    # 解析時間
    start_time = None
    end_time = None
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
    
    # 創建分析器
    analyzer = LogAnalyzer(args.log_dir)
    
    # 執行分析
    if args.observation_id or args.query_id or args.flow_id:
        # 特定ID分析
        flow_analysis = analyzer.analyze_event_flow(
            observation_id=args.observation_id,
            query_id=args.query_id,
            flow_id=args.flow_id
        )
        report = {'event_flow_analysis': flow_analysis}
    else:
        # 一般報告
        report = analyzer.generate_report(args.report_type, start_time, end_time)
    
    # 輸出結果
    if args.output:
        analyzer.export_report(report, args.output)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main() 