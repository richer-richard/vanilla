"""
Geometry Dash Game Implementation
"""

import random
import math
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class GeometryDashGame(QWidget):
    """Geometry Dash platformer game"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['GEOMETRY_DASH'][level]
        self.speed = config['speed']
        self.gravity = config['gravity']
        self.jump_power = config['jumpPower']
        
        # Game dimensions
        self.game_width = 800
        self.game_height = 400
        
        # Player
        self.player_x = 50
        self.player_y = self.game_height // 2
        self.player_size = 30
        self.velocity_y = 0
        self.is_jumping = False
        self.double_jump = False
        
        # Obstacles
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = 120
        
        # Score
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.is_running = True
        
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
        
        # Header with score and distance
        header_layout = QHBoxLayout()
        
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        self.distance_label = QLabel(f"Distance: {self.distance}")
        self.distance_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        level_label = QLabel(f"Level: {self.level}")
        level_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.score_label)
        header_layout.addWidget(self.distance_label)
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
    
    def spawn_obstacle(self):
        """Spawn a new obstacle"""
        obstacle_height = random.randint(20, 60)
        self.obstacles.append({
            'x': self.game_width,
            'height': obstacle_height,
            'width': 30
        })
    
    def update_game(self):
        """Update game state"""
        if not self.is_running or self.game_over:
            return
        
        # Apply gravity
        self.velocity_y += self.gravity
        self.player_y += self.velocity_y
        
        # Ground collision
        ground_level = self.game_height - 60
        if self.player_y + self.player_size >= ground_level:
            self.player_y = ground_level - self.player_size
            self.velocity_y = 0
            self.is_jumping = False
            self.double_jump = False
        
        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle['x'] -= self.speed
            
            # Collision detection
            if (self.player_x + self.player_size > obstacle['x'] and 
                self.player_x < obstacle['x'] + obstacle['width'] and
                self.player_y + self.player_size > self.game_height - obstacle['height']):
                self.game_over = True
                self.is_running = False
                self.stop()
            
            # Remove off-screen obstacles
            if obstacle['x'] + obstacle['width'] < 0:
                self.obstacles.remove(obstacle)
                self.score += 10
                self.distance += 1
                self.score_label.setText(f"Score: {self.score}")
                self.distance_label.setText(f"Distance: {self.distance}")
        
        self.update()
    
    def go_back(self):
        """Go back to menu"""
        self.stop()
        if self.on_menu_click:
            self.on_menu_click()
    
    def paintEvent(self, event):
        """Render game"""
        painter = QPainter(self)
        
        # Draw background with gradient
        painter.fillRect(self.rect(), QColor(Colors.BLACK))
        
        # Calculate scale
        scale_x = (self.width() - 20) / self.game_width
        scale_y = (self.height() - 100) / self.game_height
        offset_x = 10
        offset_y = 80
        
        # Draw ground
        ground_level = offset_y + (self.game_height - 60) * scale_y
        painter.fillRect(
            offset_x,
            int(ground_level),
            int(self.game_width * scale_x),
            int(60 * scale_y),
            QColor("#1a1a1a")
        )
        
        painter.setPen(QPen(QColor(Colors.PRIMARY), 2))
        painter.drawLine(int(offset_x), int(ground_level), int(offset_x + self.game_width * scale_x), int(ground_level))
        
        # Draw player (cube)
        painter.fillRect(
            int(offset_x + self.player_x * scale_x),
            int(offset_y + self.player_y * scale_y),
            int(self.player_size * scale_x),
            int(self.player_size * scale_y),
            QColor(Colors.PRIMARY)
        )
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle_y = offset_y + (self.game_height - obstacle['height']) * scale_y
            painter.fillRect(
                int(offset_x + obstacle['x'] * scale_x),
                int(obstacle_y),
                int(obstacle['width'] * scale_x),
                int(obstacle['height'] * scale_y),
                QColor(Colors.ERROR)
            )
        
        # Draw game over
        if self.game_over:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Colors.ERROR)))
            painter.drawText(self.rect(), 1 | 32, "CRASHED!")
            
            font.setPointSize(14)
            painter.setFont(font)
            painter.setPen(QPen(QColor(Colors.WHITE)))
            painter.drawText(
                self.rect().adjusted(0, 40, 0, 0),
                1 | 32,
                f"Score: {self.score} | Distance: {self.distance}"
            )
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.isAutoRepeat():
            return
        
        key = event.key()
        
        if (key == Qt.Key.Key_Space or key == Qt.Key.Key_Up or key == Qt.Key.Key_W) and not self.game_over:
            if not self.is_jumping:
                self.velocity_y = -self.jump_power
                self.is_jumping = True
            elif not self.double_jump:
                self.velocity_y = -self.jump_power
                self.double_jump = True
        elif key == Qt.Key.Key_Escape:
            self.go_back()
