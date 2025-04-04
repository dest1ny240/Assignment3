import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except:
            print("Disconnected from server.")
            break

def start_client():
    server_ip = input("Enter server IP address: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 5555))

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        msg = input()
        if msg.lower() == "/exit":
            client_socket.close()
            break
        client_socket.send(msg.encode())

if __name__ == "__main__":
    start_client()
