import pygame
import sys
import random
import heapq
from tkinter import Tk, filedialog

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
GRID_SIZE = 4
TILE_SIZE = 400 // GRID_SIZE
FPS = 30
HINT_SIZE = (200, 200)

# Colors
BACKGROUND_COLOR = (30, 30, 30)
TILE_BORDER_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
HINT_TEXT_COLOR = (200, 200, 200)
WIN_FRAME_COLOR = (50, 205, 50)

# Setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Image Slide Puzzle")
clock = pygame.time.Clock()

# Global variable for the image
IMAGE = None
HINT_IMAGE = None

# A* Solver Functions
def manhattan_distance(grid):
    """Calculate the Manhattan Distance for the grid."""
    distance = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = grid[row][col]
            if value != 0:
                target_row = (value - 1) // GRID_SIZE
                target_col = (value - 1) % GRID_SIZE
                distance += abs(row - target_row) + abs(col - target_col)
    return distance

def get_neighbors(grid, empty_pos):
    """Generate all valid neighbor states."""
    neighbors = []
    empty_row, empty_col = empty_pos
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    for dr, dc in moves:
        new_row, new_col = empty_row + dr, empty_col + dc
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            new_grid = [row[:] for row in grid]
            new_grid[empty_row][empty_col], new_grid[new_row][new_col] = new_grid[new_row][new_col], new_grid[empty_row][empty_col]
            neighbors.append((new_grid, (new_row, new_col), (dr, dc)))
    return neighbors

def a_star_solver(start_grid):
    """Solve the puzzle using the A* algorithm."""
    empty_pos = get_empty_pos(start_grid)
    open_set = []
    heapq.heappush(open_set, (manhattan_distance(start_grid), 0, start_grid, [], empty_pos))
    visited = set()

    while open_set:
        _, g, current, path, empty_pos = heapq.heappop(open_set)
        state_str = str(current)
        if state_str in visited:
            continue
        visited.add(state_str)

        if is_solved(current):
            return path

        for neighbor, new_empty_pos, move in get_neighbors(current, empty_pos):
            heapq.heappush(
                open_set,
                (g + 1 + manhattan_distance(neighbor), g + 1, neighbor, path + [move], new_empty_pos),
            )
    return []

# Puzzle Functions
def create_puzzle():
    tiles = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]
    while True:
        random.shuffle(tiles)
        grid = [tiles[i:i + GRID_SIZE] for i in range(0, len(tiles), GRID_SIZE)]
        if is_solvable(grid) and not is_solved(grid):
            return grid

def is_solvable(grid):
    tiles = [tile for row in grid for tile in row if tile != 0]
    inversions = sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles)) if tiles[i] > tiles[j])
    empty_row = GRID_SIZE - next(row for row in range(GRID_SIZE) if 0 in grid[row])
    if GRID_SIZE % 2 == 1:
        return inversions % 2 == 0
    return (inversions + empty_row) % 2 == 0

def draw_grid(grid):
    screen.fill(BACKGROUND_COLOR)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = grid[row][col]
            if value != 0:
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                src_x = ((value - 1) % GRID_SIZE) * TILE_SIZE
                src_y = ((value - 1) // GRID_SIZE) * TILE_SIZE
                src_rect = pygame.Rect(src_x, src_y, TILE_SIZE, TILE_SIZE)
                screen.blit(IMAGE, rect, src_rect)
                pygame.draw.rect(screen, TILE_BORDER_COLOR, rect, 2)

    # Draw the hint image
    hint_rect = pygame.Rect(420, 50, *HINT_SIZE)
    screen.blit(HINT_IMAGE, hint_rect)

    # Draw text over the hint image
    font = pygame.font.Font(None, 24)
    hint_text = "Hint Image"
    instructions = "Use Arrow Keys to move tiles"
    hint_text_surface = font.render(hint_text, True, HINT_TEXT_COLOR)
    instructions_surface = font.render(instructions, True, HINT_TEXT_COLOR)
    hint_text_rect = hint_text_surface.get_rect(center=(520, 30))
    instructions_rect = instructions_surface.get_rect(center=(520, 260))
    screen.blit(hint_text_surface, hint_text_rect)
    screen.blit(instructions_surface, instructions_rect)

def get_empty_pos(grid):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 0:
                return row, col

def move_tile(grid, empty_row, empty_col, new_row, new_col):
    grid[empty_row][empty_col], grid[new_row][new_col] = grid[new_row][new_col], grid[empty_row][empty_col]

def is_solved(grid):
    count = 1
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if row == GRID_SIZE - 1 and col == GRID_SIZE - 1:
                return grid[row][col] == 0
            if grid[row][col] != count:
                return False
            count += 1
    return True

def display_winning_message():
    font = pygame.font.Font(None, 72)
    text = font.render("You Win!", True, TEXT_COLOR)
    text_rect = text.get_rect(center=(200, 200))

    # Draw a frame around the winning message
    frame_rect = pygame.Rect(50, 50, 300, 300)
    pygame.draw.rect(screen, WIN_FRAME_COLOR, frame_rect, 5)

    screen.fill(BACKGROUND_COLOR)
    screen.blit(text, text_rect)
    pygame.draw.rect(screen, WIN_FRAME_COLOR, frame_rect, 5)
    pygame.display.flip()
    pygame.time.wait(3000)

# File Picker Function
def choose_image():
    root = Tk()
    root.withdraw()  # Hide the main tkinter window
    root.attributes('-topmost', True)  # Bring the file dialog to the front
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], title="Select an Image for the Puzzle")
    root.destroy()
    return file_path

# Main Game Loop
def main():
    global IMAGE, HINT_IMAGE

    # Let the user choose an image
    image_path = choose_image()
    if not image_path:
        print("No image selected. Exiting.")
        pygame.quit()
        sys.exit()

    try:
        IMAGE = pygame.image.load(image_path)
        IMAGE = pygame.transform.scale(IMAGE, (400, 400))
        HINT_IMAGE = pygame.transform.scale(IMAGE, HINT_SIZE)  # Create a smaller hint version
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.quit()
        sys.exit()

    grid = create_puzzle()
    solver_moves = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                empty_row, empty_col = get_empty_pos(grid)
                if event.key == pygame.K_UP:
                    move_tile(grid, empty_row, empty_col, empty_row + 1, empty_col)
                elif event.key == pygame.K_DOWN:
                    move_tile(grid, empty_row, empty_col, empty_row - 1, empty_col)
                elif event.key == pygame.K_LEFT:
                    move_tile(grid, empty_row, empty_col, empty_row, empty_col + 1)
                elif event.key == pygame.K_RIGHT:
                    move_tile(grid, empty_row, empty_col, empty_row, empty_col - 1)
                elif event.key == pygame.K_s:
                    solver_moves = a_star_solver(grid)

                if is_solved(grid):
                    draw_grid(grid)
                    pygame.display.flip()
                    display_winning_message()
                    running = False

        if solver_moves:
            move = solver_moves.pop(0)
            empty_row, empty_col = get_empty_pos(grid)
            move_tile(grid, empty_row, empty_col, empty_row + move[0], empty_col + move[1])

        draw_grid(grid)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
