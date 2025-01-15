import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
RED     = (255, 0, 0)
BLUE    = (0, 0, 255)
GREEN   = (0, 255, 0)
YELLOW  = (255, 255, 0)
PURPLE  = (128, 0, 128)
CYAN    = (0, 255, 255)

# Some extra appealing colors for our D-Pad
DPAD_FILL      = (80, 80, 80)    # Dark gray fill
DPAD_OUTLINE   = (150, 150, 150) # Lighter gray outline
DPAD_HIGHLIGHT = (120, 120, 120) # Slightly lighter gray for highlight

# Obstacle colors and their corresponding speeds
OBSTACLE_COLORS = {
    WHITE:  3,
    CYAN:   5,
    BLUE:   7,
    GREEN:  9,
    YELLOW: 11,
    PURPLE: 13,
    RED:    15
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

# --------------------------------------------------------
# Create a new obstacle
# --------------------------------------------------------
def create_obstacle():
    x = random.randint(0, WIDTH - obstacle_width)
    y = -obstacle_height
    color = random.choice(list(OBSTACLE_COLORS.keys()))
    speed = OBSTACLE_COLORS[color] + level - 1
    return pygame.Rect(x, y, obstacle_width, obstacle_height), color, speed

# --------------------------------------------------------
# Create a new power-up
# --------------------------------------------------------
def create_power_up():
    x = random.randint(0, WIDTH - power_up_width)
    y = random.randint(0, HEIGHT - power_up_height)
    return pygame.Rect(x, y, power_up_width, power_up_height)

# --------------------------------------------------------
# Draw a 3D rectangle
# --------------------------------------------------------
def draw_3d_rect(surface, color, rect):
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, WHITE, rect, 1)

