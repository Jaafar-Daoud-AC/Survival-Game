import pygame
import random
import math
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
item_img = {}

# الوان كل بيئة
temas = {
    "city":    dict(block=(78, 80, 118), block2=(62, 64, 98), top=(150, 152, 192), ground=(58, 58, 74), gtop=(128, 130, 154), wood=(150, 108, 66)),
    "forest":  dict(block=(104, 90, 70), block2=(84, 72, 56), top=(88, 178, 76), ground=(98, 72, 48), gtop=(88, 178, 76), wood=(140, 96, 58)),
    "desert":  dict(block=(214, 168, 104), block2=(190, 144, 84), top=(240, 204, 140), ground=(224, 182, 112), gtop=(244, 210, 146), wood=(170, 120, 70)),
    "castle":  dict(block=(98, 102, 134), block2=(76, 80, 110), top=(150, 156, 190), ground=(66, 68, 94), gtop=(120, 124, 156), wood=(120, 84, 56)),
    "volcano": dict(block=(64, 44, 50), block2=(46, 30, 36), top=(120, 70, 60), ground=(46, 30, 34), gtop=(255, 120, 40), wood=(110, 110, 124)),
}

def load_images():
    for name in ["heart", "energy", "coin", "rapid", "power", "flag"]:
        item_img[name] = pygame.image.load(os.path.join(base_dir, "items", name + ".png")).convert_alpha()
    off = item_img["flag"].copy()
    px = pygame.PixelArray(off)
    px.replace((80, 220, 120), (200, 70, 70))
    del px
    item_img["flag_off"] = off

def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)

