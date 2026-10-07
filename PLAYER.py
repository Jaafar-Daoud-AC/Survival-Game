import pygame

from ABSOLUTE import aboslute
from BULLET import Bullet
import SKILLS
import EFFECTS
screen_width = 1280
BLACK = (0, 0, 0)
RED = (255, 0, 0)
green = (0, 255, 0)
class player(aboslute):
    def __init__(self, x, y, width, height, step, image_num, score, health_player):
        aboslute.__init__(self, x, y, width, height, step, image_num, score, health_player)
        # مقاسات جسم اللاعب جوا الصورة
        self.ox = 20
        self.oy = 14
        self.bw = 24
        self.bh = 48
        self.energy = 100.0
        self.max_energy = 100
        self.unlocked = set()
        self.cool = {}
        self.invul = 0
        self.shield = 0
        self.dash_time = 0
        self.dash_dir = 1
        self.dash_hit = set()
        self.rapid = 0
        self.power = 0
        self.shoot_cool = 0
        self.max_bullets = 5
        self.jumps_left = 1
        self.coyote = 0
        self.jump_buffer = 0
        self.space_held = False
        self.kb = 0
        self.standing = True
        self.last_safe = (x, y)
        # حوالين الاشواك والحمم، هون ما منسجل مكان آمن
        self.danger = []
        self.ghosts = []
        self.events = []
        self.font = pygame.font.SysFont("conicsans", 35, True, True)
        self.font_s = pygame.font.SysFont("conicsans", 22, True, True)

    def damage(self):
        if self.power > 0:
            return 2
        return 1

    def max_jumps(self):
        if "doublejump" in self.unlocked:
            return 2
        return 1

    def draw(self, screen, camx, hero_left, hero_right, move_right, move_left, color=RED):
        self.color = color
        self.move_right = move_right
        self.move_left = move_left
        self.hero_left = hero_left
        self.hero_right = hero_right
        if self.dash_time > 0:
            self.ghosts.append((self.x, self.y, self.right))
        elif self.ghosts:
            self.ghosts.pop(0)
        if len(self.ghosts) > 5:
            self.ghosts.pop(0)
        for i, (gx, gy, gr) in enumerate(self.ghosts):
            img = (hero_right if gr else hero_left).copy()
            img.set_alpha(40 + i * 25)
            screen.blit(img, (gx - camx, gy))
        if not self.visible_player:
            return
        if not self.on_ground:
            img = self.hero_right if self.right else self.hero_left
        elif self.standing:
            img = self.hero_right if self.right else self.hero_left
        elif self.left:
            img = self.move_left[self.moves // 3]
        else:
            img = self.move_right[self.moves // 3]
        if self.hurt_time > 0:
            img = img.copy()
            img.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_ADD)
        blink = self.invul > 0 and self.shield <= 0 and self.dash_time <= 0 and (self.invul // 4) % 2 == 0
        if not blink:
            screen.blit(img, (self.x - camx, self.y))
        if self.shield > 0:
            cx, cy = self.center()
            r = 44 + (self.shield // 6) % 3
            surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            a = 90 if self.shield > 60 else 40 + (self.shield % 10) * 6
            pygame.draw.circle(surf, (120, 200, 255, a), (r + 2, r + 2), r)
            pygame.draw.circle(surf, (200, 240, 255, 220), (r + 2, r + 2), r, 3)
            screen.blit(surf, (cx - camx - r - 2, cy - r - 2))
        #pygame.draw.rect(screen, self.color, self.hitbox, 2) # THE HITBOX

    def draw_hud(self, screen, level_text=""):
        x0 = 930
        text = self.font.render("score = " + str(self.score), True, BLACK)
        screen.blit(text, (x0, 6))
        pygame.draw.rect(screen, RED, (x0, 46, 300, 26))
        hp = min(1.0, max(0, self.health_player) / self.health)
        pygame.draw.rect(screen, green, (x0, 46, int(300 * hp), 26))
        pygame.draw.rect(screen, BLACK, (x0, 46, 300, 26), 2)
        pygame.draw.rect(screen, (30, 40, 80), (x0, 78, 300, 12))
        pygame.draw.rect(screen, (70, 170, 255), (x0, 78, int(300 * self.energy / self.max_energy), 12))
        pygame.draw.rect(screen, BLACK, (x0, 78, 300, 12), 2)
        sx = x0
        for name in SKILLS.order:
            s = SKILLS.skills[name]
            box = pygame.Rect(sx, 98, 54, 46)
            have = name in self.unlocked
            pygame.draw.rect(screen, (40, 40, 50) if not have else (60, 70, 100), box)
            if have:
                ready = self.cool.get(name, 0) <= 0 and self.energy >= s["cost"]
                col = (255, 255, 255) if ready else (120, 120, 130)
                lab = self.font.render(s["label"], True, col)
                screen.blit(lab, (box.centerx - lab.get_width() // 2, box.y + 2))
                cd = self.cool.get(name, 0)
                if cd > 0:
                    h = int(box.h * cd / s["cooldown"])
                    cover = pygame.Surface((box.w, h), pygame.SRCALPHA)
                    cover.fill((0, 0, 0, 150))
                    screen.blit(cover, (box.x, box.y))
                small = self.font_s.render(str(s["cost"]), True, (150, 210, 255))
                screen.blit(small, (box.centerx - small.get_width() // 2, box.bottom - 20))
            else:
                lab = self.font.render("?", True, (90, 90, 100))
                screen.blit(lab, (box.centerx - lab.get_width() // 2, box.y + 6))
            pygame.draw.rect(screen, BLACK, box, 2)
            sx += 60
        ty = 152
        if self.rapid > 0:
            t = self.font_s.render("RAPID " + str(self.rapid // 60 + 1), True, (255, 170, 40))
            screen.blit(t, (x0, ty))
            ty += 22
        if self.power > 0:
            t = self.font_s.render("POWER " + str(self.power // 60 + 1), True, (230, 110, 240))
            screen.blit(t, (x0, ty))

    def move(self, keys, solids, oneways):
        self.events = []
        if self.hurt_time > 0:
            self.hurt_time -= 1
        if self.invul > 0:
            self.invul -= 1
        if self.shield > 0:
            self.shield -= 1
        if self.shoot_cool > 0:
            self.shoot_cool -= 1
        if self.rapid > 0:
            self.rapid -= 1
            self.max_bullets = 8
        else:
            self.max_bullets = 5
        if self.power > 0:
            self.power -= 1
        for k in list(self.cool):
            if self.cool[k] > 0:
                self.cool[k] -= 1
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + 0.09)

        use_gravity = True
        if self.dash_time > 0:
            # اثناء الاندفاع ما في جاذبية والسرعة ثابتة
            self.dash_time -= 1
            self.vx = self.dash_dir * 17
            self.vy = 0
            use_gravity = False
            self.left = self.dash_dir < 0
            self.right = self.dash_dir > 0
            self.standing = False
        elif self.kb > 0:
            self.kb -= 1
            self.vx *= 0.9
        else:
            if keys [pygame.K_LEFT]:
                self.right = False
                self.left = True
                self.vx = -self.step
                self.standing = False
            elif keys [pygame.K_RIGHT]:
                self.right = True
                self.left = False
                self.vx = self.step
                self.standing = False
            else:
                self.vx = 0
                self.standing = True
                self.moves = 0
        if keys [pygame.K_UP] and self.step <= 8:
            self.step += 1
        if keys [pygame.K_DOWN] and self.step >= 6:
            self.step -= 1

        if not self.standing and self.on_ground:
            self.moves += 1
            if self.moves >= self.image_num * 3:
                self.moves = 0

        # القفز: coyote هو وقت صغير بعد ما نترك الارض لسا نقدر نقفز فيه
        pressed = keys [pygame.K_SPACE] and not self.space_held
        self.space_held = keys [pygame.K_SPACE]
        if pressed:
            self.jump_buffer = 7
        elif self.jump_buffer > 0:
            self.jump_buffer -= 1
        if self.on_ground:
            self.coyote = 6
            self.jumps_left = self.max_jumps()
            self.isjumping = False
        else:
            if self.coyote > 0:
                self.coyote -= 1
                if self.coyote == 0:
                    self.jumps_left = min(self.jumps_left, self.max_jumps() - 1)
        if self.jump_buffer > 0 and self.dash_time <= 0:
            if self.coyote > 0:
                self.vy = -15.5
                self.coyote = 0
                self.jump_buffer = 0
                self.jumps_left = self.max_jumps() - 1
                self.isjumping = True
                self.events.append("jump")
                EFFECTS.burst(self.x + 32, self.y + 62, (220, 220, 220), 4, 2, 14, 3, 0.1)
            elif self.jumps_left > 0:
                self.vy = -14
                self.jumps_left -= 1
                self.jump_buffer = 0
                self.isjumping = True
                self.events.append("jump")
                EFFECTS.burst(self.x + 32, self.y + 62, (180, 220, 255), 8, 3, 18, 3, 0.05)
        if self.isjumping and self.vy < -6 and not keys [pygame.K_SPACE]:
            self.vy = -6

        self.mover(solids, oneways, use_gravity)
        if self.on_ground and self.ground is not None and self.ground.dx == 0 and self.ground.dy == 0:
            r = self.body()
            if self.ground.rect.left + 20 <= r.centerx <= self.ground.rect.right - 20:
                near_danger = False
                for z in self.danger:
                    if r.colliderect(z):
                        near_danger = True
                        break
                if not near_danger:
                    self.last_safe = (self.x, self.y)

    def shoot(self, bullets, speed_Bullet):
        # الحد بينحسب على الطلقات العادية بس، مو طلقات المهارات
        mine = 0
        for b in bullets:
            if b.tag == "shot":
                mine += 1
        if self.shoot_cool > 0 or mine >= self.max_bullets or not self.visible_player:
            return False
        self.shoot_cool = 6 if self.rapid > 0 else 12
        direction = 1 if self.right else -1
        cx, cy = self.center()
        color = (255, 60, 60) if self.power <= 0 else (240, 110, 255)
        bullets.append(Bullet(cx + direction * 14, cy - 6, 6 if self.power <= 0 else 8, color, direction, 15 + speed_Bullet, 0, self.damage(), True, 0, 60))
        self.events.append("shoot")
        return True

    def can_use(self, name):
        if name not in self.unlocked or name not in SKILLS.skills:
            return False
        s = SKILLS.skills[name]
        return self.cool.get(name, 0) <= 0 and self.energy >= s["cost"]

    def pay(self, name):
        s = SKILLS.skills[name]
        self.energy -= s["cost"]
        self.cool[name] = s["cooldown"]
        self.events.append("skill" if name != "dash" else "dash")

    def hurt(self, dmg, from_x=None):
        if self.invul > 0 or self.shield > 0 or self.dash_time > 0 or not self.visible_player:
            return False
        self.health_player -= dmg
        self.invul = 60
        self.hurt_time = 10
        self.kb = 10
        direction = 1
        if from_x is not None and self.x + 32 < from_x:
            direction = -1
        self.vx = direction * 6
        self.vy = -7
        self.score = max(0, self.score - 1)
        self.events.append("hurt")
        EFFECTS.do_shake(6)
        EFFECTS.burst(self.x + 32, self.y + 36, (255, 60, 60), 10, 5)
        return True

    def respawn_safe(self):
        # بعد السقطة نرجع لاخر مكان وقفنا فيه بامان
        self.x, self.y = self.last_safe
        self.vx = 0
        self.vy = 0
        self.invul = 90
        self.kb = 0
        self.dash_time = 0

    def reset_state(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.invul = 90
        self.shield = 0
        self.kb = 0
        self.dash_time = 0
        self.health_player = self.health
        self.energy = self.max_energy
        self.visible_player = True
        self.last_safe = (x, y)
        self.cool = {}
        self.rapid = 0
        self.power = 0
