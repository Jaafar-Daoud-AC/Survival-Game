# بيانات المراحل، كل عنصر: (النوع, x, y, العرض, الارتفاع)
GROUND = 640  # مستوى سطح الارض

# خلفية كل بيئة: السماء وطبقات بتتحرك بسرعات مختلفة
themes = {
    "city":    dict(name="THE CITY",    sky="city_sky.jpg",    layers=[("city_far.png", 0.2), ("city_near.png", 0.45)]),
    "forest":  dict(name="THE FOREST",  sky="forest_sky.jpg",  layers=[("forest_far.png", 0.15), ("forest_mid.png", 0.3), ("forest_near.png", 0.55)]),
    "desert":  dict(name="THE DESERT",  sky="desert_sky.jpg",  layers=[("desert_far.png", 0.15), ("desert_mid.png", 0.3), ("desert_near.png", 0.5)]),
    "castle":  dict(name="THE CASTLE",  sky="castle_sky.jpg",  layers=[("castle_far.png", 0.15), ("castle_mid.png", 0.3), ("castle_near.png", 0.55)]),
    "volcano": dict(name="THE VOLCANO", sky="volcano_sky.jpg", layers=[("volcano_far.png", 0.2), ("volcano_near.png", 0.5)]),
}

def ground(x0, x1):
    return ("ground", x0, GROUND, x1 - x0, 80)

def block(x, w, h):
    return ("block", x, GROUND - h, w, h + 80)

def top_block(x, w, h, surface):
    # مكعب فوق سطح عالي
    return ("block", x, surface - h, w, h)

def crate(x, n=1, stack=1):
    return ("crate", x, GROUND - 48 * stack, 48 * n, 48 * stack)

def ledge(x, y, w):
    return ("ledge", x, y, w, 16)

def mover(x, y, w, axis="x", rng=50, speed=0.025):
    return ("ledge", x, y, w, 16, (axis, rng, speed))

def stairs(x, n, w, dh, up=True):
    out = []
    for i in range(n):
        h = dh * (i + 1) if up else dh * (n - i)
        out.append(block(x + i * w, w, h))
    return out

def pyramid(x, n, w, dh):
    out = stairs(x, n, w, dh, True)
    for i in range(n - 1):
        out.append(block(x + (n + i) * w, w, dh * (n - 1 - i)))
    return out

