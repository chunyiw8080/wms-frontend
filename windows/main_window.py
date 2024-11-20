import os

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QTableWidgetItem, QHeaderView
from qfluentwidgets import NavigationInterface, NavigationItemPosition, FluentIcon, setTheme, Theme, \
    NavigationDisplayMode, LineEdit, PushButton, TableWidget, SmoothMode
from backendRequests.inventoryRequests import fetch_inventory_data
import sys


class MainWindow(QMainWindow):
    def __init__(self, session: requests.Session):
        super().__init__()
        self.session = session
        # print(f'session: {self.session.cookies}')
        self.setWindowTitle("侧边栏示例")
        self.setGeometry(100, 100, 1200, 800)

        palette = self.palette()  # 获取当前调色板
        palette.setColor(QPalette.ColorRole.Window, QColor("white"))  # 将窗口背景色设置为白色
        self.setAutoFillBackground(True)  # 启用自动填充背景
        self.setPalette(palette)  # 应用调色板到窗口

        # 设置主题（浅色或深色）
        # setTheme(Theme.LIGHT)

        # 创建主窗口的小部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建主布局
        main_layout = QHBoxLayout(main_widget)

        # 创建侧边栏导航
        self.navigation_interface = NavigationInterface(main_widget)
        main_layout.addWidget(self.navigation_interface)

        # 创建内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.label = QLabel("欢迎！请选择左侧的功能按钮。")
        self.content_layout.addWidget(self.label)
        main_layout.addWidget(self.content_widget, 1)  # 内容区域占据剩余空间

        # 添加导航按钮
        self.add_navigation_item("主页", 'dashboard.svg', self.dashboard)
        self.add_navigation_item("库存管理", 'warehouse.svg', self.inventory_management)
        self.add_navigation_item("订单管理", 'orders.svg', self.order_management)
        self.add_navigation_item("员工管理", 'employee.svg', self.employee_management)
        self.add_navigation_item("供应商管理", 'provider.svg', self.provider_management)
        self.add_navigation_item("项目管理", 'project.svg', self.project_management)
        self.add_navigation_item("用户管理", 'users.svg', self.user_management)



    def add_navigation_item(self, text, icon_filename, callback):
        icon_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "icons")
        icon_path = os.path.join(icon_dir, icon_filename)
        """添加侧边栏按钮项"""
        self.navigation_interface.addItem(
            routeKey=text,
            icon=QIcon(icon_path),
            text=text,
            onClick=callback,
            position=NavigationItemPosition.TOP
        )

    def dashboard(self):
        self.clear_content_layout()

    def inventory_management(self):
        try:
            self.clear_content_layout()

            hbox = QHBoxLayout()
            self.cargo_name_search = LineEdit()
            self.cargo_name_search.setPlaceholderText("货品名称")
            hbox.addWidget(self.cargo_name_search)

            self.model_search = LineEdit()
            self.model_search.setPlaceholderText("型号")
            hbox.addWidget(self.model_search)

            self.search_btn = PushButton("搜索")
            hbox.addWidget(self.search_btn)

            data = fetch_inventory_data(self.session)
            inventories = data.get('inventories', [])
            print(inventories)

            table = TableWidget(self)
            table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
            table.setSelectRightClickedRow(True)

            # 启用边框并设置圆角
            table.setBorderVisible(True)
            table.setBorderRadius(8)

            table.setWordWrap(False)
            table.setRowCount(len(inventories))
            table.setColumnCount(6)

            for i, inventory in enumerate(inventories):
                for j, key in enumerate(
                        [ "cargo_name", "model", "categories", "count", "price", "total_price"]):
                    # 确保每个字段被转化为 QTableWidgetItem
                    item = QTableWidgetItem(str(inventory[key]))
                    table.setItem(i, j, item)  # 添加到表格中
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置居中对齐

            # 设置水平表头并隐藏垂直表头
            table.setHorizontalHeaderLabels(['货品名', '型号', '类别', '数量', '单价', '总价'])
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            # table.verticalHeader().hide()


            self.content_layout.addLayout(hbox)
            self.content_layout.addWidget(table)

            create_btn = PushButton("创建")
            create_btn.clicked.connect(self.open_create_dialog)
            self.content_layout.addWidget(create_btn)
        except Exception as e:
            print(e)

    def open_create_dialog(self):
        pass

    def order_management(self):
        self.clear_content_layout()

    def employee_management(self):
         self.clear_content_layout()

    def provider_management(self):
        self.clear_content_layout()

    def project_management(self):
        self.clear_content_layout()

    def user_management(self):
        self.clear_content_layout()

    def clear_content_layout(self):
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.takeAt(i)  # 使用 takeAt 移除布局项
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # 标记为删除
            elif item.layout():
                # 如果是布局（而不是 widget），则递归删除其中的内容
                layout = item.layout()
                while layout.count():
                    layout_item = layout.takeAt(0)
                    if layout_item.widget():
                        layout_item.widget().deleteLater()
                    elif layout_item.layout():
                        self.clear_layout(layout_item.layout())  # 递归清空布局


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { color: black; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
