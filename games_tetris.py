"""
Tetris Game Implementation
"""

import random
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


# Tetromino shapes
TETROMINOES = [
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 0, 0], [1, 1, 1]],  # J
    [[1, 1], [1, 1]],         # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1, 1]],           # I
    [[1, 1, 1], [0, 1, 0]]   # T
]

TETRIS_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BD7AF7']


class TetrisGame(QWidget):
    """Tetris game implementation"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['TETRIS'][level]
        self.grid_width = config['gridWidth']
        self.grid_height = config['gridHeight']
        self.drop_speed = config['dropSpeed']
        self.score_per_line = config['scorePerLine']
        
        # Game state
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = None
        self.next_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.is_running = True
        
        # Game loop timer
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.drop_timer = QTimer()
        self.drop_timer.timeout.connect(self.drop_piece)
        
        # Setup UI
        self.setup_ui()
        
        # Initialize first piece
        self.spawn_new_piece()
    
    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with score and level
        header_layout = QHBoxLayout()
        
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        self.lines_label = QLabel(f"Lines: {self.lines_cleared}")
        self.lines_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        level_label = QLabel(f"Level: {self.level}")
        level_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.score_label)
        header_layout.addWidget(self.lines_label)
        header_layout.addStretch()
        header_layout.addWidget(level_label)
        
        layout.addLayout(header_layout)
        
        # Game canvas (this widget itself)
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
    
    def start(self):
        """Start the game"""
        self.game_timer.start(FRAME_TIME)
        self.drop_timer.start(self.drop_speed)
    
    def stop(self):
        """Stop the game"""
        self.game_timer.stop()
        self.drop_timer.stop()
    
    def rotate_piece(self, piece):
        """Rotate a tetromino 90 degrees clockwise"""
        n = len(piece)
        m = len(piece[0])
        rotated = [[0 for _ in range(n)] for _ in range(m)]
        for i in range(n):
            for j in range(m):
                rotated[j][n - 1 - i] = piece[i][j]
        return rotated
    
    def can_place(self, piece, x, y):
        """Check if piece can be placed at given position"""
        for i in range(len(piece)):
            for j in range(len(piece[0])):
                if piece[i][j]:
                    new_x = x + j
                    new_y = y + i
                    
                    if new_x < 0 or new_x >= self.grid_width or new_y >= self.grid_height:
                        return False
                    
                    if new_y >= 0 and self.grid[new_y][new_x] != 0:
                        return False
        return True
    
    def spawn_new_piece(self):
        """Spawn a new tetromino"""
        if self.next_piece is None:
            self.next_piece = TETROMINOES[random.randint(0, len(TETROMINOES) - 1)]
        
        self.current_piece = self.next_piece
        self.next_piece = TETROMINOES[random.randint(0, len(TETROMINOES) - 1)]
        self.current_x = self.grid_width // 2 - 1
        self.current_y = 0
        self.current_rotation = 0
        
        if not self.can_place(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            self.is_running = False
            self.stop()
    
    def place_piece(self):
        """Place current piece in the grid"""
        color_index = TETROMINOES.index(self.current_piece) % len(TETRIS_COLORS)
        
        for i in range(len(self.current_piece)):
            for j in range(len(self.current_piece[0])):
                if self.current_piece[i][j]:
                    grid_x = self.current_x + j
                    grid_y = self.current_y + i
                    
                    if 0 <= grid_y < self.grid_height and 0 <= grid_x < self.grid_width:
                        self.grid[grid_y][grid_x] = color_index + 1
        
        self.clear_lines()
        self.spawn_new_piece()
    
    def clear_lines(self):
        """Clear completed lines"""
        lines_to_clear = []
        
        for i in range(self.grid_height - 1, -1, -1):
            if all(cell != 0 for cell in self.grid[i]):
                lines_to_clear.append(i)
        
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [0 for _ in range(self.grid_width)])
        
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * self.score_per_line
            self.score_label.setText(f"Score: {self.score}")
            self.lines_label.setText(f"Lines: {self.lines_cleared}")
    
    def drop_piece(self):
        """Drop piece by one row"""
        if not self.is_running or self.game_over:
            return
        
        if self.can_place(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
        else:
            self.place_piece()
    
    def update_game(self):
        """Update game state and render"""
        self.update()
    
    def go_back(self):
        """Go back to menu"""
        self.stop()
        if self.on_menu_click:
            self.on_menu_click()
    
    def paintEvent(self, event):
        """Render game"""
        painter = QPainter(self)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(Colors.BLACK))
        
        # Calculate layout
        width = self.width()
        height = self.height() - 80
        cell_size = min(width / self.grid_width, height / self.grid_height)
        
        game_x = 10
        game_y = 80
        grid_width_px = int(self.grid_width * cell_size)
        grid_height_px = int(self.grid_height * cell_size)
        
        # Draw grid background
        painter.fillRect(
            game_x, game_y,
            grid_width_px, grid_height_px,
            QColor("#1a1a1a")
        )
        
        # Draw placed cells
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                cell_value = self.grid[i][j]
                
                if cell_value > 0:
                    painter.fillRect(
                        int(game_x + j * cell_size + 1),
                        int(game_y + i * cell_size + 1),
                        int(cell_size - 2),
                        int(cell_size - 2),
                        QColor(TETRIS_COLORS[cell_value - 1])
                    )
                
                painter.setPen(QPen(QColor("#333333")))
                painter.drawRect(
                    int(game_x + j * cell_size + 1),
                    int(game_y + i * cell_size + 1),
                    int(cell_size - 2),
                    int(cell_size - 2)
                )
        
        # Draw current piece
        if self.current_piece:
            color_index = TETROMINOES.index(self.current_piece) % len(TETRIS_COLORS)
            
            for i in range(len(self.current_piece)):
                for j in range(len(self.current_piece[0])):
                    if self.current_piece[i][j]:
                        grid_x = self.current_x + j
                        grid_y = self.current_y + i
                        
                        if 0 <= grid_y < self.grid_height:
                            painter.fillRect(
                                int(game_x + grid_x * cell_size + 1),
                                int(game_y + grid_y * cell_size + 1),
                                int(cell_size - 2),
                                int(cell_size - 2),
                                QColor(TETRIS_COLORS[color_index])
                            )
                            
                            painter.setPen(QPen(QColor("white")))
                            painter.drawRect(
                                int(game_x + grid_x * cell_size + 1),
                                int(game_y + grid_y * cell_size + 1),
                                int(cell_size - 2),
                                int(cell_size - 2)
                            )
        
        # Draw game over
        if self.game_over:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
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
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.isAutoRepeat() or not self.is_running or self.game_over:
            return
        
        key = event.key()
        
        if key == Qt.Key.Key_Left or key == Qt.Key.Key_A:
            if self.can_place(self.current_piece, self.current_x - 1, self.current_y):
                self.current_x -= 1
        elif key == Qt.Key.Key_Right or key == Qt.Key.Key_D:
            if self.can_place(self.current_piece, self.current_x + 1, self.current_y):
                self.current_x += 1
        elif key == Qt.Key.Key_Down or key == Qt.Key.Key_S:
            if self.can_place(self.current_piece, self.current_x, self.current_y + 1):
                self.current_y += 1
        elif key == Qt.Key.Key_Space or key == Qt.Key.Key_Up or key == Qt.Key.Key_W:
            rotated = self.rotate_piece(self.current_piece)
            if self.can_place(rotated, self.current_x, self.current_y):
                self.current_piece = rotated
        elif key == Qt.Key.Key_Escape:
            self.go_back()
