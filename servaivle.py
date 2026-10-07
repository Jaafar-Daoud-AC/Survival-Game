import pygame
import os
import sys
import json
import random
from PLAYER import player
from ENEMY import Enemy, build_sprites
from BOSS import Boss, build_boss_sprites
from BULLET import Wave
import PLATFORM
import SKILLS
import EFFECTS
import LEVELS
pygame.init()
base_dir = os.path.dirname(os.path.abspath(__file__))

# حجم النافذة
screen_width = 1280
screen_height = 720
try:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.RESIZABLE)
except pygame.error:
    screen = pygame.display.set_mode((screen_width, screen_height))
canvas = pygame.Surface((screen_width, screen_height))
pygame.display.set_caption("servaivle")

def load(*path):
    return pygame.image.load(os.path.join(base_dir, *path)).convert_alpha()

# صور اللاعب والاعداء
move_left = [load("hero", "L%d.png" % i) for i in range(1, 10)]
move_right = [load("hero", "R%d.png" % i) for i in range(1, 10)]

move_leftE = [load("enemy", "L%dE.png" % i) for i in range(1, 10)]
move_rightE = [load("enemy", "R%dE.png" % i) for i in range(1, 10)]

hero_left = load("hero", "L1.png")
hero_right = load("hero", "R1.png")

Enemy1_rightE = load("enemy", "R1E.png")
Enemy1_leftE = load("enemy", "L1E.png")

PLATFORM.load_images()
SKILLS.load_skill_images()
build_sprites(move_leftE, move_rightE)
build_boss_sprites(move_leftE, move_rightE)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 60)
clock = pygame.time.Clock()
bg_cache = {}

def get_bg(name, alpha=True):
    if name not in bg_cache:
        img = pygame.image.load(os.path.join(base_dir, "backgrounds", name))
        bg_cache[name] = img.convert_alpha() if alpha else img.convert()
    return bg_cache[name]

# خلفيات وضع البقاء (هدول الخلفيات القديمة للعبة)
survival_bgs = ["sv3.jpg", "vr.jpg", "sv1.jpg", "sv2.jpg"]
menu_bg = pygame.transform.smoothscale(get_bg("bg.jpg", False), (screen_width, screen_height))

font = pygame.font.SysFont("conicsans", 35, True, True)
font_big = pygame.font.SysFont("conicsans", 50, True, True)
font_title = pygame.font.SysFont("conicsans", 110, True, True)
font_small = pygame.font.SysFont("conicsans", 24, True, True)

sounds = {}
try:
    pygame.mixer.init()
    for n in ["shoot", "jump", "hit", "hurt", "pickup", "skill", "dash", "explode", "boss", "win", "select", "slam"]:
        sounds[n] = pygame.mixer.Sound(os.path.join(base_dir, "sounds", n + ".wav"))
        sounds[n].set_volume(0.35)
except (pygame.error, OSError):
    # ما في كرت صوت او ملف ناقص، نكمل اللعبة بدون صوت
    sounds = {}

def play(name):
    if name in sounds:
        sounds[name].play()

# التقدم المحفوظ، لو الملف خربان منبدا من الصفر
save_path = os.path.join(base_dir, "save.json")
save = {"done": 0, "best_wave": 0, "best_score": 0}
try:
    with open(save_path) as f:
        loaded = json.load(f)
    if isinstance(loaded, dict):
        for k in save:
            if isinstance(loaded.get(k), int) and not isinstance(loaded.get(k), bool):
                save[k] = max(0, loaded[k])
except (OSError, ValueError):
    pass
save["done"] = min(save["done"], 5)

def write_save():
    try:
        with open(save_path, "w") as f:
            json.dump(save, f)
    except OSError:
        pass

# مواقع الازرار الفعلية على الكيبورد (scancode)، عشان اللعبة تشتغل
# حتى لو لغة الكيبورد عربي وحروف الازرار ما بتطابق الانجليزي
PHYS = {pygame.K_a: 4, pygame.K_d: 7, pygame.K_e: 8, pygame.K_f: 9, pygame.K_m: 16,
        pygame.K_p: 19, pygame.K_r: 21, pygame.K_s: 22, pygame.K_w: 26}
PHYS_BACK = {v: k for k, v in PHYS.items()}
held_phys = set()

class MergedKeys:
    def __init__(self, real):
        self.real = real

    def __getitem__(self, k):
        if self.real[k]:
            return True
        sc = PHYS.get(k)
        return sc is not None and sc in held_phys

