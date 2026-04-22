# boss.py
import pygame
import random
import math
from config import WIDTH, HEIGHT, GROUND_Y, COLORS, BOSS_INFO


class Boss:
    def __init__(self, level=1):
        self.level = level
        self.info = BOSS_INFO.get(level, BOSS_INFO[1])
        
        self.x = WIDTH // 2 - 80
        self.y = GROUND_Y - 140
        self.w = 160
        self.h = 130
        self.max_hp = self.info["hp"]
        self.hp = self.max_hp
        self.phase = 1
        self.dead = False
        self.invincible = False
        self.invincible_timer = 0
        self.animation_frame = 0
        self.action_timer = 0
        self.current_action = "idle"
        self.projectiles = []
        self.summoned_count = 0
        
        self.dialogue_active = True
        self.dialogue_index = 0
        self.dialogue_timer = 0
        self.dialogue_text = ""
        self.dialogue_char_index = 0
        self.dialogue_done = False
        self.dialogue_line_display = ""
        
        self.player_dialogue_active = False
        self.player_dialogue_index = 0
        self.player_dialogue_timer = 0
        self.player_dialogue_text = ""
        self.player_dialogue_char_index = 0
        self.player_dialogue_line_display = ""
        self.waiting_for_player_response = False
        self.player_response_selected = 0
        self.player_dialogue_started = False
        self.pre_fight_timer = 0
        self.pre_fight_strike_ready = False
        self.pre_fight_duration = 180
        
        self.move_target_x = self.x
        self.move_speed = 2
        self.original_speed = 2
        
        self.attack_timer = 0
        self.dash_target_x = None
        
        self.phase_actions = {
            1: ["slam", "fireball", "walk"],
            2: ["slam", "fireball", "dash", "walk"],
            3: ["slam", "fireball", "dash", "summon", "ground_pound"]
        }
        self.current_pattern = []
        self.pattern_index = 0
        
        self.particles = []
        self.roar_timer = 0
        
        print(f"👑 Boss {self.info['name']} created! Starting dialogue...")
        self.start_dialogue()

    def _get_safe_rgb(self, color_name):
        color = COLORS.get(color_name, COLORS["RED"])
        if isinstance(color, tuple):
            if len(color) >= 3:
                return (color[0], color[1], color[2])
        return (255, 50, 50)

    def start_dialogue(self):
        self.dialogue_active = True
        self.dialogue_index = 0
        self.dialogue_timer = 30
        self.dialogue_char_index = 0
        self.dialogue_done = False
        self.dialogue_line_display = ""
        self.set_dialogue_text()
        
    def set_dialogue_text(self):
        if self.dialogue_index < len(self.info["dialogue"]):
            self.dialogue_text = self.info["dialogue"][self.dialogue_index]
            self.dialogue_char_index = 0
            self.dialogue_done = False
            self.dialogue_line_display = ""
            print(f"💬 {self.info['name']}: {self.dialogue_text}")
        else:
            self.dialogue_active = False
            self.dialogue_timer = 0
            self.roar_timer = 40
            print(f"⚔️ {self.info['name']}: HAY CHIEN DAU!")
            
    def update_dialogue(self):
        if not self.dialogue_active:
            return
            
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
            return
            
        if self.dialogue_char_index < len(self.dialogue_text):
            self.dialogue_char_index += 1
            self.dialogue_line_display = self.dialogue_text[:self.dialogue_char_index]
            self.dialogue_timer = 2
        else:
            if not self.dialogue_done:
                self.dialogue_done = True
                self.dialogue_timer = 60
            else:
                if self.dialogue_timer <= 0:
                    self.dialogue_index += 1
                    if self.dialogue_index < len(self.info["dialogue"]):
                        self.set_dialogue_text()
                    else:
                        self.dialogue_active = False
                        self.dialogue_timer = 0
                        self.roar_timer = 40
                        print(f"⚔️ {self.info['name']}: HAY CHIEN DAU!")
                else:
                    self.dialogue_timer -= 1

    def start_player_dialogue(self):
        self.player_dialogue_active = True
        self.player_dialogue_index = 0
        self.player_dialogue_timer = 30
        self.waiting_for_player_response = False
        self.set_player_dialogue_text()
        
    def set_player_dialogue_text(self):
        player_dialogues = [
            "Nguoi la ai? Tai sao lai tan cong vu tru nay?",
            "Ta se khong de nguoi pha huy them bat ky hanh tinh nao nua!",
            "Hay dung lai ngay, neu khong ta se phai tieu diet nguoi!",
            "Nguoi co the chon: dau hang hoac chien dau den chet!"
        ]
        
        if self.player_dialogue_index < len(player_dialogues):
            self.player_dialogue_text = player_dialogues[self.player_dialogue_index]
            self.player_dialogue_char_index = 0
            self.player_dialogue_line_display = ""
            print(f"💬 Nguoi choi: {self.player_dialogue_text}")
        else:
            self.player_dialogue_active = False
            self.waiting_for_player_response = False
            
    def update_player_dialogue(self):
        if not self.player_dialogue_active:
            return
            
        if self.player_dialogue_timer > 0:
            self.player_dialogue_timer -= 1
            return
            
        if self.player_dialogue_char_index < len(self.player_dialogue_text):
            self.player_dialogue_char_index += 1
            self.player_dialogue_line_display = self.player_dialogue_text[:self.player_dialogue_char_index]
            self.player_dialogue_timer = 2
        else:
            if not self.waiting_for_player_response:
                self.waiting_for_player_response = True
                self.player_dialogue_timer = 60
            else:
                if self.player_dialogue_timer <= 0:
                    self.player_dialogue_index += 1
                    if self.player_dialogue_index < 4:
                        self.set_player_dialogue_text()
                    else:
                        self.player_dialogue_active = False
                        self.waiting_for_player_response = False
                        self.start_pre_fight()
                else:
                    self.player_dialogue_timer -= 1
                    
    def handle_player_response(self, choice):
        if choice == 0:
            print("💬 Nguoi choi: Toi dau hang...")
            self.waiting_for_player_response = False
            self.player_dialogue_active = False
            self.dialogue_active = False
            self.pre_fight_timer = 0
            return "surrender"
        elif choice == 1:
            print("💬 Nguoi choi: Toi se chien dau den cung!")
            self.waiting_for_player_response = False
            self.player_dialogue_active = False
            self.dialogue_active = False
            self.start_pre_fight()
            return "fight"
        return None

    def start_pre_fight(self):
        self.pre_fight_timer = self.pre_fight_duration
        self.pre_fight_strike_ready = True
        self.current_action = "idle"
        self.action_timer = 0
        self.pattern_index = 0
        self.roar_timer = 0
        print(f"⏳ Boss chuan bi phan kich trong {self.pre_fight_duration // 60} giay...")

    def is_dialogue_active(self):
        return self.dialogue_active
    
    def is_player_dialogue_active(self):
        return self.player_dialogue_active
    
    def is_waiting_for_response(self):
        return self.waiting_for_player_response

    def get_dialogue_display_text(self):
        if not self.dialogue_active:
            return None
        return self.dialogue_line_display
    
    def get_player_dialogue_display_text(self):
        if not self.player_dialogue_active:
            return None
        return self.player_dialogue_line_display

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, player_x=None):
        if self.dialogue_active or self.player_dialogue_active:
            return
            
        if self.pre_fight_timer > 0:
            self.pre_fight_timer -= 1
            return
            
        old_phase = self.phase
        if self.hp <= self.max_hp * 0.3:
            self.phase = 3
        elif self.hp <= self.max_hp * 0.6:
            self.phase = 2
        else:
            self.phase = 1
        
        if old_phase != self.phase:
            self.invincible = True
            self.invincible_timer = 80
            self.animation_frame = 15
            self.roar_timer = 30
            self.current_pattern = []
            self.pattern_index = 0
            print(f"⚠️ {self.info['name']} chuyen sang PHASE {self.phase}!")
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        else:
            self.invincible = False
        
        if self.animation_frame > 0:
            self.animation_frame -= 1
        if self.roar_timer > 0:
            self.roar_timer -= 1
        
        if self.current_action == "walk" and self.phase >= 2:
            if abs(self.x - self.move_target_x) < 15:
                self.move_target_x = random.randint(50, WIDTH - self.w - 50)
            else:
                step = min(self.move_speed, abs(self.x - self.move_target_x))
                if self.move_target_x > self.x:
                    self.x += step
                else:
                    self.x -= step
        
        elif self.current_action == "dash" and self.dash_target_x is not None:
            dash_speed = 12
            if abs(self.x - self.dash_target_x) < dash_speed:
                self.current_action = "idle"
                self.dash_target_x = None
                self.move_speed = self.original_speed
            else:
                if self.dash_target_x > self.x:
                    self.x += dash_speed
                else:
                    self.x -= dash_speed
        
        if self.action_timer <= 0 and not self.dead and player_x is not None:
            self.choose_action(player_x)
        else:
            self.action_timer -= 1
        
        for p in self.projectiles[:]:
            p.update()
            if p.dead:
                self.projectiles.remove(p)
        
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
            if p[4] <= 0:
                self.particles.remove(p)

    def choose_action(self, player_x):
        if not self.current_pattern or self.pattern_index >= len(self.current_pattern):
            self.current_pattern = self.phase_actions[self.phase][:]
            random.shuffle(self.current_pattern)
            self.pattern_index = 0
        
        self.current_action = self.current_pattern[self.pattern_index]
        self.pattern_index += 1
        
        action_durations = {
            "slam": 45,
            "fireball": 50,
            "walk": 80,
            "dash": 60,
            "summon": 70,
            "ground_pound": 55
        }
        self.action_timer = action_durations.get(self.current_action, 60)
        
        if self.current_action == "slam":
            self.animation_frame = 12
            self.attack_timer = 35
            
        elif self.current_action == "fireball":
            self.shoot_fireball(player_x)
            
        elif self.current_action == "dash":
            self.move_speed = 12
            self.dash_target_x = player_x - self.w//2
            self.dash_target_x = max(50, min(WIDTH - self.w - 50, self.dash_target_x))
            
        elif self.current_action == "summon":
            self.summoned_count = random.randint(2, 4)
            
        elif self.current_action == "ground_pound":
            self.animation_frame = 10
            self.action_timer = 40
            
        for _ in range(5):
            self.particles.append([
                self.x + self.w//2 + random.randint(-20, 20),
                self.y + self.h//2,
                random.uniform(-3, 3),
                random.uniform(-2, -5),
                20
            ])

    def shoot_fireball(self, player_x):
        num_shots = 1 if self.phase < 3 else 3
        for i in range(num_shots):
            offset = (i - num_shots//2) * 40
            target_x = player_x + offset
            fireball = BossFireball(self.x + self.w//2, self.y + self.h//2, target_x, self.phase)
            fireball.damage = 1 if self.phase < 3 else 2
            self.projectiles.append(fireball)

    def can_attack(self):
        return (self.current_action in ["slam", "ground_pound"] and 
                self.animation_frame <= 3 and 
                self.action_timer > 20)

    def take_hit(self, amount=1):
        if self.invincible or self.dialogue_active or self.player_dialogue_active:
            return 0
        self.hp -= amount
        self.animation_frame = 8
        self.invincible = True
        self.invincible_timer = 25
        
        print(f"💥 Boss nhan {amount} sat thuong! HP: {self.hp}/{self.max_hp}")
        
        for _ in range(10):
            self.particles.append([
                self.x + random.randint(0, self.w),
                self.y + random.randint(0, self.h),
                random.uniform(-4, 4),
                random.uniform(-3, -1),
                15
            ])
        
        if self.hp <= 0:
            self.dead = True
            print(f"💀 Boss {self.info['name']} da bi danh bai!")
            return 500 + self.level * 100
        return 50 + self.level * 10

    def get_attack_damage(self):
        return [1, 2, 3][self.phase - 1] + (self.level // 2)

    def draw(self, screen, images=None, player_x=None):
        if self.invincible and (self.invincible_timer // 4) % 2 == 0:
            pass
        
        draw_x = self.x
        draw_y = self.y
        
        facing_right = True
        if player_x is not None:
            facing_right = player_x > self.x + self.w//2
        
        shadow_rect = pygame.Rect(draw_x + 10, draw_y + self.h - 10, self.w - 20, 15)
        pygame.draw.ellipse(screen, (30, 30, 30), shadow_rect)
        
        img_drawn = False
        if images and self.level in images:
            boss_img = images[self.level]
            if boss_img:
                screen.blit(boss_img, (draw_x, draw_y))
                img_drawn = True
        
        if not img_drawn:
            body_color = self._get_safe_rgb(self.info["color"])
            pygame.draw.rect(screen, body_color, (draw_x, draw_y, self.w, self.h), border_radius=16)
            pygame.draw.rect(screen, COLORS["WHITE"], (draw_x, draw_y, self.w, self.h), 3, border_radius=16)
            
            pygame.draw.rect(screen, COLORS["DARK_GRAY"], (draw_x + 10, draw_y + 15, self.w - 20, 25), border_radius=6)
            
            if facing_right:
                eye1_x = draw_x + self.w - 40
                eye2_x = draw_x + self.w - 80
            else:
                eye1_x = draw_x + 40
                eye2_x = draw_x + 80
            
            if self.current_action != "idle":
                eye_color = COLORS["RED"]
                eye_y_offset = 5
            else:
                eye_color = COLORS["YELLOW"]
                eye_y_offset = 0
            
            pygame.draw.circle(screen, eye_color, (eye1_x, draw_y + 45), 16)
            pygame.draw.circle(screen, eye_color, (eye2_x, draw_y + 45), 16)
            pygame.draw.circle(screen, COLORS["BLACK"], (eye1_x + (3 if facing_right else -3), draw_y + 45 + eye_y_offset), 8)
            pygame.draw.circle(screen, COLORS["BLACK"], (eye2_x + (3 if facing_right else -3), draw_y + 45 + eye_y_offset), 8)
            
            mouth_rect = pygame.Rect(draw_x + self.w//2 - 20, draw_y + 75, 40, 15)
            pygame.draw.ellipse(screen, COLORS["DARK_GRAY"], mouth_rect)
            
            if self.level >= 2:
                horn_points = [(draw_x + 20, draw_y), (draw_x + 35, draw_y - 25), (draw_x + 50, draw_y)]
                pygame.draw.polygon(screen, COLORS["DARK_GRAY"], horn_points)
                horn_points2 = [(draw_x + self.w - 20, draw_y), (draw_x + self.w - 35, draw_y - 25), (draw_x + self.w - 50, draw_y)]
                pygame.draw.polygon(screen, COLORS["DARK_GRAY"], horn_points2)
        
        name_font = pygame.font.Font(None, 18)
        name_text = name_font.render(self.info["name"], True, COLORS["GOLD"])
        screen.blit(name_text, (draw_x + self.w//2 - name_text.get_width()//2, draw_y - 25))
        
        title_font = pygame.font.Font(None, 12)
        title_text = title_font.render(self.info["title"], True, COLORS["SILVER"])
        screen.blit(title_text, (draw_x + self.w//2 - title_text.get_width()//2, draw_y - 12))
        
        if self.roar_timer > 0:
            for i in range(5):
                offset = i * 3
                pygame.draw.rect(screen, (255, 100, 0), 
                               (draw_x - offset, draw_y - offset, self.w + offset*2, self.h + offset*2), 
                               2, border_radius=20)
        
        for p in self.particles:
            color = (255, 100, 50)
            pygame.draw.circle(screen, color, (int(p[0]), int(p[1])), 3)

    def draw_dialogue(self, screen):
        if not self.dialogue_active:
            return
        
        text = self.get_dialogue_display_text()
        if not text:
            return
        
        box_width = 680
        box_height = 130
        box_x = WIDTH // 2 - box_width // 2
        box_y = HEIGHT - 170
        
        bg_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (12, 14, 22), bg_rect, border_radius=20)
        pygame.draw.rect(screen, (12, 14, 22), bg_rect.inflate(-4, -4), border_radius=18)
        
        border_color = self._get_safe_rgb(self.info["color"])
        pygame.draw.rect(screen, border_color, bg_rect, 3, border_radius=20)
        
        name_font = pygame.font.Font(None, 22)
        name_text = name_font.render(f"{self.info['name']} - {self.info['title']}", True, COLORS["WHITE"])
        screen.blit(name_text, (box_x + box_width // 2 - name_text.get_width() // 2, box_y + 12))
        
        text_font = pygame.font.Font(None, 20)
        
        words = list(text)
        lines = []
        current_line = ""
        max_width = box_width - 60
        
        for char in words:
            test_line = current_line + char
            if text_font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines):
            text_surf = text_font.render(line, True, COLORS["WHITE"])
            screen.blit(text_surf, (box_x + box_width // 2 - text_surf.get_width() // 2, box_y + 44 + i * 26))
        
        if self.dialogue_done and self.dialogue_timer <= 30:
            indicator = "▼" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
            cont_font = pygame.font.Font(None, 20)
            cont_surf = cont_font.render(indicator, True, COLORS["WHITE"])
            screen.blit(cont_surf, (box_x + box_width - 30, box_y + box_height - 26))
    
    def draw_player_dialogue(self, screen):
        if not self.player_dialogue_active:
            return
        
        text = self.get_player_dialogue_display_text()
        if not text:
            return
        
        box_width = 620
        box_height = 140
        box_x = WIDTH // 2 - box_width // 2
        box_y = HEIGHT - 260
        
        bg_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (16, 24, 16), bg_rect, border_radius=20)
        pygame.draw.rect(screen, (16, 24, 16), bg_rect.inflate(-4, -4), border_radius=18)
        
        pygame.draw.rect(screen, (0, 200, 120), bg_rect, 3, border_radius=20)
        
        name_font = pygame.font.Font(None, 22)
        name_text = name_font.render("Galactic Guardian", True, COLORS["GREEN"])
        screen.blit(name_text, (box_x + box_width // 2 - name_text.get_width() // 2, box_y + 12))
        
        text_font = pygame.font.Font(None, 20)
        
        words = list(text)
        lines = []
        current_line = ""
        max_width = box_width - 60
        
        for char in words:
            test_line = current_line + char
            if text_font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines):
            text_surf = text_font.render(line, True, COLORS["WHITE"])
            screen.blit(text_surf, (box_x + box_width // 2 - text_surf.get_width() // 2, box_y + 44 + i * 26))
        
        if self.waiting_for_player_response:
            choice_font = pygame.font.Font(None, 20)
            button_width = 420
            button_height = 40
            btn_x = box_x + box_width // 2 - button_width // 2
            btn_y = box_y + box_height - button_height - 15
            
            pygame.draw.rect(screen, (255, 215, 0), (btn_x, btn_y, button_width, button_height), border_radius=14)
            pygame.draw.rect(screen, (255, 255, 0), (btn_x, btn_y, button_width, button_height), 2, border_radius=14)
            
            choice1 = choice_font.render("1. Dau hang", True, (0, 0, 0))
            choice2 = choice_font.render("2. Chien dau", True, (0, 0, 0))
            
            screen.blit(choice1, (btn_x + 50, btn_y + button_height // 2 - choice1.get_height() // 2))
            screen.blit(choice2, (btn_x + button_width - 150, btn_y + button_height // 2 - choice2.get_height() // 2))

    def draw_projectiles(self, screen):
        for p in self.projectiles:
            p.draw(screen)

    def draw_health_bar(self, screen):
        bar_width = 600
        bar_height = 32
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 10
        
        pygame.draw.rect(screen, COLORS["DARK_GRAY"], (bar_x, bar_y, bar_width, bar_height), border_radius=16)
        
        hp_percent = self.hp / self.max_hp
        fill_color = self._get_safe_rgb(self.info["color"])
        fill_width = bar_width * hp_percent
        
        for i in range(int(fill_width)):
            t = i / bar_width
            r = fill_color[0]
            g = int(fill_color[1] * (1 - t * 0.5))
            b = int(fill_color[2] * (1 + t * 0.3))
            pygame.draw.line(screen, (r, g, b), (bar_x + i, bar_y + 4), (bar_x + i, bar_y + bar_height - 4))
        
        pygame.draw.rect(screen, COLORS["WHITE"], (bar_x, bar_y, bar_width, bar_height), 2, border_radius=16)
        
        font = pygame.font.Font(None, 22)
        phase_text = font.render(f"{self.info['name']} - PHASE {self.phase}", True, COLORS["WHITE"])
        screen.blit(phase_text, (bar_x + bar_width // 2 - phase_text.get_width() // 2, bar_y - 28))
        
        hp_text = font.render(f"HP: {self.hp}/{self.max_hp}", True, COLORS["WHITE"])
        screen.blit(hp_text, (bar_x + bar_width // 2 - hp_text.get_width() // 2, bar_y + 8))
        
        remaining_shots = self.hp
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 18)
        
        if self.hp <= 2:
            if (pygame.time.get_ticks() // 300) % 2 == 0:
                shots_color = COLORS["RED"]
            else:
                shots_color = COLORS["YELLOW"]
        else:
            shots_color = COLORS["YELLOW"]
        
        shots_text = font_medium.render(f"🔫 CAN {remaining_shots} PHAT DAN DE HA BOSS! 🔫", True, shots_color)
        text_x = bar_x + bar_width // 2 - shots_text.get_width() // 2
        text_y = bar_y + bar_height + 12
        
        bg_rect = pygame.Rect(text_x - 10, text_y - 5, shots_text.get_width() + 20, shots_text.get_height() + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=8)
        pygame.draw.rect(screen, shots_color, bg_rect, 2, border_radius=8)
        
        screen.blit(shots_text, (text_x, text_y))
        
        bullet_bar_width = 300
        bullet_bar_height = 8
        bullet_bar_x = bar_x + bar_width // 2 - bullet_bar_width // 2
        bullet_bar_y = text_y + shots_text.get_height() + 8
        
        pygame.draw.rect(screen, COLORS["DARK_GRAY"], (bullet_bar_x, bullet_bar_y, bullet_bar_width, bullet_bar_height), border_radius=4)
        
        bullet_width = bullet_bar_width / self.max_hp
        for i in range(self.max_hp):
            bullet_x = bullet_bar_x + i * bullet_width
            if i < self.hp:
                pygame.draw.rect(screen, COLORS["YELLOW"], (bullet_x, bullet_bar_y, bullet_width - 2, bullet_bar_height), border_radius=2)
            else:
                pygame.draw.rect(screen, COLORS["DARK_GRAY"], (bullet_x, bullet_bar_y, bullet_width - 2, bullet_bar_height), border_radius=2)
        
        pygame.draw.rect(screen, COLORS["WHITE"], (bullet_bar_x, bullet_bar_y, bullet_bar_width, bullet_bar_height), 1, border_radius=4)
        
        if self.hp <= 2:
            warning_font = pygame.font.Font(None, 20)
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                warning_text = warning_font.render("⚠️ BOSS SAP CHET! TIEP TUC BAN! ⚠️", True, COLORS["RED"])
                warning_x = bar_x + bar_width // 2 - warning_text.get_width() // 2
                warning_y = bullet_bar_y + bullet_bar_height + 8
                
                warning_bg = pygame.Rect(warning_x - 10, warning_y - 5, warning_text.get_width() + 20, warning_text.get_height() + 10)
                pygame.draw.rect(screen, (0, 0, 0, 200), warning_bg, border_radius=8)
                pygame.draw.rect(screen, COLORS["RED"], warning_bg, 2, border_radius=8)
                
                screen.blit(warning_text, (warning_x, warning_y))
        
        tip_font = pygame.font.Font(None, 16)
        tip_text = tip_font.render("Moi phat dan gay 1 sat thuong | Dung hai tay ✌️ de ban", True, COLORS["GRAY"])
        tip_x = bar_x + bar_width // 2 - tip_text.get_width() // 2
        tip_y = HEIGHT - 30
        screen.blit(tip_text, (tip_x, tip_y))


class BossFireball:
    def __init__(self, x, y, target_x, phase):
        self.x = x
        self.y = y
        self.w = 24
        self.h = 24
        self.speed = 5 + (phase - 1) * 1.5
        
        dx = target_x - x
        dy = (GROUND_Y + 50) - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        else:
            self.vx = 0
            self.vy = self.speed
        
        self.damage = 1 if phase < 3 else 2
        self.dead = False
        self.trail = []
        self.phase = phase

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.dead = True

    def draw(self, screen):
        for i, (tx, ty) in enumerate(self.trail):
            size = 12 - i
            if size > 0:
                color = (255, 100 + i * 30, 50)
                pygame.draw.circle(screen, color, (int(tx), int(ty)), size)
        
        pygame.draw.circle(screen, (255, 50, 50), (int(self.x), int(self.y)), 12)
        pygame.draw.circle(screen, (255, 150, 50), (int(self.x), int(self.y)), 8)
        pygame.draw.circle(screen, (255, 255, 50), (int(self.x), int(self.y)), 4)
        
        if self.phase >= 3:
            pygame.draw.circle(screen, (255, 100, 0), (int(self.x), int(self.y)), 18, 2)