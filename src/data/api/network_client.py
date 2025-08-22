#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络客户端 - 处理API请求
"""

import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal


class NetworkWorker(QThread):
    """网络请求工作线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url, data, request_type='POST'):
        super().__init__()
        self.url = url
        self.data = data
        self.request_type = request_type
    
    def run(self):
        try:
            headers = {'Content-Type': 'application/json'}
            
            if self.request_type == 'POST':
                response = requests.post(
                    self.url, 
                    data=json.dumps(self.data), 
                    headers=headers,
                    timeout=10
                )
            else:
                response = requests.get(
                    self.url, 
                    headers=headers, 
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                self.finished.emit(result)
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get(
                    'error', f'HTTP {response.status_code}'
                )
                self.error.emit(error_msg)
                
        except requests.exceptions.RequestException as e:
            self.error.emit(f'网络请求失败: {str(e)}')
        except json.JSONDecodeError as e:
            self.error.emit(f'响应解析失败: {str(e)}')
        except Exception as e:
            self.error.emit(f'未知错误: {str(e)}')