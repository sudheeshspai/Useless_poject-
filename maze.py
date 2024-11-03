import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 20
PLAYER_COLOR = (0, 128, 255)
WALL_COLOR = (0, 0, 0)
END_COLOR = (0, 255, 0)
FONT_COLOR = (255, 0, 0)
MARGIN = 5
HEADER_HEIGHT = 50
ROWS, COLS = (SCREEN_HEIGHT - HEADER_HEIGHT - 2 * MARGIN) // TILE_SIZE, (SCREEN_WIDTH - 2 * MARGIN) // TILE_SIZE

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Game")

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
                return ex, ey

# Player class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

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
                pygame.draw.rect(screen, WALL_COLOR, wall_rect)
            elif tile == "E":
                end_rect = pygame.Rect(x * TILE_SIZE + MARGIN, y * TILE_SIZE + HEADER_HEIGHT + MARGIN, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, END_COLOR, end_rect)
    return walls, end_rect

# Main game loop
def main():
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)
    maze_gen = MazeGenerator(ROWS, COLS)

    # Generate initial maze
    maze_gen.generate(1, 1)
    end_x, end_y = maze_gen.place_end()
    player = Player(TILE_SIZE + MARGIN, TILE_SIZE + HEADER_HEIGHT + MARGIN)  # Start at entrance (1, 1) in grid

    while True:
        screen.fill((255, 255, 255))
        walls, end_rect = draw_maze(maze_gen.grid)

        # Draw header
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))
        header_text = font.render("Maze Game", True, FONT_COLOR)
        screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, HEADER_HEIGHT // 2 - header_text.get_height() // 2))

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

        pygame.draw.rect(screen, PLAYER_COLOR, player.rect)

        # Check if player reaches the end
        if player.rect.colliderect(end_rect):
            # Generate a new maze on completion
            maze_gen = MazeGenerator(ROWS, COLS)
            maze_gen.generate(1, 1)
            end_x, end_y = maze_gen.place_end()
            player.rect.topleft = (TILE_SIZE + MARGIN, TILE_SIZE + HEADER_HEIGHT + MARGIN)  # Reset player position

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