def coins(x0, x1, y, n):
    out = []
    for i in range(n):
        out.append(("coin", x0 + (x1 - x0) * i // max(1, n - 1), y))
    return out

def level1():
    S = [ground(0, 1000), crate(520), crate(800, 1, 2)]
    S += [block(1000, 200, 110), block(1260, 200, 220), block(1520, 220, 330), block(1800, 320, 330), block(2180, 200, 220), block(2440, 200, 110)]
    S += [ground(2640, 3300), crate(2860), crate(3160, 1, 2)]
    S += [ledge(3350, 540, 110), ledge(3490, 470, 110)]
    S += [ground(3620, 4000), block(4000, 200, 120), ledge(4260, 400, 120), block(4440, 300, 360), ledge(4780, 280, 140), block(4960, 200, 240)]
    S += [ground(5160, 6680)]
    S += [ledge(5750, 520, 200), ledge(6150, 520, 200), ledge(5950, 400, 200)]
    E = [("goblin", 650, 640), ("goblin", 720, 640), ("goblin", 920, 640), ("runner", 960, 640),
         ("goblin", 1360, 420), ("archer", 1640, 310), ("archer", 1900, 310), ("goblin", 2040, 310), ("bat", 2000, 240),
         ("goblin", 2280, 420), ("runner", 2540, 530),
         ("goblin", 2780, 640), ("runner", 2960, 640), ("goblin", 3270, 640),
         ("goblin", 3700, 640), ("runner", 3780, 640), ("brute", 3900, 640),
         ("archer", 4100, 520), ("bat", 4350, 230), ("archer", 4560, 280), ("goblin", 4640, 280), ("bat", 4800, 200), ("goblin", 5060, 400),
         ("goblin", 5300, 640), ("runner", 5360, 640)]
    P = [("coin", 1100, 500), ("coin", 2540, 500), ("coin", 1360, 390), ("coin", 1620, 280), ("coin", 1900, 280), ("coin", 2280, 390)]
    P += [("energy", 1380, 395), ("heart", 2090, 280), ("heart", 3545, 440), ("coin", 3405, 510), ("rapid", 4560, 250), ("power", 4850, 250),
          ("energy", 5000, 370), ("heart", 5060, 370), ("coin", 3000, 560), ("coin", 3700, 600), ("heart", 5700, 600), ("energy", 5800, 600)]
    return dict(name="1  THE CITY", theme="city", world=6680, start=(100, 640), solids=S, enemies=E, pickups=P,
                checkpoints=[(2700, 640), (3680, 640), (5260, 640)], spikes=[(3000, 96, 640)], lavas=[],
                boss=dict(kind="king", x=6300, trigger=5480, arena=5400), hp_mult=1.0)

def level2():
    S = [ground(0, 1100), crate(480), crate(760, 1, 2)]
    S += [block(1100, 180, 120), block(1280, 180, 240), block(1460, 180, 360), block(1640, 680, 360)]
    S += [mover(2360, 330, 120, "x", 40, 0.030), mover(2560, 380, 120, "x", 40, 0.025), mover(2760, 330, 120, "x", 40, 0.030)]
    S += [block(3000, 400, 240), block(3400, 200, 120), ground(3600, 4600)]
    S += [block(3900, 80, 96), block(4060, 80, 192), block(4220, 80, 96)]
    S += [ledge(4690, 540, 110), ledge(4860, 440, 110), ledge(5030, 340, 110), mover(5200, 380, 120, "y", 70, 0.03), block(5400, 300, 300), ground(5700, 7280)]
    S += [ledge(6400, 500, 200), ledge(6800, 500, 200), ledge(6600, 380, 200)]
    E = [("goblin", 600, 640), ("runner", 700, 640), ("goblin", 900, 640), ("goblin", 1000, 640),
         ("archer", 1900, 280), ("brute", 2100, 280), ("goblin", 2250, 280), ("bat", 2600, 230), ("bat", 2850, 280),
         ("archer", 3100, 400), ("archer", 3300, 400), ("goblin", 3500, 520),
         ("runner", 3700, 640), ("goblin", 3800, 640), ("brute", 4350, 640), ("runner", 4500, 640),
         ("bat", 4800, 300), ("bat", 5000, 240), ("archer", 5550, 340), ("goblin", 5620, 340),
         ("goblin", 5800, 640), ("runner", 5900, 640)]
    P = [("coin", 1190, 480), ("coin", 1370, 360), ("coin", 1550, 240), ("energy", 1900, 250), ("heart", 2250, 250),
         ("coin", 2420, 290), ("coin", 2620, 340), ("coin", 2820, 290), ("heart", 3200, 370), ("energy", 3300, 370),
         ("rapid", 4100, 410), ("coin", 3940, 520), ("coin", 4260, 520), ("heart", 4720, 510),
         ("coin", 4900, 410), ("power", 5085, 310), ("energy", 5550, 310), ("heart", 5600, 310), ("heart", 5900, 600)]
    return dict(name="2  THE FOREST", theme="forest", world=7280, start=(100, 640), solids=S, enemies=E, pickups=P,
                checkpoints=[(1060, 640), (3150, 400), (3640, 640), (5730, 640)], spikes=[(4400, 96, 640)], lavas=[],
                boss=dict(kind="warden", x=6900, trigger=6080, arena=6000), hp_mult=1.2)

def level3():
    S = [ground(0, 800), crate(400, 2)]
    S += pyramid(800, 3, 120, 100)
    S += [ground(1400, 2300)]
    S += [mover(2330, 570, 110, "x", 50, 0.030), mover(2550, 520, 110, "x", 50, 0.025), mover(2720, 570, 110, "x", 50, 0.030)]
    S += [ground(2820, 4000)]
    S += [block(3000, 80, 140), ledge(3080, 500, 200), block(3280, 80, 240), ledge(3360, 400, 200), block(3560, 80, 140)]
    S += [ledge(4080, 540, 100), ledge(4250, 470, 100), ledge(4420, 540, 100)]
    S += [ground(4560, 4900)]
    S += pyramid(4900, 4, 120, 100)
    S += [ground(5740, 7380)]
    S += [ledge(6500, 520, 200), ledge(6900, 520, 200), ledge(6700, 400, 200)]
    E = [("goblin", 300, 640), ("runner", 600, 640), ("archer", 1100, 340), ("tank", 1700, 640), ("brute", 1900, 640), ("runner", 2100, 640),
         ("bat", 2500, 300), ("bat", 2650, 350), ("goblin", 2900, 640), ("archer", 3180, 500), ("archer", 3450, 400),
         ("brute", 3850, 640), ("bat", 4200, 330), ("bat", 4400, 380), ("runner", 4650, 640), ("goblin", 4750, 640),
         ("archer", 5320, 240), ("bat", 5100, 200), ("tank", 5900, 640), ("goblin", 5800, 640), ("brute", 6000, 640)]
    P = [("coin", 860, 510), ("coin", 980, 410), ("heart", 1100, 310), ("energy", 1150, 310), ("coin", 1220, 410), ("coin", 1340, 510),
         ("coin", 2390, 520), ("coin", 2600, 470), ("coin", 2770, 520), ("heart", 3180, 470), ("rapid", 3450, 370), ("coin", 3320, 360),
         ("coin", 4130, 490), ("coin", 4300, 420), ("energy", 4470, 490), ("heart", 4600, 600), ("power", 5320, 210), ("heart", 5360, 210),
         ("energy", 5850, 600), ("heart", 6000, 600)]
    return dict(name="3  THE DESERT", theme="desert", world=7380, start=(100, 640), solids=S, enemies=E, pickups=P,
                checkpoints=[(1480, 640), (2860, 640), (4600, 640), (5800, 640)], spikes=[(3750, 128, 640)], lavas=[],
                boss=dict(kind="ironbeast", x=6900, trigger=6180, arena=6100), hp_mult=1.4)

def level4():
    S = [ground(0, 1000)]
    S += [mover(1040, 580, 110, "x", 40, 0.030), mover(1190, 540, 110, "x", 40, 0.025), mover(1330, 580, 110, "x", 40, 0.030)]
    S += [ground(1440, 1580), block(1580, 100, 120), block(1680, 100, 240), block(1780, 1100, 320)]
    for x in (1960, 2120, 2280, 2440, 2600):
        S.append(top_block(x, 60, 70, GROUND - 320))
    S += [ground(2880, 4100)]
    S += [ledge(3040, 540, 100), ledge(3170, 440, 100), block(3300, 140, 300)]
    S += [ledge(3500, 520, 100), ledge(3600, 400, 90), block(3700, 120, 380)]
    S += [ledge(4180, 540, 100), ledge(4340, 470, 100), ledge(4500, 540, 100)]
    S += [ground(4640, 5200)]
    S += stairs(5200, 5, 100, 70, True)
    S += [block(5700, 400, 420)]
    S += stairs(6100, 5, 100, 70, False)
    S += [ground(6600, 8180)]
    S += [ledge(7300, 520, 200), ledge(7700, 520, 200), ledge(7500, 400, 200)]
    E = [("goblin", 500, 640), ("brute", 700, 640), ("archer", 850, 640), ("runner", 950, 640),
         ("bat", 1150, 400), ("bat", 1300, 440),
         ("archer", 1900, 320), ("brute", 2050, 320), ("goblin", 2200, 320), ("archer", 2400, 320), ("brute", 2700, 320), ("bat", 2400, 230),
         ("goblin", 3000, 640), ("brute", 3200, 640), ("archer", 3370, 340), ("tank", 3500, 640), ("archer", 3760, 260), ("runner", 3900, 640), ("brute", 4000, 640),
         ("bat", 4250, 380), ("bat", 4450, 420), ("goblin", 4700, 640), ("archer", 4900, 640), ("runner", 5000, 640),
         ("archer", 5800, 220), ("brute", 5950, 220), ("brute", 5880, 220), ("bat", 5750, 130),
         ("goblin", 6700, 640), ("brute", 6900, 640), ("tank", 6800, 640), ("runner", 6750, 640)]
    P = [("coin", 1095, 540), ("coin", 1245, 500), ("coin", 1385, 540), ("heart", 1500, 600), ("coin", 1800, 270), ("energy", 2070, 280),
         ("heart", 2385, 280), ("heart", 2780, 270), ("coin", 3090, 500), ("coin", 3220, 400), ("rapid", 3370, 310), ("power", 3760, 230),
         ("coin", 4230, 500), ("coin", 4390, 430), ("energy", 4550, 500), ("heart", 4700, 600),
         ("heart", 5900, 190), ("energy", 5800, 190), ("heart", 6700, 600), ("energy", 6800, 600)]
    return dict(name="4  THE CASTLE", theme="castle", world=8180, start=(100, 640), solids=S, enemies=E, pickups=P,
                checkpoints=[(900, 640), (2900, 640), (4660, 640), (6700, 640)], spikes=[(3880, 96, 640), (4000, 96, 640)], lavas=[],
                boss=dict(kind="knight", x=7800, trigger=6980, arena=6900), hp_mult=1.7)

def level5():
    S = [ground(0, 900)]
    S += [ledge(960, 540, 100), ledge(1100, 470, 100), ledge(1240, 400, 100), ledge(1380, 470, 100)]
    S += [ground(1520, 2300), block(1700, 100, 100), block(1900, 100, 200)]
    S += [mover(2340, 560, 110, "x", 40, 0.030), ledge(2540, 500, 100), mover(2720, 450, 110, "y", 70, 0.030), ledge(2900, 400, 100), mover(3060, 480, 110, "x", 40, 0.030)]
    S += [ground(3200, 4200)]
    S += [crate(3500, 1, 1), crate(3800, 2, 1)]
    S += pyramid(4200, 4, 110, 90)
    S += [ground(4970, 5500)]
    S += [ledge(5560, 520, 90), mover(5700, 440, 110, "y", 80, 0.030), ledge(5880, 380, 100), mover(6040, 440, 110, "x", 50, 0.030), ledge(6190, 500, 100)]
    S += [ground(6300, 9230)]
    S += [ledge(6700, 520, 150), ledge(7000, 420, 150), ledge(7300, 520, 150)]
    S += [ledge(8350, 520, 200), ledge(8750, 520, 200), ledge(8550, 400, 200)]
    E = [("goblin", 450, 640), ("runner", 600, 640), ("brute", 780, 640), ("bat", 1100, 380), ("bat", 1300, 330),
         ("goblin", 1650, 640), ("archer", 1750, 540), ("brute", 2070, 640), ("runner", 2170, 640),
         ("bat", 2500, 400), ("bat", 2800, 330), ("bat", 3000, 400),
         ("goblin", 3350, 640), ("tank", 3650, 640), ("brute", 3960, 640), ("runner", 4050, 640), ("archer", 4100, 640),
         ("archer", 4590, 280), ("brute", 4650, 280), ("bat", 4600, 150), ("brute", 4800, 460),
         ("goblin", 5100, 640), ("runner", 5300, 640),
         ("bat", 5700, 340), ("bat", 5950, 300), ("bat", 6100, 380),
         ("brute", 6450, 640), ("archer", 6770, 520), ("tank", 6900, 640), ("archer", 7070, 420), ("brute", 7200, 640), ("archer", 7370, 520),
         ("runner", 7500, 640), ("goblin", 7600, 640), ("tank", 7700, 640)]
    P = [("coin", 1010, 500), ("coin", 1150, 430), ("coin", 1290, 360), ("heart", 1430, 430), ("energy", 2050, 600),
         ("coin", 2395, 520), ("coin", 2590, 460), ("coin", 2775, 400), ("coin", 2950, 360), ("heart", 3115, 440),
         ("heart", 3400, 600), ("rapid", 4650, 250), ("power", 4700, 250), ("energy", 4750, 250),
         ("coin", 5605, 480), ("coin", 5930, 340), ("heart", 6240, 460), ("heart", 6400, 600), ("energy", 6460, 600),
         ("heart", 7800, 600), ("energy", 7860, 600), ("heart", 7920, 600)]
    return dict(name="5  THE VOLCANO", theme="volcano", world=9230, start=(100, 640), solids=S, enemies=E, pickups=P,
                checkpoints=[(850, 640), (3260, 640), (5000, 640), (6400, 640), (7900, 640)],
                spikes=[(2000, 128, 640), (3600, 96, 640), (7450, 96, 640)], lavas=[(900, 1520), (2300, 3200), (5500, 6300)],
                boss=dict(kind="overlord", x=8700, trigger=8030, arena=7950), hp_mult=2.0)

def survival():
    S = [ground(0, 3000), crate(900), crate(1800, 2, 1), block(1300, 120, 70)]
    S += [ledge(300, 520, 220), ledge(700, 420, 240), ledge(1150, 520, 200), ledge(1500, 380, 260), ledge(1950, 520, 200), ledge(2300, 420, 240), ledge(2650, 520, 200)]
    P = [("heart", 800, 380), ("energy", 1600, 340), ("heart", 2400, 380), ("energy", 400, 480)]
    return dict(name="SURVIVAL", theme="forest", world=3000, start=(1500, 640), solids=S, enemies=[], pickups=P,
                checkpoints=[], spikes=[], lavas=[], boss=None, hp_mult=1.0)

all_levels = [level1, level2, level3, level4, level5]
