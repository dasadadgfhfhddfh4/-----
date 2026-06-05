import pygame
import random

# --- Constants ---
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 50
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 100

# Colors
COLOR_BG = (20, 20, 30)
COLOR_GRID = (40, 40, 60)
COLOR_EMPTY = (30, 30, 45)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (200, 0, 0)

# Shape patterns (defined as relative coordinates [(dr, dc), ...])к 
SHAPE_PATTERNS = [
    [(0, 0)],  # 1x1
    [(0, 0), (0, 1)],  # 1x2
    [(0, 0), (1, 0)],  # 2x1
    [(0, 0), (0, 1), (0, 2)],  # 1x3
    [(0, 0), (1, 0), (2, 0)],  # 3x1
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # 2x2
    [(0, 0), (0, 1), (0, 2), (0, 3)],  # 1x4
    [(0, 0), (1, 0), (2, 0), (3, 0)],  # 4x1
    [(0, 0), (1, 0), (1, 1)],  # L-small
    [(0, 0), (0, 1), (1, 1)],  # L-small inverse
    [(0, 0), (1, 0), (1, -1)], # L-small inverse 2
    [(0, 0), (0, 1), (-1, 1)], # L-small inverse 3
    [(0, 0), (1, 0), (2, 0), (2, 1)], # L-big
    [(0, 0), (0, 1), (0, 2), (1, 0)], # L-big 2
    [(0, 0), (0, 1), (0, 2), (1, 2)], # L-big 3
    [(0, 0), (1, 0), (2, 0), (0, 1)], # L-big 4
    [(0, 0), (0, 1), (1, 1), (2, 1)], # L-big 5
    [(0, 0), (1, 0), (1, 1), (1, 2)], # L-big 6
    [(0, 1), (1, 1), (2, 1), (2, 0)], # L-big 7
    [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)], # U-ish
]

SHAPE_COLORS = [
    (255, 50, 50), (50, 255, 50), (50, 50, 255), 
    (255, 255, 50), (255, 50, 255), (50, 255, 255), 
    (255, 165, 0), (128, 0, 128), (0, 255, 128)
]

