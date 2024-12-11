from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, StrongBodyLabel
from config import URL
from backendRequests.jsonRequests import APIClient
from utils.worker import Worker

class BaseProviderDialog(MessageBoxBase):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.titleLabel = SubtitleLabel(self.title, self)
        self.viewLayout.addWidget(self.titleLabel)

        grid_layout = QGridLayout()
        self.viewLayout.addLayout(grid_layout)

        self.provider_name_label = StrongBodyLabel('项目名称: ', self)
        self.provider_name_input = LineEdit(self)
        self.provider_name_input.setFixedWidth(200)

        grid_layout.addWidget(self.provider_name_label)
        grid_layout.addWidget(self.provider_name_input)

        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

        self.provider_name_input.setFocus()


class AddProviderDialog(BaseProviderDialog):
    def __init__(self, parent=None):
        super().__init__('添加供应商', parent)
        self.yesButton.setText('添加')

    def get_provider_info(self):
        return self.provider_name_input.text().strip()


class UpdateProviderDialog(BaseProviderDialog):
    def __init__(self, provider_name, parent=None):
        super().__init__('编辑供应商', parent)
        self.provider_name = provider_name
        self.yesButton.setText('修改')
        self.set_provider_info()

    def set_provider_info(self):
        url = URL + f'/providers/search?name={self.provider_name}'
        # response = APIClient.get_request(url)
        response = Worker.unpack_thread_queue(APIClient.get_request, url)
        # print(response)
        if response.get('success') is True:
            data = response['data']
            # print(data[0].get('provider_name'))
            self.provider_name_input.setText(data[0].get('provider_name'))

    def get_provider_info(self):
        return {
            'provider_name': self.provider_name_input.text()
        }



