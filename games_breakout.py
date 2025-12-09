"""
Breakout Game Implementation
"""

import random
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class BreakoutGame(QWidget):
    """Breakout game implementation"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['BREAKOUT'][level]
        self.ball_speed = config['ballSpeed']
        self.paddle_speed = config['paddleSpeed']
        self.brick_rows = config['brickRows']
        
        # Game dimensions
        self.game_width = 800
        self.game_height = 600
        
        # Paddle
        self.paddle_width = 100
        self.paddle_height = 15
        self.paddle_x = self.game_width // 2 - self.paddle_width // 2
        self.paddle_y = self.game_height - 25
        
        # Ball
        self.ball_x = self.game_width // 2
        self.ball_y = self.paddle_y - 20
        self.ball_radius = 5
        self.ball_vx = self.ball_speed
        self.ball_vy = -self.ball_speed
        
        # Bricks
        self.brick_width = 75
        self.brick_height = 15
        self.bricks = self.create_bricks()
        
        # Score
        self.score = 0
        self.game_over = False
        self.is_running = True
        self.keys_pressed = set()
        
        # Game timer
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        
        # Setup UI
        self.setup_ui()
    
    def create_bricks(self):
        """Create brick grid"""
        bricks = []
        brick_cols = 10
        start_y = 30
        
        for row in range(self.brick_rows):
            for col in range(brick_cols):
                x = col * (self.brick_width + 5) + 5
                y = start_y + row * (self.brick_height + 5)
                bricks.append({
                    'x': x,
                    'y': y,
                    'width': self.brick_width,
                    'height': self.brick_height,
                    'active': True
                })
        
        return bricks
    
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
    
    def start(self):
        """Start the game"""
        self.game_timer.start(FRAME_TIME)
    
    def stop(self):
        """Stop the game"""
        self.game_timer.stop()
    
    def update_game(self):
        """Update game state"""
        if not self.is_running or self.game_over:
            return
        
        # Move ball
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        
        # Ball collision with walls
        if self.ball_x - self.ball_radius <= 0 or self.ball_x + self.ball_radius >= self.game_width:
            self.ball_vx = -self.ball_vx
            self.ball_x = max(self.ball_radius, min(self.game_width - self.ball_radius, self.ball_x))
        
        if self.ball_y - self.ball_radius <= 0:
            self.ball_vy = -self.ball_vy
            self.ball_y = self.ball_radius
        
        # Ball collision with paddle
        if (self.ball_y + self.ball_radius >= self.paddle_y and 
            self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_width):
            self.ball_vy = -self.ball_vy
            self.ball_y = self.paddle_y - self.ball_radius
        
        # Ball collision with bricks
        for brick in self.bricks:
            if not brick['active']:
                continue
            
            bx, by = brick['x'], brick['y']
            bw, bh = brick['width'], brick['height']
            
            # Simple AAB collision
            if (self.ball_x >= bx and self.ball_x <= bx + bw and 
                self.ball_y >= by and self.ball_y <= by + bh):
                brick['active'] = False
                self.score += 10
                self.score_label.setText(f"Score: {self.score}")
                self.ball_vy = -self.ball_vy
        
        # Ball out of bounds
        if self.ball_y > self.game_height:
            self.game_over = True
            self.is_running = False
            self.stop()
        
        # Check if all bricks cleared
        if all(not brick['active'] for brick in self.bricks):
            self.game_over = True
            self.is_running = False
            self.stop()
        
        # Paddle movement
        if Qt.Key.Key_Left in self.keys_pressed or Qt.Key.Key_A in self.keys_pressed:
            self.paddle_x = max(0, self.paddle_x - self.paddle_speed)
        if Qt.Key.Key_Right in self.keys_pressed or Qt.Key.Key_D in self.keys_pressed:
            self.paddle_x = min(self.game_width - self.paddle_width, self.paddle_x + self.paddle_speed)
        
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
        
        # Calculate scale
        scale_x = (self.width() - 20) / self.game_width
        scale_y = (self.height() - 100) / self.game_height
        offset_x = 10
        offset_y = 80
        
        # Draw bricks
        for brick in self.bricks:
            if brick['active']:
                painter.fillRect(
                    int(offset_x + brick['x'] * scale_x),
                    int(offset_y + brick['y'] * scale_y),
                    int(brick['width'] * scale_x),
                    int(brick['height'] * scale_y),
                    QColor(Colors.PRIMARY)
                )
        
        # Draw paddle
        painter.fillRect(
            int(offset_x + self.paddle_x * scale_x),
            int(offset_y + self.paddle_y * scale_y),
            int(self.paddle_width * scale_x),
            int(self.paddle_height * scale_y),
            QColor(Colors.PRIMARY)
        )
        
        # Draw ball
        painter.setBrush(QBrush(QColor(Colors.ERROR)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(offset_x + self.ball_x * scale_x - self.ball_radius * scale_x),
            int(offset_y + self.ball_y * scale_y - self.ball_radius * scale_y),
            int(self.ball_radius * 2 * scale_x),
            int(self.ball_radius * 2 * scale_y)
        )
        
        # Draw game over
        if self.game_over:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            
            bricks_cleared = sum(1 for b in self.bricks if not b['active'])
            all_cleared = all(not b['active'] for b in self.bricks)
            
            if all_cleared:
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
                f"Score: {self.score} | Bricks: {bricks_cleared}/{len(self.bricks)}"
            )
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if not event.isAutoRepeat():
            self.keys_pressed.add(event.key())
        
        if event.key() == Qt.Key.Key_Escape:
            self.go_back()
    
    def keyReleaseEvent(self, event):
        """Handle key release"""
        if not event.isAutoRepeat():
            self.keys_pressed.discard(event.key())
