import pygame
import random
from config import *

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, color=DARK_GRAY):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILE_SIZE, y * TILE_SIZE)

class Room:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.center = (x + w // 2, y + h // 2)

    def intersect(self, other):
        return self.rect.colliderect(other.rect.inflate(2, 2))  # Add padding

class DungeonGenerator:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)] # 1 = Wall, 0 = Floor
        self.rooms = []

    def generate(self):
        # Place Rooms
        for _ in range(MAX_ROOMS):
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Room(x, y, w, h)
            
            failed = False
            for other in self.rooms:
                if new_room.intersect(other):
                    failed = True
                    break
            
            if not failed:
                self.create_room(new_room)
                
                if self.rooms:
                    # Connect to previous room
                    prev_center = self.rooms[-1].center
                    new_center = new_room.center
                    
                    if random.randint(0, 1) == 1:
                        self.create_h_tunnel(prev_center[0], new_center[0], prev_center[1])
                        self.create_v_tunnel(prev_center[1], new_center[1], new_center[0])
                    else:
                        self.create_v_tunnel(prev_center[1], new_center[1], prev_center[0])
                        self.create_h_tunnel(prev_center[0], new_center[0], new_center[1])
                
                self.rooms.append(new_room)

        return self.grid, self.rooms

    def create_room(self, room):
        for y in range(room.rect.y, room.rect.y + room.rect.h):
            for x in range(room.rect.x, room.rect.x + room.rect.w):
                self.grid[y][x] = 0

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = 0
            self.grid[y+1][x] = 0 # Make tunnel wider

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = 0
            self.grid[y][x+1] = 0 # Make tunnel wider

    def build_walls(self, wall_color=DARK_GRAY):
        walls = pygame.sprite.Group()
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    walls.add(Wall(x, y, wall_color))
        return walls
