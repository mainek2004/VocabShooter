# vocab_shooter.py
# Vocabulary Shooter v1.3.1
# - Title & "Chọn chủ đề" tách riêng
# - Nền động gradient sáng-tối + bokeh
# - Súng & đạn to hơn, recoil + flash + khói
# - Enemy box thêm padding (chữ không dính mép trên)
# - Mỗi chủ đề 20 từ
# - Thêm viền bo khung game

import pygame, sys, random, json, os, math, time

# ---------------- Config chung ----------------
W, H = 1000, 650
FPS = 60
GROUND_Y = H - 90
BARREL_Y = GROUND_Y - 32
COLS = 5
TIME_LIMIT = 40.0  # giay cho ca van
DATA_FILE = "vocab_shooter_highscore.json"
TITLE = "Vocabulary Shooter"

# Kích thước & khung an toàn
BOX_W, BOX_H = 220, 78     # ô đáp án phía trên
GUN_W, GUN_H = 240, 72     # ⬅️ ô tiếng Anh (thu nhỏ để không bị tràn 2 mép)
BORDER_W = 8               # độ dày viền khung (draw_game_frame)
FRAME_OUTSET = 6           # outer rect: pygame.Rect(6,6,W-12,H-12)
FRAME_SAFE = 14            # đệm an toàn tránh bo góc/đổ bóng



# Mau sac
COL_TEXT = (40, 44, 52)
COL_BG = (245, 244, 250)
COL_PANEL = (205, 210, 240)
COL_PANEL_DARK = (180, 185, 225)
COL_BTN = (90, 95, 210)
COL_BTN_PRIMARY = (86, 168, 108)
COL_BTN_TXT = (255, 255, 255)
COL_GUN = (86, 98, 220)
COL_GUN_EDGE = (60, 70, 190)
COL_GUN_HL = (170, 180, 255)
COL_BULLET = (255, 208, 0)
COL_ENEMY = [(255,174,174),(255,218,146),(180,232,180),(173,216,255),(225,180,255)]
COL_ENEMY_DARK = [(240,140,140),(242,194,110),(145,210,145),(140,190,240),(205,150,240)]
COL_BAD = (220, 53, 69)

# ---------------- Vocab 20 tu moi chu de ----------------
VOCABS = {
    "Animals": [
        ("cat","con mèo"),("dog","con chó"),("bird","con chim"),("fish","con cá"),
        ("elephant","con voi"),("tiger","con hổ"),("monkey","con khỉ"),("cow","con bò"),
        ("pig","con heo"),("chicken","con gà"),("duck","con vịt"),("goat","con dê"),
        ("sheep","con cừu"),("horse","con ngựa"),("frog","con ếch"),("bear","con gấu"),
        ("snake","con rắn"),("deer","con nai"),("rabbit","con thỏ"),("fox","con cáo"),
    ],
    "Colors": [
        ("red","màu đỏ"),("blue","màu xanh dương"),("yellow","màu vàng"),("green","màu xanh lá"),
        ("black","màu đen"),("white","màu trắng"),("pink","màu hồng"),("orange","màu cam"),
        ("purple","màu tím"),("brown","màu nâu"),("gray","màu xám"),("cyan","màu lục lam"),
        ("magenta","màu cánh sen"),("beige","màu be"),("navy","xanh hải quân"),("teal","xanh mòng két"),
        ("maroon","nâu đỏ"),("lime","xanh chanh"),("violet","tím violet"),("gold","màu vàng kim"),
    ],
    "Food": [
        ("rice","cơm"),("noodles","mì"),("bread","bánh mì"),("milk","sữa"),
        ("egg","trứng"),("beef","thịt bò"),("pork","thịt heo"),("chicken","thịt gà"),
        ("fish","cá"),("vegetables","rau"),("salt","muối"),("sugar","đường"),
        ("soup","súp"),("cake","bánh ngọt"),("fruit","trái cây"),("banana","chuối"),
        ("apple","táo"),("orange","cam"),("water","nước"),("juice","nước ép"),
    ],
    "Jobs": [
        ("teacher","giáo viên"),("doctor","bác sĩ"),("engineer","kỹ sư"),("nurse","y tá"),
        ("chef","đầu bếp"),("police officer","cảnh sát"),("farmer","nông dân"),("student","sinh viên"),
        ("worker","công nhân"),("driver","tài xế"),("pilot","phi công"),("artist","hoạ sĩ"),
        ("singer","ca sĩ"),("actor","diễn viên"),("manager","quản lý"),("scientist","nhà khoa học"),
        ("lawyer","luật sư"),("dentist","nha sĩ"),("architect","kiến trúc sư"),("cashier","thu ngân"),
    ],
    "Verbs": [
        ("run","chạy"),("eat","ăn"),("drink","uống"),("sleep","ngủ"),("read","đọc"),
        ("write","viết"),("speak","nói"),("listen","nghe"),("play","chơi"),("study","học"),
        ("watch","xem"),("walk","đi bộ"),("jump","nhảy"),("swim","bơi"),("cook","nấu ăn"),
        ("draw","vẽ"),("open","mở"),("close","đóng"),("buy","mua"),("sell","bán"),
    ],
    "School": [
        ("book","sách"),("pen","bút"),("pencil","bút chì"),("ruler","thước"),
        ("eraser","cục gôm"),("bag","cặp"),("desk","bàn học"),("chair","ghế"),
        ("blackboard","bảng"),("homework","bài tập"),("notebook","vở"),("teacher","thầy cô"),
        ("student","học sinh"),("classroom","lớp học"),("library","thư viện"),("lesson","bài học"),
        ("exam","kỳ thi"),("score","điểm số"),("question","câu hỏi"),("answer","câu trả lời"),
    ],
}

