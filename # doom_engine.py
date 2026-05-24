"""
Mobile Port of Raycasting Game with PC Testing Support
Touch controls for Android, Mouse controls for PC testing
"""

import pygame
import math
import sys

# ---------------------- INIT ----------------------
pygame.init()

# Get display info for proper scaling
info = pygame.display.Info()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# ---------------------- TOUCH/MOUSE CONTROLS ----------------------
class Controls:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Control zones (for touch)
        self.left_zone = pygame.Rect(0, 0, screen_width // 3, screen_height)
        self.right_zone = pygame.Rect(screen_width * 2 // 3, 0, screen_width // 3, screen_height)
        
        # Movement state
        self.move_dir = [0, 0]  # forward/back, left/right
        self.look_dir = [0, 0]  # yaw, pitch
        self.move_active = False
        self.look_active = False
        
        # Control positions
        self.move_center = None
        self.look_center = None
        self.move_touch_pos = None
        self.look_touch_pos = None
        
        # For mouse testing
        self.mouse_look_active = False
        self.mouse_move_active = False
        
    def handle_event(self, event):
        # Touch events (for Android)
        if event.type == pygame.FINGERDOWN:
            x = event.x * self.screen_width
            y = event.y * self.screen_height
            
            if self.left_zone.collidepoint(x, y) and not self.move_active:
                self.move_active = True
                self.move_center = (x, y)
                self.move_touch_pos = (x, y)
                self.move_dir = [0, 0]
            elif self.right_zone.collidepoint(x, y) and not self.look_active:
                self.look_active = True
                self.look_center = (x, y)
                self.look_touch_pos = (x, y)
                self.look_dir = [0, 0]
                
        elif event.type == pygame.FINGERMOTION:
            if event.finger_id == 0 and self.move_active:
                x = event.x * self.screen_width
                y = event.y * self.screen_height
                self.move_touch_pos = (x, y)
                
                dx = x - self.move_center[0]
                dy = y - self.move_center[1]
                max_dist = self.screen_width // 6
                
                # Calculate move direction (forward/back, left/right)
                self.move_dir[0] = max(-1, min(1, dy / max_dist))  # forward/back
                self.move_dir[1] = max(-1, min(1, dx / max_dist))  # left/right
                
            elif event.finger_id == 1 and self.look_active:
                x = event.x * self.screen_width
                y = event.y * self.screen_height
                self.look_touch_pos = (x, y)
                
                dx = x - self.look_center[0]
                dy = y - self.look_center[1]
                self.look_dir[0] = dx * 0.008  # yaw
                self.look_dir[1] = dy * 0.008  # pitch
                
        elif event.type == pygame.FINGERUP:
            if event.finger_id == 0:
                self.move_active = False
                self.move_center = None
                self.move_touch_pos = None
                self.move_dir = [0, 0]
            elif event.finger_id == 1:
                self.look_active = False
                self.look_center = None
                self.look_touch_pos = None
                self.look_dir = [0, 0]
        
        # Mouse events for PC testing
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                x, y = event.pos
                if self.left_zone.collidepoint(x, y):
                    self.mouse_move_active = True
                    self.move_center = (x, y)
                    self.move_touch_pos = (x, y)
                elif self.right_zone.collidepoint(x, y):
                    self.mouse_look_active = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_move_active = False
                self.move_active = False
                self.move_center = None
                self.move_dir = [0, 0]
                self.mouse_look_active = False
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
        
        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_look_active:
                dx, dy = event.rel
                self.look_dir[0] = dx * 0.005
                self.look_dir[1] = dy * 0.005
            elif self.mouse_move_active:
                x, y = event.pos
                self.move_touch_pos = (x, y)
                if self.move_center:
                    dx = x - self.move_center[0]
                    dy = y - self.move_center[1]
                    max_dist = self.screen_width // 6
                    self.move_dir[0] = max(-1, min(1, dy / max_dist))
                    self.move_dir[1] = max(-1, min(1, dx / max_dist))
    
    def update(self):
        """Update control states"""
        if self.mouse_move_active and self.move_touch_pos:
            self.move_active = True
        if self.mouse_look_active:
            self.look_active = True
    
    def draw(self, screen):
        # Draw control zones (semi-transparent)
        s = pygame.Surface((self.screen_width // 3, self.screen_height), pygame.SRCALPHA)
        s.fill((50, 50, 50, 30))
        screen.blit(s, (0, 0))
        screen.blit(s, (self.screen_width * 2 // 3, 0))
        
        # Draw movement joystick
        if self.move_center and self.move_active:
            # Outer circle
            pygame.draw.circle(screen, (100, 100, 100, 150), 
                             (int(self.move_center[0]), int(self.move_center[1])), 80, 3)
            # Inner circle (joystick position)
            if self.move_touch_pos:
                joy_x = self.move_center[0] + self.move_dir[1] * 60
                joy_y = self.move_center[1] + self.move_dir[0] * 60
                pygame.draw.circle(screen, (150, 150, 150, 200), 
                                 (int(joy_x), int(joy_y)), 35)
                pygame.draw.circle(screen, (200, 200, 200, 255), 
                                 (int(joy_x), int(joy_y)), 20)
        
        # Draw look joystick
        if self.look_center and self.look_active:
            pygame.draw.circle(screen, (100, 100, 100, 150), 
                             (int(self.look_center[0]), int(self.look_center[1])), 80, 3)
            if self.look_touch_pos:
                joy_x = self.look_center[0] + self.look_dir[0] * 60 / 0.008
                joy_y = self.look_center[1] + self.look_dir[1] * 60 / 0.008
                joy_x = max(self.look_center[0] - 70, min(self.look_center[0] + 70, joy_x))
                joy_y = max(self.look_center[1] - 70, min(self.look_center[1] + 70, joy_y))
                pygame.draw.circle(screen, (150, 150, 150, 200), 
                                 (int(joy_x), int(joy_y)), 35)
                pygame.draw.circle(screen, (200, 200, 200, 255), 
                                 (int(joy_x), int(joy_y)), 20)
        
        # Draw labels
        font = pygame.font.Font(None, 24)
        if not pygame.mouse.get_visible():
            # Instructions for mouse look mode
            text = font.render("Mouse Look ACTIVE - Click outside right zone to exit", True, (255, 255, 0))
            text_rect = text.get_rect(center=(self.screen_width//2, 50))
            screen.blit(text, text_rect)
        else:
            # Normal instructions
            text1 = font.render("LEFT ZONE: Move (click and drag)", True, (200, 200, 200))
            text2 = font.render("RIGHT ZONE: Look (click and drag) - OR - Hold Right Click anywhere", True, (200, 200, 200))
            text1_rect = text1.get_rect(center=(self.screen_width//2, 30))
            text2_rect = text2.get_rect(center=(self.screen_width//2, 55))
            screen.blit(text1, text1_rect)
            screen.blit(text2, text2_rect)

# ---------------------- SOUND ----------------------
walk_sound = None
try:
    walk_sound = pygame.mixer.Sound("walk.mp3")
    walk_sound.set_volume(0.4)
except:
    print("Could not load walk.mp3")

# ---------------------- COLORS ----------------------
CEILING_DARK = (30, 30, 30)
CEILING_LIGHT = (120, 120, 120)
FLOOR_DARK = (30, 30, 30)
FLOOR_LIGHT = (120, 120, 120)
WALL_COLOR_LIGHT = (180, 180, 180)
WALL_COLOR_DARK = (100, 100, 100)

# ---------------------- MAP ----------------------
def get_map():
    return [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,0,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]

MAP = get_map()
MAP_H, MAP_W = len(MAP), len(MAP[0])

# ---------------------- OPTIMIZED RAYCASTING ----------------------
def cast_ray(px, py, angle):
    """Single ray casting"""
    ray_dir_x = math.cos(angle)
    ray_dir_y = math.sin(angle)
    
    map_x = int(px)
    map_y = int(py)
    
    delta_dist_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else 1e30
    delta_dist_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else 1e30
    
    step_x = 1 if ray_dir_x > 0 else -1
    step_y = 1 if ray_dir_y > 0 else -1
    
    side_dist_x = (map_x + 1 - px) * delta_dist_x if ray_dir_x > 0 else (px - map_x) * delta_dist_x
    side_dist_y = (map_y + 1 - py) * delta_dist_y if ray_dir_y > 0 else (py - map_y) * delta_dist_y
    
    hit = False
    side = 0
    
    while not hit:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
            
        if map_x < 0 or map_x >= MAP_W or map_y < 0 or map_y >= MAP_H:
            return 1000.0, side
            
        if MAP[map_y][map_x] == 1:
            hit = True
            if side == 0:
                dist = side_dist_x - delta_dist_x
            else:
                dist = side_dist_y - delta_dist_y
            return dist, side
    
    return 1000.0, 0

def cast_all_rays(px, py, player_angle, fov, width):
    """Cast all rays for the screen"""
    distances = []
    sides = []
    
    for x in range(width):
        angle = player_angle - fov/2 + (x/width) * fov
        dist, side = cast_ray(px, py, angle)
        distances.append(dist)
        sides.append(side)
    
    return distances, sides

# ---------------------- RENDER FUNCTIONS ----------------------
def draw_gradient(screen, y_start, y_end, color_top, color_bottom):
    """Draw vertical gradient"""
    height = y_end - y_start
    for y in range(y_start, y_end):
        t = (y - y_start) / height if height > 0 else 0
        r = int(color_top[0] * (1-t) + color_bottom[0] * t)
        g = int(color_top[1] * (1-t) + color_bottom[1] * t)
        b = int(color_top[2] * (1-t) + color_bottom[2] * t)
        pygame.draw.line(screen, (r,g,b), (0,y), (screen.get_width(), y))

def render(screen, player_x, player_y, player_angle, player_pitch, fov, bob_offset):
    horizon_y = screen.get_height() // 2 + int(-player_pitch * 200 + bob_offset)
    
    # Draw ceiling gradient
    if horizon_y > 0:
        draw_gradient(screen, 0, min(horizon_y, screen.get_height()), CEILING_DARK, CEILING_LIGHT)
    
    # Draw floor gradient
    if horizon_y < screen.get_height():
        draw_gradient(screen, max(0, horizon_y), screen.get_height(), FLOOR_LIGHT, FLOOR_DARK)
    
    # Cast rays
    distances, sides = cast_all_rays(player_x, player_y, player_angle, fov, screen.get_width())
    
    # Draw walls
    for x in range(screen.get_width()):
        dist = distances[x]
        if dist >= 1000:
            continue
            
        side = sides[x]
        wall_height = screen.get_height() / (dist + 0.001)
        wall_top = int(horizon_y - wall_height / 2)
        wall_bottom = int(horizon_y + wall_height / 2)
        wall_top = max(0, wall_top)
        wall_bottom = min(screen.get_height(), wall_bottom)
        
        if wall_top >= wall_bottom:
            continue
        
        # Choose wall color based on side
        if side == 0:
            base_color = WALL_COLOR_LIGHT
        else:
            base_color = WALL_COLOR_DARK
        
        # Apply distance shading
        shade = max(0.3, min(1.0, 1.0 / (dist * 0.2 + 0.2)))
        color = (int(base_color[0] * shade), 
                int(base_color[1] * shade), 
                int(base_color[2] * shade))
        
        pygame.draw.line(screen, color, (x, wall_top), (x, wall_bottom - 1))

def create_flashlight(width, height):
    """Create flashlight effect surface"""
    flashlight = pygame.Surface((width, height), pygame.SRCALPHA)
    cx, cy = width // 2, height // 2
    max_dist = math.hypot(width, height) / 2.0
    
    # Optimized: draw circles instead of pixel-by-pixel
    for radius in range(0, int(max_dist), 20):
        alpha = min(200, int(200 * (radius / (max_dist * 0.8))))
        pygame.draw.circle(flashlight, (0, 0, 0, alpha), (cx, cy), radius, 2)
    
    return flashlight

# ---------------------- MAIN GAME ----------------------
def main():
    # Player
    player_x, player_y = 2.5, 12.5
    player_angle = 0.0
    player_pitch = 0.0
    player_fov = math.pi / 3
    speed = 4.0
    
    # Controls
    controls = Controls(WIDTH, HEIGHT)
    
    # Movement
    move_forward = 0
    move_strafe = 0
    
    # Walking bob
    bob_phase = 0.0
    bob_amplitude = 3.0
    bob_frequency = 12.0
    walk_timer = 0.0
    
    # Flashlight effect
    flashlight = None
    
    # Hand sprite
    hand_sprite = None
    try:
        hand_sprite = pygame.image.load("hand.png").convert_alpha()
        scale = min(0.5, WIDTH / hand_sprite.get_width())
        new_w = int(hand_sprite.get_width() * scale)
        new_h = int(hand_sprite.get_height() * scale)
        hand_sprite = pygame.transform.scale(hand_sprite, (new_w, new_h))
    except:
        print("Could not load hand.png")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt > 0.033:
            dt = 0.033
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Alternative camera control with mouse
                elif event.key == pygame.K_SPACE:
                    if not controls.mouse_look_active:
                        controls.mouse_look_active = True
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    else:
                        controls.mouse_look_active = False
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
            
            controls.handle_event(event)
        
        controls.update()
        
        # Keyboard fallback controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_forward = 1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_forward = -1
        else:
            move_forward = 0
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_strafe = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_strafe = 1
        else:
            move_strafe = 0
        
        # Use touch/mouse controls if active
        if controls.move_active:
            move_forward = controls.move_dir[0]
            move_strafe = controls.move_dir[1]
        
        if controls.look_active:
            player_angle += controls.look_dir[0]
            player_pitch += controls.look_dir[1]
            player_pitch = max(-0.8, min(0.8, player_pitch))
        
        # Movement
        if move_forward != 0:
            nx = player_x + math.cos(player_angle) * speed * move_forward * dt
            ny = player_y + math.sin(player_angle) * speed * move_forward * dt
            if 0 <= int(nx) < MAP_W and 0 <= int(ny) < MAP_H:
                if MAP[int(ny)][int(nx)] == 0:
                    player_x, player_y = nx, ny
        
        if move_strafe != 0:
            ang = player_angle + math.pi / 2
            nx = player_x + math.cos(ang) * speed * move_strafe * dt
            ny = player_y + math.sin(ang) * speed * move_strafe * dt
            if 0 <= int(nx) < MAP_W and 0 <= int(ny) < MAP_H:
                if MAP[int(ny)][int(nx)] == 0:
                    player_x, player_y = nx, ny
        
        # Footstep sound
        is_moving = (move_forward != 0 or move_strafe != 0)
        if walk_sound and is_moving:
            walk_timer -= dt
            if walk_timer <= 0:
                walk_sound.play()
                walk_timer = 0.55
        else:
            walk_timer = 0
        
        # Walking bob
        if is_moving:
            bob_phase += bob_frequency * dt
            if bob_phase > 2 * math.pi:
                bob_phase -= 2 * math.pi
        else:
            bob_phase *= 0.95
        bob_offset = math.sin(bob_phase) * bob_amplitude
        
        # Recreate flashlight if screen size changed
        current_size = screen.get_size()
        if flashlight is None or flashlight.get_size() != current_size:
            flashlight = create_flashlight(current_size[0], current_size[1])
        
        # Render
        render(screen, player_x, player_y, player_angle, player_pitch, player_fov, bob_offset)
        
        # Apply flashlight effect
        if flashlight:
            screen.blit(flashlight, (0, 0))
        
        # Draw hand sprite
        if hand_sprite:
            hand_rect = hand_sprite.get_rect(midbottom=(current_size[0]//2, current_size[1]))
            screen.blit(hand_sprite, hand_rect)
        
        # Draw crosshair
        cx, cy = current_size[0]//2, current_size[1]//2
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 4, 1)
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), 4, 1)
        
        # Draw controls UI
        controls.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()