# door.py
import pygame
from config import WIDTH, HEIGHT, COLORS

class Door:
    def __init__(self, x, y, door_type="to_boss", target_level=None):
        """
        door_type: "to_boss" hoặc "to_next_level"
        target_level: nếu to_next_level thì chuyển sang level này
        """
        self.x = x
        self.y = y
        self.w = 64
        self.h = 96
        self.door_type = door_type
        self.target_level = target_level
        self.active = True
        self.animation_frame = 0
        
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def update(self):
        self.animation_frame += 1
        
    def draw(self, screen):
        # Vẽ cánh cửa
        # Khung
        pygame.draw.rect(screen, (100, 70, 40), self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS["GOLD"], self.rect, 3, border_radius=8)
        
        # Tay nắm
        knob_x = self.x + self.w - 15
        knob_y = self.y + self.h // 2
        pygame.draw.circle(screen, COLORS["YELLOW"], (knob_x, knob_y), 6)
        
        # Hiệu ứng ánh sáng
        glow = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
        alpha = 80 + int(40 * (self.animation_frame % 30 / 30))
        pygame.draw.rect(glow, (255, 215, 0, alpha), (10, 10, self.w, self.h), 4, border_radius=12)
        screen.blit(glow, (self.x - 10, self.y - 10))
        
        # Văn bản
        font = pygame.font.SysFont("Arial", 16, bold=True)
        if self.door_type == "to_boss":
            text = font.render("➡️ BOSS", True, COLORS["WHITE"])
        else:
            text = font.render("➡️ NEXT", True, COLORS["WHITE"])
        screen.blit(text, (self.x + self.w//2 - text.get_width()//2, self.y - 20))