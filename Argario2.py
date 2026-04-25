from math import hypot
from socket import *
import pylab as p
from pygame import *
from threading import Thread
from random import randint

# ПІДКЛЮЧЕННЯ
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(("0.tcp.eu.ngrok.io", 15374)) # Перевір цей порт!

# Отримання перших даних від сервера
data_init = sock.recv(64).decode().strip()
my_data = list(map(int, data_init.split(',')))

my_id = my_data[0]
my_player = my_data[1:] # Тут [x, y, radius]
sock.setblocking(False)

init()
win = display.set_mode((800, 800))
clock = time.Clock()
f = font.Font(None, 50)

all_players = []
running = True
lose = False

def receive_data():
    global all_players, running, lose
    while running:
        try:
            data = sock.recv(4096).decode().strip()
            if data == "LOSE":
                lose = True
            elif data:
                # Розбиваємо пакет на гравців по символу |
                parts = data.split("|")
                all_players = []
                for p_str in parts:
                    if p_str:
                        try:
                            all_players.append(list(map(int, p_str.split(","))))
                        except:
                            continue
        except:
            pass

Thread(target=receive_data, daemon=True).start()

class Eat():
    def __init__(self, x, y, c, r):
        self.x = x
        self.y = y
        self.color = c
        self.radius = r

    def chet_collision(self, player_x, player_y, player_r):
        dx = self.x - player_x
        dy = self.y - player_y
        return hypot(dx, dy) <= self.radius + player_r

eats = [Eat(randint(-2000, 2000),
            randint(-2000, 2000),
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            10) for i in range(300)]

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    win.fill((255, 255, 255))

    # Масштабування
    rad = my_player[2] if my_player[2] > 0 else 1
    scale = max(0.3, min(50 / rad, 1.5))

    # МАЛЮЄМО ІНШИХ
    for p_other in all_players:
        if p_other[0] == my_id:
            continue
        # Координати відносно нас (камера)
        sx = int((p_other[1] - my_player[0]) * scale + 400)
        sy = int((p_other[2] - my_player[1]) * scale + 400)
        draw.circle(win, (255, 0, 0), (sx, sy), int(p_other[3] * scale))

    # МАЛЮЄМО СЕБЕ
    draw.circle(win, (0, 255, 0), (400, 400), int(my_player[2] * scale))

    # МАЛЮЄМО ЇЖУ
    to_remove = []
    for eat in eats:
        if eat.chet_collision(my_player[0], my_player[1], my_player[2]):
            to_remove.append(eat)
            my_player[2] += 0.5
        else:
            sx = int((eat.x - my_player[0]) * scale + 400)
            sy = int((eat.y - my_player[1]) * scale + 400)
            if -100 < sx < 900 and -100 < sy < 900:
                draw.circle(win, eat.color, (sx, sy), int(eat.radius * scale))

    for eat in to_remove:
        if eat in eats: eats.remove(eat)

    if lose:
        t = f.render("Ти програв!", 1, (244, 0, 0))
        win.blit(t, (300, 400))

    if not lose:
        keys = key.get_pressed()
        if keys[K_w]: my_player[1] -= 10
        if keys[K_s]: my_player[1] += 10
        if keys[K_a]: my_player[0] -= 10
        if keys[K_d]: my_player[0] += 10

        
        try:
            msg = f"{my_id},{int(my_player[0])},{int(my_player[1])},{int(my_player[2])}|"
            sock.send(msg.encode())
        except:
            pass

    display.update()
    clock.tick(60)

quit()