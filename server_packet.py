import socket
import os

def broadcast(message, sender_address, clients, server_socket):
    """Broadcasts a message to all clients except the sender."""
    for client in clients:
        if client != sender_address:
            server_socket.sendto(message, client)

def server():
    HOST = 'localhost'
    PORT = 8888
    clients = []
    file_chunks = []
    assembling_file = False

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print("UDP Chat Server Started. Waiting for clients...")

    received_files_dir = 'received_files'
    if not os.path.exists(received_files_dir):
        os.makedirs(received_files_dir)

    while True:
        try:
            message, client_address = server_socket.recvfrom(65536)
            if client_address not in clients:
                clients.append(client_address)
                print(f"New client joined: {client_address}")

            if message.startswith(b"START:"):
                filename = message[len(b"START:"):].decode()
                assembling_file = True
                file_chunks.clear()
                print(f"Starting to receive file: {filename}")

            elif message.startswith(b"END:") and assembling_file:
                filename = message[len(b"END:"):].decode()
                file_path = os.path.join(received_files_dir, filename)
                with open(file_path, "wb") as file:
                    for chunk in file_chunks:
                        file.write(chunk)
                print(f"File received and saved: {file_path}")
                assembling_file = False
                broadcast(f"File {filename} received and saved.".encode(), client_address, clients, server_socket)
                file_chunks.clear()

            elif assembling_file:
                file_chunks.append(message)

            else:
                print(f"Message from {client_address}: {message.decode('utf-8')}")
                broadcast(message, client_address, clients, server_socket)

        except KeyboardInterrupt:
            print("\nServer is shutting down.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    server_socket.close()

if __name__ == "__main__":
    server()
