import sys

from PyQt6.QtWidgets import QApplication

from login import LoginWindow
from management import MainWindow


class MainApp:
    def __init__(self):
        self.login_window = LoginWindow()
        self.main_window = None
        self.login_window.login_successful.connect(self.show_main_window)

    def show_main_window(self):
        self.login_window.hide()
        self.main_window = MainWindow()
        self.main_window.show()

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_window.show()
        self.login_window.username_input.clear()
        self.login_window.password_input.clear()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show_login()
    sys.exit(app.exec())
