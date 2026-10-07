import pygame
import random
import math
from ABSOLUTE import aboslute
from BULLET import Bullet, Wave
import SKILLS
import EFFECTS
from ENEMY import tint_frames
RED = (255, 0, 0)

# البوسات
bosses = {
    "king":      dict(name="GOBLIN KING", hp=60, scale=2.8, tint=(255, 200, 90), spd=2.6, dmg=5, attacks=["charge", "slam"]),
    "warden":    dict(name="FOREST WARDEN", hp=90, scale=3.0, tint=(90, 230, 130), spd=2.2, dmg=5, attacks=["shoot", "summon", "rain"]),
    "ironbeast": dict(name="IRON BEAST", hp=130, scale=2.3, tint=None, spd=2.0, dmg=6, attacks=["shell", "charge", "summon", "rain"]),
    "knight":    dict(name="DARK KNIGHT", hp=170, scale=2.9, tint=(165, 120, 255), spd=3.2, dmg=6, attacks=["charge", "wave", "shoot", "slam"]),
    "overlord":  dict(name="THE OVERLORD", hp=260, scale=3.3, tint=(255, 80, 80), spd=3.0, dmg=7, attacks=["charge", "slam", "shoot", "summon", "rain", "wave"]),
}
boss_sprites = {}

def build_boss_sprites(move_leftE, move_rightE):
    for name, b in bosses.items():
        if name == "ironbeast":
            boss_sprites[name] = SKILLS.load_tank("foe", ["er1.png", "ergo1.png"], ["ew1.png", "ewgo1.png"], b["scale"])
        else:
            boss_sprites[name] = (tint_frames(move_leftE, b["tint"], b["scale"]), tint_frames(move_rightE, b["tint"], b["scale"]))

