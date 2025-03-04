#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workspace for the Selection Set Manager.
This file contains the SelectionSetWorkspace class which serves as the
container for all set and group widgets.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui
import os
import math
from functools import partial

from widgets.set_widget import DraggableSetWidget
from widgets.group_widget import ParentGroupWidget

class SelectionSetWorkspace(QtWidgets.QWidget):
    """Workspace area for all draggable set widgets"""
    
    def __init__(self, parent=None):
        super(SelectionSetWorkspace, self).__init__(parent)
        self.set_widgets = {}  # To store references to set widgets
        self.group_widgets = {}  # To store references to parent group widgets
        self.manager = None
        self.drag_start_pos = None
        self.multi_selection = False
        self.selected_widgets = set()
        
        # Enable positioning of child widgets
        self.setAcceptDrops(True)
        
        # Background image properties
        self.background_image = None
        self.background_pixmap = None
    
    def set_manager(self, manager):
        self.manager = manager
    
    def add_set_widget(self, set_name, pos_x=None, pos_y=None, width=None, height=None):
        """Add a new draggable set widget to the workspace"""
        set_widget = DraggableSetWidget(set_name, self)
        
        # Set the objects
        set_widget.set_objects(self.manager.sets[set_name])
        
        # Set the color
        if set_name in self.manager.set_colors:
            r, g, b = self.manager.set_colors[set_name]
            set_widget.set_color(r, g, b)
        
        # Set the transparency
        if set_name in self.manager.set_transparency:
            set_widget.set_transparency(self.manager.set_transparency[set_name])
        
        # Position the widget
        if pos_x is not None and pos_y is not None:
            set_widget.move(pos_x, pos_y)
        elif set_name in self.manager.set_positions:
            set_widget.move(self.manager.set_positions[set_name][0], 
                           self.manager.set_positions[set_name][1])
        else:
            # Default position, offset from the last widget
            default_x = 20
            default_y = 20
            if self.set_widgets:
                # Get the last position and add an offset
                last_widgets = list(self.set_widgets.values())
                last_widget = last_widgets[-1]
                default_x = last_widget.pos().x() + 20
                default_y = last_widget.pos().y() + 30
            
            set_widget.move(default_x, default_y)
            self.manager.set_positions[set_name] = [default_x, default_y]
        
        # Size the widget
        if width is not None and height is not None:
            set_widget.resize(width, height)
        elif set_name in self.manager.set_sizes:
            set_widget.resize(self.manager.set_sizes[set_name][0], 
                             self.manager.set_sizes[set_name][1])
        
        # Connect object list selection
        set_widget.object_list.itemClicked.connect(
            lambda item: self.select_object(item.data(QtCore.Qt.UserRole))
        )
        
        # Show the widget
        set_widget.show()
        
        # Store reference
        self.set_widgets[set_name] = set_widget
        
        # Add context menu to the set widget
        set_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        set_widget.customContextMenuRequested.connect(
            lambda pos: set_widget.show_context_menu(pos)
        )
        
        # Make sure parent-child relationships are visually represented
        self.update_widget_parent_indicators()
        
        return set_widget
    
    def add_parent_group_widget(self, group_name, pos_x=None, pos_y=None, width=None, height=None):
        """Add a new parent group widget to the workspace"""
        group_widget = ParentGroupWidget(group_name, self)
        
        # Set the color
        if group_name in self.manager.group_colors:
            r, g, b = self.manager.group_colors[group_name]
            group_widget.set_color(r, g, b)
        
        # Set the transparency
        if group_name in self.manager.group_transparency:
            group_widget.set_transparency(self.manager.group_transparency[group_name])
        
        # Position the widget
        if pos_x is not None and pos_y is not None:
            group_widget.move(pos_x, pos_y)
        elif group_name in self.manager.group_positions:
            group_widget.move(self.manager.group_positions[group_name][0], 
                             self.manager.group_positions[group_name][1])
        else:
            # Default position
            default_x = 20
            default_y = 20
            group_widget.move(default_x, default_y)
            self.manager.group_positions[group_name] = [default_x, default_y]
        
        # Size the widget
        if width is not None and height is not None:
            group_widget.resize(width, height)
        elif group_name in self.manager.group_sizes:
            group_widget.resize(self.manager.group_sizes[group_name][0], 
                               self.manager.group_sizes[group_name][1])
        
        # Show the widget
        group_widget.show()
        
        # Store reference
        self.group_widgets[group_name] = group_widget
        
        # Add context menu to the group widget
        group_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        group_widget.customContextMenuRequested.connect(
            lambda pos: group_widget.show_context_menu(pos)
        )
        
        # Initialize any child sets
        if group_name in self.manager.parent_groups:
            for set_name in self.manager.parent_groups[group_name]:
                if set_name in self.set_widgets:
                    group_widget.add_set_widget(set_name, self.set_widgets[set_name])
        
        return group_widget
    
    def update_widget_position(self, set_name, x, y):
        """Update a widget's position in the manager"""
        if self.manager and set_name in self.set_widgets:
            self.manager.update_set_position(set_name, x, y)
            
            # If this is a parent, check if child widgets need to move
            self.update_child_widget_positions(set_name)
    
    def update_group_position(self, group_name, x, y):
        """Update a group's position in the manager"""
        if self.manager and group_name in self.group_widgets:
            self.manager.update_group_position(group_name, x, y)
    
    def update_widget_size(self, set_name, width, height):
        """Update a widget's size in the manager"""
        if self.manager and set_name in self.set_widgets:
            self.manager.update_set_size(set_name, width, height)
    
    def update_group_size(self, group_name, width, height):
        """Update a group's size in the manager"""
        if self.manager and group_name in self.group_widgets:
            self.manager.update_group_size(group_name, width, height)
    
    def update_widget_color(self, set_name, r, g, b):
        """Update a widget's color in the manager"""
        if self.manager and set_name in self.set_widgets:
            self.manager.update_set_color(set_name, r, g, b)
            self.set_widgets[set_name].set_color(r, g, b)
    
    def set_group_color(self, group_name, r, g, b):
        """Set the color of a parent group"""
        if self.manager and group_name in self.group_widgets:
            # Update in manager
            self.manager.update_group_color(group_name, r, g, b)
            
            # Update widget
            self.group_widgets[group_name].set_color(r, g, b)
    
    def update_widget_transparency(self, set_name, transparency):
        """Update a widget's transparency in the manager"""
        if self.manager and set_name in self.set_widgets:
            self.manager.update_set_transparency(set_name, transparency)
            self.set_widgets[set_name].set_transparency(transparency)
    
    def update_group_transparency(self, group_name, transparency):
        """Update a parent group's transparency"""
        if self.manager and group_name in self.group_widgets:
            # Update in manager
            self.manager.update_group_transparency(group_name, transparency)
            
            # Update widget
            self.group_widgets[group_name].set_transparency(transparency)
    
    def set_widget_parent(self, child_name, parent_name):
        """Set a parent-child relationship between widgets"""
        if not self.manager:
            return
        
        # Update in manager
        result = self.manager.set_parent(child_name, parent_name)
        if result:
            # Update visuals
            self.update_widget_parent_indicators()
            
            # If parent is moved, child should follow
            if parent_name:
                parent_pos = self.set_widgets[parent_name].pos()
                child_pos = self.set_widgets[child_name].pos()
                
                # Adjust child position relative to parent if needed
                if not self.is_inside_parent(child_name, parent_name):
                    # Move child inside parent
                    new_x = parent_pos.x() + 20
                    new_y = parent_pos.y() + 40
                    self.set_widgets[child_name].move(new_x, new_y)
                    self.manager.update_set_position(child_name, new_x, new_y)
    
    def is_inside_parent(self, child_name, parent_name):
        """Check if the child widget is visually inside the parent widget"""
        if child_name not in self.set_widgets or parent_name not in self.set_widgets:
            return False
        
        child_widget = self.set_widgets[child_name]
        parent_widget = self.set_widgets[parent_name]
        
        # Get geometries
        child_rect = child_widget.geometry()
        parent_rect = parent_widget.geometry()
        
        # Check if child is inside parent
        return parent_rect.contains(child_rect)
    
    def update_child_widget_positions(self, parent_name):
        """Update positions of child widgets when parent is moved"""
        if not self.manager:
            return
        
        # Find all children of this parent
        children = []
        for child_name, child_parent in self.manager.set_parents.items():
            if child_parent == parent_name:
                children.append(child_name)
        
        if not children:
            return
        
        parent_widget = self.set_widgets[parent_name]
        parent_pos = parent_widget.pos()
        
        # Move children that need to stay with the parent
        for child_name in children:
            if child_name in self.set_widgets:
                child_widget = self.set_widgets[child_name]
                
                # Only move if the child is inside the parent
                if self.is_inside_parent(child_name, parent_name):
                    # Maintain relative position
                    relative_x = child_widget.pos().x() - (parent_pos.x() - self.manager.set_positions[parent_name][0])
                    relative_y = child_widget.pos().y() - (parent_pos.y() - self.manager.set_positions[parent_name][1])
                    
                    # Update position
                    child_widget.move(relative_x, relative_y)
                    self.manager.update_set_position(child_name, relative_x, relative_y)
                    
                    # Recursively update child's children
                    self.update_child_widget_positions(child_name)
    
    def add_set_to_group(self, set_name, group_name):
        """Add a set to a parent group"""
        if set_name in self.set_widgets and group_name in self.group_widgets:
            # Update in manager
            self.manager.add_set_to_group(set_name, group_name)
            
            # Update in UI
            group_widget = self.group_widgets[group_name]
            set_widget = self.set_widgets[set_name]
            
            # Add to the parent group widget
            group_widget.add_set_widget(set_name, set_widget)
            
            # If the group is expanded, update its size
            if group_widget.expanded:
                group_widget.update_size_for_children()
    
    def remove_set_from_group(self, set_name, group_name=None):
        """Remove a set from a parent group or all groups"""
        if set_name in self.set_widgets:
            # Update in manager
            self.manager.remove_set_from_group(set_name, group_name)
            
            # Update in UI
            if group_name and group_name in self.group_widgets:
                group_widget = self.group_widgets[group_name]
                group_widget.remove_set_widget(set_name)
                
                # If the group is expanded, update its size
                if group_widget.expanded:
                    group_widget.update_size_for_children()
            else:
                # Remove from all groups
                for group_name, group_widget in self.group_widgets.items():
                    group_widget.remove_set_widget(set_name)
                    
                    # If the group is expanded, update its size
                    if group_widget.expanded:
                        group_widget.update_size_for_children()
    
    def update_widget_parent_indicators(self):
        """Update visual indicators of parent-child relationships"""
        # This would be implemented with painting connections between widgets
        self.update()
    
    def delete_widget(self, set_name):
        """Delete a set widget"""
        if set_name in self.set_widgets:
            widget = self.set_widgets[set_name]
            # Show confirmation dialog
            result = QtWidgets.QMessageBox.question(
                self, "Delete Set",
                f"Are you sure you want to delete the set '{set_name}'?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if result == QtWidgets.QMessageBox.Yes:
                # Remove from any groups
                self.remove_set_from_group(set_name)
                
                # Remove from manager
                self.manager.delete_set(set_name)
                
                # Remove widget
                widget.setParent(None)
                widget.deleteLater()
                del self.set_widgets[set_name]
                
                # Update parent-child visuals
                self.update_widget_parent_indicators()
    
    def delete_group_widget(self, group_name):
        """Delete a parent group widget"""
        if group_name in self.group_widgets:
            widget = self.group_widgets[group_name]
            # Show confirmation dialog
            result = QtWidgets.QMessageBox.question(
                self, "Delete Group",
                f"Are you sure you want to delete the group '{group_name}'?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if result == QtWidgets.QMessageBox.Yes:
                # Remove from manager
                self.manager.delete_parent_group(group_name)
                
                # Remove widget
                widget.setParent(None)
                widget.deleteLater()
                del self.group_widgets[group_name]
    
    def rename_widget(self, old_name):
        """Rename a set widget"""
        if old_name in self.set_widgets:
            widget = self.set_widgets[old_name]
            
            # Show input dialog for new name
            new_name, ok = QtWidgets.QInputDialog.getText(
                self, "Rename Set", "New name:", text=old_name
            )
            
            if ok and new_name and new_name != old_name:
                if self.manager.rename_set(old_name, new_name):
                    # Update widget reference in dictionary
                    widget.update_label(new_name)
                    self.set_widgets[new_name] = widget
                    del self.set_widgets[old_name]
                    
                    # Update parent-child visuals
                    self.update_widget_parent_indicators()
    
    def rename_group_widget(self, old_name):
        """Rename a parent group widget"""
        if old_name in self.group_widgets:
            widget = self.group_widgets[old_name]
            
            # Show input dialog for new name
            new_name, ok = QtWidgets.QInputDialog.getText(
                self, "Rename Group", "New name:", text=old_name
            )
            
            if ok and new_name and new_name != old_name:
                if self.manager.rename_parent_group(old_name, new_name):
                    # Update widget reference in dictionary
                    widget.update_label(new_name)
                    self.group_widgets[new_name] = widget
                    del self.group_widgets[old_name]
    
    def select_object(self, object_name):
        """Select a single object"""
        if cmds.objExists(object_name):
            # Check if shift key is pressed
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                # Add to selection
                cmds.select(object_name, add=True)
            else:
                # Replace selection
                cmds.select(object_name, replace=True)
        else:
            cmds.warning(f"Object '{object_name}' no longer exists in the scene.")
    
    def select_set(self, set_name):
        """Select all objects in a set"""
        self.manager.select_set(set_name)
    
    def set_background_image(self, image_path):
        """Set background image for the workspace"""
        if not os.path.isfile(image_path):
            cmds.warning(f"Image file not found: {image_path}")
            return False
        
        # Load and scale the image
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            self.background_image = image_path
            self.background_pixmap = pixmap
            self.update()  # Trigger repaint
            return True
        return False
        
    def paintEvent(self, event):
        """Paint background and any parent-child connections"""
        painter = QtGui.QPainter(self)
        
        # Draw background image if it exists
        if self.background_pixmap:
            # Scale image to fit the widget while maintaining aspect ratio
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            # Center the image
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        
        # Draw parent-child connections
        if self.manager:
            # Set pen for connections
            pen = QtGui.QPen(QtGui.QColor(200, 200, 200, 150))
            pen.setWidth(2)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            
            # Draw connections
            for child_name, parent_name in self.manager.set_parents.items():
                if parent_name and child_name in self.set_widgets and parent_name in self.set_widgets:
                    child_widget = self.set_widgets[child_name]
                    parent_widget = self.set_widgets[parent_name]
                    
                    # Get center points of widgets
                    child_center = child_widget.pos() + QtCore.QPoint(child_widget.width() // 2, child_widget.height() // 2)
                    parent_center = parent_widget.pos() + QtCore.QPoint(parent_widget.width() // 2, parent_widget.height() // 2)
                    
                    # Draw the connection line
                    painter.drawLine(child_center, parent_center)
                    
                    # Draw arrow head
                    arrow_size = 8
                    angle = math.atan2(child_center.y() - parent_center.y(), 
                                      child_center.x() - parent_center.x())
                    arrow_p1 = child_center - QtCore.QPoint(
                        int(arrow_size * math.cos(angle - math.pi/6)),
                        int(arrow_size * math.sin(angle - math.pi/6))
                    )
                    arrow_p2 = child_center - QtCore.QPoint(
                        int(arrow_size * math.cos(angle + math.pi/6)),
                        int(arrow_size * math.sin(angle + math.pi/6))
                    )
                    
                    # Draw arrow head
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(200, 200, 200, 150)))
                    arrow = QtGui.QPolygon([child_center, arrow_p1, arrow_p2])
                    painter.drawPolygon(arrow)