# --------------------------------------------------------
# Check for collisions
# --------------------------------------------------------
def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# --------------------------------------------------------
# Show game over screen
# --------------------------------------------------------
def show_game_over_screen(score):
    screen.fill(BLACK)
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(
        game_over_text,
        (WIDTH // 2 - game_over_text.get_width() // 2,
         HEIGHT // 2 - game_over_text.get_height() // 2)
    )
    screen.blit(
        score_text,
        (WIDTH // 2 - score_text.get_width() // 2,
         HEIGHT // 2 + game_over_text.get_height() // 2)
    )
    pygame.display.flip()
    pygame.time.wait(3000)

# --------------------------------------------------------
# Main game loop
# --------------------------------------------------------
def main():
    global ball_x, ball_y, obstacles, WIDTH, HEIGHT, screen
    global score, level, level_timer, power_up, ball_speed_boost_remaining

    running = True
    paused = False

    # We’ll define our D-Pad position relative to bottom-left corner
    # The 'center' of the d-pad diamond:
    dpad_center_x = 100
    dpad_center_y = HEIGHT - 100
    arrow_size = 40  # Half the distance from center to tip of each arrow

    # 1) Define polygons for drawing each arrow
    #    We want a diamond shape:
    #
    #        [Up]
    #          |
    #    [Left]-[Center]-[Right]
    #          |
    #        [Down]
    #
    # 2) We also define bounding rects for collision detection
    #
    # Up arrow points
    up_arrow_poly = [
        (dpad_center_x,             dpad_center_y - arrow_size),
        (dpad_center_x - arrow_size // 2, dpad_center_y),
        (dpad_center_x + arrow_size // 2, dpad_center_y)
    ]
    # Left arrow points
    left_arrow_poly = [
        (dpad_center_x - arrow_size,             dpad_center_y),
        (dpad_center_x,                         dpad_center_y - arrow_size // 2),
        (dpad_center_x,                         dpad_center_y + arrow_size // 2)
    ]
    # Right arrow points
    right_arrow_poly = [
        (dpad_center_x + arrow_size,             dpad_center_y),
        (dpad_center_x,                         dpad_center_y - arrow_size // 2),
        (dpad_center_x,                         dpad_center_y + arrow_size // 2)
    ]
    # Down arrow points
    down_arrow_poly = [
        (dpad_center_x,             dpad_center_y + arrow_size),
        (dpad_center_x - arrow_size // 2, dpad_center_y),
        (dpad_center_x + arrow_size // 2, dpad_center_y)
    ]

    # Bounding rects (simple squares around each arrow)
    # They won't match the diamond exactly, but it’s a quick, efficient approach.
    up_arrow_rect = pygame.Rect(
        dpad_center_x - arrow_size // 2, 
        dpad_center_y - arrow_size, 
        arrow_size, 
        arrow_size
    )
    left_arrow_rect = pygame.Rect(
        dpad_center_x - arrow_size, 
        dpad_center_y - arrow_size // 2, 
        arrow_size, 
        arrow_size
    )
    right_arrow_rect = pygame.Rect(
        dpad_center_x, 
        dpad_center_y - arrow_size // 2, 
        arrow_size, 
        arrow_size
    )
    down_arrow_rect = pygame.Rect(
        dpad_center_x - arrow_size // 2, 
        dpad_center_y, 
        arrow_size, 
        arrow_size
    )

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                ball_x = min(ball_x, WIDTH - ball_radius)
                ball_y = min(ball_y, HEIGHT - ball_radius)

                # Reposition the D-Pad on resize (keep it in bottom-left)
                dpad_center_x = 100
                dpad_center_y = HEIGHT - 100

                # Update bounding rect positions
                up_arrow_rect.x = dpad_center_x - arrow_size // 2
                up_arrow_rect.y = dpad_center_y - arrow_size
                left_arrow_rect.x = dpad_center_x - arrow_size
                left_arrow_rect.y = dpad_center_y - arrow_size // 2
                right_arrow_rect.x = dpad_center_x
                right_arrow_rect.y = dpad_center_y - arrow_size // 2
                down_arrow_rect.x = dpad_center_x - arrow_size // 2
                down_arrow_rect.y = dpad_center_y

                # Shift any obstacles if they are out of screen bounds
                new_obstacles = []
                for obst in obstacles:
                    rect, c, spd = obst
                    new_x = min(rect.x, WIDTH - obstacle_width)
                    new_rect = pygame.Rect(new_x, rect.y, obstacle_width, obstacle_height)
                    new_obstacles.append((new_rect, c, spd))
                obstacles = new_obstacles

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

            # Handle mouse/touch input
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                current_speed = ball_speed_boost if ball_speed_boost_remaining > 0 else ball_speed

                # Up
                if up_arrow_rect.collidepoint(mx, my):
                    ball_y = max(ball_radius, ball_y - current_speed)
                # Left
                elif left_arrow_rect.collidepoint(mx, my):
                    ball_x = max(ball_radius, ball_x - current_speed)
                # Right
                elif right_arrow_rect.collidepoint(mx, my):
                    ball_x = min(WIDTH - ball_radius, ball_x + current_speed)
                # Down
                elif down_arrow_rect.collidepoint(mx, my):
                    ball_y = min(HEIGHT - ball_radius, ball_y + current_speed)

        if not paused:
            # Add new obstacles randomly
            if random.randint(1, 50) == 1:
                obstacles.append(create_obstacle())

            # Add new power-up randomly
            if power_up is None and random.randint(1, 500) == 1:
                power_up = create_power_up()

            # Move obstacles
            for obstacle in obstacles[:]:
                obstacle[0].y += obstacle[2]
                if obstacle[0].y > HEIGHT:
                    obstacles.remove(obstacle)
                    score += obstacle[2]  # Increase score by the speed of the dodged obstacle

            # Check for collisions with obstacles
            ball_rect = pygame.Rect(
                ball_x - ball_radius,
                ball_y - ball_radius,
                ball_radius * 2,
                ball_radius * 2
            )
            if any(check_collision(ball_rect, obst[0]) for obst in obstacles):
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

            # --------------------------------------------------------
            # Draw our fancy D-Pad
            # --------------------------------------------------------
            # Up arrow
            pygame.draw.polygon(screen, DPAD_FILL, [
                (dpad_center_x,             dpad_center_y - arrow_size),
                (dpad_center_x - arrow_size // 2, dpad_center_y),
                (dpad_center_x + arrow_size // 2, dpad_center_y)
            ])
            pygame.draw.polygon(screen, DPAD_OUTLINE, [
                (dpad_center_x,             dpad_center_y - arrow_size),
                (dpad_center_x - arrow_size // 2, dpad_center_y),
                (dpad_center_x + arrow_size // 2, dpad_center_y)
            ], width=2)

            # Left arrow
            pygame.draw.polygon(screen, DPAD_FILL, [
                (dpad_center_x - arrow_size,             dpad_center_y),
                (dpad_center_x,                         dpad_center_y - arrow_size // 2),
                (dpad_center_x,                         dpad_center_y + arrow_size // 2)
            ])
            pygame.draw.polygon(screen, DPAD_OUTLINE, [
                (dpad_center_x - arrow_size,             dpad_center_y),
                (dpad_center_x,                         dpad_center_y - arrow_size // 2),
                (dpad_center_x,                         dpad_center_y + arrow_size // 2)
            ], width=2)

            # Right arrow
            pygame.draw.polygon(screen, DPAD_FILL, [
                (dpad_center_x + arrow_size,             dpad_center_y),
                (dpad_center_x,                         dpad_center_y - arrow_size // 2),
                (dpad_center_x,                         dpad_center_y + arrow_size // 2)
            ])
            pygame.draw.polygon(screen, DPAD_OUTLINE, [
                (dpad_center_x + arrow_size,             dpad_center_y),
                (dpad_center_x,                         dpad_center_y - arrow_size // 2),
                (dpad_center_x,                         dpad_center_y + arrow_size // 2)
            ], width=2)

            # Down arrow
            pygame.draw.polygon(screen, DPAD_FILL, [
                (dpad_center_x,             dpad_center_y + arrow_size),
                (dpad_center_x - arrow_size // 2, dpad_center_y),
                (dpad_center_x + arrow_size // 2, dpad_center_y)
            ])
            pygame.draw.polygon(screen, DPAD_OUTLINE, [
                (dpad_center_x,             dpad_center_y + arrow_size),
                (dpad_center_x - arrow_size // 2, dpad_center_y),
                (dpad_center_x + arrow_size // 2, dpad_center_y)
            ], width=2)

        # Flip the display
        pygame.display.flip()
        clock.tick(60)

    show_game_over_screen(score)


if __name__ == "__main__":
    main()
