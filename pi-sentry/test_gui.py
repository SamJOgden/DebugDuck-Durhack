import pygame
import os

# --- Setup ---
# Set DISPLAY for SSH sessions
os.environ['DISPLAY'] = ':0'

pygame.init()

# Set a windowed size (7" screen is typically 800x480)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Debug Duck GUI Test")

# --- Load Assets ---
try:
    duck_image = pygame.image.load("assets/animations/duck_neutral.png")
    # Scale the image
    duck_image = pygame.transform.scale(duck_image, (400, 400))
    print("Image loaded successfully.")
except FileNotFoundError:
    print("Error: 'duck_neutral.png' not found in assets/animations folder.")
    pygame.quit()
    exit()

# --- Main Loop ---
running = True
print("Pygame loop starting. Look at your 7\" screen!")
print("Press 'q' or tap the window to quit.")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("QUIT event received")
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            print("Q key pressed")
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Mouse clicked")
            running = False

    # Draw a black background
    screen.fill((0, 0, 0))

    # Draw the duck in the center
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    duck_rect = duck_image.get_rect(center=(center_x, center_y))
    screen.blit(duck_image, duck_rect)

    # Update the display
    pygame.display.flip()

pygame.quit()
print("GUI test finished.")