import pygame
import random
import sys

# Initialize pygame
pygame.init()

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

# Ball properties
ball_radius = 15
ball_x = WIDTH // 2
ball_y = HEIGHT - 50
ball_speed = 7
ball_speed_boost = 14
ball_speed_boost_duration = 200  # frames
ball_speed_boost_remaining = 0

# Falling obstacles properties
obstacle_width = 50
obstacle_height = 20
obstacles = []

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Levels
level = 1
level_duration = 1000  # frames
level_timer = 0

# Power-ups
power_up_width = 20
power_up_height = 20
power_up_color = YELLOW
power_up = None

# Function to create a new obstacle
def create_obstacle():
    x = random.randint(0, WIDTH - obstacle_width)
    y = -obstacle_height
    color = random.choice(list(OBSTACLE_COLORS.keys()))
    speed = OBSTACLE_COLORS[color] + level - 1
    return pygame.Rect(x, y, obstacle_width, obstacle_height), color, speed

# Function to create a new power-up
def create_power_up():
    x = random.randint(0, WIDTH - power_up_width)
    y = random.randint(0, HEIGHT - power_up_height)
    return pygame.Rect(x, y, power_up_width, power_up_height)

# Function to draw a 3D rectangle
def draw_3d_rect(surface, color, rect):
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, WHITE, rect, 1)

# Function to check for collisions
def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# Function to show game over screen
def show_game_over_screen(score):
    screen.fill(BLACK)
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Main game loop
def main():
    global ball_x, ball_y, obstacles, WIDTH, HEIGHT, screen, score, level, level_timer, power_up, ball_speed_boost_remaining
    running = True
    paused = False

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                ball_x = min(ball_x, WIDTH - ball_radius)
                ball_y = min(ball_y, HEIGHT - ball_radius)
                obstacles = [(pygame.Rect(min(obstacle[0].x, WIDTH - obstacle_width), obstacle[0].y, obstacle_width, obstacle_height), obstacle[1], obstacle[2]) for obstacle in obstacles]
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

        if not paused:
            # Key handling
            keys = pygame.key.get_pressed()
            current_ball_speed = ball_speed_boost if ball_speed_boost_remaining > 0 else ball_speed
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

            # Move obstacles
            for obstacle in obstacles:
                obstacle[0].y += obstacle[2]
                if obstacle[0].y > HEIGHT:
                    obstacles.remove(obstacle)
                    score += obstacle[2]  # Increase score by the speed of the dodged obstacle

            # Check for collisions with obstacles
            ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
            if any(check_collision(ball_rect, obstacle[0]) for obstacle in obstacles):
                running = False  # End the game if a collision is detected

            # Check for collisions with power-up
            if power_up and check_collision(ball_rect, power_up):
                ball_speed_boost_remaining = ball_speed_boost_duration
                power_up = None

            # Draw obstacles
            for obstacle in obstacles:
                draw_3d_rect(screen, obstacle[1], obstacle[0])

            # Draw power-up
            if power_up:
                draw_3d_rect(screen, power_up_color, power_up)

            # Draw the ball
            pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

            # Draw the score
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            # Draw the level
            level_text = font.render(f"Level: {level}", True, WHITE)
            screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

            # Update level
            level_timer += 1
            if level_timer >= level_duration:
                level += 1
                level_timer = 0

            # Update ball speed boost
            if ball_speed_boost_remaining > 0:
                ball_speed_boost_remaining -= 1

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    show_game_over_screen(score)

if __name__ == "__main__":
    main()