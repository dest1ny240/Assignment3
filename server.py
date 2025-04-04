import socket
import threading

clients = {}
channels = {}

def broadcast(message, sender_socket, channel=None):
    if channel:
        for client in channels.get(channel, []):
            if client != sender_socket:
                client.send(message.encode())
    else:
        for client in clients.values():
            if client != sender_socket:
                client.send(message.encode())

def handle_client(client_socket, address):
    try:
        client_socket.send("Enter your nickname: ".encode())
        nickname = client_socket.recv(1024).decode().strip()
        clients[nickname] = client_socket
        print(f"{nickname} connected from {address}")
        client_socket.send("Connect success! Use /join [channel] to join a channel, /pm [user] [message] to send private messages.\n".encode())

        while True:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break

            if msg.startswith("/join "):
                channel = msg.split(" ", 1)[1].strip()
                if channel not in channels:
                    channels[channel] = []
                if client_socket not in channels[channel]:
                    channels[channel].append(client_socket)
                client_socket.send(f"You have joined the channel: {channel}\n".encode())

            elif msg.startswith("/pm "):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    client_socket.send("Invalid format. Use: /pm [user] [message]\n".encode())
                    continue
                recipient_name, private_msg = parts[1], parts[2]
                recipient_socket = clients.get(recipient_name)
                if recipient_socket:
                    recipient_socket.send(f"[Private] {nickname}: {private_msg}\n".encode())
                else:
                    client_socket.send(f"User '{recipient_name}' not found.\n".encode())

            else:
                sent = False
                for channel_name, members in channels.items():
                    if client_socket in members:
                        broadcast(f"[{channel_name}] {nickname}: {msg}", client_socket, channel_name)
                        sent = True
                        break
                if not sent:
                    broadcast(f"{nickname}: {msg}", client_socket)

    except Exception as e:
        print(f"Error with client {address}: {e}")
    finally:
        print(f"{nickname} disconnected")
        clients.pop(nickname, None)
        for ch in channels.values():
            if client_socket in ch:
                ch.remove(client_socket)
        client_socket.close()

def start_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 7788))
        server.listen()
        print("Server is running on port 7788...") 
    except Exception as e:
        print(f"Error starting server: {e}") 

    while True:
        try:
            client_socket, address = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, address), daemon=True).start()
        except Exception as e:
            print(f"Error accepting connection: {e}")  


if __name__ == "__main__":
    start_server()
