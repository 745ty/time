import pygame
import math
from config import *

class VirtualJoystick:
    def __init__(self, x, y, radius, inner_radius=None):
        self.center = (x, y)
        self.radius = radius
        self.inner_radius = inner_radius or (radius // 2)
        
        # Current state
        self.touch_pos = self.center
        self.active = False
        self.value = (0, 0) # (x, y) normalized -1 to 1
        self.touch_id = None # To track multi-touch

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            x = event.x * SCREEN_WIDTH
            y = event.y * SCREEN_HEIGHT
            dist = math.sqrt((x - self.center[0])**2 + (y - self.center[1])**2)
            
            if dist <= self.radius * 1.5: # Generous hit area
                self.active = True
                self.touch_id = event.finger_id
                self.update_pos(x, y)
                return True # Consumed

        elif event.type == pygame.FINGERMOTION:
            if self.active and event.finger_id == self.touch_id:
                x = event.x * SCREEN_WIDTH
                y = event.y * SCREEN_HEIGHT
                self.update_pos(x, y)
                return True

        elif event.type == pygame.FINGERUP:
            if self.active and event.finger_id == self.touch_id:
                self.reset()
                return True
        
        # Mouse fallback for PC testing
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                dist = math.sqrt((mx - self.center[0])**2 + (my - self.center[1])**2)
                if dist <= self.radius:
                    self.active = True
                    self.touch_id = -1 # Mouse ID
                    self.update_pos(mx, my)
                    return True
        elif event.type == pygame.MOUSEMOTION:
            if self.active and self.touch_id == -1:
                mx, my = event.pos
                self.update_pos(mx, my)
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.active and self.touch_id == -1:
                self.reset()
                return True
                
        return False

    def update_pos(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > self.radius:
            # Clamp to radius
            ratio = self.radius / dist
            self.touch_pos = (self.center[0] + dx * ratio, self.center[1] + dy * ratio)
            self.value = (dx / dist, dy / dist) # Normalized full magnitude
        else:
            self.touch_pos = (x, y)
            if dist > 10: # Deadzone
                self.value = (dx / self.radius, dy / self.radius)
            else:
                self.value = (0, 0)

    def reset(self):
        self.active = False
        self.touch_pos = self.center
        self.value = (0, 0)
        self.touch_id = None

    def draw(self, screen):
        # Draw Base (Semi-transparent)
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 200, 200, 50), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (255, 255, 255, 100), (self.radius, self.radius), self.radius, 2)
        screen.blit(s, (self.center[0] - self.radius, self.center[1] - self.radius))
        
        # Draw Knob
        knob_pos = (int(self.touch_pos[0]), int(self.touch_pos[1]))
        pygame.draw.circle(screen, (255, 255, 255, 150), knob_pos, self.inner_radius)


class TouchButton:
    def __init__(self, x, y, radius, label="", color=(100, 100, 255), callback=None):
        self.center = (x, y)
        self.radius = radius
        self.label = label
        self.color = color
        self.callback = callback
        self.pressed = False
        self.touch_id = None

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            x = event.x * SCREEN_WIDTH
            y = event.y * SCREEN_HEIGHT
            dist = math.sqrt((x - self.center[0])**2 + (y - self.center[1])**2)
            if dist <= self.radius:
                self.pressed = True
                self.touch_id = event.finger_id
                if self.callback: self.callback()
                return True
        
        elif event.type == pygame.FINGERUP:
            if self.pressed and event.finger_id == self.touch_id:
                self.pressed = False
                self.touch_id = None
                return True

        # Mouse fallback
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                dist = math.sqrt((mx - self.center[0])**2 + (my - self.center[1])**2)
                if dist <= self.radius:
                    self.pressed = True
                    self.touch_id = -1
                    if self.callback: self.callback()
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed and self.touch_id == -1:
                self.pressed = False
                self.touch_id = None
                return True
                
        return False

    def draw(self, screen, font):
        color = self.color if not self.pressed else (min(255, self.color[0]+50), min(255, self.color[1]+50), min(255, self.color[2]+50))
        
        # Base
        pygame.draw.circle(screen, color, self.center, self.radius)
        pygame.draw.circle(screen, WHITE, self.center, self.radius, 2)
        
        # Label
        if self.label:
            text_surf = font.render(self.label, True, WHITE)
            text_rect = text_surf.get_rect(center=self.center)
            screen.blit(text_surf, text_rect)
