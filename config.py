import pygame

# Screen
SCREEN_WIDTH = 1024  # Increased for larger view
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Soul Guardian - Roguelike Prototype"

# Map / Dungeon
TILE_SIZE = 48
MAP_WIDTH = 50   # in tiles
MAP_HEIGHT = 50  # in tiles
ROOM_MAX_SIZE = 15
ROOM_MIN_SIZE = 6
MAX_ROOMS = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)  # Dark gray background
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 50, 220)
YELLOW = (220, 220, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Player
PLAYER_SPEED = 5
PLAYER_SIZE = 32
PLAYER_COLOR = BLUE
PLAYER_START_HP = 100

# Weapons
WEAPON_SWORD = "Sword"
WEAPON_PISTOL = "Pistol"
WEAPON_SHOTGUN = "Shotgun"
WEAPON_MACHINEGUN = "MachineGun"

# Sword Stats
SWORD_DAMAGE = 30
SWORD_RANGE = 60
SWORD_COOLDOWN = 30
SWORD_COLOR = (200, 200, 255)

# Player Skills
SKILL_DASH_SPEED = 15
SKILL_DASH_DURATION = 10 # frames
SKILL_DASH_COOLDOWN = 120 # frames (2 seconds)

# Bullet
BULLET_SPEED = 12
BULLET_SIZE = 8
BULLET_COLOR = YELLOW

# Enemy
ENEMY_SPEED = 2.5
ENEMY_SIZE = 32
ENEMY_SPAWN_RATE = 180  # frames

# Enemy Types
ENEMY_MELEE = "Melee"
ENEMY_RANGED = "Ranged"
ENEMY_DASHER = "Dasher"
ENEMY_BOMBER = "Bomber"

# Melee Enemy Stats
MELEE_HP_BASE = 40
MELEE_COLOR = RED
MELEE_SPEED = 2.5

# Ranged Enemy Stats
RANGED_HP_BASE = 20
RANGED_COLOR = GREEN
RANGED_SPEED = 2.0
RANGED_ATTACK_RANGE = 300
RANGED_COOLDOWN = 120 # frames

# Dasher Enemy Stats
DASHER_HP_BASE = 25
DASHER_COLOR = CYAN
DASHER_SPEED = 4.5 # Very fast
DASHER_DASH_COOLDOWN = 180 # Not really a dash, just high speed

# Bomber Enemy Stats
BOMBER_HP_BASE = 15 # Weak
BOMBER_COLOR = BLACK
BOMBER_SPEED = 3.0
BOMBER_EXPLODE_RANGE = 60
BOMBER_DAMAGE = 50

# Dungeon Themes
THEMES = [
    {"wall": (100, 100, 100), "floor": (30, 30, 30), "name": "Dungeon"}, # Default Gray
    {"wall": (80, 50, 50), "floor": (40, 20, 20), "name": "Hell"}, # Red/Dark
    {"wall": (50, 80, 50), "floor": (20, 40, 20), "name": "Forest"}, # Green/Dark
    {"wall": (50, 50, 80), "floor": (20, 20, 40), "name": "Ice"}, # Blue/Dark
    {"wall": (100, 80, 40), "floor": (50, 40, 20), "name": "Desert"}, # Yellow/Brown
]

# Enemy Bullet
ENEMY_BULLET_SPEED = 6
ENEMY_BULLET_SIZE = 10
ENEMY_BULLET_COLOR = ORANGE

# Portal
PORTAL_SIZE = 40
PORTAL_COLOR = PURPLE

# UI
FONT_SIZE_LARGE = 64
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
