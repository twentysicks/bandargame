import displayio
import time
import random
import os
from blinka_displayio_pygamedisplay import PyGameDisplay
import pygame

# Initialize pygame for font handling
pygame.init()
FONT = pygame.font.Font(None, 20)  # Using pygame's default font

# Initialize the display
display = PyGameDisplay(width=128, height=128)

# Create the main display group
main_group = displayio.Group()
display.show(main_group)

# Asset loading
ASSET_PATH = "C:\\Users\\Lenovo\\Downloads\\bandar game"

def load_bitmap(filename):
    with open(filename, "rb") as file:
        return displayio.OnDiskBitmap(file)

# Load all game assets
background_bitmaps = [load_bitmap(os.path.join(ASSET_PATH, f"background{i}.bmp")) for i in range(4)]
monkey_right = load_bitmap(os.path.join(ASSET_PATH, "bandar0.bmp"))
monkey_left = load_bitmap(os.path.join(ASSET_PATH, "bandar1.bmp"))
banana_bitmaps = {
    "normal": load_bitmap(os.path.join(ASSET_PATH, "kela0.bmp")),
    "rotten": load_bitmap(os.path.join(ASSET_PATH, "kela1.bmp")),
    "super": load_bitmap(os.path.join(ASSET_PATH, "kela2.bmp"))
}

# Create background TileGrid
background_grid = displayio.TileGrid(
    background_bitmaps[0],
    pixel_shader=background_bitmaps[0].pixel_shader
)
main_group.append(background_grid)

# Create monkey TileGrid
monkey_grid = displayio.TileGrid(
    monkey_right,
    pixel_shader=monkey_right.pixel_shader,
    x=64,
    y=96
)
main_group.append(monkey_grid)

# Game variables
monkey_x = 64
monkey_y = 96
monkey_speed = 3
monkey_direction = "right"
hearts = 3
score = 0

banana_list = []
banana_speed = 2
banana_spawn_rate = 30

background_index = 0
frame_count = 0

game_running = False
game_over_displayed = False

# Create hearts group
hearts_group = displayio.Group()
main_group.append(hearts_group)

def update_hearts_display():
    while len(hearts_group):
        hearts_group.pop()
    
    for i in range(hearts):
        heart = displayio.Circle(x=15 + i * 15, y=15, r=5, fill=0xFF0000)
        hearts_group.append(heart)

def spawn_banana():
    banana_type = random.choices(
        ["normal", "rotten", "super"],
        weights=[60, 25, 15],
        k=1
    )[0]
    x = random.randint(0, display.width - 32)
    
    banana_grid = displayio.TileGrid(
        banana_bitmaps[banana_type],
        pixel_shader=banana_bitmaps[banana_type].pixel_shader,
        x=x,
        y=0
    )
    main_group.append(banana_grid)
    
    return {
        "type": banana_type,
        "x": x,
        "y": 0,
        "grid": banana_grid
    }

def move_bananas():
    for banana in banana_list:
        banana["y"] += banana_speed
        banana["grid"].y = int(banana["y"])

def check_collisions():
    global hearts, score, banana_speed
    for banana in banana_list[:]:
        if (banana["x"] < monkey_x + 32 and
            banana["x"] + 32 > monkey_x and
            banana["y"] < monkey_y + 32 and
            banana["y"] + 32 > monkey_y):
            
            if banana["type"] == "normal":
                score += 1
            elif banana["type"] == "rotten":
                hearts -= 1
            elif banana["type"] == "super":
                hearts = min(3, hearts + 1)
                score += 3
            
            main_group.remove(banana["grid"])
            banana_list.remove(banana)
            update_hearts_display()
    
    if score > 0 and score % 10 == 0:
        banana_speed = int(banana_speed * 1.10)

def reset_game():
    global monkey_x, monkey_y, hearts, score, banana_list, banana_speed
    global game_running, game_over_displayed
    
    monkey_x = 64
    monkey_y = 96
    monkey_grid.x = monkey_x
    hearts = 3
    score = 0
    
    for banana in banana_list:
        main_group.remove(banana["grid"])
    banana_list.clear()
    
    banana_speed = 2
    game_running = False
    game_over_displayed = False
    update_hearts_display()

# Initialize hearts display
update_hearts_display()

# Main game loop
running = True
while running:
    # Handle PyGame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    display.auto_refresh = False

    if not game_running:
        if hearts <= 0:
            if not game_over_displayed:
                text_surface = FONT.render("Game Over!", True, (255, 0, 0))
                text_rect = text_surface.get_rect(center=(display.width//2, display.height//2))
                display._pygame_display.blit(text_surface, text_rect)
                display.refresh()
                time.sleep(2)
                game_over_displayed = True
        else:
            text_surface = FONT.render("Press Space to Start", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(display.width//2, display.height//2))
            display._pygame_display.blit(text_surface, text_rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_running = True

    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and monkey_x > 0:
            monkey_x -= monkey_speed
            monkey_direction = "left"
            monkey_grid.bitmap = monkey_left
        if keys[pygame.K_RIGHT] and monkey_x < display.width - 32:
            monkey_x += monkey_speed
            monkey_direction = "right"
            monkey_grid.bitmap = monkey_right

        monkey_grid.x = int(monkey_x)

        # Spawn bananas
        if frame_count % banana_spawn_rate == 0:
            banana_list.append(spawn_banana())

        # Update bananas
        move_bananas()
        check_collisions()

        # Remove off-screen bananas
        for banana in banana_list[:]:
            if banana["y"] >= display.height:
                main_group.remove(banana["grid"])
                banana_list.remove(banana)

        # Update background animation
        if frame_count % 5 == 0:
            background_index = (background_index + 1) % len(background_bitmaps)
            background_grid.bitmap = background_bitmaps[background_index]

        # Draw score
        score_surface = FONT.render(f"Score: {score}", True, (255, 0, 0))
        display._pygame_display.blit(score_surface, (5, 5))

        if hearts <= 0:
            reset_game()

    frame_count += 1
    display.refresh()
    display.auto_refresh = True
    time.sleep(0.033)  # ~30 FPS

# Cleanup
pygame.quit()