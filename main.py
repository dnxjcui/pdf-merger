from PyQt6.QtGui import QIcon
from pypdf import PdfWriter, PdfReader, PaperSize
import os
# get an arrow up button, arrow down button
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, \
    QLineEdit, QMessageBox, QToolButton, QFrame, QHBoxLayout
from PyQt6 import QtCore

import sys


def standardize_pdf(paths):
    a4_width = PaperSize.A4[0]
    for path in paths:
        pdf = PdfReader(path)
        writer = PdfWriter()

        for page in pdf.pages:
            scale = page.mediabox[2] / a4_width
            page.scale_to(page.mediabox[2] / scale, page.mediabox[3] / scale)
            writer.add_page(page)

        writer.write(path)
        writer.close()


def merge_pdfs(paths, output, width=PaperSize.A4[0]):
    merger = PdfWriter()
    if not paths:
        raise ValueError("No PDFs to merge, please select something")

    if not output.endswith(".pdf"):
        if '.' in output:
            # throw an error if the output does not end with .pdf
            raise ValueError(f"Output path {output} does not end with .pdf")
        output += ".pdf"

    for path in paths:
        print(path)
        if not os.path.exists(path):
            # throw an error if the path does not exist
            raise FileNotFoundError(f"Path {path} does not exist")
        if not path.endswith(".pdf"):
            # throw an error if the path does not end with .pdf
            raise ValueError(f"PDF path {path} does not end with .pdf")

        pdf = PdfReader(path)

        # automatically scale to width
        for page in pdf.pages:
            scale = page.mediabox[2] / width
            page.scale_to(page.mediabox[2] / scale, page.mediabox[3] / scale)
            merger.add_page(page)

        # merger.append(path)

    merger.write(output)
    merger.close()
    return 0


class PdfMerger(QMainWindow):
    def __init__(self):
        super().__init__()

        # make the window fixed size
        self.setWindowTitle("PDF Merger")
        self.setFixedSize(400, 400)

        # set app icon
        self.setWindowIcon(QIcon("nick.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.pdf_list = QListWidget()
        self.layout.addWidget(self.pdf_list)
        self.pdf_list.currentRowChanged.connect(self.handle_row_change)

        ########### BUTTONS ##############
        self.shift_up_button = QPushButton('\u2191')
        self.shift_down_button = QPushButton('\u2193')

        self.shift_up_button.clicked.connect(lambda: self.shift_pdf(True))
        self.shift_down_button.clicked.connect(lambda: self.shift_pdf(False))

        self.shift_up_button.setEnabled(False)
        self.shift_down_button.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(self.shift_up_button)
        hbox.addWidget(self.shift_down_button)
        self.layout.addLayout(hbox)
        ###################################

        self.add_pdf_button = QPushButton("Add PDF")
        self.add_pdf_button.clicked.connect(self.add_pdf)
        self.layout.addWidget(self.add_pdf_button)

        self.remove_pdf_button = QPushButton("Remove PDF")
        self.remove_pdf_button.clicked.connect(self.remove_pdf)
        self.layout.addWidget(self.remove_pdf_button)

        ############ OUTPUT ############
        hbox = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Output Directory")
        hbox.addWidget(self.output_directory)

        self.output_path = None

        self.select_output_button = QPushButton("Select Output Directory")
        self.select_output_button.clicked.connect(self.select_output)
        hbox.addWidget(self.select_output_button)
        self.layout.addLayout(hbox)

        self.output_file = QLineEdit()
        self.output_file.setPlaceholderText("Output File Name")
        self.layout.addWidget(self.output_file)

        #################################

        self.merge_button = QPushButton("Merge PDFs")
        self.merge_button.clicked.connect(self.merge)

        self.layout.addWidget(self.merge_button)

        # add a warning window that can pop up with custom text
        self.warning_window = QMessageBox()


    def add_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF Files (*.pdf)")
        self.pdf_list.addItem(path)

    def remove_pdf(self):
        selected = self.pdf_list.currentRow()
        if selected != -1:
            self.pdf_list.takeItem(selected)

    # modify this to have the user select an output directory and then manually type in a file name
    def select_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_directory.setText(directory)

    def handle_row_change(self, row):
        if row == 0:
            self.shift_up_button.setEnabled(False)
        else:
            self.shift_up_button.setEnabled(True)

        if row == self.pdf_list.count() - 1:
            self.shift_down_button.setEnabled(False)
        else:
            self.shift_down_button.setEnabled(True)

    def shift_pdf(self, dir: bool):
        # shift pdf up (dir = True) or down (dir = False)
        selected = self.pdf_list.currentRow()
        if selected == -1:
            return

        def swap_items(list_widget, index1, index2):
            if 0 <= index1 < list_widget.count() and 0 <= index2 < list_widget.count():
                item1 = list_widget.item(index1)
                item2 = list_widget.item(index2)

                list_widget.takeItem(index1)
                list_widget.insertItem(index1, item2)
                list_widget.takeItem(index2)
                list_widget.insertItem(index2, item1)

        if dir:
            # swap the above row with the current row

            swap_items(self.pdf_list, selected, selected - 1)
        else:
            # swap the below row with the current row


            swap_items(self.pdf_list, selected, selected + 1)

        # manually change the selected row to the new row
        self.pdf_list.setCurrentRow(selected - (1 if dir else -1))

    def merge(self):
        pdf_paths = [self.pdf_list.item(i).text() for i in range(self.pdf_list.count())]

        paths = [path for path in pdf_paths]

        file_name = self.output_file.text()
        self.output_path = os.path.join(self.output_directory.text(), file_name)

        # print(self.output_path)

        # if self.output_path is not set, then prompt user to set it with a warning window
        if not self.output_path:
            # prompt using warning window
            self.warning_window.setText("Output path not set")
            self.warning_window.show()
            return

        try:
            # standardizing pdf sizes first.
            # standardize_pdf(paths)
            merge_pdfs(paths, self.output_path)
        except Exception as e:
            # use the warning window
            self.warning_window.setText(str(e))
            self.warning_window.show()
            return

        print("Merged PDFs!")


app = QApplication(sys.argv)
window = PdfMerger()
window.show()
sys.exit(app.exec())
