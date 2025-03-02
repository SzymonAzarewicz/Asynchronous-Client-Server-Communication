import socket
import threading
import json
import os
import base64
from PIL import Image
import io
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QTextEdit, QLineEdit, QLabel, QFileDialog,
                              QComboBox, QInputDialog, QSpinBox, QMessageBox, QSplitter,
                              QScrollBar)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont, QTextCursor

class ClientThread(QThread):
    message_received = Signal(dict)
    connection_error = Signal(str)
    
    def __init__(self, host, port, client_name):
        super().__init__()
        self.host = host
        self.port = port
        self.client_name = client_name
        self.client = None
        self.running = True
        
    def run(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            
            while self.running:
                try:
                    response = self.client.recv(4096)
                    if not response:
                        break
                        
                    try:
                        json_response = json.loads(response.decode())
                        self.message_received.emit(json_response)
                    except json.JSONDecodeError:
                        self.message_received.emit({
                            'type': 'text',
                            'message': response.decode()
                        })
                except Exception as e:
                    self.connection_error.emit(f"Błąd odbioru: {str(e)}")
                    break
        except Exception as e:
            self.connection_error.emit(f"Błąd połączenia: {str(e)}")
        
    def send_message(self, message_type, data):
        if not self.client:
            return False
            
        try:
            request = {
                'type': message_type,
                'client_name': self.client_name,
                **data
            }
            self.client.send(json.dumps(request).encode())
            return True
        except Exception as e:
            self.connection_error.emit(f"Błąd wysyłania: {str(e)}")
            return False
            
    def send_text_message(self, message):
        return self.send_message('text', {'message': message})
    
    def send_image_request(self, image_path, width):
        if not os.path.exists(image_path):
            self.connection_error.emit(f"Błąd: Plik {image_path} nie istnieje.")
            return False
            
        try:
            with open(image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                
            return self.send_message('image_to_ascii', {
                'image_data': img_data,
                'width': width
            })
        except Exception as e:
            self.connection_error.emit(f"Błąd wysyłania obrazu: {str(e)}")
            return False
    
    def send_docx_file(self, file_path):
        if not os.path.exists(file_path):
            self.connection_error.emit(f"Błąd: Plik {file_path} nie istnieje.")
            return False
            
        try:
            with open(file_path, 'rb') as docx_file:
                file_data = base64.b64encode(docx_file.read()).decode()
                
            file_name = os.path.basename(file_path)
            
            return self.send_message('docx_file', {
                'file_data': file_data,
                'file_name': file_name
            })
        except Exception as e:
            self.connection_error.emit(f"Błąd wysyłania pliku: {str(e)}")
            return False
    
    def stop(self):
        self.running = False
        if self.client:
            try:
                self.client.close()
            except:
                pass


class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client_thread = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Klient GUI")
        self.resize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        connection_layout = QHBoxLayout()
        self.host_input = QLineEdit("localhost")
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(8888)
        self.name_input = QLineEdit()
        self.connect_button = QPushButton("Połącz")
        
        connection_layout.addWidget(QLabel("Host:"))
        connection_layout.addWidget(self.host_input)
        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_input)
        connection_layout.addWidget(QLabel("Nazwa:"))
        connection_layout.addWidget(self.name_input)
        connection_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(connection_layout)
        
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter, 1)
        
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        fixed_font = QFont("Courier New")
        fixed_font.setStyleHint(QFont.Monospace)
        self.messages_area.setFont(fixed_font)
        self.messages_area.setLineWrapMode(QTextEdit.NoWrap)
        self.messages_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        splitter.addWidget(self.messages_area)
        
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        splitter.addWidget(control_widget)
        
        message_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_message_button = QPushButton("Wyślij")
        
        message_layout.addWidget(QLabel("Wiadomość:"))
        message_layout.addWidget(self.message_input, 1)
        message_layout.addWidget(self.send_message_button)
        
        control_layout.addLayout(message_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.send_image_button = QPushButton("Konwersja pliku do ASCII-art")
        self.send_docx_button = QPushButton("Wyślij plik DOCX")
        self.clear_button = QPushButton("Wyczyść wiadomości")
        
        buttons_layout.addWidget(self.send_image_button)
        buttons_layout.addWidget(self.send_docx_button)
        buttons_layout.addWidget(self.clear_button)
        
        control_layout.addLayout(buttons_layout)
        
        self.connect_button.clicked.connect(self.connect_to_server)
        self.send_message_button.clicked.connect(self.send_text_message)
        self.message_input.returnPressed.connect(self.send_text_message)
        self.send_image_button.clicked.connect(self.send_image)
        self.send_docx_button.clicked.connect(self.send_docx)
        self.clear_button.clicked.connect(self.clear_messages)
        
        self.toggle_controls(False)
        self.statusBar().showMessage("Nie połączono")
        
    def toggle_controls(self, enabled):
        self.message_input.setEnabled(enabled)
        self.send_message_button.setEnabled(enabled)
        self.send_image_button.setEnabled(enabled)
        self.send_docx_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        
        self.host_input.setEnabled(not enabled)
        self.port_input.setEnabled(not enabled)
        self.name_input.setEnabled(not enabled)
        self.connect_button.setText("Rozłącz" if enabled else "Połącz")
        
    def connect_to_server(self):
        if not self.client_thread:
            host = self.host_input.text()
            port = self.port_input.value()
            name = self.name_input.text()
            
            if not name:
                QMessageBox.warning(self, "Błąd", "Proszę podać nazwę klienta")
                return
                
            self.client_thread = ClientThread(host, port, name)
            self.client_thread.message_received.connect(self.handle_message)
            self.client_thread.connection_error.connect(self.handle_error)
            self.client_thread.start()
            
            self.statusBar().showMessage(f"Połączono jako: {name} do {host}:{port}")
            self.toggle_controls(True)
            self.log_message("System", f"Połączono do serwera jako: {name}")
        else:
            self.client_thread.stop()
            self.client_thread.wait()
            self.client_thread = None
            
            self.statusBar().showMessage("Nie połączono")
            self.toggle_controls(False)
            self.log_message("System", "Rozłączono od serwera")
            
    def send_text_message(self):
        if not self.client_thread:
            return
            
        message = self.message_input.text()
        if not message:
            return
            
        success = self.client_thread.send_text_message(message)
        if success:
            self.log_message(self.client_thread.client_name, message)
            self.message_input.clear()
            
    def send_image(self):
        if not self.client_thread:
            return
            
        file_path = 'emoji.png'
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Błąd", f"Plik {file_path} nie istnieje.")
            return
            
        try:
            with Image.open(file_path) as img:
                img_width, img_height = img.size
                suggested_width = min(120, img_width // 2)
        except:
            suggested_width = 60
            
        width, ok = QInputDialog.getInt(
            self, 
            "Podaj szerokość ASCII art", 
            "Szerokość:", 
            suggested_width, 20, 200
        )
        
        if not ok:
            return
            
        success = self.client_thread.send_image_request(file_path, width)
        if success:
            self.log_message("System", f"Wysłano żądanie konwersji obrazu: {os.path.basename(file_path)}")
            
    def send_docx(self):
        if not self.client_thread:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik DOCX",
            "",
            "Dokumenty Word (*.docx)"
        )
        
        if not file_path:
            return
            
        success = self.client_thread.send_docx_file(file_path)
        if success:
            self.log_message("System", f"Wysłano plik DOCX: {os.path.basename(file_path)}")
            
    def handle_message(self, response):
        response_type = response.get('type', '')
        
        if response_type == 'ascii_response':
            ascii_art = response.get('data', '')
            self.log_message("Serwer", "ASCII Art:", is_ascii=True)
            cursor = self.messages_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.messages_area.setTextCursor(cursor)
            self.messages_area.insertPlainText("\n" + ascii_art + "\n")
        elif response_type == 'docx_response':
            message = response.get('message', '')
            self.log_message("Serwer", message)
        elif response_type == 'text':
            message = response.get('message', '')
            self.log_message("Serwer", message)
        else:
            self.log_message("Serwer", str(response))
            
    def handle_error(self, error_message):
        self.log_message("Błąd", error_message, is_error=True)
        
    def log_message(self, sender, message, is_error=False, is_ascii=False):
        cursor = self.messages_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.messages_area.setTextCursor(cursor)
        
        if is_ascii:
            self.messages_area.append(f"<b>[{sender}]:</b>")
            return
            
        if is_error:
            self.messages_area.append(f"<span style='color: red'><b>[{sender}]:</b> {message}</span>")
        else:
            self.messages_area.append(f"<b>[{sender}]:</b> {message}")
            
    def clear_messages(self):
        self.messages_area.clear()
        self.log_message("System", "Wyczyszczono historię wiadomości")
        
    def closeEvent(self, event):
        if self.client_thread:
            self.client_thread.stop()
            self.client_thread.wait()
        event.accept()


def main():
    app = QApplication([])
    window = ClientGUI()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
