import socket
import threading
import pickle

HOST = '192.168.100.160'
PORT = 5555

# Sử dụng UDP thay vì TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("[STARTING] Server is starting...")

clients = []
roles = {}

def handle_data(data, addr):
    global clients, roles

    if addr not in clients:
        # Thêm client mới và phân vai
        clients.append(addr)
        if len(clients) == 1:
            roles[addr] = "left"
            server_socket.sendto(pickle.dumps({"role": "left"}), addr)
        elif len(clients) == 2:
            roles[addr] = "right"
            for client in clients:
                server_socket.sendto(pickle.dumps({"start": True}), client)
        else:
            server_socket.sendto(pickle.dumps("Game is full"), addr)
            return

    # Gửi dữ liệu cho các client khác
    received_data = pickle.loads(data)
    for client in clients:
        if client != addr:
            server_socket.sendto(pickle.dumps(received_data), client)

def start_server():
    while True:
        data, addr = server_socket.recvfrom(1024)
        threading.Thread(target=handle_data, args=(data, addr)).start()

start_server()
