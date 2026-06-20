import socket
import json
import threading
import time
import random

WIDTH = 800
HEIGHT = 600

BALL_SIZE = 20
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100

BALL_SPEED = 5
PADDLE_SPEED = 10

COUNTDOWN_START = 3
WIN_SCORE = 10


class GameServer:
    def __init__(self, host='localhost', port=8080):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)

        print("Server started!")

        self.clients = {0: None, 1: None}
        self.connected = {0: False, 1: False}

        self.lock = threading.Lock()

        self.sound_event = None

        self.reset_game_state()

    def reset_game_state(self):
        self.paddles = {
            0: HEIGHT // 2 - PADDLE_HEIGHT // 2,
            1: HEIGHT // 2 - PADDLE_HEIGHT // 2
        }

        self.scores = [0, 0]

        self.game_over = False
        self.winner = None

        self.countdown = COUNTDOWN_START

        self.reset_ball()

    def reset_ball(self):
        self.ball = {
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "vx": BALL_SPEED * random.choice([-1, 1]),
            "vy": BALL_SPEED * random.choice([-1, 1])
        }

    def handle_client(self, pid):
        conn = self.clients[pid]

        try:
            while True:
                data = conn.recv(64)

                if not data:
                    break

                data = data.decode().strip()

                with self.lock:
                    if data == "UP":
                        self.paddles[pid] = max(
                            0,
                            self.paddles[pid] - PADDLE_SPEED
                        )

                    elif data == "DOWN":
                        self.paddles[pid] = min(
                            HEIGHT - PADDLE_HEIGHT,
                            self.paddles[pid] + PADDLE_SPEED
                        )

        except:
            pass

        finally:
            with self.lock:
                self.connected[pid] = False
                self.game_over = True
                self.winner = 1 - pid

                print(f"Гравець {pid} відключився.")
                print(f"Гравець {1 - pid} переміг!")

            try:
                conn.close()
            except:
                pass

    def broadcast_state(self):
        state = json.dumps({
            "paddles": self.paddles,
            "ball": self.ball,
            "scores": self.scores,
            "countdown": max(self.countdown, 0),
            "winner": self.winner if self.game_over else None,
            "sound_event": self.sound_event
        }) + "\n"

        for pid, conn in self.clients.items():
            if conn:
                try:
                    conn.sendall(state.encode())

                except:
                    self.connected[pid] = False

    def ball_logic(self):
        while self.countdown > 0:
            time.sleep(1)

            with self.lock:
                self.countdown -= 1

            self.broadcast_state()

        while not self.game_over:
            with self.lock:
                self.ball["x"] += self.ball["vx"]
                self.ball["y"] += self.ball["vy"]

                if self.ball["y"] <= 0:
                    self.ball["y"] = 0
                    self.ball["vy"] *= -1
                    self.sound_event = "wall_hit"

                elif self.ball["y"] >= HEIGHT - BALL_SIZE:
                    self.ball["y"] = HEIGHT - BALL_SIZE
                    self.ball["vy"] *= -1
                    self.sound_event = "wall_hit"

                if (
                    self.ball["x"] <= 40 and
                    self.paddles[0] <= self.ball["y"] <= self.paddles[0] + PADDLE_HEIGHT
                ):
                    self.ball["vx"] *= -1
                    self.ball["x"] = 40
                    self.sound_event = "paddle_hit"

                elif (
                    self.ball["x"] >= WIDTH - 40 - BALL_SIZE and
                    self.paddles[1] <= self.ball["y"] <= self.paddles[1] + PADDLE_HEIGHT
                ):
                    self.ball["vx"] *= -1
                    self.ball["x"] = WIDTH - 40 - BALL_SIZE
                    self.sound_event = "paddle_hit"

                if self.ball["x"] < 0:
                    self.scores[1] += 1
                    self.sound_event = "score"

                    if self.scores[1] >= WIN_SCORE:
                        self.game_over = True
                        self.winner = 1
                    else:
                        self.reset_ball()

                elif self.ball["x"] > WIDTH:
                    self.scores[0] += 1
                    self.sound_event = "score"

                    if self.scores[0] >= WIN_SCORE:
                        self.game_over = True
                        self.winner = 0
                    else:
                        self.reset_ball()

            self.broadcast_state()

            self.sound_event = None

            time.sleep(0.016)

    def accept_players(self):
        for pid in [0, 1]:
            print(f"Чекаємо на гравців {pid}...")

            conn, addr = self.server.accept()

            print(f"Гравець {pid} : підключився{addr}")

            self.clients[pid] = conn
            self.connected[pid] = True

            conn.sendall((str(pid) + "\n").encode())

            threading.Thread(
                target=self.handle_client,
                args=(pid,),
                daemon=True
            ).start()

    def close_connections(self):
        for pid in [0, 1]:
            try:
                if self.clients[pid]:
                    self.clients[pid].close()

            except:
                pass

            self.clients[pid] = None
            self.connected[pid] = False

    def run(self):
        while True:
            self.accept_players()

            self.reset_game_state()

            game_thread = threading.Thread(
                target=self.ball_logic,
                daemon=True
            )

            game_thread.start()

            while not self.game_over and all(self.connected.values()):
                time.sleep(0.1)

            print(f"Гравець {self.winner} переміг!")

            time.sleep(5)

            self.close_connections()