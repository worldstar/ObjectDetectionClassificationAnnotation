import sys
import os
import zipfile
import numpy as np
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QRadioButton, QButtonGroup, QFileDialog, QMessageBox, QWidget, QStackedWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageLabelingApp(QMainWindow):
    def __init__(self):
        # 初始化
        super().__init__()

        self.setWindowTitle('Image Labeling App')

        # 同一時間僅顯示單一視窗
        self.stackedWidget = QStackedWidget()
        # 視窗顯示在中央
        self.setCentralWidget(self.stackedWidget)

        # 設立五個視窗
        self.page1 = QWidget()
        self.page2 = QWidget()
        self.page3 = QWidget()
        self.page4 = QWidget()
        self.page5 = QWidget()

        # 五個頁面添加到 QStackedWidget
        self.stackedWidget.addWidget(self.page1)
        self.stackedWidget.addWidget(self.page2)
        self.stackedWidget.addWidget(self.page3)
        self.stackedWidget.addWidget(self.page4)
        self.stackedWidget.addWidget(self.page5)

        # 初始化
        self.initPage1()
        self.initPage2()
        self.initPage3()
        self.initPage4()
        self.initPage5()

        # 追蹤當前圖片ID
        self.current_img_id = 0

    def initPage1(self):
        # 垂直布局
        layout = QVBoxLayout()

        # 增加提示文字
        self.label1 = QLabel('Welcome to the Image Labeling App\n\nInstructions:\n1. Load the dataset on the next page.\n2. Enter the classes for image classification.\n3. Review the classes and check for a backup of the label directory.\n4. Annotate images and save your changes.', self.page1)
        layout.addWidget(self.label1)

        # 創建 NEXT 按鈕
        self.next_button1 = QPushButton('Next', self.page1)
        self.next_button1.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page2))
        layout.addWidget(self.next_button1)

        # 將上面內容設為頁面1
        self.page1.setLayout(layout)

    def initPage2(self):
        layout = QVBoxLayout()

        self.label2 = QLabel('Load Dataset', self.page2)
        layout.addWidget(self.label2)

        self.load_button = QPushButton('Load Dataset', self.page2)
        self.load_button.clicked.connect(self.load_dataset)
        layout.addWidget(self.load_button)

        self.next_button2 = QPushButton('Next', self.page2)
        # 將初始狀態設為不可用
        self.next_button2.setEnabled(False)
        self.next_button2.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page3))
        layout.addWidget(self.next_button2)

        self.page2.setLayout(layout)

    def initPage3(self):
        layout = QVBoxLayout()

        self.label3 = QLabel('Enter Image Classes (one per line)', self.page3)
        layout.addWidget(self.label3)

        self.class_input = QLineEdit(self.page3)
        layout.addWidget(self.class_input)

        self.add_class_button = QPushButton('Add Class', self.page3)
        self.add_class_button.clicked.connect(self.add_class)
        layout.addWidget(self.add_class_button)

        self.class_list_label = QLabel('Classes:', self.page3)
        layout.addWidget(self.class_list_label)

        self.next_button3 = QPushButton('Next', self.page3)
        self.next_button3.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page4))
        layout.addWidget(self.next_button3)

        self.page3.setLayout(layout)

    def initPage4(self):
        layout = QVBoxLayout()

        self.label4 = QLabel('Review and Confirm Classes', self.page4)
        layout.addWidget(self.label4)

        self.dataset_info_label = QLabel('', self.page4)
        layout.addWidget(self.dataset_info_label)

        self.confirm_classes_label = QLabel('', self.page4)
        layout.addWidget(self.confirm_classes_label)

        self.next_button4 = QPushButton('Next', self.page4)
        self.next_button4.clicked.connect(self.show_page5_with_pictureid0)
        layout.addWidget(self.next_button4)

        self.page4.setLayout(layout)

    def initPage5(self):
        layout = QVBoxLayout()

        self.label5 = QLabel('Label Conversion: \n To show images, click on the prev/next image buttons.', self.page5)
        layout.addWidget(self.label5)

        self.image_label = QLabel(self.page5)
        layout.addWidget(self.image_label)
        
        self.image_id_label = QLabel('Image ID: ', self.page5)
        layout.addWidget(self.image_id_label)

        self.filename_label = QLabel('Filename: ', self.page5)
        layout.addWidget(self.filename_label)
        
        self.txt_label = QLabel('TXT Content: ', self.page5)
        layout.addWidget(self.txt_label)
        
        # 做垂直排列
        self.radio_buttons_layout = QVBoxLayout()
        # 確保同一時間只有一個按鈕被選中
        self.radio_button_group = QButtonGroup()

        layout.addLayout(self.radio_buttons_layout)
        
        button_layout = QHBoxLayout()

        self.prev_button = QPushButton('Prev image', self.page5)
        self.prev_button.clicked.connect(self.show_previous_image)
        button_layout.addWidget(self.prev_button)

        self.next_button5 = QPushButton('Next image', self.page5)
        self.next_button5.clicked.connect(self.show_next_image)
        button_layout.addWidget(self.next_button5)

        layout.addLayout(button_layout)

        self.page5.setLayout(layout)


    def load_dataset(self):
        dataset_dir = QFileDialog.getExistingDirectory(self, 'Select Dataset Folder')
        if dataset_dir:
            self.dataset_dir = dataset_dir
            categories = os.listdir(dataset_dir)
            for category in categories:
                if category == 'images':
                    self.images_dir = os.path.join(dataset_dir, category)
                elif category == 'labels' :
                    self.label_dir = os.path.join(dataset_dir, category)
                elif category == 'labelTxt':
                    self.label_dir = os.path.join(dataset_dir, category)
                else:
                    pass

            # 計算圖片數量
            self.image_count = len(os.listdir(self.images_dir))
            # 根據圖片數量創建相同數量的"未開啟過"
            self.has_ever_opened = [False] * self.image_count
            self.next_button2.setEnabled(True)
            self.dataset_info_label.setText(f'Dataset Directory: {self.dataset_dir}\nImage Directory: {self.images_dir}\nLabel Directory: {self.label_dir}')
            QMessageBox.information(self, 'Success', 'Dataset loaded successfully.')

    def add_class(self):
        class_name = self.class_input.text().strip()
        if class_name:
            if not hasattr(self, 'image_classes'):
                self.image_classes = []
            self.image_classes.append(class_name)
            self.class_input.clear()
            self.class_list_label.setText('Classes: ' + ', '.join(self.image_classes))
            self.confirm_classes_label.setText('Classes: ' + ', '.join(self.image_classes))
            if self.image_classes:
                self.next_button3.setEnabled(True)

    def displayImageAndLabel(self, img_id):
        try:
            # 將目錄中所有的圖片與標籤放入image_files, label_files
            image_files = os.listdir(self.images_dir)
            label_files = os.listdir(self.label_dir)

            # Ensure img_id is within bounds
            if img_id >= len(image_files) or img_id < 0:
                raise IndexError("Image ID is out of bounds")

            # 根據圖片ID選取該圖片
            self.tempfilename = image_files[img_id]
            img_path = os.path.join(self.images_dir, self.tempfilename)
            label_filename = self.tempfilename.rsplit('.', 1)[0] + '.txt'
            label_path = os.path.join(self.label_dir, label_filename)

            # Try loading and displaying the image
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                raise FileNotFoundError(f"Image file not found or could not be loaded: {img_path}")
            
            self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))

            # Display image ID
            self.image_id_label.setText(f'Image ID: {img_id}')
            # Display filename
            self.filename_label.setText(f'Filename: {self.tempfilename}')

            # Try reading and displaying the label
            if not os.path.exists(label_path):
                raise FileNotFoundError(f"Label file does not exist: {label_path}")

            # 讀取並從開頭開始寫入
            with open(label_path, 'r+') as file:
                label_lines = file.readlines()
                
                # 沒有標記內容則引發錯誤訊息
                if not label_lines:
                    one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
                    last_line = " ".join(map(str, one_hot_vector.astype(int)))
                    self.txt_label.setText(f'TXT Content: ')
                    # raise ValueError(f"Label file is empty: {label_path}")

                else:
                    # 如果未打開過則擷取第一行判斷格式
                    # if not self.has_ever_opened[img_id]:
                    #     check_format_line =  label_lines[0].strip()
                    #     self.processLabelLine(check_format_line)
                        
                    # strip是刪除小括弧內文字
                    last_line = label_lines[-1].strip()

                    # 如果最後一行有one_hot則輸出，沒有則生成全0向量去製作單選按鈕
                    if last_line.count('0') == (len(last_line) - 1)/2:
                        self.txt_label.setText(f'TXT Content: {last_line}')
                    else:
                        one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
                        last_line = " ".join(map(str, one_hot_vector.astype(int)))
                        self.txt_label.setText(f'TXT Content: ')
                self.updateRadioButtons(last_line)

                self.has_ever_opened[img_id] = True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image or label: {str(e)}") #跳出錯誤訊息
            self.image_label.clear()  # Clear the image label if there was an error
            self.image_id_label.setText('Image ID: Error')
            self.filename_label.setText('Filename: Error')
            self.txt_label.setText('TXT Content: Error')

    def show_page5_with_pictureid0(self):
        self.stackedWidget.setCurrentWidget(self.page5)
        self.displayImageAndLabel(0)

    def is_float(self, string):
        """Checks if a string represents a float."""
        try:
            float(string)
            return True
        except ValueError:
            return False

    def is_int(self, string):
        """Checks if a string represents an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    def check_number_type(self, string):
        """Checks if a string represents a float or an integer."""
        if self.is_float(string):
            if self.is_int(string):
                return "integer"
            else:
                return "float"
        else:
            return "neither"

    def processLabelLine(self, label_line):
        # 將第一行做分割
        parts = label_line.split()
        # 載入圖片時需要一個全0向量製作未選擇單選按鈕
        one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
        one_hot = " ".join(map(str, one_hot_vector.astype(int)))

        # 這邊輸出了 id, 類別, 座標, if format HBB
        # print(self.current_img_id,parts[0],parts[1])

        part1type = self.check_number_type(parts[1])
        # parts[1]類別為字串，part1type類別為浮點數
        # print(len(parts)) #長度為5

        if ((len(parts) == len(self.image_classes) + 1) and (part1type == "integer")):  # Assuming space-separated format with class_str at the end [clbool_0 clbool_1 ... clbool_nk-1 cls_str]
            print('int')
            # one_hot_vector = list(map(int, parts[:-1])) #in this case, it reads a one-hot vector
            # cls_str = parts[-1]
            # self.updateRadioButtons(one_hot)
            
        elif ((len(parts) == 5) and (part1type == "float")): # Yolo-HBB format [cls_int xc yc w h]
            print('HBB')
            # cls_int = int(parts[0])
            # cls_str = self.image_classes[cls_int]
            # one_hot_vector = self.string_to_one_hot([cls_str], self.image_classes)
            # one_hot_vector_str = " ".join(map(str, one_hot_vector[0].astype(int)))
            # # Append the converted one-hot vector to the file
            # label_filename = self.tempfilename.rsplit('.', 1)[0] + '.txt'
            # label_path = os.path.join(self.label_dir, label_filename)
            # with open(label_path, 'a') as file:
            #     file.write(f"\n{one_hot_vector_str}") 
            # self.updateRadioButtons(one_hot)            
            
        elif len(parts) == 10:  # Yolo-OBB format [x1 ... y4 cls_str conf]
            print('OBB')
            # cls_str = parts[-2]
            # one_hot_vector = self.string_to_one_hot([cls_str], self.image_classes)
            # one_hot_vector_str = " ".join(map(str, one_hot_vector[0].astype(int)))
            # # Append the converted one-hot vector to the file
            # label_filename = self.tempfilename.rsplit('.', 1)[0] + '.txt'
            # label_path = os.path.join(self.label_dir, label_filename)
            # with open(label_path, 'a') as file:
            #     file.write(f"\n{one_hot_vector_str}")
            # self.updateRadioButtons(one_hot)        
        else:
            QMessageBox.critical(self, "Error", f"Unrecognised data format") #無法辨別標籤格式

    def show_next_image(self):
        self.save_annotation()
        self.current_img_id = (self.current_img_id + 1) % self.image_count
        self.displayImageAndLabel(self.current_img_id)

    def show_previous_image(self):
        self.save_annotation()
        self.current_img_id = (self.current_img_id - 1) % self.image_count
        self.displayImageAndLabel(self.current_img_id)

    def save_annotation(self):
        # 獲取使用者的單一選擇，未選擇為-1
        selected_id = self.radio_button_group.checkedId()
        # 如果有勾選則把該項改成1
        if selected_id != -1:
            # 建立一個class長度的one_hot向量，並初始為0
            one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
            one_hot_vector[selected_id] = 1
            one_hot_vector_str = " ".join(map(str, one_hot_vector.astype(int)))
            
            # 將tempfilename的文件名稱根據.位置分割成兩份，並只取前面部份加上.txt
            label_filename = self.tempfilename.rsplit('.', 1)[0] + '.txt'
            # label_filename文件存放在self.label_dir目錄之中，並用label_path儲存路徑
            label_path = os.path.join(self.label_dir, label_filename)
            # 'r+'開啟讀寫模式
            with open(label_path, 'r+') as file:
                # 讀取所有行
                lines = file.readlines()
                if not lines:
                    lines.append(f"{one_hot_vector_str}")
                else:
                    last_line = lines[-1].strip()
                    # 如果最後一行的文字長度等於類別數量
                    if last_line.count('0') == (len(last_line) - 1)/2:
                        # 複寫不用換行
                        lines[-1] = f"{one_hot_vector_str}"
                    else:
                        lines.append(f"\n{one_hot_vector_str}")
                # 將讀寫頭放回開頭
                file.seek(0)
                # 複寫新文字
                file.writelines(lines)


    def string_to_one_hot(self, labels, classes):
        one_hot = np.zeros((len(labels), len(classes)))
        for i, label in enumerate(labels):
            one_hot[i, classes.index(label)] = 1
        return one_hot

    def updateRadioButtons(self ,one_hot_str):
        # 刪除舊有的單選按鈕
        for i in reversed(range(self.radio_buttons_layout.count())):
            widget = self.radio_buttons_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.radio_button_group = QButtonGroup()
        one_hot_vector = list(map(int, one_hot_str.split()))

        #根據one_hot建立對應的單選按鈕 
        for idx, (cls, value) in enumerate(zip(self.image_classes, one_hot_vector)):
            radio_btn = QRadioButton(cls)
            if value == 1:
                radio_btn.setChecked(True)
            self.radio_button_group.addButton(radio_btn, idx)
            self.radio_buttons_layout.addWidget(radio_btn)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            'Confirm Close',
            'Are you sure you want to close the APP?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.save_annotation()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageLabelingApp()
    window.show()
    sys.exit(app.exec_())
