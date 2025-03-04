#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Set widget for the Selection Set Manager.
This file contains the DraggableSetWidget class for visual representation
of selection sets.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui
import math
from functools import partial

from widgets.base_widgets import ResizeHandle, get_color_menu, get_transparency_menu, show_color_picker

class DraggableSetWidget(QtWidgets.QWidget):
    """Custom draggable widget for each set in the workspace"""
    
    def __init__(self, set_name, parent=None):
        super(DraggableSetWidget, self).__init__(parent)
        self.set_name = set_name
        self.expanded = False
        self.drag_position = None
        self.click_without_drag = False
        
        # Set minimum size
        self.setMinimumSize(100, 30)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        
        # Enable positioning and drag/drop
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.setAcceptDrops(True)
        
        # Enable drag and drop
        self.setMouseTracking(True)
        
        # Default styling
        self.bg_color = [70, 70, 70]
        self.bg_transparency = 180
        
        self.createUI()
    
    def createUI(self):
        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.setSpacing(2)
        
        # Header layout with title bar styling
        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)
        header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(8, 2, 8, 2)
        
        # Expand/collapse button
        self.expand_btn = QtWidgets.QToolButton()
        self.expand_btn.setArrowType(QtCore.Qt.RightArrow)
        self.expand_btn.setStyleSheet("QToolButton { background-color: transparent; }")
        self.expand_btn.setFixedSize(16, 16)
        
        # Set name label
        self.label = QtWidgets.QLabel(self.set_name)
        self.label.setStyleSheet("QLabel { font-weight: bold; color: #ddd; }")
        
        # Close button
        self.close_btn = QtWidgets.QToolButton()
        self.close_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton))
        self.close_btn.setStyleSheet("QToolButton { background-color: transparent; }")
        self.close_btn.setFixedSize(16, 16)
        
        # Add widgets to header layout
        header_layout.addWidget(self.expand_btn)
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)
        
        # Content widget (hidden by default)
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(4)
        self.content_widget.setVisible(False)
        
        # Add list widget for objects
        self.object_list = QtWidgets.QListWidget()
        self.object_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.object_list.setDragEnabled(False)
        self.object_list.setAlternatingRowColors(True)
        self.object_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(50, 50, 50, 120);
                border-radius: 3px;
                border: 1px solid #555;
                padding: 2px;
            }
            QListWidget::item {
                padding: 2px;
            }
            QListWidget::item:hover {
                background-color: rgba(100, 100, 100, 120);
            }
            QListWidget::item:selected {
                background-color: rgba(0, 160, 230, 120);
            }
            QListWidget::item:alternate {
                background-color: rgba(60, 60, 60, 120);
            }
        """)
        self.content_layout.addWidget(self.object_list)
        
        # Add layouts to main layout
        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.content_widget)
        
        # Add resize handle
        self.resize_handle = ResizeHandle(self)
        
        # Set up widget styling
        self.update_style()
        
        # Connect signals
        self.expand_btn.clicked.connect(self.toggle_expansion)
        self.close_btn.clicked.connect(self.request_deletion)
        
        # Position resize handle
        self.resize_handle.move(self.width() - 10, self.height() - 10)
    
    def update_style(self):
        """Update the widget style based on color and transparency"""
        r, g, b = self.bg_color
        a = self.bg_transparency
        self.setStyleSheet(f"""
            DraggableSetWidget {{
                background-color: rgba({r}, {g}, {b}, {a});
                border-radius: 5px;
                border: 1px solid #777;
            }}
        """)
    
    def set_color(self, r, g, b):
        """Set the background color of the widget"""
        self.bg_color = [r, g, b]
        self.update_style()
    
    def set_transparency(self, transparency):
        """Set the transparency of the widget"""
        self.bg_transparency = transparency
        self.update_style()
    
    def toggle_expansion(self):
        self.expanded = not self.expanded
        self.content_widget.setVisible(self.expanded)
        arrow_type = QtCore.Qt.DownArrow if self.expanded else QtCore.Qt.RightArrow
        self.expand_btn.setArrowType(arrow_type)
        
        # Adjust size based on expansion state
        if self.expanded:
            current_size = self.size()
            if current_size.height() < 100:
                self.resize(current_size.width(), 200)
    
    def handle_resize(self, width, height):
        """Handle resize from the resize handle"""
        # Notify parent of the size change
        if hasattr(self.parent(), 'update_widget_size'):
            self.parent().update_widget_size(self.set_name, width, height)
        
        # Update resize handle position
        self.resize_handle.move(self.width() - 10, self.height() - 10)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super(DraggableSetWidget, self).resizeEvent(event)
        # Update resize handle position
        self.resize_handle.move(self.width() - 10, self.height() - 10)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Check if the click is on the header
            if self.header_widget.geometry().contains(event.pos()):
                # Store the initial position for dragging
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                # Also store that we're in a potential selection operation
                self.click_without_drag = True
                event.accept()
            else:
                # If clicking elsewhere in the widget (not header), just select the set
                self.parent().select_set(self.set_name)
                event.accept()
        else:
            # Let the QWidget's context menu system handle right clicks
            super(DraggableSetWidget, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            # We're dragging, so this isn't a click-to-select operation
            if hasattr(self, 'click_without_drag'):
                self.click_without_drag = False
            
            # Start drag operation if moving beyond threshold
            if (event.pos() - self.drag_position).manhattanLength() > QtWidgets.QApplication.startDragDistance():
                self.startDrag(event.globalPos())
                return
            
            # Move the widget during drag
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()
        super(DraggableSetWidget, self).mouseMoveEvent(event)
    
    def startDrag(self, global_pos):
        """Start dragging this set widget"""
        # Create drag object
        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        
        # Store set name in mime data
        mime_data.setText(self.set_name)
        mime_data.setObjectName("set_widget")
        
        # Create a pixmap of this widget for the drag image
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setMimeData(mime_data)
        
        # Set hotspot to the cursor position
        drag.setHotSpot(self.drag_position)
        
        # Execute the drag
        result = drag.exec_(QtCore.Qt.MoveAction)
        
        # Clear the drag position
        self.drag_position = None
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Clear the drag position
            self.drag_position = None
            
            # Update the position in the manager
            self.parent().update_widget_position(self.set_name, self.pos().x(), self.pos().y())
            
            # If this was a click without drag on the header, select the set
            if hasattr(self, 'click_without_drag') and self.click_without_drag:
                self.parent().select_set(self.set_name)
            
            # Reset the click state
            self.click_without_drag = False
        super(DraggableSetWidget, self).mouseReleaseEvent(event)
    
    def update_label(self, new_name):
        self.set_name = new_name
        self.label.setText(new_name)
    
    def set_objects(self, objects):
        self.object_list.clear()
        for obj in objects:
            # Display short name but store long name
            short_name = obj.split("|")[-1]
            item = QtWidgets.QListWidgetItem(short_name)
            item.setData(QtCore.Qt.UserRole, obj)
            self.object_list.addItem(item)
    
    def request_deletion(self):
        self.parent().delete_widget(self.set_name)
    
    def show_context_menu(self, position):
        """Show context menu for this set widget"""
        menu = QtWidgets.QMenu(self)
        
        # Add actions
        select_action = menu.addAction("Select All Objects")
        select_action.triggered.connect(lambda: self.parent().select_set(self.set_name))
        
        rename_action = menu.addAction("Rename Set")
        rename_action.triggered.connect(lambda: self.parent().rename_widget(self.set_name))
        
        # Add color submenu
        parent_widget = self.parent()
        color_menu = get_color_menu(
            "Set Color", 
            self, 
            lambda r, g, b: parent_widget.update_widget_color(self.set_name, r, g, b)
        )
        menu.addMenu(color_menu)
        
        # Add transparency submenu
        transp_menu = get_transparency_menu(
            "Set Transparency", 
            self, 
            lambda t: parent_widget.update_widget_transparency(self.set_name, t)
        )
        menu.addMenu(transp_menu)
        
        # Add parent submenu
        parent_menu = menu.addMenu("Set Parent")
        
        # No parent option
        none_action = parent_menu.addAction("None")
        none_action.triggered.connect(
            lambda: parent_widget.set_widget_parent(self.set_name, None)
        )
        
        # List all potential parents (other sets)
        parent_menu.addSeparator()
        for other_name in parent_widget.set_widgets:
            if other_name != self.set_name:
                action = parent_menu.addAction(other_name)
                action.triggered.connect(
                    partial(parent_widget.set_widget_parent, self.set_name, other_name)
                )
        
        # Add to group submenu
        group_menu = menu.addMenu("Add to Group")
        
        # No group option
        none_group_action = group_menu.addAction("None (Remove from Groups)")
        none_group_action.triggered.connect(
            lambda: parent_widget.remove_set_from_group(self.set_name)
        )
        
        # List all available groups
        if parent_widget.group_widgets:
            group_menu.addSeparator()
            for group_name in parent_widget.group_widgets:
                action = group_menu.addAction(group_name)
                action.triggered.connect(
                    partial(parent_widget.add_set_to_group, self.set_name, group_name)
                )
        
        # Add delete option
        menu.addSeparator()
        delete_action = menu.addAction("Delete Set")
        delete_action.triggered.connect(lambda: self.request_deletion())
        
        # Show the menu at the specified position
        menu.exec_(self.mapToGlobal(position))