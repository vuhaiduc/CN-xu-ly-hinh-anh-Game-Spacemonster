# create_images.py
import pygame
import os

pygame.init()

# Tạo thư mục
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

def create_image(name, size, color, text=""):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    pygame.draw.rect(surf, (255,255,255), surf.get_rect(), 3, border_radius=10)
    
    # Vẽ mắt
    if not text:
        pygame.draw.circle(surf, (255,255,255), (size[0]//3, size[1]//3), size[0]//8)
        pygame.draw.circle(surf, (0,0,0), (size[0]//3, size[1]//3), size[0]//16)
        pygame.draw.circle(surf, (255,255,255), (2*size[0]//3, size[1]//3), size[0]//8)
        pygame.draw.circle(surf, (0,0,0), (2*size[0]//3, size[1]//3), size[0]//16)
    
    if text:
        font = pygame.font.SysFont("Arial", size[0]//3, bold=True)
        text_surf = font.render(text, True, (255,255,255))
        text_rect = text_surf.get_rect(center=(size[0]//2, size[1]//2))
        surf.blit(text_surf, text_rect)
    
    pygame.image.save(surf, f"assets/images/{name}")
    print(f"Created: {name}")

# Tạo các ảnh cần thiết
print("Creating images...")
create_image("player.png", (52, 52), (50, 100, 200), "P")
create_image("enemy_basic.png", (42, 42), (200, 50, 50), "E")
create_image("enemy_tank.png", (48, 48), (255, 100, 0), "S")
create_image("enemy_fast.png", (34, 34), (50, 200, 50), "F")
create_image("enemy_mage.png", (44, 44), (150, 50, 200), "M")
create_image("enemy_heavy.png", (60, 60), (139, 69, 19), "H")
create_image("boss_phase1.png", (160, 130), (0, 200, 200), "B1")
create_image("boss_phase2.png", (160, 130), (255, 150, 50), "B2")
create_image("boss_phase3.png", (160, 130), (50, 150, 255), "B3")
create_image("boss_phase4.png", (160, 130), (150, 50, 255), "B4")
create_image("boss_phase5.png", (160, 130), (255, 50, 50), "B5")
create_image("background.png", (1280, 720), (10, 5, 30), "")

print("\n✅ All images created successfully!")
print("Now run: python main.py")