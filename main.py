# main.py
import os
os.environ.setdefault("SDL_VIDEO_CENTERED", "1")

import sys
import random
import pygame
import math
import traceback

from config import WIDTH, HEIGHT, GROUND_Y, FPS, TITLE, IMG, SND, COLORS, BOSS_INFO, ENEMY_IMAGES
from effects import ScreenShake, ParticleSystem, FloatingText
from background import ParallaxBackground
from door import Door

try:
    from hand_tracking import HandTracker
    from gesture import gesture_to_action, get_gesture_icon, get_gesture_description
except Exception as e:
    print(f"⚠️ Lỗi import AI: {e}")
    HandTracker = None
    gesture_to_action = lambda x, y=False, z=None: None
    get_gesture_icon = lambda x: "?"
    get_gesture_description = lambda x: "?"

try:
    from player import Player
    from enemies import Enemy, ShieldEnemy, FastEnemy, MageEnemy, HeavyEnemy
    from boss import Boss
    from level_manager import LevelManager
    from items import ItemSpawner
    from menu import MainMenu, set_menu_screen
except Exception as e:
    print(f"⚠️ Lỗi import core: {e}")
    traceback.print_exc()
    sys.exit(1)

pygame.init()
pygame.display.set_caption(TITLE)

# Khởi tạo âm thanh an toàn
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    print("✅ Audio initialized")
except Exception as e:
    print(f"⚠️ Không thể khởi tạo âm thanh: {e}")

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set menu screen reference
set_menu_screen(screen)

clock = pygame.time.Clock()

# ==================== HỆ THỐNG FONT CHỮ ====================
def get_font(size, bold=False, italic=False):
    """Lấy font chữ - ưu tiên font hỗ trợ tiếng Việt"""
    vietnamese_fonts = [
        "Segoe UI", "Arial", "Tahoma", "Times New Roman",
        "Noto Sans", "DejaVu Sans", "FreeSans", "Roboto"
    ]
    
    for font_name in vietnamese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size, bold, italic)
            test_surf = font.render("á à ả ã ạ", True, (255,255,255))
            if test_surf.get_width() > 0:
                return font
        except:
            continue
    
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont("Arial", size, bold, italic)

# Khởi tạo các font
font_large = get_font(48, bold=True)
font_medium = get_font(28, bold=True)
font_small = get_font(18)
font_tiny = get_font(12)
font_title = get_font(72, bold=True)
font_subtitle = get_font(32, bold=True)

# ==================== HÀM PHÁT ÂM THANH AN TOÀN ====================
def safe_play_sound(sound_dict, name, volume=0.5):
    try:
        if not pygame.mixer.get_init():
            return
        snd = sound_dict.get(name)
        if snd:
            snd.set_volume(volume)
            snd.play()
    except Exception as e:
        pass


