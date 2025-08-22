# login_app.py

import sys
import json
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

# 导入 fluent-widgets 的核心组件
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, CheckBox, HyperlinkButton, InfoBar,
    InfoBarPosition
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


class LoginWindow(QWidget):
    """一个漂亮的 Fluent Design 风格登录窗口"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        # --- 窗口基本设置 ---
        self.setWindowTitle("Fluent Design 登录")
        # 登录窗口通常大小是固定的
        self.setFixedSize(360, 480)

        # --- 创建布局 ---
        # 整体垂直布局
        self.mainLayout = QVBoxLayout(self)

        # 水平布局，用于放置“记住我”和“忘记密码”
        self.optionLayout = QHBoxLayout()

        # --- 创建控件 ---
        self.titleLabel = TitleLabel("欢迎回来")
        self.usernameLineEdit = LineEdit()
        self.passwordLineEdit = PasswordLineEdit()
        self.rememberMeCheckBox = CheckBox("记住我")
        self.forgotPasswordLink = HyperlinkButton("#", "忘记密码？")
        self.loginButton = PrimaryPushButton("登 录")

        # --- 美化和设置控件 ---
        self.usernameLineEdit.setPlaceholderText("请输入用户名或邮箱")
        # 给输入框左侧添加一个图标（可选，需要图标文件）
        # from qfluentwidgets import FluentIcon
        # self.usernameLineEdit.setLeadingAction(FluentIcon.PEOPLE)

        self.passwordLineEdit.setPlaceholderText("请输入密码")
        # self.passwordLineEdit.setLeadingAction(FluentIcon.LOCK)

        # 让登录按钮更高，更醒目
        self.loginButton.setFixedHeight(40)

        # --- 布局管理 ---
        # 在标题上下添加一些空间，使其更美观
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(
            self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addSpacing(40)

        # 添加输入框
        self.mainLayout.addWidget(self.usernameLineEdit)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addWidget(self.passwordLineEdit)
        self.mainLayout.addSpacing(15)

        # "记住我" 和 "忘记密码" 在同一行
        self.optionLayout.addWidget(self.rememberMeCheckBox)
        self.optionLayout.addStretch(1)  # 添加伸缩，将“忘记密码”推到最右边
        self.optionLayout.addWidget(self.forgotPasswordLink)
        self.mainLayout.addLayout(self.optionLayout)
        self.mainLayout.addSpacing(30)

        # 添加登录按钮
        self.mainLayout.addWidget(self.loginButton)

        # 添加一个伸缩，将所有内容向上推
        self.mainLayout.addStretch(1)

        # 设置整体布局的边距
        self.mainLayout.setContentsMargins(30, 0, 30, 30)

        # --- 信号与槽连接 ---
        self.loginButton.clicked.connect(self.onLogin)

    def onLogin(self):
        """处理登录按钮点击事件"""
        username = self.usernameLineEdit.text().strip()
        password = self.passwordLineEdit.text()

        # 简单的验证逻辑
        if not username or not password:
            # 使用 InfoBar 显示错误信息，比 QMessageBox 更优雅
            InfoBar.error(
                title='登录失败',
                content="用户名和密码不能为空！",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP
            )
            return

        # 禁用登录按钮，显示加载状态
        self.loginButton.setEnabled(False)
        self.loginButton.setText("登录中...")
        
        # 创建网络请求线程
        self.worker = NetworkWorker(
            'https://pw.yangxz.top/login',
            {
                'username': username,
                'password': password
            }
        )
        self.worker.finished.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        self.worker.start()
    
    def on_login_success(self, result):
        """登录成功回调"""
        self.loginButton.setEnabled(True)
        self.loginButton.setText("登 录")
        
        # 显示成功信息
        user_info = result.get('user', {})
        display_name = user_info.get('display_name', '用户')
        
        InfoBar.success(
            title='登录成功',
            content=f"欢迎回来, {display_name}!",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )
        
        # 在这里可以保存用户信息或跳转到主界面
        # self.close()
        # self.main_window = MainWindow(user_info)
        # self.main_window.show()
    
    def on_login_error(self, error_msg):
        """登录失败回调"""
        self.loginButton.setEnabled(True)
        self.loginButton.setText("登 录")
        
        InfoBar.error(
            title='登录失败',
            content=f"登录失败: {error_msg}",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )


if __name__ == '__main__':
    # 启用高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # 注意：在 PyQt6 中，AA_EnableHighDpiScaling 和 AA_UseHighDpiPixmaps 已被移除
    # 因为 PyQt6 默认启用高 DPI 支持

    app = QApplication(sys.argv)

    # --- 设置 Fluent 主题 (至关重要的一步！) ---
    # 你可以尝试 Theme.DARK, Theme.LIGHT, 或 Theme.AUTO
    setTheme(Theme.LIGHT)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())
