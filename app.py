import sys

from PyQt6.QtWidgets import QApplication

from windows.main import MainApp

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show_login()
    sys.exit(app.exec())