# ==================== TRAILER GIỚI THIỆU (CHẠY CHẬM) ====================
class TrailerIntro:
    def __init__(self):
        self.phase = 0
        self.frame = 0
        self.text_index = 0
        self.char_index = 0
        self.display_text = ""
        self.alpha = 0
        self.fade_speed = 3
        self.wait_timer = 0
        self.particles = []
        
        # Nội dung trailer - chạy chậm
        self.story_parts = [
            {"text": "NAM 2157", "duration": 120, "color": COLORS["GOLD"]},
            {"text": "Trai Dat nhan duoc tin hieu cau cuu...", "duration": 180, "color": COLORS["CYAN"]},
            {"text": "TU RIA THIEN HA", "duration": 120, "color": COLORS["PURPLE"]},
            {"text": "Mot the luc bong toi dang xam chiem vu tru", "duration": 200, "color": COLORS["RED"]},
            {"text": "Hanh tinh nay den hanh tinh khac...", "duration": 160, "color": COLORS["ORANGE"]},
            {"text": "Chi con mot hy vong cuoi cung", "duration": 160, "color": COLORS["GREEN"]},
            {"text": "GALACTIC GUARDIAN", "duration": 180, "color": COLORS["GOLD"]},
            {"text": "Nguoi bao ve cuoi cung cua thien ha", "duration": 180, "color": COLORS["CYAN"]},
            {"text": "Hay thuc tinh va chien dau!", "duration": 160, "color": COLORS["YELLOW"]},
        ]
        
        self.current_part = 0
        self.part_progress = 0
        self.char_delay = 0
        self.char_delay_max = 2  # Mỗi ký tự cách nhau 2 frame
        
        for _ in range(150):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.3, 1.2),
                'alpha': random.randint(100, 255)
            })
    
    def update(self):
        self.frame += 1
        
        for p in self.particles:
            p['y'] += p['speed']
            if p['y'] > HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)
        
        if self.current_part < len(self.story_parts):
            part = self.story_parts[self.current_part]
            if self.part_progress >= part["duration"]:
                self.current_part += 1
                self.part_progress = 0
                self.char_index = 0
                self.display_text = ""
                self.char_delay = 0
        
        if self.current_part < len(self.story_parts):
            target_text = self.story_parts[self.current_part]["text"]
            
            if self.char_index < len(target_text):
                if self.char_delay <= 0:
                    self.char_index += 1
                    self.display_text = target_text[:self.char_index]
                    self.char_delay = self.char_delay_max
                else:
                    self.char_delay -= 1
        
        self.part_progress += 1
    
    def draw(self, screen):
        # Vẽ nền gradient
        for i in range(HEIGHT):
            t = i / HEIGHT
            r = int(5 + t * 25)
            g = int(3 + t * 15)
            b = int(10 + t * 45)
            pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))
        
        # Vẽ sao
        for p in self.particles:
            alpha = int(p['alpha'] * (0.5 + 0.5 * math.sin(self.frame * 0.01 + p['x'])))
            color = (min(255, alpha), min(255, alpha), min(255, alpha))
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), p['size'])
        
        # Vẽ hiệu ứng ánh sáng nền
        for i in range(3):
            x = WIDTH // 2 + math.sin(self.frame * 0.005 + i) * 100
            y = HEIGHT // 2 + math.cos(self.frame * 0.004 + i) * 50
            for r in range(100, 50, -10):
                alpha = int(15 * (1 - r / 100))
                pygame.draw.circle(screen, (80, 40, 120, alpha), (int(x), int(y)), r)
        
        # Vẽ text
        if self.current_part < len(self.story_parts):
            part = self.story_parts[self.current_part]
            color = part["color"]
            
            if self.part_progress < 40:
                alpha = int(255 * (self.part_progress / 40))
                color = tuple(min(255, c * alpha // 255) for c in color)
            elif self.part_progress > part["duration"] - 60:
                alpha = int(255 * ((part["duration"] - self.part_progress) / 60))
                color = tuple(min(255, c * alpha // 255) for c in color)
            
            if len(self.display_text) > 35:
                current_font = font_medium
            elif len(self.display_text) > 20:
                current_font = font_subtitle
            else:
                current_font = font_large
            
            for offset in range(3):
                shadow_color = (0, 0, 0)
                text_surf = current_font.render(self.display_text, True, shadow_color)
                text_rect = text_surf.get_rect(center=(WIDTH // 2 + offset, HEIGHT // 2 + offset))
                screen.blit(text_surf, text_rect)
            
            text_surf = current_font.render(self.display_text, True, color)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surf, text_rect)
        
        # Vẽ viền sáng
        if self.frame % 90 < 45:
            glow_alpha = int(40 + 40 * math.sin(self.frame * 0.03))
            for i in range(4):
                pygame.draw.rect(screen, (255, 215, 0, glow_alpha), 
                               (i*2, i*2, WIDTH - i*4, HEIGHT - i*4), 2)
        
        skip_font = get_font(14)
        if self.frame > 120:
            if (self.frame // 30) % 2 == 0:
                skip_text = skip_font.render("Nhan phim bat ky de bo qua...", True, (100, 100, 100))
            else:
                skip_text = skip_font.render("Nhan phim bat ky de bo qua...", True, (150, 150, 150))
            screen.blit(skip_text, (WIDTH // 2 - skip_text.get_width() // 2, HEIGHT - 50))
        
        return self.current_part >= len(self.story_parts)
    
    def skip(self):
        return True


def show_trailer_intro():
    trailer = TrailerIntro()
    start_ticks = pygame.time.get_ticks()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return True
        
        if pygame.time.get_ticks() - start_ticks > 25000:
            return True
        
        trailer.update()
        completed = trailer.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
        
        if completed:
            wait_start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - wait_start < 2000:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        return True
                pygame.display.flip()
                clock.tick(FPS)
            return True


def show_story_intro():
    screen.fill((0, 0, 0))
    
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, (100, 100, 100), (x, y), 1)
    
    story_lines = [
        "GALACTIC GUARDIAN",
        "",
        "Ban la chien binh anh sang cuoi cung.",
        "Hay chien dau de bao ve thien ha!",
        "",
        "Cham bat ky phim nao de bat dau..."
    ]
    
    y = 80
    for line in story_lines:
        if line == "GALACTIC GUARDIAN":
            color = COLORS["GOLD"]
            font = font_title
        elif line.startswith("Cham"):
            color = COLORS["GRAY"]
            font = font_small
        elif line == "":
            y += 20
            continue
        else:
            color = COLORS["WHITE"]
            font = font_medium
        
        text = font.render(line, True, color)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
        y += 50
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        clock.tick(FPS)
    
    return True


def load_image(path, size=None, default_color=None, text=None):
    try:
        if path and path.exists():
            img = pygame.image.load(str(path)).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            print(f"  ✅ Đã tải: {path.name}")
            return img
    except Exception as e:
        print(f"  ⚠️ Không load được {path.name}: {e}")
    
    if default_color:
        w, h = size if size else (64, 64)
        surf = pygame.Surface((w, h))
        surf.fill(default_color)
        pygame.draw.rect(surf, COLORS["WHITE"], surf.get_rect(), 2)
        
        if text:
            font = get_font(14, bold=True)
            text_surf = font.render(text, True, COLORS["WHITE"])
            text_rect = text_surf.get_rect(center=(w//2, h//2))
            surf.blit(text_surf, text_rect)
        
        pygame.draw.circle(surf, COLORS["WHITE"], (w//3, h//3), 6)
        pygame.draw.circle(surf, COLORS["BLACK"], (w//3, h//3), 3)
        pygame.draw.circle(surf, COLORS["WHITE"], (2*w//3, h//3), 6)
        pygame.draw.circle(surf, COLORS["BLACK"], (2*w//3, h//3), 3)
        
        return surf
    return None


def load_sound(path):
    try:
        if path and path.exists():
            return pygame.mixer.Sound(str(path))
    except Exception as e:
        print(f"  ⚠️ Không load được sound: {e}")
    return None


print("=" * 60)
print("📦 ĐANG TẢI ASSETS...")
print("=" * 60)

IMG.mkdir(parents=True, exist_ok=True)
SND.mkdir(parents=True, exist_ok=True)

print("\n🎮 Loading player...")
player_img = load_image(IMG / "player.png", (64, 64), COLORS["BLUE"], "P")

print("\n👾 Loading enemies...")
enemy_imgs = {
    "basic": load_image(IMG / "enemy_basic.png", (42, 42), COLORS["RED"], "E"),
    "shield": load_image(IMG / "enemy_tank.png", (48, 48), COLORS["ORANGE"], "S"),
    "fast": load_image(IMG / "enemy_fast.png", (34, 34), COLORS["GREEN"], "F"),
    "mage": load_image(IMG / "enemy_mage.png", (44, 44), COLORS["PURPLE"], "M"),
    "heavy": load_image(IMG / "enemy_heavy.png", (60, 60), COLORS["BROWN"], "H"),
}

print("\n👑 Loading bosses...")
boss_imgs = {}
for level, info in BOSS_INFO.items():
    img_name = info.get("image", f"boss_phase{level}.jpg")
    boss_imgs[level] = load_image(IMG / img_name, (160, 130), COLORS[info["color"]], f"B{level}")

print("\n🔊 Loading sounds...")
sounds = {
    'attack': load_sound(SND / "attack.wav"),
    'hit': load_sound(SND / "hit.wav"),
    'win': load_sound(SND / "win.wav"),
    'levelup': load_sound(SND / "levelup.wav"),
    'dodge': load_sound(SND / "dodge.wav"),
    'heal': load_sound(SND / "heal.wav"),
    'shoot': load_sound(SND / "shoot.wav"),
    'shield': load_sound(SND / "shield.wav"),
    'ammo': load_sound(SND / "ammo.wav"),
}

bgm = None
bgm_path = SND / "Summertime-background-music.mp3"
if pygame.mixer.get_init():
    if bgm_path.exists():
        try:
            pygame.mixer.music.load(str(bgm_path))
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
            bgm = bgm_path
            print(f"🎵 Playing background music: {bgm_path.name}")
        except Exception as e:
            print(f"⚠️ Không thể phát nhạc nền: {e}")
    else:
        print(f"⚠️ File nhạc nền không tìm thấy: {bgm_path}")
else:
    print("⚠️ Bỏ qua nhạc nền vì audio chưa khởi tạo")

print("\n✅ Hoàn tất tải assets!")
print("=" * 60)


def draw_text(text, x, y, color=COLORS["WHITE"], fnt=None, center=False, shadow=False):
    if fnt is None:
        fnt = font_small
    if shadow:
        shadow_surf = fnt.render(text, True, COLORS["BLACK"])
        screen.blit(shadow_surf, (x + 2, y + 2))
    surf = fnt.render(text, True, color)
    if center:
        screen.blit(surf, surf.get_rect(center=(x, y)))
    else:
        screen.blit(surf, (x, y))


def draw_heart(screen, x, y, size=16):
    heart_color = COLORS["RED"]
    points = []
    cx, cy = x + size//2, y + size//2
    for t in range(0, 360, 30):
        rad = math.radians(t)
        x_off = 16 * math.sin(rad) ** 3
        y_off = 13 * math.cos(rad) - 5 * math.cos(2*rad) - 2*math.cos(3*rad) - math.cos(4*rad)
        points.append((cx + x_off * size/32, cy - y_off * size/32))
    if len(points) > 2:
        pygame.draw.polygon(screen, heart_color, points)


def draw_ui(player, level_manager, show_fps, clock):
    panel = pygame.Surface((420, 290), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10, 10, 20, 200), panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, (255, 255, 255, 35), panel.get_rect(), 2, border_radius=16)
    screen.blit(panel, (10, 10))
    
    draw_text("GALACTIC GUARDIAN", 28, 18, COLORS["GOLD"], font_medium)
    draw_text(f"Man {level_manager.level}: {level_manager.current_name()}", 28, 48, COLORS["CYAN"], font_tiny)
    draw_text(f"Diem: {player.score}", 28, 70, COLORS["WHITE"], font_small)
    
    needed = level_manager.get_enemies_to_kill()
    remaining = level_manager.get_remaining_enemies()
    draw_text(f"Quai: {remaining}/{needed}", 28, 96, COLORS["YELLOW"], font_tiny)

    bar_width = 240
    bar_height = 10
    bar_x = 28
    bar_y = 118
    progress = level_manager.get_level_progress()
    pygame.draw.rect(screen, COLORS["DARK_GRAY"], (bar_x, bar_y, bar_width, bar_height), border_radius=5)
    pygame.draw.rect(screen, COLORS["GREEN"], (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=5)
    pygame.draw.rect(screen, COLORS["WHITE"], (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
    draw_text("Tien do", bar_x + bar_width + 10, bar_y - 1, COLORS["WHITE"], font_tiny)

    draw_heart(screen, 28, 146, 18)
    hp_bar_x = 52
    hp_bar_y = 150
    hp_bar_w = 218
    hp_bar_h = 16
    hp_percent = max(0, min(1.0, player.hp / player.max_hp))
    pygame.draw.rect(screen, COLORS["DARK_GRAY"], (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=8)
    pygame.draw.rect(screen, COLORS["RED"], (hp_bar_x, hp_bar_y, int(hp_bar_w * hp_percent), hp_bar_h), border_radius=8)
    pygame.draw.rect(screen, COLORS["WHITE"], (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), 2, border_radius=8)
    draw_text(f"{player.hp}/{player.max_hp} HP", hp_bar_x + hp_bar_w + 10, hp_bar_y + 1, COLORS["WHITE"], font_tiny)

    if player.infinite_ammo_permanent:
        draw_text(f"DAN: VO HAN", 28, 182, COLORS["YELLOW"], font_small)
        if pygame.time.get_ticks() % 1000 < 500:
            draw_text("⭐ DAN VINH VIEN! BAN THOA MAI! ⭐", 28, 200, COLORS["GOLD"], font_tiny)
    else:
        ammo_bar_x = 28
        ammo_bar_y = 182
        ammo_bar_w = 180
        ammo_bar_h = 12
        ammo_percent = player.ammo / player.max_ammo
        
        pygame.draw.rect(screen, COLORS["DARK_GRAY"], (ammo_bar_x, ammo_bar_y, ammo_bar_w, ammo_bar_h), border_radius=6)
        pygame.draw.rect(screen, COLORS["YELLOW"], (ammo_bar_x, ammo_bar_y, int(ammo_bar_w * ammo_percent), ammo_bar_h), border_radius=6)
        pygame.draw.rect(screen, COLORS["WHITE"], (ammo_bar_x, ammo_bar_y, ammo_bar_w, ammo_bar_h), 1, border_radius=6)
        
        draw_text(f"DAN: {player.ammo}/{player.max_ammo}", ammo_bar_x + ammo_bar_w + 10, ammo_bar_y - 1, COLORS["YELLOW"], font_tiny)

    ult_x = 28
    ult_y = 210
    if player.ultimate_cooldown > 0:
        ult_text = f"ULT: {player.ultimate_cooldown // 60 + 1}s"
        draw_text(ult_text, ult_x, ult_y, COLORS["PURPLE"], font_tiny)
    else:
        draw_text("ULT SAN SANG", ult_x, ult_y, COLORS["GREEN"], font_tiny)

    status = []
    if player.shield_active:
        status.append("Khien")
    if player.god_mode:
        status.append("GOD")
    if player.infinite_ammo_permanent:
        status.append("Vo han")
    if status:
        draw_text(" | ".join(status), 28, 232, COLORS["WHITE"], font_tiny)
    
    draw_text("✌️ BAN | ✊ DANH | ☝️+KEO NHẢY", 28, 255, COLORS["CYAN"], font_tiny)

    if show_fps:
        fps = int(clock.get_fps())
        fps_color = COLORS["GREEN"] if fps > 50 else COLORS["YELLOW"]
        draw_text(f"FPS: {fps}", WIDTH - 90, 18, fps_color, font_tiny)


def draw_camera_preview(tracker, camera_working, camera_enabled):
    if camera_working and camera_enabled and tracker and tracker.available:
        try:
            cam_x = WIDTH - 330
            cam_y = 10
            cam_width = 320
            cam_height = 240
            
            cam_surface = tracker.get_frame_surface()
            if cam_surface:
                cam_surface = pygame.transform.scale(cam_surface, (cam_width, cam_height))
                screen.blit(cam_surface, (cam_x, cam_y))
                pygame.draw.rect(screen, COLORS["CYAN"], (cam_x-2, cam_y-2, cam_width+4, cam_height+4), 2, border_radius=8)
                draw_text("CAMERA", cam_x + 5, cam_y + 5, COLORS["CYAN"], font_tiny)
        except Exception as e:
            pass
    elif camera_working:
        pygame.draw.rect(screen, COLORS["DARK_GRAY"], (WIDTH-330, 10, 320, 240))
        draw_text("Camera OFF", WIDTH-170, 130, COLORS["GRAY"], font_medium, center=True)
        draw_text("Nhan C de bat", WIDTH-170, 160, COLORS["GRAY"], font_small, center=True)


def draw_game_over(player, level_manager):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    draw_text("GAME OVER", WIDTH//2, HEIGHT//2 - 80, COLORS["RED"], font_large, center=True, shadow=True)
    draw_text(f"Diem: {player.score}", WIDTH//2, HEIGHT//2 - 10, COLORS["YELLOW"], font_medium, center=True)
    draw_text(f"Man dat duoc: {level_manager.level}", WIDTH//2, HEIGHT//2 + 30, COLORS["WHITE"], font_small, center=True)
    draw_text("Nhan M de ve Menu | R de choi lai | Q de thoat", WIDTH//2, HEIGHT//2 + 80, COLORS["GRAY"], font_small, center=True)


def draw_victory(player):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    for _ in range(10):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 200)
        pygame.draw.circle(screen, random.choice([COLORS["RED"], COLORS["GREEN"], COLORS["YELLOW"], COLORS["BLUE"], COLORS["PURPLE"]]), (x, y), random.randint(3, 8))
    
    draw_text("CHIEN THANG!", WIDTH//2, HEIGHT//2 - 100, COLORS["GOLD"], font_large, center=True, shadow=True)
    draw_text("Nguoi hung khong gian da bao ve thien ha!", WIDTH//2, HEIGHT//2 - 40, COLORS["CYAN"], font_medium, center=True)
    draw_text(f"Diem so cuoi cung: {player.score}", WIDTH//2, HEIGHT//2 + 10, COLORS["YELLOW"], font_medium, center=True)
    draw_text("Cam on ban da giai cuu vu tru!", WIDTH//2, HEIGHT//2 + 60, COLORS["GREEN"], font_small, center=True)
    draw_text("Nhan M de ve Menu | R de choi lai | Q de thoat", WIDTH//2, HEIGHT//2 + 120, COLORS["GRAY"], font_small, center=True)


def reset_game():
    global player, level_manager, enemies, boss, spawn_cooldown, game_over, victory
    global message, message_timer, message_color, level_transition, transition_timer
    global screen_shake, particle_system, floating_texts, background, item_spawner
    global paused, camera_enabled, door_to_boss, door_to_next_level
    
    player = Player()
    level_manager = LevelManager()
    enemies = []
    boss = None
    spawn_cooldown = 0
    game_over = False
    victory = False
    level_transition = False
    transition_timer = 0
    paused = False
    door_to_boss = None
    door_to_next_level = None
    message = "Da khoi dong lai!"
    message_timer = 120
    message_color = COLORS["YELLOW"]
    
    screen_shake = ScreenShake()
    particle_system = ParticleSystem()
    floating_texts = []
    background = ParallaxBackground()
    item_spawner = ItemSpawner()
    
    print("Game restarted!")


def start_game(level=1):
    global player, level_manager, enemies, boss, spawn_cooldown, item_spawner
    global game_over, victory, level_transition, transition_timer
    global message, message_timer, message_color, screen_shake, particle_system, floating_texts, background
    global door_to_boss, door_to_next_level, paused
    
    player = Player()
    level_manager = LevelManager()
    level_manager.level = level
    level_manager.enemies_killed_in_level = 0
    level_manager.door_to_boss_spawned = False
    level_manager.door_to_next_level_spawned = False
    level_manager.boss_defeated = False
    enemies = []
    boss = None
    spawn_cooldown = 0
    game_over = False
    victory = False
    level_transition = False
    transition_timer = 0
    paused = False
    door_to_boss = None
    door_to_next_level = None
    item_spawner = ItemSpawner()
    
    message = f"Bat dau {level_manager.current_name()}!"
    message_timer = 180
    message_color = COLORS["GOLD"]
    
    screen_shake = ScreenShake()
    particle_system = ParticleSystem()
    floating_texts = []
    background = ParallaxBackground()
    
    print(f"Game started at level {level}!")


def handle_enemy_death(enemy, enemies, level_manager, player):
    global item_spawner
    if enemy in enemies:
        enemies.remove(enemy)
        level_complete = level_manager.record_kill()
        
        item_spawner.spawn_from_enemy(enemy.x + enemy.w//2, enemy.y + enemy.h//2)
        
        particle_system.add_explosion_particles(enemy.x + enemy.w//2, enemy.y + enemy.h//2)
        
        floating_texts.append(FloatingText(
            enemy.x + enemy.w//2, enemy.y, 
            f"+{getattr(enemy, 'score', 10)}", 
            COLORS["YELLOW"], duration=40
        ))
        
        return True
    return False


# ==================== KHỞI TẠO CAMERA ====================
tracker = None
camera_working = False
camera_enabled = True

if HandTracker is not None:
    try:
        for cam_idx in [0, 1]:
            print(f"Thu camera {cam_idx}...")
            try:
                import cv2
                test_cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
                if test_cap.isOpened():
                    ret, test_frame = test_cap.read()
                    test_cap.release()
                    if ret and test_frame is not None:
                        print(f"Camera {cam_idx} hoat dong, dang khoi tao...")
                        tracker = HandTracker(camera_index=cam_idx, show_preview=False)
                        if tracker and tracker.available:
                            camera_working = True
                            print(f"Da ket noi thanh cong voi camera {cam_idx}")
                            break
                        else:
                            print(f"Camera {cam_idx} khong khoi tao duoc HandTracker")
                            if tracker:
                                tracker.release()
                                tracker = None
                    else:
                        print(f"Camera {cam_idx} khong doc duoc frame")
                else:
                    print(f"Camera {cam_idx} khong mo duoc")
            except Exception as e:
                print(f"Loi khi thu camera {cam_idx}: {e}")
                continue
        
        if camera_working:
            print("=" * 60)
            print("CAMERA READY!")
            print("   FOLLOW MODE: Nhan vat chay theo tay ban!")
            print("=" * 60)
        else:
            print("No working camera found!")
            tracker = None
            
    except Exception as e:
        print(f"Camera init error: {e}")
        tracker = None

if not camera_working:
    print("=" * 60)
    print("NO CAMERA - Keyboard mode")
    print("   Controls: <- -> : Di chuyen | SPACE : Danh | J : Nhay | F : Ban")
    print("   B : God Mode | N : Hoi mau | M : Menu | R : Choi lai | Q : Thoat")
    print("=" * 60)

# ==================== KHỞI TẠO GAME ====================
main_menu = MainMenu()
in_menu = True

player = None
level_manager = None
enemies = []
boss = None
spawn_cooldown = 0
item_spawner = ItemSpawner()
door_to_boss = None
door_to_next_level = None

screen_shake = ScreenShake()
particle_system = ParticleSystem()
floating_texts = []
background = ParallaxBackground()

running = True
game_over = False
victory = False
show_fps = False
frame_count = 0
level_transition = False
transition_timer = 0
fullscreen = False
paused = False

message = "Dua tay trai/phai de nhan vat chay theo!"
message_timer = 180
message_color = COLORS["YELLOW"]
last_gesture_display = None
gesture_display_timer = 0

follow_mode_enabled = True
last_follow_x = None

print("\nGAME STARTED!")
print("Have fun!\n")

try:
    if not show_trailer_intro():
        running = False
    elif not show_story_intro():
        running = False
except Exception as e:
    print(f"Intro error: {e}, skipping...")

try:
    while running:
        dt = clock.tick(FPS)
        frame_count += 1
        
        gesture = None
        action = None
        hand_x = None
        menu_action = None
        
        if camera_working and tracker and tracker.available and camera_enabled:
            try:
                hand_x = tracker.get_hand_position()
                gesture, action = tracker.read_gesture()
                
                if action in ["menu_up", "menu_down", "select", "back"]:
                    menu_action = action
                
                if gesture:
                    last_gesture_display = gesture
                    gesture_display_timer = 30
                        
            except Exception as e:
                if frame_count % 300 == 0:
                    print(f"Gesture read error: {e}")
        
        boss_choice_processed = False
        
        menu_event = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                menu_event = event
                
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_f:
                    show_fps = not show_fps
                elif event.key == pygame.K_c:
                    camera_enabled = not camera_enabled
                    message = "Camera " + ("ON" if camera_enabled else "OFF")
                    message_timer = 60
                    message_color = COLORS["CYAN"]
                elif event.key == pygame.K_h and camera_working:
                    follow_mode_enabled = not follow_mode_enabled
                    message = f"Follow Mode: {'ON' if follow_mode_enabled else 'OFF'}"
                    message_timer = 60
                    message_color = COLORS["GOLD"]
                elif event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        message = "TAM DUNG"
                    else:
                        message = "TIEP TUC"
                    message_timer = 60
                    message_color = COLORS["YELLOW"]
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                elif event.key == pygame.K_m and not in_menu:
                    in_menu = True
                    message = "Da thoat ve menu"
                    message_timer = 60
                elif event.key == pygame.K_r:
                    if game_over or victory:
                        reset_game()
                        start_game(1)
                        in_menu = False
                    elif in_menu:
                        pass
                    else:
                        reset_game()
                        start_game(1)
                        in_menu = False
                elif event.key == pygame.K_b and not game_over and not victory and not in_menu:
                    if player:
                        god_mode = player.toggle_god_mode()
                        if god_mode:
                            message = "GOD MODE ON!"
                            message_color = COLORS["GOLD"]
                        else:
                            message = "GOD MODE OFF"
                            message_color = COLORS["ORANGE"]
                        message_timer = 90
                elif event.key == pygame.K_n and not game_over and not victory and not in_menu:
                    if player:
                        if player.god_mode:
                            player.toggle_god_mode()
                        player.hp = player.max_hp
                        player.invincible = 0
                        player.dodge_timer = 0
                        player.heal_cooldown = 0
                        message = "Da hoi mau va tat GOD MODE!"
                        message_color = COLORS["GREEN"]
                        message_timer = 90
                elif event.key == pygame.K_j and not game_over and not victory and not in_menu and not level_transition:
                    if player and player.jump():
                        safe_play_sound(sounds, 'dodge', 0.3)
                        message = "NHẢY!"
                        message_timer = 20
                        message_color = COLORS["CYAN"]
                elif boss and not boss.dead and boss.is_waiting_for_response() and not in_menu and not game_over and not victory:
                    if event.key == pygame.K_1:
                        result = boss.handle_player_response(0)
                        boss_choice_processed = True
                    elif event.key == pygame.K_2:
                        result = boss.handle_player_response(1)
                        boss_choice_processed = True

                    if result == "surrender":
                        game_over = True
                        message = "Ban da dau hang! Game Over!"
                        message_timer = 180
                        message_color = COLORS["RED"]
                    elif result == "fight":
                        message = "Hay chien dau!"
                        message_timer = 60
                        message_color = COLORS["ORANGE"]
        
        if in_menu:
            result = main_menu.handle_event(menu_event, gesture, menu_action)
            if result:
                if result[0] == "start_level":
                    start_game(result[1])
                    in_menu = False
                elif result[0] == "quit":
                    running = False
            
            main_menu.update()
            main_menu.draw(screen)
            
            draw_camera_preview(tracker, camera_working, camera_enabled)
            
            if gesture_display_timer > 0:
                gesture_display_timer -= 1
                if last_gesture_display:
                    icon = get_gesture_icon(last_gesture_display)
                    desc = get_gesture_description(last_gesture_display)
                    draw_text(f"{icon} {desc}", WIDTH//2, 80, COLORS["GREEN"], font_medium, center=True)
            
            pygame.display.flip()
            continue
        
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text("TAM DUNG", WIDTH//2, HEIGHT//2 - 40, COLORS["WHITE"], font_large, center=True)
            draw_text("Nhan P de tiep tuc", WIDTH//2, HEIGHT//2 + 20, COLORS["GRAY"], font_medium, center=True)
            draw_text("M - Menu | R - Choi lai | Q - Thoat", WIDTH//2, HEIGHT//2 + 80, COLORS["GRAY"], font_small, center=True)
            if camera_working:
                draw_text(f"H - Follow Mode: {'ON' if follow_mode_enabled else 'OFF'}", 
                         WIDTH//2, HEIGHT//2 + 120, COLORS["CYAN"], font_small, center=True)
            pygame.display.flip()
            clock.tick(FPS)
            continue
        
        keys = pygame.key.get_pressed()
        
        if not game_over and not victory and not level_transition and player:
            
            if camera_working and camera_enabled and follow_mode_enabled and hand_x is not None:
                from settings import FOLLOW_MARGIN, FOLLOW_HAND_SMOOTHING, FOLLOW_MAX_SPEED
                
                margin = FOLLOW_MARGIN
                min_x = margin
                max_x = WIDTH - player.w - margin
                
                if max_x > min_x:
                    target_x = hand_x * (max_x - min_x) + min_x
                    target_x = max(min_x, min(max_x, target_x))
                    
                    dx = target_x - player.x
                    
                    if abs(dx) > FOLLOW_MAX_SPEED:
                        dx = FOLLOW_MAX_SPEED if dx > 0 else -FOLLOW_MAX_SPEED
                    
                    player.x += dx * FOLLOW_HAND_SMOOTHING
                    
                    player.x = max(min_x, min(max_x, player.x))
                    
                    if hasattr(player, '_last_follow_x'):
                        if player.x > player._last_follow_x + 2:
                            player.facing_right = True
                        elif player.x < player._last_follow_x - 2:
                            player.facing_right = False
                    player._last_follow_x = player.x
                    
                    if frame_count % 30 < 15:
                        message = "FOLLOW MODE ACTIVE"
                        message_timer = 5
                        message_color = COLORS["CYAN"]
            
            if action == "left" and not (camera_working and follow_mode_enabled):
                player.move_left()
                message = "<<"
                message_timer = 8
                message_color = COLORS["CYAN"]
                
            elif action == "right" and not (camera_working and follow_mode_enabled):
                player.move_right()
                message = ">>"
                message_timer = 8
                message_color = COLORS["CYAN"]
                
            elif action == "jump":
                if player.jump():
                    safe_play_sound(sounds, 'dodge', 0.3)
                    message = "NHẢY!"
                    message_timer = 20
                    message_color = COLORS["CYAN"]
                    
            elif action == "attack":
                if player.attack():
                    safe_play_sound(sounds, 'attack', 0.4)
                    screen_shake.shake(5, 3)
                    
                    target = None
                    min_dist = 150
                    for e in enemies:
                        if abs(e.y + e.h - player.y) < 110:
                            dist = abs(e.x - player.x)
                            if dist < min_dist:
                                min_dist = dist
                                target = e
                    
                    if target:
                        damage = player.get_attack_damage()
                        gained = target.take_hit()
                        if gained > 0:
                            player.score += gained
                            safe_play_sound(sounds, 'hit', 0.3)
                            particle_system.add_hit_particles(target.x + target.w//2, target.y + target.h//2)
                            floating_texts.append(FloatingText(
                                target.x + target.w//2, target.y, 
                                f"{damage} DMG!", COLORS["RED"], duration=25
                            ))
                            message = f"+{gained}!"
                            message_timer = 25
                            message_color = COLORS["YELLOW"]
                        
                        if target.dead:
                            handle_enemy_death(target, enemies, level_manager, player)
                            
                    elif boss and boss.rect.colliderect(pygame.Rect(player.x, player.y, player.w, player.h).inflate(80, 40)):
                        damage = player.get_attack_damage()
                        gained = boss.take_hit(damage)
                        if gained > 0:
                            player.score += gained
                            safe_play_sound(sounds, 'hit', 0.4)
                            screen_shake.shake(8, 5)
                            particle_system.add_hit_particles(boss.x + boss.w//2, boss.y + boss.h//2, COLORS["ORANGE"])
                            floating_texts.append(FloatingText(
                                boss.x + boss.w//2, boss.y, 
                                f"{damage} DMG!", COLORS["RED"], duration=25
                            ))
                            message = f"Boss! +{gained}"
                            message_timer = 30
                            message_color = COLORS["RED"]
                    else:
                        message = "Truot!"
                        message_timer = 15
                        message_color = COLORS["GRAY"]
                        
            elif action == "shoot":
                if player.shoot():
                    safe_play_sound(sounds, 'shoot', 0.3)
                    message = "BAN!"
                    message_timer = 15
                    message_color = COLORS["YELLOW"]
                    
            elif action == "heal":
                if player.heal():
                    safe_play_sound(sounds, 'heal', 0.5)
                    particle_system.add_hit_particles(player.x + player.w//2, player.y + player.h//2, COLORS["GREEN"])
                    floating_texts.append(FloatingText(
                        player.x + player.w//2, player.y - 20, 
                        "+1 HP", COLORS["GREEN"], duration=30
                    ))
                    message = "HOI MAU +1 HP!"
                    message_timer = 30
                    message_color = COLORS["GREEN"]
                else:
                    if player.heal_cooldown > 0:
                        message = f"Cho {player.heal_cooldown//10 + 1}s"
                    else:
                        message = "HP day!"
                    message_timer = 20
                    message_color = COLORS["GRAY"]
            
            elif action == "ultimate":
                if player.ultimate():
                    message = "CHIEU CUOI!"
                    message_timer = 30
                    message_color = COLORS["PURPLE"]
                    for e in enemies[:]:
                        gained = e.take_hit()
                        if gained > 0:
                            player.score += gained
                            particle_system.add_explosion_particles(e.x + e.w//2, e.y + e.h//2)
                            floating_texts.append(FloatingText(
                                e.x + e.w//2, e.y, 
                                "ULTIMATE!", COLORS["PURPLE"], duration=30
                            ))
                        if e.dead:
                            handle_enemy_death(e, enemies, level_manager, player)
                    if boss and not boss.dead:
                        gained = boss.take_hit(5)
                        if gained > 0:
                            player.score += gained
                            particle_system.add_explosion_particles(boss.x + boss.w//2, boss.y + boss.h//2)
                            floating_texts.append(FloatingText(
                                boss.x + boss.w//2, boss.y, 
                                "5 DMG!", COLORS["PURPLE"], duration=30
                            ))
            
            if not (camera_working and follow_mode_enabled):
                if keys[pygame.K_LEFT]:
                    player.move_left()
                if keys[pygame.K_RIGHT]:
                    player.move_right()
            
            if keys[pygame.K_SPACE]:
                if player.attack():
                    safe_play_sound(sounds, 'attack', 0.4)
                    screen_shake.shake(5, 3)
                    
                    target = None
                    min_dist = 150
                    for e in enemies:
                        if abs(e.y + e.h - player.y) < 110:
                            dist = abs(e.x - player.x)
                            if dist < min_dist:
                                min_dist = dist
                                target = e
                    
                    if target:
                        gained = target.take_hit()
                        if gained > 0:
                            player.score += gained
                            particle_system.add_hit_particles(target.x + target.w//2, target.y + target.h//2)
                            floating_texts.append(FloatingText(
                                target.x + target.w//2, target.y, 
                                "HIT!", COLORS["RED"], duration=20
                            ))
                        if target.dead:
                            handle_enemy_death(target, enemies, level_manager, player)
            if keys[pygame.K_f]:
                if player.shoot():
                    safe_play_sound(sounds, 'shoot', 0.3)
            if keys[pygame.K_j]:
                if player.jump():
                    safe_play_sound(sounds, 'dodge', 0.3)
            
            player.update()
            
            if boss is None and not level_manager.door_to_boss_spawned:
                spawn_cooldown += 1
                if spawn_cooldown >= level_manager.spawn_delay():
                    if len(enemies) < level_manager.max_enemies():
                        new_enemies = level_manager.spawn_enemies(WIDTH, enemies)
                        for e in new_enemies:
                            enemies.append(e)
                    spawn_cooldown = 0
            
            if not level_manager.boss_defeated and level_manager.should_spawn_door_to_boss() and door_to_boss is None and boss is None:
                door_x = WIDTH//2 - 32
                door_y = GROUND_Y - 96
                door_to_boss = Door(door_x, door_y, "to_boss")
                level_manager.set_door_to_boss_spawned(True)
                message = "CUA DEN BOSS DA MO! DEN GAN DE VAO!"
                message_timer = 180
                message_color = COLORS["GOLD"]
                print("Cua boss da duoc spawn!")
            
            if door_to_boss:
                door_to_boss.update()
                door_to_boss.draw(screen)
                if player.rect.colliderect(door_to_boss.rect):
                    if boss is None:
                        print("Nguoi choi vao cua boss!")
                        enemies.clear()
                        boss = Boss(level=level_manager.level)
                        door_to_boss = None
                        player.x = max(50, min(WIDTH - player.w - 50, WIDTH // 4))
                        player.invincible = 60
                        player.dodge_timer = 0
                        message = f"{boss.info['name']} XUAT HIEN!"
                        message_timer = 180
                        message_color = COLORS["RED"]
                        safe_play_sound(sounds, 'levelup', 0.7)
                        screen_shake.shake(15, 8)
                        print(f"Boss {boss.info['name']} da xuat hien!")
            
            if boss and boss.dead and not level_manager.boss_defeated:
                level_manager.set_boss_defeated(True)
                player.score += 500
                print(f"Boss defeated! Score: {player.score}")
                if not level_manager.game_completed:
                    door_x = WIDTH//2 - 32
                    door_y = GROUND_Y - 96
                    door_to_next_level = Door(door_x, door_y, "to_next_level", level_manager.level + 1)
                    message = "Canh cua den man tiep theo da mo!"
                    message_timer = 120
                    message_color = COLORS["GOLD"]
                    boss = None
                    print("Cua next level da duoc spawn!")
            
            if door_to_next_level:
                door_to_next_level.update()
                door_to_next_level.draw(screen)
                if player.rect.colliderect(door_to_next_level.rect):
                    print("Nguoi choi vao cua next level!")
                    if level_manager.can_advance_to_next_level():
                        enemies.clear()
                        spawn_cooldown = 0
                        player.full_heal()
                        item_spawner.clear()
                        door_to_next_level = None
                        level_transition = True
                        transition_timer = 60
                        message = f"{level_manager.current_name()}"
                        message_timer = 180
                        message_color = COLORS["GOLD"]
                        safe_play_sound(sounds, 'levelup', 0.5)
                        print(f"Chuyen sang {level_manager.current_name()}!")
                    else:
                        victory = True
                        door_to_next_level = None
            
            for e in enemies[:]:
                e.update(GROUND_Y)
                
                if isinstance(e, MageEnemy):
                    if e.can_shoot():
                        e.shoot(player.x + player.w//2, player.y + player.h//2)
                    
                    for projectile in e.get_projectiles():
                        if player.rect.colliderect(projectile.rect):
                            if player.dodge_timer <= 0 and player.invincible <= 0 and not player.shield_active:
                                player.hit(projectile.damage)
                                safe_play_sound(sounds, 'hit', 0.4)
                                particle_system.add_hit_particles(player.x + player.w//2, player.y + player.h//2)
                                floating_texts.append(FloatingText(
                                    player.x + player.w//2, player.y, 
                                    f"-{projectile.damage} HP", COLORS["PURPLE"], duration=25
                                ))
                                projectile.dead = True
                            else:
                                projectile.dead = True
                
                if e.can_attack() and player.rect.colliderect(e.rect.inflate(e.attack_range, 20)):
                    e.attack()
                    if player.dodge_timer <= 0 and player.invincible <= 0 and not player.shield_active:
                        damage = getattr(e, 'damage', 1)
                        player.hit(damage)
                        safe_play_sound(sounds, 'hit', 0.5)
                        screen_shake.shake(6, 4)
                        particle_system.add_hit_particles(player.x + player.w//2, player.y + player.h//2)
                        floating_texts.append(FloatingText(
                            player.x + player.w//2, player.y, 
                            f"-{damage} HP", COLORS["RED"], duration=30
                        ))
                        message = f"-{damage} HP! ({player.hp} left)"
                        message_timer = 30
                        message_color = COLORS["RED"]
                        if player.hp <= 0:
                            game_over = True
                
                if e.dead:
                    handle_enemy_death(e, enemies, level_manager, player)
            
            item_messages = item_spawner.check_collisions(player)
            for msg, sound_name in item_messages:
                message = msg
                message_timer = 60
                message_color = COLORS["GREEN"]
                floating_texts.append(FloatingText(
                    player.x + player.w//2, player.y - 30, 
                    msg, COLORS["GOLD"], duration=40
                ))
                if sound_name == "heal":
                    safe_play_sound(sounds, 'heal', 0.5)
                elif sound_name == "shield":
                    safe_play_sound(sounds, 'dodge', 0.4)
                elif sound_name == "ammo":
                    safe_play_sound(sounds, 'shoot', 0.3)
            
            for bullet in player.bullets[:]:
                hit_target = False
                
                for e in enemies[:]:
                    if bullet.rect.colliderect(e.rect):
                        gained = e.take_hit()
                        if gained > 0:
                            player.score += gained
                            particle_system.add_hit_particles(e.x + e.w//2, e.y + e.h//2)
                            floating_texts.append(FloatingText(
                                e.x + e.w//2, e.y, 
                                f"+{gained}", COLORS["YELLOW"], duration=25
                            ))
                        if e.dead:
                            handle_enemy_death(e, enemies, level_manager, player)
                        bullet.dead = True
                        hit_target = True
                        break
                
                if not hit_target and boss and not boss.dead and bullet.rect.colliderect(boss.rect):
                    gained = boss.take_hit(bullet.damage)
                    if gained > 0:
                        player.score += gained
                        particle_system.add_hit_particles(boss.x + boss.w//2, boss.y + boss.h//2, COLORS["ORANGE"])
                        floating_texts.append(FloatingText(
                            boss.x + boss.w//2, boss.y, 
                            f"{bullet.damage} DMG!", COLORS["RED"], duration=25
                        ))
                        screen_shake.shake(6, 4)
                        message = f"Boss hit! +{gained}"
                        message_timer = 25
                        message_color = COLORS["ORANGE"]
                    
                    bullet.dead = True
                    hit_target = True
                
                if bullet.dead and bullet in player.bullets:
                    player.bullets.remove(bullet)
            
            # ========== BOSS LOGIC ==========
            if boss and not boss.dead:
                try:
                    if boss.is_dialogue_active():
                        boss.update_dialogue()
                        
                        if not boss.is_dialogue_active() and not hasattr(boss, 'player_dialogue_started'):
                            boss.player_dialogue_started = True
                            boss.start_player_dialogue()
                    
                    elif boss.is_player_dialogue_active():
                        boss.update_player_dialogue()
                        
                        if boss.is_waiting_for_response():
                            if frame_count % 30 < 15:
                                message = "1: Dau hang | 2: Chien dau"
                                message_timer = 5
                                message_color = COLORS["YELLOW"]
                            
                            if not boss_choice_processed:
                                if gesture == "one_index":
                                    result = boss.handle_player_response(0)
                                    if result == "surrender":
                                        game_over = True
                                        message = "Ban da dau hang! Game Over!"
                                        message_timer = 180
                                        message_color = COLORS["RED"]
                                        boss_choice_processed = True
                                elif gesture == "two_fingers":
                                    result = boss.handle_player_response(1)
                                    if result == "fight":
                                        message = "Hay chien dau!"
                                        message_timer = 60
                                        message_color = COLORS["ORANGE"]
                                        boss_choice_processed = True
                    else:
                        boss.update(player.x + player.w//2)
                        
                        if boss.can_attack() and abs(boss.y + boss.h - player.y) < 120:
                            if abs(boss.x - player.x) < 150:
                                damage = boss.get_attack_damage()
                                player.hit(damage)
                                safe_play_sound(sounds, 'hit', 0.6)
                                screen_shake.shake(8, 6)
                                particle_system.add_hit_particles(player.x + player.w//2, player.y + player.h//2)
                                floating_texts.append(FloatingText(
                                    player.x + player.w//2, player.y, 
                                    f"-{damage} HP!", COLORS["RED"], duration=35
                                ))
                                message = f"Boss attack! -{damage} HP"
                                message_timer = 30
                                message_color = COLORS["RED"]
                                if player.hp <= 0:
                                    game_over = True
                        
                        if player.rect.colliderect(boss.rect.inflate(30, 30)):
                            if player.dodge_timer <= 0 and player.invincible <= 0 and not player.shield_active:
                                damage = boss.get_attack_damage()
                                safe_play_sound(sounds, 'hit', 0.5)
                                screen_shake.shake(8, 6)
                                particle_system.add_hit_particles(player.x + player.w//2, player.y + player.h//2)
                                floating_texts.append(FloatingText(
                                    player.x + player.w//2, player.y, 
                                    f"-{damage} HP", COLORS["RED"], duration=35
                                ))
                                player.hit(damage)
                                message = f"VA CHAM BOSS! -{damage} HP"
                                message_timer = 30
                                message_color = COLORS["RED"]
                                if player.hp <= 0:
                                    game_over = True
                        
                        for fireball in boss.projectiles[:]:
                            if player.rect.colliderect(fireball.rect):
                                if player.dodge_timer <= 0 and player.invincible <= 0 and not player.shield_active:
                                    player.hit(fireball.damage)
                                    safe_play_sound(sounds, 'hit', 0.5)
                                    particle_system.add_hit_particles(player.x + player.w//2, player.y + player.h//2)
                                    floating_texts.append(FloatingText(
                                        player.x + player.w//2, player.y, 
                                        f"-{fireball.damage} HP", COLORS["RED"], duration=25
                                    ))
                                    message = f"Fireball! -{fireball.damage} HP"
                                    message_timer = 25
                                    message_color = COLORS["ORANGE"]
                                    if player.hp <= 0:
                                        game_over = True
                                if fireball in boss.projectiles:
                                    boss.projectiles.remove(fireball)
                except Exception as e:
                    print(f"Loi trong boss logic: {e}")
        
        if player and player.hp <= 0:
            game_over = True
        
        if level_transition:
            transition_timer -= 1
            if transition_timer <= 0:
                level_transition = False
        
        particle_system.update()
        for text in floating_texts[:]:
            if not text.update():
                floating_texts.remove(text)
        
        shake_x, shake_y = screen_shake.apply()
        
        screen.fill((0, 0, 0))
        if player:
            background.draw(screen, player.x + player.w//2)
        else:
            background.draw(screen, WIDTH//2)
        
        for i in range(0, WIDTH, 30):
            x = i + shake_x
            if 0 <= x <= WIDTH:
                pygame.draw.line(screen, (60, 90, 40), (x, GROUND_Y), (x, GROUND_Y - 5), 2)
        
        for e in enemies:
            img = enemy_imgs.get(getattr(e, "type", "basic"))
            e.draw(screen, img)
        
        if boss and not boss.dead:
            try:
                if player:
                    boss.draw(screen, boss_imgs, player_x=player.x + player.w//2)
                else:
                    boss.draw(screen, boss_imgs, player_x=WIDTH//2)
                boss.draw_dialogue(screen)
                boss.draw_player_dialogue(screen)
                if not boss.is_dialogue_active() and not boss.is_player_dialogue_active():
                    boss.draw_health_bar(screen)
                boss.draw_projectiles(screen)
            except Exception as e:
                print(f"Loi ve boss: {e}")
        
        if player:
            player.draw(screen, player_img)
            player.draw_bullets(screen)
        item_spawner.draw(screen)
        
        particle_system.draw(screen)
        for text in floating_texts:
            text.draw(screen, font_small)
        
        if player:
            draw_ui(player, level_manager, show_fps, clock)
        draw_camera_preview(tracker, camera_working, camera_enabled)
        
        if player:
            if player.shield_active:
                draw_text("KHIEN DANG HOAT DONG", WIDTH//2, HEIGHT - 140, COLORS["CYAN"], font_small, center=True)
            if player.infinite_ammo_permanent:
                draw_text("DAN VINH VIEN", WIDTH//2, HEIGHT - 120, COLORS["YELLOW"], font_small, center=True)
            if camera_working and follow_mode_enabled:
                draw_text("FOLLOW MODE DANG BAT", WIDTH//2, HEIGHT - 160, COLORS["GREEN"], font_small, center=True)
        
        if gesture_display_timer > 0:
            gesture_display_timer -= 1
            if last_gesture_display:
                icon = get_gesture_icon(last_gesture_display)
                desc = get_gesture_description(last_gesture_display)
                draw_text(f"{icon} {desc}", WIDTH//2, 80, COLORS["GREEN"], font_medium, center=True)
        
        if message_timer > 0:
            message_timer -= 1
            draw_text(message, WIDTH//2, HEIGHT - 50, message_color, font_small, center=True, shadow=True)
        
        if level_transition:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            if level_manager:
                draw_text(f"{level_manager.current_name()}", WIDTH//2, HEIGHT//2, COLORS["YELLOW"], font_large, center=True, shadow=True)
        
        if game_over and player:
            draw_game_over(player, level_manager)
        elif victory and player:
            draw_victory(player)
        
        if not in_menu and not game_over and not victory:
            if camera_working:
                draw_text("M:Menu | C:Camera | H:Follow Mode | P:Tam dung", WIDTH - 320, 10, COLORS["GRAY"], font_tiny)
            else:
                draw_text("M: Menu | C: Camera | P: Tam dung", WIDTH - 250, 10, COLORS["GRAY"], font_tiny)
        
        if camera_working:
            if follow_mode_enabled:
                draw_text("FOLLOW MODE: Dua tay trai/phai de di chuyen nhan vat", 
                         WIDTH//2, HEIGHT - 20, COLORS["GREEN"], font_tiny, center=True)
            else:
                draw_text("Camera ON", 
                         WIDTH//2, HEIGHT - 20, COLORS["CYAN"], font_tiny, center=True)
        else:
            draw_text("Khong co Camera | Mui ten/SPACE/J | B:God | N:Normal | M:Menu | Q:Thoat", 
                     WIDTH//2, HEIGHT - 20, COLORS["ORANGE"], font_tiny, center=True)
        
        pygame.display.flip()

except Exception as e:
    print(f"\nGAME CRASHED: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")

finally:
    print("\nShutting down...")
    if tracker:
        try:
            tracker.release()
        except:
            pass
    pygame.quit()
    print("Game closed successfully!")