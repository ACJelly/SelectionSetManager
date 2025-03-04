#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main UI for the Selection Set Manager.
This file contains the SelectionSetUI class which integrates all components
into a unified interface.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui
import os

from managers import SelectionSetManager
from widgets.workspace import SelectionSetWorkspace
from widgets.channel_panel import ChannelSelectionPanel
from widgets.chain_panel import ChainSelectionPanel
from utils import maya_main_window

class SelectionSetUI(QtWidgets.QDialog):
    """UI for the Selection Set Manager"""
    
    def __init__(self, parent=maya_main_window()):
        super(SelectionSetUI, self).__init__(parent)
        
        self.setWindowTitle("Advanced Selection Set Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        
        self.manager = SelectionSetManager()
        
        self.create_ui()
        self.create_connections()
        self.apply_stylesheet()
    
    def create_ui(self):
        """Create the UI layout and widgets"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)
        
        # Top panel with tabs
        self.top_panel = QtWidgets.QTabWidget()
        
        # Channel selection panel
        self.channel_panel = ChannelSelectionPanel(self.manager)
        self.top_panel.addTab(self.channel_panel, "Channel Selection")
        
        # Chain selection panel
        self.chain_panel = ChainSelectionPanel(self.manager)
        self.top_panel.addTab(self.chain_panel, "Hierarchy Tools")
        
        # Add to main layout
        main_layout.addWidget(self.top_panel)
        
        # Toolbar layout
        toolbar_layout = QtWidgets.QHBoxLayout()
        
        # Create set button
        self.create_btn = QtWidgets.QPushButton("Create Set")
        self.create_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder))
        
        # Create parent group button
        self.create_group_btn = QtWidgets.QPushButton("Create Group")
        self.create_group_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        
        # Set background image button
        self.bg_image_btn = QtWidgets.QPushButton("Set Background Image")
        self.bg_image_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogInfoView))
        
        # Export/Import buttons
        self.export_btn = QtWidgets.QPushButton("Export Sets")
        self.export_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
        
        self.import_btn = QtWidgets.QPushButton("Import Sets")
        self.import_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))
        
        # Add buttons to toolbar
        toolbar_layout.addWidget(self.create_btn)
        toolbar_layout.addWidget(self.create_group_btn)
        toolbar_layout.addWidget(self.bg_image_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.import_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # Create workspace for draggable sets
        self.workspace = SelectionSetWorkspace()
        self.workspace.set_manager(self.manager)
        self.workspace.setMinimumSize(780, 450)
        
        # Add workspace to main layout with a frame
        workspace_frame = QtWidgets.QFrame()
        workspace_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        workspace_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        workspace_frame.setStyleSheet("QFrame { background-color: #333; border: 1px solid #555; }")
        
        workspace_layout = QtWidgets.QVBoxLayout(workspace_frame)
        workspace_layout.setContentsMargins(1, 1, 1, 1)
        workspace_layout.addWidget(self.workspace)
        
        main_layout.addWidget(workspace_frame)
        
        # Info label
        self.info_label = QtWidgets.QLabel(
            "Drag sets to position them. Right-click on a set for options. "
            "Resize from the bottom-right corner."
        )
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa; font-style: italic;")
        main_layout.addWidget(self.info_label)
    
    def create_connections(self):
        """Connect UI signals to slots"""
        self.create_btn.clicked.connect(self.create_set)
        self.create_group_btn.clicked.connect(self.create_parent_group)
        self.bg_image_btn.clicked.connect(self.set_background_image)
        self.export_btn.clicked.connect(self.export_sets)
        self.import_btn.clicked.connect(self.import_sets)
        
        # Connect channel selection panel signals
        self.channel_panel.channelsChanged.connect(self.on_channels_changed)
    
    def create_parent_group(self):
        """Create a new parent group"""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Create Parent Group", "Group Name:", text="Group"
        )
        
        if ok and name:
            result = self.manager.create_parent_group(name)
            if result:
                self.workspace.add_parent_group_widget(result)
    
    def on_channels_changed(self):
        """Handle changes to channel selection"""
        # Get current selection
        selected = cmds.ls(selection=True)
        
        if selected:
            # Store the current selection to restore it with new channel settings
            selected_objects = selected
            
            # Re-select the same objects but with the new channel settings
            cmds.select(clear=True)
            self.manager.select_objects_with_channel_filtering(selected_objects)
    
    def apply_stylesheet(self):
        """Apply custom stylesheet to the UI"""
        self.setStyleSheet("""
            QDialog {
                background-color: #3c3c3c;
                color: #ddd;
            }
            QPushButton {
                background-color: #555;
                color: #ddd;
                border-radius: 3px;
                border: 1px solid #666;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #666;
                border: 1px solid #777;
            }
            QPushButton:pressed {
                background-color: #444;
            }
            QLabel {
                color: #ddd;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #444;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #ddd;
                padding: 4px 10px;
                border: 1px solid #555;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #444;
                border-bottom: 1px solid #444;
            }
            QLineEdit {
                background-color: #555;
                color: #ddd;
                border: 1px solid #777;
                padding: 2px 4px;
                border-radius: 2px;
            }
        """)
    
    def create_set(self):
        """Create a new set from current selection"""
        result = self.manager.create_set()
        if result:
            self.workspace.add_set_widget(result)
    
    def set_background_image(self):
        """Set a background image for the workspace"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Background Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            # Set the image in manager and workspace
            self.manager.set_background_image(file_path)
            self.workspace.set_background_image(file_path)
    
    def export_sets(self):
        """Export sets to a JSON file"""
        if not self.manager.sets and not self.manager.parent_groups:
            cmds.warning("No sets or groups to export.")
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Selection Sets", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if not file_path.endswith(".json"):
                file_path += ".json"
            
            # Update positions and sizes from workspace before exporting
            for set_name, widget in self.workspace.set_widgets.items():
                self.manager.update_set_position(
                    set_name, widget.pos().x(), widget.pos().y()
                )
                self.manager.update_set_size(
                    set_name, widget.width(), widget.height()
                )
            
            # Update parent group positions and sizes
            for group_name, widget in self.workspace.group_widgets.items():
                self.manager.update_group_position(
                    group_name, widget.pos().x(), widget.pos().y()
                )
                self.manager.update_group_size(
                    group_name, widget.width(), widget.height()
                )
            
            if self.manager.export_sets(file_path):
                cmds.inViewMessage(
                    amg=f"Successfully exported sets to {os.path.basename(file_path)}",
                    pos='midCenter', fade=True
                )
    
    def import_sets(self):
        """Import sets from a JSON file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Selection Sets", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if self.manager.import_sets(file_path):
                # Clear existing widgets
                for widget in list(self.workspace.set_widgets.values()):
                    widget.setParent(None)
                    widget.deleteLater()
                self.workspace.set_widgets.clear()
                
                for widget in list(self.workspace.group_widgets.values()):
                    widget.setParent(None)
                    widget.deleteLater()
                self.workspace.group_widgets.clear()
                
                # Add parent group widgets
                for group_name in self.manager.parent_groups:
                    # Get position
                    pos_x, pos_y = None, None
                    if group_name in self.manager.group_positions:
                        pos_x, pos_y = self.manager.group_positions[group_name]
                    
                    # Get size
                    width, height = None, None
                    if group_name in self.manager.group_sizes:
                        width, height = self.manager.group_sizes[group_name]
                    
                    # Add the widget
                    self.workspace.add_parent_group_widget(group_name, pos_x, pos_y, width, height)
                
                # Add new set widgets with all properties
                for set_name in self.manager.sets:
                    # Get position
                    pos_x, pos_y = None, None
                    if set_name in self.manager.set_positions:
                        pos_x, pos_y = self.manager.set_positions[set_name]
                    
                    # Get size
                    width, height = None, None
                    if set_name in self.manager.set_sizes:
                        width, height = self.manager.set_sizes[set_name]
                    
                    # Add the widget
                    self.workspace.add_set_widget(set_name, pos_x, pos_y, width, height)
                    
                    # Set properties
                    if set_name in self.manager.set_colors:
                        r, g, b = self.manager.set_colors[set_name]
                        self.workspace.update_widget_color(set_name, r, g, b)
                    
                    if set_name in self.manager.set_transparency:
                        transp = self.manager.set_transparency[set_name]
                        self.workspace.update_widget_transparency(set_name, transp)
                
                # Add sets to groups
                for group_name, set_names in self.manager.parent_groups.items():
                    for set_name in set_names:
                        self.workspace.add_set_to_group(set_name, group_name)
                
                # Set background image if one was imported
                if self.manager.background_image:
                    self.workspace.set_background_image(self.manager.background_image)
                
                # Update parent-child relationships
                self.workspace.update_widget_parent_indicators()
                
                cmds.inViewMessage(
                    amg=f"Successfully imported sets from {os.path.basename(file_path)}",
                    pos='midCenter', fade=True
                )