import pygame
import random
import sys
import os
import json

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Obstacle colors and their corresponding speeds
OBSTACLE_COLORS = {
    WHITE: 3,
    CYAN: 5,
    BLUE: 7,
    GREEN: 9,
    YELLOW: 11,
    PURPLE: 13,
    RED: 15
}

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Ball Dodger")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load assets
collision_sound = pygame.mixer.Sound('collision.wav')
power_up_sound = pygame.mixer.Sound('power_up.wav')
background_music = 'bgm.wav'
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # Loop the music
heart_image = pygame.image.load('heart.png')
heart_image = pygame.transform.scale(heart_image, (30, 30))

# Font initialization
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 48)

# File paths
SETTINGS_FILE = "settings.json"
SCORES_FILE = "scores.json"

# Default settings
default_settings = {
    "player_name": "Player",
    "volume": 0.5
}

# Game variables
ball_radius = 15
ball_speed = 7
ball_speed_boost = 14
ball_speed_boost_duration = 200
obstacle_width = 50
obstacle_height = 20
power_up_width = 20
power_up_height = 20
power_up_color = YELLOW

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return default_settings.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_scores(name, score):
    scores = load_scores()
    scores.append({"name": name, "score": score})
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def create_obstacle():
    x = random.randint(0, WIDTH - obstacle_width)
    y = -obstacle_height
    color = random.choice(list(OBSTACLE_COLORS.keys()))
    speed = OBSTACLE_COLORS[color]
    return pygame.Rect(x, y, obstacle_width, obstacle_height), color, speed


def create_power_up():
    x = random.randint(0, WIDTH - power_up_width)
    y = -power_up_height
    return pygame.Rect(x, y, power_up_width, power_up_height)

def draw_3d_rect(surface, color, rect):
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, WHITE, rect, 1)

