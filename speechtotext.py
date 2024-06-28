import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QComboBox, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QTextCursor
import speech_recognition as sr
from googletrans import Translator

class WhisperThread(QThread):
    recognized = pyqtSignal(str)

    def __init__(self, input_lang, translation_lang):
        super().__init__()
        self.input_lang = input_lang
        self.translation_lang = translation_lang

    def run(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            while getattr(self, "running", True):
                try:
                    audio = recognizer.listen(source)
                    text = recognizer.recognize_google_cloud(audio, language=self.input_lang)
                    translated_text = self.translate_text(text, self.input_lang, self.translation_lang)
                    self.recognized.emit(translated_text)
                except sr.UnknownValueError:
                    pass  # Ignore unrecognized speech

    def translate_text(self, text, src_lang, dest_lang):
        translator = Translator()
        translated_text = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated_text.text

class WhisperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #fdfcdc;")
        self.setWindowIcon(QIcon("C:\\Users\\sansk\\Desktop\\test\\s-l1600.jpg"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)
    
        # Input language selection
        self.input_lang_label = QLabel("Input Language:")
        layout.addWidget(self.input_lang_label)
        self.input_lang_combo = QComboBox()
        self.input_lang_combo.addItems(["en", "es", "fr", "de"])  # Add more languages as needed
        layout.addWidget(self.input_lang_combo)
    
        # Translation language selection
        self.translation_lang_label = QLabel("Translation Language:")
        layout.addWidget(self.translation_lang_label)
        self.translation_lang_combo = QComboBox()
        self.translation_lang_combo.addItems(["es", "fr", "de", "hi"])  # Add more languages as needed
        layout.addWidget(self.translation_lang_combo)

        # "Get Started" button
        self.get_started_button = QPushButton("Get Started")
        self.get_started_button.clicked.connect(self.show_whisper_interface)
        self.get_started_button.setStyleSheet("background-color: #ffc300; color: black; border-radius: 8; padding: 10px;")
        layout.addWidget(self.get_started_button, alignment=Qt.AlignCenter)  # Align to center

        self.text_box = QTextEdit()
        self.text_box.hide()  # Initially hide the text box
        layout.addWidget(self.text_box)

        button_layout = QVBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_whisper)
        self.start_button.setStyleSheet("background-color: #ffc300; color: black; border-radius: 8; padding: 10px;")
        button_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setDisabled(True)
        self.stop_button.clicked.connect(self.stop_whisper)
        self.stop_button.setStyleSheet("background-color: #90e0ef; color: black; border-radius: 8; padding: 10px;")
        button_layout.addWidget(self.stop_button)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_text)
        self.clear_button.setStyleSheet("background-color: #ffc300; color: black; border-radius: 8; padding: 10px;")
        button_layout.addWidget(self.clear_button)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_text)
        self.save_button.setStyleSheet("background-color: #90e0ef; color: black; border-radius: 8; padding: 10px;")
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.recognized_text = ""
        self.listening = False
        self.whisper_thread = None

        # Initially hide the buttons
        self.start_button.hide()
        self.stop_button.hide()
        self.clear_button.hide()
        self.save_button.hide()

    def show_whisper_interface(self):
        # Hide the input language and translation language selection
        self.input_lang_label.hide()
        self.input_lang_combo.hide()
        self.translation_lang_label.hide()
        self.translation_lang_combo.hide()

        # Hide the "Get Started" button
        self.get_started_button.hide()

        # Show the rest of the interface
        self.text_box.show()
        self.start_button.show()
        self.stop_button.show()
        self.clear_button.show()
        self.save_button.show()

    def start_whisper(self):
        try:
            input_lang = self.input_lang_combo.currentText()
            translation_lang = self.translation_lang_combo.currentText()
            self.recognized_text = ""  # Clear recognized text
            self.text_box.clear()  # Clear text box
            self.whisper_thread = WhisperThread(input_lang, translation_lang)
            self.whisper_thread.running = True
            self.whisper_thread.start()
            self.listening = True
            self.stop_button.setDisabled(False)
            self.start_button.setDisabled(True)
            self.status_label.setText("Listening...")
        except Exception as e:
            print(f"An error occurred: {e}")

    def stop_whisper(self):
        try:
            self.whisper_thread.running = False
            self.whisper_thread.wait()
            self.listening = False
            self.status_label.setText("Recognition stopped.")
            self.start_button.setDisabled(False)q
            self.stop_button.setDisabled(True)
        except Exception as e:
            print(f"An error occurred: {e}")

    def clear_text(self):
        self.text_box.clear()
        self.recognized_text = ""  # Clear recognized text

    def save_text(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)")
            if file_path:
                with open(file_path, "w") as file:
                    file.write(self.recognized_text)
        except Exception as e:
            print(f"An error occurred: {e}")

    def update_text_real_time(self, text):
        cursor = self.text_box.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + " ")
        self.text_box.setTextCursor(cursor)
        self.text_box.ensureCursorVisible()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperGUI()
    window.show()
    sys.exit(app.exec_())
