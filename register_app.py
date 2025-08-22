# register_app.py

import sys
import json
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

# 导入 fluent-widgets 的核心组件
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, InfoBar, InfoBarPosition
)


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
                response = requests.get(self.url, headers=headers, timeout=10)
            
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
        except json.JSONDecodeError:
            self.error.emit('服务器响应格式错误')
        except Exception as e:
            self.error.emit(f'未知错误: {str(e)}')


class RegisterWindow(QWidget):
    """用户注册窗口"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        # --- 窗口基本设置 ---
        self.setWindowTitle("用户注册")
        self.setFixedSize(400, 600)

        # --- 创建布局 ---
        self.mainLayout = QVBoxLayout(self)

        # --- 创建控件 ---
        self.titleLabel = TitleLabel("创建新账户")
        self.usernameLineEdit = LineEdit()
        self.emailLineEdit = LineEdit()
        self.displayNameLineEdit = LineEdit()
        self.passwordLineEdit = PasswordLineEdit()
        self.confirmPasswordLineEdit = PasswordLineEdit()
        self.registerButton = PrimaryPushButton("注 册")

        # --- 美化和设置控件 ---
        self.usernameLineEdit.setPlaceholderText("请输入用户名")
        self.emailLineEdit.setPlaceholderText("请输入邮箱地址")
        self.displayNameLineEdit.setPlaceholderText("请输入显示名称（可选）")
        self.passwordLineEdit.setPlaceholderText("请输入密码（至少6个字符）")
        self.confirmPasswordLineEdit.setPlaceholderText("请再次输入密码")

        # --- 设置控件样式 ---
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置输入框的最小高度
        input_height = 40
        self.usernameLineEdit.setMinimumHeight(input_height)
        self.emailLineEdit.setMinimumHeight(input_height)
        self.displayNameLineEdit.setMinimumHeight(input_height)
        self.passwordLineEdit.setMinimumHeight(input_height)
        self.confirmPasswordLineEdit.setMinimumHeight(input_height)
        
        # 设置按钮样式
        self.registerButton.setMinimumHeight(45)

        # --- 添加控件到布局 ---
        self.mainLayout.addStretch(1)  # 顶部弹性空间
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addSpacing(30)
        
        self.mainLayout.addWidget(self.usernameLineEdit)
        self.mainLayout.addSpacing(15)
        
        self.mainLayout.addWidget(self.emailLineEdit)
        self.mainLayout.addSpacing(15)
        
        self.mainLayout.addWidget(self.displayNameLineEdit)
        self.mainLayout.addSpacing(15)
        
        self.mainLayout.addWidget(self.passwordLineEdit)
        self.mainLayout.addSpacing(15)
        
        self.mainLayout.addWidget(self.confirmPasswordLineEdit)
        self.mainLayout.addSpacing(30)
        
        self.mainLayout.addWidget(self.registerButton)
        self.mainLayout.addStretch(1)  # 底部弹性空间

        # 设置整体布局的边距
        self.mainLayout.setContentsMargins(40, 30, 40, 30)

        # --- 信号与槽连接 ---
        self.registerButton.clicked.connect(self.onRegister)

    def onRegister(self):
        """处理注册按钮点击事件"""
        username = self.usernameLineEdit.text().strip()
        email = self.emailLineEdit.text().strip()
        display_name = self.displayNameLineEdit.text().strip()
        password = self.passwordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()

        # 验证输入
        if not username or not email or not password:
            InfoBar.error(
                title='注册失败',
                content="请填写必要的注册信息！",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP
            )
            return
        
        if len(password) < 6:
            InfoBar.error(
                title='注册失败',
                content="密码长度至少需要6个字符！",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP
            )
            return
        
        if password != confirm_password:
            InfoBar.error(
                title='注册失败',
                content="两次输入的密码不一致！",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP
            )
            return

        # 禁用注册按钮，显示加载状态
        self.registerButton.setEnabled(False)
        self.registerButton.setText("注册中...")
        
        # 创建网络请求线程
        self.worker = NetworkWorker(
            'https://pw.yangxz.top/register',
            {
                'username': username,
                'email': email,
                'password': password,
                'display_name': display_name or username
            }
        )
        self.worker.finished.connect(self.on_register_success)
        self.worker.error.connect(self.on_register_error)
        self.worker.start()
    
    def on_register_success(self, result):
        """注册成功回调"""
        self.registerButton.setEnabled(True)
        self.registerButton.setText("注 册")
        
        InfoBar.success(
            title='注册成功',
            content="账户创建成功！请使用新账户登录。",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )
        
        # 清空表单
        self.usernameLineEdit.clear()
        self.emailLineEdit.clear()
        self.displayNameLineEdit.clear()
        self.passwordLineEdit.clear()
        self.confirmPasswordLineEdit.clear()
    
    def on_register_error(self, error_msg):
        """注册失败回调"""
        self.registerButton.setEnabled(True)
        self.registerButton.setText("注 册")
        
        InfoBar.error(
            title='注册失败',
            content=f"注册失败: {error_msg}",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )


if __name__ == '__main__':
    # 启用高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    # 设置 Fluent 主题
    setTheme(Theme.LIGHT)

    window = RegisterWindow()
    window.show()

    sys.exit(app.exec())