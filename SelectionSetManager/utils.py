#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility functions for the Selection Set Manager.
This file contains various utility functions used throughout the application.
"""

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    
    Returns:
        QWidget: The Maya main window as a QWidget
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def get_unique_name(base_name, existing_names):
    """
    Generate a unique name by adding an incremental number suffix
    
    Args:
        base_name (str): The base name to start with
        existing_names (list): List of existing names to avoid duplicates
        
    Returns:
        str: A unique name that doesn't exist in the existing_names list
    """
    name = base_name
    counter = 1
    
    while name in existing_names:
        name = f"{base_name}_{counter}"
        counter += 1
    
    return name

def short_name(full_path):
    """
    Extract the short name from a full Maya path
    
    Args:
        full_path (str): Full Maya path like '|group1|pSphere1'
        
    Returns:
        str: The short name ('pSphere1')
    """
    return full_path.split('|')[-1]

def get_object_type_icon(obj_type):
    """
    Get an appropriate icon for a Maya object type
    
    Args:
        obj_type (str): Maya object type
        
    Returns:
        QIcon: Icon representing the object type
    """
    from PySide2 import QtGui
    
    # Define icons for common types
    icon_map = {
        'transform': QtWidgets.QStyle.SP_TitleBarNormalButton,
        'mesh': QtWidgets.QStyle.SP_FileIcon,
        'joint': QtWidgets.QStyle.SP_TitleBarContextHelpButton,
        'camera': QtWidgets.QStyle.SP_ComputerIcon,
        'light': QtWidgets.QStyle.SP_MessageBoxInformation,
        'nurbsCurve': QtWidgets.QStyle.SP_FileLinkIcon,
        'nurbsSurface': QtWidgets.QStyle.SP_FileDialogDetailedView
    }
    
    # Get icon based on object type
    style = QtWidgets.QApplication.style()
    if obj_type in icon_map:
        return style.standardIcon(icon_map[obj_type])
    else:
        # Default icon for unknown types
        return style.standardIcon(QtWidgets.QStyle.SP_FileIcon)

def get_object_color(obj_name):
    """
    Get the display color of a Maya object if it has an override
    
    Args:
        obj_name (str): Name of the Maya object
        
    Returns:
        tuple: (r, g, b) tuple of color values, or None if no override
    """
    if not cmds.objExists(obj_name):
        return None
    
    # Check if object has color override
    try:
        if cmds.getAttr(f"{obj_name}.overrideEnabled"):
            color_index = cmds.getAttr(f"{obj_name}.overrideColor")
            # Convert color index to RGB using Maya's color table
            # This is simplified - a full implementation would need the complete color map
            color_map = {
                0: (0.6, 0.6, 0.6),  # Gray
                1: (0.0, 0.0, 0.0),  # Black
                2: (0.25, 0.25, 0.25),  # Dark Gray
                3: (0.6, 0.6, 0.6),  # Light Gray
                4: (0.8, 0.0, 0.0),  # Dark Red
                5: (0.0, 0.0, 0.8),  # Dark Blue
                6: (0.0, 0.8, 0.0),  # Dark Green
                7: (0.0, 0.8, 0.8),  # Dark Cyan
                8: (0.8, 0.0, 0.8),  # Dark Magenta
                9: (0.8, 0.8, 0.0),  # Dark Yellow
                # Add more colors as needed
            }
            
            return color_map.get(color_index, (0.6, 0.6, 0.6))  # Default to gray if not found
    except:
        pass
    
    return None

def create_directory_if_not_exists(directory_path):
    """
    Create a directory if it doesn't exist
    
    Args:
        directory_path (str): Path to the directory to create
        
    Returns:
        bool: True if directory exists/was created, False if failed
    """
    import os
    
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except Exception as e:
        cmds.warning(f"Failed to create directory: {directory_path}. Error: {str(e)}")
        return False