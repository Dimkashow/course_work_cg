import pygame as pg
from settings import *


class Label:
    def __init__(self, render, text, pos):
        self.render = render
        self.x, self.y = pos
        self.label = text

    def draw(self):
        f = pg.font.Font(None, SIZE_TEXT_STD)
        text = f.render(self.label, True, COLOR_TEXT_STD)
        self.render.screen.blit(text, (self.x, self.y))


class Button:
    def __init__(self, render, box, text, function, inputs):
        self.render = render
        self.position = box
        self.text = text
        self.rect = pg.Rect(box)
        self.box = box
        self.function = function
        self.inputs = inputs

    def draw(self):
        pg.draw.rect(self.render.screen, GREY, self.rect)
        f = pg.font.Font(None, SIZE_TEXT_INPUT_STD)
        final_text = self.text
        text = f.render(final_text, True, COLOR_TEXT_STD)
        self.render.screen.blit(text, (self.box[0] + 5, self.box[1] + 5))

    def check(self, pos):
        if self.rect.collidepoint(pos):
            arg = []
            for i in self.inputs:
                arg.append(int(i.text))
            self.function(arg)


class Input:
    def __init__(self, render, box):
        self.render = render
        self.rect = pg.Rect(box)
        self.box = box
        self.active = False
        self.text = ""
        self.text_active = "|"

    def draw(self):
        pg.draw.rect(self.render.screen, GREY, self.rect)
        f = pg.font.Font(None, SIZE_TEXT_INPUT_STD)
        final_text = self.text
        if self.active:
            final_text += self.text_active

        text = f.render(final_text, True, COLOR_TEXT_STD)
        self.render.screen.blit(text, (self.box[0] + 5, self.box[1] + 5))

    def check(self, pos):
        if self.rect.collidepoint(pos):
            self.active = True
        else:
            self.active = False

    def add(self, char):
        # TODO check GRID_SIZE
        if self.active and len(self.text) < MAX_INPUT_LEN:
            self.text += char

    def delete(self):
        if self.active:
            self.text = self.text[:-1]


class Interface:
    def __init__(self, render):
        self.render = render
        self.buttons = []
        self.labels = []
        self.inputs = []

        self.labels.append(Label(render, "X:", (10, 13)))
        self.labels.append(Label(render, "Y:", (110, 13)))
        self.labels.append(Label(render, "Z:", (210, 13)))

        self.inputs.append(Input(render, (40, 10, 60, 30)))
        self.inputs.append(Input(render, (140, 10, 60, 30)))
        self.inputs.append(Input(render, (240, 10, 60, 30)))

        self.labels.append(Label(render, "LEVEL:", (640, 13)))
        self.inputs.append(Input(render, (740, 10, 60, 30)))

        # TODO ДИЗИГН
        self.buttons.append(Button(render, (340, 10, 60, 30), "Add", self.render.add_cube,
                                   [self.inputs[0], self.inputs[1], self.inputs[2]]))

        self.buttons.append(Button(render, (440, 10, 60, 30), "Del", self.render.del_cube,
                                   [self.inputs[0], self.inputs[1], self.inputs[2]]))

        self.buttons.append(Button(render, (840, 10, 60, 30), "Load", self.render.load_level,
                                   [self.inputs[3]]))

        self.buttons.append(Button(render, (940, 10, 60, 30), "Save", self.render.save_level,
                                   [self.inputs[3]]))

    def draw(self):
        x_input_rect = pg.Rect(0, 0, self.render.WIDTH, 50)
        pg.draw.rect(self.render.screen, WHITE, x_input_rect)
        pg.draw.rect(self.render.screen, BLACK, x_input_rect, 2)

        if self.render.level_passed:
            win_rect = pg.Rect(0, 50, self.render.WIDTH, self.render.HEIGHT)
            pg.draw.rect(self.render.screen, WHITE, win_rect)

            f = pg.font.Font(None, 70)
            text = f.render("Level passed!!! Select another level", True, COLOR_TEXT_STD)
            self.render.screen.blit(text, (self.render.WIDTH / 4, self.render.HEIGHT / 2))

        for i in range(len(self.labels)):
            self.labels[i].draw()

        for i in range(len(self.inputs)):
            self.inputs[i].draw()

        for i in range(len(self.buttons)):
            self.buttons[i].draw()

    def control(self):
        ev = pg.event.get()
        for event in ev:
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                if event.button == 1:
                    for i in range(len(self.inputs)):
                        self.inputs[i].check(pos)

                    for i in range(len(self.buttons)):
                        self.buttons[i].check(pos)

                    self.render.check_add_block(pos)
                else:
                    self.render.check_del_block(pos)

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    for i in range(len(self.inputs)):
                        self.inputs[i].delete()
                else:
                    for i in range(len(self.inputs)):
                        self.inputs[i].add(event.unicode)

            elif event.type == pg.QUIT:
                exit()
