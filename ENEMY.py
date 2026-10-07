import  pygame
import random
import math
import os
from  ABSOLUTE import aboslute
from BULLET import Bullet
import SKILLS
import EFFECTS
RED = (255, 0, 0)
green = (0, 255, 0)

base_dir = os.path.dirname(os.path.abspath(__file__))

# مواصفات كل نوع عدو
tipos = {
    "goblin": dict(hp=3, spd=2.2, dmg=3, scale=1.0, tint=None, score=10, ai="walk"),
    "runner": dict(hp=2, spd=4.2, dmg=2, scale=0.85, tint=(150, 190, 255), score=12, ai="walk"),
    "brute":  dict(hp=10, spd=1.4, dmg=5, scale=1.5, tint=(255, 150, 150), score=30, ai="walk"),
    "archer": dict(hp=3, spd=1.6, dmg=2, scale=1.0, tint=(255, 225, 120), score=15, ai="range"),
    "bat":    dict(hp=2, spd=2.8, dmg=2, scale=1.0, tint=None, score=12, ai="fly"),
    "tank":   dict(hp=14, spd=1.0, dmg=4, scale=1.0, tint=None, score=40, ai="tank"),
}

sprites = {}

def tint_frames(frames, tint, scale):
    out = []
    for f in frames:
        w = int(f.get_width() * scale)
        h = int(f.get_height() * scale)
        img = pygame.transform.scale(f, (w, h)) if scale != 1.0 else f.copy()
        if tint is not None:
            img.fill(tint + (255,), special_flags=pygame.BLEND_RGBA_MULT)
        out.append(img)
    return out

def build_sprites(move_leftE, move_rightE):
    # بنجهز صور كل نوع مرة وحدة من البداية بدل ما نغير الحجم واللون كل مرة
    for name, t in tipos.items():
        if t["ai"] in ("walk", "range"):
            sprites[name] = (tint_frames(move_leftE, t["tint"], t["scale"]), tint_frames(move_rightE, t["tint"], t["scale"]))
    bl = []
    for i in range(3):
        bl.append(pygame.image.load(os.path.join(base_dir, "enemy", "B%d.png" % (i + 1))).convert_alpha())
    bl = [pygame.transform.scale(b, (int(b.get_width() * 0.7), int(b.get_height() * 0.7))) for b in bl]
    br = [pygame.transform.flip(b, True, False) for b in bl]
    sprites["bat"] = (bl, br)
    tl, tr = SKILLS.load_tank("foe", ["er1.png", "ergo1.png"], ["ew1.png", "ewgo1.png"], 0.65)
    sprites["tank"] = (tl, tr)
    # البوسات بتاخد صور الغوبلن بس اكبر
    sprites["_goblin"] = (move_leftE, move_rightE)

