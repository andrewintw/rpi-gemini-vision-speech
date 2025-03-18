import cv2
import keyboard
import time
from datetime import datetime
import os
from google import genai
from PIL import Image
from gtts import gTTS
import pygame
import RPi.GPIO as GPIO  # 新增 GPIO 支援

# 直接設定變數（之後可以改為從設定檔讀取）
GEMINI_API_KEY = "AIzaSyDt7LRWsHFYaFeOh46ZHfF1NQbJQ6Pjbow"
BUTTON_PIN = 17  # GPIO17 用於拍照按鈕

# 初始化 GPIO
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class CameraModule:
    def __init__(self):
        self.camera = None
        # 確保圖片存放路徑存在
        self.image_dir = os.path.join(os.path.dirname(__file__), 'images', 'captures')
        os.makedirs(self.image_dir, exist_ok=True)
    
    def initialize_camera(self):
        """開啟攝影機"""
        try:
            if self.camera is not None:
                self.release()
            
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                raise Exception("無法開啟攝影機")
            return True
            
        except Exception as e:
            print("攝影機初始化失敗")
            self.release()
            return False
    
    def capture_image(self):
        """拍攝照片"""
        try:
            # 開啟攝影機
            if not self.initialize_camera():
                return None
            
            # 拍攝照片
            ret, frame = self.camera.read()
            
            # 立即關閉攝影機
            self.release()
            
            if not ret:
                raise Exception("無法擷取影像")
            
            # 產生時間戳記檔名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            filepath = os.path.join(self.image_dir, filename)
            
            # 儲存影像
            cv2.imwrite(filepath, frame)
            print(f"已儲存影像: {filepath}")
            return filepath
            
        except Exception as e:
            print("拍攝失敗")
            self.release()
            return None
    
    def release(self):
        """釋放攝影機資源"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None

class GeminiVisionModule:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.prompt = """
        - 請用繁體中文回答，這張圖片可獲得的資訊
        - 不要做格式化的輸出，因為這是給語音輸出用的
        - 試著描述圖片的場景，並且描述圖片中的人物或物體之間的關係
        """
    
    def analyze_image(self, image_path):
        """分析圖片內容"""
        try:
            # 開啟並確認圖片
            if not os.path.exists(image_path):
                raise FileNotFoundError("找不到圖片")
            
            img = Image.open(image_path)
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[self.prompt, img]
            )
            return response.text
            
        except Exception as e:
            print("影像分析失敗")
            return None

class TTSModule:
    def __init__(self):
        # 初始化 pygame 用於音訊播放
        pygame.mixer.init()
        
        # 確保輸出目錄存在
        self.output_dir = os.path.join(os.path.dirname(__file__), 'audio')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def text_to_speech(self, text):
        """將文字轉換成語音並播放"""
        try:
            if not text:
                return False
            
            output_file = os.path.join(self.output_dir, "output.mp3")
            
            # 如果檔案存在，先停止播放並釋放
            if os.path.exists(output_file):
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                try:
                    os.remove(output_file)
                except:
                    return False
            
            # 使用 gTTS 轉換文字為語音
            tts = gTTS(text=text, lang='zh-tw')
            tts.save(output_file)
            
            # 播放音訊
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # 播放完成後釋放檔案
            pygame.mixer.music.unload()
            return True
            
        except Exception as e:
            print("TTS 處理失敗")
            return False
    
    def cleanup(self):
        """清理暫存的音訊檔"""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        
        output_file = os.path.join(self.output_dir, "output.mp3")
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except:
                pass

def main():
    # 初始化 GPIO
    setup_gpio()
    
    camera = CameraModule()
    vision = GeminiVisionModule()
    tts = TTSModule()
    
    print("\n系統就緒！按下按鈕或空白鍵拍攝，按 q 結束程式")
    
    try:
        while True:
            # 檢查 GPIO 按鈕
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # 按鈕被按下
                print("\n開始拍攝...")
                image_path = camera.capture_image()
                
                if image_path:
                    print("開始分析影像...")
                    result = vision.analyze_image(image_path)
                    
                    if result:
                        print("\n分析結果：")
                        print(result)
                        print("\n開始語音輸出...")
                        tts.text_to_speech(result)
                        print("\n按下按鈕或空白鍵拍攝，按 q 結束程式")
                
                time.sleep(0.5)  # 防止按鈕彈跳
            
            # 保留鍵盤控制以方便開發測試
            if keyboard.is_pressed('space'):
                print("\n開始拍攝...")
                image_path = camera.capture_image()
                
                if image_path:
                    print("開始分析影像...")
                    result = vision.analyze_image(image_path)
                    
                    if result:
                        print("\n分析結果：")
                        print(result)
                        print("\n開始語音輸出...")
                        tts.text_to_speech(result)
                        print("\n按下按鈕或空白鍵拍攝，按 q 結束程式")
                
                time.sleep(0.5)
            
            elif keyboard.is_pressed('q'):
                print("\n結束程式...")
                break
            
            time.sleep(0.1)
            
    except Exception as e:
        print("程式執行發生錯誤")
    
    finally:
        camera.release()
        tts.cleanup()
        GPIO.cleanup()  # 清理 GPIO 設定

if __name__ == "__main__":
    main()