# login_app.py

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

# 导入 fluent-widgets 的核心组件
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, CheckBox, HyperlinkButton, InfoBar,
    InfoBarPosition
)


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
        username = self.usernameLineEdit.text()
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

        # 假设正确的用户名和密码是 admin / 123456
        if username == "admin" and password == "123456":
            InfoBar.success(
                title='登录成功',
                content=f"欢迎回来, {username}!",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP
            )
            # 在这里，你可以关闭登录窗口并打开主窗口
            # self.close()
            # self.main_window = MainWindow()
            # self.main_window.show()
        else:
            InfoBar.warning(
                title='登录失败',
                content="用户名或密码错误！",
                duration=2000,
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
