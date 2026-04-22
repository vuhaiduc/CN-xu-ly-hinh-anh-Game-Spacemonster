# menu.py
import pygame
import random
from config import WIDTH, HEIGHT, COLORS, LEVEL_NAMES, BOSS_INFO

# Global screen reference
_menu_screen = None

def set_menu_screen(screen_obj):
    """Set global screen reference for menu drawing"""
    global _menu_screen
    _menu_screen = screen_obj

def draw_text(text, x, y, color, font, center=False, shadow=False):
    """Vẽ text lên screen"""
    global _menu_screen
    if _menu_screen is None:
        return
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        _menu_screen.blit(shadow_surf, (x + 2, y + 2))
    surf = font.render(text, True, color)
    if center:
        _menu_screen.blit(surf, surf.get_rect(center=(x, y)))
    else:
        _menu_screen.blit(surf, (x, y))


class MainMenu:
    def __init__(self):
        self.state = "main"  # main, level_select, help
        self.selected_option = 0
        self.selected_level = 0
        
        self.main_options = [" BAT DAU ", "HUONG DAN"]
        self.level_options = []
        for i, name in enumerate(LEVEL_NAMES, 1):
            self.level_options.append(f"Màn {i}: {name}")
        
        self.animation_frame = 0
        self.title_y_offset = 0
        self.particles = []
        
        for _ in range(100):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.5, 2)
            })
        
    def update(self):
        self.animation_frame += 1
        self.title_y_offset = int(5 * abs(pygame.time.get_ticks() / 500 % 2 - 1))
        
        for p in self.particles:
            p['y'] += p['speed']
            if p['y'] > HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)
    
    def handle_event(self, event, gesture=None, action=None):
        if self.state == "main":
            # Xử lý keyboard
            if event and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.main_options)
                    return None
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.main_options)
                    return None
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.select_option()
            
            # Xử lý gesture
            if action:
                if action == "menu_up":
                    self.selected_option = (self.selected_option - 1) % len(self.main_options)
                elif action == "menu_down":
                    self.selected_option = (self.selected_option + 1) % len(self.main_options)
                elif action == "select":
                    return self.select_option()
                    
        elif self.state == "help":
            if event and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.state = "main"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.state = "main"
            elif action and action in ["menu_down", "select"]:
                self.state = "main"
            return None
            
        elif self.state == "level_select":
            if event and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_level = (self.selected_level - 1) % len(self.level_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_level = (self.selected_level + 1) % len(self.level_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return ("start_level", self.selected_level + 1)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.state = "main"
                    self.selected_level = 0
                    
            elif action:
                if action == "menu_up":
                    self.selected_level = (self.selected_level - 1) % len(self.level_options)
                elif action == "menu_down":
                    self.selected_level = (self.selected_level + 1) % len(self.level_options)
                elif action == "select":
                    return ("start_level", self.selected_level + 1)
                elif action == "back":
                    self.state = "main"
                    self.selected_level = 0
                    
        return None
    
    def select_option(self):
        if self.selected_option == 0:
            self.state = "level_select"
            return None
        elif self.selected_option == 1:
            self.state = "help"
            return None
        return None
    
    def draw(self, screen_obj):
        global _menu_screen
        _menu_screen = screen_obj
        
        # Background gradient
        for i in range(HEIGHT):
            t = i / HEIGHT
            r = int(10 + t * 30)
            g = int(5 + t * 20)
            b = int(30 + t * 50)
            pygame.draw.line(_menu_screen, (r, g, b), (0, i), (WIDTH, i))
        
        # Stars
        for p in self.particles:
            brightness = 100 + p['size'] * 50
            pygame.draw.circle(_menu_screen, (brightness, brightness, brightness), 
                             (int(p['x']), int(p['y'])), p['size'])
        
        # Main panel
        panel = pygame.Surface((720, 440), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 18, 36, 220), panel.get_rect(), border_radius=30)
        pygame.draw.rect(panel, (255, 255, 255, 20), panel.get_rect(), 2, border_radius=30)
        _menu_screen.blit(panel, (WIDTH//2 - 360, HEIGHT//2 - 260))
        
        # Title
        font_title = pygame.font.SysFont("Arial", 72, bold=True)
        
        title_y = HEIGHT // 4 + self.title_y_offset
        title_shadow = font_title.render("GALACTIC GUARDIAN", True, (0, 0, 0))
        _menu_screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, title_y + 3))
        
        title_color = COLORS["GOLD"]
        if self.animation_frame % 30 < 15:
            title_color = COLORS["YELLOW"]
        title = font_title.render("GALACTIC GUARDIAN", True, title_color)
        _menu_screen.blit(title, (WIDTH//2 - title.get_width()//2, title_y))
        
        font_sub = pygame.font.SysFont("Arial", 20)
        sub_text = font_sub.render("Gesture Control Adventure", True, COLORS["CYAN"])
        _menu_screen.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, title_y + 80))
        
        if self.state == "main":
            self.draw_main_menu()
        elif self.state == "help":
            self.draw_help_screen()
        elif self.state == "level_select":
            self.draw_level_select()
    
    def draw_main_menu(self):
        font = pygame.font.SysFont("Arial", 36)
        font_small = pygame.font.SysFont("Arial", 18)
        
        gestures_y = HEIGHT - 90
        gestures = [
            ("⬆️⬇️", "Chọn", COLORS["CYAN"]),
            ("✊/✋", "Xác nhận", COLORS["GREEN"]),
        ]
        
        for i, (icon, text, color) in enumerate(gestures):
            x = WIDTH//2 - 150 + i * 200
            icon_surf = font_small.render(icon, True, color)
            text_surf = font_small.render(text, True, COLORS["WHITE"])
            _menu_screen.blit(icon_surf, (x, gestures_y))
            _menu_screen.blit(text_surf, (x, gestures_y + 25))
        
        menu_y = HEIGHT // 2 - 20
        for i, option in enumerate(self.main_options):
            color = COLORS["YELLOW"] if i == self.selected_option else COLORS["WHITE"]
            
            if i == self.selected_option:
                glow = pygame.Surface((380, 56), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 140, 60), glow.get_rect(), border_radius=18)
                _menu_screen.blit(glow, (WIDTH//2 - 190, menu_y + i * 80 - 10))
                arrow = font.render("▶", True, COLORS["GREEN"])
                _menu_screen.blit(arrow, (WIDTH//2 - 180, menu_y + i * 80 + 4))
            
            text = font.render(option, True, color)
            _menu_screen.blit(text, (WIDTH//2 - text.get_width()//2, menu_y + i * 80))
    
    def draw_level_select(self):
        font = pygame.font.SysFont("Arial", 26)
        font_title = pygame.font.SysFont("Arial", 36, bold=True)
        font_small = pygame.font.SysFont("Arial", 16)
        
        title = font_title.render("CHỌN MÀN CHƠI", True, COLORS["GOLD"])
        _menu_screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4 - 50))
        
        info_panel = pygame.Surface((760, 360), pygame.SRCALPHA)
        pygame.draw.rect(info_panel, (16, 22, 40, 210), info_panel.get_rect(), border_radius=24)
        pygame.draw.rect(info_panel, (255, 255, 255, 20), info_panel.get_rect(), 2, border_radius=24)
        _menu_screen.blit(info_panel, (WIDTH//2 - 380, HEIGHT//4 + 20))

        back_text = font_small.render("🤟 (ba ngón) để quay lại", True, COLORS["GRAY"])
        _menu_screen.blit(back_text, (WIDTH - 230, HEIGHT - 40))
        
        select_text = font_small.render("⬆️⬇️ Chọn | ✊ Xác nhận", True, COLORS["CYAN"])
        _menu_screen.blit(select_text, (20, HEIGHT - 40))
        
        start_y = HEIGHT // 4 + 60
        visible_items = min(5, len(self.level_options))
        
        scroll_offset = max(0, min(len(self.level_options) - visible_items, 
                                   self.selected_level - visible_items // 2))
        
        for i in range(visible_items):
            idx = scroll_offset + i
            if idx < len(self.level_options):
                is_selected = (idx == self.selected_level)
                color = COLORS["YELLOW"] if is_selected else COLORS["WHITE"]
                
                y_pos = start_y + i * 55
                
                if idx == 4:
                    boss_icon = "👑"
                elif idx == 1:
                    boss_icon = "🔥"
                elif idx == 2:
                    boss_icon = "❄️"
                else:
                    boss_icon = "👾"
                boss_surf = font_small.render(boss_icon, True, COLORS["RED"] if idx == 4 else COLORS["CYAN"])
                
                card_x = WIDTH//2 - 320
                card_w = 640
                card_h = 50
                card_rect = pygame.Rect(card_x, y_pos - 8, card_w, card_h)
                if is_selected:
                    highlight = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                    pygame.draw.rect(highlight, (255, 215, 0, 50), highlight.get_rect(), border_radius=16)
                    pygame.draw.rect(highlight, (255, 255, 255, 20), highlight.get_rect(), 2, border_radius=16)
                    _menu_screen.blit(highlight, card_rect.topleft)
                    arrow = font.render("▶", True, COLORS["GREEN"])
                    _menu_screen.blit(arrow, (card_x + 8, y_pos + 4))
                
                text_surf = font.render(self.level_options[idx], True, color)
                _menu_screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_pos))
                _menu_screen.blit(boss_surf, (card_x + 16, y_pos + 10))
                
                difficulty = "⭐" * min(5, idx + 1)
                diff_surf = font_small.render(difficulty, True, COLORS["GOLD"] if idx >= 3 else COLORS["SILVER"])
                _menu_screen.blit(diff_surf, (card_x + card_w - diff_surf.get_width() - 16, y_pos + 12))

    def draw_help_screen(self):
        font_title = pygame.font.SysFont("Arial", 46, bold=True)
        font_text = pygame.font.SysFont("Arial", 22)
        font_small = pygame.font.SysFont("Arial", 18)

        help_lines = [
            "HƯỚNG DẪN CHƠI",
            "",
            "🖐️ FOLLOW MODE: Di chuyển nhân vật bằng tay",
            "✊ NAM DAM: Đấm cận chiến",
            "✊ + VUỐT: Di chuyển nhanh",
            "☝️ + KÉO LÊN: Nhảy",
            "✌️: Bắn súng",
            "🤟: Hồi máu",
            "👍: Chiêu cuối",
            "",
            "🔫 SÚNG VÀNG: ĐẠN VĨNH VIỄN!",
            "",
            "HOẶC dùng bàn phím:",
            "← → : Di chuyển",
            "SPACE : Đánh cận chiến",
            "F : Bắn xa",
            "J : Nhảy",
            "B : God mode",
            "N : Hồi máu/Normal",
            "M : Menu",
            "P : Pause",
            "Q : Thoát",
            "",
            "Nhấn ESC hoặc SPACE để quay lại menu"
        ]

        _menu_screen.fill((8, 12, 20))
        title = font_title.render(help_lines[0], True, COLORS["GOLD"])
        _menu_screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        y = 150
        for line in help_lines[1:]:
            # Bỏ qua dòng trống
            if not line:
                y += 12
                continue
            
            # Xác định màu sắc dựa trên nội dung dòng
            if any(line.startswith(emoji) for emoji in ["🖐️", "✊", "☝️", "✌️", "🤟", "👍", "🔫"]):
                color = COLORS["CYAN"]
            elif any(line.startswith(key) for key in ["←", "→", "SPACE", "ESC", "F ", "J ", "B ", "N ", "M ", "P ", "Q "]):
                color = COLORS["YELLOW"]
            elif line.startswith("HOẶC") or line.startswith("Nhấn"):
                color = COLORS["GOLD"]
            else:
                color = COLORS["WHITE"]
            
            # Chọn font dựa trên loại dòng
            if line.startswith("HOẶC") or line.startswith("Nhấn"):
                font = font_small
            else:
                font = font_text
                
            text = font.render(line, True, color)
            _menu_screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 28