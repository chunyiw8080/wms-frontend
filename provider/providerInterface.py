import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QApplication, QTableWidgetItem
from qfluentwidgets import CardWidget, StrongBodyLabel, LineEdit, PushButton, ComboBox, setCustomStyleSheet, \
    TableWidget, SmoothMode, CheckBox, InfoBar

from provider.providerDialog import AddProviderDialog, UpdateProviderDialog
from utils.custom_styles import ADD_BUTTON_STYLE
from config import URL
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker
from utils.app_logger import get_logger

error_logger = get_logger(logger_name='error_logger', log_file='error.log')

class ProviderInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('ProviderInterface')
        self.setWindowTitle('供应商管理')

        # 后端返回的数据条目集合
        self.providers = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 父布局 - 垂直布局
        layout = QVBoxLayout(self)

        # 顶部按钮组
        card_widget = CardWidget(self)
        buttons_layout = QHBoxLayout(card_widget)

        self.search_label = StrongBodyLabel(self)
        self.search_label.setText('根据项目名称搜索: ')
        self.search_input = LineEdit(self)
        self.search_input.setFixedWidth(200)
        self.search_btn = PushButton('搜索', self)
        self.search_btn.clicked.connect(self.search_project_by_name)

        self.operations_label = StrongBodyLabel(self)
        self.operations_label.setText('操作: ')
        self.operations_combo = ComboBox(self)
        self.operations_combo.setFixedWidth(200)
        self.operations_combo.addItems(['------', '新增', '编辑'])
        self.operation_exec_button = PushButton('执行', self)
        self.operation_exec_button.clicked.connect(self.exec_operations)
        setCustomStyleSheet(self.operation_exec_button, ADD_BUTTON_STYLE, ADD_BUTTON_STYLE)

        buttons_layout.addWidget(self.search_label)
        buttons_layout.addWidget(self.search_input)
        buttons_layout.addWidget(self.search_btn)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.operations_label)
        buttons_layout.addWidget(self.operations_combo)
        buttons_layout.addWidget(self.operation_exec_button)

        layout.addWidget(card_widget)

        self.table_widget = TableWidget(self)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setBorderVisible(True)
        self.table_widget.verticalHeader().setVisible(False)  # 不显示行号
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["", "供应商名称"])

        layout.addWidget(self.table_widget)

        self.setStyleSheet("ProviderInterface {background-color:white;}")
        self.resize(1280, 760)

    def populate_table(self):
        """生成表格, 遍历从后端获取的数据并逐行填入到表格中"""
        self.table_widget.setRowCount(len(self.providers))
        for row, provider_info in enumerate(self.providers):
            self.setup_table_row(row, provider_info)
        self.adjust_column_widths()

    def adjust_column_widths(self):
        # 设置第一列为固定宽度
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_widget.setColumnWidth(0, 50)  # 第一列宽度固定为 50 像素

        # 让其他列自动调整宽度以适应表格大小
        for col in range(2, self.table_widget.columnCount()):
            self.table_widget.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch
            )

    def setup_table_row(self, row: int, provider_info: dict):
        # 将多选框绘制到每行的首列
        checkbox = CheckBox()
        self.table_widget.setCellWidget(row, 0, checkbox)
        for col, key in enumerate(['provider_name']):
            value = provider_info.get(key, '')
            # 单元格赋值
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table_widget.setItem(row, col + 1, item)  #注意：第一列是多选框，所以在赋值时从第二列开始

    def load_data(self):
        url = URL + '/providers/all'
        # response = APIClient.get_request(url)
        try:
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            if response.get('success') is True:
                data = response['data']
                self.providers = [ item for item in data if item['provider_name'] != 'null']
                self.populate_table()
        except Exception as e:
            error_logger.error(f'providerInterface.load_data: {e}')

    def search_project_by_name(self):
        if self.search_input.text() == '':
            self.load_data()
            self.populate_table()
            return
        provider_name = self.search_input.text().strip()
        url = URL + f'/providers/search?name={provider_name}'
        try:
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            print(response)
            if response.get('success') is True:
                data = response['data']
                self.providers = [data] if isinstance(data, str) else data
                self.populate_table()
            elif response.get('error') is not None:
                InfoBar.error(title='查询失败', content=response.get('error'), parent=self, duration=5000)
            else:
                InfoBar.error(title='查询失败', content='没有对应的数据', parent=self, duration=5000)
        except Exception as e:
            InfoBar.error(title='系统错误', content=str(e), parent=self, duration=5000)
            error_logger.error(f'providerInterface.search_project_by_name: {e}')

    def exec_operations(self):
        index = self.operations_combo.currentIndex()
        match index:
            case 1:
                self.add_project()
            case 2:
                selected_project_list = self.get_selected_providers()
                if len(selected_project_list) != 0:
                    for project_name in selected_project_list:
                        self.edit_project(project_name)

    def add_project(self):
        dialog = AddProviderDialog(self)
        if dialog.exec():
            provider_name = dialog.get_provider_info()
            url = URL + '/providers/create'
            data = {"provider_name": provider_name}
            try:
                response = Worker.unpack_thread_queue(APIClient.post_request, url, data)
                if response.get('success') is True:
                    InfoBar.success(title='操作成功', content=response.get('message'), parent=self)
                    self.load_data()
                    self.populate_table()
                elif response.get('error') is not None:
                    InfoBar.error(title='操作成功', content=response.get('error'), parent=self)
                else:
                    InfoBar.warning(title='操作失败', content=response.get('message'), parent=self)
            except Exception as e:
                error_logger.error(f'providerInterface.add_project: {e}')

    def delete_project(self):
        pass

    def edit_project(self, provider_name):
        try:
            dialog = UpdateProviderDialog(provider_name, self)
            if dialog.exec():
                project = dialog.get_provider_info()
                url = URL + f'/providers/update/{provider_name}'
                response = APIClient.post_request(url, project)
                print(response)
                if response.get('success') is True:
                    InfoBar.success(title='操作成功', content='项目名称已更改', parent=self, duration=5000)
                    self.load_data()
                    self.populate_table()
                elif response.get('success') is False:
                    InfoBar.warning(title='操作成功', content='项目名称已更改', parent=self, duration=5000)
                else:
                    InfoBar.error(title='系统错误', content=response.get('error'), parent=self, duration=5000)
        except Exception as e:
            InfoBar.error(title='系统错误', content=str(e), parent=self, duration=5000)
            error_logger.error(f'providerInterface.edit_project: {e}')

    def get_selected_providers(self):
        """获取并返回多选框被选中的数据的cargo_id"""
        selected_provider_name = []
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if checkbox.isChecked():
                provider_name = str(self.table_widget.item(row, 1).text())
                selected_provider_name.append(provider_name)

        return selected_provider_name


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProviderInterface()
    window.show()
    sys.exit(app.exec())