"""
DevSync Design System
Modern, beautiful design tokens and utilities
"""

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtCore import QEasingCurve
from enum import Enum


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"


# ============================================================================
# COLOR SYSTEM
# ============================================================================

class Colors:
    """Modern color palette"""
    
    LIGHT = {
        # Primary
        'primary': '#0066FF',
        'primary_hover': '#0052CC',
        'primary_light': '#E6F0FF',
        'primary_dark': '#003D99',
        
        # Success
        'success': '#00C853',
        'success_hover': '#00A844',
        'success_light': '#E8F5E9',
        
        # Warning
        'warning': '#FF9800',
        'warning_hover': '#E68900',
        'warning_light': '#FFF3E0',
        
        # Error
        'error': '#F44336',
        'error_hover': '#D32F2F',
        'error_light': '#FFEBEE',
        
        # Info
        'info': '#2196F3',
        'info_light': '#E3F2FD',
        
        # Backgrounds
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
        'bg_tertiary': '#E9ECEF',
        'bg_hover': '#F1F3F5',
        
        # Text
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'text_tertiary': '#ADB5BD',
        'text_disabled': '#CED4DA',
        
        # Borders
        'border': '#DEE2E6',
        'border_light': '#E9ECEF',
        'border_dark': '#CED4DA',
        
        # Shadows
        'shadow': 'rgba(0, 0, 0, 0.1)',
        'shadow_dark': 'rgba(0, 0, 0, 0.2)',
    }
    
    DARK = {
        # Primary
        'primary': '#4D9FFF',
        'primary_hover': '#66B3FF',
        'primary_light': '#1A3A52',
        'primary_dark': '#3380CC',
        
        # Success
        'success': '#4CAF50',
        'success_hover': '#66BB6A',
        'success_light': '#1B3A1E',
        
        # Warning
        'warning': '#FFB74D',
        'warning_hover': '#FFCC80',
        'warning_light': '#3D2E1F',
        
        # Error
        'error': '#EF5350',
        'error_hover': '#F44336',
        'error_light': '#3D1F1E',
        
        # Info
        'info': '#42A5F5',
        'info_light': '#1E3A52',
        
        # Backgrounds
        'bg_primary': '#1E1E1E',
        'bg_secondary': '#252525',
        'bg_tertiary': '#2D2D2D',
        'bg_hover': '#333333',
        
        # Text
        'text_primary': '#E8E8E8',
        'text_secondary': '#A0A0A0',
        'text_tertiary': '#707070',
        'text_disabled': '#505050',
        
        # Borders
        'border': '#3D3D3D',
        'border_light': '#2D2D2D',
        'border_dark': '#4D4D4D',
        
        # Shadows
        'shadow': 'rgba(0, 0, 0, 0.3)',
        'shadow_dark': 'rgba(0, 0, 0, 0.5)',
    }


# ============================================================================
# TYPOGRAPHY
# ============================================================================

class Typography:
    """Font system"""
    
    FAMILIES = {
        'primary': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'monospace': 'JetBrains Mono, Consolas, Monaco, "Courier New", monospace',
        'display': 'Outfit, Inter, sans-serif',
    }
    
    SIZES = {
        'xs': 11,
        'sm': 13,
        'base': 15,
        'lg': 18,
        'xl': 24,
        '2xl': 32,
        '3xl': 40,
        '4xl': 48,
    }
    
    WEIGHTS = {
        'regular': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
        'extrabold': 800,
    }
    
    LINE_HEIGHTS = {
        'tight': 1.2,
        'normal': 1.5,
        'relaxed': 1.75,
    }


# ============================================================================
# SPACING & LAYOUT
# ============================================================================

class Spacing:
    """Spacing scale"""
    
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48
    XXXL = 64


class BorderRadius:
    """Border radius scale"""
    
    SM = 6
    MD = 10
    LG = 16
    XL = 24
    FULL = 9999


class Shadows:
    """Shadow definitions"""
    
    SM = '0 2px 4px rgba(0, 0, 0, 0.05)'
    MD = '0 4px 12px rgba(0, 0, 0, 0.08)'
    LG = '0 8px 24px rgba(0, 0, 0, 0.12)'
    XL = '0 16px 48px rgba(0, 0, 0, 0.16)'
    INNER = 'inset 0 2px 4px rgba(0, 0, 0, 0.06)'


# ============================================================================
# ANIMATION
# ============================================================================

class Animation:
    """Animation timing and easing"""
    
    DURATIONS = {
        'instant': 0,
        'fast': 150,
        'normal': 250,
        'slow': 400,
        'slower': 600,
    }
    
    EASING = {
        'ease_out': QEasingCurve.Type.OutCubic,
        'ease_in': QEasingCurve.Type.InCubic,
        'ease_in_out': QEasingCurve.Type.InOutCubic,
        'spring': QEasingCurve.Type.OutBack,
    }


# ============================================================================
# STYLE GENERATOR
# ============================================================================

