import pygame
import random
import sys
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module
# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 20
MARGIN = 5
HEADER_HEIGHT = 50
PADDING = 10  # Padding between header and timer

def calculate_rows_cols(screen_width, screen_height, tile_size, margin, header_height):
    rows = (screen_height - header_height - 2 * margin) // tile_size
    cols = (screen_width - 2 * margin) // tile_size
    return rows, cols

ROWS, COLS = calculate_rows_cols(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MARGIN, HEADER_HEIGHT)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Mazecraft")

# Load custom font
custom_font = pygame.font.Font("minecraft-regular.ttf", 48)  # Decreased font size
small_font = pygame.font.Font("minecraft-regular.ttf", 24)  # Decreased font size

# Load images
background_image = pygame.image.load("background.png").convert()
player_image = pygame.image.load("person.png").convert_alpha()
wall_image = pygame.image.load("grass.png").convert()
end_image = pygame.image.load("endpoint.png").convert_alpha()
person_image = pygame.image.load("person.png").convert_alpha()  # Load person.png image

# Load sound effect
round_sound = pygame.mixer.Sound("mario.mp3")  # Replace with your sound file
# Load music
end_music = "end_sound.mp3"  # Replace with your music file

# Load GIF
gif_path = "c.gif"  # Replace with your GIF file

class MazeGenerator:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [["W" for _ in range(cols)] for _ in range(rows)]
        self.visited = [[False for _ in range(cols)] for _ in range(rows)]

    def generate(self, x, y):
        # Mark the current cell as a path and visited
        self.grid[y][x] = " "
        self.visited[y][x] = True

        # Define movement directions
        directions = [(0, -2), (0, 2), (2, 0), (-2, 0)]
        random.shuffle(directions)  # Randomize to create a unique maze each time

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= ny < self.rows and 0 <= nx < self.cols and not self.visited[ny][nx]:
                # Carve a path between cells
                self.grid[y + dy // 2][x + dx // 2] = " "
                self.generate(nx, ny)

    def place_end(self):
        # Randomly place the end point far from the start
        while True:
            ex, ey = random.randint(self.cols // 2, self.cols - 1), random.randint(self.rows // 2, self.rows - 1)
            if self.grid[ey][ex] == " ":
                self.grid[ey][ex] = "E"
                return

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))

    def move(self, dx, dy, walls):
        if not self.collide(dx, dy, walls):
            self.rect.x += dx
            self.rect.y += dy

    def collide(self, dx, dy, walls):
        next_rect = self.rect.move(dx, dy)
        return next_rect.collidelist(walls) != -1

# Draw the maze
def draw_maze(maze):
    walls = []
    end_rect = None
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            if tile == "W":
                wall_rect = pygame.Rect(x * TILE_SIZE + MARGIN, y * TILE_SIZE + HEADER_HEIGHT + MARGIN, TILE_SIZE, TILE_SIZE)
                walls.append(wall_rect)
                screen.blit(pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE)), wall_rect.topleft)
            elif tile == "E":
                end_rect = pygame.Rect(x * TILE_SIZE + MARGIN, y * TILE_SIZE + HEADER_HEIGHT + MARGIN, TILE_SIZE, TILE_SIZE)
                screen.blit(pygame.transform.scale(end_image, (TILE_SIZE, TILE_SIZE)), end_rect.topleft)
    return walls, end_rect

# Display round number
def display_round(level):
    screen.fill((0, 0, 0))
    round_text = custom_font.render(f"Round {level}", True, (255, 255, 255))
    screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, SCREEN_HEIGHT // 2 - round_text.get_height() // 2))
    screen.blit(pygame.transform.scale(person_image, (TILE_SIZE * 2, TILE_SIZE * 2)), (SCREEN_WIDTH // 2 - TILE_SIZE, SCREEN_HEIGHT // 2 + round_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(1000)  # Wait for 1 second

# Display GIF as background with text
def display_gif_with_text(gif_path, text, duration):
    clip = VideoFileClip(gif_path)
    clip = clip.subclip(0, duration)
    pygame.mixer.music.load(end_music)
    pygame.mixer.music.play()
    start_time = pygame.time.get_ticks()
    while pygame.mixer.music.get_busy():
        screen.fill((0, 0, 0))
        final_text = custom_font.render(text, True, (255, 0, 0))
        screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, SCREEN_HEIGHT // 2 - final_text.get_height() // 2))
        pygame.display.flip()
        clip.preview()
        pygame.time.wait(100)

# Main game loop
def main():
    clock = pygame.time.Clock()
    maze_gen = MazeGenerator(ROWS, COLS)
    level = 1
    start_ticks = pygame.time.get_ticks()

    # Generate initial maze
    maze_gen.generate(1, 1)
    maze_gen.place_end()
    player = Player(TILE_SIZE + MARGIN, TILE_SIZE + HEADER_HEIGHT + MARGIN)  # Start at entrance (1, 1) in grid

    while True:
        screen.blit(background_image, (0, 0))
        walls, end_rect = draw_maze(maze_gen.grid)

        # Draw header
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))
        header_text = custom_font.render(f"Mazecraft - Level {level}", True, (57, 255, 20))  # Neon green color
        screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, HEADER_HEIGHT // 2 - header_text.get_height() // 2))

        # Timer
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_text = small_font.render(f"Time: {seconds}s", True, (0, 0, 0))  # Black color
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, HEADER_HEIGHT + PADDING))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-TILE_SIZE, 0, walls)
        if keys[pygame.K_RIGHT]:
            player.move(TILE_SIZE, 0, walls)
        if keys[pygame.K_UP]:
            player.move(0, -TILE_SIZE, walls)
        if keys[pygame.K_DOWN]:
            player.move(0, TILE_SIZE, walls)

        screen.blit(player.image, player.rect.topleft)

        # Check if player reaches the end
        if player.rect.colliderect(end_rect):
            round_sound.play()  # Play sound effect immediately
            if level < 10:
                level += 1
                display_round(level)  # Display the round number
                maze_gen = MazeGenerator(ROWS, COLS)
                maze_gen.generate(1, 1)
                maze_gen.place_end()
                player.rect.topleft = (TILE_SIZE + MARGIN, TILE_SIZE + HEADER_HEIGHT + MARGIN)  # Reset player position
                start_ticks = pygame.time.get_ticks()  # Reset timer
            else:
                # Display final message with animation
                total_time = (pygame.time.get_ticks() - start_ticks) // 1000
                final_text = custom_font.render(f"Total Time Wasted: {total_time}s\nWasted your time successfully", True, (255, 0, 0))
                screen.fill((0, 0, 0))
                screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, SCREEN_HEIGHT // 2 - final_text.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(2000)  # Display the text for 2 seconds
                display_gif_with_text(gif_path, f"Total Time Wasted: {total_time}s\n, 10")  # Display the GIF and text for 10 seconds
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
