import socket
import threading
import json
import os
import shutil
import base64
from PIL import Image
import io
from tkinter import Tk, filedialog

def receive_messages(client, client_name):
    while True:
        try:
            response = client.recv(4096)
            if not response:
                break
                
            try:
                json_response = json.loads(response.decode())
                if json_response.get('type') == 'ascii_response':
                    print("\nOdpowiedź serwera dla", client_name + ":")
                    print(json_response.get('data', 'No data received'))
                elif json_response.get('type') == 'docx_response':
                    print(f"\nOdpowiedź serwera dla {client_name}: {json_response.get('message', 'Brak wiadomości')}")
                else:
                    print(f"\nOdpowiedź serwera dla {client_name}: {json_response}")
            except json.JSONDecodeError:
                print(f"\nOdpowiedź serwera dla {client_name}: {response.decode()}")
        except Exception as e:
            print(f"Błąd odbioru dla {client_name}: {str(e)}")
            break

def send_image_request(client, image_path, width, client_name):
    if not os.path.exists(image_path):
        print(f"Błąd: Plik {image_path} nie istnieje.")
        return
        
    try:
        # Read and encode the image
        with open(image_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            
        request = {
            'type': 'image_to_ascii',
            'image_data': img_data,
            'width': width,
            'client_name': client_name
        }
        client.send(json.dumps(request).encode())
        print(f"Wysłano żądanie konwersji obrazu od {client_name}: {image_path}")
    except Exception as e:
        print(f"Błąd wysyłania dla {client_name}: {str(e)}")

def send_docx_file(client, client_name):
    # Ukryj główne okno Tk
    root = Tk()
    root.withdraw()
    
    # Otwórz okno wyboru pliku
    file_path = filedialog.askopenfilename(
        title="Wybierz plik DOCX",
        filetypes=[("Dokumenty Word", "*.docx")]
    )
    
    root.destroy()
    
    if not file_path:
        print("Anulowano wybór pliku.")
        return
        
    if not os.path.exists(file_path):
        print(f"Błąd: Plik {file_path} nie istnieje.")
        return
        
    try:
        # Odczytaj i zakoduj plik
        with open(file_path, 'rb') as docx_file:
            file_data = base64.b64encode(docx_file.read()).decode()
            
        file_name = os.path.basename(file_path)
        
        request = {
            'type': 'docx_file',
            'file_data': file_data,
            'file_name': file_name,
            'client_name': client_name
        }
        
        # Podziel na mniejsze części, jeśli plik jest duży
        json_data = json.dumps(request)
        client.send(json_data.encode())
        print(f"Wysłano plik DOCX: {file_name} od {client_name}")
    except Exception as e:
        print(f"Błąd wysyłania pliku dla {client_name}: {str(e)}")

def send_message(client, client_name):
    while True:
        print(f"\n[{client_name}] Wybierz opcję:")
        print("1. Wyślij wiadomość tekstową")
        print("2. Konwertuj obraz na ASCII art")
        print("3. Wyślij plik DOCX")
        
        choice = input(f"[{client_name}] Twój wybór (1/2/3): ")
        
        if choice == '1':
            message = input(f"[{client_name}] Wpisz wiadomość: ")
            request = {
                'type': 'text',
                'message': message,
                'client_name': client_name
            }
            client.send(json.dumps(request).encode())
        elif choice == '2':
            image_path = 'emoji.png'
            try:
                term_width = (shutil.get_terminal_size().columns * 2) // 3
            except:
                term_width = 60
                
            width_input = input(f"[{client_name}] Podaj szerokość ASCII art (domyślnie {term_width}): ")
            width = int(width_input) if width_input.isdigit() else term_width
            send_image_request(client, image_path, width, client_name)
        elif choice == '3':
            send_docx_file(client, client_name)
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8888))

    client_name = input("Podaj swoją nazwę: ")
    print(f"Połączono jako: {client_name}")

    receive_thread = threading.Thread(target=receive_messages, args=(client, client_name))
    receive_thread.start()

    send_message(client, client_name)

if __name__ == "__main__":
    main()
