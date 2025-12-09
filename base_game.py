"""
Base Game Widget - Abstract base class for all games
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont
from constants import Colors, GAME_WIDTH, GAME_HEIGHT, FRAME_TIME


class BaseGameWidget(QWidget):
    """Base class for all game widgets"""
    
    def __init__(self, level=1, parent=None):
        super().__init__(parent)
        self.level = level
        self.is_running = True
        self.game_over = False
        self.score = 0
        
        # Game timer for FPS control
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(FRAME_TIME)
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup basic UI layout with back button"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
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
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_game(self):
        """Override in subclasses to implement game logic"""
        pass
    
    def go_back(self):
        """Go back to menu - override in subclasses if needed"""
        self.cleanup()
        if hasattr(self.parent(), 'show_menu'):
            self.parent().show_menu()
    
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        self.game_timer.stop()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.cleanup()
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.go_back()
        event.accept()
