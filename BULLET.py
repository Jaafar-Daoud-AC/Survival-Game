import pygame
from ABSOLUTE import aboslute
bullets = []
screen_width = 1280

class Bullet(aboslute):
    # "shot" طلقة اللاعب العادية، و"skill" لطلقات المهارات
    # (حتى ما تنحسب من الحد الاقصى للطلقات)
    tag = "shot"

    def __init__(self, x, y, redius, color, direction, step, vy=0, damage=1, friendly=True, gravity=0, life=80):
        self.x = x
        self.y = y
        self.redius = redius
        self.color = color
        self.direction = direction
        self.step = step * direction
        self.vy = vy
        self.damage = damage
        self.friendly = friendly
        self.gravity = gravity
        self.life = life
        self.trail = []
        self.pierce = 0
        self.dead = False

    def rect(self):
        return pygame.Rect(int(self.x - self.redius), int(self.y - self.redius), self.redius * 2, self.redius * 2)

    def update(self, solids):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.step
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        if self.life <= 0 or self.y > 900 or self.y < -200:
            self.dead = True
        r = self.rect()
        for s in solids:
            if r.colliderect(s.rect):
                self.dead = True
                break

    def draw(self, screen, camx):
        n = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            rr = max(1, int(self.redius * (i + 1) / (n + 1)))
            c = tuple(int(v * (i + 1) / (n + 2)) for v in self.color)
            pygame.draw.circle(screen, c, (int(tx - camx), int(ty)), rr)
        pos = (int(self.x - camx), int(self.y))
        pygame.draw.circle(screen, self.color, pos, self.redius)
        pygame.draw.circle(screen, (255, 255, 255), pos, max(1, self.redius // 2))

class Wave(Bullet):
    # موجة بتمشي ع الارض، لازم تقفز عنها
    def __init__(self, x, y, width, height, direction, step, damage=4, color=(255, 170, 60), life=90):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.redius = 0
        self.color = color
        self.direction = direction
        self.step = step * direction
        self.vy = 0
        self.damage = damage
        self.friendly = False
        self.gravity = 0
        self.life = life
        self.trail = []
        self.pierce = 99
        self.dead = False

    def rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h), self.w, self.h)

    def update(self, solids):
        self.x += self.step
        self.life -= 1
        if self.life <= 0:
            self.dead = True
        r = self.rect()
        for s in solids:
            if r.colliderect(s.rect) and r.bottom > s.rect.top + 6:
                self.dead = True
                break

    def draw(self, screen, camx):
        r = self.rect()
        r.x -= int(camx)
        pts = [(r.left, r.bottom), (r.centerx, r.top), (r.right, r.bottom)]
        pygame.draw.polygon(screen, self.color, pts)
        inner = [(r.left + r.w // 4, r.bottom), (r.centerx, r.top + r.h // 3), (r.right - r.w // 4, r.bottom)]
        pygame.draw.polygon(screen, (255, 240, 180), inner)
