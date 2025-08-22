"""应用程序启动器

负责根据不同模式启动相应的窗口
"""

from typing import Optional
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

# 导入窗口类
try:
    from .windows.main_window import MainAppWithMenu as MainWindow
except ImportError:
    MainWindow = None

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

from infrastructure.logging.logger import get_logger


class AppLauncher(QObject):
    """应用程序启动器
    
    根据不同的启动模式创建并显示相应的窗口
    """
    
    # 信号定义
    window_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        """初始化启动器
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self.logger = get_logger(self.__class__.__name__)
        self.current_window: Optional[QObject] = None
        
    def launch(self, mode: str = 'main') -> bool:
        """启动应用程序窗口
        
        Args:
            mode: 启动模式 ('main', 'login', 'register', 'auth', 'worker_test')
            
        Returns:
            bool: 启动是否成功
        """
        try:
            self.logger.info(f"启动模式: {mode}")
            
            if mode == 'main':
                return self._launch_main_window()
            elif mode == 'login':
                return self._launch_login_window()
            elif mode == 'register':
                return self._launch_register_window()
            elif mode == 'auth':
                return self._launch_auth_window()
            elif mode == 'worker_test':
                return self._launch_worker_test_window()
            else:
                self.logger.error(f"未知的启动模式: {mode}")
                self._show_error("错误", f"未知的启动模式: {mode}")
                return False
                
        except Exception as e:
            self.logger.error(f"启动窗口失败: {e}", exc_info=True)
            self._show_error("启动失败", f"启动窗口时发生错误: {str(e)}")
            return False
    
    def _launch_main_window(self) -> bool:
        """启动主窗口
        
        Returns:
            bool: 启动是否成功
        """
        if MainWindow is None:
            self.logger.error("MainWindow类未找到")
            self._show_error("错误", "主窗口类未找到，请检查导入")
            return False
            
        try:
            self.current_window = MainWindow()
            self.current_window.show()
            self.logger.info("主窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动主窗口失败: {e}", exc_info=True)
            self._show_error("启动失败", f"启动主窗口时发生错误: {str(e)}")
            return False
    
    def _launch_login_window(self) -> bool:
        """启动登录窗口
        
        Returns:
            bool: 启动是否成功
        """
        if LoginWindow is None:
            self.logger.error("LoginWindow类未找到")
            self._show_error("错误", "登录窗口类未找到，请检查导入")
            return False
            
        try:
            self.current_window = LoginWindow()
            self.current_window.show()
            self.logger.info("登录窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动登录窗口失败: {e}", exc_info=True)
            self._show_error("启动失败", f"启动登录窗口时发生错误: {str(e)}")
            return False
    
    def _launch_register_window(self) -> bool:
        """启动注册窗口
        
        Returns:
            bool: 启动是否成功
        """
        if RegisterWindow is None:
            self.logger.error("RegisterWindow类未找到")
            self._show_error("错误", "注册窗口类未找到，请检查导入")
            return False
            
        try:
            self.current_window = RegisterWindow()
            self.current_window.show()
            self.logger.info("注册窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动注册窗口失败: {e}", exc_info=True)
            self._show_error("启动失败", f"启动注册窗口时发生错误: {str(e)}")
            return False
    
    def _launch_auth_window(self) -> bool:
        """启动认证窗口
        
        Returns:
            bool: 启动是否成功
        """
        if AuthWindow is None:
            self.logger.error("AuthWindow类未找到")
            self._show_error("错误", "认证窗口类未找到，请检查导入")
            return False
            
        try:
            self.current_window = AuthWindow()
            self.current_window.show()
            self.logger.info("认证窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动认证窗口失败: {e}", exc_info=True)
            self._show_error("启动失败", f"启动认证窗口时发生错误: {str(e)}")
            return False
    
    def _launch_worker_test_window(self) -> bool:
        """启动Worker测试窗口
        
        Returns:
            bool: 启动是否成功
        """
        if WorkerTestWindow is None:
            self.logger.error("WorkerTestWindow类未找到")
            self._show_error("错误", "Worker测试窗口类未找到，请检查导入")
            return False
            
        try:
            self.current_window = WorkerTestWindow()
            self.current_window.show()
            self.logger.info("Worker测试窗口已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动Worker测试窗口失败: {e}", exc_info=True)
            self._show_error("启动失败", f"启动Worker测试窗口时发生错误: {str(e)}")
            return False
    
    def _show_error(self, title: str, message: str):
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
    
    def get_current_window(self) -> Optional[QObject]:
        """获取当前窗口
        
        Returns:
            当前窗口对象或None
        """
        return self.current_window
    
    def close_current_window(self):
        """关闭当前窗口"""
        if self.current_window:
            try:
                self.current_window.close()
                self.current_window = None
                self.window_closed.emit()
                self.logger.info("当前窗口已关闭")
            except Exception as e:
                self.logger.error(f"关闭窗口失败: {e}", exc_info=True)