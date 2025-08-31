import pygame
import sys
import random
import os

SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

HIGHSCORE_FILE = "tetris_highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH + 150, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")
clock = pygame.time.Clock()

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

class Tetromino:
    def __init__(self):
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def valid_space(shape, offset, grid):
    off_x, off_y = offset
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                x = off_x + j
                y = off_y + i
                if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                    return False
                if grid[y][x] != BLACK:
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for y in range(GRID_HEIGHT-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(GRID_WIDTH):
                try:
                    del locked[(x, y)]
                except:
                    continue
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x, y0 = key
                if y0 < y:
                    locked[(x, y0+1)] = locked.pop((x, y0))
    return cleared

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, grid[y][x], rect)
            pygame.draw.rect(surface, GRAY, rect, 1)

def draw_tetromino(surface, tetromino):
    for i, row in enumerate(tetromino.shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((tetromino.x + j) * BLOCK_SIZE, (tetromino.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, tetromino.color, rect)
                pygame.draw.rect(surface, GRAY, rect, 1)

def draw_next_tetromino(surface, tetromino):
    font = pygame.font.SysFont("SimHei", 20)
    label = font.render("下一个方块：", True, (0,0,0))
    surface.blit(label, (SCREEN_WIDTH + 10, 30))
    for i, row in enumerate(tetromino.shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(SCREEN_WIDTH + 10 + j * BLOCK_SIZE, 60 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, tetromino.color, rect)
                pygame.draw.rect(surface, (0,0,0), rect, 1)

def try_rotate_with_wallkick(current_piece, grid):
    old_shape = current_piece.shape
    current_piece.rotate()
    # 先尝试原地旋转
    if valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
        return
    # 尝试向左移动一格
    if valid_space(current_piece.shape, (current_piece.x - 1, current_piece.y), grid):
        current_piece.x -= 1
        return
    # 尝试向右移动一格
    if valid_space(current_piece.shape, (current_piece.x + 1, current_piece.y), grid):
        current_piece.x += 1
        return
    # 都不行，恢复原状
    current_piece.shape = old_shape

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    current_piece = Tetromino()
    next_piece = Tetromino()
    change_piece = False
    fall_time = 0
    score = 0
    fall_speed = 0.15
    paused = False

    # 加载最高分
    highscore = load_highscore()
    new_high = False

    while True:
        grid = create_grid(locked_positions)
        clock.tick(60)
        if not paused:
            fall_time += clock.get_rawtime() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # 暂停/继续
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                            current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                            current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        try_rotate_with_wallkick(current_piece, grid)
                    elif event.key == pygame.K_SPACE:
                        while valid_space(current_piece.shape, (current_piece.x, current_piece.y + 1), grid):
                            current_piece.y += 1
                        change_piece = True

        if paused:
            screen.fill(WHITE)
            draw_grid(screen, grid)
            draw_tetromino(screen, current_piece)
            draw_next_tetromino(screen, next_piece)
            font = pygame.font.SysFont("SimHei", 36)
            text = font.render("已暂停，按P继续", True, (255, 0, 0))
            screen.blit(text, (30, SCREEN_HEIGHT // 2 - 50))
            font2 = pygame.font.SysFont("SimHei", 24)
            score_text = font2.render(f"得分：{score}", True, (0, 0, 0))
            screen.blit(score_text, (SCREEN_WIDTH + 10, 10))
            highscore_text = font2.render(f"最高分：{highscore}", True, (0, 0, 255))
            screen.blit(highscore_text, (SCREEN_WIDTH + 10, 40))
            pygame.display.flip()
            continue

        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                current_piece.y -= 1
                change_piece = True

        if change_piece:
            for i, row in enumerate(current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        locked_positions[(current_piece.x + j, current_piece.y + i)] = current_piece.color
            current_piece = next_piece
            next_piece = Tetromino()
            change_piece = False
            lines_cleared = clear_rows(grid, locked_positions)
            score += lines_cleared * 100
            # 判定是否破最高分
            if score > highscore:
                highscore = score
                save_highscore(highscore)
                new_high = True

            if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                font = pygame.font.SysFont("SimHei", 36)
                text = font.render("游戏结束！按R键重来", True, (255, 0, 0))
                screen.blit(text, (20, SCREEN_HEIGHT // 2 - 50))
                font2 = pygame.font.SysFont("SimHei", 24)
                highscore_text = font2.render(f"最高分：{highscore}", True, (0, 0, 255))
                screen.blit(highscore_text, (SCREEN_WIDTH + 10, 40))
                if new_high:
                    new_high_text = font2.render("新纪录！", True, (255, 0, 0))
                    screen.blit(new_high_text, (SCREEN_WIDTH + 10, 70))
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            main()

        screen.fill(WHITE)
        draw_grid(screen, grid)
        draw_tetromino(screen, current_piece)
        draw_next_tetromino(screen, next_piece)
        font = pygame.font.SysFont("SimHei", 24)
        score_text = font.render(f"得分：{score}", True, (0, 0, 0))
        screen.blit(score_text, (SCREEN_WIDTH + 10, 10))
        highscore_text = font.render(f"最高分：{highscore}", True, (0, 0, 255))
        screen.blit(highscore_text, (SCREEN_WIDTH + 10, 40))
        if new_high:
            new_high_text = font.render("新纪录！", True, (255, 0, 0))
            screen.blit(new_high_text, (SCREEN_WIDTH + 10, 70))
        pygame.display.flip()

if __name__ == "__main__":
    main()