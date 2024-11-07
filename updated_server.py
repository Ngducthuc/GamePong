import socket
import threading
import pickle
import time

HOST = '192.168.100.234'
PORT = 5555
WIDTH, HEIGHT = 800, 600
paddle_width, paddle_height = 10, 100
ball_radius = 10
goal_width = 10
goal_height = HEIGHT // 3
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5
score_left = 0
score_right = 0

paddle1_y = HEIGHT // 2
paddle2_y = HEIGHT // 2

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
clients = []
roles = {}

def broadcast_data(data):
    """Sends data to all connected clients."""
    for client in clients:
        client.sendall(pickle.dumps(data))
def handle_ball_movement():
    """Handles ball movement, collision detection, and scoring."""
    global ball_x, ball_y, ball_dx, ball_dy, score_left, score_right
    while True:
        ball_x += ball_dx
        ball_y += ball_dy

        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
            ball_dy *= -1

        if (20 <= ball_x <= 30 and paddle1_y <= ball_y <= paddle1_y + paddle_height) or \
           (WIDTH - 30 <= ball_x <= WIDTH - 20 and paddle2_y <= ball_y <= paddle2_y + paddle_height):
            ball_dx *= -1

        if ball_x - ball_radius <= 0:
            if HEIGHT // 2 - goal_height // 2 <= ball_y <= HEIGHT // 2 + goal_height // 2:
                score_right += 1
                reset_ball()
            else:
                ball_dx *= -1
        elif ball_x + ball_radius >= WIDTH:
            if HEIGHT // 2 - goal_height // 2 <= ball_y <= HEIGHT // 2 + goal_height // 2:
                score_left += 1
                reset_ball()
            else:
                ball_dx *= -1

        broadcast_data({
            "ball_x": ball_x,
            "ball_y": ball_y,
            "score_left": score_left,
            "score_right": score_right
        })

        time.sleep(0.03)
def reset_ball():
    """Resets the ball to the center and reverses its direction."""
    global ball_x, ball_y, ball_dx
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx *= -1

def handle_client(conn, addr):
    global clients, roles, paddle1_y, paddle2_y
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

            if "paddle1_y" in received_data:
                paddle1_y = received_data["paddle1_y"]
            elif "paddle2_y" in received_data:
                paddle2_y = received_data["paddle2_y"]

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
    threading.Thread(target=handle_ball_movement, daemon=True).start()
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
