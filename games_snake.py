"""
Snake Game Implementation
"""

import math
import random
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class SnakeGame(QWidget):
    """Classic Snake game implementation"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['SNAKE'][level]
        self.grid_size = config['gridSize']
        self.update_speed = config['speed']
        self.score_per_food = config['scorePerFood']
        
        # Game state
        self.snake = [QPoint(10, 10)]
        self.food = QPoint(15, 15)
        self.direction = QPoint(1, 0)
        self.next_direction = QPoint(1, 0)
        self.score = 0
        self.game_over = False
        self.is_running = True
        
        # Game loop timer
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_snake)
        
        # Setup UI
        self.setup_ui()
        
        # Spawn initial food
        self.spawn_food()
    
    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with score and level
        header_layout = QHBoxLayout()
        
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        level_label = QLabel(f"Level: {self.level}")
        level_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.score_label)
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
    
    def spawn_food(self):
        """Spawn food at random position not occupied by snake"""
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            point = QPoint(x, y)
            if point not in self.snake:
                self.food = point
                break
    
    def start(self):
        """Start the game"""
        self.game_timer.start(FRAME_TIME)
        self.move_timer.start(self.update_speed)
    
    def stop(self):
        """Stop the game"""
        self.game_timer.stop()
        self.move_timer.stop()
    
    def move_snake(self):
        """Move snake in the current direction"""
        if not self.is_running or self.game_over:
            return
        
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.snake[0]
        new_head = QPoint(
            (head.x() + self.direction.x()) % self.grid_size,
            (head.y() + self.direction.y()) % self.grid_size
        )
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            self.is_running = False
            self.stop()
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food:
            self.score += self.score_per_food
            self.score_label.setText(f"Score: {self.score}")
            self.spawn_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
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
        
        # Calculate cell size
        width = self.width()
        height = self.height() - 80  # Account for UI elements
        cell_width = width / self.grid_size
        cell_height = height / self.grid_size
        
        # Draw grid
        painter.setPen(QPen(QColor("#1a1a1a")))
        for i in range(self.grid_size + 1):
            painter.drawLine(int(i * cell_width), 80, int(i * cell_width), int(80 + height))
            painter.drawLine(0, int(80 + i * cell_height), int(width), int(80 + i * cell_height))
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            if i == 0:
                painter.fillRect(
                    int(segment.x() * cell_width + 1),
                    int(80 + segment.y() * cell_height + 1),
                    int(cell_width - 2),
                    int(cell_height - 2),
                    QColor(Colors.SNAKE_HEAD)
                )
            else:
                painter.fillRect(
                    int(segment.x() * cell_width + 1),
                    int(80 + segment.y() * cell_height + 1),
                    int(cell_width - 2),
                    int(cell_height - 2),
                    QColor(Colors.SNAKE_BODY)
                )
            
            painter.setPen(QPen(QColor(Colors.SNAKE_BORDER)))
            painter.drawRect(
                int(segment.x() * cell_width + 1),
                int(80 + segment.y() * cell_height + 1),
                int(cell_width - 2),
                int(cell_height - 2)
            )
        
        # Draw food
        painter.setBrush(QBrush(QColor(Colors.SNAKE_FOOD)))
        painter.setPen(Qt.PenStyle.NoPen)
        center_x = self.food.x() * cell_width + cell_width / 2
        center_y = 80 + self.food.y() * cell_height + cell_height / 2
        radius = cell_width / 2 - 2
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))
        
        # Draw game over
        if self.game_over:
            # Semi-transparent overlay
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            
            # Game over text
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Colors.ERROR)))
            painter.drawText(self.rect(), 1 | 32, "GAME OVER")
            
            # Final score
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
        if event.isAutoRepeat():
            return
        
        key = event.key()
        
        if key == Qt.Key.Key_Up or key == Qt.Key.Key_W:
            if self.direction.y() == 0:
                self.next_direction = QPoint(0, -1)
        elif key == Qt.Key.Key_Down or key == Qt.Key.Key_S:
            if self.direction.y() == 0:
                self.next_direction = QPoint(0, 1)
        elif key == Qt.Key.Key_Left or key == Qt.Key.Key_A:
            if self.direction.x() == 0:
                self.next_direction = QPoint(-1, 0)
        elif key == Qt.Key.Key_Right or key == Qt.Key.Key_D:
            if self.direction.x() == 0:
                self.next_direction = QPoint(1, 0)
        elif key == Qt.Key.Key_Escape:
            self.go_back()
