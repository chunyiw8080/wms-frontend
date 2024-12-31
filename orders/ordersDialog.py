import datetime

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, ComboBox, StrongBodyLabel, InfoBar
from utils.db_utils import load_categories, load_providers, load_projects
from utils.functional_utils import convert_date_to_chinese
from config import URL
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker


class BaseOrderDialog(MessageBoxBase):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.add_update_data_mapping = {
            '入库': "inbound",
            '出库': "outbound",
            "待处理": "waiting",
            "已完成": "pass",
            "被取消": "reject"
        }
        self.setup_ui()

    def setup_ui(self):
        self.titleLabel = SubtitleLabel(self.title, self)
        self.viewLayout.addWidget(self.titleLabel)

        self.grid_layout = QGridLayout()
        self.viewLayout.addLayout(self.grid_layout)

        self.order_id_input = LineEdit(self)
        self.order_id_input.setFixedWidth(200)
        self.order_type_combo = ComboBox(self)
        self.order_type_combo.addItems(['', '出库', '入库'])
        self.cargo_name_input = LineEdit(self)
        self.model_input = LineEdit(self)
        self.price_input = LineEdit(self)
        self.count_input = LineEdit(self)
        self.provider_combo = ComboBox(self)
        self.provider_combo.addItem('')
        self.provider_combo.addItems(load_providers() if load_projects() is not None else [])
        self.project_combo = ComboBox(self)
        self.project_combo.addItem('')
        self.project_combo.addItems(load_projects() if load_projects() is not None else [])
        self.status_combo = ComboBox(self)
        self.status_combo.addItems(['', '待处理', '已完成', '被取消'])
        self.employee_input = LineEdit(self)
        self.published_input = LineEdit(self)
        self.published_input.setDisabled(True)
        self.processed_input = LineEdit(self)
        self.processed_input.setDisabled(True)
        self.processed_input.setFixedWidth(200)

        fields = [
            ("单号: ", self.order_id_input),
            ("类型: ", self.order_type_combo),
            ("货品名称: ", self.cargo_name_input),
            ("型号: ", self.model_input),
            ("单价: ", self.price_input),
            ("数量: ", self.count_input),
            ("供应商: ", self.provider_combo),
            ("归属项目: ", self.project_combo),
            ("状态: ", self.status_combo),
            ("经办人: ", self.employee_input),
            ("订单创建日期: ", self.published_input),
            ("订单审批日期: ", self.processed_input)
        ]
        self.load_widgets(fields)

        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

    def load_widgets(self, fields):
        for i, (label_text, widget) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            label = StrongBodyLabel(label_text, self)
            self.grid_layout.addWidget(label, row, col)
            self.grid_layout.addWidget(widget, row, col + 1)

            # 设置列的拉伸比例
        self.grid_layout.setColumnStretch(1, 1)  # 第一对标签和控件
        self.grid_layout.setColumnStretch(3, 1)  # 第二对标签和控件

    def _validate_input(self):
        errors = []
        if self.order_type_combo.currentIndex() == 0:
            errors.append(f'订单类型不能为空;')
        if not self.cargo_name_input or not self.model_input:
            errors.append(f'货品名称和型号不能为空;')
        if not self.price_input or not self.count_input:
            errors.append(f'单价和数量不能为空;')
        if self.provider_combo.currentIndex() == 0 and self.project_combo.currentIndex() == 0:
            errors.append(f'至少填写供应商和归属项目中的一个;')
        if self.status_combo.currentIndex() == 0:
            errors.append(f'订单状态不能为空;')
        if not self.employee_input:
            errors.append(f'经办人不能为空;')
        return errors

    def accept(self):
        errors = self._validate_input()
        if errors:
            error_message = "\n".join(errors)
            InfoBar.error(
                title='输入错误',
                content=error_message,
                parent=self,
                duration=5000
            )
            return
        else:
            super().accept()

    def get_order_info(self):
        order_info = {
            "order_id": self.order_id_input.text(),
            "order_type": self.add_update_data_mapping[self.order_type_combo.currentText()],
            "cargo_name": self.cargo_name_input.text(),
            "model": self.model_input.text(),
            "price": self.price_input.text(),
            "count": self.count_input.text(),
            "provider": self.provider_combo.currentText(),
            "project": self.project_combo.currentText(),
            "status": self.add_update_data_mapping[self.status_combo.currentText()],
            "employee_name": self.employee_input.text(),
            "published_at": self.published_input.text(),
            "processed_at": self.processed_input.text(),
        }
        return order_info


