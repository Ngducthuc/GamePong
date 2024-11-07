import pygame
import socket
import pickle
import threading

SERVER_IP = '192.168.100.160'
SERVER_PORT = 5555

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (30, 30, 60)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

paddle_width, paddle_height = 10, 100
ball_radius = 10
paddle1_y = HEIGHT // 2
paddle2_y = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2

role = None
game_started = False

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()

# Hàm nhận dữ liệu
def receive_data():
    global paddle1_y, paddle2_y, ball_x, ball_y, game_started, role
    while True:
        data, _ = client_socket.recvfrom(1024)
        if not data:
            break
        message = pickle.loads(data)
        if "role" in message:
            role = message["role"]
        if "start" in message:
            game_started = True
        if "paddle1_y" in message:
            paddle1_y = message["paddle1_y"]
        if "paddle2_y" in message:
            paddle2_y = message["paddle2_y"]

# Khởi động luồng nhận dữ liệu
threading.Thread(target=receive_data, daemon=True).start()

def main():
    global paddle1_y, paddle2_y, ball_x, ball_y, game_started, role
    running = True
    while running:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, WHITE, (0, HEIGHT // 2 - 50, 10, 100))
        pygame.draw.rect(screen, WHITE, (WIDTH - 10, HEIGHT // 2 - 50, 10, 100))

        if role == "left":
            pygame.draw.rect(screen, RED, (20, paddle1_y, paddle_width, paddle_height))
            pygame.draw.rect(screen, BLUE, (WIDTH - 30, paddle2_y, paddle_width, paddle_height))
        elif role == "right":
            pygame.draw.rect(screen, BLUE, (WIDTH - 30, paddle2_y, paddle_width, paddle_height))
            pygame.draw.rect(screen, RED, (20, paddle1_y, paddle_width, paddle_height))

        if game_started:
            pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if role == "left":
            if keys[pygame.K_w] and paddle1_y > 0:
                paddle1_y -= 5
                client_socket.sendto(pickle.dumps({"paddle1_y": paddle1_y}), (SERVER_IP, SERVER_PORT))
            if keys[pygame.K_s] and paddle1_y < HEIGHT - paddle_height:
                paddle1_y += 5
                client_socket.sendto(pickle.dumps({"paddle1_y": paddle1_y}), (SERVER_IP, SERVER_PORT))
        elif role == "right":
            if keys[pygame.K_UP] and paddle2_y > 0:
                paddle2_y -= 5
                client_socket.sendto(pickle.dumps({"paddle2_y": paddle2_y}), (SERVER_IP, SERVER_PORT))
            if keys[pygame.K_DOWN] and paddle2_y < HEIGHT - paddle_height:
                paddle2_y += 5
                client_socket.sendto(pickle.dumps({"paddle2_y": paddle2_y}), (SERVER_IP, SERVER_PORT))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
