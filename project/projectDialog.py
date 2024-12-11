from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, StrongBodyLabel
from config import URL
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker

class BaseProjectDialog(MessageBoxBase):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.titleLabel = SubtitleLabel(self.title, self)
        self.viewLayout.addWidget(self.titleLabel)

        grid_layout = QGridLayout()
        self.viewLayout.addLayout(grid_layout)

        self.project_name_label = StrongBodyLabel('项目名称: ', self)
        self.project_name_input = LineEdit(self)
        self.project_name_input.setFixedWidth(200)

        grid_layout.addWidget(self.project_name_label)
        grid_layout.addWidget(self.project_name_input)

        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

        self.project_name_input.setFocus()


class AddProjectDialog(BaseProjectDialog):
    def __init__(self, parent=None):
        super().__init__('添加项目', parent)
        self.yesButton.setText('添加')

    def get_project_info(self):
        return self.project_name_input.text().strip()


class UpdateProjectDialog(BaseProjectDialog):
    def __init__(self, project_name, parent=None):
        super().__init__('编辑项目', parent)
        self.project_name = project_name
        self.yesButton.setText('修改')
        self.set_project_info()

    def set_project_info(self):
        url = URL + f'/project/search?name={self.project_name}'
        # response = APIClient.get_request(url)
        response = Worker.unpack_thread_queue(APIClient.get_request, url)
        if response.get('success') is True:
            data = response['data']
            print(data[0].get('project_name'))
            self.project_name_input.setText(data[0].get('project_name'))

    def get_project_info(self):
        return {
            'project_name': self.project_name_input.text()
        }



