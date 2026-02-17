import pygame
import math
from config import *
from weapons import Pistol, Shotgun, MachineGun, Bullet, Sword, Weapon
from assets import SpriteFactory

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, hp=None, weapon_idx=0):
        super().__init__()
        self.image = SpriteFactory.create_player_sprite()
        self.original_image = self.image # Keep original for rotation if needed
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED
        self.hp = hp if hp is not None else PLAYER_START_HP
        self.weapon_list = [Sword(), Pistol(), Shotgun(), MachineGun()]
        self.current_weapon_idx = weapon_idx
        self.weapon = self.weapon_list[self.current_weapon_idx]
        
        # Skill (Dash)
        self.skill_cooldown = 0
        self.dash_timer = 0
        self.dash_direction = (0, 0)

    def switch_weapon(self):
        self.current_weapon_idx = (self.current_weapon_idx + 1) % len(self.weapon_list)
        self.weapon = self.weapon_list[self.current_weapon_idx]

    def use_skill(self, direction_override=None):
        if self.skill_cooldown <= 0 and self.dash_timer <= 0:
            self.skill_cooldown = SKILL_DASH_COOLDOWN
            self.dash_timer = SKILL_DASH_DURATION
            
            # Use override if provided (for joystick)
            if direction_override and (direction_override[0] != 0 or direction_override[1] != 0):
                self.dash_direction = direction_override
                return

            # Determine dash direction
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_w]: dy = -1
            if keys[pygame.K_s]: dy = 1
            if keys[pygame.K_a]: dx = -1
            if keys[pygame.K_d]: dx = 1
            
            # If no key pressed, dash towards mouse
            if dx == 0 and dy == 0:
                mx, my = pygame.mouse.get_pos()
                px, py = self.rect.center
                # Need camera offset here really, but let's approximate or just dash forward
                # Without camera info inside Player, mouse pos is screen relative.
                # Assuming Player is centered on screen usually?
                # Let's just dash in facing direction if we had one, or default right.
                dx = 1
            
            # Normalize
            length = math.sqrt(dx*dx + dy*dy)
            if length != 0:
                self.dash_direction = (dx/length, dy/length)
            else:
                self.dash_direction = (1, 0) # Default right

    def update(self, walls, move_vec=None, aim_vec=None):
        # Update Cooldowns
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1
        
        # Weapon Update
        self.weapon.update()

        # Dashing State
        if self.dash_timer > 0:
            self.dash_timer -= 1
            # Dash Movement (Ignore collision? Or just fast?)
            # Let's move fast but still collide
            speed = SKILL_DASH_SPEED
            self.rect.x += self.dash_direction[0] * speed
            self.collide(walls, 'x')
            self.rect.y += self.dash_direction[1] * speed
            self.collide(walls, 'y')
            return # Skip normal movement

        # Normal Movement
        dx = 0
        dy = 0
        
        if move_vec:
            # Joystick input
            dx = move_vec[0]
            dy = move_vec[1]
            # If magnitude > 1 (shouldn't be with joystick normalization, but safety)
            # Joystick gives dx, dy proportional to tilt.
            # We multiply by speed.
            dx *= self.speed
            dy *= self.speed
        else:
            # Keyboard input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: dy = -1
            if keys[pygame.K_s]: dy = 1
            if keys[pygame.K_a]: dx = -1
            if keys[pygame.K_d]: dx = 1
                
            # Normalize diagonal movement
            if dx != 0 or dy != 0:
                length = math.sqrt(dx*dx + dy*dy)
                dx = dx / length * self.speed
                dy = dy / length * self.speed
            
        # Move X and check collision
        self.rect.x += dx
        self.collide(walls, 'x')
        
        # Move Y and check collision
        self.rect.y += dy
        self.collide(walls, 'y')
        
        # Boundary Check (Map limits)
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > MAP_WIDTH * TILE_SIZE: self.rect.right = MAP_WIDTH * TILE_SIZE
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > MAP_HEIGHT * TILE_SIZE: self.rect.bottom = MAP_HEIGHT * TILE_SIZE

    def collide(self, walls, direction):
        hits = pygame.sprite.spritecollide(self, walls, False)
        if hits:
            if direction == 'x':
                if self.rect.centerx < hits[0].rect.centerx: # Moving right
                    self.rect.right = hits[0].rect.left
                else: # Moving left
                    self.rect.left = hits[0].rect.right
            if direction == 'y':
                if self.rect.centery < hits[0].rect.centery: # Moving down
                    self.rect.bottom = hits[0].rect.top
                else: # Moving up
                    self.rect.top = hits[0].rect.bottom

    def shoot(self):
        # Calculate direction towards mouse
        mx, my = pygame.mouse.get_pos()
        # Adjust for camera offset (will need to implement camera later, but for now assuming direct mapping)
        # Wait, if we implement camera, mouse position needs adjustment. 
        # For now, let's assume no camera or pass camera offset.
        # But wait, Dungeon is big (50x50 tiles), screen is small. We need a Camera!
        # I'll implement a simple camera in Game class and pass offset here?
        # No, better to pass target position to shoot() from Game class.
        pass

    def shoot_at(self, target_pos):
        # target_pos is (x, y) relative to screen or world?
        # In handle_input, we calculated it relative to camera top-left, so it's world coordinates relative to (0,0) of screen?
        # Actually handle_input passed (mx - cx, my - cy).
        # cx, cy are usually negative (camera position).
        # So target_pos is world coordinates.
        
        tx, ty = target_pos
        px, py = self.rect.center
        angle = math.atan2(ty - py, tx - px)
        
        return self.weapon.shoot(self.rect.centerx, self.rect.centery, angle)

    def shoot_dir(self, aim_vec):
        if aim_vec[0] == 0 and aim_vec[1] == 0:
            return []
        
        angle = math.atan2(aim_vec[1], aim_vec[0])
        return self.weapon.shoot(self.rect.centerx, self.rect.centery, angle)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((ENEMY_BULLET_SIZE, ENEMY_BULLET_SIZE))
        self.image.fill(ENEMY_BULLET_COLOR)
        # Make it circular
        pygame.draw.circle(self.image, ENEMY_BULLET_COLOR, (ENEMY_BULLET_SIZE//2, ENEMY_BULLET_SIZE//2), ENEMY_BULLET_SIZE//2)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = ENEMY_BULLET_SPEED
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Kill if off screen/map limits (simplified)
        # Actually better to let Game class handle wall collisions or just lifetime
        pass

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, hp_multiplier=1.0, enemy_type=ENEMY_MELEE):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = SpriteFactory.create_enemy_sprite(enemy_type, hp_multiplier)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.target = target
        
        # Stats based on type
        if enemy_type == ENEMY_MELEE:
            self.speed = MELEE_SPEED
            self.hp = MELEE_HP_BASE * hp_multiplier
            self.attack_cooldown = 0
        elif enemy_type == ENEMY_RANGED:
            self.speed = RANGED_SPEED
            self.hp = RANGED_HP_BASE * hp_multiplier
            self.attack_cooldown = RANGED_COOLDOWN
            self.attack_range = RANGED_ATTACK_RANGE
        elif enemy_type == ENEMY_DASHER:
            self.speed = DASHER_SPEED
            self.hp = DASHER_HP_BASE * hp_multiplier
            self.attack_cooldown = 0
        elif enemy_type == ENEMY_BOMBER:
            self.speed = BOMBER_SPEED
            self.hp = BOMBER_HP_BASE * hp_multiplier
            self.attack_cooldown = 0
            self.explode_range = BOMBER_EXPLODE_RANGE

    def update(self, walls):
        px, py = self.target.rect.center
        ex, ey = self.rect.center
        dist = math.sqrt((px - ex)**2 + (py - ey)**2)
        angle = math.atan2(py - ey, px - ex)

        if self.enemy_type == ENEMY_MELEE or self.enemy_type == ENEMY_DASHER:
            # Simple chase
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.move(dx, dy, walls)
            
        elif self.enemy_type == ENEMY_BOMBER:
             # Chase until close, then explode (handled in Game logic ideally, or here)
             # Let's just chase here, Game class will check distance for explosion damage
             dx = math.cos(angle) * self.speed
             dy = math.sin(angle) * self.speed
             self.move(dx, dy, walls)
             
        elif self.enemy_type == ENEMY_RANGED:
            # Maintain distance
            if dist > self.attack_range:
                # Move closer
                dx = math.cos(angle) * self.speed
                dy = math.sin(angle) * self.speed
                self.move(dx, dy, walls)
            elif dist < self.attack_range - 50:
                # Move away if too close (kiting)
                dx = -math.cos(angle) * self.speed
                dy = -math.sin(angle) * self.speed
                self.move(dx, dy, walls)
            
            # Update cooldown
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
    
    def move(self, dx, dy, walls):
        self.rect.x += dx
        self.collide(walls, 'x')
        self.rect.y += dy
        self.collide(walls, 'y')

    def collide(self, walls, direction):
        hits = pygame.sprite.spritecollide(self, walls, False)
        if hits:
            if direction == 'x':
                if self.rect.centerx < hits[0].rect.centerx: # Moving right
                    self.rect.right = hits[0].rect.left
                else: # Moving left
                    self.rect.left = hits[0].rect.right
            if direction == 'y':
                if self.rect.centery < hits[0].rect.centery: # Moving down
                    self.rect.bottom = hits[0].rect.top
                else: # Moving up
                    self.rect.top = hits[0].rect.bottom

    def shoot(self):
        if self.enemy_type == ENEMY_RANGED and self.attack_cooldown <= 0:
            self.attack_cooldown = RANGED_COOLDOWN
            # Aim at player
            px, py = self.target.rect.center
            ex, ey = self.rect.center
            angle = math.atan2(py - ey, px - ex)
            return EnemyBullet(ex, ey, angle)
        return None

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteFactory.create_portal_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