class Shape:
    def __init__(self, pattern, color, index):
        self.pattern = pattern
        self.color = color
        self.index = index
        self.is_placed = False
        self.is_dragging = False
        self.pos = self._get_initial_pos()
        self.grid_pos = None # (row, col)

    def _get_initial_pos(self):
        # Position shapes at the bottom of the screen
        x_start = 60 + self.index * 140
        y_start = 500
        return pygame.Vector2(x_start, y_start)

    def draw(self, screen, scale=1.0):
        if self.is_placed:
            return
        
        # Adjust drawing size if dragging
        s = CELL_SIZE * scale if not self.is_dragging else CELL_SIZE
        for dr, dc in self.pattern:
            rect = pygame.Rect(
                self.pos.x + dc * s, 
                self.pos.y + dr * s, 
                s - 2, s - 2
            )
            pygame.draw.rect(screen, self.color, rect, border_radius=4)

    def get_rects(self, scale=1.0):
        s = CELL_SIZE * scale if not self.is_dragging else CELL_SIZE
        rects = []
        for dr, dc in self.pattern:
            rects.append(pygame.Rect(self.pos.x + dc * s, self.pos.y + dr * s, s, s))
        return rects

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Blast")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        self.grid = [[COLOR_EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.shapes = []
        self.spawn_shapes()
        
        self.dragging_shape = None
        self.game_over = False

    def spawn_shapes(self):
        # Clear old shapes that were placed
        self.shapes = [s for s in self.shapes if not s.is_placed]
        
        # Spawn until we have 3 shapes
        while len(self.shapes) < 3:
            pattern = random.choice(SHAPE_PATTERNS)
            color = random.choice(SHAPE_COLORS)
            self.shapes.append(Shape(pattern, color, len(self.shapes)))
        
        # Update indices for position
        for i, s in enumerate(self.shapes):
            s.index = i
            s.pos = s._get_initial_pos()

    def check_fit(self, shape, row, col):
        for dr, dc in shape.pattern:
            r, c = row + dr, col + dc
            if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
                return False
            if self.grid[r][c] != COLOR_EMPTY:
                return False
        return True

    def place_shape(self, shape, row, col):
        for dr, dc in shape.pattern:
            self.grid[row + dr][col + dc] = shape.color
        shape.is_placed = True
        self.score += len(shape.pattern) * 10
        self.clear_lines()
        
        if all(s.is_placed for s in self.shapes):
            self.spawn_shapes()
        else:
            # Re-index remaining shapes
            unplaced = [s for s in self.shapes if not s.is_placed]
            for i, s in enumerate(unplaced):
                s.index = i
                s.pos = s._get_initial_pos()

    def clear_lines(self):
        rows_to_clear = []
        cols_to_clear = []

        # Check rows
        for r in range(GRID_SIZE):
            if all(self.grid[r][c] != COLOR_EMPTY for c in range(GRID_SIZE)):
                rows_to_clear.append(r)
        
        # Check columns
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] != COLOR_EMPTY for r in range(GRID_SIZE)):
                cols_to_clear.append(c)

        # Clear and add score
        for r in rows_to_clear:
            for c in range(GRID_SIZE):
                self.grid[r][c] = COLOR_EMPTY
        
        for c in cols_to_clear:
            for r in range(GRID_SIZE):
                self.grid[r][c] = COLOR_EMPTY
        
        cleared = len(rows_to_clear) + len(cols_to_clear)
        if cleared > 0:
            self.score += cleared * 100

    def check_game_over(self):
        # If any remaining shape can fit anywhere on the grid, game is not over
        unplaced_shapes = [s for s in self.shapes if not s.is_placed]
        if not unplaced_shapes:
            return False # No unplaced shapes, so it's not game over (waiting for spawn)
        
        for shape in unplaced_shapes:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.check_fit(shape, r, c):
                        return False
        return True

    def run(self):
        running = True
        while running:
            self.screen.fill(COLOR_BG)
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                        # Check if we clicked a shape
                        for s in self.shapes:
                            if not s.is_placed:
                                # Check collision with shape rects (scaled down initially)
                                for rect in s.get_rects(scale=0.7):
                                    if rect.collidepoint(mouse_pos):
                                        self.dragging_shape = s
                                        s.is_dragging = True
                                        break
                            if self.dragging_shape: break

                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.dragging_shape:
                            # Determine which cell the shape is dropped into
                            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                            # Calculate grid coordinate based on the first block of the shape
                            # We assume the "anchor" is the top-left block of the pattern
                            # But it's simpler to find the closest grid cell for the anchor block
                            # Let's use the top-left block of the pattern for placement logic
                            
                            # To make it intuitive, we align the mouse to the grid
                            # The shape's first block (0,0) is what we use to anchor
                            # We find the cell that contains the anchor block
                            
                            # Offset calculation to align shape with grid
                            # shape.pos is where the anchor (0,0) is. 
                            # But while dragging, we move shape.pos.
                            # The anchor block is at shape.pos.
                            
                            # We need to translate mouse_pos to grid coordinates
                            # The (0,0) block's center is at self.dragging_shape.pos
                            # Wait, while dragging, self.dragging_shape.pos follows mouse.
                            # Let's refine dragging.
                            
                            col = int((mouse_pos.x - GRID_OFFSET_X) // CELL_SIZE)
                            row = int((mouse_pos.y - GRID_OFFSET_Y) // CELL_SIZE)
                            
                            # Snap to grid adjustment:
                            # We need to check where the anchor (0,0) would land
                            # The mouse is currently at the center of the anchor block
                            # So anchor (0,0) is at (mouse_pos.x - CELL_SIZE//2, mouse_pos.y - CELL_SIZE//2)
                            # Let's use that for the snap.
                            
                            snap_x = mouse_pos.x - CELL_SIZE // 2
                            snap_y = mouse_pos.y - CELL_SIZE // 2
                            
                            grid_col = int((snap_x - GRID_OFFSET_X) // CELL_SIZE)
                            grid_row = int((snap_y - GRID_OFFSET_Y) // CELL_SIZE)

                            if self.check_fit(self.dragging_shape, grid_row, grid_col):
                                self.place_shape(self.dragging_shape, grid_row, grid_col)
                            
                            self.dragging_shape.is_dragging = False
                            self.dragging_shape = None

            # Update dragging position
            if self.dragging_shape:
                m_pos = pygame.mouse.get_pos()
                self.dragging_shape.pos = pygame.Vector2(m_pos[0] - CELL_SIZE // 2, m_pos[1] - CELL_SIZE // 2)

            # Drawing Grid
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    rect = pygame.Rect(
                        GRID_OFFSET_X + c * CELL_SIZE, 
                        GRID_OFFSET_Y + r * CELL_SIZE, 
                        CELL_SIZE - 1, CELL_SIZE - 1
                    )
                    color = self.grid[r][c] if self.grid[r][c] != COLOR_EMPTY else COLOR_EMPTY
                    pygame.draw.rect(self.screen, color, rect, border_radius=3)

            # Drawing Preview
            if self.dragging_shape:
                m_pos = pygame.mouse.get_pos()
                snap_x = m_pos[0] - CELL_SIZE // 2
                snap_y = m_pos[1] - CELL_SIZE // 2
                grid_col = int((snap_x - GRID_OFFSET_X) // CELL_SIZE)
                grid_row = int((snap_y - GRID_OFFSET_Y) // CELL_SIZE)
                
                if 0 <= grid_row < GRID_SIZE and 0 <= grid_col < GRID_SIZE:
                    fits = self.check_fit(self.dragging_shape, grid_row, grid_col)
                    preview_color = (0, 255, 0) if fits else (255, 0, 0)
                    
                    # Semi-transparent surface for preview
                    preview_surf = pygame.Surface((CELL_SIZE - 1, CELL_SIZE - 1), pygame.SRCALPHA)
                    preview_surf.fill((*preview_color, 128))
                    
                    for dr, dc in self.dragging_shape.pattern:
                        pr = grid_row + dr
                        pc = grid_col + dc
                        if 0 <= pr < GRID_SIZE and 0 <= pc < GRID_SIZE:
                            self.screen.blit(preview_surf, (GRID_OFFSET_X + pc * CELL_SIZE, GRID_OFFSET_Y + pr * CELL_SIZE))

            # Drawing Shapes
            for s in self.shapes:
                s.draw(self.screen, scale=0.7 if not s.is_dragging else 1.0)

            # Score
            score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 40))

            if self.check_game_over():
                self.game_over = True

            if self.game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0,0))
                go_text = self.font.render("GAME OVER", True, COLOR_GAME_OVER)
                self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2))
                restart_text = self.font_small.render("Press R to Restart", True, COLOR_TEXT)
                self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.__init__()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    Game().run()