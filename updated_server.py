import socket
import threading
import pickle
import time

HOST = '192.168.100.234'
PORT = 5555
WIDTH, HEIGHT = 800, 600
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5
goal_height = HEIGHT // 3
paddle1_y = HEIGHT // 2  # Initialize paddle1 position
paddle2_y = HEIGHT // 2  # Initialize paddle2 position
clients = []
roles = {}
score_left = 0
score_right = 0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)

def handle_client(conn, addr):
    global clients, roles, paddle1_y, paddle2_y, score_left, score_right
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

            # Update paddle positions based on client role
            if "paddle1_y" in received_data:
                paddle1_y = received_data["paddle1_y"]
                broadcast({"paddle1_y": paddle1_y}, conn)
            if "paddle2_y" in received_data:
                paddle2_y = received_data["paddle2_y"]
                broadcast({"paddle2_y": paddle2_y}, conn)

            # Update scores and broadcast them
            if "score_left" in received_data and "score_right" in received_data:
                score_left = received_data["score_left"]
                score_right = received_data["score_right"]
                broadcast({"score_left": score_left, "score_right": score_right})
        except:
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    conn.close()
    if conn in clients:
        clients.remove(conn)
        roles.pop(conn, None)

def broadcast(message, sender_conn=None):
    for client in clients:
        if client != sender_conn:
            client.sendall(pickle.dumps(message))

def update_ball_position():
    global ball_x, ball_y, ball_dx, ball_dy, score_left, score_right, paddle1_y, paddle2_y
    while True:
        ball_x += ball_dx
        ball_y += ball_dy

        # Ball collision with top and bottom walls
        if ball_y - 10 <= 0 or ball_y + 10 >= HEIGHT:
            ball_dy *= -1

        # Ball collision with paddles
        if (20 <= ball_x <= 30 and paddle1_y <= ball_y <= paddle1_y + 100) or \
           (WIDTH - 30 <= ball_x <= WIDTH - 20 and paddle2_y <= ball_y <= paddle2_y + 100):
            ball_dx *= -1

        # Ball goes out of bounds on the left side
        if ball_x - 10 <= 0:
            if HEIGHT // 2 - goal_height // 2 <= ball_y <= HEIGHT // 2 + goal_height // 2:
                score_right += 1
                reset_ball()
            else:
                ball_dx *= -1

        # Ball goes out of bounds on the right side
        elif ball_x + 10 >= WIDTH:
            if HEIGHT // 2 - goal_height // 2 <= ball_y <= HEIGHT // 2 + goal_height // 2:
                score_left += 1
                reset_ball()
            else:
                ball_dx *= -1

        # Send updated ball position and scores to clients
        broadcast({"ball_x": ball_x, "ball_y": ball_y, "score_left": score_left, "score_right": score_right})
        time.sleep(1/60)

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx *= -1

def start_server():
    print("[STARTING] Server is starting...")
    threading.Thread(target=update_ball_position, daemon=True).start()
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
