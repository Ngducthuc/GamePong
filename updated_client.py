import pygame
import socket
import pickle
import threading
SERVER_IP = '192.168.100.234'
SERVER_PORT = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (30, 30, 60)
ACCENT_COLOR = (100, 255, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
paddle_width, paddle_height = 10, 100
ball_radius = 10
paddle1_y = HEIGHT // 2
paddle2_y = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5
role = None  # Player role (left or right)
game_started = False  # Game start condition
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()
def receive_data():
    global paddle1_y, paddle2_y, ball_x, ball_y, game_started, role
    while True:
        data = client_socket.recv(1024)
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
goal_width = 10
goal_height = HEIGHT // 3
score_left = 0
score_right = 0
def main():
    global paddle1_y, paddle2_y, ball_x, ball_y, ball_dx, ball_dy, game_started, role, score_left, score_right
    threading.Thread(target=receive_data, daemon=True).start()
    running = True
    while running:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, WHITE, (0, HEIGHT // 2 - goal_height // 2, goal_width, goal_height))  # Khung thành bên trái
        pygame.draw.rect(screen, WHITE, (WIDTH - goal_width, HEIGHT // 2 - goal_height // 2, goal_width, goal_height))  # Khung thành bên phải
        font = pygame.font.Font(None, 74)
        score_text = font.render(f"{score_left} - {score_right}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        if role == "left":
            pygame.draw.rect(screen, RED, (20, paddle1_y, paddle_width, paddle_height))
            pygame.draw.rect(screen, BLUE, (WIDTH - 30, paddle2_y, paddle_width, paddle_height))
        elif role == "right":
            pygame.draw.rect(screen, BLUE, (WIDTH - 30, paddle2_y, paddle_width, paddle_height))
            pygame.draw.rect(screen, RED, (20, paddle1_y, paddle_width, paddle_height))
        if game_started:
            pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)
            ball_x += ball_dx
            ball_y += ball_dy
            if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
                ball_dy *= -1
            if (20 <= ball_x <= 30 and paddle1_y <= ball_y <= paddle1_y + paddle_height) or (WIDTH - 30 <= ball_x <= WIDTH - 20 and paddle2_y <= ball_y <= paddle2_y + paddle_height):
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if role == "left":
            if keys[pygame.K_w] and paddle1_y > 0:
                paddle1_y -= 5
                client_socket.sendall(pickle.dumps({"paddle1_y": paddle1_y}))
            if keys[pygame.K_s] and paddle1_y < HEIGHT - paddle_height:
                paddle1_y += 5
                client_socket.sendall(pickle.dumps({"paddle1_y": paddle1_y}))
        elif role == "right":
            if keys[pygame.K_UP] and paddle2_y > 0:
                paddle2_y -= 5
                client_socket.sendall(pickle.dumps({"paddle2_y": paddle2_y}))
            if keys[pygame.K_DOWN] and paddle2_y < HEIGHT - paddle_height:
                paddle2_y += 5
                client_socket.sendall(pickle.dumps({"paddle2_y": paddle2_y}))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx *= -1
if __name__ == "__main__":
    main()