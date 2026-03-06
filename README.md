# yolo-classification-gui-by-gyf-v0.18使用教學
## 流程簡介
看完後請點選“Next”進入下一步。
<p align="center">
<img src="images/image1.png" width="600">
</p>

## 📁 步驟 1: 載入資料集
點選“Load Dataset”挑選資料集。

<p align="center">
<img src="images/image2.png" width="600">
</p>

<p align="center">
<img src="images/image3.png" width="600">
</p>

> [!IMPORTANT]
> 資料集內部需含有資料夾 `images` 及 `labels`（`labels` 可用 `labelTxt` 替代）。

## ⚙️ 步驟 2: 設定類別格式
這邊可能跳出兩種畫面，分別是第一次使用這個程式與接續使用，您可以檢查 `labels` 或 `labelTxt` 內是否存在檔案 classes.txt 。

### CASE１:第一次使用將需要的類別分次輸入，如下圖。並根據需求選擇One-hot vector或是True label完成後點選“Next”
此處類別假設了踢足球的三種可能場景，公園、學校操場與足球場。

<p align="center">
<img src="images/image4.png" width="600">
</p>

Ex. 0 1 0 0 表示第二個類別
Ex. 3 表示第四個類別(0-base)

### CASE２:接續使用Labels內部有儲存之前的紀錄在 classes.txt ，可以點選Yes跳過輸入類別。
<p align="center">
<img src="images/image5.png" width="600">
</p>

確認檔案正確後點選“Next”。
<p align="center">
<img src="images/image6.png" width="600">
</p>

上述完成後即可開始使用
<p align="center">
<img src="images/image7.png" width="600">
</p>

完成後點選“Ｘ”離開
第一步：選擇是否點選標記(可以透過數字鍵1~9點選)
第二步：選擇前一張或後一張圖片繼續標記(可以透過方向鍵左右進行切換)
