import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QApplication, QTableWidgetItem
from qfluentwidgets import CardWidget, StrongBodyLabel, LineEdit, PushButton, setCustomStyleSheet, SmoothMode, \
    TableWidget, InfoBar

from utils.custom_styles import ADD_BUTTON_STYLE
from config import URL
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker
from utils.ui_components import create_btn_widget
from utils.functional_utils import convert_date_to_chinese
from utils.app_logger import get_logger
from users.userDialog import AddUserDialog, UpdateUserDialog

error_logger = get_logger(logger_name='error_logger', log_file='error.log')


class UserInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('UserInterface')
        self.setWindowTitle('用户管理')

        # 后端返回的数据条目集合
        self.users = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 顶部按钮组
        card_widget = CardWidget(self)
        buttons_layout = QHBoxLayout(card_widget)

        self.search_label = StrongBodyLabel('根据用户名或id搜索: ', self)
        self.search_input = LineEdit(self)
        self.search_btn = PushButton('搜索', self)
        self.search_btn.clicked.connect(self.search_user)

        self.add_user_btn = PushButton('新增用户', self)
        self.add_user_btn.clicked.connect(self.add_user)
        setCustomStyleSheet(self.add_user_btn, ADD_BUTTON_STYLE, ADD_BUTTON_STYLE)

        buttons_layout.addWidget(self.search_label)
        buttons_layout.addWidget(self.search_input)
        buttons_layout.addWidget(self.search_btn)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.add_user_btn)

        layout.addWidget(card_widget)

        self.table_widget = TableWidget(self)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setBorderVisible(True)
        self.table_widget.verticalHeader().setVisible(True)  # 不显示行号
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

        # 设置表头
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels(
            ["用户id", "用户名", "密码", "所属员工", "创建日期", "状态", "权限", "操作"])

        layout.addWidget(self.table_widget)

        self.setStyleSheet("UserInterface {background-color:white;}")
        self.resize(1280, 760)

    def populate_table(self):
        """生成表格, 遍历从后端获取的数据并逐行填入到表格中"""
        self.table_widget.setRowCount(len(self.users))
        for row, user_info in enumerate(self.users):
            self.setup_table_row(row, user_info)

    def setup_table_row(self, row: int, user_info: dict):
        # 将多选框绘制到每行的首列
        for col, key in enumerate(
                ['user_id', 'username', 'password', 'employee_id', 'created_at', 'status', 'privilege']):
            match key:
                case 'password':
                    value = '********'
                case 'created_at':
                    value = convert_date_to_chinese(user_info.get(key, ''))
                case 'status':
                    value = '启用' if user_info.get(key, '') == 1 else '停用'
                case _:
                    value = user_info.get(key)
            # 单元格赋值
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table_widget.setItem(row, col, item)  #注意：第一列是多选框，所以在赋值时从第二列开始
        # 为每行添加编辑按钮
        action_widget = create_btn_widget(
            callback=lambda: self.update_user(user_info['user_id'])
        )
        self.table_widget.setCellWidget(row, 7, action_widget)  # 将组件添加到每行的最后一列

    def load_data(self):
        url = URL + '/users/all'
        try:
            # response = APIClient.get_request(url)
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            self.users = response.get("users")
            self.populate_table()
        except Exception as e:
            InfoBar.error(title='系统错误', content=str(e), parent=self, duration=5000)
            error_logger.error(f'userInterface.load_data: {str(e)}')

    def update_user(self, user_id):
        try:
            dialog = UpdateUserDialog(parent=self, user_id=user_id)
            if dialog.exec():
                url = URL + f'/users/update/{user_id}'
                user_info = dialog.get_user_info()

                response = Worker.unpack_thread_queue(APIClient.post_request, url, user_info)
                print(response)
                if response.get('success') is True:
                    InfoBar.success(title='更新成功', content='已完成用户资料更新', parent=self, duration=5000)
                    self.load_data()
                elif response.get('success') is False:
                    InfoBar.error(title='更新失败', content='未能完成用户资料更新', parent=self, duration=5000)
                else:
                    InfoBar.error(title='系统错误', content=response.get('error'), parent=self, duration=5000)
        except Exception as e:
            InfoBar.error(title='系统错误', content=str(e), parent=self, duration=5000)
            error_logger.error(f'userInterface.update_user: {str(e)}')

    def add_user(self):
        dialog = AddUserDialog(self)
        url = URL + '/users/create'
        try:
            if dialog.exec():
                user_info = dialog.get_user_info()
                # response = APIClient.post_request(url, user_info)
                response = Worker.unpack_thread_queue(APIClient.post_request, url, user_info)
                if response.get('success') is True:
                    InfoBar.success(title='用户创建成功', content=f'{user_info.get('employee_name')}已被成功创建',
                                    parent=self, duration=5000)
                    self.load_data()
                elif response.get('success') is False:
                    InfoBar.error(title='用户创建失败', content='未能成功创建用户', parent=self, duration=5000)
                else:
                    InfoBar.error(title='用户创建失败', content=response.get('error'), parent=self, duration=5000)
        except Exception as e:
            InfoBar.error(title='用户创建失败', content=str(e), parent=self, duration=5000)
            error_logger.error(f'userInterface.add_user: {str(e)}')

    def search_user(self):
        condition = self.search_input.text()
        try:
            if condition:
                url = URL + f'/users/search?condition={condition}'

                response = Worker.unpack_thread_queue(APIClient.get_request, url)

                if response.get('success') is True:
                    self.users = response.get('data')
                    self.populate_table()
                elif response.get('success') is False:
                    InfoBar.warning(title='没有结果', content='没有与查询条件相匹配的结果', parent=self, duration=5000)
                else:
                    InfoBar.error(title='系统错误', content=response.get('error'), parent=self, duration=5000)
            else:
                self.load_data()
        except Exception as e:
            error_logger.error(f'userInterface.search_user: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UserInterface()
    window.show()
    sys.exit(app.exec())
