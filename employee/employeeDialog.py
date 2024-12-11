from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import MessageBoxBase, LineEdit, ComboBox, StrongBodyLabel, SubtitleLabel, InfoBar
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker
from config import URL

class BaseEmployeeDialog(MessageBoxBase):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.titleLabel = SubtitleLabel(self.title, self)
        self.viewLayout.addWidget(self.titleLabel)

        grid_layout = QGridLayout()
        self.viewLayout.addLayout(grid_layout)

        self.employee_name_input = LineEdit(self)
        self.gender_combo = ComboBox(self)
        self.gender_combo.addItems(['男', '女'])

        self.position_input = LineEdit(self)

        fields = [
            ("姓名: ", self.employee_name_input),
            ("性别: ", self.gender_combo),
            ("职务: ", self.position_input)
        ]
        for row, (label_text, widget) in enumerate(fields):
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
        for widget in [self.employee_name_input, self.gender_combo, self.position_input]:
            widget.setMinimumWidth(200)

    def get_employee_info(self):
        employee_info = {
            "employee_name": self.employee_name_input.text().strip(),
            "gender": self.gender_combo.currentText(),
            "position": self.position_input.text().strip()
        }
        return employee_info

    def _validate_employee_info(self):
        errors = []
        if not self.employee_name_input.text().strip():
            errors.append("员工姓名不能为空")
        if not self.position_input.text().strip():
            errors.append("员工职务不能为空")

        return errors

    def accept(self):
        errors = self._validate_employee_info()
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

class AddEmployeeDialog(BaseEmployeeDialog):
    def __init__(self, parent=None):
        super().__init__('添加员工', parent)
        self.yesButton.setText('添加')

class UpdateEmployeeDialog(BaseEmployeeDialog):
    def __init__(self, employee_id, parent=None):
        super().__init__('编辑库存信息', parent)
        self.employee_id = employee_id
        self.yesButton.setText('修改')
        self.set_employee_info()

    def set_employee_info(self):
        url = URL + f'/employees/{self.employee_id}'
        # response = APIClient.get_request(url)
        response = Worker.unpack_thread_queue(APIClient.get_request, url)
        if response['success'] is True:
            data = response['data']
            self.employee_name_input.setText(data['employee_name'])
            self.gender_combo.setCurrentText(data['gender'])
            self.position_input.setText(data['position'])
        else:
            InfoBar.error(
                title='加载失败',
                content=response['message'],
                parent=self,
                duration=5000
            )