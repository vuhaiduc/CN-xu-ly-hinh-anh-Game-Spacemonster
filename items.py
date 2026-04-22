# items.py
import pygame
import random
from config import WIDTH, HEIGHT, GROUND_Y, COLORS


class Item:
    """Vật phẩm rơi xuống"""
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.w = 28
        self.h = 28
        self.item_type = item_type  # 'health', 'shield', 'ammo'
        self.speed_y = 2.5
        self.dead = False
        self.lifetime = 300
        self.age = 0
        
        self.colors = {
            'health': COLORS["GREEN"],
            'shield': COLORS["CYAN"],
            'ammo': COLORS["YELLOW"]
        }
        
        self.icons = {
            'health': '❤️',
            'shield': '🛡️',
            'ammo': '🔫'
        }
        
        self.float_offset = 0
        self.float_speed = 0.1
        
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def update(self):
        self.y += self.speed_y
        self.age += 1
        self.float_offset += self.float_speed
        
        if self.age >= self.lifetime or self.y > GROUND_Y + 100:
            self.dead = True
    
    def draw(self, screen):
        color = self.colors.get(self.item_type, COLORS["WHITE"])
        float_y = self.y + int(3 * abs(pygame.time.get_ticks() / 200 % 2 - 1))
        
        shadow_rect = pygame.Rect(self.x + 4, self.y + self.h - 4, self.w - 8, 6)
        pygame.draw.ellipse(screen, (20, 20, 20), shadow_rect)
        
        glow = pygame.Surface((self.w + 12, self.h + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color[:3], 60), glow.get_rect(), border_radius=10)
        screen.blit(glow, (self.x - 6, float_y - 6))
        
        pygame.draw.rect(screen, color, (self.x, float_y, self.w, self.h), border_radius=8)
        pygame.draw.rect(screen, COLORS["WHITE"], (self.x, float_y, self.w, self.h), 2, border_radius=8)
        
        font = pygame.font.SysFont("Segoe UI Emoji", 20)
        icon_surf = font.render(self.icons[self.item_type], True, COLORS["WHITE"])
        screen.blit(icon_surf, (self.x + self.w//2 - 10, float_y + self.h//2 - 10))
    
    def collect(self, player):
        """Xử lý khi nhặt vật phẩm"""
        if self.item_type == 'health':
            if player.hp < player.max_hp:
                player.hp = min(player.max_hp, player.hp + 1)
                return "❤️ +1 HP!", "heal"
            return None, None
        elif self.item_type == 'shield':
            player.activate_shield(240)
            return "🛡️ KHIÊN KÍCH HOẠT! (4s)", "shield"
        elif self.item_type == 'ammo':
            # ĐẠN VĨNH VIỄN - không bao giờ hết
            player.activate_permanent_infinite_ammo()
            return "🔫 ĐẠN VĨNH VIỄN! BẮN THOẢI MÁI! 🔫", "ammo"
        
        return None, None


class ItemSpawner:
    def __init__(self):
        self.items = []
        self.spawn_timer = 0
        self.spawn_delay = 180
        
    def update(self):
        self.spawn_timer -= 1
        
        for item in self.items[:]:
            item.update()
            if item.dead:
                self.items.remove(item)
    
    def try_spawn(self, x=None, y=None):
        if self.spawn_timer <= 0:
            if x is None:
                x = random.randint(50, WIDTH - 50)
            if y is None:
                y = random.randint(50, GROUND_Y - 100)
            
            # Giới hạn vị trí spawn trong màn hình
            x = max(20, min(WIDTH - 50, x))
            y = max(20, min(GROUND_Y - 50, y))
            
            rand = random.random()
            if rand < 0.4:
                item_type = 'health'
            elif rand < 0.7:
                item_type = 'shield'
            else:
                item_type = 'ammo'
            
            self.items.append(Item(x, y, item_type))
            self.spawn_timer = self.spawn_delay
            return True
        return False
    
    def spawn_from_enemy(self, x, y):
        if random.random() < 0.4:
            # Giới hạn vị trí spawn trong màn hình
            spawn_x = max(20, min(WIDTH - 50, x))
            spawn_y = max(20, min(GROUND_Y - 50, y))
            
            rand = random.random()
            if rand < 0.4:
                item_type = 'health'
            elif rand < 0.7:
                item_type = 'shield'
            else:
                item_type = 'ammo'
            self.items.append(Item(spawn_x, spawn_y, item_type))
    
    def draw(self, screen):
        for item in self.items:
            item.draw(screen)
    
    def check_collisions(self, player):
        results = []
        for item in self.items[:]:
            if player.rect.colliderect(item.rect):
                msg, sound = item.collect(player)
                if msg:
                    results.append((msg, sound))
                self.items.remove(item)
        return results
    
    def clear(self):
        self.items.clear()