import pygame
import random
import math
import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TILE_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Fade system constants
FADE_TIME = 300  # Frames until tile completely fades (5 seconds at 60 FPS)
FADE_RATE = 1.0 / FADE_TIME

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)
DARK_YELLOW = (255, 255, 100)
BEIGE = (245, 245, 220)
CREAM = (255, 253, 208)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
LIGHT_GRAY = (192, 192, 192)
FLUORESCENT_WHITE = (248, 248, 255)
DIRTY_WHITE = (240, 240, 235)
BUZZING_YELLOW = (255, 255, 150)

# Game settings
PLAYER_SPEED = 2
FLASHLIGHT_RANGE = 80
FLASHLIGHT_ANGLE = 60  # degrees

class TileType(Enum):
    EMPTY = 0
    WALL = 1
    FLOOR = 2
    DOOR = 3
    EXIT = 4
    VENT = 5
    WATER_DAMAGE = 6
    ELECTRICAL = 7
    STAIRWELL = 8
    ELEVATOR = 9

class RoomType(Enum):
    OFFICE_SPACE = "office_space"
    LONG_HALLWAY = "long_hallway"
    CONFERENCE_ROOM = "conference_room"
    STORAGE_ROOM = "storage_room"
    ELECTRICAL_ROOM = "electrical_room"
    FLOODED_AREA = "flooded_area"
    MAINTENANCE = "maintenance"
    LOBBY = "lobby"
    CAFETERIA = "cafeteria"
    BATHROOM = "bathroom"
    SERVER_ROOM = "server_room"
    ABANDONED_OFFICE = "abandoned_office"

