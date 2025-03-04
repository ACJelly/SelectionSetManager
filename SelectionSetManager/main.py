#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point for the Selection Set Manager.
This file initializes and shows the main UI.
"""

import maya.cmds as cmds
from PySide2 import QtWidgets

from ui import SelectionSetUI

def show_ui():
    """Show the Selection Set Manager UI"""
    # Close existing UI if it exists
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, SelectionSetUI):
            widget.close()
    
    # Create and show new UI
    ui = SelectionSetUI()
    ui.show()
    return ui

# For testing in script editor
if __name__ == "__main__":
    show_ui()