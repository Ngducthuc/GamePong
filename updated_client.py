import pygame
import socket
import pickle
import threading
import datetime

# Server info
SERVER_IP = '192.168.100.234'
SERVER_PORT = 5555
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
ACCENT_COLOR = (100, 255, 100)
paddle_width, paddle_height = 10, 100
ball_radius = 10
goal_width = 10
goal_height = HEIGHT // 3
score_left = 0
score_right = 0
paddle1_y = HEIGHT // 2
paddle2_y = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
role = None
game_started = False
game_over = False

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()
connected = False
client_socket = None

paddle_red_img = pygame.image.load('Ronaldo-Da-Phat.png').convert_alpha()
paddle_blue_img = pygame.image.load('Lionel_Messi.png').convert_alpha()
paddle_red_img = pygame.transform.scale(paddle_red_img, (paddle_width * 6.5, paddle_height*1.5))
paddle_blue_img = pygame.transform.scale(paddle_blue_img, (paddle_width*6.5, paddle_height*1.5))
def save_score(score_left, score_right, winner):
    # Lưu điểm vào file text
    with open("scores.txt", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Date: {timestamp}\n")
        file.write(f"Score - Left Player: {score_left}, Right Player: {score_right}\n")
        file.write(f"Winner: {winner}\n")
        file.write("="*30 + "\n")
    print("Score saved to scores.txt")
def connect_to_server():
    global client_socket, connected
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    connected = True
def receive_data():
    global paddle1_y, paddle2_y, ball_x, ball_y, game_started, role, score_left, score_right, time_remaining, game_over, winner
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        message = pickle.loads(data)
        if "role" in message:
            role = message["role"]
        if "game_ready" in message and message["game_ready"]:
            game_started = True
        if "paddle1_y" in message:
            paddle1_y = message["paddle1_y"]
        if "paddle2_y" in message:
            paddle2_y = message["paddle2_y"]
        if "ball_x" in message and "ball_y" in message:
            ball_x = message["ball_x"]
            ball_y = message["ball_y"]
        if "score_left" in message:
            score_left = message["score_left"]
        if "score_right" in message:
            score_right = message["score_right"]
        if "time_remaining" in message:
            time_remaining = message["time_remaining"]
        if "game_over" in message:
            game_over = message["game_over"]
            winner = message.get("winner", "draw")
def draw_soccer_field():
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREEN, (20, 20, WIDTH - 40, HEIGHT - 40), 5) 
    pygame.draw.circle(screen, GREEN, (WIDTH // 2, HEIGHT // 2), 50, 5)  
    pygame.draw.line(screen, GREEN, (WIDTH // 2, 20), (WIDTH // 2, HEIGHT - 20), 5)
    pygame.draw.rect(screen, GREEN, (20, HEIGHT // 2 - goal_height // 2, 60, goal_height), 5)
    pygame.draw.rect(screen, GREEN, (WIDTH - 80, HEIGHT // 2 - goal_height // 2, 60, goal_height), 5)
def show_waiting_screen():
    waiting = True
    font = pygame.font.Font(None, 74)
    button_font = pygame.font.Font(None, 50)
    button_text = button_font.render("Join Game", True, WHITE)
    button_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    while waiting:
        draw_soccer_field()  # Draw soccer field background
        title_text = font.render("Ping Pong Game", True, ACCENT_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
        pygame.draw.rect(screen, ACCENT_COLOR, button_rect.inflate(20, 20), border_radius=10)
        screen.blit(button_text, button_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                connect_to_server()
                threading.Thread(target=receive_data, daemon=True).start()
                waiting = False
        pygame.display.flip()
        clock.tick(60)
    return True
time_remaining = 0
ball_speed_x = 5
ball_speed_y = 5
def main():
    global paddle1_y, paddle2_y, ball_x, ball_y, game_started, role, score_left, score_right, game_over, winner, time_remaining, ball_speed_x, ball_speed_y
    if not show_waiting_screen():
        return

    # Chờ đến khi nhận được tín hiệu bắt đầu game từ server
    while not game_started:
        draw_soccer_field()
        font = pygame.font.Font(None, 50)
        waiting_text = font.render("Waiting for another player...", True, WHITE)
        screen.blit(waiting_text, (WIDTH // 2 - waiting_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(60)

    # Vòng lặp game
    running = True
    while running:
        draw_soccer_field()
        score_text = pygame.font.Font(None, 74).render(f"{score_left} - {score_right}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        time_text = pygame.font.Font(None, 50).render(f"Time: {time_remaining}s", True, WHITE)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 50))
        if role == "left":
            screen.blit(paddle_red_img, (20, paddle1_y))
            screen.blit(paddle_blue_img, (WIDTH - 90, paddle2_y))
        elif role == "right":
            screen.blit(paddle_blue_img, (WIDTH - 90, paddle2_y))
            screen.blit(paddle_red_img, (20, paddle1_y))
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
            ball_speed_y *= -1  # Đổi hướng theo trục y
        if (ball_x - ball_radius <= 20 + paddle_width and
            paddle1_y < ball_y < paddle1_y + paddle_height):
            ball_speed_x *= -1
        if (ball_x + ball_radius >= WIDTH - 90 and
            paddle2_y < ball_y < paddle2_y + paddle_height):
            ball_speed_x *= -1
        if ball_x < 0:
            score_right += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_speed_x *= -1
        elif ball_x > WIDTH:
            score_left += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_speed_x *= -1
        if game_started and not game_over:
            glow_radius = 15
            pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius + glow_radius, width=2)
            pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)
        if game_over:
            font = pygame.font.Font(None, 100)
            if winner == "draw":
                winner_text = font.render("Draw!", True, ACCENT_COLOR)
            else:
                winner_text = font.render(f"{winner.capitalize()} wins!", True, ACCENT_COLOR)
            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(3000)
            save_score(score_left, score_right, winner)
            running = False
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
if __name__ == "__main__":
    main()