class Enemy(aboslute):
    def __init__(self, x, y, kind="goblin", mult=1.0):
        t = tipos[kind]
        self.kind = kind
        self.t = t
        sp = sprites[kind][0][0]
        width = sp.get_width()
        height = sp.get_height()
        aboslute.__init__(self, x, y, width, height, t["spd"], len(sprites[kind][0]), 0, max(1, int(round(t["hp"] * mult))))
        self.mult = mult
        s = t["scale"]
        if t["ai"] in ("walk", "range"):
            self.ox = int(20 * s)
            self.oy = int(4 * s)
            self.bw = int(26 * s)
            self.bh = int(54 * s)
            # القدمين على الارض مو الراس
            self.y = y - (self.oy + self.bh)
        elif t["ai"] == "fly":
            self.ox = width // 2 - 14
            self.oy = height // 2 - 12
            self.bw = 28
            self.bh = 26
            self.y = y - height // 2
        else:
            self.ox = 4
            self.oy = 4
            self.bw = width - 8
            self.bh = height - 4
            self.y = y - (self.oy + self.bh)
        self.x = x - width // 2
        self.dmg = t["dmg"]
        self.active = False
        self.dead = False
        self.facing = 1
        self.jump_cd = 0
        self.shoot_cd = random.randint(40, 120)
        self.phase = random.random() * 6.28
        self.dive = 0
        self.dive_cd = random.randint(60, 140)
        self.dive_vx = 0
        self.dive_vy = 0
        self.tank_cd = 0
        self.kb = 0
        self.update_hitbox()

    def pit_ahead(self, solids, oneways, d):
        # في حفرة قدامنا؟ بنمد خط من القدم لتحت، لو ما لمس شي يعني رح نقع
        r = self.body()
        px = r.right + 24 if d > 0 else r.left - 24
        probe = pygame.Rect(px - 2, r.bottom, 4, 900 - r.bottom)
        for s in solids:
            if probe.colliderect(s.rect):
                return False
        for s in oneways:
            if probe.colliderect(s.rect):
                return False
        return True

    def update(self, p, solids, oneways, enemy_bullets):
        if self.hurt_time > 0:
            self.hurt_time -= 1
        if self.tank_cd > 0:
            self.tank_cd -= 1
        px, py = p.center()
        cx, cy = self.center()
        dx = px - cx
        ai = self.t["ai"]
        if self.kb > 0:
            self.kb -= 1
            self.vx *= 0.85
            if ai == "fly":
                # الخفاش بالهوا، بس بيرجع لورا
                self.x += self.vx
                self.update_hitbox()
            else:
                self.mover(solids, oneways)
            return
        # walk و tank بيمشوا على الارض، range بيحافظ على مسافة ويرمي، fly هو الخفاش
        if ai == "walk" or ai == "tank":
            if abs(dx) > 10:
                self.facing = 1 if dx > 0 else -1
            self.vx = self.facing * self.step
            if ai == "walk":
                if self.jump_cd > 0:
                    self.jump_cd -= 1
                elif self.on_ground and self.jump_cd <= 0:
                    # يقفز لو الجدار قدامه، او احيانا لو اللاعب فوقه
                    above = py < cy - 70 and abs(dx) < 260
                    if self.hit_wall or (above and random.random() < 0.03):
                        self.vy = -14.5
                        self.jump_cd = 40
            else:
                self.shoot_cd -= 1
                if self.shoot_cd <= 0 and abs(dx) < 750:
                    self.shoot_cd = 130
                    d = 1 if dx > 0 else -1
                    t = 55
                    g = 0.28
                    vy0 = (py - cy) / t - g * t / 2
                    vx = dx / t
                    enemy_bullets.append(Bullet(cx + d * 40, cy - 10, 8, (255, 140, 40), 1, vx, vy0, self.dmg, False, g, 120))
                    EFFECTS.burst(cx + d * 50, cy - 10, (255, 220, 120), 6, 3)
                if abs(dx) < 120:
                    self.vx = 0
            if self.vx and self.on_ground and self.pit_ahead(solids, oneways, 1 if self.vx > 0 else -1):
                self.vx = 0
            self.mover(solids, oneways)
        elif ai == "range":
            if abs(dx) > 10:
                self.facing = 1 if dx > 0 else -1
            dist = abs(dx)
            if dist < 260:
                self.vx = -self.facing * self.step
            elif dist > 460:
                self.vx = self.facing * self.step
            else:
                self.vx = 0
            if self.vx and self.on_ground and self.pit_ahead(solids, oneways, 1 if self.vx > 0 else -1):
                self.vx = 0
            self.shoot_cd -= 1
            if self.shoot_cd <= 0 and dist < 700:
                self.shoot_cd = 110
                ang = math.atan2(py - cy, dx)
                sp = 6
                enemy_bullets.append(Bullet(cx, cy - 6, 6, (255, 200, 60), 1, math.cos(ang) * sp, math.sin(ang) * sp, self.dmg, False, 0, 140))
            self.mover(solids, oneways)
        elif ai == "fly":
            self.phase += 0.06
            self.facing = 1 if dx > 0 else -1
            if self.dive > 0:
                self.dive -= 1
                self.x += self.dive_vx
                self.y += self.dive_vy
            else:
                self.dive_cd -= 1
                tx = px + math.cos(self.phase) * 160
                ty = py - 120 + math.sin(self.phase * 1.7) * 40
                self.x += max(-self.step, min(self.step, (tx - cx) * 0.05))
                self.y += max(-self.step, min(self.step, (ty - cy) * 0.05))
                if self.dive_cd <= 0 and abs(dx) < 400:
                    ang = math.atan2(py - cy, dx)
                    self.dive = 28
                    self.dive_cd = random.randint(110, 200)
                    self.dive_vx = math.cos(ang) * 7
                    self.dive_vy = math.sin(ang) * 7
            self.moves += 1
        self.update_hitbox()

    def hit(self, damage=1, direction=0):
        self.health_player -= damage
        self.hurt_time = 6
        if direction and self.t["ai"] != "tank":
            self.kb = 5
            self.vx = direction * 4
            if self.t["ai"] != "fly":
                self.vy = -4
        EFFECTS.burst(self.x + self.width // 2, self.y + self.height // 2, (120, 255, 120), 4, 3, 14)
        if self.health_player <= 0:
            self.dead = True
            return True
        return False

    def draw(self, screen, camx, color=RED):
        sx = self.x - camx
        if sx > 1280 or sx + self.width < 0:
            return
        left, right = sprites[self.kind]
        frames = right if self.facing > 0 else left
        if self.t["ai"] == "tank":
            n = 2
            img = frames[(self.moves // 8) % n]
            if abs(self.vx) > 0.1:
                self.moves += 1
        elif self.t["ai"] == "fly":
            img = frames[(self.moves // 4) % 3]
        else:
            if abs(self.vx) > 0.1 and self.on_ground:
                self.moves += 1
            img = frames[(self.moves // 3) % len(frames)]
        if self.hurt_time > 0:
            img = img.copy()
            img.fill((200, 200, 200, 0), special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(img, (sx, self.y))
        #pygame.draw.rect(screen, color, self.hitbox, 2) # THE HITBOX
        if self.health_player < self.health:
            bx = int(self.hitbox[0] - camx)
            by = int(self.hitbox[1] - 14)
            pygame.draw.rect(screen, RED, (bx, by, 44, 7))
            pygame.draw.rect(screen, green, (bx, by, int(44 * max(0, self.health_player) / self.health), 7))
