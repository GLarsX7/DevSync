"""
Modern UI Components for DevSync
Beautiful, animated, reusable components
"""

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect, QFrame
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QPoint, QSize, pyqtSignal, QParallelAnimationGroup
)
from PyQt6.QtGui import QPainter, QColor, QPen, QConicalGradient, QLinearGradient

from design_system import (
    Colors, Typography, Spacing, BorderRadius, 
    Animation, StyleSheet, Theme, get_font
)


# ============================================================================
# MODERN CARD
# ============================================================================

class ModernCard(QFrame):
    """Beautiful card with hover effects"""
    
    def __init__(self, parent=None, theme=Theme.LIGHT):
        super().__init__(parent)
        self.theme = theme
        self.setup_ui()
        
    def setup_ui(self):
        colors = Colors.DARK if self.theme == Theme.DARK else Colors.LIGHT
        
        self.setStyleSheet(f"""
            ModernCard {{
                background: {colors['bg_primary']};
                border-radius: {BorderRadius.LG}px;
                border: 1px solid {colors['border_light']};
                padding: {Spacing.LG}px;
            }}
        """)
        
        # Add subtle shadow effect
        self.setGraphicsEffect(None)  # Will add shadow on hover
        
    def enterEvent(self, event):
        """Animate on hover"""
        # TODO: Add elevation animation
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Remove hover effect"""
        super().leaveEvent(event)


# ============================================================================
# ANIMATED BUTTON
# ============================================================================

class AnimatedButton(QPushButton):
    """Button with smooth animations"""
    
    def __init__(self, text, variant='primary', parent=None, theme=Theme.LIGHT):
        super().__init__(text, parent)
        self.variant = variant
        self.theme = theme
        self.setup_style()
        
    def setup_style(self):
        if self.variant == 'primary':
            self.setStyleSheet(StyleSheet.button_primary(self.theme))
        else:
            self.setStyleSheet(StyleSheet.button_secondary(self.theme))
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(get_font('primary', 'base', 'semibold'))


# ============================================================================
# LOADING SPINNER
# ============================================================================

class ModernSpinner(QWidget):
    """Smooth circular loading spinner"""
    
    def __init__(self, size=32, parent=None, theme=Theme.LIGHT):
        super().__init__(parent)
        self.theme = theme
        self.size = size
        self.angle = 0
        self.setFixedSize(size, size)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def start(self):
        """Start spinning"""
        self.timer.start(16)  # ~60 FPS
        self.show()
        
    def stop(self):
        """Stop spinning"""
        self.timer.stop()
        self.hide()
        
    def rotate(self):
        """Rotate animation"""
        self.angle = (self.angle + 6) % 360
        self.update()
        
    def paintEvent(self, event):
        """Draw spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = Colors.DARK if self.theme == Theme.DARK else Colors.LIGHT
        
        # Draw circular gradient
        gradient = QConicalGradient(self.size/2, self.size/2, self.angle)
        gradient.setColorAt(0, QColor(colors['primary']))
        gradient.setColorAt(0.5, QColor(colors['primary_hover']))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        pen = QPen()
        pen.setWidth(3)
        pen.setBrush(gradient)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        painter.setPen(pen)
        painter.drawArc(3, 3, self.size-6, self.size-6, 0, 270 * 16)


# ============================================================================
# TOAST NOTIFICATION
# ============================================================================

