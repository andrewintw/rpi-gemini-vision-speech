# Raspberry Pi Gemini Vision 系統

這是一個運行於 Raspberry Pi 的影像辨識系統，使用 Google Gemini API 進行影像分析，並透過語音輸出結果。

## 環境需求

- Python 3.9+
- Webcam
- 喇叭（用於語音輸出）
- GPIO 按鈕（接在 GPIO17）

## 安裝步驟

1. 建議先更新 pip：
```bash
python -m pip install --upgrade pip
```

2. 安裝必要的 Python 套件：
```bash
# 使用 requirements.txt 安裝所有套件
sudo pip3 install -r requirements.txt

# 或手動安裝個別套件
sudo pip3 install google-genai      # Google Gemini API
sudo pip3 install opencv-python     # 攝影機控制與圖片處理
sudo pip3 install pillow            # 圖片處理
sudo pip3 install keyboard          # 鍵盤控制
sudo pip3 install gTTS              # Google Text-to-Speech
sudo pip3 install pygame            # 音訊播放
sudo pip3 install RPi.GPIO          # GPIO 控制
```

## 專案結構

```
RPi_Gemini_Vision/
├── audio/                     # 語音輸出暫存目錄
├── images/                    # 圖片存放目錄
│   └── captures/              # 拍攝的照片
├── rpi-gemini-vision.py       # 主程式
└── rpi-gemini-vision.service  # 系統服務設定檔
```

## 功能特點

- 支援中文語音輸出分析結果
- 支援攝影機即時拍攝與分析
- 支援 GPIO 按鈕觸發拍攝
- 支援鍵盤控制（空白鍵拍攝，q 鍵結束）

## 硬體連接

1. GPIO 接線：
   - 按鈕一端接 GPIO17 (實體腳位 11)
   - 按鈕另一端接 GND (任一接地腳位)

## 系統服務設定

若要讓程式在 Raspberry Pi 開機時自動執行，請依照以下步驟設定：

1. 複製服務檔案到系統目錄：
```bash
sudo cp rpi-gemini-vision.service /etc/systemd/system/
```

2. 重新載入 systemd：
```bash
sudo systemctl daemon-reload
```

3. 啟用服務：
```bash
sudo systemctl enable rpi-gemini-vision
```

4. 啟動服務：
```bash
sudo systemctl start rpi-gemini-vision
```

服務管理指令：
- 查看狀態：`sudo systemctl status rpi-gemini-vision`
- 停止服務：`sudo systemctl stop rpi-gemini-vision`
- 重啟服務：`sudo systemctl restart rpi-gemini-vision`
- 查看日誌：`sudo journalctl -u rpi-gemini-vision`

## 注意事項

- 請確保攝影機可正常使用
- 需要有效的 Gemini API 金鑰（在程式碼中設定）
- 需要連接喇叭以聽取語音輸出
- 需要正確連接 GPIO 按鈕
- 需要網路連接以使用 Gemini API 和 Google TTS 

## 部署步驟

1. 建立專案目錄：
```bash
mkdir -p /home/pi/RPi_Gemini_Vision
cd /home/pi/RPi_Gemini_Vision
```

2. 建立必要的子目錄：
```bash
mkdir -p audio    # 語音輸出暫存目錄
mkdir -p images/captures    # 拍攝照片儲存目錄
```

3. 複製程式檔案：
```bash
# 複製主程式
cp rpi-gemini-vision.py /home/pi/RPi_Gemini_Vision/

# 複製服務檔案
sudo cp rpi-gemini-vision.service /etc/systemd/system/
```

雖然程式會自動建立必要的目錄，但建議還是手動建立以確保權限正確。 