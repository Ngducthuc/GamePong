import socket
import threading
import pickle

HOST = '192.168.100.234'
PORT = 5555
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)

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
            client.sendall(pickle.dumps({"start": True}))
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

            # Broadcast the updated score to all clients
            if "score_left" in received_data and "score_right" in received_data:
                for client in clients:
                    client.sendall(pickle.dumps({
                        "score_left": received_data["score_left"],
                        "score_right": received_data["score_right"]
                    }))

            # Forward other data to all clients except the sender
            for client in clients:
                if client != conn:
                    client.sendall(pickle.dumps(received_data))

        except:
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    conn.close()
    if conn in clients:
        clients.remove(conn)
        roles.pop(conn, None)

def start_server():
    print("[STARTING] Server is starting...")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
