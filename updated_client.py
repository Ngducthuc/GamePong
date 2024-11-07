import pygame
import socket
import pickle
import threading

# Server info
SERVER_IP = '192.168.100.234'
SERVER_PORT = 5555
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 60)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()

connected = False
client_socket = None

def connect_to_server():
    global client_socket, connected
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    connected = True

def receive_data():
    global paddle1_y, paddle2_y, ball_x, ball_y, game_started, role, score_left, score_right
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
        if "ball_x" in message and "ball_y" in message:
            ball_x = message["ball_x"]
            ball_y = message["ball_y"]
        if "score_left" in message:
            score_left = message["score_left"]
        if "score_right" in message:
            score_right = message["score_right"]

# ... (Other client code remains the same)

if __name__ == "__main__":
    main()
