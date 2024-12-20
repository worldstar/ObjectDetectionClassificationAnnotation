import os
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor

# 設定日誌
logging.basicConfig(
    filename='overwrite_log.txt',  # 日誌文件名稱
    level=logging.INFO,           # 設定日誌級別
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='cp1252'
)

def build_target_index(target_dir):
    target_index = {}
    for root, _, files in os.walk(target_dir):
        for file_name in files:
            if file_name.endswith('.txt') and not file_name.startswith('.'):  # 排除隱藏文件
                target_index[file_name] = os.path.join(root, file_name)
    return target_index

def copy_file(source_file, target_file):
    try:
        shutil.copy2(source_file, target_file)
        message = f"覆蓋完成: {source_file} -> {target_file}"
        # print(message)
        logging.info(message)  # 記錄成功的覆蓋操作
    except Exception as e:
        message = f"覆蓋失敗: {source_file} -> {target_file}，錯誤: {e}"
        print(message)
        logging.error(message)  # 記錄失敗的覆蓋操作

def overwrite_labels_with_dict(source_dir, target_dir):
    if not os.path.exists(source_dir):
        message = f"來源資料夾不存在: {source_dir}"
        print(message)
        logging.error(message)
        return
    if not os.path.exists(target_dir):
        message = f"目標資料夾不存在: {target_dir}"
        print(message)
        logging.error(message)
        return

    # 建立目標資料夾的索引
    print("正在建立目標資料夾的索引...")
    target_index = build_target_index(target_dir)
    print(f"索引建立完成，共 {len(target_index)} 個文件。")
    logging.info(f"索引建立完成，共 {len(target_index)} 個文件。")

    # 建立一個線程池
    with ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(source_dir):
            for file_name in files:
                if file_name.endswith('.txt') and not file_name.startswith('.'):  # 排除隱藏文件
                    source_file = os.path.join(root, file_name)

                    # 根據文件名稱查找目標路徑
                    target_file = target_index.get(file_name)
                    if target_file:
                        # 提交覆蓋任務到線程池
                        futures.append(executor.submit(copy_file, source_file, target_file))
                    else:
                        message = f"未找到對應文件: {file_name}，跳過覆蓋。"
                        print(message)
                        logging.warning(message)  # 記錄跳過的文件

        # 等待所有線程完成
        for future in futures:
            future.result()

# 使用範例
source_folder = "testing/src"  # 替換為來源資料夾路徑
target_folder = "testing/dest"  # 替換為目標資料夾路徑

overwrite_labels_with_dict(source_folder, target_folder)