class AddOrderDialog(BaseOrderDialog):
    def __init__(self, parent=None):
        super().__init__('创建订单', parent)
        try:
            # formatted_date = formatdate(timeval=time(), localtime=False, usegmt=True)
            # self.published_input.setText(formatted_date)
            self.order_id_input.setText('系统自动设置')
            self.order_id_input.setDisabled(True)
            current_date = datetime.date.today().strftime('%Y-%m-%d')
            self.published_input.setText(current_date)
            self.published_input.setDisabled(True)
            self.yesButton.setText('添加')
        except Exception as e:
            print(e)


class UpdateOrderDialog(BaseOrderDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(f'编辑订单 - {order_id}', parent)
        self.order_id = order_id
        self.yesButton.setText('确定')
        self.data_mapping = {
            'pass': '已完成',
            'waiting': '待处理',
            'reject': '被取消',
            'inbound': '入库',
            'outbound': '出库'
        }
        self.set_order_info()

    def set_order_info(self):
        try:
            url = URL + f'/orders/{self.order_id}'
            # response = APIClient.get_request(url)
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            if response['success'] is True:
                data = response['data']
                # print(data)
                if data['status'] == 'pass' or data['status'] == 'reject':
                    self.order_id_input.setText(data['order_id'])
                    self.order_id_input.setDisabled(True)
                    self.order_type_combo.setCurrentText(self.data_mapping[data['order_type']])
                    self.order_type_combo.setDisabled(True)
                    self.cargo_name_input.setText(data['cargo_name'])
                    self.cargo_name_input.setDisabled(True)
                    self.model_input.setText(data['model'])
                    self.model_input.setDisabled(True)
                    self.price_input.setText(data['price'])
                    self.price_input.setDisabled(True)
                    self.count_input.setText(str(data['count']))
                    self.count_input.setDisabled(True)
                    self.provider_combo.setCurrentText(data['provider'])
                    self.provider_combo.setDisabled(True)
                    self.project_combo.setCurrentText(data['project'])
                    self.project_combo.setDisabled(True)
                    self.status_combo.setCurrentText(self.data_mapping[data['status']])
                    self.status_combo.setDisabled(True)
                    self.employee_input.setText(data['employee_name'])
                    self.employee_input.setDisabled(True)
                    self.published_input.setText(convert_date_to_chinese(data['published_at']))
                    self.published_input.setDisabled(True)
                    self.processed_input.setText(convert_date_to_chinese(data['processed_at']))
                    self.processed_input.setDisabled(True)
                else:
                    self.order_id_input.setText(data['order_id'])
                    self.order_id_input.setDisabled(True)
                    self.order_id_input.setDisabled(True)
                    self.order_type_combo.setCurrentText(self.data_mapping[data['order_type']])
                    self.cargo_name_input.setText(data['cargo_name'])
                    self.model_input.setText(data['model'])
                    self.price_input.setText(data['price'])
                    self.count_input.setText(str(data['count']))
                    self.provider_combo.setCurrentText(data['provider'])
                    self.project_combo.setCurrentText(data['project'])
                    self.status_combo.setCurrentText(self.data_mapping[data['status']])
                    self.employee_input.setText(data['employee_name'])
                    self.published_input.setText(convert_date_to_chinese(data['published_at']))
                    self.published_input.setDisabled(True)
                    self.processed_input.setText('')
                    self.processed_input.setDisabled(True)
        except Exception as e:
            InfoBar.error(title='系统异常', content=str(e), parent=self, duration=5000)
