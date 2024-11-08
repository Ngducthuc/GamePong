import socket
import threading
import pickle
import time

# Server configuration
HOST = '192.168.88.151'
PORT = 5555
WIDTH, HEIGHT = 800, 600
paddle_width, paddle_height = 10, 100
ball_radius = 10
goal_width = 10
goal_height = HEIGHT // 3

# Initial positions and scores
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5
score_left = 0
score_right = 0
paddle1_y = HEIGHT // 2
paddle2_y = HEIGHT // 2

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
clients = []
roles = {}
is_game_ready = False
game_over = False

def broadcast_data(data):
    """Send data to all connected clients."""
    for client in clients:
        client.sendall(pickle.dumps(data))

def handle_ball_movement():
    """Handles ball movement, collision detection, and scoring."""
    global ball_x, ball_y, ball_dx, ball_dy, score_left, score_right, game_over
    while True:
        if is_game_ready and not game_over: 
            # Update ball position
            ball_x += ball_dx
            ball_y += ball_dy

            # Ball collision with top and bottom walls
            if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
                ball_dy *= -1

            # Ball collision with paddles
            if (20 <= ball_x <= 30 and paddle1_y <= ball_y <= paddle1_y + paddle_height) or \
               (WIDTH - 30 <= ball_x <= WIDTH - 20 and paddle2_y <= ball_y <= paddle2_y + paddle_height):
                ball_dx *= -1

            # Ball out of bounds (goal)
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

            # Check if game is over
            check_game_over()

            # Send updated game state to clients
            broadcast_data({
                "ball_x": ball_x,
                "ball_y": ball_y,
                "score_left": score_left,
                "score_right": score_right
            })

        time.sleep(0.03)

def check_game_over():
    """Check if either player has reached 10 points."""
    global game_over
    if score_left >= 10 or score_right >= 10:
        game_over = True
        broadcast_data({"game_over": True, "winner": "left" if score_left >= 10 else "right"})

def check_game_ready():
    """Checks if there are enough players to start the game."""
    global is_game_ready
    if len(clients) == 2:
        is_game_ready = True
        for client in clients:
            client.sendall(pickle.dumps({"game_ready": True}))
    else:
        is_game_ready = False

def reset_ball():
    """Resets the ball to the center and reverses its direction."""
    global ball_x, ball_y, ball_dx
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx *= -1

def handle_client(conn, addr):
    """Handles each client's connection and game data."""
    global clients, roles, paddle1_y, paddle2_y
    print(f"[NEW CONNECTION] {addr} connected.")
    
    if len(clients) < 2:
        clients.append(conn)
        
        if len(clients) == 1:
            roles[conn] = "left"
            conn.sendall(pickle.dumps({"role": "left"}))
        elif len(clients) == 2:
            roles[conn] = "right"
            conn.sendall(pickle.dumps({"role": "right"}))
        
        check_game_ready()

    else:
        conn.sendall(pickle.dumps("Game is full"))
        conn.close()
        return

    while True:
        try:
            data = conn.recv(2048)
            if not data:
                break
            received_data = pickle.loads(data)

            # Update paddle positions
            if roles[conn] == "left":
                paddle1_y = received_data.get("paddle1_y", paddle1_y)
            elif roles[conn] == "right":
                paddle2_y = received_data.get("paddle2_y", paddle2_y)

            # Send the updated paddle positions to other clients
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
        check_game_ready()

def start_server():
    """Starts the server and listens for client connections."""
    print("[STARTING] Server is starting...")
    threading.Thread(target=handle_ball_movement, daemon=True).start()
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
