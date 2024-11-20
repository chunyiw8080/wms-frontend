from decimal import Decimal
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QComboBox, QHBoxLayout
from qfluentwidgets import MessageBoxBase, LineEdit, ComboBox, StrongBodyLabel, SubtitleLabel, EditableComboBox, \
    PushButton, InfoBar
from backendRequests.jsonRequests import get_request
from inventory.db_utils import load_categories

class BaseInventoryDialog(MessageBoxBase):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()


    def setup_ui(self):
        self.titleLabel = SubtitleLabel(self.title, self)
        self.viewLayout.addWidget(self.titleLabel)

        grid_layout = QGridLayout()
        self.viewLayout.addLayout(grid_layout)

        self.cargo_name_input = LineEdit(self)
        self.model_input = LineEdit(self)

        self.category_combo = ComboBox(self)
        self.category_combo.addItem('未分类')
        self.category_combo.addItems(load_categories())

        # self.add_category_btn = PushButton('新建类别', self)

        self.count_input = LineEdit(self)
        self.price_input = LineEdit(self)

        fileds = [
            ("货品名称: ", self.cargo_name_input),
            ("型号: ", self.model_input),
            ("类别: ", self.category_combo),
            ("初始数量: ", self.count_input),
            ("单价: ", self.price_input)
        ]

        for row, (label_text, widget) in enumerate(fileds):
            label = StrongBodyLabel(label_text, self)
            grid_layout.addWidget(label, row, 0) #每行的第一列
            grid_layout.addWidget(widget, row, 1) # 每行的第二列

        # 设置列拉伸
        grid_layout.setColumnStretch(1, 1)
        #设置左对齐
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

        # 设置输入框宽度
        for widget in [self.cargo_name_input, self.model_input, self.category_combo, self.count_input, self.price_input]:
            widget.setMinimumWidth(200)

        # 设置光标默认定位到id输入框
        self.cargo_name_input.setFocus()



    def _validateInput(self) -> list:
        errors = []
        if not self.cargo_name_input.text().strip():
            errors.append("货品名称不能为空;")
        if not self.model_input.text().strip():
            errors.append("型号不能为空;")

        count = self.count_input.text().strip()
        if not count:
            errors.append("数量不能为空;")
        else:
            if self.to_number(count) is None:
                errors.append("数量必须是数字;")
            else:
                if self.to_number(count) < 0:
                    errors.append("数量必须为大于0的整数;")

        if not self.price_input.text().strip():
            errors.append("无效的单价;")
        return errors

    def accept(self):
        errors = self._validateInput()
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

    def get_inventory_info(self) -> dict:
        """获取窗口中用户输入的库存信息"""
        return {
            'cargo_name': self.cargo_name_input.text(),
            'model': self.model_input.text(),
            'categories': self.category_combo.currentText(),
            'count': self.count_input.text(),
            'price': self.price_input.text()
        }

    @staticmethod
    def to_number(value):
        try:
            result = int(value)
            return result
        except ValueError:
            return None

class AddInventoryDialog(BaseInventoryDialog):
    def __init__(self, parent=None):
        super().__init__('新增库存记录', parent)
        self.yesButton.setText('添加')


class UpdateInventoryDialog(BaseInventoryDialog):
    def __init__(self, cargo_id, parent=None):
        super().__init__('编辑库存信息', parent)
        self.cargo_id = cargo_id
        self.yesButton.setText('修改')
        self.set_inventory_info()

    def set_inventory_info(self):
        response = get_request(f"http://127.0.0.1:5000/inventory/{self.cargo_id}")
        if response['success']:
            data = response['inventory']
            self.cargo_name_input.setText(data['cargo_name'])
            self.model_input.setText(data['model'])
            self.category_combo.setCurrentText(data['categories'])
            self.count_input.setText(str(data['count']))
            self.count_input.setReadOnly(True)
            self.price_input.setText(str(data['price']))
            self.price_input.setReadOnly(True)