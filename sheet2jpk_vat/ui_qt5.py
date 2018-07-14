# -*- coding: utf-8 -*-

try:
	from PyQt5 import QtWidgets as QtGui
	from PyQt5.QtGui import QTextDocument
except ImportError as ex:
	print("The library PyQt5 cannot be imported: {}".format(ex))
	print("Please install PyQt5 package (pip install PyQt5).")
	exit(1)

qt_app = QtGui.QApplication([])


class Cancelled(KeyboardInterrupt):
	pass


def SelectOneOf(title, msg, options):
	value, status = QtGui.QInputDialog.getItem(None, title, msg, options, editable=False)
	if status is False:
		raise Cancelled()
	return value


def MsgBoxCritical(title, msg):
	QtGui.QMessageBox().critical(None, title, msg)


def MsgBoxInfo(title, msg):
	msgbox = QtGui.QMessageBox()
	msgbox.setText(msg)
	msgbox.setWindowTitle(title)
	msgbox.setIcon(QtGui.QMessageBox.Information)
	msgbox.addButton('OK', QtGui.QMessageBox.AcceptRole)
	msgbox.exec_()


def MsgBoxYesNo(title, msg):
	msgbox = QtGui.QMessageBox()
	msgbox.setText(msg)
	msgbox.setWindowTitle(title)
	msgbox.setIcon(QtGui.QMessageBox.Question)
	msgbox.addButton('No', QtGui.QMessageBox.RejectRole)
	btn_yes = msgbox.addButton('Yes', QtGui.QMessageBox.YesRole)
	msgbox.exec_()

	return msgbox.clickedButton() == btn_yes


class ReportDialog(QtGui.QDialog):

	def __init__(self, html, allow_cancel=False, msg="Wiersze błędne:"):
		super(ReportDialog, self).__init__()

		OKButton = QtGui.QPushButton("OK")
		OKButton.setDefault(True)

		buttonBox = QtGui.QDialogButtonBox()
		buttonBox.addButton(OKButton, QtGui.QDialogButtonBox.AcceptRole)
		if allow_cancel:
			buttonBox.addButton(QtGui.QPushButton("Przerwij"), QtGui.QDialogButtonBox.RejectRole)

		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.cancel)

		content = QtGui.QTextEdit()

		grid = QtGui.QGridLayout()

		grid.addWidget(QtGui.QLabel(msg), 0, 0)
		grid.addWidget(content, 1, 0)

		layout = QtGui.QVBoxLayout()
		layout.addLayout(grid)
		layout.addWidget(buttonBox)

		self.setLayout(layout)
		self.setWindowTitle("Weryfikacja")
		self.resize(1000, 800)

		doc = QTextDocument()
		css = """
			table.invoices tr td {
				padding-left: 4px;
				padding-right: 4px;
			}
			table.invoices tr {
				padding-bottom: 5px;
				border: 1px solid #000 !important;
			}
			table.invoices {
				with: 100%;
				border-collapse: collapse;
			}
			table.invoices, table.invoices th, table.invoices td {
				border: 1px solid black;
			}
			table.invoices td.currency {
				text-align: right;
				font-family: monospace;
			}
			ul.errors li {
				color: #E44;
			}
		"""
		doc.setDefaultStyleSheet(css)

		content.setDocument(doc)
		content.setReadOnly(True)
		content.setHtml(html)

		self.status = None

	def cancel(self):
		self.status = False
		self.close()

	def accept(self):
		self.status = True
		self.close()

	def run(self):
		self.exec_()
		return self.status
