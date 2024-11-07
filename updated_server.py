
import socket
import threading
import pickle
HOST = '192.168.100.234'
PORT = 5555
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
print("[STARTING] Server is starting...")
clients = []
roles = {}
def handle_client(conn, addr):
    global clients, roles
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)
    if len(clients) == 1:
        roles[conn] = "left"
        conn.sendall(pickle.dumps({"role": "left"}))
    elif len(clients) == 2:
        roles[conn] = "right"
        conn.sendall(pickle.dumps({"role": "right", "start": True}))
        for client in clients:
            try:
                client.sendall(pickle.dumps({"start": True}))
            except:
                client.close()
                clients.remove(client)
    else:
        conn.sendall(pickle.dumps("Game is full"))
        conn.close()
        return
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            received_data = pickle.loads(data)
            for client in clients:
                if client != conn:
                    try:
                        client.sendall(pickle.dumps(received_data))
                    except:
                        client.close()
                        clients.remove(client)
        except:
            break
    print(f"[DISCONNECT] {addr} disconnected.")
    conn.close()
    if conn in clients:
        clients.remove(conn)
        roles.pop(conn, None)
def start_server():
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
start_server()
