from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, ComboBox, PasswordLineEdit, StrongBodyLabel, InfoBar
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker
from config import URL

class BaseUserDialog(MessageBoxBase):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.titleLabel = SubtitleLabel(self.title, self)
        self.viewLayout.addWidget(self.titleLabel)

        grid_layout = QGridLayout()
        self.viewLayout.addLayout(grid_layout)

        self.user_id_input = LineEdit(self)
        self.user_id_input.setText('系统自动设置')
        self.user_id_input.setDisabled(True)
        self.username_input = LineEdit(self)
        self.employee_combo = ComboBox(self)
        self.employee_combo.addItem('')
        self.employee_combo.addItems(self.load_employees())
        self.status_combo = ComboBox(self)
        self.status_combo.addItems(['启用', '停用'])
        self.privilege_combo = ComboBox(self)
        self.privilege_combo.addItems(['A', 'B', 'C', 'D'])
        self.password_input = PasswordLineEdit(self)
        self.verify_password_input = PasswordLineEdit(self)

        fields = [
            ('用户id: ', self.user_id_input),
            ('用户名: ', self.username_input),
            ('所属员工: ', self.employee_combo),
            ('账号状态: ', self.status_combo),
            ('账号权限: ', self.privilege_combo),
            ('密码: ', self.password_input),
            ('再次确认密码: ', self.verify_password_input),
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

        for widget in [self.user_id_input, self.username_input, self.employee_combo, self.status_combo, self.privilege_combo, self.password_input, self.verify_password_input]:
            widget.setMinimumWidth(200)

        # 设置光标默认定位到id输入框
        self.username_input.setFocus()

    def load_employees(self):
        url = URL + '/employees/all'
        response = Worker.unpack_thread_queue(APIClient.get_request, url)

        employees = []
        if isinstance(response, (dict, list)):  # 有效 JSON
            if response.get('success') is True:  # 有数据
                data = response.get('data')
                for employee_info in data:
                    employee_name = employee_info.get('employee_name')
                    employees.append(employee_name)
        print(employees)
        return employees

    def _validateInput(self) -> list:
        username = self.username_input.text().strip()
        employee = self.employee_combo.currentText()
        password1 = self.password_input.text().strip()
        password2 = self.verify_password_input.text().strip()

        errors = []

        if username is None:
            errors.append('用户名不能为空;')
        if employee is None:
            errors.append('所属员工不能为空;')
        if password1 != password2:
            errors.append('两次输入的密码不一致;')

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

    def get_user_info(self):
        return {
            "username": self.username_input.text().strip(),
            "employee_name": self.employee_combo.currentText(),
            "status": 1 if self.status_combo.currentText() == '启用' else 0,
            "privilege": self.privilege_combo.currentText(),
            "password": self.password_input.text().strip(),
        }

class AddUserDialog(BaseUserDialog):
    def __init__(self, parent=None):
        super().__init__('新增用户', parent)
        self.yesButton.setText('添加')

class UpdateUserDialog(BaseUserDialog):
    def __init__(self, user_id, parent=None):
        super().__init__('编辑库存信息', parent)
        self.user_id = user_id
        self.yesButton.setText('修改')
        self.set_user_info()
        self.username_input.setDisabled(True)
        self.employee_combo.setDisabled(True)

    def set_user_info(self):
        url = URL + f'/users/{self.user_id}'
        try:
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            if response.get('success') is True:
                user = response.get('user')
                self.user_id_input.setText(user.get('user_id'))
                self.username_input.setText(user.get('username'))
                self.employee_combo.setCurrentText(self._get_employee_name(user.get('employee_id')))
                self.status_combo.setCurrentText('启用' if user.get('status') == 1 else '停用')
                self.privilege_combo.setCurrentText(user.get('privilege'))
                self.password_input.setText(None)
                self.verify_password_input.setText(None)
        except Exception as e:
            print(e)

    def _get_employee_name(self, employee_id):
        url = URL + f'/employees/{employee_id}'
        try:
            response = Worker.unpack_thread_queue(APIClient.get_request, url)
            if response.get('success') is True:
                info = response.get('data')
                employee_name = info.get('employee_name')
                return employee_name
            else:
                return None
        except Exception as e:
            print(e)
            return None
