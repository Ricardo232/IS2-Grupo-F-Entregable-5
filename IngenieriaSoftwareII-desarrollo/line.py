import pygame as pg

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.points = []
        self.get_points(x1, y1, x2, y2)

    def get_points(self, x1, y1, x2, y2):
        x_1 = int(x1)
        x_2 = int(x2)
        y_1 = int(y1)
        y_2 = int(y2)
        try:
            m = (y_2 - y_1) / (x_2 - x_1)
        except ZeroDivisionError as e:
            m = ""
        if m:
            b = y_1 - m * x_1
            for i in range(x_1, x_2 + 1):
                self.points.append([i, m * i + b])

    def check_collision(self, sprite, axis):
        if axis == "x":
            for point in self.points:
                if sprite.hit_rect.collidepoint(point[0], point[1]):
                    if point[0] > sprite.hit_rect.centerx:
                        sprite.pos.x = point[0] - sprite.hit_rect.width / 2
                    if point[0] < sprite.hit_rect.centerx:
                        sprite.pos.x = point[0] + sprite.hit_rect.width / 2
                    #sprite.vel.x = 0
                    sprite.hit_rect.centerx = sprite.pos.x

        if axis == "y":
            for point in self.points:
                if sprite.hit_rect.collidepoint(point[0], point[1]):
                    if point[1] > sprite.hit_rect.centery:
                        sprite.pos.y = point[1] - sprite.hit_rect.height / 2
                    if point[1] < sprite.hit_rect.centery:
                        sprite.pos.y = point[1] + sprite.hit_rect.height / 2
                    #sprite.vel.y = 0
                    sprite.hit_rect.centery = sprite.pos.y
