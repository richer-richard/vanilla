"""
Minesweeper Game Implementation
"""

import random
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class MinesweeperGame(QWidget):
    """Minesweeper game implementation"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['MINESWEEPER'][level]
        self.grid_size = config['gridSize']
        self.num_mines = config['mines']
        
        # Create grid
        self.grid = [[{'mine': False, 'revealed': False, 'flagged': False, 'adjacent_mines': 0} 
                      for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place mines
        self.place_mines()
        self.calculate_adjacent_mines()
        
        # Game state
        self.game_over = False
        self.won = False
        self.is_running = True
        self.revealed_count = 0
        self.flagged_count = 0
        self.score = 0
        
        # Setup UI
        self.setup_ui()
    
    def place_mines(self):
        """Place mines randomly on the grid"""
        placed_mines = 0
        while placed_mines < self.num_mines:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            
            if not self.grid[y][x]['mine']:
                self.grid[y][x]['mine'] = True
                placed_mines += 1
    
    def calculate_adjacent_mines(self):
        """Calculate adjacent mine count for each cell"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x]['mine']:
                    continue
                
                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.grid_size and 0 <= nx < self.grid_size:
                            if self.grid[ny][nx]['mine']:
                                count += 1
                
                self.grid[y][x]['adjacent_mines'] = count
    
    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with score and flags
        header_layout = QHBoxLayout()
        
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        self.flags_label = QLabel(f"Flags: {self.flagged_count}/{self.num_mines}")
        self.flags_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        level_label = QLabel(f"Level: {self.level}")
        level_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.score_label)
        header_layout.addWidget(self.flags_label)
        header_layout.addStretch()
        header_layout.addWidget(level_label)
        
        layout.addLayout(header_layout)
        
        # Game canvas
        layout.addStretch()
        
        # Back button
        back_btn = QPushButton("← Menu")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: linear-gradient(135deg, {Colors.PRIMARY}, {Colors.SECONDARY});
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: linear-gradient(135deg, {Colors.SECONDARY}, {Colors.PRIMARY});
            }}
        """)
        back_btn.clicked.connect(self.go_back)
        
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
        self.setMinimumSize(GAME_WIDTH, GAME_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
    
    def reveal_cell(self, x, y):
        """Reveal a cell and process game logic"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return
        
        cell = self.grid[y][x]
        
        if cell['revealed'] or cell['flagged']:
            return
        
        cell['revealed'] = True
        self.revealed_count += 1
        
        if cell['mine']:
            self.game_over = True
            self.is_running = False
            # Reveal all mines
            for row in self.grid:
                for c in row:
                    if c['mine']:
                        c['revealed'] = True
        else:
            self.score += 5
            self.score_label.setText(f"Score: {self.score}")
            
            # Auto-reveal adjacent cells if no adjacent mines
            if cell['adjacent_mines'] == 0:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                            if not self.grid[ny][nx]['revealed']:
                                self.reveal_cell(nx, ny)
        
        # Check if won
        self.check_win()
    
    def toggle_flag(self, x, y):
        """Toggle flag on a cell"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return
        
        cell = self.grid[y][x]
        
        if cell['revealed']:
            return
        
        if cell['flagged']:
            cell['flagged'] = False
            self.flagged_count -= 1
        else:
            cell['flagged'] = True
            self.flagged_count += 1
        
        self.flags_label.setText(f"Flags: {self.flagged_count}/{self.num_mines}")
    
    def check_win(self):
        """Check if player has won"""
        unrevealed_count = sum(1 for row in self.grid for c in row if not c['revealed'])
        if unrevealed_count == self.num_mines:
            self.won = True
            self.game_over = True
            self.is_running = False
            self.score += 100
            self.score_label.setText(f"Score: {self.score}")
    
    def go_back(self):
        """Go back to menu"""
        if self.on_menu_click:
            self.on_menu_click()
    
    def paintEvent(self, event):
        """Render game"""
        painter = QPainter(self)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(Colors.BLACK))
        
        # Calculate cell size and layout
        width = self.width() - 20
        height = self.height() - 100
        cell_size = min(width / self.grid_size, height / self.grid_size)
        
        offset_x = 10 + (width - cell_size * self.grid_size) // 2
        offset_y = 80 + (height - cell_size * self.grid_size) // 2
        
        # Draw grid
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell = self.grid[y][x]
                
                cell_x = int(offset_x + x * cell_size)
                cell_y = int(offset_y + y * cell_size)
                cell_w = int(cell_size)
                cell_h = int(cell_size)
                
                # Draw cell background
                if cell['revealed']:
                    if cell['mine']:
                        painter.fillRect(cell_x, cell_y, cell_w, cell_h, QColor(Colors.ERROR))
                    else:
                        painter.fillRect(cell_x, cell_y, cell_w, cell_h, QColor("#2a2a2a"))
                else:
                    painter.fillRect(cell_x, cell_y, cell_w, cell_h, QColor(Colors.PRIMARY))
                
                # Draw cell border
                painter.setPen(QPen(QColor("#1a1a1a"), 1))
                painter.drawRect(cell_x, cell_y, cell_w, cell_h)
                
                # Draw cell content
                painter.setPen(QPen(QColor(Colors.WHITE)))
                font = QFont()
                font.setPointSize(int(cell_size / 4))
                painter.setFont(font)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                
                if cell['revealed']:
                    if cell['mine']:
                        painter.drawText(cell_x, cell_y, cell_w, cell_h, 4 | 32, "💣")
                    elif cell['adjacent_mines'] > 0:
                        color = QColor(Colors.PRIMARY)
                        painter.setPen(QPen(color))
                        painter.drawText(cell_x, cell_y, cell_w, cell_h, 4 | 32, str(cell['adjacent_mines']))
                elif cell['flagged']:
                    painter.drawText(cell_x, cell_y, cell_w, cell_h, 4 | 32, "🚩")
        
        # Draw game over
        if self.game_over:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            
            if self.won:
                painter.setPen(QPen(QColor(Colors.SUCCESS)))
                painter.drawText(self.rect(), 1 | 32, "YOU WIN!")
            else:
                painter.setPen(QPen(QColor(Colors.ERROR)))
                painter.drawText(self.rect(), 1 | 32, "GAME OVER")
            
            font.setPointSize(14)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Colors.WHITE)))
            painter.drawText(
                self.rect().adjusted(0, 40, 0, 0),
                1 | 32,
                f"Final Score: {self.score}"
            )
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if self.game_over:
            return
        
        # Calculate cell coordinates
        width = self.width() - 20
        height = self.height() - 100
        cell_size = min(width / self.grid_size, height / self.grid_size)
        
        offset_x = 10 + (width - cell_size * self.grid_size) // 2
        offset_y = 80 + (height - cell_size * self.grid_size) // 2
        
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()
        
        if mouse_x < offset_x or mouse_y < offset_y:
            return
        
        x = int((mouse_x - offset_x) / cell_size)
        y = int((mouse_y - offset_y) / cell_size)
        
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return
        
        if event.button() == Qt.MouseButton.LeftButton:
            self.reveal_cell(x, y)
        elif event.button() == Qt.MouseButton.RightButton:
            self.toggle_flag(x, y)
        
        self.update()
