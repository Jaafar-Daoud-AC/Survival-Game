import pygame


class aboslute:
    def __init__(self, x, y, width, height, step, image_num, score, health_player):
        self.B = 50
        self.b = 5
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.width = width
        self.height = height
        self.step = step
        self.isjumping = False
        self.speed = 10
        self.image_num = image_num
        self.score = score
        self.moves = 0
        self.left = False
        self.right = True
        self.visible_player = True
        self.health_player = health_player
        self.health = health_player
        # الصندوق اللي نصطدم فيه، مو الصورة كلها
        self.ox = 20
        self.oy = 10
        self.bw = width - 40
        self.bh = height - 10
        self.vx = 0
        self.vy = 0
        self.gravity = 0.8
        self.max_fall = 18
        self.on_ground = False
        self.ground = None
        self.hit_wall = False
        self.hurt_time = 0
        self.hitbox = (self.x + self.ox, self.y + self.oy, self.bw, self.bh)

    def body(self):
        return pygame.Rect(int(self.x + self.ox), int(self.y + self.oy), self.bw, self.bh)

    def update_hitbox(self):
        self.hitbox = (int(self.x + self.ox), int(self.y + self.oy), self.bw, self.bh)

    def center(self):
        r = self.body()
        return r.centerx, r.centery

    def _inside_solid(self, solids):
        r = self.body()
        for s in solids:
            if r.colliderect(s.rect):
                return True
        return False

    def mover(self, solids, oneways, use_gravity=True):
        # لو واقفين على منصة متحركة بناخذ حركتها،
        # بس اذا دخلتنا بجدار او سقف منلغي الحركة وبتكمل المنصة لحالها
        if self.ground is not None:
            gx, gy = self.ground.dx, self.ground.dy
            if gx:
                self.x += gx
                if self._inside_solid(solids):
                    self.x -= gx
            if gy:
                self.y += gy
                if self._inside_solid(solids):
                    self.y -= gy

        self.x += self.vx
        self.hit_wall = False
        r = self.body()
        for s in solids:
            if r.colliderect(s.rect):
                if self.vx > 0:
                    self.x -= r.right - s.rect.left
                elif self.vx < 0:
                    self.x += s.rect.right - r.left
                else:
                    # واقفين بس تداخلنا مع شي (منصة دفتنا)، نطلع من اقرب جهة
                    if r.centerx < s.rect.centerx:
                        self.x -= r.right - s.rect.left
                    else:
                        self.x += s.rect.right - r.left
                self.hit_wall = True
                r = self.body()

        old_bottom = r.bottom
        if use_gravity:
            self.vy = min(self.vy + self.gravity, self.max_fall)
        self.y += self.vy
        self.on_ground = False
        self.ground = None
        r = self.body()
        for s in solids:
            if r.colliderect(s.rect):
                if self.vy > 0:
                    self.y -= r.bottom - s.rect.top
                    self.on_ground = True
                    self.ground = s
                elif self.vy < 0:
                    self.y += s.rect.bottom - r.top
                self.vy = 0
                r = self.body()

        # القدم لامسة سطح صلب بالضبط من غير ما تتداخل معه.
        # لازم نحسبها ارض، وإلا كل كم اطار بيصير "بالهوا" وتخرب الحركة والانيميشن
        if self.vy >= 0 and not self.on_ground:
            for s in solids:
                if s.rect.top == r.bottom and r.right > s.rect.left and r.left < s.rect.right:
                    self.y = s.rect.top - self.oy - self.bh
                    self.vy = 0
                    self.on_ground = True
                    self.ground = s
                    r = self.body()
                    break

        # الالواح الخشب بننزل عليها من فوق بس
        if self.vy >= 0:
            for p in oneways:
                if r.right > p.rect.left and r.left < p.rect.right:
                    if old_bottom <= p.rect.top + 4 + abs(p.dy) and r.bottom >= p.rect.top:
                        lift = r.bottom - p.rect.top
                        self.y -= lift
                        # لو رفعنا اللوح لجوا سقف ما منقف عليه
                        if self._inside_solid(solids):
                            self.y += lift
                            continue
                        self.vy = 0
                        self.on_ground = True
                        self.ground = p
                        r = self.body()
        self.update_hitbox()
