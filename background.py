# background.py
import pygame
import random
from config import WIDTH, HEIGHT, GROUND_Y, COLORS, IMG

class ParallaxBackground:
    def __init__(self):
        self.space_bg = self.load_space_background()
        self.stars = self.create_stars()
        self.planets = self.create_planets()
        self.nebula = self.create_nebula()
        self.camera_x = 0
        self.ground_surface = self.create_ground_surface()
        
    def load_space_background(self):
        try:
            space_img_path = IMG / "background.jpg"
            if space_img_path.exists():
                print("✅ Đã tải ảnh nền: background.jpg")
                img = pygame.image.load(str(space_img_path)).convert()
                img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                return img
        except Exception as e:
            print(f"⚠️ Không load được background.jpg: {e}")
        
        print("🎨 Tạo gradient nền thay thế...")
        surf = pygame.Surface((WIDTH, HEIGHT))
        for i in range(HEIGHT):
            t = i / HEIGHT
            r = int(10 + t * 20)
            g = int(5 + t * 10)
            b = int(30 + t * 40)
            pygame.draw.line(surf, (r, g, b), (0, i), (WIDTH, i))
        
        for _ in range(300):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            brightness = random.randint(150, 255)
            size = random.choice([1, 2])
            pygame.draw.circle(surf, (brightness, brightness, brightness), (x, y), size)
        
        return surf
    
    def create_stars(self):
        stars = []
        far_stars = []
        for _ in range(150):
            far_stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 2),
                'brightness': random.randint(100, 180)
            })
        stars.append({'stars': far_stars, 'speed': 0.1})
        
        near_stars = []
        for _ in range(100):
            near_stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(2, 3),
                'brightness': random.randint(180, 255)
            })
        stars.append({'stars': near_stars, 'speed': 0.3})
        
        self.shooting_stars = []
        return stars
    
    def create_planets(self):
        planets = []
        
        big_planet = pygame.Surface((180, 180), pygame.SRCALPHA)
        pygame.draw.circle(big_planet, (210, 150, 80), (90, 90), 80)
        pygame.draw.circle(big_planet, (180, 120, 60), (90, 90), 75)
        pygame.draw.ellipse(big_planet, (160, 130, 70), (30, 70, 120, 40), 8)
        planets.append({
            'surface': big_planet,
            'x': WIDTH + 50,
            'y': 50,
            'speed': 0.15
        })
        
        small_planet = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(small_planet, (100, 150, 200), (30, 30), 25)
        pygame.draw.circle(small_planet, (70, 120, 170), (30, 30), 22)
        planets.append({
            'surface': small_planet,
            'x': -100,
            'y': 150,
            'speed': 0.20
        })
        
        moon = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(moon, (180, 180, 170), (20, 20), 18)
        pygame.draw.circle(moon, (150, 150, 140), (20, 20), 15)
        pygame.draw.circle(moon, (120, 120, 110), (12, 15), 4)
        pygame.draw.circle(moon, (120, 120, 110), (25, 25), 3)
        planets.append({
            'surface': moon,
            'x': WIDTH // 3,
            'y': 80,
            'speed': 0.25
        })
        
        return planets
    
    def create_nebula(self):
        nebula = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        colors = [(80, 40, 120), (60, 30, 100), (100, 50, 140)]
        for _ in range(8):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT // 2)
            radius = random.randint(100, 250)
            color = random.choice(colors)
            
            for i in range(radius, 0, -20):
                alpha = int(30 * (i / radius))
                temp_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (radius, radius), i)
                nebula.blit(temp_surf, (x - radius, y - radius))
        
        return nebula
    
    def create_ground_surface(self):
        ground_surf = pygame.Surface((WIDTH, HEIGHT - GROUND_Y + 20), pygame.SRCALPHA)
        ground_rect = pygame.Rect(0, 0, WIDTH, HEIGHT - GROUND_Y + 20)
        
        pygame.draw.rect(ground_surf, (30, 25, 45), ground_rect)
        
        surface_height = 12
        pygame.draw.rect(ground_surf, (50, 45, 70), (0, 0, WIDTH, surface_height))
        
        for i in range(0, WIDTH, 25):
            if random.random() < 0.2:
                x = i + random.randint(-8, 8)
                crystal_height = random.randint(8, 18)
                color = random.choice([(100, 150, 255), (150, 100, 255), (100, 255, 150)])
                points = [(x, surface_height), 
                         (x - 4, surface_height - crystal_height // 2),
                         (x, surface_height - crystal_height),
                         (x + 4, surface_height - crystal_height // 2)]
                pygame.draw.polygon(ground_surf, color, points)
        
        return ground_surf
    
    def add_shooting_star(self):
        if random.random() < 0.005:
            self.shooting_stars.append({
                'x': random.randint(0, WIDTH // 2),
                'y': random.randint(0, HEIGHT // 3),
                'vx': random.uniform(8, 15),
                'vy': random.uniform(3, 8),
                'length': random.randint(30, 60),
                'life': 60
            })
    
    def update_shooting_stars(self):
        for star in self.shooting_stars[:]:
            star['x'] += star['vx']
            star['y'] += star['vy']
            star['life'] -= 1
            if star['life'] <= 0 or star['x'] > WIDTH + 100 or star['y'] > HEIGHT + 100:
                self.shooting_stars.remove(star)
    
    def update(self, player_x):
        target_x = player_x - WIDTH // 3
        target_x = max(0, min(target_x, 1000))
        self.camera_x = self.camera_x * 0.9 + target_x * 0.1
        self.update_shooting_stars()
        self.add_shooting_star()
    
    def draw_stars(self, screen, offset_x=0):
        for layer in self.stars:
            speed = layer['speed']
            layer_offset = offset_x * speed
            for star in layer['stars']:
                x = star['x'] - layer_offset
                if x < -50:
                    x += WIDTH + 100
                elif x > WIDTH + 50:
                    x -= WIDTH + 100
                if -50 <= x <= WIDTH + 50:
                    brightness = star['brightness']
                    color = (brightness, brightness, brightness)
                    pygame.draw.circle(screen, color, (int(x), star['y']), star['size'])
    
    def draw_planets(self, screen, offset_x=0):
        for planet in self.planets:
            x = planet['x'] - offset_x * planet['speed']
            if x < -planet['surface'].get_width() - 50:
                x += WIDTH + planet['surface'].get_width() + 100
            elif x > WIDTH + 50:
                x -= WIDTH + planet['surface'].get_width() + 100
            screen.blit(planet['surface'], (int(x), planet['y']))
    
    def draw_shooting_stars(self, screen):
        """Vẽ sao băng - ĐÃ SỬA LỖI"""
        try:
            for star in self.shooting_stars[:]:
                # Tránh lỗi chia cho 0
                if star['vx'] == 0:
                    continue
                    
                for i in range(star['length'], 0, -10):
                    width = max(1, 4 - i // 15)
                    try:
                        start = (int(star['x'] - i), int(star['y'] - i * (star['vy'] / star['vx'])))
                        end = (int(star['x'] - (i - 5)), int(star['y'] - (i - 5) * (star['vy'] / star['vx'])))
                        brightness = 200 + int(55 * (i / star['length']))
                        color = (brightness, brightness, 150)
                        pygame.draw.line(screen, color, start, end, width)
                    except (OverflowError, ValueError, ZeroDivisionError):
                        continue
                        
                try:
                    pygame.draw.circle(screen, (255, 255, 200), (int(star['x']), int(star['y'])), 3)
                except:
                    continue
        except Exception as e:
            # Bỏ qua lỗi vẽ sao băng, không crash game
            pass
    
    def draw(self, screen, player_x=None):
        if player_x:
            self.update(player_x)
        screen.blit(self.space_bg, (0, 0))
        screen.blit(self.nebula, (0, 0))
        self.draw_stars(screen, self.camera_x)
        self.draw_planets(screen, self.camera_x)
        self.draw_shooting_stars(screen)
        screen.blit(self.ground_surface, (0, GROUND_Y))
        
        # Vẽ viền sáng cho mặt đất
        for i in range(3):
            glow_color = (80 + i * 20, 70 + i * 15, 120 + i * 20)
            pygame.draw.line(screen, glow_color, (0, GROUND_Y - i), (WIDTH, GROUND_Y - i), 1)
        pygame.draw.line(screen, (100, 150, 255), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)