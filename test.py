import pygame
import sys


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 700, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Atomic Samurai")
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
clock = pygame.time.Clock()
FPS = 60

PLAYER_WIDTH, PLAYER_HEIGHT = 120, 100  
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = 15
GRAVITY = 1
ATTACK_WIDTH, ATTACK_HEIGHT = 50, 30
ATTACK_DAMAGE = 5
ATTACK_COOLDOWN = 500  
DASH_SPEED = 20  
DASH_COOLDOWN = 7000  
DASH_DURATION = 100  

font = pygame.font.Font(None, 36)

def loadsheet(path, frame_count, width, height):
    
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(frame_count):
        frame = sheet.subsurface(pygame.Rect(i * width, 0, width, height))
        frames.append(frame)
    return frames

player1_animations = {
    "idle": loadsheet("idle2.png", 8, 200, 200),
    "run": loadsheet("run2.png", 8, 200, 200),
    "attack1": loadsheet("attack1_2.png", 6, 200, 200),
    "attack2": loadsheet("attack2_2.png", 6, 200, 200),
    "jump": loadsheet("jump2.png", 2, 200, 200),
    "fall": loadsheet("fall2.png", 2, 200, 200),
    "take_hit": loadsheet("take_hit2.png", 4, 200, 200),
    "death": loadsheet("death2.png", 6, 200, 200),
    "dash": loadsheet("attack1_2.png", 6, 200, 200),  
}
player2_animations = {
    "idle": loadsheet("idle.png", 8, 200, 200),
    "run": loadsheet("run.png", 8, 200, 200),
    "attack1": loadsheet("attack1.png", 6, 200, 200),
    "attack2": loadsheet("attack2.png", 6, 200, 200),
    "jump": loadsheet("jump.png", 2, 200, 200),
    "fall": loadsheet("fall.png", 2, 200, 200),
    "take_hit": loadsheet("take hit.png", 4, 200, 200),
    "death": loadsheet("death.png", 6, 200, 200),
    "dash": loadsheet("attack1.png", 6, 200, 200),  
}
attack_sound = pygame.mixer.Sound("sound.mp3")
jump_sound = pygame.mixer.Sound("daa.mp3")
game_over_sound = pygame.mixer.Sound("gameover.mp3")
dash_sound = pygame.mixer.Sound("daa.mp3") 

class Player:
    def __init__(self, x, y, width, height, animations, keys):
        self.rect = pygame.Rect(x, y, width, height)
        self.animations = animations
        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.1
        self.image = self.animations[self.state][self.frame_index]
        self.facing_right = True
        self.health = 100
        self.attacking = False
        self.velocity_y = 0
        self.on_ground = True
        self.last_attack = 0
        self.keys = keys
        self.dash_speed = DASH_SPEED
        self.dash_cooldown = DASH_COOLDOWN
        self.last_dash = 0 
        self.is_dashing = False 

    def update_animation(self):
        
        if self.state == "attack1" or self.state == "attack2" or self.state == "dash":
            self.animation_speed = 0.5  
        else:
            self.animation_speed = 0.2  

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0  
            if self.state == "death": 
                self.frame_index = len(self.animations[self.state]) - 1
        self.image = self.animations[self.state][int(self.frame_index)]

    def draw(self, screen):
        
        if self.facing_right:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            
            flipped_image = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped_image, (self.rect.x, self.rect.y))


player1 = Player(100, HEIGHT - PLAYER_HEIGHT - 50, PLAYER_WIDTH, PLAYER_HEIGHT, player1_animations, {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'jump': pygame.K_SPACE,
    'attack': pygame.K_w,
    'dash': pygame.K_s,  
})
player1.facing_right = True  

player2 = Player(WIDTH - 200, HEIGHT - PLAYER_HEIGHT - 50, PLAYER_WIDTH, PLAYER_HEIGHT, player2_animations, {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_l,
    'attack': pygame.K_UP,
    'dash': pygame.K_DOWN,  
})
player2.facing_right = False  

