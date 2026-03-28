from pygame import *


init()

size = 800, 600
win = display.set_mode(size)
display.set_caption("Моя гра ахха")
clock = time.Clock()

player = Rect(200,200,50,50)
player_speed = 3

while True:
    for e in event.get():
        if e.type == QUIT:
            quit()
    draw.rect(win, (0,200,0), player)

    keys = key.get_pressed()

    if keys[K_w]:
        player.y -= player_speed
    if keys[K_a]:
        player.x -= player_speed
    if keys[K_s]:
        player.y += player_speed
    if keys[K_d]:
        player.x += player_speed

    display.update()
    clock.tick(60)

