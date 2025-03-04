#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Channel selection panel for the Selection Set Manager.
This file contains the ChannelSelectionPanel class for filtering
which transform channels are included in selections.
"""

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui

class ChannelSelectionPanel(QtWidgets.QWidget):
    """Panel for channel selection settings"""
    
    channelsChanged = QtCore.Signal()
    
    def __init__(self, manager, parent=None):
        super(ChannelSelectionPanel, self).__init__(parent)
        self.manager = manager
        self.create_ui()
    
    def create_ui(self):
        """Create the channel selection UI"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Create checkboxes for channel selection
        self.tx_check = QtWidgets.QCheckBox("TX")
        self.ty_check = QtWidgets.QCheckBox("TY")
        self.tz_check = QtWidgets.QCheckBox("TZ")
        self.rx_check = QtWidgets.QCheckBox("RX")
        self.ry_check = QtWidgets.QCheckBox("RY")
        self.rz_check = QtWidgets.QCheckBox("RZ")
        
        # Style the checkboxes
        checkbox_style = """
            QCheckBox {
                color: #ddd;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #777;
                background-color: #555;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #0af;
                background-color: #0af;
            }
        """
        
        self.tx_check.setStyleSheet(checkbox_style)
        self.ty_check.setStyleSheet(checkbox_style)
        self.tz_check.setStyleSheet(checkbox_style)
        self.rx_check.setStyleSheet(checkbox_style)
        self.ry_check.setStyleSheet(checkbox_style)
        self.rz_check.setStyleSheet(checkbox_style)
        
        # Set initial state from manager
        self.tx_check.setChecked(self.manager.active_channels["tx"])
        self.ty_check.setChecked(self.manager.active_channels["ty"])
        self.tz_check.setChecked(self.manager.active_channels["tz"])
        self.rx_check.setChecked(self.manager.active_channels["rx"])
        self.ry_check.setChecked(self.manager.active_channels["ry"])
        self.rz_check.setChecked(self.manager.active_channels["rz"])
        
        # Create translate and rotate groups
        translate_layout = QtWidgets.QHBoxLayout()
        translate_layout.setSpacing(5)
        translate_layout.addWidget(self.tx_check)
        translate_layout.addWidget(self.ty_check)
        translate_layout.addWidget(self.tz_check)
        
        rotate_layout = QtWidgets.QHBoxLayout()
        rotate_layout.setSpacing(5)
        rotate_layout.addWidget(self.rx_check)
        rotate_layout.addWidget(self.ry_check)
        rotate_layout.addWidget(self.rz_check)
        
        # Add separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: #555;")
        
        # Add select all/none buttons
        select_all_btn = QtWidgets.QPushButton("All")
        select_all_btn.setFixedWidth(50)
        select_none_btn = QtWidgets.QPushButton("None")
        select_none_btn.setFixedWidth(50)
        
        # Add to layout
        layout.addLayout(translate_layout)
        layout.addWidget(separator)
        layout.addLayout(rotate_layout)
        layout.addStretch()
        layout.addWidget(select_all_btn)
        layout.addWidget(select_none_btn)
        
        # Connect signals
        self.tx_check.toggled.connect(lambda state: self.update_channel("tx", state))
        self.ty_check.toggled.connect(lambda state: self.update_channel("ty", state))
        self.tz_check.toggled.connect(lambda state: self.update_channel("tz", state))
        self.rx_check.toggled.connect(lambda state: self.update_channel("rx", state))
        self.ry_check.toggled.connect(lambda state: self.update_channel("ry", state))
        self.rz_check.toggled.connect(lambda state: self.update_channel("rz", state))
        
        select_all_btn.clicked.connect(self.select_all_channels)
        select_none_btn.clicked.connect(self.select_no_channels)
        
        # Update visual indicators
        self.updateChannelIndicators()
    
    def updateChannelIndicators(self):
        """Update visual indicators for active channels"""
        # Change checkbox texts to indicate state
        tx_color = "#0af" if self.manager.active_channels["tx"] else "#ddd"
        ty_color = "#0af" if self.manager.active_channels["ty"] else "#ddd"
        tz_color = "#0af" if self.manager.active_channels["tz"] else "#ddd"
        rx_color = "#0af" if self.manager.active_channels["rx"] else "#ddd"
        ry_color = "#0af" if self.manager.active_channels["ry"] else "#ddd"
        rz_color = "#0af" if self.manager.active_channels["rz"] else "#ddd"
        
        self.tx_check.setStyleSheet(f"color: {tx_color}; {self.tx_check.styleSheet()}")
        self.ty_check.setStyleSheet(f"color: {ty_color}; {self.ty_check.styleSheet()}")
        self.tz_check.setStyleSheet(f"color: {tz_color}; {self.tz_check.styleSheet()}")
        self.rx_check.setStyleSheet(f"color: {rx_color}; {self.rx_check.styleSheet()}")
        self.ry_check.setStyleSheet(f"color: {ry_color}; {self.ry_check.styleSheet()}")
        self.rz_check.setStyleSheet(f"color: {rz_color}; {self.rz_check.styleSheet()}")
    
    def update_channel(self, channel, state):
        """Update the state of a channel in the manager"""
        self.manager.update_channel_state(channel, state)
        self.updateChannelIndicators()  # Update visual indicators
        self.channelsChanged.emit()
    
    def select_all_channels(self):
        """Select all channels"""
        self.tx_check.setChecked(True)
        self.ty_check.setChecked(True)
        self.tz_check.setChecked(True)
        self.rx_check.setChecked(True)
        self.ry_check.setChecked(True)
        self.rz_check.setChecked(True)
    
    def select_no_channels(self):
        """Deselect all channels"""
        self.tx_check.setChecked(False)
        self.ty_check.setChecked(False)
        self.tz_check.setChecked(False)
        self.rx_check.setChecked(False)
        self.ry_check.setChecked(False)
        self.rz_check.setChecked(False)