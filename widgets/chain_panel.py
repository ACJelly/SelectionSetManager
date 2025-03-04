Copy#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hierarchy chain selection panel for the Selection Set Manager.
This file contains the ChainSelectionPanel class for working with hierarchical
chains of objects in Maya.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui

class ChainSelectionPanel(QtWidgets.QWidget):
    """Panel for hierarchy chain selection tools"""
    
    def __init__(self, manager, parent=None):
        super(ChainSelectionPanel, self).__init__(parent)
        self.manager = manager
        self.create_ui()
    
    def create_ui(self):
        """Create the chain selection UI"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)
        
        # Create "Chain Selection:" label
        label = QtWidgets.QLabel("Chain Selection:")
        label.setStyleSheet("color: #ddd;")
        layout.addWidget(label)
        
        # Create buttons for chain operations
        self.select_chain_btn = QtWidgets.QPushButton("Select Chain")
        self.select_chain_btn.setToolTip(
            "Select all children of the currently selected object"
        )
        
        self.create_chain_set_btn = QtWidgets.QPushButton("Create Chain Set")
        self.create_chain_set_btn.setToolTip(
            "Create a selection set from the selected object and all its children"
        )
        
        # Add separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: #555;")
        
        # Create text field and label for chain name
        name_label = QtWidgets.QLabel("Set Name:")
        name_label.setStyleSheet("color: #ddd;")
        
        self.chain_name_field = QtWidgets.QLineEdit()
        self.chain_name_field.setPlaceholderText("Auto")
        self.chain_name_field.setFixedWidth(100)
        
        # Add to layout
        layout.addWidget(self.select_chain_btn)
        layout.addWidget(separator)
        layout.addWidget(self.create_chain_set_btn)
        layout.addWidget(name_label)
        layout.addWidget(self.chain_name_field)
        layout.addStretch()
        
        # Connect signals
        self.select_chain_btn.clicked.connect(self.select_chain)
        self.create_chain_set_btn.clicked.connect(self.create_chain_set)
    
    def select_chain(self):
        """Select the hierarchy chain from selected object"""
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            cmds.warning("Nothing selected. Please select a top node first.")
            return
        
        # Use the first selected object as the top node
        top_node = selection[0]
        self.manager.select_hierarchy_chain(top_node)
    
    def create_chain_set(self):
        """Create a set from the hierarchy chain"""
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            cmds.warning("Nothing selected. Please select a top node first.")
            return
        
        # Use the first selected object as the top node
        top_node = selection[0]
        
        # Get custom name if provided
        custom_name = self.chain_name_field.text().strip()
        
        # Create the set
        result = self.manager.create_chain_set(top_node, custom_name if custom_name else None)
        
        # Add to workspace
        if result and hasattr(self.parent(), 'workspace'):
            self.parent().workspace.add_set_widget(result)