def get_keys():
    return MergedKeys(pygame.key.get_pressed())

# متغيرات اللعبة
health_hero = 30
speed_Bullet = 0
state = "menu"
mode = "story"
menu_pos = 0
select_pos = 0
level = None
lv_index = 0
world_w = 3000
platforms = []
solids = []
oneways = []
hazards = []
pickups = []
checkpoints = []
enemies = []
enemy_bullets = []
bullets = []
novas = []
allies = []
boss = None
boss_fight = False
arena_wall = None
arena_x0 = 0
camx = 0
cp = None
cp_score = 0
banner_text = ""
banner_timer = 0
hint_timer = 0
end_timer = 0
reward_text = []
frame = 0
# وضع البقاء
wave = 0
wave_queue = []
wave_delay = 0
wave_spawn_cd = 0

player1 = player(100, 576, 64, 64, 5, 9, 0, health_hero)

def new_player():
    global player1
    player1 = player(100, 576, 64, 64, 5, 9, 0, health_hero)
    sync_skills()

def sync_skills():
    s = set()
    for i in range(min(save["done"], len(SKILLS.rewards))):
        for r in SKILLS.rewards[i]:
            s.add(r)
    player1.unlocked = s

def say(text, seconds=2):
    global banner_text, banner_timer
    banner_text = text
    banner_timer = int(seconds * 60)

