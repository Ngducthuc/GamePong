import socket
import threading
import pickle
import time

# Server IP và Port
HOST = '192.168.100.234'
PORT = 5555

# Khởi tạo Socket và các biến
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
clients = []
roles = {}

# Kích thước màn hình và biến cần thiết cho trò chơi
WIDTH, HEIGHT = 800, 600
paddle_height = 100
ball_radius = 10
goal_height = HEIGHT // 3
paddle1_y = HEIGHT // 2
paddle2_y = HEIGHT // 2

# Biến liên quan đến bóng
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5
score_left = 0
score_right = 0

# Hàm để reset vị trí bóng khi có điểm
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx *= -1  # Đổi hướng bóng

# Hàm để cập nhật vị trí bóng
def update_ball():
    global ball_x, ball_y, ball_dx, ball_dy, score_left, score_right

    # Cập nhật vị trí bóng
    ball_x += ball_dx
    ball_y += ball_dy

    # Xử lý va chạm với tường trên và dưới
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
        ball_dy *= -1

    # Kiểm tra nếu bóng ra khỏi giới hạn bên trái hoặc bên phải
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

    # Gửi vị trí bóng và điểm số cho các client
    send_game_state()

# Hàm để gửi trạng thái trò chơi cho tất cả các client
def send_game_state():
    data = {
        "ball_x": ball_x,
        "ball_y": ball_y,
        "score_left": score_left,
        "score_right": score_right
    }
    message = pickle.dumps(data)
    for client in clients:
        client.sendall(message)

# Hàm xử lý mỗi client
def handle_client(conn, addr):
    global clients, roles
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)

    # Gán vai trò cho client
    if len(clients) == 1:
        roles[conn] = "left"
        conn.sendall(pickle.dumps({"role": "left"}))
    elif len(clients) == 2:
        roles[conn] = "right"
        conn.sendall(pickle.dumps({"role": "right", "start": True}))
        # Bắt đầu trò chơi khi đủ 2 người chơi
        for client in clients:
            client.sendall(pickle.dumps({"start": True}))
    else:
        conn.sendall(pickle.dumps("Game is full"))
        conn.close()
        return

    # Lắng nghe dữ liệu từ client
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            received_data = pickle.loads(data)

            # Nhận vị trí của các thanh trượt từ client và gửi lại cho đối thủ
            if "paddle1_y" in received_data:
                paddle1_y = received_data["paddle1_y"]
            if "paddle2_y" in received_data:
                paddle2_y = received_data["paddle2_y"]

            # Gửi vị trí của thanh trượt và điểm số cho tất cả client
            game_data = {
                "paddle1_y": paddle1_y,
                "paddle2_y": paddle2_y,
                "score_left": score_left,
                "score_right": score_right
            }
            for client in clients:
                client.sendall(pickle.dumps(game_data))
        except:
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    conn.close()
    if conn in clients:
        clients.remove(conn)
        roles.pop(conn, None)

# Luồng chính của server để cập nhật bóng
def ball_update_thread():
    while True:
        time.sleep(1 / 60)  # Tốc độ cập nhật 60 lần/giây
        update_ball()

# Khởi động server
def start_server():
    print("[STARTING] Server is starting...")
    threading.Thread(target=ball_update_thread, daemon=True).start()  # Bắt đầu luồng cập nhật bóng
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