class StyleSheet:
    """Generate modern stylesheets"""
    
    @staticmethod
    def get_theme_colors(theme: Theme = Theme.LIGHT):
        """Get colors for theme"""
        return Colors.DARK if theme == Theme.DARK else Colors.LIGHT
    
    @staticmethod
    def card(theme: Theme = Theme.LIGHT):
        """Modern card style"""
        colors = StyleSheet.get_theme_colors(theme)
        return f"""
            QWidget {{
                background: {colors['bg_primary']};
                border-radius: {BorderRadius.LG}px;
                border: 1px solid {colors['border_light']};
                padding: {Spacing.LG}px;
            }}
        """
    
    @staticmethod
    def button_primary(theme: Theme = Theme.LIGHT):
        """Primary button style"""
        colors = StyleSheet.get_theme_colors(theme)
        return f"""
            QPushButton {{
                background: {colors['primary']};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.LG}px;
                font-size: {Typography.SIZES['base']}px;
                font-weight: {Typography.WEIGHTS['semibold']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: {colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background: {colors['primary_dark']};
            }}
            QPushButton:disabled {{
                background: {colors['bg_tertiary']};
                color: {colors['text_disabled']};
            }}
        """
    
    @staticmethod
    def button_secondary(theme: Theme = Theme.LIGHT):
        """Secondary button style"""
        colors = StyleSheet.get_theme_colors(theme)
        return f"""
            QPushButton {{
                background: {colors['bg_secondary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.LG}px;
                font-size: {Typography.SIZES['base']}px;
                font-weight: {Typography.WEIGHTS['medium']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: {colors['bg_hover']};
                border-color: {colors['border_dark']};
            }}
            QPushButton:pressed {{
                background: {colors['bg_tertiary']};
            }}
        """
    
    @staticmethod
    def input(theme: Theme = Theme.LIGHT):
        """Modern input style"""
        colors = StyleSheet.get_theme_colors(theme)
        return f"""
            QLineEdit, QTextEdit {{
                background: {colors['bg_primary']};
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.MD}px;
                font-size: {Typography.SIZES['base']}px;
                selection-background-color: {colors['primary_light']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors['primary']};
                background: {colors['bg_primary']};
            }}
            QLineEdit:hover, QTextEdit:hover {{
                border-color: {colors['border_dark']};
            }}
        """
    
    @staticmethod
    def progress_bar(theme: Theme = Theme.LIGHT):
        """Modern progress bar"""
        colors = StyleSheet.get_theme_colors(theme)
        return f"""
            QProgressBar {{
                border: none;
                border-radius: {BorderRadius.FULL}px;
                background: {colors['bg_tertiary']};
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['primary']},
                    stop:1 {colors['primary_hover']}
                );
                border-radius: {BorderRadius.FULL}px;
            }}
        """
    
    @staticmethod
    def main_window(theme: Theme = Theme.LIGHT):
        """Main window style"""
        colors = StyleSheet.get_theme_colors(theme)
        return f"""
            QMainWindow {{
                background: {colors['bg_secondary']};
            }}
            QWidget {{
                color: {colors['text_primary']};
                font-family: {Typography.FAMILIES['primary']};
                font-size: {Typography.SIZES['base']}px;
            }}
            QGroupBox {{
                background: {colors['bg_primary']};
                border: 1px solid {colors['border_light']};
                border-radius: {BorderRadius.LG}px;
                margin-top: {Spacing.MD}px;
                padding: {Spacing.LG}px;
                font-weight: {Typography.WEIGHTS['semibold']};
            }}
            QGroupBox::title {{
                color: {colors['text_primary']};
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 {Spacing.SM}px;
                background: {colors['bg_primary']};
            }}
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {colors['bg_secondary']};
                color: {colors['text_secondary']};
                border: none;
                border-radius: {BorderRadius.MD}px {BorderRadius.MD}px 0 0;
                padding: {Spacing.SM}px {Spacing.LG}px;
                margin-right: {Spacing.XS}px;
                font-weight: {Typography.WEIGHTS['medium']};
            }}
            QTabBar::tab:selected {{
                background: {colors['bg_primary']};
                color: {colors['primary']};
                font-weight: {Typography.WEIGHTS['semibold']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {colors['bg_hover']};
            }}
            QListWidget, QTreeWidget, QTableWidget {{
                background: {colors['bg_primary']};
                border: 1px solid {colors['border_light']};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px;
            }}
            QListWidget::item, QTreeWidget::item {{
                padding: {Spacing.SM}px;
                border-radius: {BorderRadius.SM}px;
            }}
            QListWidget::item:selected, QTreeWidget::item:selected {{
                background: {colors['primary_light']};
                color: {colors['primary']};
            }}
            QListWidget::item:hover, QTreeWidget::item:hover {{
                background: {colors['bg_hover']};
            }}
            QScrollBar:vertical {{
                background: {colors['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['border_dark']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['text_tertiary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QToolTip {{
                background: {colors['bg_primary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: {BorderRadius.SM}px;
                padding: {Spacing.XS}px {Spacing.SM}px;
            }}
        """


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_font(family='primary', size='base', weight='regular'):
    """Get QFont with design system values"""
    font = QFont()
    font.setFamily(Typography.FAMILIES[family].split(',')[0])
    font.setPointSize(Typography.SIZES[size])
    font.setWeight(Typography.WEIGHTS[weight])
    return font


def get_color(color_name: str, theme: Theme = Theme.LIGHT):
    """Get QColor from design system"""
    colors = Colors.DARK if theme == Theme.DARK else Colors.LIGHT
    return QColor(colors.get(color_name, '#000000'))