class Boss(aboslute):
    # الحالات: sleep > intro > idle > windup > act > recover > idle ...
    # ولما تخلص الصحة بيروح على dying ومنها dead
    def __init__(self, x, floor_y, kind, mult=1.0):
        b = bosses[kind]
        self.kind = kind
        self.info = b
        self.name = b["name"]
        frames = boss_sprites[kind][0]
        w = frames[0].get_width()
        h = frames[0].get_height()
        hp = int(b["hp"] * mult)
        aboslute.__init__(self, x, 0, w, h, b["spd"], len(frames), 0, hp)
        s = b["scale"]
        if kind == "ironbeast":
            self.ox = 6
            self.oy = 6
            self.bw = w - 12
            self.bh = h - 6
        else:
            self.ox = int(20 * s)
            self.oy = int(4 * s)
            self.bw = int(26 * s)
            self.bh = int(54 * s)
        self.floor_y = floor_y
        self.x = x - w // 2
        self.y = floor_y - (self.oy + self.bh)
        self.dmg = b["dmg"]
        self.state = "sleep"
        self.atk = None
        self.last_atk = None
        self.t = 0
        self.facing = -1
        self.dead = False
        self.warnings = []
        self.spawn_requests = []
        self.air = False
        self.fired = 0
        self.tank_cd = 0
        self.arena = (0, 99999)
        self.update_hitbox()

    def phase(self):
        r = self.health_player / self.health
        if r > 0.66:
            return 0
        if r > 0.33:
            return 1
        return 2

    def activate(self):
        if self.state == "sleep":
            self.state = "intro"
            self.t = 100
            EFFECTS.do_shake(20)

    def hit(self, damage=1, direction=0):
        if self.state in ("sleep", "intro", "dying") or self.dead:
            return False
        self.health_player -= damage
        self.hurt_time = 4
        EFFECTS.burst(self.x + self.width // 2, self.y + self.height // 2, (255, 230, 120), 3, 4, 12)
        if self.health_player <= 0:
            self.health_player = 0
            self.state = "dying"
            self.t = 100
            self.vx = 0
            self.warnings = []
            return True
        return False

    def aim(self, p):
        cx, cy = self.center()
        px, py = p.center()
        ang = math.atan2(py - cy, px - cx)
        return ang

    def update(self, p, solids, oneways, enemy_bullets):
        if self.dead:
            return
        if self.hurt_time > 0:
            self.hurt_time -= 1
        if self.tank_cd > 0:
            self.tank_cd -= 1
        cx, cy = self.center()
        px, py = p.center()
        ph = self.phase()
        if self.state == "sleep":
            self.mover(solids, oneways)
            return
        if self.state == "intro":
            self.t -= 1
            self.facing = 1 if px > cx else -1
            self.mover(solids, oneways)
            if self.t <= 0:
                self.state = "idle"
                self.t = 40
            return
        if self.state == "dying":
            self.t -= 1
            self.vx = 0
            if self.t % 4 == 0:
                EFFECTS.burst(self.x + random.randint(0, self.width), self.y + random.randint(0, self.height), (255, random.randint(120, 220), 60), 6, 6, 30, 6)
            if self.t % 20 == 0:
                EFFECTS.do_shake(10)
            self.mover(solids, oneways)
            if self.t <= 0:
                self.dead = True
                EFFECTS.burst(cx, cy, (255, 240, 160), 60, 10, 40, 8)
            return

        # علامات التحذير تحت المطر، لما يخلص وقتها بتنزل الكرة
        for w in self.warnings[:]:
            w[1] -= 1
            if w[1] <= 0:
                enemy_bullets.append(Bullet(w[0], -30, 15, (255, 100, 40), 1, 0, 7, self.dmg - 1, False, 0.25, 200))
                self.warnings.remove(w)

        if self.state == "idle":
            self.facing = 1 if px > cx else -1
            dist = abs(px - cx)
            self.vx = self.facing * self.step * 0.6 if dist > 220 else 0
            self.t -= 1
            if self.t <= 0:
                choices = [a for a in self.info["attacks"] if a != self.last_atk]
                self.atk = random.choice(choices)
                self.last_atk = self.atk
                self.state = "windup"
                self.t = {"charge": 35, "slam": 26, "shoot": 25, "summon": 40, "rain": 30, "wave": 25, "shell": 30}[self.atk]
                self.vx = 0
                self.fired = 0
            self.mover(solids, oneways)
        elif self.state == "windup":
            self.vx = 0
            self.t -= 1
            self.facing = 1 if px > cx else -1
            if self.t <= 0:
                self.state = "act"
                self.start_attack(p, enemy_bullets)
            self.mover(solids, oneways)
        elif self.state == "act":
            self.do_attack(p, solids, oneways, enemy_bullets, ph)
        elif self.state == "recover":
            self.vx = 0
            self.t -= 1
            if self.t <= 0:
                self.state = "idle"
                self.t = max(25, 65 - ph * 18)
            self.mover(solids, oneways)
        self.update_hitbox()

    def start_attack(self, p, enemy_bullets):
        cx, cy = self.center()
        px, py = p.center()
        self.t = 0
        ph = self.phase()
        if self.atk == "charge":
            self.vx = self.facing * (9 + ph * 2)
            self.t = 70
        elif self.atk == "slam":
            self.vy = -19
            self.vx = max(-8, min(8, (px - cx) / 45))
            self.air = True
            self.t = 5
        elif self.atk == "shoot":
            self.t = 0
            self.fired = 0
        elif self.atk == "summon":
            n = 2 + ph
            for i in range(n):
                kind = random.choice(["goblin", "runner", "bat"] if ph < 2 else ["runner", "bat", "archer"])
                off = random.choice([-1, 1]) * random.randint(140, 320)
                self.spawn_requests.append((kind, cx + off, self.floor_y if kind != "bat" else self.floor_y - 140))
            EFFECTS.ring(cx, cy, (200, 120, 255), 24, 6)
            self.state = "recover"
            self.t = 45
        elif self.atk == "rain":
            n = 5 + ph * 2
            for i in range(n):
                x = max(self.arena[0] + 60, min(self.arena[1] - 60, px + random.randint(-420, 420)))
                self.warnings.append([x, 45 + i * 9])
            self.state = "recover"
            self.t = 100
        elif self.atk == "wave":
            self.t = 0
            self.fired = 0
        elif self.atk == "shell":
            self.fire_shell(p, 0, enemy_bullets)
            if ph >= 1:
                self.fire_shell(p, 60, enemy_bullets)
            self.state = "recover"
            self.t = 50

    def fire_shell(self, p, offset, enemy_bullets):
        cx, cy = self.center()
        px, py = p.center()
        px += offset * self.facing
        t = 60
        g = 0.28
        vy0 = (py - cy) / t - g * t / 2
        vx = (px - cx) / t
        EFFECTS.burst(cx + self.facing * 80, cy - 10, (255, 220, 120), 8, 4)
        enemy_bullets.append(Bullet(cx + self.facing * 70, cy - 10, 10, (255, 140, 40), 1, vx, vy0, self.dmg, False, g, 140))

    def do_attack(self, p, solids, oneways, enemy_bullets, ph):
        cx, cy = self.center()
        px, py = p.center()
        if self.atk == "charge":
            self.t -= 1
            self.vx = self.facing * (9 + ph * 2)
            self.mover(solids, oneways)
            if self.t <= 0 or self.hit_wall:
                if self.hit_wall:
                    EFFECTS.do_shake(12)
                    EFFECTS.burst(cx + self.facing * 40, cy, (200, 200, 200), 12, 5)
                self.state = "recover"
                self.t = 45
                self.vx = 0
        elif self.atk == "slam":
            self.mover(solids, oneways)
            if self.t > 0:
                self.t -= 1
            elif self.on_ground:
                self.vx = 0
                EFFECTS.do_shake(18)
                EFFECTS.burst(cx, self.y + self.height, (220, 200, 160), 20, 6)
                for d in (-1, 1):
                    enemy_bullets.append(Wave(cx + d * 40, self.floor_y, 50, 38, d, 7 + ph, self.dmg - 1))
                self.state = "recover"
                self.t = 45
        elif self.atk == "shoot":
            self.vx = 0
            self.t -= 1
            self.mover(solids, oneways)
            if self.t <= 0:
                self.t = 14
                n = 3 + ph * 2
                base = self.aim(p)
                for k in range(n):
                    ang = base + math.radians((k - (n - 1) / 2) * 13)
                    enemy_bullets.append(Bullet(cx + self.facing * 30, cy - self.bh // 4, 7, (255, 150, 60), 1, math.cos(ang) * 6.5, math.sin(ang) * 6.5, self.dmg - 2, False, 0, 150))
                self.fired += 1
                if self.fired >= 2 + ph:
                    self.state = "recover"
                    self.t = 40
        elif self.atk == "wave":
            self.vx = 0
            self.t -= 1
            self.mover(solids, oneways)
            if self.t <= 0:
                self.t = 20
                enemy_bullets.append(Wave(cx + self.facing * 60, self.floor_y, 56, 74, self.facing, 8 + ph, self.dmg - 1, (190, 120, 255)))
                EFFECTS.do_shake(6)
                self.fired += 1
                if self.fired >= 1 + (1 if ph >= 1 else 0) + (1 if ph >= 2 else 0):
                    self.state = "recover"
                    self.t = 45

    def draw(self, screen, camx, color=RED):
        sx = self.x - camx
        if sx > 1280 or sx + self.width < 0:
            return
        left, right = boss_sprites[self.kind]
        frames = right if self.facing > 0 else left
        if abs(self.vx) > 0.1 and self.on_ground:
            self.moves += 1
        idx = (self.moves // 3) % len(frames) if self.kind != "ironbeast" else (self.moves // 6) % 2
        img = frames[idx]
        flash = None
        if self.state == "windup" and (self.t // 3) % 2 == 0:
            flash = (150, 0, 0, 0)
        if self.hurt_time > 0:
            flash = (160, 160, 160, 0)
        if self.state == "dying" and (self.t // 3) % 2 == 0:
            flash = (255, 255, 255, 0)
        if self.phase() == 2 and self.state not in ("dying",) and flash is None and (pygame.time.get_ticks() // 200) % 2 == 0:
            flash = (60, 0, 0, 0)
        if flash:
            img = img.copy()
            img.fill(flash, special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(img, (sx, self.y))
        #pygame.draw.rect(screen, color, self.hitbox, 2) # THE HITBOX
        for w in self.warnings:
            x = int(w[0] - camx)
            pygame.draw.rect(screen, (255, 60, 40), (x - 18, self.floor_y - 6, 36, 6))
            pygame.draw.polygon(screen, (255, 200, 60), [(x - 10, self.floor_y - 40), (x + 10, self.floor_y - 40), (x, self.floor_y - 14)])
