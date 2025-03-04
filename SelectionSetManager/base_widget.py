#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base widgets for the Selection Set Manager.
This file contains reusable widget components used throughout the application.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui

class ResizeHandle(QtWidgets.QWidget):
    """Resize handle for widgets"""
    
    def __init__(self, parent=None):
        super(ResizeHandle, self).__init__(parent)
        self.setFixedSize(10, 10)
        self.setCursor(QtCore.Qt.SizeFDiagCursor)
        
        # Set style
        self.setStyleSheet("""
            ResizeHandle {
                background-color: #777;
                border-radius: 2px;
            }
            ResizeHandle:hover {
                background-color: #999;
            }
        """)
        
        self.dragging = False
        self.drag_start_pos = None
        self.parent_start_size = None
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos()
            self.parent_start_size = self.parent().size()
            event.accept()
        else:
            super(ResizeHandle, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == QtCore.Qt.LeftButton:
            delta = event.globalPos() - self.drag_start_pos
            new_width = max(100, self.parent_start_size.width() + delta.x())
            new_height = max(50, self.parent_start_size.height() + delta.y())
            
            self.parent().resize(new_width, new_height)
            # Inform the parent widget about resize
            self.parent().handle_resize(new_width, new_height)
            event.accept()
        else:
            super(ResizeHandle, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.dragging:
            self.dragging = False
            event.accept()
        else:
            super(ResizeHandle, self).mouseReleaseEvent(event)


def get_color_menu(title, parent_widget, set_color_callback):
    """
    Create a color selection submenu
    
    Args:
        title (str): The title of the submenu
        parent_widget (QWidget): Parent widget for the menu
        set_color_callback (function): Callback function to handle color selection
                                       Should accept r, g, b parameters
    
    Returns:
        QMenu: The created color submenu
    """
    color_menu = QtWidgets.QMenu(title, parent_widget)
    
    # Predefined colors
    colors = [
        ("Red", QtGui.QColor(180, 60, 60)),
        ("Green", QtGui.QColor(60, 180, 60)),
        ("Blue", QtGui.QColor(60, 60, 180)),
        ("Yellow", QtGui.QColor(180, 180, 60)),
        ("Cyan", QtGui.QColor(60, 180, 180)),
        ("Magenta", QtGui.QColor(180, 60, 180)),
        ("Gray", QtGui.QColor(120, 120, 120)),
        ("Dark Gray", QtGui.QColor(70, 70, 70)),
        ("Light Gray", QtGui.QColor(180, 180, 180))
    ]
    
    for name, color in colors:
        action = color_menu.addAction(name)
        # Create color icon
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(color)
        action.setIcon(QtGui.QIcon(pixmap))
        action.triggered.connect(
            lambda checked=False, r=color.red(), g=color.green(), b=color.blue(): 
            set_color_callback(r, g, b)
        )
    
    # Add custom color picker option
    color_menu.addSeparator()
    custom_action = color_menu.addAction("Custom...")
    custom_action.triggered.connect(
        lambda: show_color_picker(parent_widget, set_color_callback)
    )
    
    return color_menu


def get_transparency_menu(title, parent_widget, set_transparency_callback):
    """
    Create a transparency selection submenu
    
    Args:
        title (str): The title of the submenu
        parent_widget (QWidget): Parent widget for the menu
        set_transparency_callback (function): Callback function to handle transparency selection
                                             Should accept a transparency parameter (0-255)
    
    Returns:
        QMenu: The created transparency submenu
    """
    transp_menu = QtWidgets.QMenu(title, parent_widget)
    
    # Transparency options
    for transp in [255, 200, 150, 100, 50]:
        percentage = int((transp/255.0)*100)
        action = transp_menu.addAction(f"{percentage}%")
        action.triggered.connect(
            lambda checked=False, t=transp: set_transparency_callback(t)
        )
    
    return transp_menu


def show_color_picker(parent_widget, set_color_callback, initial_color=None):
    """
    Show a color picker dialog and call the callback with the selected color
    
    Args:
        parent_widget (QWidget): Parent widget for the dialog
        set_color_callback (function): Callback function to handle color selection
        initial_color (QColor, optional): Initial color to show in the dialog
    """
    if initial_color is None:
        initial_color = QtGui.QColor(70, 70, 70)
    
    color = QtWidgets.QColorDialog.getColor(
        initial_color, parent_widget, "Choose Color"
    )
    
    if color.isValid():
        set_color_callback(color.red(), color.green(), color.blue())