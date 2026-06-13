import fontTools.fontBuilder
from pygame import *
import sys

from settings import Settings, settings_loop

purple = (142, 36, 100)
orange = (225, 108, 68)
blue = (85, 118, 201)
white = (255, 255, 255)


BUTTON = [
    "почати",
    "НАЛАШТУВАННЯ",
    "Вихід"
]

class Button():
    def __init__(self,
                 text,
                 font,
                 width,
                 height,
                 pos,
                 round_top = False,
                 round_bottom = False
    ):
        self.text = text
        self.font = font
        self.width = width
        self.height = height
        self.pos = pos
        self.round_top = round_top
        self.round_bottom = round_bottom

        self.rect = Rect(
            pos[0],
            pos[1],
            width,
            height
        )

    def draw(self, screen, selected = False):
        if self.text == "почати":
            color = orange if selected else purple

        elif self.text == "НАЛАШТУВАННЯ":
            color = orange if selected else blue

        else:
            color = orange if selected else blue

        border_radius = 20

        bottom_left = border_radius if self.round_bottom else 0
        bottom_radius = border_radius if self.round_bottom else 0

        top_left = border_radius if self.round_top else 0
        top_right = border_radius if self.round_top else 0

        draw.rect(
            screen,
            color,
            self.text,
            border_top_left_radius= top_left,
            border_top_right_radius= top_right,
            border_bottom_right_radius= bottom_left,
            border_bottom_left_radius= bottom_radius

        )
        text_surf = self.font.render(self.text, True, white)
        text_rect = text_surf.get_rect(center = self.rect.center)
        screen.blit(text_surf, text_rect)

def menu_loop(
        screen_width,
        screen_height,
        screen,
        settings
):
    init()

    display.set_caption("Ping_Pong")
    clock = time.Clock()
    mixer.init()
    play_menu_music(settings)

    MENU_CHOICE_SOUND = mixer.Sound('sounds/Menu Choice.mp3')

    font_obj = font.Font(None, 40)
    button_width = 400
    button_height = 70

    gap = 10

    total_height = (
        len(BUTTON) * button_height + (len(BUTTON)-1) * gap

    )
    start_y = (
            screen_height - total_height
    ) // 2

    buttons = []

    for i, text in enumerate(BUTTON):
        x = (
            screen_width - button_width
        ) // 2

        y = start_y + i * (button_height + gap)

        round_top = i == 0
        round_bottom = i == len(BUTTON) -1

        buttons.append(
            Button(
                text,
                font_obj,
                button_width,
                button_height,
                (x, y),
                round_top,
                round_bottom
            )
        )

    selected_index = 0

    while True:

        screen.fill((30, 30, 30))
        for e in event.get():
            if e.type == QUIT:
                quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_DOWN:
                    selected_index = (selected_index + 1) % len(buttons)
                    MENU_CHOICE_SOUND.play()
                elif e.key == K_UP:
                    selected_index =