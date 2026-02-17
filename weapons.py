import pygame
import math
from config import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage, lifetime=100, color=BULLET_COLOR):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.damage = damage
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.lifetime = lifetime

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class Weapon:
    def __init__(self, name, cooldown, damage, speed, spread=0, bullet_count=1):
        self.name = name
        self.cooldown = cooldown
        self.damage = damage
        self.speed = speed
        self.spread = spread
        self.bullet_count = bullet_count
        self.current_cooldown = 0

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def shoot(self, x, y, angle):
        if self.current_cooldown <= 0:
            self.current_cooldown = self.cooldown
            bullets = []
            start_angle = angle - (self.spread / 2)
            step = self.spread / (self.bullet_count - 1) if self.bullet_count > 1 else 0
            
            for i in range(self.bullet_count):
                current_angle = start_angle + (step * i) if self.bullet_count > 1 else angle
                # Add slight random variation
                import random
                current_angle += random.uniform(-0.05, 0.05)
                
                b = Bullet(x, y, current_angle, self.speed, self.damage)
                bullets.append(b)
            return bullets
        return []

class Sword(Weapon):
    def __init__(self):
        super().__init__(WEAPON_SWORD, cooldown=SWORD_COOLDOWN, damage=SWORD_DAMAGE, speed=0)
        self.attack_range = SWORD_RANGE

    def shoot(self, x, y, angle):
        if self.current_cooldown <= 0:
            self.current_cooldown = self.cooldown
            # Sword creates a "slash" projectile that doesn't move far but hits area
            # For simplicity, we can make it a short-lived projectile or handle it differently
            # Let's make it a short-lived, large invisible bullet that acts as the slash
            
            slash = Bullet(x, y, angle, speed=5, damage=self.damage, lifetime=5, color=SWORD_COLOR)
            # Make slash bigger
            slash.image = pygame.Surface((32, 32))
            slash.image.fill(SWORD_COLOR)
            slash.rect = slash.image.get_rect()
            slash.rect.center = (x + math.cos(angle)*20, y + math.sin(angle)*20)
            return [slash]
        return []

class Pistol(Weapon):
    def __init__(self):
        super().__init__(WEAPON_PISTOL, cooldown=20, damage=10, speed=12)

class Shotgun(Weapon):
    def __init__(self):
        super().__init__(WEAPON_SHOTGUN, cooldown=45, damage=8, speed=10, spread=0.5, bullet_count=5)

class MachineGun(Weapon):
    def __init__(self):
        super().__init__(WEAPON_MACHINEGUN, cooldown=5, damage=5, speed=15, spread=0.1, bullet_count=1)