@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int
    room_type: RoomType
    is_lit: bool = False
    connections: List[Tuple[int, int]] = None

    def __post_init__(self):
        if self.connections is None:
            self.connections = []

    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def overlaps(self, other: 'Room') -> bool:
        return not (self.x + self.width <= other.x or 
                   other.x + other.width <= self.x or 
                   self.y + self.height <= other.y or 
                   other.y + other.height <= self.y)

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.angle = 0  # Facing direction in degrees
        self.has_flashlight = True
        
    def move(self, dx: float, dy: float, level_map: List[List[TileType]]):
        # Check horizontal movement
        new_x = self.x + dx
        if self._can_move_to(new_x, self.y, level_map):
            self.x = new_x
        
        # Check vertical movement
        new_y = self.y + dy
        if self._can_move_to(self.x, new_y, level_map):
            self.y = new_y
    
    def _can_move_to(self, x: float, y: float, level_map: List[List[TileType]]) -> bool:
        # Player is 16x16 pixels, so check all four corners plus center
        player_size = 8  # Half the player size (16/2)
        
        positions_to_check = [
            (x - player_size, y - player_size),  # Top-left
            (x + player_size, y - player_size),  # Top-right
            (x - player_size, y + player_size),  # Bottom-left
            (x + player_size, y + player_size),  # Bottom-right
            (x, y)  # Center
        ]
        
        for check_x, check_y in positions_to_check:
            grid_x = int(check_x // TILE_SIZE)
            grid_y = int(check_y // TILE_SIZE)
            
            # Check bounds
            if not (0 <= grid_x < len(level_map[0]) and 0 <= grid_y < len(level_map)):
                return False
            
            # Check for walls
            if level_map[grid_y][grid_x] == TileType.WALL:
                return False
        
        return True
    
    def update_angle(self, mouse_pos: Tuple[int, int]):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.degrees(math.atan2(dy, dx))

class BackroomsGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[TileType.WALL for _ in range(width)] for _ in range(height)]
        self.rooms = []
        
    def generate(self) -> Tuple[List[List[TileType]], List[Room]]:
        self._generate_rooms()
        self._connect_rooms()
        self._add_room_features()
        return self.grid, self.rooms
    
    def _generate_rooms(self):
        attempts = 0
        while len(self.rooms) < 20 and attempts < 150:
            room_type = random.choice(list(RoomType))
            width, height = self._get_room_size(room_type)
            
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            
            # Most backrooms areas are dark with flickering lights
            is_lit = random.random() < 0.3  # 30% chance of being lit
            new_room = Room(x, y, width, height, room_type, is_lit)
            
            if not any(new_room.overlaps(existing) for existing in self.rooms):
                self.rooms.append(new_room)
                self._carve_room(new_room)
            
            attempts += 1
    
    def _get_room_size(self, room_type: RoomType) -> Tuple[int, int]:
        size_ranges = {
            RoomType.OFFICE_SPACE: (8, 16, 6, 12),
            RoomType.LONG_HALLWAY: (20, 40, 3, 6),
            RoomType.CONFERENCE_ROOM: (10, 16, 8, 14),
            RoomType.STORAGE_ROOM: (4, 8, 4, 8),
            RoomType.ELECTRICAL_ROOM: (5, 8, 5, 8),
            RoomType.FLOODED_AREA: (8, 14, 8, 14),
            RoomType.MAINTENANCE: (6, 10, 4, 8),
            RoomType.LOBBY: (12, 20, 10, 16),
            RoomType.CAFETERIA: (12, 18, 8, 14),
            RoomType.BATHROOM: (4, 8, 6, 10),
            RoomType.SERVER_ROOM: (6, 10, 6, 10),
            RoomType.ABANDONED_OFFICE: (6, 12, 6, 12)
        }
        
        min_w, max_w, min_h, max_h = size_ranges.get(room_type, (6, 12, 6, 12))
        return random.randint(min_w, max_w), random.randint(min_h, max_h)
    
    def _carve_room(self, room: Room):
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = TileType.FLOOR
    
    def _connect_rooms(self):
        if len(self.rooms) < 2:
            return
            
        connected = {0}
        unconnected = set(range(1, len(self.rooms)))
        
        while unconnected:
            room_a_idx = random.choice(list(connected))
            room_b_idx = random.choice(list(unconnected))
            
            room_a = self.rooms[room_a_idx]
            room_b = self.rooms[room_b_idx]
            
            self._create_corridor(room_a.center(), room_b.center())
            
            connected.add(room_b_idx)
            unconnected.remove(room_b_idx)
        
        # Add some extra connections for that maze-like backrooms feel
        for _ in range(len(self.rooms) // 3):
            room_a = random.choice(self.rooms)
            room_b = random.choice(self.rooms)
            if room_a != room_b:
                self._create_corridor(room_a.center(), room_b.center())
    
    def _create_corridor(self, start: Tuple[int, int], end: Tuple[int, int]):
        x1, y1 = start
        x2, y2 = end
        
        # Create L-shaped corridor
        if random.choice([True, False]):
            # Horizontal first, then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.grid[y1][x] = TileType.FLOOR
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.grid[y][x2] = TileType.FLOOR
        else:
            # Vertical first, then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x1 < self.width and 0 <= y < self.height:
                    self.grid[y][x1] = TileType.FLOOR
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y2 < self.height:
                    self.grid[y2][x] = TileType.FLOOR
    
    def _add_room_features(self):
        for room in self.rooms:
            self._add_features_by_type(room)
    
    def _add_features_by_type(self, room: Room):
        cx, cy = room.center()
        
        if room.room_type == RoomType.STORAGE_ROOM:
            # Add some exits/items scattered around
            for _ in range(random.randint(1, 3)):
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                if self.grid[y][x] == TileType.FLOOR:
                    self.grid[y][x] = TileType.EXIT
        
        elif room.room_type == RoomType.ELECTRICAL_ROOM:
            # Add electrical hazards
            for _ in range(random.randint(2, 4)):
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                if self.grid[y][x] == TileType.FLOOR:
                    self.grid[y][x] = TileType.ELECTRICAL
        
        elif room.room_type == RoomType.FLOODED_AREA:
            # Add water damage in center
            water_width = max(2, room.width // 2)
            water_height = max(2, room.height // 2)
            start_x = cx - water_width // 2
            start_y = cy - water_height // 2
            
            for y in range(start_y, start_y + water_height):
                for x in range(start_x, start_x + water_width):
                    if (room.x < x < room.x + room.width - 1 and 
                        room.y < y < room.y + room.height - 1):
                        self.grid[y][x] = TileType.WATER_DAMAGE
        
        elif room.room_type == RoomType.MAINTENANCE:
            # Add vents
            for _ in range(random.randint(1, 3)):
                x = random.randint(room.x + 1, room.x + room.width - 2)
                y = random.randint(room.y + 1, room.y + room.height - 2)
                if self.grid[y][x] == TileType.FLOOR:
                    self.grid[y][x] = TileType.VENT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Backrooms - Level 0")
        self.clock = pygame.time.Clock()
        
        # Camera offset
        self.camera_x = 0
        self.camera_y = 0
        
        # Generate backrooms layout (make it larger for better exploration)
        generator = BackroomsGenerator(GRID_WIDTH * 3, GRID_HEIGHT * 3)
        self.level_map, self.rooms = generator.generate()
        
        # Find a starting position in the first room
        start_room = self.rooms[0] if self.rooms else None
        if start_room:
            self.player = Player(
                start_room.center()[0] * TILE_SIZE,
                start_room.center()[1] * TILE_SIZE
            )
        else:
            self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Visibility system
        self.visible_tiles = set()
        self.explored_tiles = {}  # Now stores fade timers
        
    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED
        
        self.player.move(dx, dy, self.level_map)
        
        # Update camera to center on player
        self._update_camera()
        
        # Convert mouse position to world coordinates for player angle
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_x = mouse_pos[0] + self.camera_x
        world_mouse_y = mouse_pos[1] + self.camera_y
        self.player.update_angle((world_mouse_x, world_mouse_y))
        
        self._update_visibility()
    
    def _update_camera(self):
        # Center camera on player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
    
    def _update_visibility(self):
        self.visible_tiles.clear()
        
        player_grid_x = int(self.player.x // TILE_SIZE)
        player_grid_y = int(self.player.y // TILE_SIZE)
        
        # Check if player is in a lit room
        current_room = self._get_current_room()
        
        if current_room and current_room.is_lit:
            # If in a lit room, make entire room visible
            for y in range(current_room.y, current_room.y + current_room.height):
                for x in range(current_room.x, current_room.x + current_room.width):
                    if 0 <= x < len(self.level_map[0]) and 0 <= y < len(self.level_map):
                        self.visible_tiles.add((x, y))
        
        # Always use flashlight mechanics (even in lit rooms)
        self._calculate_flashlight_visibility()
        
        # Update fade timers for explored tiles
        self._update_fade_timers()
        
        # Add/refresh visible tiles in explored tiles with full visibility
        for tile in self.visible_tiles:
            self.explored_tiles[tile] = 1.0  # Full visibility
    
    def _update_fade_timers(self):
        # Fade out tiles that are not currently visible
        tiles_to_remove = []
        for tile, visibility in self.explored_tiles.items():
            if tile not in self.visible_tiles:
                new_visibility = max(0.0, visibility - FADE_RATE)
                if new_visibility <= 0:
                    tiles_to_remove.append(tile)
                else:
                    self.explored_tiles[tile] = new_visibility
        
        # Remove completely faded tiles
        for tile in tiles_to_remove:
            del self.explored_tiles[tile]
    
    def _get_current_room(self) -> Optional[Room]:
        player_grid_x = int(self.player.x // TILE_SIZE)
        player_grid_y = int(self.player.y // TILE_SIZE)
        
        for room in self.rooms:
            if (room.x <= player_grid_x < room.x + room.width and
                room.y <= player_grid_y < room.y + room.height):
                return room
        return None
    
    def _calculate_flashlight_visibility(self):
        if not self.player.has_flashlight:
            return
        
        player_grid_x = int(self.player.x // TILE_SIZE)
        player_grid_y = int(self.player.y // TILE_SIZE)
        
        # Cast rays for flashlight cone
        start_angle = self.player.angle - FLASHLIGHT_ANGLE // 2
        end_angle = self.player.angle + FLASHLIGHT_ANGLE // 2
        
        for angle in range(int(start_angle), int(end_angle) + 1, 2):
            self._cast_ray(
                self.player.x / TILE_SIZE,
                self.player.y / TILE_SIZE,
                math.radians(angle),
                FLASHLIGHT_RANGE // TILE_SIZE
            )
    
    def _cast_ray(self, start_x: float, start_y: float, angle: float, max_distance: float):
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        x, y = start_x, start_y
        distance = 0
        
        while distance < max_distance:
            grid_x, grid_y = int(x), int(y)
            
            if not (0 <= grid_x < len(self.level_map[0]) and 0 <= grid_y < len(self.level_map)):
                break
                
            self.visible_tiles.add((grid_x, grid_y))
            
            if self.level_map[grid_y][grid_x] == TileType.WALL:
                break
            
            x += dx * 0.1
            y += dy * 0.1
            distance += 0.1
    
    def _get_tile_color(self, tile_type: TileType, room_type: RoomType = None) -> Tuple[int, int, int]:
        base_colors = {
            TileType.WALL: CREAM,  # Yellowy backrooms walls
            TileType.FLOOR: DARK_YELLOW,  # Moist carpet
            TileType.EXIT: GREEN,  # Emergency exits
            TileType.VENT: DARK_GRAY,  # Air vents
            TileType.WATER_DAMAGE: BLUE,  # Water stains
            TileType.ELECTRICAL: ORANGE,  # Electrical hazards
            TileType.STAIRWELL: LIGHT_GRAY,
            TileType.ELEVATOR: GRAY,
        }
        
        # Modify colors based on room type for that authentic backrooms feel
        if room_type:
            if room_type == RoomType.OFFICE_SPACE and tile_type == TileType.FLOOR:
                return BEIGE  # Office carpet
            elif room_type == RoomType.LONG_HALLWAY and tile_type == TileType.FLOOR:
                return DARK_YELLOW  # Classic backrooms carpet
            elif room_type == RoomType.CONFERENCE_ROOM and tile_type == TileType.FLOOR:
                return BROWN  # Conference room carpet
            elif room_type == RoomType.FLOODED_AREA and tile_type == TileType.FLOOR:
                return DARK_BROWN  # Water-damaged carpet
            elif room_type == RoomType.ELECTRICAL_ROOM and tile_type == TileType.FLOOR:
                return GRAY  # Industrial flooring
            elif room_type == RoomType.BATHROOM and tile_type == TileType.FLOOR:
                return DIRTY_WHITE  # Tile flooring
            elif room_type == RoomType.SERVER_ROOM and tile_type == TileType.FLOOR:
                return DARK_GRAY  # Raised server room floor
            elif room_type == RoomType.ABANDONED_OFFICE and tile_type == TileType.FLOOR:
                return DARK_BROWN  # Old, deteriorated carpet
        
        return base_colors.get(tile_type, BUZZING_YELLOW)
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Calculate which tiles are visible on screen
        start_x = max(0, int(self.camera_x // TILE_SIZE) - 1)
        end_x = min(len(self.level_map[0]), int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        start_y = max(0, int(self.camera_y // TILE_SIZE) - 1)
        end_y = min(len(self.level_map), int((self.camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 2)
        
        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Convert world coordinates to screen coordinates
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y
                tile_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                tile_type = self.level_map[y][x]
                
                # Find room type for this tile
                room_type = None
                for room in self.rooms:
                    if (room.x <= x < room.x + room.width and
                        room.y <= y < room.y + room.height):
                        room_type = room.room_type
                        break
                
                is_visible = (x, y) in self.visible_tiles
                is_explored = (x, y) in self.explored_tiles
                
                if is_visible:
                    # Fully visible
                    color = self._get_tile_color(tile_type, room_type)
                    pygame.draw.rect(self.screen, color, tile_rect)
                elif is_explored:
                    # Explored but not currently visible (fading)
                    visibility = self.explored_tiles[(x, y)]
                    color = self._get_tile_color(tile_type, room_type)
                    # Apply fading effect
                    faded_color = tuple(int(c * visibility * 0.5) for c in color)  # Max 50% brightness when faded
                    pygame.draw.rect(self.screen, faded_color, tile_rect)
                
                # Draw tile borders for visible tiles
                if is_visible and tile_type != TileType.WALL:
                    pygame.draw.rect(self.screen, GRAY, tile_rect, 1)
        
        # Draw player (convert world coordinates to screen coordinates)
        player_screen_x = int(self.player.x - self.camera_x)
        player_screen_y = int(self.player.y - self.camera_y)
        player_rect = pygame.Rect(
            player_screen_x - 8,
            player_screen_y - 8,
            16, 16
        )
        pygame.draw.rect(self.screen, GREEN, player_rect)
        
        # Draw direction indicator
        end_x = player_screen_x + math.cos(math.radians(self.player.angle)) * 20
        end_y = player_screen_y + math.sin(math.radians(self.player.angle)) * 20
        pygame.draw.line(self.screen, WHITE, 
                        (player_screen_x, player_screen_y), 
                        (int(end_x), int(end_y)), 2)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        # Current room info
        current_room = self._get_current_room()
        if current_room:
            room_text = f"Area: {current_room.room_type.value.replace('_', ' ').title()}"
            lighting_text = "Fluorescent Lights" if current_room.is_lit else "Dim/Broken Lights"
        else:
            room_text = "Area: Hallway"
            lighting_text = "Dim/Broken Lights"
        
        font = pygame.font.Font(None, 36)
        room_surface = font.render(room_text, True, FLUORESCENT_WHITE)
        lighting_surface = font.render(f"Lighting: {lighting_text}", True, FLUORESCENT_WHITE)
        
        self.screen.blit(room_surface, (10, 10))
        self.screen.blit(lighting_surface, (10, 50))
        
        # Backrooms-themed instructions
        instructions = [
            "WASD/Arrow Keys: Move carefully",
            "Mouse: Aim flashlight",
            "Find the way out...",
            "The humming grows louder..."
        ]
        
        small_font = pygame.font.Font(None, 24)
        for i, instruction in enumerate(instructions):
            text_surface = small_font.render(instruction, True, BUZZING_YELLOW)
            self.screen.blit(text_surface, (10, SCREEN_HEIGHT - 110 + i * 25))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()  
