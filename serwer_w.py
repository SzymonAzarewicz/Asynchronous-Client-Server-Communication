import socket
import threading
from PIL import Image
import json
import base64
import io

class Client:
    def __init__(self, socket, address, name=None):
        self.socket = socket
        self.address = address
        self.name = name or f"Klient_{address[1]}"

clients = []

def broadcast(message, sender=None):
    """Wysyła wiadomość do wszystkich klientów oprócz nadawcy"""
    for client in clients:
        if client != sender:
            try:
                client.socket.send(message)
            except:
                remove_client(client)

def remove_client(client):
    """Usuwa klienta z listy"""
    if client in clients:
        clients.remove(client)
        print(f"Klient {client.name} rozłączony.")

def image_to_ascii(image_data, width):
    """Convert an image to ASCII art with dynamic sizing"""
    try:
        # Decode base64 image data
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get original dimensions
        orig_width, orig_height = image.size
        
        # Calculate proportional height
        aspect_ratio = orig_height / orig_width
        height = int(aspect_ratio * width * 0.5)  # Multiply by 0.5 to account for character aspect ratio
        
        # Resize image
        image = image.resize((width, height))
        image = image.convert('L')
        
        # Define ASCII characters from dark to light
        chars = '@%#*+=-:. '
        
        # Convert pixels to ASCII
        ascii_str = ""
        for y in range(height):
            for x in range(width):
                pixel_value = image.getpixel((x, y))
                char_idx = int(pixel_value * (len(chars)-1) / 255)
                ascii_str += chars[char_idx]
            ascii_str += "\n"
        
        return ascii_str
    except Exception as e:
        return f"Błąd konwersji: {str(e)}"

def handle_client(client):
    while True:
        try:
            data = client.socket.recv(1024000)  # Increased buffer size for image data
            if not data:
                break
            
            try:
                request = json.loads(data.decode())
                client_name = request.get('client_name', client.name)
                
                if request.get('type') == 'image_to_ascii' and 'image_data' in request:
                    # Process image to ASCII conversion
                    width = request.get('width', 60)
                    ascii_art = image_to_ascii(request['image_data'], width)
                    
                    # Print ASCII art on server
                    print(f"\nOtrzymano żądanie konwersji obrazu od {client_name}. Wynik:")
                    print(ascii_art)
                    
                    # Send the ASCII art back to client
                    response = json.dumps({'type': 'ascii_response', 'data': ascii_art})
                    client.socket.send(response.encode())
                
                elif request.get('type') == 'text':
                    # Handle text message
                    message = request.get('message', '')
                    print(f"\nOdebrano od {client_name}: {message}")
                    response = json.dumps({
                        'type': 'text',
                        'message': f"Wiadomość od {client_name}: {message}"
                    })
                    broadcast(response.encode(), client)
                    
                else:
                    # Normal echo behavior
                    print(f"\nOdebrano od {client_name}: {data.decode()}")
                    client.socket.send(data)
                    
            except json.JSONDecodeError:
                # Normal text message handling
                print(f"\nOdebrano od {client.name}: {data.decode()}")
                client.socket.send(data)
                
        except Exception as e:
            print(f"Błąd obsługi klienta {client.name}: {str(e)}")
            break
            
    remove_client(client)
    client.socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8888))
    server.listen(5)
    print("Serwer nasłuchuje...")

    while True:
        client_socket, addr = server.accept()
        client = Client(client_socket, addr)
        clients.append(client)
        print(f"Połączono z {client.name} ({addr})")
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

if __name__ == "__main__":
    main()
