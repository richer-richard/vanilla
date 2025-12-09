"""
Pong Game Implementation - Two player AI vs Human
"""

import random
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class PongGame(QWidget):
    """Pong game implementation"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['PONG'][level]
        self.ball_speed = config['ballSpeed']
        self.paddle_speed = config['paddleSpeed']
        self.score_to_win = config['scoreToWin']
        
        # Game dimensions
        self.game_width = 800
        self.game_height = 500
        
        # Paddles
        self.paddle_height = 80
        self.paddle_width = 10
        self.player_y = self.game_height // 2 - self.paddle_height // 2
        self.ai_y = self.game_height // 2 - self.paddle_height // 2
        
        # Ball
        self.ball_x = self.game_width // 2
        self.ball_y = self.game_height // 2
        self.ball_radius = 5
        self.ball_vx = self.ball_speed
        self.ball_vy = self.ball_speed
        
        # Score
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.is_running = True
        self.keys_pressed = set()
        
        # Game timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with scores
        header_layout = QHBoxLayout()
        
        self.player_label = QLabel(f"Player: {self.player_score}")
        self.player_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 16px;")
        
        self.ai_label = QLabel(f"AI: {self.ai_score}")
        self.ai_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 16px;")
        
        level_label = QLabel(f"Level: {self.level}")
        level_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.player_label)
        header_layout.addStretch()
        header_layout.addWidget(level_label)
        header_layout.addStretch()
        header_layout.addWidget(self.ai_label)
        
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
        
        # Ball collision with top and bottom
        if self.ball_y - self.ball_radius <= 0 or self.ball_y + self.ball_radius >= self.game_height:
            self.ball_vy = -self.ball_vy
            self.ball_y = max(self.ball_radius, min(self.game_height - self.ball_radius, self.ball_y))
        
        # Ball collision with paddles
        # Player paddle (left)
        if (self.ball_x - self.ball_radius <= self.paddle_width and 
            self.player_y <= self.ball_y <= self.player_y + self.paddle_height):
            self.ball_vx = -self.ball_vx
            self.ball_x = self.paddle_width + self.ball_radius
        
        # AI paddle (right)
        if (self.ball_x + self.ball_radius >= self.game_width - self.paddle_width and 
            self.ai_y <= self.ball_y <= self.ai_y + self.paddle_height):
            self.ball_vx = -self.ball_vx
            self.ball_x = self.game_width - self.paddle_width - self.ball_radius
        
        # Ball out of bounds (scoring)
        if self.ball_x < 0:
            self.ai_score += 1
            self.ai_label.setText(f"AI: {self.ai_score}")
            self.reset_ball()
            
            if self.ai_score >= self.score_to_win:
                self.game_over = True
                self.is_running = False
                self.stop()
        
        if self.ball_x > self.game_width:
            self.player_score += 1
            self.player_label.setText(f"Player: {self.player_score}")
            self.reset_ball()
            
            if self.player_score >= self.score_to_win:
                self.game_over = True
                self.is_running = False
                self.stop()
        
        # Player paddle movement
        if Qt.Key.Key_Up in self.keys_pressed or Qt.Key.Key_W in self.keys_pressed:
            self.player_y = max(0, self.player_y - self.paddle_speed)
        if Qt.Key.Key_Down in self.keys_pressed or Qt.Key.Key_S in self.keys_pressed:
            self.player_y = min(self.game_height - self.paddle_height, self.player_y + self.paddle_speed)
        
        # AI paddle movement (simple AI)
        paddle_center = self.ai_y + self.paddle_height // 2
        if paddle_center < self.ball_y - 10:
            self.ai_y = min(self.game_height - self.paddle_height, self.ai_y + self.paddle_speed)
        elif paddle_center > self.ball_y + 10:
            self.ai_y = max(0, self.ai_y - self.paddle_speed)
        
        self.update()
    
    def reset_ball(self):
        """Reset ball to center"""
        self.ball_x = self.game_width // 2
        self.ball_y = self.game_height // 2
        self.ball_vx = self.ball_speed * random.choice([-1, 1])
        self.ball_vy = self.ball_speed * random.choice([-1, 1])
    
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
        
        # Draw center line
        painter.setPen(QPen(QColor("#333333"), 1))
        center_x = offset_x + self.game_width * scale_x / 2
        for i in range(10, self.height() - 50, 20):
            painter.drawLine(int(center_x), i, int(center_x), i + 10)
        
        # Draw player paddle
        painter.fillRect(
            int(offset_x),
            int(offset_y + self.player_y * scale_y),
            int(self.paddle_width * scale_x),
            int(self.paddle_height * scale_y),
            QColor(Colors.PRIMARY)
        )
        
        # Draw AI paddle
        painter.fillRect(
            int(offset_x + (self.game_width - self.paddle_width) * scale_x),
            int(offset_y + self.ai_y * scale_y),
            int(self.paddle_width * scale_x),
            int(self.paddle_height * scale_y),
            QColor(Colors.SECONDARY)
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
            
            winner = "YOU WON!" if self.player_score > self.ai_score else "YOU LOST!"
            color = Colors.SUCCESS if self.player_score > self.ai_score else Colors.ERROR
            
            painter.setPen(QPen(QColor(color)))
            painter.drawText(self.rect(), 1 | 32, winner)
            
            font.setPointSize(14)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Colors.WHITE)))
            painter.drawText(
                self.rect().adjusted(0, 40, 0, 0),
                1 | 32,
                f"Final: {self.player_score} - {self.ai_score}"
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
