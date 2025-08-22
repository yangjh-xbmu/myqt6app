#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker测试窗口 - 用于测试Cloudflare Worker API
"""

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, TextEdit, PrimaryPushButton,
    ComboBox, InfoBar, InfoBarPosition, CardWidget
)

import json
import requests


class WorkerRequestThread(QThread):
    """Worker请求线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url, method='GET', data=None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data
    
    def run(self):
        try:
            headers = {'Content-Type': 'application/json'}
            
            if self.method == 'GET':
                response = requests.get(self.url, headers=headers, timeout=10)
            elif self.method == 'POST':
                response = requests.post(
                    self.url, 
                    data=json.dumps(self.data) if self.data else None,
                    headers=headers, 
                    timeout=10
                )
            elif self.method == 'PUT':
                response = requests.put(
                    self.url,
                    data=json.dumps(self.data) if self.data else None,
                    headers=headers,
                    timeout=10
                )
            elif self.method == 'DELETE':
                response = requests.delete(
                    self.url, 
                    headers=headers, 
                    timeout=10
                )
            else:
                self.error.emit(f'不支持的HTTP方法: {self.method}')
                return
            
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text
            }
            
            # 尝试解析JSON响应
            try:
                result['json'] = response.json()
            except json.JSONDecodeError:
                result['json'] = None
            
            self.finished.emit(result)
            
        except requests.exceptions.RequestException as e:
            self.error.emit(f'请求失败: {str(e)}')
        except Exception as e:
            self.error.emit(f'未知错误: {str(e)}')


class WorkerTestWindow(QWidget):
    """Worker测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('Cloudflare Worker API 测试工具')
        self.setFixedSize(800, 700)
        
        # 设置窗口居中
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = TitleLabel('Cloudflare Worker API 测试工具')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 请求配置卡片
        request_card = CardWidget()
        request_layout = QVBoxLayout()
        request_layout.setSpacing(15)
        
        # URL输入
        self.url_input = LineEdit()
        self.url_input.setPlaceholderText(
            '请输入API URL '
            '(例如: https://your-worker.your-subdomain.workers.dev/api/test)'
        )
        self.url_input.setText('https://pw.yangxz.top/api/test')
        self.url_input.setClearButtonEnabled(True)
        request_layout.addWidget(self.url_input)
        
        # HTTP方法选择
        method_layout = QHBoxLayout()
        method_layout.addWidget(TitleLabel('HTTP方法:'))
        
        self.method_combo = ComboBox()
        self.method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE'])
        self.method_combo.setCurrentText('GET')
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        
        request_layout.addLayout(method_layout)
        
        # 请求数据输入
        request_layout.addWidget(TitleLabel('请求数据 (JSON格式):'))
        self.request_data_input = TextEdit()
        self.request_data_input.setPlaceholderText(
            '请输入JSON格式的请求数据\n例如: {"key": "value"}'
        )
        self.request_data_input.setFixedHeight(120)
        request_layout.addWidget(self.request_data_input)
        
        # 发送请求按钮
        self.send_button = PrimaryPushButton('发送请求')
        self.send_button.clicked.connect(self.send_request)
        request_layout.addWidget(self.send_button)
        
        request_card.setLayout(request_layout)
        layout.addWidget(request_card)
        
        # 响应显示卡片
        response_card = CardWidget()
        response_layout = QVBoxLayout()
        response_layout.setSpacing(15)
        
        response_layout.addWidget(TitleLabel('响应结果:'))
        
        self.response_display = TextEdit()
        self.response_display.setPlaceholderText('响应结果将在这里显示...')
        self.response_display.setReadOnly(True)
        response_layout.addWidget(self.response_display)
        
        response_card.setLayout(response_layout)
        layout.addWidget(response_card)
        
        self.setLayout(layout)
        
        # 设置回车键触发发送请求
        self.url_input.returnPressed.connect(self.send_request)
    
    def send_request(self):
        """发送请求"""
        url = self.url_input.text().strip()
        method = self.method_combo.currentText()
        
        # 验证URL
        if not url:
            self.show_error('请输入API URL')
            return
        
        if not url.startswith(('http://', 'https://')):
            self.show_error('请输入有效的URL（以http://或https://开头）')
            return
        
        # 解析请求数据
        request_data = None
        if method in ['POST', 'PUT']:
            data_text = self.request_data_input.toPlainText().strip()
            if data_text:
                try:
                    request_data = json.loads(data_text)
                except json.JSONDecodeError as e:
                    self.show_error(f'请求数据JSON格式错误: {str(e)}')
                    return
        
        # 禁用发送按钮，防止重复请求
        self.send_button.setEnabled(False)
        self.send_button.setText('发送中...')
        
        # 清空响应显示
        self.response_display.clear()
        
        # 创建请求线程
        self.worker = WorkerRequestThread(url, method, request_data)
        
        # 连接信号
        self.worker.finished.connect(self.on_request_finished)
        self.worker.error.connect(self.on_request_error)
        
        # 启动线程
        self.worker.start()
    
    def on_request_finished(self, result):
        """请求完成处理"""
        self.send_button.setEnabled(True)
        self.send_button.setText('发送请求')
        
        # 格式化响应结果
        response_text = f"状态码: {result['status_code']}\n\n"
        
        # 显示响应头
        response_text += "响应头:\n"
        for key, value in result['headers'].items():
            response_text += f"  {key}: {value}\n"
        response_text += "\n"
        
        # 显示响应内容
        response_text += "响应内容:\n"
        if result['json']:
            # 格式化JSON响应
            response_text += json.dumps(
                result['json'], 
                indent=2, 
                ensure_ascii=False
            )
        else:
            response_text += result['content']
        
        self.response_display.setPlainText(response_text)
        
        # 显示成功信息
        InfoBar.success(
            title='请求成功',
            content=f'状态码: {result["status_code"]}',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def on_request_error(self, error_msg):
        """请求错误处理"""
        self.send_button.setEnabled(True)
        self.send_button.setText('发送请求')
        
        self.response_display.setPlainText(f'请求失败: {error_msg}')
        
        self.show_error(f'请求失败: {error_msg}')
    
    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error(
            title='错误',
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )