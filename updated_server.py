import socket
import threading
import pickle

HOST = '192.168.100.234'
PORT = 5555
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

clients = []
roles = {}

def start_server():
    global clients, roles
    print("[STARTING] Server is starting...")
    while True:
        data, addr = server_socket.recvfrom(1024)
        if addr not in clients and len(clients) < 2:
            clients.append(addr)
            role = "left" if len(clients) == 1 else "right"
            server_socket.sendto(pickle.dumps({"role": role, "start": len(clients) == 2}), addr)
            roles[addr] = role
            if len(clients) == 2:
                for client in clients:
                    server_socket.sendto(pickle.dumps({"start": True}), client)
        elif addr in clients:
            received_data = pickle.loads(data)
            for client in clients:
                if client != addr:
                    server_socket.sendto(pickle.dumps(received_data), client)
        else:
            server_socket.sendto(pickle.dumps("Game is full"), addr)

start_server()
