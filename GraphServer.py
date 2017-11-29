
from Ui_main import Ui_MainWindow
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QLineEdit,QFileDialog

class GraphServer(QDialog, Ui_MainWindow):
    
    def __init__(self, parent=None):
           super(GraphServer, self).__init__(parent)
           self.setupUi(self)

if __name__ == "__main__":
     import sys
     from PyQt5.QtWidgets import QApplication
     app = QApplication(sys.argv)
     gs = GraphServer()
     gs.show()
     sys.exit(app.exec_()) 
