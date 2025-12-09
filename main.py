"""
Vanilla Arcade Hub - Main Application
A complete Python GUI arcade game collection using PyQt6
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient
from constants import Colors, GAMES, WINDOW_WIDTH, WINDOW_HEIGHT

# Import all game modules
from games_snake import SnakeGame
from games_tetris import TetrisGame
from games_pong import PongGame
from games_breakout import BreakoutGame
from games_geometry_dash import GeometryDashGame
from games_minesweeper import MinesweeperGame
from games_space_shooters import SpaceShootersGame


class VanillaArcadeHub(QMainWindow):
    """Main application window for Vanilla Arcade Hub"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VANILLA - Arcade Hub")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(self.get_stylesheet())
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header
        self.setup_header()
        
        # Content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area)
        
        # Footer
        self.setup_footer()
        
        self.central_widget.setLayout(self.main_layout)
        
        # Current game state
        self.current_game = None
        self.current_level = 1
        
        # Show homepage
        self.show_homepage()
    
    def get_stylesheet(self):
        """Return the global stylesheet"""
        return f"""
        QMainWindow {{
            background: linear-gradient(135deg, {Colors.DARK_BG} 0%, {Colors.MEDIUM_BG} 50%, {Colors.DARKER_BG} 100%);
        }}
        QWidget {{
            background: linear-gradient(135deg, {Colors.DARK_BG} 0%, {Colors.MEDIUM_BG} 50%, {Colors.DARKER_BG} 100%);
            color: {Colors.LIGHT_GRAY};
        }}
        QPushButton {{
            background: linear-gradient(135deg, {Colors.PRIMARY}, {Colors.SECONDARY});
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background: linear-gradient(135deg, {Colors.SECONDARY}, {Colors.PRIMARY});
        }}
        QPushButton:pressed {{
            transform: scale(0.98);
        }}
        QLabel {{
            color: {Colors.LIGHT_GRAY};
        }}
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        """
    
    def setup_header(self):
        """Setup header with title"""
        header = QWidget()
        header.setStyleSheet(f"""
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
            border-bottom: 1px solid rgba(102, 126, 234, 0.2);
        """)
        header.setMinimumHeight(70)
        header.setMaximumHeight(70)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 15, 30, 15)
        
        # Logo button (home)
        logo_btn = QPushButton("← VANILLA")
        logo_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.PRIMARY};
                border: none;
                font-family: 'Press Start 2P', monospace;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background: rgba(102, 126, 234, 0.1);
                border-radius: 5px;
            }}
        """)
        logo_btn.clicked.connect(self.show_homepage)
        header_layout.addWidget(logo_btn)
        
        # Spacer
        header_layout.addStretch()
        
        # Subtitle
        subtitle = QLabel("Classic Arcade Games Reimagined")
        subtitle.setStyleSheet(f"color: {Colors.MEDIUM_GRAY}; font-size: 11px; letter-spacing: 1px;")
        header_layout.addWidget(subtitle)
        
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
    
    def setup_footer(self):
        """Setup footer"""
        footer = QWidget()
        footer.setStyleSheet(f"""
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.05), transparent);
            border-top: 1px solid rgba(102, 126, 234, 0.1);
        """)
        footer.setMinimumHeight(60)
        footer.setMaximumHeight(60)
        
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(30, 10, 30, 10)
        
        brand = QLabel("VANILLA")
        brand.setStyleSheet(f"""
            color: {Colors.PRIMARY};
            font-family: 'Press Start 2P', monospace;
            font-size: 10px;
            font-weight: bold;
        """)
        
        desc = QLabel("Classic Arcade Games Reimagined • © 2024 • Built with Python & PyQt6")
        desc.setStyleSheet(f"color: {Colors.MEDIUM_GRAY}; font-size: 10px;")
        
        footer_layout.addWidget(brand)
        footer_layout.addWidget(desc)
        footer_layout.addStretch()
        
        footer.setLayout(footer_layout)
        self.main_layout.addWidget(footer)
    
    def clear_content(self):
        """Clear content area"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def show_homepage(self):
        """Show the homepage"""
        self.clear_content()
        
        # Content wrapper
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(40)
        
        # Add stretch at top
        layout.addStretch()
        
        # Title
        title = QLabel("VANILLA")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {Colors.PRIMARY}; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Classic Games Reimagined")
        subtitle_font = QFont()
        subtitle_font.setPointSize(18)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {Colors.MEDIUM_GRAY}; text-align: center;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Description
        desc = QLabel(
            "Experience timeless arcade games with modern design and smooth gameplay.\n"
            "Relive the joy of retro gaming or discover them for the first time."
        )
        desc.setStyleSheet(f"color: {Colors.LIGHT_GRAY}; text-align: center;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # CTA Button
        play_btn = QPushButton("PLAY NOW")
        play_btn.setMinimumHeight(50)
        play_btn.setMaximumWidth(200)
        play_btn.setStyleSheet(f"""
            QPushButton {{
                background: linear-gradient(135deg, {Colors.PRIMARY}, {Colors.SECONDARY});
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 40px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: linear-gradient(135deg, {Colors.SECONDARY}, {Colors.PRIMARY});
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }}
        """)
        play_btn.clicked.connect(self.show_menu)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(play_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Add stretch at bottom
        layout.addStretch()
        
        content.setLayout(layout)
        self.content_layout.addWidget(content)
    
    def show_menu(self):
        """Show the game selection menu"""
        self.clear_content()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("Select Your Game")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # Games grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        game_keys = list(GAMES.keys())
        for idx, game_key in enumerate(game_keys):
            game_info = GAMES[game_key]
            row = idx // 2
            col = idx % 2
            
            # Game card button
            card = QPushButton()
            card.setMinimumHeight(150)
            card.setStyleSheet(f"""
                QPushButton {{
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
                    border: 2px solid rgba(102, 126, 234, 0.3);
                    border-radius: 15px;
                    padding: 20px;
                    color: white;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.1));
                    border-color: rgba(102, 126, 234, 0.7);
                    transform: translateY(-5px);
                }}
            """)
            
            # Card layout
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(10, 10, 10, 10)
            
            # Game name
            name_label = QLabel(f"{game_info['icon']} {game_info['name']}")
            name_font = QFont()
            name_font.setPointSize(16)
            name_font.setBold(True)
            name_label.setFont(name_font)
            name_label.setStyleSheet(f"color: white; background: transparent;")
            card_layout.addWidget(name_label)
            
            # Description
            desc_label = QLabel(game_info['description'])
            desc_label.setStyleSheet(f"color: {Colors.MEDIUM_GRAY}; background: transparent; font-size: 11px;")
            desc_label.setWordWrap(True)
            card_layout.addWidget(desc_label)
            
            card_layout.addStretch()
            card.setLayout(card_layout)
            
            # Connect click handler
            card.clicked.connect(lambda checked=False, gk=game_key: self.show_levels(gk))
            
            grid.addWidget(card, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        self.content_layout.addWidget(scroll)
    
    def show_levels(self, game_key):
        """Show level selection for a game"""
        self.clear_content()
        
        game_info = GAMES[game_key]
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Title
        title = QLabel(f"Select Difficulty - {game_info['name']}")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title)
        
        # Levels
        levels_layout = QHBoxLayout()
        levels_layout.setSpacing(20)
        levels_layout.addStretch()
        
        for level_config in game_info['levels']:
            level_btn = QPushButton(level_config['name'])
            level_btn.setMinimumHeight(70)
            level_btn.setMinimumWidth(150)
            level_btn.setStyleSheet(f"""
                QPushButton {{
                    background: linear-gradient(135deg, {Colors.PRIMARY}, {Colors.SECONDARY});
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px 30px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: linear-gradient(135deg, {Colors.SECONDARY}, {Colors.PRIMARY});
                }}
            """)
            level_btn.clicked.connect(
                lambda checked=False, gk=game_key, lv=level_config['level']: self.start_game(gk, lv)
            )
            levels_layout.addWidget(level_btn)
        
        levels_layout.addStretch()
        layout.addLayout(levels_layout)
        layout.addStretch()
        
        content.setLayout(layout)
        self.content_layout.addWidget(content)
    
    def start_game(self, game_key, level):
        """Start a game"""
        self.clear_content()
        
        # Map game keys to game classes
        game_classes = {
            'SNAKE': SnakeGame,
            'TETRIS': TetrisGame,
            'PONG': PongGame,
            'BREAKOUT': BreakoutGame,
            'GEOMETRY_DASH': GeometryDashGame,
            'MINESWEEPER': MinesweeperGame,
            'SPACE_SHOOTERS': SpaceShootersGame
        }
        
        GameClass = game_classes.get(game_key)
        if not GameClass:
            self.show_menu()
            return
        
        # Create game instance
        game = GameClass(level=level, on_menu_click=self.show_menu)
        game.start()
        
        self.content_layout.addWidget(game)
        self.current_game = game


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = VanillaArcadeHub()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
