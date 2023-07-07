import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JPEG Converter')
        self.resize(600, 400)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.button = QPushButton("Open Image", self)
        self.button.clicked.connect(self.open_image)
        layout.addWidget(self.button)

    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_name:
            pixmap = QPixmap(file_name)
            image_path = os.path.dirname(file_name)  
            image = pixmap.toImage()  

            
            width, height = image.width(), image.height()
            buffer = image.bits().asstring(width * height * 4)  
            np_array = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))

        
            reversed_array = np_array[::-1, ::-1, :]

        
            reversed_image = QPixmap.fromImage(QImage(reversed_array.data.tobytes(), width, height, QImage.Format_RGBA8888))

            
            reversed_image.save(os.path.join(image_path, 'reversed_' + os.path.basename(file_name)))

            self.label.setPixmap(reversed_image.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

