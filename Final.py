import sys
import os
import numpy as np
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage


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
            quality, ok = QInputDialog.getInt(self, "JPEG Compression", "Compression Quality (1 to 100):", 50, 1, 100)
            if ok:
                image = cv2.imread(self.image_path)

                # Convert BGR to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Apply JPEG compression
                compressed_image = jpeg_compress(image_rgb, quality)

                # Convert RGB to QImage
                compressed_qimage = QImage(compressed_image.data, compressed_image.shape[1],
                                           compressed_image.shape[0], QImage.Format_RGB888)

                # Save the compressed image in the same directory with a 'compressed_' prefix
                image_dir, image_name = os.path.split(self.image_path)
                compressed_image_path = os.path.join(image_dir, 'compressed_' + image_name.split('.')[0]+'.jpeg')
                compressed_qimage.save(compressed_image_path)

                # Display the compressed image
                pixmap = QPixmap.fromImage(compressed_qimage)
                self.label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
                self.label.setText("Image compressed and saved as 'compressed_image.jpg'.")


def jpeg_compress(image, quality=50):
    height, width, _ = image.shape

    # Calculate the number of 8x8 blocks in the image
    num_blocks_y = int(np.ceil(height / 8))
    num_blocks_x = int(np.ceil(width / 8))

    # Create an empty array to store the compressed image
    compressed_image = np.zeros_like(image)

    # Color Space Transformation (RGB to YCbCr)
    ycbcr_image = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)

    for block_y in range(num_blocks_y):
        for block_x in range(num_blocks_x):
            # Extract the 8x8 block from the Y channel
            y_block = ycbcr_image[block_y*8:(block_y+1)*8, block_x*8:(block_x+1)*8, 0]

            # Applying Discrete Cosine Transform (DCT) to the Y block
            y_dct = cv2.dct(np.float32(y_block) - 128)

            # Quantization
            quantization_table = create_quantization_table(quality)
            y_quantized = np.round(y_dct / quantization_table) * quantization_table

            # Applying Inverse Discrete Cosine Transform (IDCT) to obtain the compressed Y block
            y_compressed = cv2.idct(y_quantized) + 128

            # Place the compressed Y block into the compressed image
            compressed_image[block_y*8:(block_y+1)*8, block_x*8:(block_x+1)*8, 0] = y_compressed

    # Splitting into Cb and Cr components
    cb, cr = cv2.split(ycbcr_image[:, :, 1:])

    # Downsampling the chrominance components (Cb and Cr)
    cb_downsampled = cv2.resize(cb, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR)
    cr_downsampled = cv2.resize(cr, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR)

    # Resize the chrominance components to match the dimensions of the original image
    cb_downsampled = cv2.resize(cb_downsampled, (width, height), interpolation=cv2.INTER_LINEAR)
    cr_downsampled = cv2.resize(cr_downsampled, (width, height), interpolation=cv2.INTER_LINEAR)

    # Combining the compressed Y, downsampled Cb, and downsampled Cr components into a single image
    compressed_image[:, :, 1] = cb_downsampled
    compressed_image[:, :, 2] = cr_downsampled

    # Color Space Transformation (YCbCr to RGB)
    compressed_image_rgb = cv2.cvtColor(compressed_image, cv2.COLOR_YCrCb2RGB)

    return compressed_image_rgb


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

