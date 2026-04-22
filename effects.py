import pygame
import random
import math
from config import COLORS, WIDTH, HEIGHT

class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        
    def shake(self, duration=10, intensity=5):
        self.duration = duration
        self.intensity = intensity
        
    def apply(self):
        if self.duration > 0:
            self.duration -= 1
            offset_x = random.randint(-self.intensity, self.intensity)
            offset_y = random.randint(-self.intensity, self.intensity)
            return offset_x, offset_y
        return 0, 0


class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_hit_particles(self, x, y, color=None):
        if color is None:
            color = COLORS["RED"]
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2
            self.particles.append(Particle(x, y, color, (vx, vy), 20))
            
    def add_explosion_particles(self, x, y):
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([COLORS["RED"], COLORS["ORANGE"], COLORS["YELLOW"]])
            self.particles.append(Particle(x, y, color, (vx, vy), 30))
            
    def add_dust_particles(self, x, y):
        for _ in range(5):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-2, -5)
            self.particles.append(Particle(x, y, COLORS["GRAY"], (vx, vy), 15))
            
    def update(self):
        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)
                
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.age = 0
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.vx *= 0.98
        self.age += 1
        return self.age < self.lifetime
        
    def draw(self, screen):
        color = self.color
        if self.age > self.lifetime // 2:
            factor = 1 - (self.age - self.lifetime//2) / (self.lifetime//2)
            color = tuple(int(c * factor) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class FloatingText:
    def __init__(self, x, y, text, color=None, duration=30):
        self.x = x
        self.y = y
        self.text = text
        self.color = color or COLORS["WHITE"]
        self.duration = duration
        self.age = 0
        
    def update(self):
        self.y -= 1.5
        self.age += 1
        return self.age < self.duration
        
    def draw(self, screen, font):
        color = self.color
        surf = font.render(self.text, True, color)
        screen.blit(surf, (self.x - surf.get_width()//2, self.y))