# ---------------- Font helper ----------------
def _try_font(paths, size):
    for p in paths:
        if os.path.isfile(p):
            try:
                return pygame.font.Font(p, size)
            except:
                pass
    return None

def get_font(size, bold=False):
    base = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    fonts_dir = os.path.join(base, "fonts")
    if bold:
        candidates = [
            os.path.join(fonts_dir, "NotoSans-Bold.ttf"),
            os.path.join(fonts_dir, "DejaVuSans-Bold.ttf"),
            "C:\\Windows\\Fonts\\segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
    else:
        candidates = [
            os.path.join(fonts_dir, "NotoSans-Regular.ttf"),
            os.path.join(fonts_dir, "DejaVuSans.ttf"),
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]
    f = _try_font(candidates, size)
    if f: return f
    try:
        return pygame.font.SysFont("Segoe UI", size, bold=bold)
    except:
        return pygame.font.Font(None, size)

def render_fit_text(text, max_width, max_size=32, min_size=16, color=(30,30,35), bold=False):
    size = max_size
    while size >= min_size:
        font = get_font(size, bold=bold)
        surf = font.render(text, True, color)
        if surf.get_width() <= max_width:
            return surf, size
        size -= 2
    font = get_font(min_size, bold=bold)
    t = text
    while t and font.render(t + "...", True, color).get_width() > max_width:
        t = t[:-1]
    surf = font.render((t + "...") if t != text else t, True, color)
    return surf, min_size

def draw_text_center(surface, text, center_xy, max_width, max_size=32, min_size=16, color=(30,30,35), bold=False):
    surf, _ = render_fit_text(text, max_width, max_size, min_size, color, bold)
    surface.blit(surf, surf.get_rect(center=center_xy))

# ---------------- Luu diem ----------------
def load_high():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"highscore":0}
    return {"highscore":0}

def save_high(high):
    try:
        with open(DATA_FILE,"w",encoding="utf-8") as f:
            json.dump(high,f)
    except:
        pass

# ---------------- Ve khoi tien ich ----------------
def draw_shadow(surf, rect, radius=12, alpha=45):
    shadow = pygame.Surface((rect.w+20, rect.h+20), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0,0,0,alpha), shadow.get_rect(), border_radius=radius+8)
    surf.blit(shadow, (rect.x-10, rect.y-10))

def round_rect(surf, rect, color, radius=12):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

