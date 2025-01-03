import sys, requests
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, MessageBox,  MSFluentWindow)

from utils.app_logger import get_logger
from inventory.inventoryInterface import InventoryInterface
from orders.ordersInterface import OrdersInterface
from employee.employeeInterface import EmployeeInterface
from project.projectInterface import ProjectInterface
from provider.providerInterface import ProviderInterface
from users.userInterface import UserInterface
from history.historyInterface import HistoryInterface
from operation_logs.logsInterface import LogsInterface
from backendRequests.jsonRequests import APIClient
from utils.token_utils import decode_token
from config import URL
from windows.mypath import *

error_logger = get_logger(logger_name='error_logger', log_file='error.log')

class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.payload = decode_token(APIClient.jwt_token)
        # print(f'management window payload: {self.payload}')
        self.inventoryInterface = InventoryInterface()
        self.ordersInterface = OrdersInterface()
        self.employeeInterface = EmployeeInterface()
        self.projectInterface = ProjectInterface()
        self.providerInterface = ProviderInterface()
        self.userInterface = UserInterface()
        self.historyInterface = HistoryInterface()
        self.logsInterface = LogsInterface()

        self.initNavigation()
        self.initWindow()

    def load_subinterface_icons(self):
        return {
            "inventory_icon": QIcon(warehouse_path),
            "order_icon": QIcon(orders_path),
            "project_icon": QIcon(project_path),
            "provider_icon": QIcon(provider_path),
            "user_icon": QIcon(users_path),
            "employee_icon": QIcon(employee_path),
            "file_icon": QIcon(file_path),
            "logs_icon": QIcon(logs_path),
        }

    def initNavigation(self):
        self.addSubInterface(self.inventoryInterface, self.load_subinterface_icons().get("inventory_icon"), '库存管理')
        self.addSubInterface(self.historyInterface, self.load_subinterface_icons().get('file_icon'), '历史记录')
        self.addSubInterface(self.ordersInterface, self.load_subinterface_icons().get("order_icon"), '出入库管理')
        self.addSubInterface(self.projectInterface, self.load_subinterface_icons().get("project_icon"), '项目管理')
        self.addSubInterface(self.providerInterface, self.load_subinterface_icons().get("provider_icon"), '供应商管理')

        if self.payload.get('permissions') != 'W':
            self.addSubInterface(self.userInterface, self.load_subinterface_icons().get("user_icon"), '用户管理')
            self.addSubInterface(self.employeeInterface, self.load_subinterface_icons().get("employee_icon"), '员工管理')
            self.addSubInterface(self.logsInterface, self.load_subinterface_icons().get("logs_icon"), '操作日志')
            # position=NavigationItemPosition.BOTTOM

    def initWindow(self):
        self.resize(1280, 760)
        self.setWindowIcon(QIcon(logo_path))
        self.setWindowTitle("沈阳市二一三自动化装备有限公司仓库管理系统")

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def closeEvent(self, event):
        if APIClient.jwt_token is not None:
            self.destroy_token()
            APIClient.jwt_token = None

    def destroy_token(self):
        url = URL + '/users/logout'
        headers = {
            "Authorization": f"Bearer {APIClient.jwt_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, timeout=10)
        except Exception as e:
            error_logger.error(f'Management.destroy_token: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()