background = pygame.image.load("background.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
game_over = False

# Functions
def draw_health():
    
    pygame.draw.rect(screen, RED, (50, 20, player1.health * 2, 20))
    pygame.draw.rect(screen, BLUE, (WIDTH - 250, 20, player2.health * 2, 20))

    p1_health_text = font.render(f"P1: {player1.health}", True, WHITE)
    p2_health_text = font.render(f"P2: {player2.health}", True, WHITE)
    screen.blit(p1_health_text, (50, 50))
    screen.blit(p2_health_text, (WIDTH - 250, 50))

def handle_movement(player, keys):
    
    if keys[player.keys['left']]:
        player.rect.x -= PLAYER_SPEED
        player.facing_right = False
        player.state = "run"
        if player.rect.x < 0:  # Left boundary
            player.rect.x = 0
    elif keys[player.keys['right']]:
        player.rect.x += PLAYER_SPEED
        player.facing_right = True
        player.state = "run"
        if player.rect.x > WIDTH - PLAYER_WIDTH:  # Right boundary
            player.rect.x = WIDTH - PLAYER_WIDTH
    else:
        player.state = "idle"  # Reset to idle when not moving

    if keys[player.keys['jump']] and player.on_ground:
        player.velocity_y = -PLAYER_JUMP_SPEED
        player.on_ground = False
        player.state = "jump"
        jump_sound.play()

    if player.velocity_y > 0 and not player.on_ground:
        player.state = "fall"

def apply_gravity(player):
    
    player.rect.y += player.velocity_y
    player.velocity_y += GRAVITY
    if player.rect.y + PLAYER_HEIGHT >= HEIGHT - 50:
        player.rect.y = HEIGHT - PLAYER_HEIGHT - 50
        player.velocity_y = 0
        player.on_ground = True

def attacks(player, keys, current_time, target):
   
    if keys[player.keys['attack']] and current_time - player.last_attack > ATTACK_COOLDOWN:
        player.attacking = True
        player.last_attack = current_time
        player.state = "attack1"
        attack_sound.play()

        if player.facing_right:
            attack_rect = pygame.Rect(player.rect.x + PLAYER_WIDTH, player.rect.y + PLAYER_HEIGHT // 2 - ATTACK_HEIGHT // 2, ATTACK_WIDTH, ATTACK_HEIGHT)
        else:
            attack_rect = pygame.Rect(player.rect.x - ATTACK_WIDTH, player.rect.y + PLAYER_HEIGHT // 2 - ATTACK_HEIGHT // 2, ATTACK_WIDTH, ATTACK_HEIGHT)

        if attack_rect.colliderect(target.rect):
            target.health -= ATTACK_DAMAGE
            target.state = "take_hit"
    elif current_time - player.last_attack > ATTACK_COOLDOWN // 2:  
        player.attacking = False
        player.state = "idle"

def handle_dash(player, keys, current_time, target):
    
    if keys[player.keys['dash']] and current_time - player.last_dash > player.dash_cooldown:
        player.is_dashing = True
        player.last_dash = current_time
        player.state = "dash"
        player.attacking = True 
        dash_sound.play()

    if player.is_dashing:
        
        if player.facing_right:
            player.rect.x += player.dash_speed
        else:
            player.rect.x -= player.dash_speed

        
        if player.rect.colliderect(target.rect):
            target.health -= ATTACK_DAMAGE
            target.state = "take_hit"

        
        if current_time - player.last_dash > DASH_DURATION:
            player.is_dashing = False
            player.state = "idle"
            player.attacking = False

def show_game_over():
    
    screen.fill(BLACK)
    if player1.health <= 0:
        winner_text = font.render("Zorojiro Wins!", True, BLUE)
    else:
        winner_text = font.render("Mihawk Wins!", True, RED)
    
    game_over_text = font.render("GAME OVER", True, RED)
    restart_text = font.render("Press R to Restart", True, WHITE)
   
    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    
    screen.blit(winner_text, winner_rect)
    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  
                player1.health = 100
                player2.health = 100
                game_over = False

    if player1.health <= 0 or player2.health <= 0:
        game_over = True
        game_over_sound.play()

    
    if not game_over:
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        
        handle_movement(player1, keys)
        handle_movement(player2, keys)
        attacks(player1, keys, current_time, player2)
        attacks(player2, keys, current_time, player1)
        handle_dash(player1, keys, current_time, player2)
        handle_dash(player2, keys, current_time, player1)
        apply_gravity(player1)
        apply_gravity(player2)
        player1.update_animation()
        player2.update_animation()
        screen.blit(background, (0, 0))
        player1.draw(screen)
        player2.draw(screen)
        draw_health()
        pygame.display.flip()

    if game_over:
        show_game_over()

    clock.tick(FPS)