# ---------------- Nen dong ----------------
class BokehDot:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.r = random.uniform(8, 26)
        self.vx = random.uniform(-15, 15)
        self.vy = random.uniform(5, 28)
        self.alpha = random.randint(40, 90)

    def update(self, dt, w, h):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < -50: self.x = w + 50
        if self.x > w + 50: self.x = -50
        if self.y > h + 50:
            self.y = -50
            self.x = random.uniform(0, w)

    def draw(self, screen):
        s = pygame.Surface((int(self.r*2), int(self.r*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,255,255,self.alpha), (int(self.r), int(self.r)), int(self.r))
        screen.blit(s, (int(self.x-self.r), int(self.y-self.r)))

class GradientPulse:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.t = 0.0

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        k = (math.sin(self.t*0.6)+1)/2
        c1 = (int(220+35*k), int(230+20*k), 255)
        c2 = (int(200+20*k), 220, int(238+15*k))
        layers = 8
        for i in range(layers):
            y0 = int(i*self.h/layers)
            y1 = int((i+1)*self.h/layers)
            a = i/(layers-1)
            r = int(c1[0]*(1-a)+c2[0]*a)
            g = int(c1[1]*(1-a)+c2[1]*a)
            b = int(c1[2]*(1-a)+c2[2]*a)
            pygame.draw.rect(screen, (r,g,b), (0,y0,self.w,y1-y0))

# ---------------- UI Button ----------------
class Button:
    def __init__(self, x,y,w,h,text,onclick,color=COL_BTN,txt_color=COL_BTN_TXT):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
        self.onclick = onclick
        self.color = color
        self.txt_color = txt_color

    def draw(self, screen):
        draw_shadow(screen, self.rect, 12, 60)
        round_rect(screen, self.rect, self.color, 12)
        draw_text_center(screen, self.text, self.rect.center, max_width=self.rect.w-16, max_size=28, color=self.txt_color, bold=True)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and callable(self.onclick):
                self.onclick()

# ---------------- Enemy, Bullet ----------------
class Enemy:
    def __init__(self, x,y,w,h,text,is_correct,color):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
        self.is_correct = is_correct
        self.color = color
        self.pad_top = 6  # day chu xuong chut

    def draw(self, screen):
        draw_shadow(screen, self.rect, 14, 45)
        round_rect(screen, self.rect, self.color, 14)

        # Chu co dinh size 24px, cat bot neu qua dai
        pad = 22
        font = get_font(24, bold=False)
        max_w = self.rect.w - pad*2
        t = self.text
        surf = font.render(t, True, (30,30,35))
        if surf.get_width() > max_w:
            while t and font.render(t + "...", True, (30,30,35)).get_width() > max_w:
                t = t[:-1]
            surf = font.render((t + "...") if t else "", True, (30,30,35))

        center = (self.rect.centerx, self.rect.centery + self.pad_top)
        screen.blit(surf, surf.get_rect(center=center))

class Bullet:
    def __init__(self, x,y):
        self.x = x; self.y = y
        self.r = 8
        self.speed = 860

    def update(self, dt): self.y -= self.speed * dt
    def draw(self, screen): pygame.draw.circle(screen, COL_BULLET, (int(self.x), int(self.y)), self.r)
    @property
    def rect(self): return pygame.Rect(int(self.x-self.r), int(self.y-self.r), self.r*2, self.r*2)

# ---------------- Sung: recoil + flash + khoi ----------------
class SmokePuff:
    def __init__(self, x,y):
        self.x=float(x); self.y=float(y)
        self.r = random.uniform(5,11)
        self.vx = random.uniform(-22,22)
        self.vy = random.uniform(-32,-12)
        self.life = random.uniform(0.5,0.9)

    def update(self, dt):
        self.life -= dt
        self.x += self.vx*dt; self.y += self.vy*dt

    def draw(self, screen):
        if self.life<=0: return
        a = max(0, int(120*self.life))
        s = pygame.Surface((int(self.r*2),int(self.r*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (230,230,240,a), (int(self.r),int(self.r)), int(self.r))
        screen.blit(s, (int(self.x-self.r), int(self.y-self.r)))

    def alive(self): return self.life>0

class Player:
    def __init__(self, x):
        self.x = x
        self.cooldown = 0.0
        self.recoil_t = 0.0
        self.flash_t = 0.0
        self.smokes = []

    def update(self, dt):
        if self.cooldown>0: self.cooldown -= dt
        if self.recoil_t>0: self.recoil_t -= dt
        if self.flash_t>0: self.flash_t -= dt
        for s in self.smokes: s.update(dt)
        self.smokes = [s for s in self.smokes if s.alive()]

    def can_shoot(self): return self.cooldown<=0
    def shoot(self):
        self.cooldown = 0.22
        self.recoil_t = 0.12
        self.flash_t = 0.08
        for _ in range(3): self.smokes.append(SmokePuff(self.x, BARREL_Y-8))

    def draw(self, screen, word):
        recoil_px = 12*(self.recoil_t/0.12) if self.recoil_t>0 else 0
        gun_w, gun_h = GUN_W, GUN_H
        gx = int(self.x - gun_w//2)
        gy = GROUND_Y - gun_h - int(recoil_px)
        gun_rect = pygame.Rect(gx, gy, gun_w, gun_h)
        draw_shadow(screen, gun_rect, 16, 60)
        round_rect(screen, gun_rect, COL_GUN, 16)
        hl_rect = pygame.Rect(gx+12, gy+10, gun_w-24, 16)
        round_rect(screen, hl_rect, COL_GUN_HL, 8)
        barrel = pygame.Rect(int(self.x - 16), BARREL_Y - 28 - int(recoil_px), 32, 52)
        round_rect(screen, barrel, COL_GUN_EDGE, 10)
        ring = pygame.Rect(barrel.x-6, barrel.y-6, barrel.w+12, 12)
        round_rect(screen, ring, (220,230,255), 6)
        pad = 24
        draw_text_center(screen, word, gun_rect.center, max_width=gun_rect.w-pad*2, max_size=44, min_size=24, color=(255,255,255), bold=True)
        if self.flash_t>0:
            t = self.flash_t/0.08
            length = 36 + 44*t
            width = 18 + 10*t
            tip_x, tip_y = self.x, barrel.top - 6
            points = [(tip_x, tip_y - width//2),
                      (tip_x, tip_y + width//2),
                      (tip_x, tip_y - length)]
            pygame.draw.polygon(screen, (255,240,120), points)
        for s in self.smokes: s.draw(screen)
        font_small = get_font(22)
        hint = font_small.render("← → hoac A/D de chon cot  •  SPACE de ban", True, (60,60,70))
        screen.blit(hint, (20, H-28))

# ---------------- Explosion ----------------
class Particle:
    def __init__(self, x,y,color):
        self.x=float(x); self.y=float(y)
        ang = random.uniform(0, 2*math.pi)
        speed = random.uniform(190, 540)
        self.vx = math.cos(ang)*speed
        self.vy = math.sin(ang)*speed
        self.life = random.uniform(0.35, 0.7)
        self.size = random.randint(3,6)
        rc = (COL_BULLET[0]+color[0])//2
        gc = (COL_BULLET[1]+color[1])//2
        bc = (COL_BULLET[2]+color[2])//2
        self.color = (rc,gc,bc)
        self.gravity = 800

    def update(self, dt):
        self.life -= dt
        self.x += self.vx*dt; self.y += self.vy*dt
        self.vy += self.gravity*dt

    def draw(self, screen):
        if self.life>0:
            a = max(30, int(255*min(1.0, self.life/0.7)))
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color,a), (self.size,self.size), self.size)
            screen.blit(s, (int(self.x-self.size), int(self.y-self.size)))

    def alive(self): return self.life>0

class Explosion:
    def __init__(self, x,y,base_color,amount=28):
        self.particles = [Particle(x,y,base_color) for _ in range(amount)]
    def update(self, dt):
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]
    def draw(self, screen):
        for p in self.particles: p.draw(screen)
    def done(self): return len(self.particles)==0

# ---------------- Phao hoa (WIN) ----------------
class FireworkParticle:
    def __init__(self, x,y,color):
        self.x,self.y = x,y
        ang = random.uniform(0, 2*math.pi)
        spd = random.uniform(120, 420)
        self.vx = math.cos(ang)*spd
        self.vy = math.sin(ang)*spd
        self.life = random.uniform(0.8, 1.6)
        self.size = random.randint(2,4)
        self.color = color
        self.gravity = 90

    def update(self, dt):
        self.life -= dt
        self.x += self.vx*dt; self.y += self.vy*dt
        self.vy += self.gravity*dt

    def draw(self, screen):
        if self.life>0:
            a = int(255 * max(0.0, min(1.0, self.life/1.6)))
            pygame.draw.circle(screen, (*self.color, a), (int(self.x), int(self.y)), self.size)

    def alive(self): return self.life>0

class Rocket:
    def __init__(self, x, target_y, color):
        self.x = x
        self.y = H + 10
        self.color = color
        self.target_y = target_y
        self.speed = random.uniform(380, 520)
        self.exploded = False
        self.trail = []

    def update(self, dt):
        if not self.exploded:
            self.y -= self.speed * dt
            self.trail.append((self.x, self.y))
            if len(self.trail) > 12: self.trail.pop(0)
            if self.y <= self.target_y:
                self.exploded = True

    def draw(self, screen):
        if not self.exploded:
            for i, (tx, ty) in enumerate(self.trail):
                a = int(40 + i*12)
                pygame.draw.circle(screen, (255, 240, 160, min(a, 180)), (int(tx), int(ty)), 2)

class FireworkShow:
    def __init__(self):
        self.rockets = []
        self.particles = []

    def spawn(self):
        for _ in range(random.randint(3,5)):
            x = random.randint(100, W-100)
            y = random.randint(120, 240)
            color = random.choice([(255,100,120),(120,200,255),(255,220,120),(180,255,180),(220,160,255)])
            self.rockets.append(Rocket(x, y, color))

    def update(self, dt):
        for r in self.rockets:
            r.update(dt)
            if r.exploded:
                for _ in range(50):
                    self.particles.append(FireworkParticle(r.x, r.y, r.color))
                for _ in range(35):
                    self.particles.append(FireworkParticle(r.x, r.y, (255,255,255)))
        self.rockets = [r for r in self.rockets if not r.exploded]

        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

        if len(self.rockets)==0 and len(self.particles)<40:
            self.spawn()

    def draw(self, screen):
        for r in self.rockets: r.draw(screen)
        for p in self.particles:
            p.draw(screen)

# ---------------- Game chinh ----------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W,H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Nen
        self.grad = GradientPulse(W, H)
        self.bokehs = [BokehDot(W,H) for _ in range(26)]

        # State
        self.page = "menu"      # menu | playing | over | win
        self.topic = None
        self.buttons = []
        self.high = load_high()

        self.player = Player(W//2)
        self.col_x = self._compute_columns()
        self.current_word = ""
        self.enemies = []
        self.bullets = []
        self.effects = []
        self.score = 0
        self.best = self.high.get("highscore",0)
        self.round_used = set()
        self.play_order = []
        self.progress = 0
        self.flash = None
        self.timer_start = 0.0
        self.time_left = TIME_LIMIT
        self.fireworks = FireworkShow()

        self.topic_panel_rect = pygame.Rect(40, 160, W-80, 420)  # tach khoi Title
        self.build_menu()

    def _compute_columns(self):
        # mép trong khung, tính cả viền + bo góc + nửa bề rộng lớn nhất (ô trên hoặc ô tiếng Anh)
        half = max(BOX_W, GUN_W) // 2
        inner_left  = FRAME_OUTSET + BORDER_W + FRAME_SAFE + half
        inner_right = W - FRAME_OUTSET - BORDER_W - FRAME_SAFE - half

        span = inner_right - inner_left
        step = span / (COLS - 1) if COLS > 1 else 0
        return [int(inner_left + i * step) for i in range(COLS)]

    # Ve vien bo khung game
    def draw_game_frame(self):
        border_w = 8
        radius = 24
        outer = pygame.Rect(6, 6, W-12, H-12)
        draw_shadow(self.screen, outer, radius, 60)
        pygame.draw.rect(self.screen, (60, 70, 100), outer, border_w, border_radius=radius)

    # -------- menu --------
    def build_menu(self):
        self.buttons = []
        topics = list(VOCABS.keys())
        panel = self.topic_panel_rect
        cols = 3
        btn_h_margin = 40
        btn_v_margin = 26
        btn_w = (panel.w - (cols+1)*btn_h_margin)//cols
        btn_h = 56
        start_x = panel.x + btn_h_margin
        start_y = panel.y + 60
        for idx, name in enumerate(topics):
            c = idx%cols; r = idx//cols
            x = start_x + c*(btn_w+btn_h_margin)
            y = start_y + r*(btn_h+btn_v_margin)
            def make_cb(n=name): return lambda: self.select_topic(n)
            self.buttons.append(Button(x,y,btn_w,btn_h,name, make_cb()))
        pb_w, pb_h = 200,56
        pb_x = panel.centerx - pb_w//2
        pb_y = panel.bottom - pb_h - 18
        self.btn_play = Button(pb_x,pb_y,pb_w,pb_h,"Play", self.start_game, color=COL_BTN_PRIMARY)

    def select_topic(self, name): self.topic = name

    def start_game(self):
        if not self.topic: return
        self.page = "playing"
        self.score = 0
        self.player = Player(self.col_x[2])
        self.bullets=[]; self.effects=[]; self.flash=None
        n = min(20, len(VOCABS[self.topic]))
        self.play_order = random.sample(range(len(VOCABS[self.topic])), n)
        self.progress = 0
        self.timer_start = pygame.time.get_ticks()/1000.0
        self.time_left = TIME_LIMIT
        self.next_round()

    # -------- vong choi --------
    def next_round(self):
        if self.progress >= len(self.play_order):
            self.page = "win"
            self.fireworks = FireworkShow()
            self.fireworks.spawn()
            return

        idx = self.play_order[self.progress]
        en, vi = VOCABS[self.topic][idx]
        self.current_word = en

        all_vis = [vi for _,vi in VOCABS[self.topic]]
        pool = [x for x in all_vis if x != vi]
        wrongs = random.sample(pool, k=4)
        opts = wrongs + [vi]
        random.shuffle(opts)

        self.enemies = []
        box_w, box_h = 220, 78
        top_y = 120
        for i, text in enumerate(opts):
            cx = self.col_x[i % COLS]
            rect_x = cx - box_w // 2
            col = COL_ENEMY[i % len(COL_ENEMY)]
            self.enemies.append(Enemy(rect_x, top_y, box_w, box_h, text, text==vi, col))

    # -------- nen & HUD --------
    def draw_dynamic_bg(self, dt):
        self.grad.update(dt)
        self.grad.draw(self.screen)
        for b in self.bokehs:
            b.update(dt, W, H)
            b.draw(self.screen)

    def draw_header_panel(self):
        p = pygame.Rect(20, 20, W-40, 90)
        draw_shadow(self.screen, p, 16, 55)
        round_rect(self.screen, p, COL_PANEL, 16)
        draw_text_center(self.screen, "Vocabulary Shooter", (40+280, 36+26), max_width=560, max_size=44, min_size=28, color=COL_TEXT, bold=True)

    def draw_choose_topic_label(self):
        label_pos = (W//2, self.topic_panel_rect.top - 18)
        draw_text_center(self.screen, "Chon chu de", label_pos, max_width=360, max_size=28, min_size=22, color=COL_TEXT)

    def draw_hud(self):
        # Timer chip o goc phai
        t_left = max(0.0, self.time_left)
        t_txt = f"{t_left:0.1f}s"
        chip_w, chip_h = 140, 44
        chip = pygame.Rect(W - 40 - chip_w, 34, chip_w, chip_h)
        draw_shadow(self.screen, chip, 10, 50)
        round_rect(self.screen, chip, COL_BTN, 12)
        draw_text_center(self.screen, t_txt, chip.center, max_width=chip.w - 12,
                         max_size=28, min_size=20, color=COL_BTN_TXT, bold=True)

        # Score/Best ben trai chip
        right_limit = chip.left - 12
        area_w = 160
        area_x = right_limit - area_w
        sc_font = get_font(28, bold=False)
        sc_surf = sc_font.render(f"Score: {self.score}", True, COL_TEXT)
        self.screen.blit(sc_surf, (area_x + area_w - sc_surf.get_width(), 34))
        bs_surf = sc_font.render(f"Best: {self.best}", True, COL_TEXT)
        self.screen.blit(bs_surf, (area_x + area_w - bs_surf.get_width(), 64))

        # Thanh tien do thoi gian
        bar_height = 40
        bar_bg = pygame.Rect(40, 118, W - 80, bar_height)
        round_rect(self.screen, bar_bg, (235, 235, 245), bar_height // 2)
        fill_w = int(bar_bg.w * (t_left / TIME_LIMIT))
        bar_fg = pygame.Rect(bar_bg.x, bar_bg.y, max(0, fill_w), bar_bg.h)
        round_rect(self.screen, bar_fg, COL_BTN_PRIMARY, bar_height // 2)

        # Mat dat
        base = pygame.Rect(0, GROUND_Y, W, H - GROUND_Y)
        round_rect(self.screen, base, COL_PANEL_DARK, 0)

    # -------- update/draw playing --------
    def update_play(self, dt):
        now = pygame.time.get_ticks()/1000.0
        self.time_left = TIME_LIMIT - (now - self.timer_start)
        if self.time_left <= 0:
            self.page = "over"
            return

        self.player.update(dt)
        for b in self.bullets: b.update(dt)
        self.bullets = [b for b in self.bullets if b.y>-20]
        for fx in self.effects: fx.update(dt)
        self.effects = [fx for fx in self.effects if not fx.done()]

        hit=None
        for b in self.bullets:
            for e in self.enemies:
                if b.rect.colliderect(e.rect):
                    hit=(b,e); break
            if hit: break
        if hit:
            b,e=hit
            cx,cy=e.rect.center
            self.effects.append(Explosion(cx,cy,(255,180,120),amount=30))
            if b in self.bullets: self.bullets.remove(b)
            if e.is_correct:
                self.score+=1
                self.best=max(self.best,self.score)
                self.high["highscore"]=self.best; save_high(self.high)
                self.flash=("correct",0.18)
                self.progress += 1
                self.next_round()
            else:
                self.flash=("wrong",0.6)
                self.page="over"
        if self.flash:
            kind,t=self.flash
            t-=dt; self.flash=(kind,t) if t>0 else None

    def draw_play(self, dt):
        self.draw_dynamic_bg(dt)
        self.draw_game_frame()  # vien bo
        self.draw_header_panel()
        self.draw_hud()
        for e in self.enemies: e.draw(self.screen)
        for fx in self.effects: fx.draw(self.screen)
        self.player.draw(self.screen, self.current_word)
        for b in self.bullets: b.draw(self.screen)
        nearest = min(range(COLS), key=lambda i: abs(self.col_x[i]-self.player.x))
        sel_x = self.col_x[nearest]
        marker = pygame.Rect(sel_x-6, BARREL_Y-50, 12, 38)
        round_rect(self.screen, marker, COL_BULLET, 6)
        if self.flash and self.flash[0]=="correct":
            overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((40,167,69,60))
            self.screen.blit(overlay,(0,0))

    # -------- menu / win / over --------
    def draw_menu(self, dt):
        self.draw_dynamic_bg(dt)
        self.draw_game_frame()  # vien bo
        self.draw_header_panel()
        self.draw_choose_topic_label()

        box = self.topic_panel_rect
        draw_shadow(self.screen, box, 20, 55)
        round_rect(self.screen, box, (255,255,255), 20)

        for btn in self.buttons: btn.draw(self.screen)
        sel = self.topic or "Chua chon"
        sel_rect = pygame.Rect(W-450, H-110, 360, 32)
        draw_text_center(self.screen, f"Chu de: {sel}", sel_rect.center, max_width=sel_rect.w, max_size=28, color=COL_TEXT)
        self.btn_play.draw(self.screen)

        guide_rect = pygame.Rect(40, H-40, W-80, 26)
        draw_text_center(self.screen, "Huong dan: A/D hoac ←/→ de chon cot • SPACE de ban • R choi lai • ESC thoat",
                         guide_rect.center, max_width=guide_rect.w, max_size=22, min_size=18, color=(70,70,80))

    def draw_over(self, dt):
        self.draw_dynamic_bg(dt)
        self.draw_game_frame()  # vien bo
        self.draw_header_panel()
        self.draw_hud()

        overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((0,0,0,140))
        self.screen.blit(overlay,(0,0))
        panel = pygame.Rect(W//2-220, H//2-120, 440, 240)
        draw_shadow(self.screen, panel, 20, 70); round_rect(self.screen, panel, (255,255,255), 18)
        draw_text_center(self.screen, "Game Over", (W//2, H//2-56), max_width=360, max_size=44, color=COL_BAD, bold=True)
        draw_text_center(self.screen, f"Diem: {self.score}   Ky luc: {self.best}", (W//2, H//2-10), max_width=380, max_size=30, color=COL_TEXT)
        draw_text_center(self.screen, "Nhan R de choi lai  •  M ve Menu  •  ESC thoat", (W//2, H//2+42), max_width=420, max_size=22, color=(90,90,100))

    def draw_win(self, dt):
        self.draw_dynamic_bg(dt)
        self.draw_game_frame()  # vien bo
        self.draw_header_panel()
        self.fireworks.update(dt)
        self.fireworks.draw(self.screen)

        overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((255,255,255,40))
        self.screen.blit(overlay,(0,0))
        panel = pygame.Rect(W//2-240, H//2-140, 480, 280)
        draw_shadow(self.screen, panel, 20, 70); round_rect(self.screen, panel, (255,255,255), 18)
        draw_text_center(self.screen, "YOU WIN 🎉", (W//2, H//2-40), max_width=420, max_size=48, color=COL_BAD, bold=True)
        draw_text_center(self.screen, f"Hoan thanh 20/20 trong {TIME_LIMIT:.0f}s!", (W//2, H//2+5), max_width=420, max_size=28, color=(60,60,80))
        draw_text_center(self.screen, "Nhan R de choi lai  •  M ve Menu  •  ESC thoat", (W//2, H//2+50), max_width=420, max_size=22, color=(90,90,100))

    # -------- input --------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.page=="menu":
                if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                    for btn in self.buttons: btn.handle(e)
                    self.btn_play.handle(e)
                if e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN:
                    self.start_game()
            elif self.page=="playing":
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    elif e.key==pygame.K_m: self.page="menu"
                    elif e.key in (pygame.K_a, pygame.K_LEFT):
                        i = min(range(COLS), key=lambda k: abs(self.col_x[k]-self.player.x))
                        i = max(0, i-1); self.player.x = self.col_x[i]
                    elif e.key in (pygame.K_d, pygame.K_RIGHT):
                        i = min(range(COLS), key=lambda k: abs(self.col_x[k]-self.player.x))
                        i = min(COLS-1, i+1); self.player.x = self.col_x[i]
                    elif e.key==pygame.K_SPACE and self.player.can_shoot():
                        self.player.shoot()
                        self.bullets.append(Bullet(self.player.x, BARREL_Y))
                if e.type==pygame.KEYDOWN and e.key==pygame.K_r:
                    self.start_game()
            elif self.page in ("over","win"):
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_r: self.start_game()
                    elif e.key==pygame.K_m: self.page="menu"
                    elif e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()

    # -------- main loop --------
    def run(self):
        while True:
            dt = self.clock.tick(FPS)/1000.0
            self.handle_events()
            if self.page=="menu": self.draw_menu(dt)
            elif self.page=="playing":
                self.update_play(dt)
                self.draw_play(dt)
                if self.progress >= len(self.play_order) and self.time_left > 0:
                    self.page = "win"
                    self.fireworks = FireworkShow()
                    self.fireworks.spawn()
            elif self.page=="over": self.draw_over(dt)
            elif self.page=="win": self.draw_win(dt)
            pygame.display.flip()

# ---------------- Run ----------------
if __name__ == "__main__":
    Game().run()
