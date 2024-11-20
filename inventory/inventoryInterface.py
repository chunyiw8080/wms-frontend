import math, urllib, sys, openpyxl
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QHeaderView, QTableWidgetItem, \
     QFileDialog
from qfluentwidgets import CardWidget, PushButton, SearchLineEdit, TableWidget, setCustomStyleSheet, InfoBar, CheckBox, \
    MessageBox, LineEdit, ComboBox, PrimaryPushButton, StrongBodyLabel, SmoothMode
from utils.custom_styles import ADD_BUTTON_STYLE, DELETE_BUTTON_STYLE
from backendRequests.jsonRequests import get_request, post_request, delete_request
from inventoryDialog import AddInventoryDialog, UpdateInventoryDialog
from utils.ui_components import create_action_widget, CustomHeaderView
from inventory.db_utils import load_categories


class InventoryInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('InventoryInterface')
        self.setWindowTitle('库存管理')

        # 后端返回的数据条目集合
        self.inventories = []

        # 分页属性
        self.current_page = 1
        self.per_page = 20
        self.total_pages = 1

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 父布局 - 垂直布局
        layout = QVBoxLayout(self)

        # 顶部按钮组
        card_widget = CardWidget(self)
        buttons_layout = QHBoxLayout(card_widget)

        self.category_label = StrongBodyLabel(self)
        self.category_label.setText('分类显示: ')
        self.categoriesComboBox = ComboBox(self)
        self.categoriesComboBox.setFixedWidth(200)
        self.categoriesComboBox.addItem('所有类别', None)
        self.categoriesComboBox.addItems(load_categories())
        self.categoriesComboBox.currentIndexChanged.connect(self.on_category_selected)

        self.search_label = StrongBodyLabel(self)
        self.search_label.setText("条件搜索: ")
        self.cargo_name_input = LineEdit(self)
        self.cargo_name_input.setPlaceholderText('输入货品名称')
        self.cargo_name_input.setFixedWidth(200)

        self.model_input = LineEdit(self)
        self.model_input.setPlaceholderText('输入型号')
        self.model_input.setFixedWidth(200)

        self.searchButton = PushButton('搜索', self)
        self.searchButton.clicked.connect(self.search_inventories)

        self.operations_label = StrongBodyLabel(self)
        self.operations_label.setText('执行操作: ')
        self.operationsComboBox = ComboBox(self)
        self.operationsComboBox.setFixedWidth(150)
        self.operationsComboBox.addItems(['---------------', '新增记录', '批量删除', '批量编辑', '导出为Excel', '从Excel中导入'])
        self.execBtn = PushButton('执行', self)
        setCustomStyleSheet(self.execBtn, ADD_BUTTON_STYLE, ADD_BUTTON_STYLE)
        self.execBtn.clicked.connect(self.exec_operations)

        buttons_layout.addWidget(self.category_label)
        buttons_layout.addWidget(self.categoriesComboBox)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.search_label)
        buttons_layout.addWidget(self.cargo_name_input)
        buttons_layout.addWidget(self.model_input)
        buttons_layout.addWidget(self.searchButton)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.operations_label)
        buttons_layout.addWidget(self.operationsComboBox)
        buttons_layout.addWidget(self.execBtn)

        layout.addWidget(card_widget)

        # 添加Table
        self.table_widget = TableWidget(self)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setBorderVisible(True)
        self.table_widget.verticalHeader().setVisible(True)  # 不显示行号
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

        # 设置表头
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels(
            ["", "货品编号", "货品名称", "型号", "类别", "数量", "单价", "总价", "操作"])

        # self.custom_header = CustomHeaderView(orientation=Qt.Orientation.Horizontal, parent=self.table_widget)
        # self.table_widget.setHorizontalHeader(self.custom_header)

        layout.addWidget(self.table_widget)

        # 创建分页布局
        self.paginationWidget = QWidget(self)
        pagination_layout = QHBoxLayout(self.paginationWidget)
        self.prevButton = PrimaryPushButton("上一页", self)
        self.prevButton.clicked.connect(self.load_prev_page)
        self.pageLabel = StrongBodyLabel(self)
        self.nextButton = PrimaryPushButton("下一页", self)
        self.nextButton.clicked.connect(self.load_next_page)


        pagination_layout.addStretch(10)
        pagination_layout.addWidget(self.prevButton)
        pagination_layout.addWidget(self.pageLabel)
        pagination_layout.addWidget(self.nextButton)

        layout.addWidget(self.paginationWidget)

        self.setStyleSheet("InventoryInterface {background-color:white;}")
        self.resize(1280, 760)

    def exec_operations(self):
        index = self.operationsComboBox.currentIndex()
        match index:
            case 1:
                self.add_inventory()
            case 2:
                self.batch_delete_inventory()
            case 3:
                ids = self.get_selected_inventory_ids()
                if len(ids) != 0:
                    for cargo_id in ids:
                        self.update_inventory(cargo_id)
                else:
                    InfoBar.warning(title='操作失败', content='请先选择要编辑的条目', parent=self, duration=4000)
            case 4:
                self.export_to_excel()
            case 5:
                self.import_from_excel()
        self.operationsComboBox.setCurrentIndex(0)

    def get_count(self):
        """获取数据的总量或者分类数据的总量，用于设置分页控制器"""
        url = 'http://127.0.0.1:5000/inventory/count'
        if self.categoriesComboBox.currentIndex() != 0:
            # 当分类选框有实际选中时，构造带参的url参数为category=被选中的分类Text
            url += '?category=' + self.categoriesComboBox.currentText()
            response = get_request(url)
        else:
            response = get_request(url)
        count = response['count']
        return count

    def load_data(self):
        # 从后端获取数据
        url = f'http://127.0.0.1:5000/inventory/page/{self.current_page}'
        if self.categoriesComboBox.currentIndex() == 0:
            # 分类选框为全部类别时的分页控制器
            count = self.get_count()
            self.total_pages = math.ceil(count / self.per_page)
            self.update_pagination_controls()
            result = get_request(url)
        else:
            # 当分类被选中时，构造带参url
            url += '?category=' + self.categoriesComboBox.currentText()
            result = get_request(url)
            self.update_pagination_controls()
        # 判断返回值类型
        if isinstance(result, (dict, list)):  # 有效 JSON
            if result['success'] is True:  # 有数据
                self.inventories = result['data']
                self.populate_table()
            else:
                InfoBar.warning(title='获取数据失败', content=result['message'], parent=self, duration=5000)
        elif isinstance(result, str):  # 错误信息
            InfoBar.error(title='服务器状态异常', content='无法连接到后端服务器', parent=self, duration=10000)
        else:
            print("Unexpected result:", result)

    def update_pagination_controls(self):
        # 判断分页是否有数据，如果有显示当前是第几页，一共几页，否则显示0页
        if self.total_pages:
            if self.total_pages == 1:
                self.hide_pagination(False)
            else:
                self.hide_pagination(True)
                self.pageLabel.setText(f'第 {self.current_page} 页, 共 {self.total_pages} 页')
                self.prevButton.setEnabled(self.current_page > 1)
                self.nextButton.setEnabled(self.current_page < self.total_pages)
        else:
            self.pageLabel.setText(f'共 0 页')
            self.prevButton.setDisabled(True)
            self.nextButton.setDisabled(True)

    def populate_table(self):
        """生成表格, 遍历从后端获取的数据并逐行填入到表格中"""
        self.table_widget.setRowCount(len(self.inventories))
        for row, inventory_info in enumerate(self.inventories):
            self.setup_table_row(row, inventory_info)

    def setup_table_row(self, row: int, inventory_info: dict):
        # 将多选框绘制到每行的首列
        checkbox = CheckBox()
        self.table_widget.setCellWidget(row, 0, checkbox)
        for col, key in enumerate(['cargo_id', 'cargo_name', 'model', 'categories', 'count', 'price', 'total_price']):
            value = inventory_info.get(key, '')
            # 单元格赋值
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, col + 1, item)  #注意：第一列是多选框，所以在赋值时从第二列开始

        # 为每行添加编辑按钮
        action_widget = create_action_widget(
            callback=lambda: self.update_inventory(inventory_info['cargo_id'])
        )
        self.table_widget.setCellWidget(row, 8, action_widget)  # 将组件添加到每行的最后一列

    def update_inventory(self, cargo_id: str):
        try:
            dialog = UpdateInventoryDialog(cargo_id, self)
            if dialog.exec():
                new_inventory_info = dialog.get_inventory_info()
                response = post_request(f'http://127.0.0.1:5000/inventory/update/{cargo_id}', new_inventory_info)
                if response.get('success'):
                    InfoBar.success(title='操作成功', content=response.get('message'), parent=self, duration=4000)
                    self.load_data()
                    self.populate_table()
                else:
                    InfoBar.error(title='操作失败', content=response.get('message'), parent=self, duration=4000)
        except Exception as e:
            InfoBar.error(title='操作失败', content=str(e), parent=self, duration=4000)

    def add_inventory(self):
        """添加库存记录"""
        try:
            dialog = AddInventoryDialog(self)
            if dialog.exec():
                inventory_info = dialog.get_inventory_info()
                response = post_request('http://127.0.0.1:5000/inventory/create', inventory_info)
                # print(f'response: {response}')
                if response.get('success'):
                    InfoBar.success(title='操作成功', content=response.get('message'), parent=self, duration=4000)
                    self.load_data()
                    self.populate_table()
                else:
                    InfoBar.error(title='操作失败', content=response.get('message'), parent=self, duration=4000)
        except Exception as e:
            InfoBar.error(title='操作失败', content=str(e), parent=self, duration=4000)

    def batch_delete_inventory(self):
        """批量删除"""
        try:
            selected_inventory_ids = self.get_selected_inventory_ids()
            if not selected_inventory_ids:
                InfoBar.warning(title='删除失败', content='请先选中要删除的条目', parent=self, duration=4000)
                return
            else:
                w = MessageBox("确认删除", f'确定要删除 {len(selected_inventory_ids)} 个条目吗?', self)
                if w.exec():
                    response = delete_request('http://127.0.0.1:5000/inventory/delete', selected_inventory_ids)
                    if response.get('success'):
                        InfoBar.success(title='操作成功', content=response.get('message'), parent=self, duration=4000)
                        self.load_data()
                        self.populate_table()
                    else:
                        InfoBar.error(title='操作失败', content=response.get('error'), parent=self, duration=4000)
        except Exception as e:
            InfoBar.error(title='操作失败', content=str(e), parent=self, duration=4000)


    def get_selected_inventory_ids(self) -> list:
        """获取并返回多选框被选中的数据的cargo_id"""
        selected_inventory_ids = []
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if checkbox.isChecked():
                cargo_id = str(self.table_widget.item(row, 1).text())
                selected_inventory_ids.append(cargo_id)

        return selected_inventory_ids

    def search_inventories(self):
        try:
            cargo_name = self.cargo_name_input.text()
            model = self.model_input.text()
            if not cargo_name and not model:
                self.load_data()
                self.populate_table()
                self.current_page = 1
                self.update_pagination_controls()
                self.hide_pagination(True)
            else:
                url = "http://127.0.0.1:5000/inventory/search?"
                if cargo_name:
                    url += f"cargo_name={cargo_name}"
                if model:
                    url += f"&model={model}"
                self.categoriesComboBox.setCurrentIndex(0)
                response = get_request(url)

                if response.get('success'):
                    self.inventories = response.get('data')
                    self.populate_table()
                    self.categoriesComboBox.setCurrentIndex(0)
                    self.hide_pagination(False)
                else:
                    InfoBar.warning(title='操作失败', content=response.get('message'), parent=self, duration=4000)
                    self.categoriesComboBox.setCurrentIndex(0)
        except Exception as e:
            InfoBar.error(title='操作失败', content=str(e), parent=self, duration=4000)

    def on_category_selected(self):
        """当分类栏中有项目被选中时的操作"""
        try:
            category_page_count = self.get_count()
            self.total_pages = math.ceil(category_page_count / self.per_page)
            # 更新分页控制器
            self.current_page = 1
            self.update_pagination_controls()
            index = self.categoriesComboBox.currentIndex()
            if index == 0:
                # 如果选中的index为0，即全部类别，显示全部数据，设置分页为初始状态
                self.load_data()
                self.populate_table()
            else:
                url = f"http://127.0.0.1:5000/inventory/search?category={self.categoriesComboBox.currentText()}"
                response = get_request(url)
                if response.get('success'):
                    # print(response.get('data'))
                    self.inventories = response.get('data')
                    self.populate_table()
                else:
                    InfoBar.warning(title='操作失败', content=response.get('message'), parent=self, duration=4000)
        except Exception as e:
            InfoBar.error(title='操作失败', content=str(e), parent=self, duration=4000)

    def load_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()
            self.populate_table()

    def load_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()
            self.populate_table()

    def hide_pagination(self, res):
        self.paginationWidget.setVisible(res)

    def export_to_excel(self):
        try:
            category = self.categoriesComboBox.currentText()
            w = MessageBox("确认导出", f"是否将 {category} 的全部条目导出为excel文件?", self)
            if w.exec():
                if self.categoriesComboBox.currentIndex() == 0:
                    url = f"http://127.0.0.1:5000/inventory/all"
                else:
                    url = f"http://127.0.0.1:5000/inventory/all?category={category}"
                response = get_request(url)
                if response.get('error'):
                    InfoBar.warning(title='操作失败', content=response.get('error'), parent=self, duration=4000)
                    return
                if response.get('success') is False:
                    InfoBar.warning(title='操作失败', content=response.get('message'), parent=self, duration=4000)
                    return
                else:
                    exported_data = response.get('data')
                    date = datetime.today().strftime('%Y-%m-%d')
                    filename = f"{category}库存记录-{date}"
                    # print(exported_data)
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = filename
                    # 写入表头
                    headers = ["货品编号", "货品名称", "型号", "类别", "数量", "单价", "总价"]
                    ws.append(headers)
                    # 写入库存信息
                    for inventory in exported_data:
                        row = [
                            inventory['cargo_id'],
                            inventory['cargo_name'],
                            inventory['model'],
                            inventory['categories'],
                            inventory['count'],
                            inventory['price'],
                            inventory['total_price']
                        ]
                        ws.append(row)
                    file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", f"{filename}.xlsx", "Excel Files (*.xlsx)")
                    if file_path:
                        wb.save(file_path)
                        InfoBar.success(title="操作成功", content="已成功导出数据为Excel文件", parent=self, duration=4000)
                    else:
                        InfoBar.warning(title="操作失败", content="操作被终止", parent=self, duration=4000)
        except Exception as e:
            InfoBar.error(title="操作失败", content=str(e), parent=self, duration=4000)

    def import_from_excel(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "Excel Files (*.xlsx)")
            if not file_path:
                InfoBar.warning("操作取消", "用户终止了导入操作", parent=self, duration=4000)
                return
            else:
                wb = openpyxl.load_workbook(filename=file_path)
                ws = wb.active
                expected_header = ["货品编号", "货品名称", "型号", "类别", "数量", "单价", "总价"]
                headers = [ cell.value for cell in ws[1]]
                if headers != expected_header:
                    InfoBar.error(title="操作失败", content="表头与预期不符", parent=self, duration=4000)
                    return
                else:
                    # 询问用户如何处理已存在的条目信息
                    imported_count, skipped_count = 0, 0
                    skipped_row = []
                    dataset = []
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        cargo_id, cargo_name, model, categories, count, price, total_price = row
                        if not all([cargo_name, model, categories, count, price]):
                            skipped_count += 1
                            skipped_row.append(f"{skipped_count}. {cargo_name} - {model}\n")
                        else:
                            info = {
                                "cargo_name": cargo_name,
                                "model": model,
                                "categories": categories,
                                "count": count,
                                "price": price,
                            }
                            dataset.append(info)
                    url = f"http://127.0.0.1:5000/inventory/import"
                    json = {
                        "dataset": dataset
                    }
                    response = post_request(url, json)
                    res = response.get('success')
                    skipped_row_backend = response.get('skipped_row')
                    skipped_row.append(skipped_row_backend)
                    if res is False:
                        InfoBar.warning(title='导入失败', content=f'以下数据: {skipped_row} 重复', parent=self, duration=5000)
                    else:
                        imported_count = int(response.get("imported"))
                        skipped_count += int(response.get("skipped"))
                        InfoBar.success(title="导入成功", content=f"导入了 {imported_count} 条, 忽略了 {skipped_count} 条, 被忽略的条目为: {skipped_row}", parent=self, duration=5000)
                        self.current_page = 1
                        self.load_data()
                        self.populate_table()
        except Exception as e:
            InfoBar.error(title="操作失败", content=str(e), parent=self, duration=5000)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InventoryInterface()
    window.show()
    sys.exit(app.exec())
