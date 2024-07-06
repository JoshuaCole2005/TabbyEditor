import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QListWidget, QSplitter, QFrame, 
                               QDockWidget, QScrollArea, QListWidgetItem, QSplitterHandle,
                               QRubberBand)
from PySide6.QtCore import Qt, QMimeData, QEvent, QRect
from PySide6.QtGui import QDrag, QColor, QIcon, QPainter, QPen

class DraggableWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(1)
        
        # Create title widget
        self.title_widget = QWidget()
        self.title_widget.setObjectName("panelTitle")
        self.title_widget.setFixedHeight(40)  # Set a fixed height for all titles
        title_layout = QHBoxLayout(self.title_widget)
        title_layout.setContentsMargins(10, 5, 10, 5)
        title_label = QLabel(title)
        title_layout.addWidget(title_label)
        
        layout.addWidget(self.title_widget)
        
        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("panelContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        layout.addWidget(self.content_widget)
        
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.title)
        drag.setMimeData(mime_data)
        
        self.rubber_band.setGeometry(self.rect())
        self.rubber_band.show()
        
        drag.exec(Qt.MoveAction)
        
        self.rubber_band.hide()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        source_widget = event.source()
        if source_widget != self:
            parent = self.parent()
            source_index = parent.indexOf(source_widget)
            target_index = parent.indexOf(self)
            if source_index < target_index:
                parent.insertWidget(target_index, source_widget)
                parent.insertWidget(source_index, self)
            else:
                parent.insertWidget(source_index, self)
                parent.insertWidget(target_index, source_widget)
            event.acceptProposedAction()

class OptionsPanel(DraggableWidget):
    def __init__(self, parent=None):
        super().__init__("Options", parent)
        self.list_widget = QListWidget()
        self.list_widget.addItems(["Video", "Audio", "Video Effects", "AI Features"])
        self.content_layout.addWidget(self.list_widget)

class MediaLibraryPanel(DraggableWidget):
    def __init__(self, parent=None):
        super().__init__("Media Library", parent)
        self.import_button = QPushButton()
        self.import_button.setIcon(QIcon.fromTheme("go-down"))
        self.import_button.setFixedSize(30, 30)
        self.content_layout.addWidget(self.import_button, alignment=Qt.AlignLeft | Qt.AlignTop)
        self.media_list = QListWidget()
        self.content_layout.addWidget(self.media_list)

class VideoPlayerPanel(DraggableWidget):
    def __init__(self, parent=None):
        super().__init__("Video Player", parent)
        self.player_placeholder = QWidget()
        self.player_placeholder.setMinimumHeight(200)
        self.content_layout.addWidget(self.player_placeholder)
        self.play_pause_button = QPushButton("Play/Pause")
        self.content_layout.addWidget(self.play_pause_button)

class TimelineWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(1)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Timeline"))

class CustomSplitterHandle(QSplitterHandle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            CustomSplitterHandle {
                background-color: #1a2c42;
            }
            CustomSplitterHandle:hover {
                background-color: #2c3e50;
            }
        """)
        self.is_resizing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_resizing = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_resizing = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.is_resizing:
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_resizing:
            painter = QPainter(self)
            pen = QPen(QColor(80, 200, 255))  # Bright blue color
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

class CustomSplitter(QSplitter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHandleWidth(5)
        self.setStyleSheet("""
            CustomSplitter::handle {
                background-color: #1a2c42;
            }
            CustomSplitter::handle:hover {
                background-color: #2c3e50;
            }
        """)

    def createHandle(self):
        return CustomSplitterHandle(self.orientation(), self)

class TabbyEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabby Editor")
        self.showFullScreen()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.main_splitter = CustomSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        self.options_panel = OptionsPanel()
        self.media_library_panel = MediaLibraryPanel()
        self.video_player_panel = VideoPlayerPanel()

        self.main_splitter.addWidget(self.options_panel)
        self.main_splitter.addWidget(self.media_library_panel)
        self.main_splitter.addWidget(self.video_player_panel)

        self.main_splitter.setSizes([100, 300, 600])

        self.timeline = TimelineWidget()
        main_layout.addWidget(self.timeline)

        self.create_menu_bar()
        self.apply_stylesheet()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Project")
        file_menu.addAction("Open Project")
        file_menu.addAction("Save Project")
        file_menu.addAction("Export Video")
        file_menu.addAction("Exit")

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0a192f;
                color: #e6f1ff;
            }
            QLabel {
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                background-color: #172a45;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                margin: 4px;
                color: #64ffda;
            }
            QPushButton:hover {
                background-color: #303C55;
                color: #b39ddb;
            }
            QListWidget {
                background-color: #172a45;
                border: 1px solid #303C55;
                border-radius: 8px;
                color: #8892b0;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #303C55;
                color: #b39ddb;
            }
            QMenuBar {
                background-color: #172a45;
                color: #8892b0;
                border-bottom: 1px solid #303C55;
            }
            QMenuBar::item:selected {
                background-color: #303C55;
                color: #b39ddb;
            }
            QMenu {
                background-color: #172a45;
                border: 1px solid #303C55;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #303C55;
                color: #b39ddb;
            }
            #timeline {
                border: 1px solid #303C55;
                border-radius: 8px;
                margin-top: 10px;
                padding: 5px;
            }
            DraggableWidget {
                background-color: #0f2547;
                border: 1px solid #303C55;
                border-radius: 10px;
            }
            #panelTitle {
                background-color: #0f2547;
                border: 1px solid #303C55;
                border-radius: 8px;
                margin: 1px 1px 0 1px;
            }
            #panelTitle QLabel {
                font-weight: bold;
                color: #a8d8ff;  /* Soft light blue color */
            }
            #panelContent {
                background-color: #0f2547;
                border-bottom-left-radius: 9px;
                border-bottom-right-radius: 9px;
            }
            CustomSplitter::handle {
                background-color: #0a192f;
            }
            CustomSplitter::handle:horizontal {
                width: 5px;
            }
            CustomSplitter::handle:vertical {
                height: 5px;
            }
            CustomSplitter::handle:hover {
                background-color: #303C55;
            }
        """)

def main():
    app = QApplication(sys.argv)
    editor = TabbyEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()