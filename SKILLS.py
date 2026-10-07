import pygame
import os
from ABSOLUTE import aboslute
from BULLET import Bullet
import EFFECTS

base_dir = os.path.dirname(os.path.abspath(__file__))

# كل مهارة: زر، تكلفة طاقة، وقت انتظار بين استعمالين
skills = {
    "dash":   dict(key=pygame.K_d, cost=15, cooldown=40, label="D", name="DASH"),
    "triple": dict(key=pygame.K_a, cost=20, cooldown=25, label="A", name="TRIPLE"),
    "shield": dict(key=pygame.K_f, cost=30, cooldown=60, label="F", name="SHIELD"),
    "nova":   dict(key=pygame.K_e, cost=45, cooldown=90, label="E", name="NOVA"),
    "tank":   dict(key=pygame.K_r, cost=100, cooldown=300, label="R", name="TANK"),
}
order = ["dash", "triple", "shield", "nova", "tank"]

# اللي بنفتحه بعد كل بوس
rewards = [["doublejump"], ["dash"], ["triple"], ["shield"], ["nova", "tank"]]
names = {"doublejump": "DOUBLE JUMP (SPACE x2)", "dash": "DASH (D)", "triple": "TRIPLE SHOT (A)",
         "shield": "SHIELD (F)", "nova": "NOVA (E)", "tank": "TANK ULTIMATE (R)"}

def load_tank(folder, left_files, right_files, scale):
    # الدبابة صغيرة وسط صورة 400x400 فنقص الفاضي حواليها
    crop = pygame.Rect(117, 164, 166, 72)
    out = []
    for files in (left_files, right_files):
        frames = []
        for f in files:
            img = pygame.image.load(os.path.join(base_dir, folder, f)).convert_alpha()
            img = img.subsurface(crop).copy()
            size = (int(crop.w * scale), int(crop.h * scale))
            frames.append(pygame.transform.smoothscale(img, size))
        out.append(frames)
    return out[0], out[1]

green_left = []
green_right = []

def load_skill_images():
    global green_left, green_right
    green_left, green_right = load_tank("fn", ["er.png", "ergo.png"], ["ew.png", "ewgo.png"], 0.85)

def use_dash(p):
    p.dash_time = 10
    p.dash_dir = 1 if p.right else -1
    p.invul = max(p.invul, 14)
    p.dash_hit = set()
    EFFECTS.burst(p.x + 32, p.y + 40, (200, 220, 255), 8, 4)

def use_triple(p, bullets, speed_Bullet):
    direction = 1 if p.right else -1
    cx, cy = p.center()
    for vy in (-3, 0, 3):
        b = Bullet(cx, cy - 4, 6, (255, 190, 60), direction, 14 + speed_Bullet, vy, p.damage(), True, 0, 60)
        b.tag = "skill"
        bullets.append(b)

def use_shield(p):
    p.shield = 240

def use_nova(p, novas):
    cx, cy = p.center()
    novas.append(Nova(cx, cy))
    EFFECTS.do_shake(10)

def use_tank(p, allies):
    direction = 1 if p.right else -1
    t = Tank(p.x + (40 if direction > 0 else -90), p.y - 20, direction)
    allies.append(t)

class Nova:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 300
        self.hit = set()
        self.dead = False

    def update(self, targets, enemy_bullets, damage):
        self.radius += 14
        if self.radius >= self.max_radius:
            self.dead = True
        for t in targets:
            if id(t) in self.hit:
                continue
            tx, ty = t.center()
            d = ((tx - self.x) ** 2 + (ty - self.y) ** 2) ** 0.5
            if d <= self.radius + 20:
                self.hit.add(id(t))
                t.hit(damage * 4, 1 if tx > self.x else -1)
        for b in enemy_bullets:
            d = ((b.x - self.x) ** 2 + (b.y - self.y) ** 2) ** 0.5
            if d <= self.radius and b.pierce < 50:
                b.dead = True

    def draw(self, screen, camx):
        k = 1 - self.radius / self.max_radius
        col = (int(120 + 135 * k), int(200 + 55 * k), 255)
        w = max(2, int(10 * k))
        pygame.draw.circle(screen, col, (int(self.x - camx), int(self.y)), int(self.radius), w)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - camx), int(self.y)), max(1, int(self.radius) - w), 1)

class Tank(aboslute):
    def __init__(self, x, y, direction):
        w = green_right[0].get_width()
        h = green_right[0].get_height()
        aboslute.__init__(self, x, y, w, h, 7, 2, 0, 1)
        self.ox = 0
        self.oy = 0
        self.bw = w
        self.bh = h
        self.direction = direction
        self.life = 260
        self.fire = 10
        self.dead = False

    def update(self, solids, oneways, bullets, damage):
        self.vx = self.direction * self.step
        self.mover(solids, oneways)
        self.moves += 1
        self.life -= 1
        self.fire -= 1
        if self.fire <= 0:
            self.fire = 28
            bx = self.x + (self.width if self.direction > 0 else 0)
            b = Bullet(bx, self.y + 14, 8, (130, 255, 150), self.direction, 15, 0, damage * 2, True, 0, 70)
            b.tag = "skill"
            bullets.append(b)
        if self.life <= 0 or self.hit_wall:
            self.dead = True
            EFFECTS.burst(self.x + self.width // 2, self.y + 20, (255, 200, 80), 24, 7)
            EFFECTS.do_shake(8)

    def draw(self, screen, camx):
        frames = green_right if self.direction > 0 else green_left
        screen.blit(frames[(self.moves // 6) % 2], (self.x - camx, self.y))
