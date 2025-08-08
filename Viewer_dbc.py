import sys
import cantools
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QAction, QMessageBox, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class GenericDBCViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN DBC Viewer")
        self.setGeometry(100, 100, 1000, 700)

        self.setup_ui()
        self.create_menu()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Element", "Details"])
        self.tree.setColumnWidth(0, 300)
        self.tree.setFont(QFont("Segoe UI", 10))
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setExpandsOnDoubleClick(True)
        layout.addWidget(self.tree)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open DBC", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setIcon(QIcon.fromTheme("document-open"))
        open_action.triggered.connect(self.load_dbc)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setIcon(QIcon.fromTheme("application-exit"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def load_dbc(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open DBC File", "", "DBC Files (*.dbc)")
        if not path:
            return
        try:
            db = cantools.database.load_file(path)
            self.populate_tree(db)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load DBC:\n{str(e)}")

    def populate_tree(self, db):
        self.tree.clear()
        for msg in db.messages:
            msg_id = f"0x{msg.frame_id:X}"
            msg_label = f"{msg.name} ({msg_id})"
            msg_info = f"Length: {msg.length} | Protocol: {msg.protocol or 'N/A'}"

            msg_item = QTreeWidgetItem(["🧭 " + msg_label, msg_info])
            msg_item.setExpanded(True)

            if msg.comment:
                msg_item.addChild(QTreeWidgetItem(["Comment", msg.comment]))
            if msg.senders:
                msg_item.addChild(QTreeWidgetItem(["Senders", ", ".join(msg.senders)]))

            #msg_item.addChild(QTreeWidgetItem(["Is Multiplexed", str(msg.is_multiplexed)]))

            for sig in msg.signals:
                sig_info = (
                    f"Start: {sig.start}, Length: {sig.length}, Signed: {sig.is_signed}, "
                    f"Scale: {sig.scale}, Offset: {sig.offset}, Unit: {sig.unit or ''}"
                )
                sig_item = QTreeWidgetItem([f"📶 {sig.name}", sig_info])
                if sig.choices:
                    for val, desc in sig.choices.items():
                        sig_item.addChild(QTreeWidgetItem([f"↳ {val}", desc]))
                msg_item.addChild(sig_item)

            self.tree.addTopLevelItem(msg_item)
        self.tree.expandAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Optional: Enable dark mode
    # app.setStyleSheet("QTreeWidget { background-color: #2b2b2b; color: #dcdcdc; }")

    viewer = GenericDBCViewer()
    viewer.show()
    sys.exit(app.exec_())
