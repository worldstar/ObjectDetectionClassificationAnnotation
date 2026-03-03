import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QRadioButton, QButtonGroup, QFileDialog, QMessageBox, QWidget, QStackedWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
        # 標記模式：'onehot' 或 'truelabel'
        self.label_mode = 'onehot'
        # 是否從 classes.txt 載入過模式（用來鎖定此資料集的模式）
        self.label_mode_locked = False

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
        self.next_button2.clicked.connect(self.go_to_classes_or_review)
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

        # 標記模式選擇
        self.label_mode_label = QLabel('Label Mode:', self.page3)
        layout.addWidget(self.label_mode_label)

        self.label_mode_onehot = QRadioButton('One-hot vector', self.page3)
        self.label_mode_truelabel = QRadioButton('True label (index)', self.page3)
        self.label_mode_group = QButtonGroup(self.page3)
        self.label_mode_group.addButton(self.label_mode_onehot)
        self.label_mode_group.addButton(self.label_mode_truelabel)
        self.label_mode_onehot.setChecked(True)

        layout.addWidget(self.label_mode_onehot)
        layout.addWidget(self.label_mode_truelabel)

        self.class_list_label = QLabel('Classes:', self.page3)
        layout.addWidget(self.class_list_label)

        self.next_button3 = QPushButton('Next', self.page3)
        self.next_button3.setEnabled(False)
        self.next_button3.clicked.connect(self.handle_classes_confirmed)
        layout.addWidget(self.next_button3)

        # **讓 Enter 鍵執行 add_class**
        self.class_input.returnPressed.connect(self.add_class) 

        self.page3.setLayout(layout)

    def go_to_classes_or_review(self):
        # 若已經從檔案或先前步驟載入過 classes，讓使用者選擇是否直接跳過 Page 3
        if hasattr(self, 'image_classes') and self.image_classes:
            reply = QMessageBox.question(
                self,
                'Use Saved Classes',
                'Detected saved classes for this dataset.\nDo you want to reuse them and skip the class input page?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.confirm_classes_label.setText('Classes: ' + ', '.join(self.image_classes))
                self.stackedWidget.setCurrentWidget(self.page4)
                return
            else:
                # 使用者選擇重新輸入，清空舊的 classes
                self.image_classes = []
                self.class_list_label.setText('Classes:')
                self.confirm_classes_label.setText('')
                self.next_button3.setEnabled(False)

        self.stackedWidget.setCurrentWidget(self.page3)

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

        self.filename_label = QLabel('Filename: ', self.page5)
        self.filename_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.filename_label)
        
        self.image_id_label = QLabel('Image ID: ', self.page5)
        layout.addWidget(self.image_id_label)
        
        self.txt_label = QLabel('TXT Content: ', self.page5)
        layout.addWidget(self.txt_label)
        
        self.radio_buttons_layout = QVBoxLayout()
        self.radio_button_group = QButtonGroup()
        layout.addLayout(self.radio_buttons_layout)
        
        button_layout = QHBoxLayout()

        self.prev_button = QPushButton('Prev image', self.page5)
        self.prev_button.clicked.connect(self.show_previous_image)
        self.prev_button.setFocusPolicy(Qt.NoFocus)  # 讓按鈕無法被選中
        button_layout.addWidget(self.prev_button)

        self.next_button5 = QPushButton('Next image', self.page5)
        self.next_button5.clicked.connect(self.show_next_image)
        self.next_button5.setFocusPolicy(Qt.NoFocus)  # 讓按鈕無法被選中
        button_layout.addWidget(self.next_button5)

        layout.addLayout(button_layout)
        self.page5.setLayout(layout)

    def keyPressEvent(self, event):
        if self.stackedWidget.currentWidget() == self.page5:  # 只在 Page 5 監聽鍵盤
            key = event.key()
            if Qt.Key_1 <= key <= Qt.Key_9:  # 數字鍵 1-9
                index = key - Qt.Key_1  # 轉換為索引（0-based）
                button = self.radio_button_group.button(index)
                if button:
                    button.setChecked(True)  # 設定選中
            elif key == Qt.Key_Left:
                self.prev_button.setFocusPolicy(Qt.NoFocus)
                self.next_button5.setFocusPolicy(Qt.NoFocus)
                self.show_previous_image()
                return
            elif key == Qt.Key_Right:
                self.prev_button.setFocusPolicy(Qt.NoFocus)
                self.next_button5.setFocusPolicy(Qt.NoFocus)
                self.show_next_image()
                return
        super().keyPressEvent(event)  # 傳遞其他事件

    def load_dataset(self):
        dataset_dir = QFileDialog.getExistingDirectory(self, 'Select Dataset Folder')
        if dataset_dir:
            self.dataset_dir = dataset_dir
            # 重設 classes 與當前圖片 ID
            self.current_img_id = 0
            self.image_classes = []
            self.label_mode = 'onehot'
            self.label_mode_locked = False

            categories = os.listdir(dataset_dir)
            self.images_dir = None
            self.label_dir = None
            for category in categories:
                if category == 'images':
                    self.images_dir = os.path.join(dataset_dir, category)
                elif category in ['labels', 'labelTxt']:
                    self.label_dir = os.path.join(dataset_dir, category)

            # 若 labels 資料夾不存在，則自動建立一個
            if self.label_dir is None:
                self.label_dir = os.path.join(dataset_dir, 'labels')
                os.makedirs(self.label_dir, exist_ok=True)

            if self.images_dir is None:
                QMessageBox.critical(self, 'Error', 'Dataset must contain an "images" folder.')
                return

            # 計算圖片數量
            self.image_files = os.listdir(self.images_dir)
            self.image_count = len(self.image_files)
            # 根據圖片數量創建相同數量的"未開啟過"
            self.has_ever_opened = [False] * self.image_count
            self.next_button2.setEnabled(True)
            self.dataset_info_label.setText(f'Dataset Directory: {self.dataset_dir}\nImage Directory: {self.images_dir}\nLabel Directory: {self.label_dir}')

            # 嘗試從 labels 資料夾讀取已儲存的 classes 設定檔
            classes_file = os.path.join(self.label_dir, 'classes.txt')
            if os.path.exists(classes_file):
                try:
                    mode = 'onehot'
                    loaded_classes = []
                    mode_from_file = False
                    with open(classes_file, 'r', encoding='utf-8') as f:
                        for raw_line in f:
                            line = raw_line.strip()
                            if not line:
                                continue
                            if line.startswith('__mode__='):
                                val = line.split('=', 1)[1].strip().lower()
                                if val in ('onehot', 'truelabel'):
                                    mode = val
                                    mode_from_file = True
                                continue
                            loaded_classes.append(line)
                    if loaded_classes:
                        self.image_classes = loaded_classes
                        self.label_mode = mode
                        self.class_list_label.setText('Classes: ' + ', '.join(self.image_classes))
                        self.confirm_classes_label.setText('Classes: ' + ', '.join(self.image_classes))
                        self.next_button3.setEnabled(True)

                        # 依照儲存的模式更新並鎖定選項，避免混用
                        if mode == 'truelabel':
                            self.label_mode_truelabel.setChecked(True)
                        else:
                            self.label_mode_onehot.setChecked(True)

                        if mode_from_file:
                            self.label_mode_locked = True
                            self.label_mode_onehot.setEnabled(False)
                            self.label_mode_truelabel.setEnabled(False)
                except Exception as e:
                    QMessageBox.warning(self, 'Warning', f'Failed to load saved classes: {e}')

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

    def handle_classes_confirmed(self):
        # 確認至少有一個類別，並將類別資訊存到 labels 資料夾
        if not hasattr(self, 'image_classes') or not self.image_classes:
            QMessageBox.warning(self, 'No Classes', 'Please add at least one class before proceeding.')
            return

        # 從 UI 讀取目前選擇的標記模式（若未被鎖定）
        if not self.label_mode_locked:
            if self.label_mode_truelabel.isChecked():
                self.label_mode = 'truelabel'
            else:
                self.label_mode = 'onehot'

        try:
            classes_file = os.path.join(self.label_dir, 'classes.txt')
            with open(classes_file, 'w', encoding='utf-8') as f:
                # 第一行記錄此資料集的標記模式
                f.write(f"__mode__={self.label_mode}\n")
                # 後面每行為一個類別名稱
                for cls in self.image_classes:
                    f.write(f"{cls}\n")
        except Exception as e:
            QMessageBox.warning(self, 'Warning', f'Failed to save classes: {e}')

        self.confirm_classes_label.setText('Classes: ' + ', '.join(self.image_classes))
        self.stackedWidget.setCurrentWidget(self.page4)

    def _parse_one_hot_line(self, line):
        """嘗試將一行字串解析為 0/1 one-hot 向量，失敗則回傳 None。"""
        if not hasattr(self, 'image_classes') or not self.image_classes:
            return None

        parts = line.strip().split()
        if len(parts) != len(self.image_classes):
            return None

        try:
            vec = [int(p) for p in parts]
        except ValueError:
            return None

        if any(v not in (0, 1) for v in vec):
            return None

        return vec

    def displayImageAndLabel(self, img_id):
        try:
            # 將目錄中所有的圖片與標籤放入image_files, label_files
            image_files = self.image_files

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

            # 若找不到對應的標籤檔，則自動建立一個空的 txt 檔案
            if not os.path.exists(label_path):
                try:
                    open(label_path, 'w').close()
                except Exception as e:
                    raise FileNotFoundError(f"Failed to create label file: {label_path}, error: {e}")

            # 讀取並從開頭開始寫入
            with open(label_path, 'r+') as file:
                label_lines = file.readlines()
                
                # 沒有標記內容則引發錯誤訊息
                if not label_lines:
                    # 無任何標記：預設全 0，不選擇任何類別
                    one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
                    one_hot_str = " ".join(map(str, one_hot_vector.astype(int)))
                    self.txt_label.setText(f'TXT Content: ')
                else:
                    # 取得最後一行內容
                    last_line = label_lines[-1].strip()

                    if self.label_mode == 'truelabel':
                        # TrueLabel：嘗試讀取整數索引（1-based），轉為 one-hot 顯示
                        idx = 0
                        try:
                            val = int(last_line)
                            if 1 <= val <= len(self.image_classes):
                                idx = val
                        except ValueError:
                            idx = 0

                        one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
                        if idx > 0:
                            one_hot_vector[idx - 1] = 1
                            self.txt_label.setText(f'TXT Content: {idx}')
                        else:
                            self.txt_label.setText(f'TXT Content: ')

                        one_hot_str = " ".join(map(str, one_hot_vector.astype(int)))
                    else:
                        # One-hot 模式：解析最後一行為 one-hot，失敗則使用全 0
                        parsed_vec = self._parse_one_hot_line(last_line)
                        if parsed_vec is not None:
                            one_hot_str = " ".join(map(str, parsed_vec))
                            self.txt_label.setText(f'TXT Content: {one_hot_str}')
                        else:
                            one_hot_vector = np.zeros(len(self.image_classes), dtype=int)
                            one_hot_str = " ".join(map(str, one_hot_vector.astype(int)))
                            self.txt_label.setText(f'TXT Content: ')

                self.updateRadioButtons(one_hot_str)

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

        
        # if ((len(parts) == len(self.image_classes) + 1) and (part1type == "integer")):  # Assuming space-separated format with class_str at the end [clbool_0 clbool_1 ... clbool_nk-1 cls_str]
        #     print('int')
        #     # one_hot_vector = list(map(int, parts[:-1])) #in this case, it reads a one-hot vector
        #     # cls_str = parts[-1]
        #     # self.updateRadioButtons(one_hot)
            
        # elif ((len(parts) == 5) and (part1type == "float")): # Yolo-HBB format [cls_int xc yc w h]
        #     print('HBB')
        #     # cls_int = int(parts[0])
        #     # cls_str = self.image_classes[cls_int]
        #     # one_hot_vector = self.string_to_one_hot([cls_str], self.image_classes)
        #     # one_hot_vector_str = " ".join(map(str, one_hot_vector[0].astype(int)))
        #     # # Append the converted one-hot vector to the file
        #     # label_filename = self.tempfilename.rsplit('.', 1)[0] + '.txt'
        #     # label_path = os.path.join(self.label_dir, label_filename)
        #     # with open(label_path, 'a') as file:
        #     #     file.write(f"\n{one_hot_vector_str}") 
        #     # self.updateRadioButtons(one_hot)            
            
        # elif len(parts) == 10:  # Yolo-OBB format [x1 ... y4 cls_str conf]
        #     print('OBB')
        #     # cls_str = parts[-2]
        #     # one_hot_vector = self.string_to_one_hot([cls_str], self.image_classes)
        #     # one_hot_vector_str = " ".join(map(str, one_hot_vector[0].astype(int)))
        #     # # Append the converted one-hot vector to the file
        #     # label_filename = self.tempfilename.rsplit('.', 1)[0] + '.txt'
        #     # label_path = os.path.join(self.label_dir, label_filename)
        #     # with open(label_path, 'a') as file:
        #     #     file.write(f"\n{one_hot_vector_str}")
        #     # self.updateRadioButtons(one_hot)        
        # else:
        #     QMessageBox.critical(self, "Error", f"Unrecognised data format") #無法辨別標籤格式

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
            # 確保標籤檔存在
            if not os.path.exists(label_path):
                open(label_path, 'w').close()

            # 依標記模式寫入檔案
            if self.label_mode == 'truelabel':
                # TrueLabel：直接寫入類別索引（1-based）
                label_value = selected_id + 1
                with open(label_path, 'r+') as file:
                    lines = file.readlines()
                    if not lines:
                        lines.append(f"{label_value}")
                    else:
                        last_line = lines[-1].strip()
                        is_valid_int = False
                        try:
                            existing = int(last_line)
                            if 1 <= existing <= len(self.image_classes):
                                is_valid_int = True
                        except ValueError:
                            is_valid_int = False

                        if is_valid_int:
                            lines[-1] = f"{label_value}"
                        else:
                            lines.append(f"\n{label_value}")

                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()
            else:
                # One-hot：維持原本行為
                with open(label_path, 'r+') as file:
                    # 讀取所有行
                    lines = file.readlines()
                    if not lines:
                        lines.append(f"{one_hot_vector_str}")
                    else:
                        last_line = lines[-1].strip()
                        # 如果最後一行已是合法 one-hot，則覆寫；否則新增一行
                        if self._parse_one_hot_line(last_line) is not None:
                            lines[-1] = f"{one_hot_vector_str}"
                        else:
                            lines.append(f"\n{one_hot_vector_str}")
                    # 將讀寫頭放回開頭
                    file.seek(0)
                    # 複寫新文字
                    file.writelines(lines)
                    # 截斷多餘舊內容
                    file.truncate()


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
        parts = one_hot_str.split()
        expected_len = len(self.image_classes)
        # 預設為全 0，長度與 classes 一致
        one_hot_vector = [0] * expected_len

        if expected_len > 0 and len(parts) >= expected_len:
            try:
                candidate = [int(p) for p in parts[:expected_len]]
                if all(v in (0, 1) for v in candidate):
                    one_hot_vector = candidate
            except ValueError:
                # 若解析失敗則維持全 0
                pass

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

     # 設定全局字體大小
    app.setFont(QFont("Arial", 14))
    
    window = ImageLabelingApp()
    window.show()
    sys.exit(app.exec_())
