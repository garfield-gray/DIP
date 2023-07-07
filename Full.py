import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QPixmap, QImage, QImageWriter


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JPEG Abbas and Faeze')
        self.resize(600, 400)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.button_open = QPushButton("Open Image", self)
        self.button_open.clicked.connect(self.open_image)
        layout.addWidget(self.button_open)

        self.button_compress = QPushButton("Compress Image", self)
        self.button_compress.clicked.connect(self.compress_image)
        layout.addWidget(self.button_compress)

        self.image_path = ""

    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)",
                                                   options=options)
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))

    def compress_image(self):
        if self.image_path:
            compression_rate, ok = QInputDialog.getDouble(self, "JPEG Compression",
                                                          "Compression Rate (0.0 to 1.0):", 0.5, 0.0, 1.0, 2)
            if ok:
                image = QImage(self.image_path)

                # Create a new QImage with reduced quality using JPEG compression
                compressed_image = QImage(image)
                writer = QImageWriter()
                writer.setCompression(1)  # Set JPEG compression
                writer.setQuality(int(compression_rate * 100))  # Set compression quality rate
                writer.setFormat(QByteArray(b"jpg"))  # Set output format as JPEG
                writer.setFileName("compressed_image.jpg")  # Set output file name
                writer.write(compressed_image)

                self.label.setText("Image compressed and saved as 'compressed_image.jpg'.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