class ToastNotification(QWidget):
    """Modern toast notification"""
    
    closed = pyqtSignal()
    
    def __init__(self, message, type='info', duration=3000, parent=None, theme=Theme.LIGHT):
        super().__init__(parent)
        self.theme = theme
        self.duration = duration
        self.setup_ui(message, type)
        
    def setup_ui(self, message, type):
        colors = Colors.DARK if self.theme == Theme.DARK else Colors.LIGHT
        
        # Icon mapping
        icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        }
        
        # Color mapping
        type_colors = {
            'success': colors['success'],
            'error': colors['error'],
            'warning': colors['warning'],
            'info': colors['info']
        }
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.setSpacing(Spacing.SM)
        
        # Icon
        icon_label = QLabel(icons.get(type, 'ℹ'))
        icon_label.setFont(get_font('primary', 'lg', 'bold'))
        icon_label.setStyleSheet(f"color: {type_colors.get(type, colors['info'])};")
        layout.addWidget(icon_label)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setFont(get_font('primary', 'base', 'medium'))
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label, 1)
        
        # Style
        self.setStyleSheet(f"""
            ToastNotification {{
                background: {colors['bg_primary']};
                border: 1px solid {type_colors.get(type, colors['border'])};
                border-left: 4px solid {type_colors.get(type, colors['primary'])};
                border-radius: {BorderRadius.MD}px;
            }}
        """)
        
        self.setFixedWidth(400)
        self.adjustSize()
        
    def show_animated(self, parent_widget):
        """Show with slide-in animation"""
        self.setParent(parent_widget)
        
        # Position at top-right
        x = parent_widget.width() - self.width() - Spacing.LG
        y = Spacing.LG
        
        # Start off-screen
        self.move(parent_widget.width(), y)
        self.show()
        
        # Slide in
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(Animation.DURATIONS['normal'])
        self.anim.setStartValue(QPoint(parent_widget.width(), y))
        self.anim.setEndValue(QPoint(x, y))
        self.anim.setEasingCurve(Animation.EASING['ease_out'])
        self.anim.start()
        
        # Auto-dismiss
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.hide_animated)
            
    def hide_animated(self):
        """Hide with fade-out animation"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(Animation.DURATIONS['fast'])
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setEasingCurve(Animation.EASING['ease_in'])
        self.fade_anim.finished.connect(self.close)
        self.fade_anim.finished.connect(self.closed.emit)
        self.fade_anim.start()


# ============================================================================
# STAT CARD
# ============================================================================

class StatCard(ModernCard):
    """Animated stat display card"""
    
    def __init__(self, title, value, icon='', color='primary', parent=None, theme=Theme.LIGHT):
        super().__init__(parent, theme)
        self.setup_content(title, value, icon, color)
        
    def setup_content(self, title, value, icon, color):
        colors = Colors.DARK if self.theme == Theme.DARK else Colors.LIGHT
        
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.SM)
        
        # Icon
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(get_font('primary', '2xl', 'bold'))
            icon_label.setStyleSheet(f"color: {colors[color]};")
            layout.addWidget(icon_label)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setFont(get_font('display', '3xl', 'bold'))
        self.value_label.setStyleSheet(f"color: {colors['text_primary']};")
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(get_font('primary', 'sm', 'medium'))
        title_label.setStyleSheet(f"color: {colors['text_secondary']};")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
    def update_value(self, new_value):
        """Update value with animation"""
        # TODO: Add number counting animation
        self.value_label.setText(str(new_value))


# ============================================================================
# ACTIVITY ITEM
# ============================================================================

class ActivityItem(QWidget):
    """Single activity list item"""
    
    def __init__(self, icon, title, subtitle, time, parent=None, theme=Theme.LIGHT):
        super().__init__(parent)
        self.theme = theme
        self.setup_ui(icon, title, subtitle, time)
        
    def setup_ui(self, icon, title, subtitle, time):
        colors = Colors.DARK if self.theme == Theme.DARK else Colors.LIGHT
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.setSpacing(Spacing.MD)
        
        # Icon/Indicator
        indicator = QLabel(icon)
        indicator.setFont(get_font('primary', 'lg'))
        indicator.setFixedSize(32, 32)
        indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        indicator.setStyleSheet(f"""
            background: {colors['primary_light']};
            color: {colors['primary']};
            border-radius: 16px;
        """)
        layout.addWidget(indicator)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(get_font('primary', 'base', 'semibold'))
        content_layout.addWidget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(get_font('primary', 'sm', 'regular'))
            subtitle_label.setStyleSheet(f"color: {colors['text_secondary']};")
            content_layout.addWidget(subtitle_label)
        
        layout.addLayout(content_layout, 1)
        
        # Time
        time_label = QLabel(time)
        time_label.setFont(get_font('primary', 'sm', 'regular'))
        time_label.setStyleSheet(f"color: {colors['text_tertiary']};")
        layout.addWidget(time_label)
        
        # Hover effect
        self.setStyleSheet(f"""
            ActivityItem {{
                background: transparent;
                border-radius: {BorderRadius.MD}px;
            }}
            ActivityItem:hover {{
                background: {colors['bg_hover']};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


# ============================================================================
# MODERN PROGRESS BAR
# ============================================================================

class ModernProgressBar(QWidget):
    """Smooth animated progress bar"""
    
    def __init__(self, parent=None, theme=Theme.LIGHT):
        super().__init__(parent)
        self.theme = theme
        self.progress = 0
        self.setFixedHeight(8)
        
    def set_progress(self, value):
        """Set progress with animation"""
        self.target_progress = max(0, min(100, value))
        
        # Animate to new value
        self.anim = QPropertyAnimation(self, b"progress_value")
        self.anim.setDuration(Animation.DURATIONS['normal'])
        self.anim.setStartValue(self.progress)
        self.anim.setEndValue(self.target_progress)
        self.anim.setEasingCurve(Animation.EASING['ease_out'])
        self.anim.valueChanged.connect(lambda v: self.update())
        self.anim.start()
        
    def paintEvent(self, event):
        """Draw progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = Colors.DARK if self.theme == Theme.DARK else Colors.LIGHT
        
        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors['bg_tertiary']))
        painter.drawRoundedRect(self.rect(), 4, 4)
        
        # Progress
        if self.progress > 0:
            progress_width = int(self.width() * (self.progress / 100))
            
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor(colors['primary']))
            gradient.setColorAt(1, QColor(colors['primary_hover']))
            
            painter.setBrush(gradient)
            painter.drawRoundedRect(0, 0, progress_width, self.height(), 4, 4)
    
    def get_progress_value(self):
        return self.progress
    
    def set_progress_value(self, value):
        self.progress = value
        self.update()
    
    progress_value = property(get_progress_value, set_progress_value)