def show_settings_page():
    settings = load_settings()
    input_active = False
    input_text = settings["player_name"]
    
    running = True
    while running:
        screen.fill(BLACK)
        
        # Draw title
        title = large_font.render("Settings", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Draw player name input box
        pygame.draw.rect(screen, GRAY if not input_active else WHITE,
                        (WIDTH//2 - 200, 150, 400, 40), 2)
        
        name_label = font.render("Player Name:", True, WHITE)
        screen.blit(name_label, (WIDTH//2 - 200, 120))
        
        name_surface = font.render(input_text, True, WHITE)
        screen.blit(name_surface, (WIDTH//2 - 190, 160))
        
        # Draw high scores
        scores = load_scores()
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        score_title = font.render("High Scores", True, WHITE)
        screen.blit(score_title, (WIDTH//2 - score_title.get_width()//2, 250))
        
        y_pos = 300
        for i, score in enumerate(scores[:5]):
            score_text = font.render(f"{score['name']}: {score['score']}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, y_pos))
            y_pos += 40
        
        # Draw back button
        back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, WHITE, back_button, 2)
        back_text = font.render("Back to Game", True, WHITE)
        screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, 
                               back_button.centery - back_text.get_height()//2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_box = pygame.Rect(WIDTH//2 - 200, 150, 400, 40)
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                
                if back_button.collidepoint(event.pos):
                    if input_text.strip():
                        settings["player_name"] = input_text
                        save_settings(settings)
                    return
            
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                    if input_text.strip():
                        settings["player_name"] = input_text
                        save_settings(settings)
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 20:
                        input_text += event.unicode
        
        pygame.display.flip()
        clock.tick(60)

def show_main_menu():
    while True:
        screen.fill(BLACK)
        
        title = large_font.render("Ball Dodger", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        play_button = pygame.Rect(WIDTH//2 - 100, 250, 200, 50)
        settings_button = pygame.Rect(WIDTH//2 - 100, 320, 200, 50)
        quit_button = pygame.Rect(WIDTH//2 - 100, 390, 200, 50)
        
        pygame.draw.rect(screen, WHITE, play_button, 2)
        pygame.draw.rect(screen, WHITE, settings_button, 2)
        pygame.draw.rect(screen, WHITE, quit_button, 2)
        
        play_text = font.render("Play", True, WHITE)
        settings_text = font.render("Settings", True, WHITE)
        quit_text = font.render("Quit", True, WHITE)
        
        screen.blit(play_text, (play_button.centerx - play_text.get_width()//2,
                               play_button.centery - play_text.get_height()//2))
        screen.blit(settings_text, (settings_button.centerx - settings_text.get_width()//2,
                                  settings_button.centery - settings_text.get_height()//2))
        screen.blit(quit_text, (quit_button.centerx - quit_text.get_width()//2,
                               quit_button.centery - quit_text.get_height()//2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "play"
                elif settings_button.collidepoint(event.pos):
                    show_settings_page()
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(60)

def game_loop():
    ball_x = WIDTH // 2
    ball_y = HEIGHT - 50
    obstacles = []
    score = 0
    level = 1
    level_timer = 0
    power_up = None
    ball_speed_boost_remaining = 0
    lives = 3
    settings = load_settings()
    player_name = settings["player_name"]
    
    running = True
    paused = False

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            keys = pygame.key.get_pressed()
            current_ball_speed = ball_speed_boost if ball_speed_boost_remaining > 0 else ball_speed
            
            # Ball movement
            if keys[pygame.K_LEFT] and ball_x - ball_radius > 0:
                ball_x -= current_ball_speed
            if keys[pygame.K_RIGHT] and ball_x + ball_radius < WIDTH:
                ball_x += current_ball_speed
            if keys[pygame.K_UP] and ball_y - ball_radius > 0:
                ball_y -= current_ball_speed
            if keys[pygame.K_DOWN] and ball_y + ball_radius < HEIGHT:
                ball_y += current_ball_speed

            # Add new obstacles
            if random.randint(1, 50) == 1:
                obstacles.append(create_obstacle())

            # Add new power-up
            if power_up is None and random.randint(1, 500) == 1:
                power_up = create_power_up()

            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle[0].y += obstacle[2]
                if obstacle[0].y > HEIGHT:
                    obstacles.remove(obstacle)
                    score += obstacle[2]

            # Collision detection
            ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, 
                                  ball_radius * 2, ball_radius * 2)
            
            for obstacle in obstacles[:]:
                if ball_rect.colliderect(obstacle[0]):
                    collision_sound.play()
                    lives -= 1
                    obstacles.remove(obstacle)
                    if lives <= 0:
                        save_scores(player_name, score)
                        return

            # Handle power-up
            if power_up:
                if ball_rect.colliderect(power_up):
                    power_up_sound.play()
                    power_up = None
                    ball_speed_boost_remaining = ball_speed_boost_duration
                pygame.draw.rect(screen, power_up_color, power_up)

            # Draw game elements
            for obstacle in obstacles:
                draw_3d_rect(screen, obstacle[1], obstacle[0])

            pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), ball_radius)

            # Draw UI
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            level_text = font.render(f"Level: {level}", True, WHITE)
            screen.blit(level_text, (10, 40))
            
            name_text = font.render(f"Player: {player_name}", True, WHITE)
            screen.blit(name_text, (WIDTH - name_text.get_width() - 10, 10))

            # Draw lives
            for i in range(lives):
                screen.blit(heart_image, (10 + i * 35, HEIGHT - 40))

            # Update level
            level_timer += 1
            if level_timer >= 1000:  # Increase level every 1000 frames
                level += 1
                level_timer = 0

            if ball_speed_boost_remaining > 0:
                ball_speed_boost_remaining -= 1

        else:
            pause_text = font.render("PAUSED - Press SPACE to Continue", True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))

        pygame.display.flip()
        clock.tick(60)

def main():
    while True:
        action = show_main_menu()
        if action == "play":
            game_loop()

if __name__ == "__main__":
    main()