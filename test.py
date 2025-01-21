import pygame
import random

pygame.init()

# Window setup
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dodge Ball")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)  # Dodgeball color
green = (0, 255, 0)  # Player's ball
blue = (0, 0, 255)   # Enemy's ball

# Ball class
class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y

    def draw(self):
        pygame.draw.circle(screen, red, (self.x, self.y), self.radius)

# Player class
class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 0
        self.speed_y = 0

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed_x
        elif direction == "right":
            self.x += self.speed_x
        if direction == "up":
            self.y -= self.speed_y
        elif direction == "down":
            self.y += self.speed_y


# Game loop
running = True
balls = []  
players = [Player(100, 100, 5)] # Initial player position and speed

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle Player movement (Update Player positions)
    for player in players:
        keys = pygame.key.get_pressed()  
        if keys[pygame.K_LEFT]:
            player.move("left") 
        elif keys[pygame.K_RIGHT]:
            player.move("right")   
        elif keys[pygame.K_UP]:
            player.move("up")    
        elif keys[pygame.K_DOWN]:
            player.move("down")

    # Update ball positions and movements
    for ball in balls:
        ball.draw()  # Draw the ball

    # Clear the screen 
    screen.fill(white) # Fill screen with white color

    # Update the display 
    pygame.display.update()


pygame.quit()
