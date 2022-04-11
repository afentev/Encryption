import sys
from lib import cypher

from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QTextEdit, QComboBox, QLabel, QLineEdit,\
    QMessageBox
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QTextCursor, QRegExpValidator


disabled_style = """QLineEdit:disabled {
background-color:#D8D8D8;
}"""


class QTextEditWrapper(QTextEdit):
    """
    This class is a wrapper for QTextEdit; it behaves like _io.TextIOWrapper
    """
    def __init__(self):
        super().__init__()

    def write(self, *args):
        self.append(*args)

    def flush(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 1)
        self.setTextCursor(cursor)

    def read(self):
        return self.toPlainText()

    def seek(self, pos: int):
        pass

    def close(self):
        pass


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cypher = cypher.Cypher(self.input, self.output)
        self.cypher.load('Caesar', 1, "", (0, 0))

    def initUI(self):
        self.setWindowTitle("Cypher GUI")
        self.resize(800, 500)
        self.input = QTextEditWrapper()
        self.input.setAcceptRichText(False)
        self.output = QTextEditWrapper()
        self.options = QComboBox()
        self.options.addItem('Caesar')
        self.options.addItem('Vernam')
        self.options.addItem('RSA')
        self.options.currentIndexChanged.connect(self.change_mode)
        self.modeLabel = QLabel()
        self.modeLabel.setText("Encryption mode: ")

        self.caesarLabel = QLabel("Offset for Caesar:")
        self.vernamLabel = QLabel("Key for Vernam:")
        self.pubExpLabel = QLabel("Public exponent for RSA:")
        self.privExpLabel = QLabel("Private exponent for RSA:")
        self.productLabel = QLabel("Product (modulo) for RSA:")

        self.caesarData = QLineEdit()
        self.vernamData = QLineEdit()
        self.pubExpData = QLineEdit()
        self.privExpData = QLineEdit()
        self.productData = QLineEdit()

        self.caesarData.setValidator(QRegExpValidator(QRegExp(r"\d+")))
        self.vernamData.setValidator(QRegExpValidator(QRegExp(r"[a-zA-Z]+")))
        self.pubExpData.setValidator(QRegExpValidator(QRegExp(r"\d+")))
        self.privExpData.setValidator(QRegExpValidator(QRegExp(r"\d+")))
        self.productData.setValidator(QRegExpValidator(QRegExp(r"\d+")))

        self.caesarData.setStyleSheet(disabled_style)
        self.vernamData.setStyleSheet(disabled_style)
        self.pubExpData.setStyleSheet(disabled_style)
        self.privExpData.setStyleSheet(disabled_style)
        self.productData.setStyleSheet(disabled_style)

        self.pubExpData.textChanged.connect(self.disable_private)
        self.privExpData.textChanged.connect(self.disable_public)
        self.action = QPushButton("Encrypt/Decrypt")
        self.action.clicked.connect(self.transform)

        self.vernamData.setEnabled(False)
        self.pubExpData.setEnabled(False)
        self.privExpData.setEnabled(False)
        self.productData.setEnabled(False)

        self.crack = QPushButton("Crack Caesar")
        self.crack.clicked.connect(self.do_crack)

        layout = QGridLayout()

        self.output.setReadOnly(True)
        layout.addWidget(self.modeLabel, 0, 0)
        layout.addWidget(self.options, 0, 1)

        layout.addWidget(self.input, 1, 0)
        layout.addWidget(self.output, 1, 1)

        layout.addWidget(self.caesarLabel, 2, 0)
        layout.addWidget(self.caesarData, 2, 1)

        layout.addWidget(self.vernamLabel, 3, 0)
        layout.addWidget(self.vernamData, 3, 1)

        layout.addWidget(self.pubExpLabel, 4, 0)
        layout.addWidget(self.pubExpData, 4, 1)

        layout.addWidget(self.privExpLabel, 5, 0)
        layout.addWidget(self.privExpData, 5, 1)

        layout.addWidget(self.productLabel, 6, 0)
        layout.addWidget(self.productData, 6, 1)

        layout.addWidget(self.action, 7, 0, 1, 2)
        layout.addWidget(self.crack, 8, 0, 1, 2)

        self.setLayout(layout)

    def transform(self):
        self.output.clear()
        method = self.options.currentText()

        error_message = None

        try:
            if method == 'Caesar':
                self.cypher.load('Caesar', int(self.caesarData.text()), "", (0, 0))
            elif method == 'Vernam':
                self.cypher.load('Vernam', 0, self.vernamData.text(), (0, 0))
            else:
                if self.pubExpData.isEnabled():
                    self.cypher.load('RSA', 0, "", (int(self.pubExpData.text()), int(self.productData.text())))
                else:
                    self.cypher.load('RSA', 0, "", (int(self.privExpData.text()), int(self.productData.text())))
                    self.cypher.decrypt()
                    return

            self.cypher.encrypt()
        except ValueError:
            if method == 'Caesar':
                error_message = "Please, provide an offset for Caesar"
            elif method == 'RSA':
                is_encrypting = self.pubExpData.text() and self.productData.text()
                is_decrypting = self.privExpData.text() and self.productData.text()
                if is_encrypting:
                    error_message = "Please, provide a correct RSA-key"
                elif is_decrypting:
                    error_message = "Incorrect input: expected sequence of hexadecimal numbers"
                else:
                    error_message = "Please, provide a key for RSA"
        except ZeroDivisionError:
            error_message = "Please, provide a key for Vernam"
        except OverflowError:
            error_message = "Invalid RSA key"
        except Exception as error:
            error_message = "Unknown error: {TRACEBACK}".format(TRACEBACK=error)

        if error_message is not None:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Unexpected Error")
            msg.setInformativeText(error_message)
            msg.setWindowTitle("Error")
            msg.exec_()

    def do_crack(self):
        self.output.clear()
        self.cypher.crack()

    def change_mode(self, newPos: int):
        if newPos == 0:
            self.crack.setEnabled(True)
            self.caesarData.setEnabled(True)
            self.vernamData.setEnabled(False)
            self.pubExpData.setEnabled(False)
            self.privExpData.setEnabled(False)
            self.productData.setEnabled(False)
        elif newPos == 1:
            self.crack.setEnabled(False)
            self.vernamData.setEnabled(True)
            self.caesarData.setEnabled(False)
            self.pubExpData.setEnabled(False)
            self.privExpData.setEnabled(False)
            self.productData.setEnabled(False)
        else:
            self.crack.setEnabled(False)
            if not self.privExpData.text():
                self.pubExpData.setEnabled(True)
            if not self.pubExpData.text():
                self.privExpData.setEnabled(True)
            self.productData.setEnabled(True)
            self.caesarData.setEnabled(False)
            self.vernamData.setEnabled(False)

    def disable_private(self):
        if self.pubExpData.text():
            self.privExpData.setEnabled(False)
        else:
            self.privExpData.setEnabled(True)

    def disable_public(self):
        if self.privExpData.text():
            self.pubExpData.setEnabled(False)
        else:
            self.pubExpData.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
