"""应用程序启动器

负责根据不同模式启动相应的窗口
"""

from typing import Optional
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

# 导入窗口类
from .windows.main_window import MainWindow

try:
    from .windows.login_window import LoginWindow
except ImportError:
    LoginWindow = None

try:
    from .windows.register_window import RegisterWindow
except ImportError:
    RegisterWindow = None

try:
    from .windows.auth_window import AuthWindow
except ImportError:
    AuthWindow = None

try:
    from .windows.worker_test_window import WorkerTestWindow
except ImportError:
    WorkerTestWindow = None

from infrastructure.logging.logger import getLogger
from business.services.auth_service import AuthService
from infrastructure.config.app_config import AppConfig


class AppLauncher(QObject):
    """应用程序启动器

    根据不同的启动模式创建并显示相应的窗口
    """

    # 信号定义
    windowClosed = pyqtSignal()

    def __init__(self, parent=None):
        """初始化启动器

        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self.logger = getLogger(self.__class__.__name__)
        self.currentWindow: Optional[QObject] = None

        # 初始化认证服务
        self.configManager = AppConfig()
        self.authService = AuthService(self.configManager)

        # 连接认证信号
        self._connectAuthSignals()

    def launch(self, mode: str = 'main') -> bool:
        """启动应用程序窗口

        Args:
            mode: 启动模式 ('main', 'login', 'register', 'auth', 'worker_test')

        Returns:
            bool: 启动是否成功
        """
        try:
            self.logger.info(f"启动模式: {mode}")

            # 智能启动逻辑：如果是main模式，先检查登录状态
            if mode == 'main':
                return self._smartLaunch()
            elif mode == 'login':
                return self._launchLoginWindow()
            elif mode == 'register':
                return self._launchRegisterWindow()
            elif mode == 'auth':
                return self._launchAuthWindow()
            elif mode == 'worker_test':
                return self._launchWorkerTestWindow()
            else:
                self.logger.error(f"未知的启动模式: {mode}")
                self._showError("错误", f"未知的启动模式: {mode}")
                return False

        except Exception as e:
            self.logger.error(f"启动窗口失败: {e}", exc_info=True)
            self._showError("启动失败", f"启动窗口时发生错误: {str(e)}")
            return False

    def _connectAuthSignals(self):
        """连接认证服务信号"""
        self.authService.loginSuccess.connect(self._onLoginSuccess)
        self.authService.logoutSuccess.connect(self._onLogoutSuccess)

    def _smartLaunch(self) -> bool:
        """智能启动逻辑

        根据用户登录状态决定启动哪个窗口：
        - 如果用户已登录或自动登录成功，启动主窗口
        - 否则启动登录窗口

        Returns:
            bool: 启动是否成功
        """
        try:
            # 尝试自动登录
            self.authService.tryAutoLogin()

            # 检查登录状态
            if self.authService.isLoggedIn():
                self.logger.info("用户已登录，启动主窗口")
                return self._launchMainWindow()
            else:
                self.logger.info("用户未登录，启动登录窗口")
                return self._launchLoginWindow()

        except Exception as e:
            self.logger.error(f"智能启动失败: {e}", exc_info=True)
            # 出错时默认启动登录窗口
            return self._launchLoginWindow()

    def _onLoginSuccess(self, userData):
        """登录成功处理"""
        self.logger.info(f"用户登录成功: {userData.get('user', {}).get('username', 'Unknown')}")
        # 如果当前是登录窗口，切换到主窗口
        if isinstance(self.currentWindow, LoginWindow):
            self._switchToMainWindow()

    def _onLogoutSuccess(self):
        """登出成功处理"""
        self.logger.info("用户登出成功")
        # 如果当前是主窗口，切换到登录窗口
        if MainWindow and isinstance(self.currentWindow, MainWindow):
            self._switchToLoginWindow()

    def _switchToMainWindow(self):
        """切换到主窗口"""
        try:
            if self.currentWindow:
                self.currentWindow.close()
            self._launchMainWindow()
        except Exception as e:
            self.logger.error(f"切换到主窗口失败: {e}", exc_info=True)

    def _switchToLoginWindow(self):
        """切换到登录窗口"""
        try:
            if self.currentWindow:
                self.currentWindow.close()
            self._launchLoginWindow()
        except Exception as e:
            self.logger.error(f"切换到登录窗口失败: {e}", exc_info=True)

    def _switchToRegisterWindow(self):
        """切换到注册窗口"""
        try:
            if self.currentWindow:
                self.currentWindow.close()
            self._launchRegisterWindow()
        except Exception as e:
            self.logger.error(f"切换到注册窗口失败: {e}", exc_info=True)

    def _onRegisterSuccess(self, userData):
        """注册成功处理"""
        self.logger.info(f"用户注册成功: {userData.get('username', 'Unknown')}")
        # 注册成功后切换到登录窗口
        self._switchToLoginWindow()

    def _launchMainWindow(self) -> bool:
        """启动主窗口

        Returns:
            bool: 启动是否成功
        """
        if MainWindow is None:
            self.logger.error("MainWindow类未找到")
            self._showError("错误", "主窗口类未找到，请检查导入")
            return False

        try:
            self.logger.info("开始创建MainWindow实例...")
            self.currentWindow = MainWindow()
            self.logger.info("MainWindow实例创建成功")

            self.logger.info("开始显示主窗口...")
            self.currentWindow.show()
            self.logger.info("主窗口显示成功")

            self.logger.info("主窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动主窗口失败: {e}", exc_info=True)
            self._showError("启动失败", f"启动主窗口时发生错误: {str(e)}")
            return False

    def _launchLoginWindow(self) -> bool:
        """启动登录窗口

        Returns:
            bool: 启动是否成功
        """
        if LoginWindow is None:
            self.logger.error("LoginWindow类未找到")
            self._showError("错误", "登录窗口类未找到，请检查导入")
            return False

        try:
            self.currentWindow = LoginWindow()
            # 连接窗口信号到启动器
            if hasattr(self.currentWindow, 'loginSuccess'):
                self.currentWindow.loginSuccess.connect(
                    self._onLoginSuccess
                )
            if hasattr(self.currentWindow, 'switch_to_register'):
                self.currentWindow.switch_to_register.connect(
                    self._switchToRegisterWindow
                )
            self.currentWindow.show()
            self.logger.info("登录窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动登录窗口失败: {e}", exc_info=True)
            self._showError("启动失败", f"启动登录窗口时发生错误: {str(e)}")
            return False

    def _launchRegisterWindow(self) -> bool:
        """启动注册窗口

        Returns:
            bool: 启动是否成功
        """
        if RegisterWindow is None:
            self.logger.error("RegisterWindow类未找到")
            self._showError("错误", "注册窗口类未找到，请检查导入")
            return False

        try:
            self.currentWindow = RegisterWindow()
            # 连接窗口信号到启动器
            if hasattr(self.currentWindow, 'registerSuccess'):
                self.currentWindow.registerSuccess.connect(
                    self._onRegisterSuccess
                )
            if hasattr(self.currentWindow, 'switch_to_login'):
                self.currentWindow.switch_to_login.connect(
                    self._switchToLoginWindow
                )
            self.currentWindow.show()
            self.logger.info("注册窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动注册窗口失败: {e}", exc_info=True)
            self._showError("启动失败", f"启动注册窗口时发生错误: {str(e)}")
            return False

    def _launchAuthWindow(self) -> bool:
        """启动认证窗口

        Returns:
            bool: 启动是否成功
        """
        if AuthWindow is None:
            self.logger.error("AuthWindow类未找到")
            self._showError("错误", "认证窗口类未找到，请检查导入")
            return False

        try:
            self.currentWindow = AuthWindow()
            self.currentWindow.show()
            self.logger.info("认证窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动认证窗口失败: {e}", exc_info=True)
            self._showError("启动失败", f"启动认证窗口时发生错误: {str(e)}")
            return False

    def _launchWorkerTestWindow(self) -> bool:
        """启动Worker测试窗口

        Returns:
            bool: 启动是否成功
        """
        if WorkerTestWindow is None:
            self.logger.error("WorkerTestWindow类未找到")
            self._showError("错误", "Worker测试窗口类未找到，请检查导入")
            return False

        try:
            self.currentWindow = WorkerTestWindow()
            self.currentWindow.show()
            self.logger.info("Worker测试窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动Worker测试窗口失败: {e}", exc_info=True)
            self._showError("启动失败", f"启动Worker测试窗口时发生错误: {str(e)}")
            return False

    def _showError(self, title: str, message: str):
        """显示错误消息

        Args:
            title: 错误标题
            message: 错误消息
        """
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.exec()
        except Exception as e:
            # 如果连错误对话框都无法显示，则输出到控制台
            print(f"错误: {title} - {message}")
            print(f"显示错误对话框失败: {e}")

    def getCurrentWindow(self) -> Optional[QObject]:
        """获取当前窗口

        Returns:
            当前窗口对象或None
        """
        return self.currentWindow

    def closeCurrentWindow(self):
        """关闭当前窗口"""
        if self.currentWindow:
            try:
                self.currentWindow.close()
                self.currentWindow = None
                self.windowClosed.emit()
                self.logger.info("当前窗口已关闭")
            except Exception as e:
                self.logger.error(f"关闭窗口失败: {e}", exc_info=True)