def load_level(index, from_checkpoint=None, survival_mode=False):
    global level, lv_index, platforms, solids, oneways, hazards, pickups, checkpoints, enemies
    global enemy_bullets, bullets, novas, allies, boss, boss_fight, arena_wall, arena_x0, camx, cp, cp_score
    global world_w, hint_timer, wave, wave_queue, wave_delay, end_timer
    lv_index = index
    level = LEVELS.survival() if survival_mode else LEVELS.all_levels[index]()
    world_w = level["world"]
    theme = level["theme"]
    platforms = []
    for s in level["solids"]:
        move = s[5] if len(s) > 5 else None
        platforms.append(PLATFORM.Platform(s[0], s[1], s[2], s[3], s[4], theme, move, s[1]))
    platforms.append(PLATFORM.Platform("wall", -60, -2000, 60, 4000, theme))
    platforms.append(PLATFORM.Platform("wall", world_w, -2000, 60, 4000, theme))
    solids = [p for p in platforms if p.solid]
    oneways = [p for p in platforms if not p.solid]
    hazards = []
    for x, w, y in level["spikes"]:
        hazards.append(PLATFORM.Hazard("spikes", x, y, w, theme))
    for x0, x1 in level["lavas"]:
        hazards.append(PLATFORM.Hazard("lava", x0, 672, x1 - x0, theme))
    player1.danger = [h.rect.inflate(90, 120) for h in hazards]
    pickups = [PLATFORM.Pickup(k, x, y) for k, x, y in level["pickups"]]
    checkpoints = [PLATFORM.Checkpoint(x, y) for x, y in level["checkpoints"]]
    enemies = []
    for kind, x, sy in level["enemies"]:
        enemies.append(Enemy(x, sy, kind, level["hp_mult"]))
    enemy_bullets = []
    bullets = []
    novas = []
    allies = []
    boss = None
    boss_fight = False
    arena_wall = None
    EFFECTS.clear_effects()
    if level["boss"]:
        b = level["boss"]
        boss = Boss(b["x"], GROUND_Y, b["kind"])
        boss.arena = (b["arena"], b["arena"] + screen_width)
        arena_x0 = b["arena"]
    start_x, start_y = level["start"]
    cp = None
    if from_checkpoint:
        # منبدا من اخر علم، ونشيل الاعداء والعناصر اللي وراه
        start_x, start_y = from_checkpoint
        cp = from_checkpoint
        enemies = [e for e in enemies if e.x > start_x + 100]
        pickups = [p for p in pickups if p.x > start_x]
        for c in checkpoints:
            if c.x <= start_x:
                c.active = True
    else:
        cp_score = 0
    player1.reset_state(start_x - 32, start_y - 62)
    player1.visible_player = True
    camx = max(0, min(world_w - screen_width, start_x - screen_width // 2))
    hint_timer = 600 if (index == 0 and not survival_mode) else 0
    end_timer = 0
    wave = 0
    wave_queue = []
    wave_delay = 90
    say(level["name"] if not survival_mode else "SURVIVAL", 2.5)

GROUND_Y = LEVELS.GROUND

def start_story(index):
    global state, mode
    mode = "story"
    new_player()
    player1.score = 0
    load_level(index)
    state = "play"

def start_survival():
    global state, mode
    mode = "survival"
    new_player()
    player1.score = 0
    load_level(0, None, True)
    state = "play"

def respawn():
    global state
    if mode == "survival":
        start_survival()
        return
    pos = cp if cp else None
    sc = cp_score
    load_level(lv_index, pos)
    player1.score = sc if pos else 0
    state = "play"

def take_damage_fall():
    player1.health_player -= 4
    play("hurt")
    EFFECTS.do_shake(8)
    if player1.health_player > 0:
        player1.respawn_safe()

# موجات الاعداء بوضع البقاء
def make_wave(n):
    global wave_queue
    pool = ["goblin", "runner"]
    if n >= 3:
        pool.append("archer")
    if n >= 4:
        pool.append("bat")
    if n >= 6:
        pool.append("brute")
    if n >= 8:
        pool.append("tank")
    count = min(28, 4 + n * 2)
    q = [random.choice(pool) for i in range(count)]
    wave_queue = q

def spawn_wave_enemy(kind):
    px = player1.x
    side = random.choice([-1, 1])
    x = 70 if side < 0 else world_w - 70
    if abs(x - px) < 600:
        x = world_w - 70 if side < 0 else 70
    e = Enemy(x, GROUND_Y if kind != "bat" else 300, kind, 1 + 0.12 * wave)
    e.active = True
    enemies.append(e)

def update_survival():
    global wave, wave_delay, boss, boss_fight, wave_spawn_cd
    if wave_queue:
        wave_spawn_cd -= 1
        if wave_spawn_cd <= 0:
            wave_spawn_cd = max(18, 55 - wave * 2)
            if len(enemies) < 14:
                spawn_wave_enemy(wave_queue.pop(0))
        return
    boss_alive = boss is not None and not boss.dead
    if len(enemies) == 0 and not boss_alive:
        if wave > 0 and wave_delay == 0:
            wave_delay = 150
            player1.score += 50 * wave
            say("WAVE %d CLEAR" % wave, 2)
            if wave > save["best_wave"]:
                save["best_wave"] = wave
            write_save()
            play("win")
            for i in range(2):
                pickups.append(PLATFORM.Pickup(random.choice(["heart", "energy"]), random.randint(200, world_w - 200), 580))
        if wave_delay > 0:
            wave_delay -= 1
            if wave_delay == 0:
                wave += 1
                if wave % 5 == 0:
                    kinds = ["king", "warden", "ironbeast", "knight", "overlord"]
                    boss = Boss(world_w // 2 + random.choice([-600, 600]), GROUND_Y, kinds[(wave // 5 - 1) % 5], 1 + 0.35 * (wave // 5 - 1))
                    boss.arena = (0, world_w)
                    boss.activate()
                    boss_fight = True
                    play("boss")
                    say("WAVE %d - BOSS: %s" % (wave, boss.name), 3)
                    make_wave(wave // 2)
                else:
                    boss = None
                    boss_fight = False
                    say("WAVE %d" % wave, 2)
                    make_wave(wave)

def kill_enemy(e):
    EFFECTS.burst(e.x + e.width // 2, e.y + e.height // 2, (120, 255, 120), 14, 6, 24, 5)
    play("hit")
    gain = e.t["score"]
    player1.score += gain
    player1.energy = min(player1.max_energy, player1.energy + 4)
    EFFECTS.add_text(e.x + e.width // 2, e.y - 10, "+%d" % gain, YELLOW)
    r = random.random()
    cx, cy = e.center()
    if r < 0.12:
        pickups.append(PLATFORM.Pickup("heart", cx, int(min(cy, 600))))
    elif r < 0.30:
        pickups.append(PLATFORM.Pickup("energy", cx, int(min(cy, 600))))
    elif r < 0.45:
        pickups.append(PLATFORM.Pickup("coin", cx, int(min(cy, 600))))

def damage_target(t, dmg, direction):
    if t.hit(dmg, direction):
        return True
    return False

def update_play():
    global camx, speed_Bullet, boss_fight, arena_wall, hint_timer, banner_timer, state, cp, cp_score, end_timer
    keys = get_keys()
    for p in platforms:
        p.update()
    speed_Bullet = player1.step - 5
    player1.move(keys, solids, oneways)
    if keys [pygame.K_s]:
        player1.shoot(bullets, speed_Bullet)
    for ev in player1.events:
        play(ev)
    if hint_timer > 0:
        hint_timer -= 1
    if banner_timer > 0:
        banner_timer -= 1

    pcx, pcy = player1.center()
    pbody = player1.body()

    if mode == "survival":
        update_survival()

    # اول ما اللاعب يعدي خط البوس نسكر الساحة وراه
    if mode == "story" and boss and not boss_fight and not boss.dead and player1.x > level["boss"]["trigger"]:
        boss_fight = True
        arena_wall = PLATFORM.Platform("wall", arena_x0 - 60, -2000, 60, 4000, level["theme"])
        platforms.append(arena_wall)
        solids.append(arena_wall)
        boss.activate()
        play("boss")
        say("BOSS: " + boss.name, 3)

    for e in enemies[:]:
        if not e.active and abs(e.x - player1.x) < 1100:
            e.active = True
        if not e.active:
            continue
        e.update(player1, solids, oneways, enemy_bullets)
        if e.y > 900 or e.x < -200 or e.x > world_w + 200:
            enemies.remove(e)
            continue
        if e.dead:
            continue
        if pbody.colliderect(e.body()):
            if player1.dash_time > 0:
                if id(e) not in player1.dash_hit:
                    player1.dash_hit.add(id(e))
                    e.hit(3, 1 if e.x > player1.x else -1)
                    EFFECTS.do_shake(4)
            elif player1.hurt(e.dmg, e.x + e.width // 2):
                pass

    if boss and boss.state != "sleep":
        boss.update(player1, solids, oneways, enemy_bullets)
        for req in boss.spawn_requests:
            if len(enemies) < 9:
                kind, x, sy = req
                lo, hi = boss.arena
                x = max(lo + 60, min(hi - 60, x))
                ne = Enemy(x, sy, kind, 1.0)
                ne.active = True
                enemies.append(ne)
        boss.spawn_requests = []
        if boss.state not in ("intro", "dying") and not boss.dead and pbody.colliderect(boss.body()):
            if player1.dash_time > 0:
                if id(boss) not in player1.dash_hit:
                    player1.dash_hit.add(id(boss))
                    boss.hit(3, 0)
            else:
                player1.hurt(boss.dmg, boss.x + boss.width // 2)
        if boss.dead:
            on_boss_dead()

    for b in bullets[:]:
        b.update(solids)
        hit = False
        r = b.rect()
        targets = [e for e in enemies if e.active and not e.dead]
        if boss and boss.state not in ("sleep", "intro", "dying") and not boss.dead:
            targets.append(boss)
        for t in targets:
            if r.colliderect(t.body()):
                t.hit(b.damage, 1 if b.step > 0 else -1)
                player1.score += 1
                player1.energy = min(player1.max_energy, player1.energy + 2)
                if player1.health_player < player1.health:
                    player1.health_player += 0.3
                play("hit")
                hit = True
                break
        if hit or b.dead:
            if hit:
                EFFECTS.burst(b.x, b.y, (255, 220, 120), 5, 3, 12)
            bullets.remove(b)

    for b in enemy_bullets[:]:
        b.update(solids)
        if b.dead:
            enemy_bullets.remove(b)
            continue
        if b.rect().colliderect(pbody):
            if isinstance(b, Wave):
                player1.hurt(b.damage, b.x)
            else:
                if player1.shield > 0:
                    EFFECTS.ring(b.x, b.y, (140, 220, 255), 10, 4)
                else:
                    player1.hurt(b.damage, b.x)
                enemy_bullets.remove(b)

    for n in novas[:]:
        targets = [e for e in enemies if not e.dead]
        if boss and boss.state not in ("sleep", "intro", "dying") and not boss.dead:
            targets.append(boss)
        n.update(targets, enemy_bullets, player1.damage())
        if n.dead:
            novas.remove(n)
    for a in allies[:]:
        a.update(solids, oneways, bullets, player1.damage())
        ar = pygame.Rect(int(a.x), int(a.y), a.width, a.height)
        targets = [e for e in enemies if not e.dead]
        if boss and boss.state not in ("sleep", "intro", "dying") and not boss.dead:
            targets.append(boss)
        for t in targets:
            if ar.colliderect(t.body()):
                if t.tank_cd <= 0:
                    t.hit(3 * player1.damage(), a.direction)
                    t.tank_cd = 12
        if a.dead:
            allies.remove(a)

    for e in enemies[:]:
        if e.dead:
            kill_enemy(e)
            enemies.remove(e)

    # الاشواك والحمم والسقوط بالحفر
    pr = player1.body()
    for h in hazards:
        if pr.colliderect(h.hit_rect()):
            if h.kind == "spikes":
                if player1.hurt(4, h.rect.centerx):
                    player1.vy = -10
            else:
                EFFECTS.burst(pr.centerx, 680, (255, 150, 40), 16, 6)
                take_damage_fall()
    if player1.y > 800:
        take_damage_fall()
    # بعد السقطة اللاعب بيرجع لمكان ثاني، لازم نعيد حساب مكانه
    pr = player1.body()

    for p in pickups[:]:
        if p.rect().colliderect(pr):
            collect(p)
            pickups.remove(p)

    for c in checkpoints:
        if not c.active and c.rect().colliderect(pr):
            for o in checkpoints:
                o.active = False
            c.active = True
            cp = (c.x, c.y)
            cp_score = player1.score
            player1.health_player = min(player1.health, player1.health_player + 6)
            EFFECTS.add_text(c.x, c.y - 90, "CHECKPOINT", (120, 255, 160))
            EFFECTS.burst(c.x, c.y - 40, (120, 255, 160), 14, 5)
            play("pickup")

    # بالقتال الكاميرا بتتثبت على الساحة
    if boss_fight and mode == "story" and not boss.dead:
        target = arena_x0
    else:
        look = 90 if player1.right else -90
        target = player1.x + 32 + look - screen_width // 2
    camx += (target - camx) * 0.1
    camx = max(0, min(world_w - screen_width, camx))

    EFFECTS.update_effects()

    if player1.health_player <= 0:
        player1.health_player = 0
        player1.visible_player = False
        EFFECTS.burst(pcx, pcy, (255, 60, 60), 30, 8, 40, 6)
        play("explode")
        if mode == "survival":
            if wave > save["best_wave"]:
                save["best_wave"] = wave
            if player1.score > save["best_score"]:
                save["best_score"] = player1.score
            write_save()
        state = "dead"

    # بعد موت البوس نستنى شوي قبل شاشة النهاية
    if end_timer > 0:
        end_timer -= 1
        if end_timer == 0:
            state = "complete"
            play("win")

def collect(p):
    k = p.kind
    play("pickup")
    if k == "heart":
        player1.health_player = min(player1.health, player1.health_player + 6)
        EFFECTS.add_text(p.x, p.y - 20, "+HP", (255, 100, 120))
    elif k == "energy":
        player1.energy = min(player1.max_energy, player1.energy + 40)
        EFFECTS.add_text(p.x, p.y - 20, "+ENERGY", (120, 200, 255))
    elif k == "coin":
        player1.score += 10
        EFFECTS.add_text(p.x, p.y - 20, "+10", YELLOW)
    elif k == "rapid":
        player1.rapid = 600
        EFFECTS.add_text(p.x, p.y - 20, "RAPID FIRE", (255, 170, 40))
    elif k == "power":
        player1.power = 600
        EFFECTS.add_text(p.x, p.y - 20, "DOUBLE DAMAGE", (230, 110, 240))
    EFFECTS.burst(p.x, p.y, (255, 255, 200), 6, 3, 14)

def on_boss_dead():
    global boss_fight, end_timer, reward_text, boss
    if mode == "survival":
        player1.score += 200
        for i in range(5):
            pickups.append(PLATFORM.Pickup(random.choice(["heart", "energy", "coin"]), random.randint(300, world_w - 300), 580))
        boss = None
        boss_fight = False
        play("win")
        return
    if end_timer > 0 or state != "play":
        return
    play("explode")
    player1.score += 150
    for i in range(6):
        pickups.append(PLATFORM.Pickup("coin", int(boss.x + boss.width // 2 + (i - 3) * 40), 560))
    if arena_wall in solids:
        solids.remove(arena_wall)
        platforms.remove(arena_wall)
    boss_fight = False
    end_timer = 150
    reward_text = []
    for r in SKILLS.rewards[lv_index]:
        reward_text.append(SKILLS.names[r])
    if save["done"] <= lv_index:
        save["done"] = lv_index + 1
        write_save()
    sync_skills()

# ---- الرسم ----
def draw_text_center(text, y, fnt, color, shadow=True, surf=None):
    surf = surf or screen
    img = fnt.render(text, True, color)
    if shadow:
        sh = fnt.render(text, True, BLACK)
        surf.blit(sh, (screen_width // 2 - sh.get_width() // 2 + 3, y + 3))
    surf.blit(img, (screen_width // 2 - img.get_width() // 2, y))

def draw_background():
    th = LEVELS.themes[level["theme"]]
    if mode == "survival":
        name = survival_bgs[((wave - 1) // 3) % len(survival_bgs)] if wave > 0 else survival_bgs[0]
        key = "s_" + name
        if key not in bg_cache:
            bg_cache[key] = pygame.transform.smoothscale(get_bg(name, False), (screen_width, screen_height))
        canvas.blit(bg_cache[key], (0, 0))
        return
    canvas.blit(get_bg(th["sky"], False), (0, 0))
    for name, f in th["layers"]:
        img = get_bg(name)
        off = int(camx * f) % screen_width
        canvas.blit(img, (-off, 0))
        canvas.blit(img, (screen_width - off, 0))

def redrawGame():
    global frame
    frame += 1
    draw_background()
    for p in platforms:
        p.draw(canvas, camx)
    for h in hazards:
        h.draw(canvas, camx)
    for c in checkpoints:
        c.draw(canvas, camx)
    for p in pickups:
        p.draw(canvas, camx)
    for e in enemies:
        if e.active:
            e.draw(canvas, camx, RED)
    if boss and boss.state != "sleep":
        boss.draw(canvas, camx, RED)
    for a in allies:
        a.draw(canvas, camx)
    player1.draw(canvas, camx, hero_left, hero_right, move_right, move_left, RED)
    for b in bullets:
        b.draw(canvas, camx)
    for b in enemy_bullets:
        b.draw(canvas, camx)
    for n in novas:
        n.draw(canvas, camx)
    EFFECTS.draw_effects(canvas, camx)
    ox = oy = 0
    if EFFECTS.shake > 0:
        ox = random.randint(-EFFECTS.shake, EFFECTS.shake) // 2
        oy = random.randint(-EFFECTS.shake, EFFECTS.shake) // 2
        screen.fill(BLACK)
    screen.blit(canvas, (ox, oy))
    draw_hud()
    pygame.display.update()

def draw_hud():
    player1.draw_hud(screen)
    txt = font_small.render(level["name"] if mode == "story" else "WAVE %d" % wave, True, BLACK)
    screen.blit(txt, (20, 14))
    if mode == "survival":
        b = font_small.render("best wave = %d" % save["best_wave"], True, BLACK)
        screen.blit(b, (20, 44))
    if boss and boss.state not in ("sleep",) and not boss.dead:
        w = 620
        x = screen_width // 2 - w // 2 - 120
        pygame.draw.rect(screen, (60, 0, 0), (x, 20, w, 24))
        pygame.draw.rect(screen, (255, 140, 30), (x, 20, int(w * max(0, boss.health_player) / boss.health), 24))
        for k in (1, 2):
            pygame.draw.line(screen, BLACK, (x + int(w * k / 3), 20), (x + int(w * k / 3), 44), 2)
        pygame.draw.rect(screen, BLACK, (x, 20, w, 24), 3)
        nm = font_small.render(boss.name, True, WHITE)
        screen.blit(nm, (x + w // 2 - nm.get_width() // 2, 48))
    if banner_timer > 0:
        a = min(255, banner_timer * 6)
        img = font_big.render(banner_text, True, WHITE)
        img.set_alpha(a)
        sh = font_big.render(banner_text, True, BLACK)
        sh.set_alpha(a)
        screen.blit(sh, (screen_width // 2 - img.get_width() // 2 + 3, 183))
        screen.blit(img, (screen_width // 2 - img.get_width() // 2, 180))
    if hint_timer > 0:
        lines = ["ARROWS = move     SPACE = jump     S = shoot", "UP / DOWN = speed     P = pause"]
        for i, l in enumerate(lines):
            t = font_small.render(l, True, BLACK)
            screen.blit(t, (screen_width // 2 - t.get_width() // 2, 260 + i * 28))

def draw_overlay(alpha=150):
    s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    screen.blit(s, (0, 0))

menu_items = ["STORY MODE", "SURVIVAL MODE", "CONTROLS", "QUIT"]
menu_anim = 0

def draw_menu():
    global menu_anim
    menu_anim += 1
    screen.blit(menu_bg, (0, 0))
    pygame.draw.rect(screen, (70, 150, 40), (0, 640, screen_width, 80))
    pygame.draw.rect(screen, (50, 190, 30), (0, 640, screen_width, 10))
    hero = move_right[(menu_anim // 4) % 9]
    gob = move_leftE[(menu_anim // 4) % 9]
    screen.blit(pygame.transform.scale(hero, (192, 192)), (140, 454))
    screen.blit(pygame.transform.scale(gob, (192, 192)), (950, 454))
    draw_text_center("SURVIVAL", 50, font_title, (255, 240, 120))
    for i, item in enumerate(menu_items):
        col = YELLOW if i == menu_pos else WHITE
        draw_text_center(("> " if i == menu_pos else "") + item, 230 + i * 70, font_big, col)
    s = font_small.render("best wave = %d     best score = %d     levels done = %d/5" % (save["best_wave"], save["best_score"], save["done"]), True, BLACK)
    screen.blit(s, (screen_width // 2 - s.get_width() // 2, 660))
    pygame.display.update()

def draw_select():
    screen.blit(menu_bg, (0, 0))
    draw_overlay(90)
    draw_text_center("SELECT LEVEL", 50, font_big, WHITE)
    names = ["THE CITY", "THE FOREST", "THE DESERT", "THE CASTLE", "THE VOLCANO"]
    for i, n in enumerate(names):
        x = 90 + i * 232
        box = pygame.Rect(x, 220, 210, 260)
        open_ = i <= save["done"]
        th = ["city", "forest", "desert", "castle", "volcano"][i]
        img = pygame.transform.smoothscale(get_bg(LEVELS.themes[th]["sky"], False), (190, 120))
        pygame.draw.rect(screen, (30, 30, 40), box)
        screen.blit(img, (x + 10, 230))
        if not open_:
            s = pygame.Surface((190, 120), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (x + 10, 230))
        t = font_small.render("%d  %s" % (i + 1, n), True, WHITE if open_ else (110, 110, 120))
        screen.blit(t, (x + 105 - t.get_width() // 2, 365))
        if open_ and i < save["done"]:
            c = font_small.render("DONE", True, (120, 255, 160))
            screen.blit(c, (x + 105 - c.get_width() // 2, 400))
        elif not open_:
            c = font_small.render("LOCKED", True, (200, 90, 90))
            screen.blit(c, (x + 105 - c.get_width() // 2, 400))
        pygame.draw.rect(screen, YELLOW if i == select_pos else BLACK, box, 4)
    draw_text_center("LEFT / RIGHT  choose        ENTER  start        ESC  back", 560, font_small, WHITE)
    pygame.display.update()

def draw_controls():
    screen.blit(menu_bg, (0, 0))
    draw_overlay(130)
    draw_text_center("CONTROLS", 30, font_big, WHITE)
    lines = ["LEFT / RIGHT   move", "SPACE   jump  (press twice for double jump)", "S   shoot  (hold for auto fire)",
             "UP / DOWN   run faster / slower", "D   dash  (invincible)", "A   triple shot", "F   shield  (blocks bullets)",
             "E   nova  (blast around you)", "R   tank ultimate  (full energy)", "P   pause       F11   fullscreen", "",
             "Skills unlock after each boss.", "ESC to go back"]
    for i, l in enumerate(lines):
        t = font_small.render(l, True, WHITE)
        screen.blit(t, (screen_width // 2 - 260, 110 + i * 38))
    pygame.display.update()

def draw_dead():
    draw_overlay(120)
    text = font_big.render("--END--", True, RED)
    text1 = font_big.render("--ENTER W FOR RESTART--", True, RED)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, 220))
    screen.blit(text1, (screen_width // 2 - text1.get_width() // 2, 290))
    if mode == "survival":
        t = font.render("wave %d   score %d" % (wave, player1.score), True, WHITE)
        screen.blit(t, (screen_width // 2 - t.get_width() // 2, 360))
    t = font_small.render("M = menu", True, WHITE)
    screen.blit(t, (screen_width // 2 - t.get_width() // 2, 410))
    pygame.display.update()

def draw_complete():
    draw_overlay(140)
    draw_text_center("LEVEL %d COMPLETE" % (lv_index + 1), 150, font_big, (120, 255, 160))
    draw_text_center("score = %d" % player1.score, 225, font, WHITE)
    y = 290
    if reward_text:
        draw_text_center("NEW ABILITY", y, font, YELLOW)
        for r in reward_text:
            y += 45
            draw_text_center(r, y, font, WHITE)
    draw_text_center("ENTER = continue", 520, font_small, WHITE)
    pygame.display.update()

def draw_win():
    screen.blit(menu_bg, (0, 0))
    draw_overlay(110)
    draw_text_center("YOU SURVIVED", 150, font_title, YELLOW)
    draw_text_center("final score = %d" % player1.score, 300, font_big, WHITE)
    draw_text_center("ENTER = menu", 400, font_small, WHITE)
    pygame.display.update()

def draw_paused():
    draw_overlay(130)
    draw_text_center("PAUSED", 250, font_big, WHITE)
    draw_text_center("P = resume      ESC = menu", 320, font_small, WHITE)
    pygame.display.update()

# ---- الاحداث ----
def quit_game():
    pygame.quit()
    sys.exit()

def handle_events():
    global state, menu_pos, select_pos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYUP:
            held_phys.discard(getattr(event, "scancode", None))
            continue
        if event.type == getattr(pygame, "WINDOWFOCUSLOST", -1):
            held_phys.clear()
            continue
        if event.type != pygame.KEYDOWN:
            continue
        sc = getattr(event, "scancode", None)
        if sc in PHYS_BACK:
            held_phys.add(sc)
        # نعتمد على مكان الزر الفعلي اذا كان واحد من ازرار اللعبة
        k = PHYS_BACK.get(sc, event.key)
        if k == pygame.K_F11:
            try:
                pygame.display.toggle_fullscreen()
            except pygame.error:
                # بعض الانظمة ما تدعم تبديل الشاشة الكاملة، نتجاهل
                pass
            continue
        if state == "menu":
            if k == pygame.K_UP:
                menu_pos = (menu_pos - 1) % len(menu_items)
                play("select")
            elif k == pygame.K_DOWN:
                menu_pos = (menu_pos + 1) % len(menu_items)
                play("select")
            elif k == pygame.K_RETURN:
                play("select")
                if menu_pos == 0:
                    select_pos = min(save["done"], 4)
                    state = "select"
                elif menu_pos == 1:
                    start_survival()
                elif menu_pos == 2:
                    state = "controls"
                else:
                    quit_game()
            elif k == pygame.K_ESCAPE:
                quit_game()
        elif state == "select":
            if k == pygame.K_LEFT:
                select_pos = max(0, select_pos - 1)
                play("select")
            elif k == pygame.K_RIGHT:
                select_pos = min(min(save["done"], 4), select_pos + 1)
                play("select")
            elif k == pygame.K_RETURN:
                start_story(select_pos)
            elif k == pygame.K_ESCAPE:
                state = "menu"
        elif state == "controls":
            if k in (pygame.K_ESCAPE, pygame.K_RETURN):
                state = "menu"
        elif state == "play":
            if k in (pygame.K_ESCAPE, pygame.K_p):
                state = "paused"
                continue
            for name in SKILLS.order:
                if k == SKILLS.skills[name]["key"] and player1.can_use(name):
                    player1.pay(name)
                    use_skill(name)
        elif state == "paused":
            if k == pygame.K_p:
                state = "play"
            elif k == pygame.K_ESCAPE:
                state = "menu"
        elif state == "dead":
            if k == pygame.K_w:
                respawn()
            elif k == pygame.K_m or k == pygame.K_ESCAPE:
                state = "menu"
        elif state == "complete":
            if k == pygame.K_RETURN:
                if lv_index >= 4:
                    state = "win"
                else:
                    load_level(lv_index + 1)
                    state = "play"
        elif state == "win":
            if k == pygame.K_RETURN:
                state = "menu"

def use_skill(name):
    if name == "dash":
        SKILLS.use_dash(player1)
    elif name == "triple":
        SKILLS.use_triple(player1, bullets, speed_Bullet)
    elif name == "shield":
        SKILLS.use_shield(player1)
    elif name == "nova":
        SKILLS.use_nova(player1, novas)
    elif name == "tank":
        SKILLS.use_tank(player1, allies)

def step():
    handle_events()
    if state == "menu":
        draw_menu()
    elif state == "select":
        draw_select()
    elif state == "controls":
        draw_controls()
    elif state == "play":
        update_play()
        if state == "play":
            redrawGame()
    elif state == "paused":
        draw_paused()
    elif state == "dead":
        EFFECTS.update_effects()
        redrawGame()
        draw_dead()
    elif state == "complete":
        draw_complete()
    elif state == "win":
        draw_win()

def main():
    while True:
        clock.tick(60)
        step()

if __name__ == "__main__":
    main()
