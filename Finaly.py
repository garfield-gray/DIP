import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('My PyQt5 App')
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
            quality, ok = QInputDialog.getInt(self, "JPEG Compression", "Compression Quality (1 to 100):", 50, 1, 100)
            if ok:
                image = plt.imread(self.image_path)

                # Apply JPEG compression
                compressed_image = jpeg_compress(image, quality)

                # Save the compressed image in the same directory with a 'compressed_' prefix and '.jpg' extension
                image_dir, image_name = os.path.split(self.image_path)
                compressed_image_path = os.path.join(image_dir, 'compressed_' + image_name.split('.')[0] + '.jpg')
                plt.imsave(compressed_image_path, compressed_image)

                # Display the compressed image
                pixmap = QPixmap(compressed_image_path)
                self.label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
                self.label.setText("Image compressed and saved as 'compressed_image.jpg'.")


def jpeg_compress(image, quality=50):
    # Convert image to YCbCr color space
    ycbcr_image = rgb_to_ycbcr(image)

    # Splitting into Y, Cb, and Cr components
    y, cb, cr = ycbcr_image[:, :, 0], ycbcr_image[:, :, 1], ycbcr_image[:, :, 2]

    # Apply JPEG compression to Y channel
    y_quantized = jpeg_compress_channel(y, quality)

    # Convert Y, Cb, and Cr channels back to the range of 0 to 255
    y_quantized = np.clip(y_quantized, 0, 255).astype(np.uint8)
    cb = np.clip(cb, 0, 255).astype(np.uint8)
    cr = np.clip(cr, 0, 255).astype(np.uint8)

    # Combine compressed Y channel with Cb and Cr channels
    compressed_image = np.dstack((y_quantized, cb, cr))

    # Convert image back to RGB color space
    compressed_image_rgb = ycbcr_to_rgb(compressed_image)

    return compressed_image_rgb



def jpeg_compress_channel(channel, quality):
    # Split the channel into 8x8 blocks
    height, width = channel.shape
    blocks = []
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            block = channel[y:y+8, x:x+8]
            blocks.append(block)

    # Apply quantization table to each block
    quantization_table = create_quantization_table(quality)
    channel_quantized = np.zeros_like(channel)
    idx = 0
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            block = blocks[idx]
            quantized_block = np.round(block / quantization_table) * quantization_table
            channel_quantized[y:y+8, x:x+8] = quantized_block
            idx += 1

    return channel_quantized


def create_quantization_table(quality):
    # Quality factor scaling matrix
    if quality < 50:
        quality_scale = 5000 / quality
    else:
        quality_scale = 200 - 2 * quality

    # Creating the quantization table
    quantization_table = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]
    ])

    # Scaling the quantization table based on the quality factor
    quantization_table = np.round((quantization_table * quality_scale + 50) / 100)

    # Limiting the values of the quantization table to a maximum of 255 and a minimum of 1
    quantization_table[quantization_table > 255] = 255
    quantization_table[quantization_table < 1] = 1

    return quantization_table


def rgb_to_ycbcr(image):
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]

    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
    cr = 0.5 * r - 0.4187 * g - 0.0813 * b + 128

    ycbcr_image = np.dstack((y, cb, cr))

    return ycbcr_image
def ycbcr_to_rgb(ycbcr_image):
    ycbcr_image = ycbcr_image.astype(np.uint8)
    rgb_image = cv2.cvtColor(ycbcr_image, cv2.COLOR_YCrCb2RGB)

    return rgb_image


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

