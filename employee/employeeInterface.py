import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QHeaderView, QTableWidgetItem
from qfluentwidgets import CardWidget, StrongBodyLabel, LineEdit, setCustomStyleSheet, PushButton, ComboBox, \
    TableWidget, SmoothMode, InfoBar, CheckBox

from utils.custom_styles import ADD_BUTTON_STYLE
from backendRequests.jsonRequests import APIClient
from config import URL
from utils.ui_components import create_btn_widget
from employee.employeeDialog import AddEmployeeDialog, UpdateEmployeeDialog
from utils.worker import Worker


class EmployeeInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('EmployeeInterface')
        self.setWindowTitle('库存管理')

        # 后端返回的数据条目集合
        self.employees = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 父布局 - 垂直布局
        layout = QVBoxLayout(self)

        # 顶部按钮组
        card_widget = CardWidget(self)
        buttons_layout = QHBoxLayout(card_widget)

        self.search_label = StrongBodyLabel(self)
        self.search_label.setText("按员工姓名或职务搜索: ")
        self.search_input = LineEdit(self)
        self.search_input.setFixedWidth(200)
        self.search_btn = PushButton('搜索', self)
        self.search_btn.clicked.connect(self.search_employees)

        self.operations_label = StrongBodyLabel(self)
        self.operations_label.setText('执行操作: ')
        self.operationsComboBox = ComboBox(self)
        self.operationsComboBox.setFixedWidth(150)
        self.operationsComboBox.addItems(
            ['---------------', '添加员工', '删除员工'])
        self.execBtn = PushButton('执行', self)
        setCustomStyleSheet(self.execBtn, ADD_BUTTON_STYLE, ADD_BUTTON_STYLE)
        self.execBtn.clicked.connect(self.exec_operations)

        buttons_layout.addWidget(self.search_label)
        buttons_layout.addWidget(self.search_input)
        buttons_layout.addWidget(self.search_btn)

        buttons_layout.addStretch(1)

        buttons_layout.addWidget(self.operations_label)
        buttons_layout.addWidget(self.operationsComboBox)
        buttons_layout.addWidget(self.execBtn)

        layout.addWidget(card_widget)

        self.table_widget = TableWidget(self)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setBorderVisible(True)
        self.table_widget.verticalHeader().setVisible(True)  # 不显示行号
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

        # 设置表头
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(
            ["", "员工id", "姓名", "性别", "职务", "操作"])

        layout.addWidget(self.table_widget)

        self.setStyleSheet("EmployeeInterface {background-color:white;}")
        self.resize(1280, 760)

    def exec_operations(self):
        index = self.operationsComboBox.currentIndex()
        match index:
            case 1:
                self.add_employee()
            case 2:
                self.delete_employees()

    def load_data(self):
        url = URL + '/employees/all'
        # response = APIClient.get_request(url)
        response = Worker.unpack_thread_queue(APIClient.get_request, url)
        if isinstance(response, (dict, list)):  # 有效 JSON
            if response.get('success') is True:  # 有数据
                self.employees = response.get('data')
                self.populate_table()
            else:
                InfoBar.warning(title='获取数据失败', content=response.get('message'), parent=self, duration=5000)
        elif isinstance(response, str):  # 错误信息
            InfoBar.error(title='服务器状态异常', content='无法连接到后端服务器', parent=self, duration=10000)
        else:
            print("Unexpected result:", response)

    def populate_table(self):
        """生成表格, 遍历从后端获取的数据并逐行填入到表格中"""
        self.table_widget.setRowCount(len(self.employees))
        for row, employee_info in enumerate(self.employees):
            self.setup_table_row(row, employee_info)

    def setup_table_row(self, row: int, employee_info: dict):
        # 将多选框绘制到每行的首列
        checkbox = CheckBox()
        self.table_widget.setCellWidget(row, 0, checkbox)
        for col, key in enumerate(['employee_id', 'employee_name', 'gender', 'position']):
            value = employee_info.get(key, '')
            # 单元格赋值
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table_widget.setItem(row, col + 1, item)  #注意：第一列是多选框，所以在赋值时从第二列开始

        # 为每行添加编辑按钮
        action_widget = create_btn_widget(
            callback=lambda: self.update_employee(employee_info['employee_id'])
        )
        self.table_widget.setCellWidget(row, 5, action_widget)  # 将组件添加到每行的最后一列

    def search_employees(self):
        condition = self.search_input.text().strip()
        if not condition:
            self.load_data()
            self.populate_table()
        else:
            url = URL + f'/employees/search?condition={condition}'
            response = APIClient.get_request(url)
            if response.get('success') is True:
                self.employees = response.get('data')
                self.populate_table()
            elif response.get('success') is False:
                InfoBar.warning(title='搜索失败', content=response.get('message'), parent=self, duration=4000)
                return
            else:
                InfoBar.error(title='操作失败', content=response.get('error'), parent=self, duration=4000)
                return

    def add_employee(self):
        url = URL + f'/employees/create'
        try:
            dialog = AddEmployeeDialog(self)
            if dialog.exec():
                info = dialog.get_employee_info()
                response = APIClient.post_request(url, info)
                if response.get('success') is True:
                    InfoBar.success(title='操作成功', content=response.get('message'), parent=self, duration=5000)
                    self.load_data()
                    self.populate_table()
                elif response.get('success') is False:
                    InfoBar.error(title='操作失败', content=response.get('message'), parent=self, duration=5000)
                elif response.get('error') is not None:
                    InfoBar.error(title='操作失败', content=response.get('error'), parent=self, duration=5000)
        except Exception as e:
            print(e)

    def update_employee(self, employee_id):
        url = URL + f'/employees/update/{employee_id}'
        try:
            dialog = UpdateEmployeeDialog(employee_id, self)
            if dialog.exec():
                new_employee_info = dialog.get_employee_info()
                response = APIClient.post_request(url, new_employee_info)
                if response['success'] is True:
                    InfoBar.success(title='操作成功', content=response['message'], parent=self, duration=5000)
                    self.load_data()
                    self.populate_table()
                elif response['success'] is False:
                    InfoBar.error(title='操作失败', content=response['message'], parent=self, duration=5000)
                elif response['error'] is not None:
                    InfoBar.error(title='操作失败', content=response['error'], parent=self, duration=5000)
        except Exception as e:
            print(e)

    def delete_employees(self):
        url = URL + '/employees/delete'
        selected_ids = self.get_selected_employee_ids()
        try:
            response = APIClient.delete_request(url, selected_ids)
            print(response)
            if response.get('success') is True:
                self.load_data()
                self.populate_table()
                InfoBar.success(title='删除成功', content='已成功删除所选员工信息', parent=self, duration=5000)
                return
            elif response.get('success') is False:
                InfoBar.warning(title='删除失败', content=response.get('message'), parent=self, duration=5000)
                return
            elif response.get('error'):
                InfoBar.error(title='删除失败', content=response.get('error'), parent=self, duration=5000)
                return
        except Exception as e:
            print(e)

    def get_selected_employee_ids(self) -> list:
        """获取并返回多选框被选中的数据的cargo_id"""
        selected_employee_ids = []
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if checkbox.isChecked():
                employee_id = str(self.table_widget.item(row, 1).text())
                selected_employee_ids.append(employee_id)

        return selected_employee_ids


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmployeeInterface()
    window.show()
    sys.exit(app.exec())
