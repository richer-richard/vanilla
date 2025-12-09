"""
Space Shooters Game Implementation
"""

import random
import math
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from constants import Colors, LEVEL_CONFIG, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class SpaceShootersGame(QWidget):
    """Space Shooters game implementation"""
    
    def __init__(self, level=1, on_menu_click=None, parent=None):
        super().__init__(parent)
        self.level = level
        self.on_menu_click = on_menu_click
        
        # Game configuration
        config = LEVEL_CONFIG['SPACE_SHOOTERS'][level]
        self.enemy_speed = config['enemySpeed']
        self.spawn_rate = config['spawnRate']
        self.player_speed = config['playerSpeed']
        
        # Game dimensions
        self.game_width = 800
        self.game_height = 600
        
        # Player
        self.player_x = self.game_width // 2
        self.player_y = self.game_height - 50
        self.player_size = 30
        self.keys_pressed = set()
        
        # Bullets
        self.bullets = []
        
        # Enemies
        self.enemies = []
        self.spawn_timer = 0
        
        # Score and health
        self.score = 0
        self.health = 100
        self.game_over = False
        self.is_running = True
        
        # Game timer
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with score and health
        header_layout = QHBoxLayout()
        
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        self.health_label = QLabel(f"Health: {self.health}%")
        self.health_label.setStyleSheet(f"color: {Colors.ERROR}; font-weight: bold; font-size: 14px;")
        
        level_label = QLabel(f"Level: {self.level}")
        level_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(self.score_label)
        header_layout.addStretch()
        header_layout.addWidget(self.health_label)
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
    
    def spawn_enemy(self):
        """Spawn an enemy"""
        x = random.randint(0, self.game_width - 30)
        self.enemies.append({
            'x': x,
            'y': -30,
            'size': 25,
            'health': 20
        })
    
    def shoot(self):
        """Create a bullet"""
        self.bullets.append({
            'x': self.player_x + self.player_size // 2 - 2,
            'y': self.player_y,
            'width': 4,
            'height': 15,
            'speed': 10
        })
    
    def update_game(self):
        """Update game state"""
        if not self.is_running or self.game_over:
            return
        
        # Player movement
        if Qt.Key.Key_Left in self.keys_pressed or Qt.Key.Key_A in self.keys_pressed:
            self.player_x = max(0, self.player_x - self.player_speed)
        if Qt.Key.Key_Right in self.keys_pressed or Qt.Key.Key_D in self.keys_pressed:
            self.player_x = min(self.game_width - self.player_size, self.player_x + self.player_speed)
        
        # Spawn enemies
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed']
            
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
                continue
            
            # Check collision with enemies
            for enemy in self.enemies[:]:
                if (bullet['x'] <= enemy['x'] + enemy['size'] and
                    bullet['x'] + bullet['width'] >= enemy['x'] and
                    bullet['y'] <= enemy['y'] + enemy['size'] and
                    bullet['y'] + bullet['height'] >= enemy['y']):
                    
                    enemy['health'] -= 10
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if enemy['health'] <= 0:
                        self.enemies.remove(enemy)
                        self.score += 10
                        self.score_label.setText(f"Score: {self.score}")
                    break
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy['y'] += self.enemy_speed
            
            # Check collision with player
            if (enemy['x'] <= self.player_x + self.player_size and
                enemy['x'] + enemy['size'] >= self.player_x and
                enemy['y'] <= self.player_y + self.player_size and
                enemy['y'] + enemy['size'] >= self.player_y):
                
                self.enemies.remove(enemy)
                self.health -= 10
                self.health_label.setText(f"Health: {self.health}%")
                
                if self.health <= 0:
                    self.game_over = True
                    self.is_running = False
                    self.stop()
            
            # Remove off-screen enemies
            if enemy['y'] > self.game_height:
                self.enemies.remove(enemy)
        
        self.update()
    
    def go_back(self):
        """Go back to menu"""
        self.stop()
        if self.on_menu_click:
            self.on_menu_click()
    
    def paintEvent(self, event):
        """Render game"""
        painter = QPainter(self)
        
        # Draw background with stars
        painter.fillRect(self.rect(), QColor(Colors.BLACK))
        
        # Calculate scale
        scale_x = (self.width() - 20) / self.game_width
        scale_y = (self.height() - 100) / self.game_height
        offset_x = 10
        offset_y = 80
        
        # Draw stars (simple background animation)
        painter.setPen(QPen(QColor("#44444444")))
        for i in range(20):
            x = (i * 40) % int(self.game_width * scale_x)
            y = (i * 30) % int(self.game_height * scale_y)
            painter.drawEllipse(int(offset_x + x), int(offset_y + y), 2, 2)
        
        # Draw player (ship)
        painter.fillRect(
            int(offset_x + self.player_x * scale_x),
            int(offset_y + self.player_y * scale_y),
            int(self.player_size * scale_x),
            int(self.player_size * scale_y),
            QColor(Colors.PRIMARY)
        )
        
        # Draw bullets
        for bullet in self.bullets:
            painter.fillRect(
                int(offset_x + bullet['x'] * scale_x),
                int(offset_y + bullet['y'] * scale_y),
                int(bullet['width'] * scale_x),
                int(bullet['height'] * scale_y),
                QColor(Colors.SUCCESS)
            )
        
        # Draw enemies
        for enemy in self.enemies:
            painter.fillRect(
                int(offset_x + enemy['x'] * scale_x),
                int(offset_y + enemy['y'] * scale_y),
                int(enemy['size'] * scale_x),
                int(enemy['size'] * scale_y),
                QColor(Colors.ERROR)
            )
            
            # Draw health bar
            health_bar_width = enemy['size'] * (enemy['health'] / 20)
            painter.fillRect(
                int(offset_x + enemy['x'] * scale_x),
                int(offset_y + (enemy['y'] - 5) * scale_y),
                int(health_bar_width * scale_x),
                int(3 * scale_y),
                QColor(Colors.SUCCESS)
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
        if not event.isAutoRepeat():
            self.keys_pressed.add(event.key())
            
            if event.key() == Qt.Key.Key_Space:
                self.shoot()
        
        if event.key() == Qt.Key.Key_Escape:
            self.go_back()
    
    def keyReleaseEvent(self, event):
        """Handle key release"""
        if not event.isAutoRepeat():
            self.keys_pressed.discard(event.key())
