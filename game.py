import pygame
import random
from config import *
from entities import Player, Enemy, Portal
from weapons import Bullet
from dungeon import DungeonGenerator, Wall
from localization import get_text, TEXTS
from ui_touch import VirtualJoystick, TouchButton

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - SCREEN_WIDTH), x)  # right
        y = max(-(self.height - SCREEN_HEIGHT), y)  # bottom

        self.camera = pygame.Rect(x, y, self.width, self.height)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU" # MENU, PLAYING, GAMEOVER, TUTORIAL
        self.lang = "en"
        
        # Tutorial Variables
        self.tutorial_step = 0
        self.tutorial_timer = 0
        
        # Fonts
        self.load_fonts()
        
        # Touch Controls
        self.touch_active = True # Default enabled for testing
        self.joystick_left = VirtualJoystick(100, SCREEN_HEIGHT - 100, 60, 30)
        self.joystick_right = VirtualJoystick(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100, 60, 30)
        
        # Skill Button
        self.btn_skill = TouchButton(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 60, 40, "D", CYAN, self.on_touch_skill)
        # Switch Weapon Button
        self.btn_switch = TouchButton(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 160, 40, "W", ORANGE, self.on_touch_switch)

        self.load_data()
        self.start_game() # Initializes level 1

    def on_touch_skill(self):
        if self.player: self.player.use_skill()

    def on_touch_switch(self):
        if self.player: self.player.switch_weapon()

    def load_fonts(self):
        # Use system font for Chinese support
        # "simhei" is common on Windows for Simplified Chinese
        # "arial" or "microsoftyahei" might also work
        try:
            self.font_large = pygame.font.SysFont("simhei", FONT_SIZE_LARGE)
            self.font_medium = pygame.font.SysFont("simhei", FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.SysFont("simhei", FONT_SIZE_SMALL)
        except:
            # Fallback
            self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

    def load_data(self):
        # Placeholder for loading assets
        pass

    def start_game(self):
        self.level = 1
        self.difficulty_multiplier = 1.0
        self.score = 0
        self.player = None # Will be created in new_level
        self.current_theme = THEMES[0]
        self.new_level()

    def start_tutorial(self):
        self.state = "TUTORIAL"
        self.tutorial_step = 1
        self.tutorial_timer = 0
        self.new_level(is_tutorial=True)
        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
    def new_level(self, is_tutorial=False):
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()
        
        if is_tutorial:
            # Create a simple box room for tutorial
            self.walls.add(Wall(0, 0)) # Placeholder
            # Build a simple 20x15 room
            for x in range(20):
                self.walls.add(Wall(x, 0))
                self.walls.add(Wall(x, 14))
            for y in range(15):
                self.walls.add(Wall(0, y))
                self.walls.add(Wall(19, y))
            
            self.all_sprites.add(self.walls)
            
            # Player Spawn
            self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.all_sprites.add(self.player)
            
            # Camera centered
            self.camera = Camera(20 * TILE_SIZE, 15 * TILE_SIZE)
            
            # Dummy Enemy for later steps
            self.dummy_enemy = None
            
            return

        # Dungeon Generation
        self.dungeon_gen = DungeonGenerator()
        grid, rooms = self.dungeon_gen.generate()
        self.walls = self.dungeon_gen.build_walls(self.current_theme["wall"])
        self.all_sprites.add(self.walls)
        
        # Player Spawn (Center of first room)
        start_room = rooms[0]
        player_x = start_room.center[0] * TILE_SIZE
        player_y = start_room.center[1] * TILE_SIZE
        
        if self.player is None:
            self.player = Player(player_x, player_y)
        else:
            # Preserve stats but reset position
            self.player.rect.center = (player_x, player_y)
            # Add back to group
            
        self.all_sprites.add(self.player)
        
        # Portal Spawn (Center of last room)
        end_room = rooms[-1]
        portal = Portal(end_room.center[0] * TILE_SIZE, end_room.center[1] * TILE_SIZE)
        self.all_sprites.add(portal)
        self.portals.add(portal)
        
        # Camera
        self.camera = Camera(MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)
        
        # Spawning
        self.spawn_timer = 0
        
        # Initial enemies spawn (populate rooms)
        # Skip the start room (rooms[0]) to give player a safe start
        for i in range(1, len(rooms)):
            room = rooms[i]
            # Number of enemies per room scales with level
            num_enemies = random.randint(1, 2 + int(self.level * 0.5))
            for _ in range(num_enemies):
                self.spawn_enemy_in_room(room)

    def spawn_enemy_in_room(self, room):
        # Pick random spot in room
        x = random.randint(room.rect.x + 1, room.rect.x + room.rect.w - 2) * TILE_SIZE
        y = random.randint(room.rect.y + 1, room.rect.y + room.rect.h - 2) * TILE_SIZE
        
        # Don't spawn too close to player (just in case)
        dist = ((x - self.player.rect.centerx)**2 + (y - self.player.rect.centery)**2)**0.5
        if dist < 300: # Safe distance
            return

        # Randomly choose type based on level
        r = random.random()
        enemy_type = ENEMY_MELEE
        
        # Level 1: Mostly Melee, rare Ranged
        # Level 3+: Introduce Dasher
        # Level 5+: Introduce Bomber
        
        if self.level >= 5:
            if r < 0.2: enemy_type = ENEMY_BOMBER
            elif r < 0.4: enemy_type = ENEMY_DASHER
            elif r < 0.6: enemy_type = ENEMY_RANGED
        elif self.level >= 3:
            if r < 0.2: enemy_type = ENEMY_DASHER
            elif r < 0.4: enemy_type = ENEMY_RANGED
        else:
            if r < 0.2: enemy_type = ENEMY_RANGED

        enemy = Enemy(x, y, self.player, self.difficulty_multiplier, enemy_type)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def handle_input(self, event):
        # Handle Touch Input
        if self.touch_active:
            if self.joystick_left.handle_event(event): return
            if self.joystick_right.handle_event(event): return
            if self.btn_skill.handle_event(event): return
            if self.btn_switch.handle_event(event): return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "PLAYING" or self.state == "TUTORIAL":
                    self.state = "MENU"
                elif self.state == "MENU":
                    self.running = False
            
            if self.state == "MENU":
                if event.key == pygame.K_RETURN:
                    self.state = "PLAYING"
                if event.key == pygame.K_t:
                    self.start_tutorial()
                if event.key == pygame.K_l:
                    self.lang = "zh" if self.lang == "en" else "en"
                if event.key == pygame.K_r:
                    self.start_game()
                    self.state = "PLAYING"

            if self.state == "GAMEOVER":
                if event.key == pygame.K_r:
                    self.start_game()
                    self.state = "PLAYING"
            
            if self.state == "PLAYING" or self.state == "TUTORIAL":
                if event.key == pygame.K_q:
                    self.player.switch_weapon()
                    if self.state == "TUTORIAL" and self.tutorial_step == 3:
                        self.tutorial_step = 4
                        self.tutorial_timer = 0
                if event.key == pygame.K_SPACE:
                    self.player.use_skill()
                    if self.state == "TUTORIAL" and self.tutorial_step == 4:
                        self.tutorial_step = 5
                        self.tutorial_timer = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "PLAYING" or self.state == "TUTORIAL":
                if event.button == 1:  # Left click
                    # Adjust mouse position for camera
                    mx, my = pygame.mouse.get_pos()
                    cx, cy = self.camera.camera.topleft
                    target_pos = (mx - cx, my - cy)
                    
                    bullets = self.player.shoot_at(target_pos)
                    if bullets:
                        for b in bullets:
                            self.all_sprites.add(b)
                            self.bullets.add(b)
                        
                        if self.state == "TUTORIAL" and self.tutorial_step == 2:
                            self.tutorial_step = 3
                            self.tutorial_timer = 0

    def update(self):
        if self.state == "TUTORIAL":
            # Simple update for tutorial
            self.camera.update(self.player)
            
            # Input from Joystick (Tutorial)
            if self.touch_active:
                move_vec = self.joystick_left.value
                aim_vec = self.joystick_right.value
                self.player.update(self.walls, move_vec, aim_vec)
                
                # Check for shooting
                if self.joystick_right.active and (abs(aim_vec[0]) > 0.1 or abs(aim_vec[1]) > 0.1):
                    # Auto shoot when aiming
                    bullets = self.player.shoot_dir(aim_vec)
                    if bullets:
                        for b in bullets:
                            self.all_sprites.add(b)
                            self.bullets.add(b)
                        if self.tutorial_step == 2:
                            self.tutorial_step = 3
                            self.tutorial_timer = 0
            else:
                self.player.update(self.walls)
                
            self.bullets.update()
            self.enemy_bullets.update()
            if self.dummy_enemy:
                self.dummy_enemy.update(self.walls)
            
            # Tutorial Logic
            self.tutorial_timer += 1
            
            # Step 1: Move
            if self.tutorial_step == 1:
                keys = pygame.key.get_pressed()
                moved = False
                if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
                    moved = True
                if self.touch_active and (abs(self.joystick_left.value[0]) > 0.1 or abs(self.joystick_left.value[1]) > 0.1):
                    moved = True
                
                if moved:
                    if self.tutorial_timer > 60:
                        self.tutorial_step = 2
                        self.tutorial_timer = 0
            
            # Step 2: Shoot (Handled in handle_input)
            
            # Step 3: Switch Weapon (Handled in handle_input)
            
            # Step 4: Skill (Handled in handle_input)
            
            # Step 5: Kill Dummy
            if self.tutorial_step == 5:
                if not self.dummy_enemy:
                    # Spawn dummy
                    self.dummy_enemy = Enemy(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2, self.player, enemy_type=ENEMY_MELEE)
                    self.dummy_enemy.speed = 0 # Stationary
                    self.all_sprites.add(self.dummy_enemy)
                    self.enemies.add(self.dummy_enemy)
                
                # Check collision
                pygame.sprite.groupcollide(self.bullets, self.walls, True, False)
                hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
                for enemy, bullets_hit in hits.items():
                    for bullet in bullets_hit:
                        enemy.hp -= bullet.damage
                        if enemy.hp <= 0:
                            enemy.kill()
                            self.dummy_enemy = None
                            self.tutorial_step = 6
                            self.tutorial_timer = 0
                            
            # Step 6: Finish
            if self.tutorial_step == 6:
                if self.tutorial_timer > 180: # Wait 3 seconds
                    self.state = "MENU"

        if self.state == "PLAYING":
            # Update Camera
            self.camera.update(self.player)
            
            # Update all sprites
            if self.touch_active:
                move_vec = self.joystick_left.value
                aim_vec = self.joystick_right.value
                self.player.update(self.walls, move_vec, aim_vec)
                
                if self.joystick_right.active and (abs(aim_vec[0]) > 0.1 or abs(aim_vec[1]) > 0.1):
                    bullets = self.player.shoot_dir(aim_vec)
                    if bullets:
                        for b in bullets:
                            self.all_sprites.add(b)
                            self.bullets.add(b)
            else:
                self.player.update(self.walls)
                
            self.enemies.update(self.walls)
            self.bullets.update()
            self.enemy_bullets.update()
            
            # Enemy Logic (Shoot)
            for enemy in self.enemies:
                bullet = enemy.shoot()
                if bullet:
                    self.all_sprites.add(bullet)
                    self.enemy_bullets.add(bullet)
            
            # Enemy Spawning (Continuous)
            self.spawn_timer += 1
            if self.spawn_timer >= ENEMY_SPAWN_RATE / self.difficulty_multiplier: # Faster spawn on higher levels
                self.spawn_timer = 0
                self.spawn_random_enemy()
                
            # Collision: Bullet vs Enemy
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
            for enemy, bullets_hit in hits.items():
                for bullet in bullets_hit:
                    enemy.hp -= bullet.damage
                    if enemy.hp <= 0:
                        enemy.kill()
                        self.score += 10
                        break 
                
            # Collision: Bullet vs Wall
            pygame.sprite.groupcollide(self.bullets, self.walls, True, False)
            pygame.sprite.groupcollide(self.enemy_bullets, self.walls, True, False)

            # Collision: Player vs Enemy
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits:
                self.player.hp -= 1
                if self.player.hp <= 0:
                    self.state = "GAMEOVER"
            
            # Collision: Player vs Enemy Bullet
            hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hits:
                self.player.hp -= 5 # Bullet damage
                if self.player.hp <= 0:
                    self.state = "GAMEOVER"

            # Collision: Player vs Portal
            hits = pygame.sprite.spritecollide(self.player, self.portals, False)
            if hits:
                self.next_level()

    def next_level(self):
        self.level += 1
        self.difficulty_multiplier += 0.2
        # Pick new theme
        self.current_theme = random.choice(THEMES)
        self.new_level()
        # Heal player slightly?
        self.player.hp = min(PLAYER_START_HP, self.player.hp + 20)

    def spawn_random_enemy(self):
        # Spawn in a random room except the one player is in
        if not self.dungeon_gen.rooms: return
        
        # Try a few times to find a valid spot
        for _ in range(5):
            room = random.choice(self.dungeon_gen.rooms)
            x = random.randint(room.rect.x + 1, room.rect.x + room.rect.w - 2) * TILE_SIZE
            y = random.randint(room.rect.y + 1, room.rect.y + room.rect.h - 2) * TILE_SIZE
            
            # Don't spawn too close to player
            dist = ((x - self.player.rect.centerx)**2 + (y - self.player.rect.centery)**2)**0.5
            if dist > 400: # Spawn far away so player doesn't see it pop in
                r = random.random()
                enemy_type = ENEMY_MELEE
                
                if self.level >= 5:
                    if r < 0.2: enemy_type = ENEMY_BOMBER
                    elif r < 0.4: enemy_type = ENEMY_DASHER
                    elif r < 0.6: enemy_type = ENEMY_RANGED
                elif self.level >= 3:
                    if r < 0.2: enemy_type = ENEMY_DASHER
                    elif r < 0.4: enemy_type = ENEMY_RANGED
                else:
                    if r < 0.2: enemy_type = ENEMY_RANGED
                
                enemy = Enemy(x, y, self.player, self.difficulty_multiplier, enemy_type)
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)
                break

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == "MENU":
            self.draw_text(get_text("title", self.lang), self.font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            self.draw_text(get_text("menu_start", self.lang), self.font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.draw_text(get_text("menu_tutorial", self.lang), self.font_medium, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            self.draw_text(get_text("menu_restart", self.lang), self.font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            self.draw_text(get_text("menu_lang", self.lang), self.font_medium, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
            
        elif self.state == "TUTORIAL":
            # Draw Map and Sprites with Camera
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            
            # Tutorial Instructions
            self.draw_tutorial_hud()
            
            # Touch Controls
            if self.touch_active:
                self.joystick_left.draw(self.screen)
                self.joystick_right.draw(self.screen)
                self.btn_skill.draw(self.screen, self.font_small)
                self.btn_switch.draw(self.screen, self.font_small)
            
        elif self.state == "PLAYING":
            # Draw Map and Sprites with Camera
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
                
            # Draw HUD
            self.draw_hud()
            
            # Touch Controls
            if self.touch_active:
                self.joystick_left.draw(self.screen)
                self.joystick_right.draw(self.screen)
                self.btn_skill.draw(self.screen, self.font_small)
                self.btn_switch.draw(self.screen, self.font_small)
            
        elif self.state == "GAMEOVER":
            self.draw_text(get_text("game_over", self.lang), self.font_large, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            self.draw_text(get_text("score", self.lang, self.score), self.font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.draw_text(get_text("level_reached", self.lang, self.level), self.font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            self.draw_text(get_text("restart_prompt", self.lang), self.font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

    def draw_tutorial_hud(self):
        text = ""
        if self.tutorial_step == 1:
            text = get_text("tut_move", self.lang)
        elif self.tutorial_step == 2:
            text = get_text("tut_shoot", self.lang)
        elif self.tutorial_step == 3:
            text = get_text("tut_switch", self.lang)
        elif self.tutorial_step == 4:
            text = get_text("tut_skill", self.lang)
        elif self.tutorial_step == 5:
            text = get_text("tut_dummy", self.lang)
        elif self.tutorial_step == 6:
            text = get_text("tut_complete", self.lang)
            
        # Draw text at top
        self.draw_text(text, self.font_medium, WHITE, SCREEN_WIDTH // 2, 50)
        
        # Show HUD elements for context
        self.draw_hud()

    def draw_hud(self):
        # HP Bar
        bar_width = 200
        bar_height = 20
        fill = (self.player.hp / PLAYER_START_HP) * bar_width
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(self.screen, GREEN, fill_rect)
        pygame.draw.rect(self.screen, WHITE, outline_rect, 2)
        
        # Weapon Info
        w_name = self.player.weapon.name
        # Map weapon name to localized string key
        w_key = "weapon_" + w_name.lower()
        w_name_loc = get_text(w_key, self.lang)
        
        weapon_text = get_text("weapon", self.lang, w_name_loc)
        self.draw_text(weapon_text, self.font_small, WHITE, 100, 50, align="left")
        
        # Skill Info
        skill_text = get_text("skill_ready", self.lang)
        skill_color = CYAN
        if self.player.skill_cooldown > 0:
            skill_text = get_text("skill_cooldown", self.lang, int(self.player.skill_cooldown / 60))
            skill_color = GRAY
        self.draw_text(skill_text, self.font_small, skill_color, 100, 80, align="left")
        
        # Score & Level
        score_text = get_text("score", self.lang, self.score)
        self.draw_text(score_text, self.font_small, WHITE, SCREEN_WIDTH - 100, 20)
        
        level_text = get_text("level", self.lang, self.level)
        self.draw_text(level_text, self.font_small, YELLOW, SCREEN_WIDTH // 2, 20)

    def draw_text(self, text, font, color, x, y, align="center"):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = (x, y)
        elif align == "left":
            text_rect.topleft = (x, y) # This might need adjustment based on how I call it
            # Actually let's just center it for now or use top-left
            text_rect.center = (x, y) # Simplified
        elif align == "right":
            text_rect.topright = (x, y)
        self.screen.blit(text_surface, text_rect)
