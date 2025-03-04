#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Group widget for the Selection Set Manager.
This file contains the ParentGroupWidget class for visual representation
of parent groups that can contain sets.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui
from functools import partial

from widgets.base_widgets import ResizeHandle, get_color_menu, get_transparency_menu, show_color_picker

class ParentGroupWidget(QtWidgets.QWidget):
    """Custom widget for parent groups that contain sets but are not sets themselves"""
    
    def __init__(self, group_name, parent=None):
        super(ParentGroupWidget, self).__init__(parent)
        self.group_name = group_name
        self.expanded = False
        self.drag_position = None
        self.click_without_drag = False
        self.child_widgets = {}  # To track child set widgets: {set_name: widget_reference}
        
        # Set minimum size
        self.setMinimumSize(150, 40)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        
        # Enable positioning
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        
        # Enable drop for drag-drop operations
        self.setAcceptDrops(True)
        
        # Default styling
        self.bg_color = [100, 100, 60]  # Yellowish
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
                background-color: #5a5a3a;
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
        
        # Group name label with special styling to distinguish from sets
        self.label = QtWidgets.QLabel(f"Group: {self.group_name}")
        self.label.setStyleSheet("QLabel { font-weight: bold; color: #ff9; }")
        
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
        
        # Container for child set widgets
        self.children_container = QtWidgets.QWidget()
        self.children_layout = QtWidgets.QVBoxLayout(self.children_container)
        self.children_layout.setContentsMargins(2, 2, 2, 2)
        self.children_layout.setSpacing(4)
        self.content_layout.addWidget(self.children_container)
        
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
            ParentGroupWidget {{
                background-color: rgba({r}, {g}, {b}, {a});
                border-radius: 5px;
                border: 1px solid #aa7;
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
            self.update_size_for_children()
    
    def update_size_for_children(self):
        """Update size to fit all child widgets"""
        if not self.expanded:
            return
        
        # Get total height needed for all child sets
        total_height = 40  # Header height
        for child_widget in self.child_widgets.values():
            child_height = child_widget.height() if child_widget.isVisible() else 0
            total_height += child_height + 4  # Adding spacing
        
        # Add padding
        total_height += 16
        
        # Get maximum width needed
        max_width = 300  # Default minimum width
        for child_widget in self.child_widgets.values():
            if child_widget.isVisible() and child_widget.width() > max_width:
                max_width = child_widget.width()
        
        # Add padding
        max_width += 24
        
        # Resize the group
        self.resize(max_width, total_height)
        
        # Notify parent of the size change
        if hasattr(self.parent(), 'update_group_size'):
            self.parent().update_group_size(self.group_name, max_width, total_height)
        
        # Update resize handle position
        self.resize_handle.move(self.width() - 10, self.height() - 10)
    
    def handle_resize(self, width, height):
        """Handle resize from the resize handle"""
        # Notify parent of the size change
        if hasattr(self.parent(), 'update_group_size'):
            self.parent().update_group_size(self.group_name, width, height)
        
        # Update resize handle position
        self.resize_handle.move(self.width() - 10, self.height() - 10)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super(ParentGroupWidget, self).resizeEvent(event)
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
            # No else here because we don't select anything for groups
        else:
            # Let the QWidget's context menu system handle right clicks
            super(ParentGroupWidget, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            # We're dragging, so this isn't a click-to-select operation
            if hasattr(self, 'click_without_drag'):
                self.click_without_drag = False
            
            # Move the widget during drag
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            
            # Notify parent of the position change
            if hasattr(self.parent(), 'update_group_position'):
                self.parent().update_group_position(self.group_name, new_pos.x(), new_pos.y())
            
            event.accept()
        super(ParentGroupWidget, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Clear the drag position
            self.drag_position = None
            
            # Update the position in the manager
            if hasattr(self.parent(), 'update_group_position'):
                self.parent().update_group_position(self.group_name, self.pos().x(), self.pos().y())
            
            # Reset the click state
            self.click_without_drag = False
        super(ParentGroupWidget, self).mouseReleaseEvent(event)
    
    def update_label(self, new_name):
        self.group_name = new_name
        self.label.setText(f"Group: {new_name}")
    
    def add_set_widget(self, set_name, widget):
        """Add a set widget to this parent group"""
        self.child_widgets[set_name] = widget
        
        # Update size if expanded
        if self.expanded:
            self.update_size_for_children()
    
    def remove_set_widget(self, set_name):
        """Remove a set widget from this parent group"""
        if set_name in self.child_widgets:
            del self.child_widgets[set_name]
            
            # Update size if expanded
            if self.expanded:
                self.update_size_for_children()
    
    def request_deletion(self):
        if hasattr(self.parent(), 'delete_group_widget'):
            self.parent().delete_group_widget(self.group_name)
    
    def show_context_menu(self, position):
        """Show context menu for this group widget"""
        menu = QtWidgets.QMenu(self)
        
        # Add rename option
        rename_action = menu.addAction("Rename Group")
        rename_action.triggered.connect(lambda: self.parent().rename_group_widget(self.group_name))
        
        # Add color submenu
        parent_widget = self.parent()
        color_menu = get_color_menu(
            "Set Color", 
            self, 
            lambda r, g, b: parent_widget.set_group_color(self.group_name, r, g, b)
        )
        menu.addMenu(color_menu)
        
        # Add transparency submenu
        transp_menu = get_transparency_menu(
            "Set Transparency", 
            self, 
            lambda t: parent_widget.update_group_transparency(self.group_name, t)
        )
        menu.addMenu(transp_menu)
        
        # Add delete option
        menu.addSeparator()
        delete_action = menu.addAction("Delete Group")
        delete_action.triggered.connect(lambda: self.request_deletion())
        
        # Show the menu at the specified position
        menu.exec_(self.mapToGlobal(position))
    
    # Drop event handlers
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        # Accept the drag if it's a set widget
        mime_data = event.mimeData()
        if mime_data.hasText():
            set_name = mime_data.text()
            if hasattr(self.parent(), 'set_widgets') and set_name in self.parent().set_widgets:
                event.acceptProposedAction()
                # Highlight the group to indicate it can accept the drop
                self.setStyleSheet(f"""
                    ParentGroupWidget {{
                        background-color: rgba({self.bg_color[0]}, {self.bg_color[1]}, {self.bg_color[2]}, {self.bg_transparency});
                        border-radius: 5px;
                        border: 2px solid #ff0;
                    }}
                """)
        
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        # Reset the highlight
        self.update_style()
        
    def dropEvent(self, event):
        """Handle drop event"""
        mime_data = event.mimeData()
        if mime_data.hasText():
            set_name = mime_data.text()
            
            # Add the set to this group
            if hasattr(self.parent(), 'set_widgets') and set_name in self.parent().set_widgets:
                self.parent().add_set_to_group(set_name, self.group_name)
                event.acceptProposedAction()
                
                # Show a feedback message
                cmds.inViewMessage(
                    amg=f"Added '{set_name}' to group '{self.group_name}'",
                    pos='topCenter', fade=True, fadeStayTime=1000
                )
                
        # Reset highlight
        self.update_style()