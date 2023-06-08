import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt  # Importação adicionada
from pydub import AudioSegment
import speech_recognition as sr
import re
import shutil

class AudioToTextConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor de Áudio para Texto")
        self.setGeometry(200, 200, 600, 400)

        self.audio_file = ""
        self.full_text = ""

        self.lbl_status = QLabel(self)
        self.lbl_status.setGeometry(50, 20, 500, 30)
        self.lbl_status.setText("Selecione um arquivo de áudio")

        self.btn_select_audio = QPushButton("Selecionar Áudio", self)
        self.btn_select_audio.setGeometry(30, 70, 130, 30)
        self.btn_select_audio.clicked.connect(self.select_audio)

        self.txt_audio_path = QLineEdit(self)
        self.txt_audio_path.setGeometry(160, 70, 400, 30)

        self.btn_convert = QPushButton("Converter", self)
        self.btn_convert.setGeometry(140, 120, 120, 30)
        self.btn_convert.clicked.connect(self.convert_audio)

        self.txt_result = QTextEdit(self)
        self.txt_result.setGeometry(30, 170, 540, 200)

        self.lbl_signature = QLabel("by guiferreira", self)
        self.lbl_signature.setGeometry(0, 370, 600, 30)
        self.lbl_signature.setAlignment(Qt.AlignCenter)

    def select_audio(self):
        self.audio_file, _ = QFileDialog.getOpenFileName(self, "Selecionar Áudio", "", "Audio Files (*.mp3 *.wav *.mp4 *.m4a)")
        self.txt_audio_path.setText(self.audio_file)
        self.lbl_status.setText(f"Arquivo selecionado: {os.path.basename(self.audio_file)}")

    def convert_audio(self):
        self.audio_file = self.txt_audio_path.text()
        if self.audio_file:
            output_path = os.path.dirname(self.audio_file)
            audio_filename = os.path.basename(self.audio_file)

            audio_folder = os.path.join(output_path, "audios")
            if not os.path.exists(audio_folder):
                os.makedirs(audio_folder)

            split_audio(self.audio_file, audio_folder)

            self.full_text = ""
            audio_parts = sorted([filename for filename in os.listdir(audio_folder) if filename.endswith((".mp3", ".wav", ".mp4", ".m4a"))], key=numeric_part)
            for filename in audio_parts:
                part_audio_file = os.path.join(audio_folder, filename)
                wav_audio_file = convert_to_wav(part_audio_file)
                part_text = convert_audio_to_text(wav_audio_file)
                self.full_text += part_text + " "

            self.full_text = format_text(self.full_text)
            self.txt_result.setText(self.full_text)

            clear_audio_folder(audio_folder)

            self.lbl_status.setText("Conversão concluída!")

        else:
            self.lbl_status.setText("Nenhum arquivo de áudio selecionado.")

def numeric_part(text):
    return int(re.search(r'\d+', text).group())

def split_audio(input_file, output_path):
    audio = AudioSegment.from_file(input_file)
    duration = len(audio) // 1000  # duração em segundos

    for i in range(0, duration, 60):  # dividir em partes de 1 minuto
        start_time = i * 1000
        end_time = (i + 60) * 1000
        part = audio[start_time:end_time]
        part.export(f"{output_path}/part{i}.wav", format="wav")

def convert_to_wav(audio_file):
    wav_audio_file = os.path.splitext(audio_file)[0] + ".wav"
    audio = AudioSegment.from_file(audio_file)
    audio.export(wav_audio_file, format="wav")
    return wav_audio_file

def convert_audio_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
        text = r.recognize_google(audio, language="pt-BR")
        return text

def format_text(text):
    # Adiciona pontuação e parágrafos adequados
    text = text.replace(" .", ".").replace(" ,", ",").replace(" ?", "?").replace(" !", "!").replace(" :", ":").replace(" ;", ";")
    text = text.replace(". ", ".\n\n").replace("? ", "?\n\n").replace("! ", "!\n\n")
    text = text.replace("\n.", ".\n").replace("\n?", "?\n").replace("\n!", "!\n")
    text = text.strip()

    return text

def clear_audio_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    shutil.rmtree(folder_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioToTextConverter()
    window.show()
    sys.exit(app.exec_())
