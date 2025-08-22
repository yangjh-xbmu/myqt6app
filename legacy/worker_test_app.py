# worker_test_app.py

import sys
import json
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout
)

# 导入 fluent-widgets 的核心组件
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, PrimaryPushButton, PushButton,
    InfoBar, InfoBarPosition, LineEdit, TextEdit
)


class WorkerRequestThread(QThread):
    """处理网络请求的线程，避免阻塞UI"""
    
    # 定义信号
    request_finished = pyqtSignal(dict)  # 请求成功
    request_error = pyqtSignal(str)      # 请求失败
    
    def __init__(self, url, method='GET', data=None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data
    
    def run(self):
        """在后台线程中执行网络请求"""
        try:
            if self.method == 'GET':
                response = requests.get(self.url, timeout=10)
            elif self.method == 'POST':
                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    self.url, 
                    json=self.data, 
                    headers=headers, 
                    timeout=10
                )
            
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            self.request_finished.emit(result)
            
        except requests.exceptions.RequestException as e:
            self.request_error.emit(f"网络请求错误: {str(e)}")
        except json.JSONDecodeError as e:
            self.request_error.emit(f"JSON解析错误: {str(e)}")
        except Exception as e:
            self.request_error.emit(f"未知错误: {str(e)}")


class WorkerTestWindow(QWidget):
    """Python Worker测试界面"""
    
    def __init__(self):
        super().__init__()
        # 远程Worker地址
        self.worker_url = "https://pw.yangxz.top"
        self.request_thread = None
        self.initUi()
    
    def initUi(self):
        # --- 窗口基本设置 ---
        self.setWindowTitle("Python Worker 测试工具")
        self.setFixedSize(600, 700)
        
        # --- 创建布局 ---
        self.mainLayout = QVBoxLayout(self)
        
        # --- 创建控件 ---
        self.titleLabel = TitleLabel("Python Worker 测试")
        
        # URL输入框
        self.urlLineEdit = LineEdit()
        self.urlLineEdit.setPlaceholderText(
            "Worker URL (默认: https://pw.yangxz.top)"
        )
        self.urlLineEdit.setText(self.worker_url)
        
        # 测试按钮组
        self.testButtonLayout = QHBoxLayout()
        self.testGetButton = PrimaryPushButton("测试 GET /test")
        self.testStatusButton = PushButton("获取状态")
        self.testPostButton = PushButton("测试 POST /data")
        
        # POST数据输入框
        self.postDataEdit = LineEdit()
        placeholder_text = (
            '输入POST数据 (JSON格式，如: '
            '{"client": "Qt6App", "message": "Hello"})'
        )
        self.postDataEdit.setPlaceholderText(placeholder_text)
        self.postDataEdit.setText(
            '{"client": "Qt6App", "message": "Hello from PyQt6!"}'
        )
        
        # 响应显示区域
        self.responseLabel = TitleLabel("响应结果:")
        self.responseTextEdit = TextEdit()
        self.responseTextEdit.setReadOnly(True)
        self.responseTextEdit.setPlainText("点击测试按钮查看Worker响应...")
        
        # 清除按钮
        self.clearButton = PushButton("清除结果")
        
        # --- 布局管理 ---
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(
            self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter
        )
        self.mainLayout.addSpacing(30)
        
        # URL输入
        self.mainLayout.addWidget(self.urlLineEdit)
        self.mainLayout.addSpacing(20)
        
        # 测试按钮
        self.testButtonLayout.addWidget(self.testGetButton)
        self.testButtonLayout.addWidget(self.testStatusButton)
        self.testButtonLayout.addWidget(self.testPostButton)
        self.mainLayout.addLayout(self.testButtonLayout)
        self.mainLayout.addSpacing(15)
        
        # POST数据输入
        self.mainLayout.addWidget(self.postDataEdit)
        self.mainLayout.addSpacing(20)
        
        # 响应显示
        self.mainLayout.addWidget(self.responseLabel)
        self.mainLayout.addWidget(self.responseTextEdit)
        self.mainLayout.addSpacing(15)
        
        # 清除按钮
        self.mainLayout.addWidget(self.clearButton)
        
        # 设置整体布局的边距
        self.mainLayout.setContentsMargins(30, 0, 30, 30)
        
        # --- 信号与槽连接 ---
        self.testGetButton.clicked.connect(self.test_get_endpoint)
        self.testStatusButton.clicked.connect(self.test_status_endpoint)
        self.testPostButton.clicked.connect(self.test_post_endpoint)
        self.clearButton.clicked.connect(self.clear_response)
        self.urlLineEdit.textChanged.connect(self.update_worker_url)
    
    def update_worker_url(self):
        """更新Worker URL"""
        url_text = self.urlLineEdit.text().strip()
        self.worker_url = (
            url_text or "https://pw.yangxz.top"
        )
    
    def test_get_endpoint(self):
        """测试GET /test端点"""
        self.make_request(f"{self.worker_url}/test", "GET")
    
    def test_status_endpoint(self):
        """测试GET /status端点"""
        self.make_request(f"{self.worker_url}/status", "GET")
    
    def test_post_endpoint(self):
        """测试POST /data端点"""
        try:
            post_data_text = self.postDataEdit.text().strip()
            if not post_data_text:
                self.show_error("请输入POST数据")
                return
            
            post_data = json.loads(post_data_text)
            self.make_request(f"{self.worker_url}/data", "POST", post_data)
            
        except json.JSONDecodeError as e:
            self.show_error(f"POST数据JSON格式错误: {str(e)}")
    
    def make_request(self, url, method, data=None):
        """发起网络请求"""
        # 如果有正在运行的请求，先停止它
        if self.request_thread and self.request_thread.isRunning():
            self.request_thread.quit()
            self.request_thread.wait()
        
        # 禁用按钮，显示加载状态
        self.set_buttons_enabled(False)
        self.responseTextEdit.setPlainText(f"正在请求 {method} {url}...")
        
        # 创建并启动请求线程
        self.request_thread = WorkerRequestThread(url, method, data)
        self.request_thread.request_finished.connect(self.on_request_success)
        self.request_thread.request_error.connect(self.on_request_error)
        self.request_thread.finished.connect(
            lambda: self.set_buttons_enabled(True)
        )
        self.request_thread.start()
    
    def on_request_success(self, result):
        """处理请求成功"""
        formatted_json = json.dumps(result, indent=2, ensure_ascii=False)
        self.responseTextEdit.setPlainText(formatted_json)
        
        InfoBar.success(
            title='请求成功',
            content="Worker响应已接收",
            duration=2000,
            parent=self,
            position=InfoBarPosition.TOP
        )
    
    def on_request_error(self, error_message):
        """处理请求错误"""
        self.responseTextEdit.setPlainText(f"错误: {error_message}")
        self.show_error(error_message)
    
    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error(
            title='请求失败',
            content=message,
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )
    
    def clear_response(self):
        """清除响应结果"""
        self.responseTextEdit.setPlainText("点击测试按钮查看Worker响应...")
    
    def set_buttons_enabled(self, enabled):
        """设置按钮启用状态"""
        self.testGetButton.setEnabled(enabled)
        self.testStatusButton.setEnabled(enabled)
        self.testPostButton.setEnabled(enabled)
    
    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self.request_thread and self.request_thread.isRunning():
            self.request_thread.quit()
            self.request_thread.wait()
        event.accept()


if __name__ == '__main__':
    # 启用高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # 设置 Fluent 主题
    setTheme(Theme.LIGHT)
    
    window = WorkerTestWindow()
    window.show()
    
    sys.exit(app.exec())