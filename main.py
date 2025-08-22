# main.py

import sys  # 导入 sys 模块，用于处理 Python 运行时环境的变量和函数

# 从 PyQt6.QtWidgets 模块中导入我们需要的类
# QApplication: 管理应用程序的主要设置和控制流
# QMainWindow: 主窗口类，可以包含菜单栏、工具栏、状态栏等
# QWidget: 所有用户界面对象的基类
# QLabel: 用于显示文本或图像的控件
# QVBoxLayout: 垂直布局管理器
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt  # 导入Qt核心模块，用于访问如对齐方式等枚举值

# 创建一个继承自 QMainWindow 的自定义窗口类
# 这是构建复杂应用的常用模式，便于组织代码


class MyWindow(QMainWindow):
    def __init__(self):
        # 调用父类的构造函数
        super().__init__()

        # 初始化 UI
        self.initUI()

    def initUI(self):
        # 1. 设置窗口标题
        self.setWindowTitle("我的第一个 PyQt 应用")

        # 2. 设置窗口的初始位置和大小
        # setGeometry(x, y, width, height)
        # x, y 是窗口左上角在屏幕上的坐标
        # width, height 是窗口的宽度和高度
        self.setGeometry(300, 300, 400, 200)

        # 3. 创建一个中心小部件 (Central Widget)
        # QMainWindow 需要一个中心小部件来放置其他控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 4. 创建一个布局管理器
        # QVBoxLayout 会将控件垂直排列
        layout = QVBoxLayout()

        # 5. 创建一个标签 (QLabel) 控件
        label = QLabel("你好, PyQt 世界!")
        # 设置标签文本居中对齐
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 6. 将标签添加到布局中
        layout.addWidget(label)

        # 7. 将布局应用到中心小部件上
        central_widget.setLayout(layout)


# Python的主入口点
if __name__ == '__main__':
    # 1. 创建一个 QApplication 实例
    # 每个 PyQt 应用都必须有一个 QApplication 实例
    # sys.argv 允许你从命令行传递参数给你的应用
    app = QApplication(sys.argv)

    # 2. 创建我们自定义窗口的一个实例
    window = MyWindow()

    # 3. 显示窗口
    window.show()

    # 4. 启动应用程序的事件循环
    # app.exec() 开始运行应用，并等待用户交互（如点击、按键等）
    # sys.exit() 确保程序在关闭时能够干净地退出
    sys.exit(app.exec())
