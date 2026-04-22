# player.py
import pygame
import math
from config import WIDTH, HEIGHT, GROUND_Y, COLORS

# Đảm bảo có đầy đủ các màu cần thiết
if "SILVER" not in COLORS:
    COLORS["SILVER"] = (192, 192, 192)
if "CYAN" not in COLORS:
    COLORS["CYAN"] = (0, 255, 255)
if "GOLD" not in COLORS:
    COLORS["GOLD"] = (255, 215, 0)


class Player:
    def __init__(self):
        self.w = 64
        self.h = 64
        self.x = WIDTH // 2 - self.w // 2
        self.y = GROUND_Y - self.h
        self.ground_y = GROUND_Y - self.h
        
        self.vx = 0
        self.acceleration = 1.2
        self.deceleration = 0.88
        self.max_speed = 7
        
        self.is_jumping = False
        self.velocity_y = 0
        self.gravity = 0.65
        self.jump_power = -13
        
        self.hp = 5
        self.max_hp = 5
        self.score = 0
        self.god_mode = False
        
        self.invincible = 0
        self.dodge_timer = 0
        self.attack_cooldown = 0
        self.heal_cooldown = 0
        self.gun_cooldown = 0
        self.gun_damage = 1  # SỬA: mỗi phát đạn gây 1 sát thương
        
        self.ammo = 30
        self.max_ammo = 99
        
        self.ultimate_cooldown = 0
        self.ultimate_max_cooldown = 600
        
        self.animation_frame = 0
        self.facing_right = True
        self.combo_count = 0
        self.combo_timer = 0
        
        self.bullets = []
        self.trail = []
        
        self.shield_active = False
        self.shield_timer = 0
        
        # ĐẠN VĨNH VIỄN
        self.infinite_ammo_permanent = False
        
        # Thống kê bắn trúng boss
        self.boss_hit_count = 0
        
    def reset(self):
        """Reset player stats for new game"""
        self.hp = self.max_hp
        self.score = 0
        self.ammo = 30
        self.ultimate_cooldown = 0
        self.infinite_ammo_permanent = False
        self.shield_active = False
        self.shield_timer = 0
        self.god_mode = False
        self.invincible = 0
        self.dodge_timer = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.bullets.clear()
        self.trail.clear()
        self.boss_hit_count = 0
        self.x = WIDTH // 2 - self.w // 2
        self.y = GROUND_Y - self.h
        self.vx = 0
        self.is_jumping = False
        self.velocity_y = 0
        self.attack_cooldown = 0
        self.heal_cooldown = 0
        self.gun_cooldown = 0
        self.animation_frame = 0
        self.facing_right = True
        
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def move_left(self):
        self.vx = max(-self.max_speed, self.vx - self.acceleration)
        self.facing_right = False

    def move_right(self):
        self.vx = min(self.max_speed, self.vx + self.acceleration)
        self.facing_right = True

    def jump(self):
        if not self.is_jumping and self.y >= self.ground_y - 5:
            self.is_jumping = True
            self.velocity_y = self.jump_power
            self.animation_frame = 8
            return True
        return False

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 12
            self.animation_frame = 6
            self.combo_timer = 30
            self.combo_count = min(3, self.combo_count + 1)
            return True
        return False

    def get_attack_damage(self):
        base_damage = 1
        if self.combo_count >= 3:
            return base_damage + 2
        elif self.combo_count >= 2:
            return base_damage + 1
        return base_damage

    def shoot(self):
        if self.gun_cooldown <= 0 and (self.infinite_ammo_permanent or self.ammo > 0):
            if not self.infinite_ammo_permanent:
                self.ammo -= 1
            self.gun_cooldown = 20
            direction = 1 if self.facing_right else -1
            bullet = PlayerBullet(self.x + self.w//2, self.y + self.h//2 - 5, self.gun_damage, direction)
            self.bullets.append(bullet)
            return True
        return False

    def dodge(self):
        if self.dodge_timer <= 0:
            self.dodge_timer = 15
            self.invincible = 20
            dash_dir = 1 if self.facing_right else -1
            self.vx = dash_dir * 12
            return True
        return False

    def heal(self, amount=1):
        if self.heal_cooldown <= 0 and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + amount)
            self.heal_cooldown = 120
            return True
        return False
        
    def ultimate(self):
        if self.ultimate_cooldown <= 0:
            self.ultimate_cooldown = self.ultimate_max_cooldown
            return True
        return False
        
    def full_heal(self):
        self.hp = self.max_hp
        self.combo_count = 0
        self.ammo = min(self.max_ammo, self.ammo + 10)

    def toggle_god_mode(self):
        self.god_mode = not self.god_mode
        return self.god_mode

    def hit(self, damage=1):
        if self.god_mode or self.invincible > 0:
            return False
        if self.shield_active:
            self.shield_active = False
            self.shield_timer = 0
            self.animation_frame = 8
            return False
        self.hp -= damage
        self.invincible = 35
        self.combo_count = 0
        self.animation_frame = 10
        return True
    
    def activate_shield(self, duration):
        self.shield_active = True
        self.shield_timer = duration
    
    def activate_permanent_infinite_ammo(self):
        """Kích hoạt đạn VĨNH VIỄN"""
        self.infinite_ammo_permanent = True
        self.ammo = self.max_ammo
        print("🔫 PERMANENT INFINITE AMMO ACTIVATED!")

    def update(self):
        self.x += self.vx
        self.vx *= self.deceleration
        self.x = max(0, min(WIDTH - self.w, self.x))
        
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.is_jumping = False
                self.velocity_y = 0
                self.animation_frame = 4
        
        self.invincible = max(0, self.invincible - 1)
        self.dodge_timer = max(0, self.dodge_timer - 1)
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        self.heal_cooldown = max(0, self.heal_cooldown - 1)
        self.gun_cooldown = max(0, self.gun_cooldown - 1)
        self.ultimate_cooldown = max(0, self.ultimate_cooldown - 1)
        self.animation_frame = max(0, self.animation_frame - 1)

        if self.dodge_timer > 0 or abs(self.vx) > 4:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 12:
                self.trail.pop(0)
        elif self.trail:
            self.trail.pop(0)
        
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0
        
        for b in self.bullets[:]:
            b.update()
            if b.dead:
                self.bullets.remove(b)

    def draw(self, screen, image=None):
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0 and not self.god_mode:
            return

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(70 + 100 * (i / max(1, len(self.trail) - 1))) if len(self.trail) > 1 else 120
            trail_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            pygame.draw.rect(trail_surf, (255, 255, 120, alpha), trail_surf.get_rect(), border_radius=12)
            screen.blit(trail_surf, (tx, ty))

        if image is not None:
            sprite = image
            if not self.facing_right:
                sprite = pygame.transform.flip(image, True, False)
            screen.blit(sprite, (self.x, self.y))
        else:
            shadow_rect = pygame.Rect(self.x + 8, self.y + self.h - 6, self.w - 16, 10)
            pygame.draw.ellipse(screen, (30, 30, 30), shadow_rect)

            if self.god_mode:
                body_color = COLORS["GOLD"]
            elif self.dodge_timer > 0:
                body_color = COLORS["YELLOW"]
            elif self.animation_frame > 5:
                body_color = COLORS["RED"]
            else:
                body_color = COLORS["BLUE"]

            body_rect = pygame.Rect(self.x, self.y, self.w, self.h)
            pygame.draw.rect(screen, body_color, body_rect, border_radius=12)
            pygame.draw.rect(screen, COLORS["WHITE"], body_rect, 2, border_radius=12)

            chest = pygame.Rect(self.x + 8, self.y + 12, self.w - 16, 20)
            pygame.draw.rect(screen, COLORS["CYAN"], chest, border_radius=6)

            belt = pygame.Rect(self.x + 5, self.y + self.h - 18, self.w - 10, 8)
            pygame.draw.rect(screen, COLORS["DARK_GRAY"], belt, border_radius=3)
            pygame.draw.rect(screen, COLORS["GOLD"], (self.x + self.w//2 - 6, self.y + self.h - 18, 12, 8), border_radius=2)

            if self.facing_right:
                shoulder_x = self.x + self.w - 10
            else:
                shoulder_x = self.x - 2
            pygame.draw.rect(screen, COLORS["GRAY"], (shoulder_x, self.y + 8, 12, 16), border_radius=4)

            eye_offset = 2 if self.animation_frame > 3 else 0
            if self.facing_right:
                eye1_x = self.x + self.w - 18
                eye2_x = self.x + self.w - 38
            else:
                eye1_x = self.x + 18
                eye2_x = self.x + 38

            pygame.draw.circle(screen, COLORS["WHITE"], (eye1_x, self.y + 18), 8)
            pygame.draw.circle(screen, COLORS["WHITE"], (eye2_x, self.y + 18), 8)
            pygame.draw.circle(screen, COLORS["BLACK"], (eye1_x + eye_offset, self.y + 18 + eye_offset), 4)
            pygame.draw.circle(screen, COLORS["BLACK"], (eye2_x + eye_offset, self.y + 18 + eye_offset), 4)
            pygame.draw.circle(screen, COLORS["WHITE"], (eye1_x + eye_offset - 1, self.y + 16 + eye_offset), 2)
            pygame.draw.circle(screen, COLORS["WHITE"], (eye2_x + eye_offset - 1, self.y + 16 + eye_offset), 2)

        if self.dodge_timer > 0:
            dodge_surf = pygame.Surface((self.w + 14, self.h + 14), pygame.SRCALPHA)
            pygame.draw.rect(dodge_surf, (255, 220, 120, 90), dodge_surf.get_rect(), border_radius=18)
            screen.blit(dodge_surf, (self.x - 7, self.y - 7))

        if self.shield_active:
            shield_surf = pygame.Surface((self.w + 16, self.h + 16), pygame.SRCALPHA)
            for i in range(3):
                alpha = 100 - i * 25
                color = (0, 255, 255, alpha)
                pygame.draw.rect(shield_surf, color, 
                               (i*2, i*2, self.w + 16 - i*4, self.h + 16 - i*4), 
                               3, border_radius=18)
            screen.blit(shield_surf, (self.x - 8, self.y - 8))
            
            font = pygame.font.SysFont("Arial", 12, bold=True)
            time_left = self.shield_timer // 60 + 1
            shield_text = font.render(f"🛡️ {time_left}s", True, COLORS["CYAN"])
            screen.blit(shield_text, (self.x + self.w//2 - 25, self.y - 20))
        
        if self.infinite_ammo_permanent:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            ammo_text = font.render("🔫 ĐẠN VĨNH VIỄN! 🔫", True, COLORS["YELLOW"])
            screen.blit(ammo_text, (self.x + self.w//2 - 70, self.y - 25))
            
            glow_surf = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 215, 0, 80), glow_surf.get_rect(), border_radius=16)
            screen.blit(glow_surf, (self.x - 10, self.y - 10))
        
        if self.attack_cooldown > 5:
            self.draw_sword(screen)
        
        if self.combo_count >= 2 and self.combo_timer > 0:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            combo_text = f"{self.combo_count}x COMBO!"
            text_color = COLORS["ORANGE"] if self.combo_count == 2 else COLORS["RED"]
            text_surf = font.render(combo_text, True, text_color)
            screen.blit(text_surf, (self.x + self.w//2 - 30, self.y - 20))
    
    def draw_sword(self, screen):
        if self.facing_right:
            sword_start = (self.x + self.w - 10, self.y + self.h//2)
            sword_end = (self.x + self.w + 35, self.y + self.h//2 - 15)
        else:
            sword_start = (self.x + 10, self.y + self.h//2)
            sword_end = (self.x - 35, self.y + self.h//2 - 15)
        
        blade_color = COLORS.get("SILVER", (192, 192, 192))
        pygame.draw.line(screen, blade_color, sword_start, sword_end, 5)
        pygame.draw.line(screen, COLORS["WHITE"], sword_start, sword_end, 2)
        
        slash_center = ((sword_start[0] + sword_end[0])//2, (sword_start[1] + sword_end[1])//2)
        for i in range(3):
            offset = i * 5
            pygame.draw.line(screen, (255, 200, 100), 
                           (slash_center[0] - offset, slash_center[1] - offset),
                           (slash_center[0] + offset, slash_center[1] + offset), 3)

    def draw_bullets(self, screen):
        for b in self.bullets:
            b.draw(screen)


class PlayerBullet:
    def __init__(self, x, y, damage, direction=1):
        self.x = x
        self.y = y
        self.w = 10
        self.h = 6
        self.speed = 14
        self.damage = damage  # Sát thương = 1
        self.dead = False
        self.direction = direction
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        
        self.x += self.speed * self.direction
        if self.x < -50 or self.x > WIDTH + 50:
            self.dead = True

    def draw(self, screen):
        for i, (tx, ty) in enumerate(self.trail):
            fade = int(90 * ((i + 1) / max(1, len(self.trail))))
            trail_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            pygame.draw.rect(trail_surf, (255, 235, 140, fade), trail_surf.get_rect(), border_radius=3)
            screen.blit(trail_surf, (tx, ty))

        for i, (tx, ty) in enumerate(self.trail[-3:], start=1):
            glow_alpha = int(90 * (i / 3))
            glow_surf = pygame.Surface((self.w + 8, self.h + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 180, 80, glow_alpha), glow_surf.get_rect(), border_radius=4)
            screen.blit(glow_surf, (tx - 4, ty - 4))

        pygame.draw.rect(screen, COLORS["YELLOW"], self.rect, border_radius=3)
        pygame.draw.rect(screen, COLORS["ORANGE"], self.rect.inflate(-2, -2), border_radius=2)