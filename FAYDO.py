import sys
import math
import threading
import time
import os
import glob
import webbrowser
import subprocess
import speech_recognition as sr
import pyttsx3
import pyautogui
import wikipedia
from dotenv import load_dotenv


load_dotenv('weather.env')

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QSizePolicy, QHBoxLayout, QLineEdit,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer, QPoint
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QFont,
    QIcon, QLinearGradient, QRadialGradient, QPixmap
)

# ---------------------- Voice Assistant Core ----------------------
engine = pyttsx3.init()

class LogEmitter(QObject):
    log_signal = pyqtSignal(str)

log_emitter = LogEmitter()

def speak(text):
    engine.say(text)
    engine.runAndWait()
    log_emitter.log_signal.emit(f"Faydo: {text}")

def listen(timeout=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        log_emitter.log_signal.emit("Calibrating for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        log_emitter.log_signal.emit("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            log_emitter.log_signal.emit(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError:
            speak("Speech recognition service is unavailable.")
            return ""
        except sr.WaitTimeoutError:
            return ""

def search_file(filename, directory="C:/"):
    speak(f"Searching for {filename}")
    files = glob.glob(f"{directory}//{filename}*", recursive=True)
    if files:
        speak(f"Found {filename}. Opening it now.")
        os.startfile(files[0])
    else:
        speak(f"Sorry, I couldn't find {filename} on your system.")

def execute_command(command):
    if "open notepad" in command:
        speak("Opening Notepad")
        subprocess.Popen(["notepad.exe"])
    elif "open chrome" in command:
        speak("Opening Google Chrome")
        os.system("start chrome")
    elif "open explorer" in command:
        speak("Opening File Explorer")
        os.system("explorer")
    elif "open calculator" in command:
        speak("Opening Calculator")
        os.system("calc")
    elif "open vs code" in command or "open visual studio code" in command:
        speak("Opening Visual Studio Code")
        os.system("code")
    elif "shutdown" in command:
        speak("Shutting down the system")
        os.system("shutdown /s /t 5")
    elif "restart" in command:
        speak("Restarting the system")
        os.system("shutdown /r /t 5")
    elif "log off" in command:
        speak("Logging off")
        os.system("shutdown /l")
    elif "left click" in command or ("click" in command and "double" not in command):
        speak("Performing left click")
        pyautogui.click()
    elif "double click" in command:
        speak("Performing double click")
        pyautogui.doubleClick()
    elif "right click" in command:
        speak("Performing right click")
        pyautogui.rightClick()
    elif "scroll up" in command:
        speak("Scrolling up")
        pyautogui.scroll(500)
    elif "scroll down" in command:
        speak("Scrolling down")
        pyautogui.scroll(-500)
    elif "close window" in command:
        speak("Closing the active window")
        pyautogui.hotkey('alt', 'f4')
    elif "switch window" in command:
        speak("Switching windows")
        pyautogui.hotkey('alt', 'tab')
    elif "lock screen" in command:
        speak("Locking the screen")
        pyautogui.hotkey("win", "l")
    elif "increase volume" in command:
        speak("Increasing volume")
        pyautogui.press("volumeup")
    elif "decrease volume" in command:
        speak("Decreasing volume")
        pyautogui.press("volumedown")
    elif "mute volume" in command or "mute" in command:
        speak("Muting volume")
        pyautogui.press("volumemute")
    elif "type" in command:
        words = command.replace("type", "").strip()
        speak(f"Typing {words}")
        pyautogui.write(words, interval=0.1)
        if "search" in words:
            speak(f"Searching for {words} in Chrome")
            pyautogui.hotkey('ctrl', 't')
            pyautogui.write('https://www.google.com/search?q=' + words)
            pyautogui.press('enter')
    elif command.startswith("search for"):
        query = command.replace("search for", "").strip()
        speak(f"Searching for {query}")
        os.system(f'start chrome "https://www.google.com/search?q={query}"')
    elif command.startswith("open "):
        websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "chat gpt": "https://chat.openai.com/"
        }
        site = command.replace("open ", "").strip()
        if site in websites:
            speak(f"Opening {site}")
            if site == "chat gpt":
                webbrowser.open(websites[site])
                time.sleep(5)
                extra_input = command.replace("open chat gpt", "").strip()
                if extra_input:
                    pyautogui.write(extra_input)
                    pyautogui.press('enter')
            else:
                os.system(f'start chrome "{websites[site]}"')
        else:
            speak("Website not recognized.")
    elif "search file" in command:
        filename = command.replace("search file", "").strip()
        if filename:
            search_file(filename)
        else:
            speak("Please say the filename you want to search for.")
            
    elif "search" in command:
        query = command.replace("search", "").strip()
        if query:
            speak(f"Searching Wikipedia for {query}")
            try:
                result = wikipedia.summary(query, sentences=2)
                speak(result)
            except wikipedia.exceptions.DisambiguationError:
                speak("Multiple results found. Please be more specific.")
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find any information on that topic.")
        else:
            speak("Please specify what you want to search for.")
            
    elif "close application" in command:
        speak("Which application do you want to close?")
        app_name = listen(timeout=5)
        if app_name:
            try:
                os.system(f'taskkill /F /IM {app_name}.exe')
                speak(f"{app_name} closed successfully!")
            except Exception as e:
                speak(f"Error closing {app_name}: {e}")
                
    elif "enter" in command:
        speak("Pressing enter")
        pyautogui.press("enter")
        
    elif "play music" in command:
        speak("Playing music")
        os.system("start wmplayer")
        
    elif "next song" in command:
        speak("Skipping to the next song")
        pyautogui.press("media_nexttrack")
        
    elif "previous song" in command:
        speak("Going back to the previous song")
        pyautogui.press("media_prevtrack")
        
    elif "stop music" in command:
        speak("Stopping the music")
        pyautogui.press("media_stop")
        
    elif "exit program" in command or "stop listening" in command or "close everything" in command or command in ["exit", "stop"]:
        speak("Exiting program. Goodbye!")
        stop_listening()
        os._exit(0)
    
    elif "weather" in command:
        fetch_weather(command)

    elif "brightness" in command:
        adjust_brightness(command)
        
    elif "take screenshot" in command:
        take_screenshot()
        
    elif "exit program" in command or "stop listening" in command or "close everything" in command or command in ["exit", "stop"]:
        speak("Exiting program. Goodbye!")
        stop_listening()
        os._exit(0)
    
    else:
        speak("Command not recognized.")

def take_screenshot():
    filename = f"screenshot_{int(time.time())}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    speak(f"Screenshot saved as {filename}")

def adjust_brightness(command):
    try:
        import re
        match = re.search(r'(\d+)', command)
        if match:
            brightness = int(match.group(1))
            brightness = max(0, min(100, brightness))
            try:
                sbc.set_brightness(brightness)
                speak(f"Brightness set to {brightness}%")
            except Exception as e:
                speak("Sorry, brightness control is not supported on this device.")
        else:
            speak("Please specify the brightness level.")
    except Exception as e:
        speak("Sorry, I couldn't understand the brightness command.")



def fetch_weather(command):
    import requests
    city = command.replace("weather in", "").replace("weather", "").strip()
    if not city:
        speak("Please specify a city for weather information.")
        return

    API_KEY = os.getenv("OPENWEATHER_API")
    if not API_KEY:
        speak("Weather API key is missing. Please configure it.")
        return

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data.get("cod") == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            speak(f"Weather in {city} is {weather} with temperature {temp} degrees Celsius.")
        else:
            speak(f"Couldn't find weather for {city}.")
    except Exception as e:
        speak("Failed to retrieve weather data.")

# ---------------------- Listening Management ----------------------
listening = False
assistant_thread = None

def voice_assistant_loop():
    global listening
    while listening:
        command = listen(timeout=5)
        if command:
            execute_command(command)
        time.sleep(0.5)

def start_listening():
    global listening, assistant_thread
    if not listening:
        listening = True
        assistant_thread = threading.Thread(target=voice_assistant_loop, daemon=True)
        assistant_thread.start()
        log_emitter.log_signal.emit("Faydo started listening...")

def stop_listening():
    global listening
    listening = False
    log_emitter.log_signal.emit("Faydo stopped.")

# ---------------------- Interactive Robot Image ----------------------
class InteractiveRobot(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load your robot image; update the path as needed
        self.setPixmap(QPixmap(r"E:/Speech/ai.png"))
        self.setScaledContents(True)
        self.setFixedSize(200, 200)
        # Optional: add a drop shadow effect for style
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        # When clicked, the robot speaks a greeting
        speak("Hello! I'm your Faydo interactive robot assistant. I'll make your work easier and more efficient!")
        super().mousePressEvent(event)

# ---------------------- Modern UI Implementation ----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Faydo Companion 🤖✨")
        self.setGeometry(200, 100, 500, 650)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.oldPos = self.pos()
        self.setup_ui()

    def setup_ui(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        widget.setLayout(main_layout)

        # Header with gradient text
        header = QLabel("Faydo Companion")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font: bold 32px 'Segoe UI';
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B6B, stop:0.5 #4ECDC4, stop:1 #556270);
                -webkit-background-clip: text;
                color: transparent;
            }
        """)
        main_layout.addWidget(header)

        # Interactive Robot Image
        self.robot_widget = InteractiveRobot()
        # Center the robot image
        main_layout.addWidget(self.robot_widget, 0, Qt.AlignCenter)

        # Status container
        self.status_container = QWidget()
        self.status_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 15px;
        """)
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label
        self.status_label = QLabel("Tap the mic to start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font: 16px 'Segoe UI';
            color: #666;
            padding: 8px;
        """)
        status_layout.addWidget(self.status_label)

        # Mic button
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(100, 100)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5,
                    fx:0.5, fy:0.5, stop:0 white, stop:1 #FF6B6B);
                border-radius: 50px;
                border: 3px solid #ffffff;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover { background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5,
                    fx:0.5, fy:0.5, stop:0 white, stop:1 #FF5252); }
            QPushButton:pressed { box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); }
        """)
        self.mic_icon = QLabel(self.mic_button)
        self.mic_icon.setPixmap(QIcon.fromTheme("microphone").pixmap(40, 40))
        self.mic_icon.setAlignment(Qt.AlignCenter)
        self.mic_icon.setGeometry(30, 30, 40, 40)
        self.mic_button.clicked.connect(self.toggle_listening)
        status_layout.addWidget(self.mic_button, 0, Qt.AlignCenter)

        self.status_container.setLayout(status_layout)
        main_layout.addWidget(self.status_container)

        # Command input
        input_container = QWidget()
        input_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 10px;
        """)
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command and press Enter...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font: 14px 'Segoe UI';
                padding: 8px;
                background: transparent;
            }
        """)
        self.command_input.returnPressed.connect(self.process_text_command)
        input_layout.addWidget(self.command_input)
        input_container.setLayout(input_layout)
        main_layout.addWidget(input_container)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: none;
                font: 13px 'Segoe UI';
                padding: 15px;
                color: #444;
            }
        """)
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        # Window styling
        widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ECE9E6, stop:1 #FFFFFF);
                border-radius: 20px;
            }
        """)
        self.setCentralWidget(widget)
        self.add_shadow()

    def add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.centralWidget().setGraphicsEffect(shadow)

    # Window dragging functionality
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def toggle_listening(self):
        global listening
        if not listening:
            start_listening()
            self.status_label.setText("Listening...")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5,
                        fx:0.5, fy:0.5, stop:0 white, stop:1 #4ECDC4);
                    border-radius: 50px;
                }
            """)
        else:
            stop_listening()
            self.status_label.setText("Tap the mic to start")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5,
                        fx:0.5, fy:0.5, stop:0 white, stop:1 #FF6B6B);
                    border-radius: 50px;
                }
            """)

    def process_text_command(self):
        command = self.command_input.text().strip()
        if command:
            log_emitter.log_signal.emit(f"You (typed): {command}")
            execute_command(command)
            self.command_input.clear()

    def append_log(self, message):
        if "Faydo:" in message:
            self.log_area.append(f"""
                <div style="margin:5px; padding:8px 12px; 
                    background:#e3f2fd; border-radius:10px;
                    border-bottom-left-radius:0;">
                    {message}
                </div>
            """)
        else:
            self.log_area.append(f"""
                <div style="margin:5px; padding:8px 12px; 
                    background:#f5f5f5; border-radius:10px;
                    border-bottom-right-radius:0; text-align:right;">
                    {message}
                </div>
            """)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        stop_listening()
        super().closeEvent(event)

# ---------------------- Application Entry Point ----------------------
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    log_emitter.log_signal.connect(main_window.append_log)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
