# user_auth_app.py

import sys
import json
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget

# 导入 fluent-widgets 的核心组件
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, InfoBar, InfoBarPosition, Pivot
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


class LoginInterface(QWidget):
    """登录界面"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = TitleLabel("用户登录")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        # 用户名输入
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText("请输入用户名或邮箱")
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(15)
        
        # 密码输入
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(30)
        
        # 登录按钮
        self.login_btn = PrimaryPushButton("登 录")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # 设置布局边距
        layout.setContentsMargins(40, 30, 40, 30)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            InfoBar.error(
                title='登录失败',
                content="用户名和密码不能为空！",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP
            )
            return
        
        # 禁用登录按钮
        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")
        
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
        self.login_btn.setEnabled(True)
        self.login_btn.setText("登 录")
        
        user_info = result.get('user', {})
        display_name = user_info.get('display_name', '用户')
        
        InfoBar.success(
            title='登录成功',
            content=f"欢迎回来, {display_name}!",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )
    
    def on_login_error(self, error_msg):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("登 录")
        
        InfoBar.error(
            title='登录失败',
            content=f"登录失败: {error_msg}",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )


class RegisterInterface(QWidget):
    """注册界面"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = TitleLabel("用户注册")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        # 用户名输入
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(15)
        
        # 邮箱输入
        self.email_input = LineEdit()
        self.email_input.setPlaceholderText("请输入邮箱地址")
        self.email_input.setMinimumHeight(40)
        layout.addWidget(self.email_input)
        
        layout.addSpacing(15)
        
        # 显示名称输入
        self.display_name_input = LineEdit()
        self.display_name_input.setPlaceholderText("请输入显示名称（可选）")
        self.display_name_input.setMinimumHeight(40)
        layout.addWidget(self.display_name_input)
        
        layout.addSpacing(15)
        
        # 密码输入
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("请输入密码（至少6个字符）")
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(15)
        
        # 确认密码输入
        self.confirm_password_input = PasswordLineEdit()
        self.confirm_password_input.setPlaceholderText("请再次输入密码")
        self.confirm_password_input.setMinimumHeight(40)
        layout.addWidget(self.confirm_password_input)
        
        layout.addSpacing(30)
        
        # 注册按钮
        self.register_btn = PrimaryPushButton("注 册")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        # 设置布局边距
        layout.setContentsMargins(40, 30, 40, 30)
    
    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        display_name = self.display_name_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
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
        
        # 禁用注册按钮
        self.register_btn.setEnabled(False)
        self.register_btn.setText("注册中...")
        
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
        self.register_btn.setEnabled(True)
        self.register_btn.setText("注 册")
        
        InfoBar.success(
            title='注册成功',
            content="账户创建成功！请切换到登录页面使用新账户登录。",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )
        
        # 清空表单
        self.username_input.clear()
        self.email_input.clear()
        self.display_name_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
    
    def on_register_error(self, error_msg):
        self.register_btn.setEnabled(True)
        self.register_btn.setText("注 册")
        
        InfoBar.error(
            title='注册失败',
            content=f"注册失败: {error_msg}",
            duration=3000,
            parent=self,
            position=InfoBarPosition.TOP
        )


class UserAuthApp(QWidget):
    """用户认证主应用"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("用户认证系统")
        self.setFixedSize(500, 650)
        
        layout = QVBoxLayout(self)
        
        # 创建 Pivot 导航
        self.pivot = Pivot(self)
        self.pivot.addItem(
            routeKey='login',
            text='登录',
            onClick=lambda: self.stackedWidget.setCurrentWidget(
                self.login_interface
            )
        )
        self.pivot.addItem(
            routeKey='register', 
            text='注册',
            onClick=lambda: self.stackedWidget.setCurrentWidget(
                self.register_interface
            )
        )
        
        layout.addWidget(self.pivot)
        
        # 创建堆叠窗口部件
        self.stackedWidget = QStackedWidget()
        
        # 创建登录和注册界面
        self.login_interface = LoginInterface()
        self.register_interface = RegisterInterface()
        
        # 添加到堆叠窗口部件
        self.stackedWidget.addWidget(self.login_interface)
        self.stackedWidget.addWidget(self.register_interface)
        
        layout.addWidget(self.stackedWidget)
        
        # 设置默认显示登录界面
        self.stackedWidget.setCurrentWidget(self.login_interface)
        self.pivot.setCurrentItem('login')
        
        # 设置布局边距
        layout.setContentsMargins(20, 20, 20, 20)


if __name__ == '__main__':
    # 启用高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    # 设置 Fluent 主题
    setTheme(Theme.LIGHT)

    window = UserAuthApp()
    window.show()

    sys.exit(app.exec())