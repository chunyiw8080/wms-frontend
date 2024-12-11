from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QHeaderView
from qfluentwidgets import PushButton, CheckBox


class CustomHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        # 允许点击表头
        self.setSectionsClickable(True)
        # 创建表头CheckBox
        self.checkbox = CheckBox(parent)
        self.checkbox.stateChanged.connect(self.checkAll)

    def paintSection(self, painter, rect, logicalIndex):
        """绘制表头矩形(选择框)"""
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            self.checkbox.setGeometry(rect)
            self.checkbox.setVisible(True)
        else:
            self.checkbox.setVisible(False)

    def checkAll(self, state):
        # 获取表格对象
        table_widget = self.parent()
        for row in range(table_widget.rowCount()):
            checkbox = table_widget.cellWidget(row, 0)
            if checkbox:
                checkbox.setCheckState(Qt.CheckState(state))


def create_btn_widget(callback) -> QWidget:
    # 创建widget容器
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    # 编辑按钮
    edit_btn = PushButton('编辑')
    edit_btn.clicked.connect(callback)

    layout.addWidget(edit_btn)
    return widget

def create_combo_widget(callback) -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    # 编辑按钮
    # operations_combo = ComboBox()
    # operations_combo.addItems(['------', '编辑', '打印单据'])
    # operations_combo.clicked.connect(callback)
    print_btn = PushButton('打印单据')
    print_btn.clicked.connect(callback)

    layout.addWidget(print_btn)
    return widget
