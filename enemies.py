# enemies.py
import pygame
import random
import math
from config import WIDTH, HEIGHT, COLORS
from settings import ATTACK_RANGE

class Enemy:
    name = "Basic"
    type = "basic"
    hp = 1
    speed = 1.2
    score = 10
    color = COLORS["RED"]
    size = 42
    damage = 1
    attack_cooldown_max = 60
    attack_range = ATTACK_RANGE  # Dùng từ settings
    
    def __init__(self, x, y=0):
        self.x = x
        self.y = y
        self.w = self.size
        self.h = self.size
        self.dead = False
        self.hp_current = self.hp
        self.on_ground = False
        self.attack_timer = 0
        self.move_direction = 1
        self.move_timer = random.randint(60, 180)
        self.animation_offset = 0
        self.ground_y = HEIGHT - 100

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, ground_y=HEIGHT - 100):
        self.ground_y = ground_y
        
        if not self.on_ground:
            self.y += 4
            if self.y + self.h >= ground_y:
                self.y = ground_y - self.h
                self.on_ground = True
        else:
            self.x += self.speed * self.move_direction
            
            if self.x <= 20:
                self.x = 20
                self.move_direction = 1
            elif self.x + self.w >= WIDTH - 20:
                self.x = WIDTH - self.w - 20
                self.move_direction = -1
            
            self.move_timer -= 1
            if self.move_timer <= 0:
                self.move_direction *= -1
                self.move_timer = random.randint(60, 180)
        
        if self.attack_timer > 0:
            self.attack_timer -= 1

    def can_attack(self):
        return self.on_ground and self.attack_timer <= 0

    def attack(self):
        if self.can_attack():
            self.attack_timer = self.attack_cooldown_max
            self.animation_offset = 10
            return True
        return False

    def take_hit(self):
        self.hp_current -= 1
        if self.hp_current <= 0:
            self.dead = True
            return self.score
        return 0

    def draw(self, screen, image=None):
        if image:
            screen.blit(image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
            pygame.draw.rect(screen, COLORS["WHITE"], self.rect, 2, border_radius=8)
            eye_x = self.x + (10 if self.move_direction > 0 else self.w - 18)
            pygame.draw.circle(screen, COLORS["WHITE"], (eye_x, self.y + 15), 6)
            pygame.draw.circle(screen, COLORS["BLACK"], (eye_x, self.y + 15), 3)


class ShieldEnemy(Enemy):
    name = "Shield"
    type = "shield"
    hp = 3
    speed = 0.8
    score = 25
    color = COLORS["ORANGE"]
    size = 48
    damage = 1
    
    def __init__(self, x, y=0):
        super().__init__(x, y)
        self.shield_active = True
        self.shield_regen = 0

    def take_hit(self):
        if self.shield_active:
            self.shield_active = False
            self.shield_regen = 180
            return 0
        return super().take_hit()

    def update(self, ground_y=HEIGHT - 100):
        super().update(ground_y)
        if self.shield_regen > 0:
            self.shield_regen -= 1
            if self.shield_regen <= 0:
                self.shield_active = True

    def draw(self, screen, image=None):
        super().draw(screen, image)
        if self.shield_active:
            shield_rect = self.rect.inflate(12, 12)
            pygame.draw.rect(screen, COLORS["YELLOW"], shield_rect, 3, border_radius=10)


class FastEnemy(Enemy):
    name = "Fast"
    type = "fast"
    hp = 1
    speed = 2.5
    score = 15
    color = COLORS["GREEN"]
    size = 34
    damage = 1
    attack_cooldown_max = 45


class MageEnemy(Enemy):
    name = "Mage"
    type = "mage"
    hp = 2
    speed = 0.6
    score = 30
    color = COLORS["PURPLE"]
    size = 44
    damage = 1
    attack_range = 300
    shoot_cooldown_max = 90
    
    def __init__(self, x, y=0):
        super().__init__(x, y)
        self.shoot_timer = 0
        self.projectiles = []
        
    def can_shoot(self):
        return self.on_ground and self.shoot_timer <= 0
    
    def shoot(self, target_x, target_y):
        if self.can_shoot():
            self.shoot_timer = self.shoot_cooldown_max
            self.animation_offset = 12
            projectile = MageProjectile(
                self.x + self.w//2, 
                self.y + self.h//2, 
                target_x, 
                target_y
            )
            self.projectiles.append(projectile)
            return projectile
        return None
    
    def update(self, ground_y=HEIGHT - 100):
        super().update(ground_y)
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        
        for p in self.projectiles[:]:
            p.update()
            if p.dead:
                self.projectiles.remove(p)
    
    def get_projectiles(self):
        return self.projectiles
    
    def draw(self, screen, image=None):
        super().draw(screen, image)
        
        if self.shoot_timer > self.shoot_cooldown_max - 15:
            glow = pygame.Surface((self.w + 10, self.h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (150, 50, 255, 100), glow.get_rect(), border_radius=10)
            screen.blit(glow, (self.x - 5, self.y - 5))
        
        staff_x = self.x + self.w - 10 if self.move_direction > 0 else self.x + 5
        pygame.draw.line(screen, COLORS["GOLD"], (staff_x, self.y + 15), (staff_x, self.y + self.h - 15), 4)
        pygame.draw.circle(screen, COLORS["PURPLE"], (staff_x, self.y + 10), 8)
        pygame.draw.circle(screen, COLORS["WHITE"], (staff_x, self.y + 10), 4)
        
        for p in self.projectiles:
            p.draw(screen)


class HeavyEnemy(Enemy):
    name = "Heavy"
    type = "heavy"
    hp = 5
    speed = 0.4
    score = 40
    color = COLORS["BROWN"]
    size = 60
    damage = 2
    attack_cooldown_max = 90


class MageProjectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.w = 14
        self.h = 14
        self.speed = 6
        
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        else:
            self.vx = 0
            self.vy = self.speed
        
        self.damage = 1
        self.dead = False
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

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
            size = 8 - i
            if size > 0:
                color = (150 + i * 20, 50, 200 - i * 20)
                pygame.draw.circle(screen, color, (int(tx), int(ty)), size)
        
        pygame.draw.circle(screen, COLORS["PURPLE"], (int(self.x), int(self.y)), 7)
        pygame.draw.circle(screen, COLORS["MAGENTA"], (int(self.x), int(self.y)), 4)
        pygame.draw.circle(screen, COLORS["WHITE"], (int(self.x), int(self.y)), 2)
        glow_surf = pygame.Surface((26, 26), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (150, 50, 255, 80), (13, 13), 12, 2)
        screen.blit(glow_surf, (int(self.x) - 13, int(self.y) - 13))