def build_block(w, h, theme, rnd):
    t = temas[theme]
    img = pygame.Surface((w, h))
    img.fill(t["block"])
    if theme == "city":
        for wy in range(30, h - 10, 34):
            for wx in range(14, w - 20, 30):
                lit = rnd.random() < 0.45
                col = (255, 214, 120) if lit else (44, 46, 74)
                pygame.draw.rect(img, col, (wx, wy, 14, 20))
        pygame.draw.rect(img, t["block2"], (0, 0, w, 12))
        pygame.draw.rect(img, t["top"], (0, 0, w, 4))
        pygame.draw.rect(img, t["block2"], (0, 0, 5, h))
        pygame.draw.rect(img, shade(t["block"], 0.8), (w - 5, 0, 5, h))
    else:
        bh = 26
        for row in range(0, h // bh + 1):
            off = 0 if row % 2 == 0 else 24
            for bx in range(-off, w, 48):
                c = shade(t["block"], rnd.uniform(0.86, 1.1))
                pygame.draw.rect(img, c, (bx + 1, row * bh + 1, 46, bh - 2))
        for row in range(0, h // bh + 1):
            pygame.draw.line(img, t["block2"], (0, row * bh), (w, row * bh), 2)
        if theme == "volcano":
            for i in range(max(2, w // 40)):
                x = rnd.randint(4, w - 4)
                y = rnd.randint(14, max(15, h - 4))
                pygame.draw.line(img, (255, 110, 30), (x, y), (x + rnd.randint(-14, 14), y + rnd.randint(10, 30)), 2)
        pygame.draw.rect(img, t["top"], (0, 0, w, 8))
        if theme == "castle":
            for bx in range(0, w, 32):
                pygame.draw.rect(img, t["block2"], (bx + 16, 8, 16, 10))
        if theme == "forest":
            for bx in range(0, w, 14):
                pygame.draw.rect(img, shade(t["top"], 0.85), (bx, 8, 8, rnd.randint(3, 8)))
    pygame.draw.rect(img, (0, 0, 0), (0, 0, w, h), 1)
    return img

def build_ground(w, h, theme, rnd):
    t = temas[theme]
    img = pygame.Surface((w, h))
    img.fill(t["ground"])
    for i in range(w // 6):
        x = rnd.randint(0, w - 1)
        y = rnd.randint(14, h - 1)
        pygame.draw.rect(img, shade(t["ground"], rnd.uniform(0.8, 1.15)), (x, y, rnd.randint(3, 9), rnd.randint(2, 5)))
    pygame.draw.rect(img, t["gtop"], (0, 0, w, 10))
    pygame.draw.rect(img, shade(t["gtop"], 0.8), (0, 10, w, 3))
    if theme == "city":
        for x in range(0, w, 70):
            pygame.draw.rect(img, (230, 200, 70), (x + 10, 46, 36, 4))
    if theme == "volcano":
        pygame.draw.rect(img, (255, 190, 70), (0, 0, w, 3))
    return img

def build_crate(w, h):
    img = pygame.Surface((w, h))
    img.fill((168, 118, 66))
    for x in range(0, w, 48):
        for y in range(0, h, 48):
            pygame.draw.rect(img, (120, 80, 44), (x, y, 48, 48), 4)
            pygame.draw.line(img, (136, 92, 50), (x + 4, y + 4), (x + 44, y + 44), 4)
            pygame.draw.line(img, (136, 92, 50), (x + 44, y + 4), (x + 4, y + 44), 4)
    return img

def build_ledge(w, theme):
    t = temas[theme]
    img = pygame.Surface((w, 16), pygame.SRCALPHA)
    pygame.draw.rect(img, t["wood"], (0, 0, w, 12))
    pygame.draw.rect(img, shade(t["wood"], 1.25), (0, 0, w, 3))
    for x in range(0, w, 28):
        pygame.draw.line(img, shade(t["wood"], 0.7), (x, 0), (x, 11), 2)
    pygame.draw.rect(img, shade(t["wood"], 0.6), (0, 12, w, 4))
    return img

class Platform:
    def __init__(self, kind, x, y, w, h, theme, move=None, seed=0):
        self.kind = kind
        self.rect = pygame.Rect(x, y, w, h)
        self.theme = theme
        self.dx = 0
        self.dy = 0
        self.move = move
        self.base_x = x
        self.base_y = y
        self.t = random.Random(seed).uniform(0, 6.28) if move else 0
        self.solid = kind in ("ground", "block", "crate", "wall")
        rnd = random.Random(x * 31 + y * 7 + w)
        self.image = None
        if kind == "block":
            self.image = build_block(w, h, theme, rnd)
        elif kind == "ground":
            self.image = build_ground(w, h, theme, rnd)
        elif kind == "crate":
            self.image = build_crate(w, h)
        elif kind == "ledge":
            self.image = build_ledge(w, theme)

    def update(self):
        self.dx = 0
        self.dy = 0
        if self.move:
            axis, rng, speed = self.move
            self.t += speed
            off = math.sin(self.t) * rng
            if axis == "x":
                nx = self.base_x + off
                self.dx = int(nx) - self.rect.x
                self.rect.x = int(nx)
            else:
                ny = self.base_y + off
                self.dy = int(ny) - self.rect.y
                self.rect.y = int(ny)

    def draw(self, screen, camx):
        if self.image is None:
            return
        x = self.rect.x - int(camx)
        if x > 1280 or x + self.rect.w < 0:
            return
        screen.blit(self.image, (x, self.rect.y))

class Hazard:
    def __init__(self, kind, x, y, w, theme="city"):
        self.kind = kind
        if kind == "spikes":
            self.rect = pygame.Rect(x, y - 24, w, 24)
        else:
            self.rect = pygame.Rect(x, y, w, 720 - y + 40)
        self.t = random.random() * 6

    def hit_rect(self):
        if self.kind == "spikes":
            return self.rect.inflate(-6, -8)
        return self.rect

    def draw(self, screen, camx):
        x = self.rect.x - int(camx)
        if x > 1280 or x + self.rect.w < 0:
            return
        if self.kind == "spikes":
            for sx in range(0, self.rect.w, 16):
                pts = [(x + sx, self.rect.bottom), (x + sx + 8, self.rect.top), (x + sx + 16, self.rect.bottom)]
                pygame.draw.polygon(screen, (170, 175, 190), pts)
                pygame.draw.polygon(screen, (235, 238, 245), [(x + sx + 8, self.rect.top), (x + sx + 12, self.rect.bottom), (x + sx + 8, self.rect.bottom)])
        else:
            self.t += 0.08
            pygame.draw.rect(screen, (255, 90, 20), (x, self.rect.y + 6, self.rect.w, self.rect.h))
            for sx in range(0, self.rect.w, 12):
                hh = int(math.sin(self.t + sx * 0.3) * 4)
                pygame.draw.rect(screen, (255, 170, 50), (x + sx, self.rect.y + hh, 12, 10))
                pygame.draw.rect(screen, (255, 230, 120), (x + sx, self.rect.y + hh, 12, 3))

class Pickup:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.t = random.random() * 6
        self.taken = False
        self.img = item_img[kind]
        self.w, self.h = self.img.get_size()

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2 - 4, self.w, self.h + 8)

    def draw(self, screen, camx):
        self.t += 0.1
        sx = self.x - int(camx) - self.w // 2
        if sx > 1280 or sx + self.w < 0:
            return
        screen.blit(self.img, (sx, self.y - self.h // 2 + int(math.sin(self.t) * 4)))

class Checkpoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = False

    def rect(self):
        return pygame.Rect(self.x - 20, self.y - 70, 40, 70)

    def draw(self, screen, camx):
        img = item_img["flag"] if self.active else item_img["flag_off"]
        sx = self.x - int(camx)
        if sx < -60 or sx > 1340:
            return
        screen.blit(img, (sx - 4, self.y - img.get_height()))
