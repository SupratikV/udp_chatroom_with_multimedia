import socket
import threading
import os

def listen_for_messages(sock):
    while True:
        try:
            message, _ = sock.recvfrom(4096)  # Adjust buffer size if necessary for larger messages
            print(message.decode('utf-8'))
        except OSError:
            break  # Exit the loop if the socket is closed.

def send_file(sock, filepath, server_address):
    if not os.path.isfile(filepath):
        print("File does not exist.")
        return
    
    filename = os.path.basename(filepath)
    start_marker = f"START:{filename}".encode()
    sock.sendto(start_marker, server_address)  # Signal the start of a file transfer
    
    with open(filepath, "rb") as f:
        chunk = f.read(1024)  # Read the file in chunks
        while chunk:
            sock.sendto(chunk, server_address)
            chunk = f.read(1024)
    
    end_marker = f"END:{filename}".encode()
    sock.sendto(end_marker, server_address)  # Signal the end of the file transfer
    print(f"Sent file: {filename}")

def client():
    HOST = 'localhost'
    PORT = 8888
    server_address = (HOST, PORT)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Start listening for messages in a separate thread
    threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

    username = input("Enter your username: ")
    print("Type your message or type '/sendfile <filepath>' to send a multimedia file.")

    while True:
        message = input("")
        if message.startswith("/sendfile"):
            _, filepath = message.split(" ", 1)
            send_file(client_socket, filepath, server_address)
        else:
            full_message = f"{username}: {message}".encode('utf-8')
            client_socket.sendto(full_message, server_address)

if __name__ == "__main__":
    client()
