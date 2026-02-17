import pygame
from config import *

class SpriteFactory:
    @staticmethod
    def create_player_sprite():
        # Create a surface with transparency
        surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        
        # Body (Circle)
        center = (PLAYER_SIZE // 2, PLAYER_SIZE // 2)
        radius = PLAYER_SIZE // 2
        pygame.draw.circle(surface, PLAYER_COLOR, center, radius)
        
        # Outline
        pygame.draw.circle(surface, WHITE, center, radius, 2)
        
        # Eyes (White sclera)
        eye_radius = 4
        left_eye_pos = (center[0] - 6, center[1] - 4)
        right_eye_pos = (center[0] + 6, center[1] - 4)
        pygame.draw.circle(surface, WHITE, left_eye_pos, eye_radius)
        pygame.draw.circle(surface, WHITE, right_eye_pos, eye_radius)
        
        # Pupils (Black)
        pupil_radius = 2
        # Look slightly forward/down
        pygame.draw.circle(surface, BLACK, (left_eye_pos[0], left_eye_pos[1] + 1), pupil_radius)
        pygame.draw.circle(surface, BLACK, (right_eye_pos[0], right_eye_pos[1] + 1), pupil_radius)
        
        return surface

    @staticmethod
    def create_enemy_sprite(enemy_type, hp_multiplier=1.0):
        surface = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
        
        # Color based on type
        if enemy_type == ENEMY_MELEE:
            color = MELEE_COLOR
            # Darken if stronger
            if hp_multiplier > 1.2: color = (180, 0, 0)
            if hp_multiplier > 1.5: color = (120, 0, 0)
            
            # Body (Rounded Rect)
            rect = pygame.Rect(0, 0, ENEMY_SIZE, ENEMY_SIZE)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=5)
            
            # Angry Eyes (Triangles)
            pygame.draw.polygon(surface, YELLOW, [(8, 10), (16, 14), (8, 18)])
            pygame.draw.polygon(surface, YELLOW, [(24, 10), (16, 14), (24, 18)])
            # Mouth
            pygame.draw.line(surface, BLACK, (10, 24), (22, 24), 2)
            
        elif enemy_type == ENEMY_RANGED:
            color = RANGED_COLOR
            # Darken if stronger
            if hp_multiplier > 1.2: color = (0, 180, 0)
            if hp_multiplier > 1.5: color = (0, 120, 0)

            # Body (Triangle / Robe-like)
            points = [(ENEMY_SIZE//2, 2), (2, ENEMY_SIZE-2), (ENEMY_SIZE-2, ENEMY_SIZE-2)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, BLACK, points, 2)
            
            # Glowing Eye (Single Cyclops eye)
            pygame.draw.circle(surface, CYAN, (ENEMY_SIZE//2, ENEMY_SIZE//2 - 2), 6)
            pygame.draw.circle(surface, WHITE, (ENEMY_SIZE//2, ENEMY_SIZE//2 - 2), 2)
        
        elif enemy_type == ENEMY_DASHER:
            color = DASHER_COLOR
            # Lightning Bolt Shape or similar
            # For simplicity, a sleek diamond
            points = [(ENEMY_SIZE//2, 0), (ENEMY_SIZE, ENEMY_SIZE//2), (ENEMY_SIZE//2, ENEMY_SIZE), (0, ENEMY_SIZE//2)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, WHITE, points, 2)
            # Speed lines
            pygame.draw.line(surface, WHITE, (5, ENEMY_SIZE//2), (ENEMY_SIZE-5, ENEMY_SIZE//2), 2)

        elif enemy_type == ENEMY_BOMBER:
            color = BOMBER_COLOR
            # Bomb shape (Circle)
            pygame.draw.circle(surface, color, (ENEMY_SIZE//2, ENEMY_SIZE//2), ENEMY_SIZE//2 - 2)
            # Fuse
            pygame.draw.line(surface, ORANGE, (ENEMY_SIZE//2, 5), (ENEMY_SIZE//2 + 5, 0), 3)
            # Skull or danger sign
            pygame.draw.circle(surface, RED, (ENEMY_SIZE//2, ENEMY_SIZE//2), 6)
        
        return surface

    @staticmethod
    def create_portal_sprite():
        surface = pygame.Surface((PORTAL_SIZE, PORTAL_SIZE), pygame.SRCALPHA)
        center = (PORTAL_SIZE // 2, PORTAL_SIZE // 2)
        radius = PORTAL_SIZE // 2
        
        # Outer ring
        pygame.draw.circle(surface, PORTAL_COLOR, center, radius, 4)
        
        # Inner swirl (simplified as concentric circles for now)
        pygame.draw.circle(surface, (100, 0, 100), center, radius - 8, 2)
        pygame.draw.circle(surface, (200, 100, 255), center, radius - 16)
        
        return surface
