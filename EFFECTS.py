import pygame
import random

particles = []
texts = []
shake = 0

class Particle:
    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.25):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity

class FloatText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 45

font_small = None

def burst(x, y, color, n=10, speed=5, life=25, size=4, gravity=0.25):
    for i in range(n):
        vx = random.uniform(-speed, speed)
        vy = random.uniform(-speed, speed * 0.5)
        particles.append(Particle(x, y, vx, vy, random.randint(life // 2, life), color, random.randint(2, size), gravity))

def ring(x, y, color, n=24, speed=8):
    import math
    for i in range(n):
        a = i * 6.2832 / n
        particles.append(Particle(x, y, math.cos(a) * speed, math.sin(a) * speed, 22, color, 4, 0))

def add_text(x, y, text, color=(255, 255, 255)):
    texts.append(FloatText(x, y, text, color))

def do_shake(power):
    global shake
    if power > shake:
        shake = power

def update_effects():
    global shake
    for p in particles[:]:
        p.x += p.vx
        p.y += p.vy
        p.vy += p.gravity
        p.life -= 1
        if p.life <= 0:
            particles.remove(p)
    for t in texts[:]:
        t.y -= 1
        t.life -= 1
        if t.life <= 0:
            texts.remove(t)
    if shake > 0:
        shake -= 1

def draw_effects(screen, camx):
    global font_small
    if font_small is None:
        font_small = pygame.font.SysFont("conicsans", 24, True, True)
    for p in particles:
        size = max(1, int(p.size * p.life / p.max_life))
        pygame.draw.rect(screen, p.color, (p.x - camx - size // 2, p.y - size // 2, size, size))
    for t in texts:
        img = font_small.render(t.text, True, t.color)
        screen.blit(img, (t.x - camx - img.get_width() // 2, t.y))

def clear_effects():
    global shake
    del particles[:]
    del texts[:]
    shake = 0
