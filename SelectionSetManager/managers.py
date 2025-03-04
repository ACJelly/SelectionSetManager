#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core managers for the Selection Set system.
This file contains the SelectionSetManager class which handles
all the logical operations of sets and groups.
"""

import maya.cmds as cmds
import json
import os
import base64

class SelectionSetManager:
    """Core class for managing selection sets"""
    
    def __init__(self):
        self.sets = {}  # Dictionary to store sets: {set_name: [object1, object2, ...]}
        self.set_positions = {}  # Dictionary to store set widget positions
        self.set_colors = {}  # Dictionary to store set colors
        self.set_sizes = {}  # Dictionary to store set sizes
        self.set_transparency = {}  # Dictionary to store set transparency
        self.set_parents = {}  # Dictionary to store parent-child relationships
        self.background_image = None  # Path to background image
        self.active_channels = {  # Dictionary to track active channels
            "tx": True, "ty": True, "tz": True,
            "rx": True, "ry": True, "rz": True
        }
        # Parent groups
        self.parent_groups = {}  # Dictionary to store parent groups: {group_name: [set_name1, set_name2, ...]}
        self.group_positions = {}  # Dictionary to store parent group positions
        self.group_colors = {}  # Dictionary to store parent group colors
        self.group_sizes = {}  # Dictionary to store parent group sizes
        self.group_transparency = {}  # Dictionary to store parent group transparency
    
    def create_parent_group(self, name="ParentGroup"):
        """Create a new parent group container (not a selection set)"""
        # Ensure unique name
        group_name = name
        counter = 1
        while group_name in self.parent_groups:
            group_name = f"{name}_{counter}"
            counter += 1
        
        # Initialize the parent group with an empty list of sets
        self.parent_groups[group_name] = []
        
        # Initialize position at (0,0) or offset from last group/set
        if self.group_positions:
            # Get the last position and add an offset
            last_x = max(pos[0] for pos in self.group_positions.values())
            last_y = max(pos[1] for pos in self.group_positions.values())
            self.group_positions[group_name] = [last_x + 20, last_y + 20]
        elif self.set_positions:
            # Use the last set position as reference
            last_x = max(pos[0] for pos in self.set_positions.values())
            last_y = max(pos[1] for pos in self.set_positions.values())
            self.group_positions[group_name] = [last_x + 20, last_y + 20]
        else:
            self.group_positions[group_name] = [20, 20]
        
        # Initialize default properties
        self.group_colors[group_name] = [100, 100, 60]  # Default color (yellowish)
        self.group_sizes[group_name] = [300, 200]  # Default size (larger than sets)
        self.group_transparency[group_name] = 180  # Default transparency
        
        return group_name
    
    def add_set_to_group(self, set_name, group_name):
        """Add a selection set to a parent group"""
        if set_name not in self.sets:
            cmds.warning(f"Set '{set_name}' not found.")
            return False
        
        if group_name not in self.parent_groups:
            cmds.warning(f"Parent group '{group_name}' not found.")
            return False
        
        # Remove from other groups first
        for other_group, sets in self.parent_groups.items():
            if set_name in sets:
                sets.remove(set_name)
        
        # Add to the specified group
        if set_name not in self.parent_groups[group_name]:
            self.parent_groups[group_name].append(set_name)
        
        return True
    
    def remove_set_from_group(self, set_name, group_name=None):
        """Remove a selection set from a parent group or all groups"""
        if set_name not in self.sets:
            cmds.warning(f"Set '{set_name}' not found.")
            return False
        
        if group_name is not None:
            if group_name not in self.parent_groups:
                cmds.warning(f"Parent group '{group_name}' not found.")
                return False
            
            if set_name in self.parent_groups[group_name]:
                self.parent_groups[group_name].remove(set_name)
        else:
            # Remove from all groups
            for group_name, sets in self.parent_groups.items():
                if set_name in sets:
                    sets.remove(set_name)
        
        return True
    
    def rename_parent_group(self, old_name, new_name):
        """Rename a parent group"""
        if old_name not in self.parent_groups:
            cmds.warning(f"Parent group '{old_name}' not found.")
            return False
        
        if new_name in self.parent_groups:
            cmds.warning(f"Parent group named '{new_name}' already exists.")
            return False
        
        # Update all dictionaries
        self.parent_groups[new_name] = self.parent_groups[old_name]
        
        if old_name in self.group_positions:
            self.group_positions[new_name] = self.group_positions[old_name]
            del self.group_positions[old_name]
        
        if old_name in self.group_colors:
            self.group_colors[new_name] = self.group_colors[old_name]
            del self.group_colors[old_name]
        
        if old_name in self.group_sizes:
            self.group_sizes[new_name] = self.group_sizes[old_name]
            del self.group_sizes[old_name]
        
        if old_name in self.group_transparency:
            self.group_transparency[new_name] = self.group_transparency[old_name]
            del self.group_transparency[old_name]
        
        del self.parent_groups[old_name]
        return True
    
    def delete_parent_group(self, name):
        """Delete a parent group"""
        if name not in self.parent_groups:
            cmds.warning(f"Parent group '{name}' not found.")
            return False
        
        # Remove the group from all dictionaries
        del self.parent_groups[name]
        
        if name in self.group_positions:
            del self.group_positions[name]
        
        if name in self.group_colors:
            del self.group_colors[name]
        
        if name in self.group_sizes:
            del self.group_sizes[name]
        
        if name in self.group_transparency:
            del self.group_transparency[name]
        
        return True
    
    def update_group_position(self, name, x, y):
        """Update the position of a parent group"""
        if name in self.parent_groups:
            self.group_positions[name] = [x, y]
            return True
        return False
    
    def update_group_size(self, name, width, height):
        """Update the size of a parent group"""
        if name in self.parent_groups:
            self.group_sizes[name] = [width, height]
            return True
        return False
    
    def update_group_color(self, name, r, g, b):
        """Update the color of a parent group"""
        if name in self.parent_groups:
            self.group_colors[name] = [r, g, b]
            return True
        return False
    
    def update_group_transparency(self, name, transparency):
        """Update the transparency of a parent group"""
        if name in self.parent_groups:
            self.group_transparency[name] = transparency
            return True
        return False
    
    def create_set(self, name="NewSet"):
        """Create a new selection set from current selection"""
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            cmds.warning("Nothing selected. Please select objects to create a set.")
            return None
        
        # Ensure unique name
        set_name = name
        counter = 1
        while set_name in self.sets:
            set_name = f"{name}_{counter}"
            counter += 1
        
        self.sets[set_name] = selection
        # Initialize position at (0,0) or offset from last set
        if self.set_positions:
            # Get the last position and add an offset
            last_x = max(pos[0] for pos in self.set_positions.values())
            last_y = max(pos[1] for pos in self.set_positions.values())
            self.set_positions[set_name] = [last_x + 20, last_y + 20]
        else:
            self.set_positions[set_name] = [20, 20]
        
        # Initialize default properties
        self.set_colors[set_name] = [70, 70, 70]  # Default color
        self.set_sizes[set_name] = [200, 150]  # Default size
        self.set_transparency[set_name] = 180  # Default transparency (0-255)
        self.set_parents[set_name] = None  # No parent by default
            
        return set_name
    
    def rename_set(self, old_name, new_name):
        """Rename a selection set"""
        if old_name not in self.sets:
            cmds.warning(f"Set '{old_name}' not found.")
            return False
        
        if new_name in self.sets:
            cmds.warning(f"Set named '{new_name}' already exists.")
            return False
        
        # Update all dictionaries
        self.sets[new_name] = self.sets[old_name]
        if old_name in self.set_positions:
            self.set_positions[new_name] = self.set_positions[old_name]
            del self.set_positions[old_name]
        if old_name in self.set_colors:
            self.set_colors[new_name] = self.set_colors[old_name]
            del self.set_colors[old_name]
        if old_name in self.set_sizes:
            self.set_sizes[new_name] = self.set_sizes[old_name]
            del self.set_sizes[old_name]
        if old_name in self.set_transparency:
            self.set_transparency[new_name] = self.set_transparency[old_name]
            del self.set_transparency[old_name]
        
        # Update parent-child relationships
        if old_name in self.set_parents:
            self.set_parents[new_name] = self.set_parents[old_name]
            del self.set_parents[old_name]
        
        # Update any child references to this set
        for child_name, parent_name in self.set_parents.items():
            if parent_name == old_name:
                self.set_parents[child_name] = new_name
        
        # Update any group references
        for group_name, sets in self.parent_groups.items():
            if old_name in sets:
                sets.remove(old_name)
                sets.append(new_name)
        
        del self.sets[old_name]
        return True
    
    def delete_set(self, name):
        """Delete a selection set"""
        if name in self.sets:
            # Remove from all dictionaries
            del self.sets[name]
            if name in self.set_positions:
                del self.set_positions[name]
            if name in self.set_colors:
                del self.set_colors[name]
            if name in self.set_sizes:
                del self.set_sizes[name]
            if name in self.set_transparency:
                del self.set_transparency[name]
            
            # Update parent-child relationships
            if name in self.set_parents:
                del self.set_parents[name]
            
            # Update any child references to this set
            for child_name, parent_name in list(self.set_parents.items()):
                if parent_name == name:
                    self.set_parents[child_name] = None
            
            # Remove from any parent groups
            self.remove_set_from_group(name)
            
            return True
        return False
    
    def select_set(self, name, respect_channels=True):
        """Select all objects in a set and its children"""
        if name not in self.sets:
            cmds.warning(f"Set '{name}' not found.")
            return False
        
        # Collect all objects to select, including from child sets
        all_objects = self.get_all_objects_in_set_hierarchy(name)
        
        # Filter out objects that no longer exist
        valid_objects = [obj for obj in all_objects if cmds.objExists(obj)]
        
        if not valid_objects:
            cmds.warning(f"No valid objects found in set '{name}' or its children.")
            return False
        
        # Apply channel filtering if requested
        if respect_channels:
            self.select_objects_with_channel_filtering(valid_objects)
        else:
            cmds.select(valid_objects, replace=True)
        
        return True
    
    def get_all_objects_in_set_hierarchy(self, set_name):
        """Get all objects in a set and its child sets recursively"""
        if set_name not in self.sets:
            return []
        
        # Start with objects in this set
        all_objects = list(self.sets[set_name])
        
        # Add objects from all child sets
        for child_name, parent_name in self.set_parents.items():
            if parent_name == set_name:
                all_objects.extend(self.get_all_objects_in_set_hierarchy(child_name))
        
        return all_objects
    
    def select_objects_with_channel_filtering(self, objects):
        """Select objects with channel filtering applied"""
        if not objects:
            return
        
        # If all channels are active or none are active, just do a normal select
        if all(self.active_channels.values()) or not any(self.active_channels.values()):
            cmds.select(objects, replace=True)
            return
        
        # Clear selection
        cmds.select(clear=True)
        
        # Get active channel components
        active_components = []
        if self.active_channels["tx"]:
            active_components.append(".tx")
        if self.active_channels["ty"]:
            active_components.append(".ty")
        if self.active_channels["tz"]:
            active_components.append(".tz")
        if self.active_channels["rx"]:
            active_components.append(".rx")
        if self.active_channels["ry"]:
            active_components.append(".ry")
        if self.active_channels["rz"]:
            active_components.append(".rz")
        
        try:
            # First select all the objects (this ensures we get the right context)
            cmds.select(objects, replace=True)
            
            # Then filter down to just the channels
            selected_attrs = []
            for obj in objects:
                for component in active_components:
                    attr = obj + component
                    if cmds.objExists(attr):
                        selected_attrs.append(attr)
            
            # If we have attributes to select, select them
            if selected_attrs:
                cmds.select(selected_attrs, replace=True)
                # Print feedback to script editor
                cmds.inViewMessage(
                    amg=f"Selected {len(selected_attrs)} channels on {len(objects)} objects",
                    pos='topCenter', fade=True, fadeStayTime=1000
                )
        except Exception as e:
            # If there's an error, fall back to just selecting the objects
            cmds.warning(f"Error in channel filtering: {e}. Selecting objects instead.")
            cmds.select(objects, replace=True)
    
    def select_hierarchy_chain(self, top_node):
        """Select a hierarchy chain from the top node down"""
        if not cmds.objExists(top_node):
            cmds.warning(f"Object '{top_node}' does not exist.")
            return False
        
        # Get all descendants
        descendants = cmds.listRelatives(top_node, allDescendants=True, fullPath=True) or []
        
        # Add the top node itself
        full_chain = [top_node] + descendants
        
        # Select the chain
        cmds.select(full_chain, replace=True)
        return True
    
    def create_chain_set(self, top_node, name=None):
        """Create a set from a hierarchy chain"""
        if not cmds.objExists(top_node):
            cmds.warning(f"Object '{top_node}' does not exist.")
            return None
        
        # Get all descendants
        descendants = cmds.listRelatives(top_node, allDescendants=True, fullPath=True) or []
        
        # Add the top node itself
        full_chain = [top_node] + descendants
        
        # Create a set name if not provided
        if not name:
            # Use the top node's short name
            short_name = top_node.split("|")[-1]
            name = f"{short_name}_Chain"
        
        # Save current selection
        current_selection = cmds.ls(selection=True, long=True)
        
        # Select the chain
        cmds.select(full_chain, replace=True)
        
        # Create the set
        result = self.create_set(name)
        
        # Restore previous selection
        if current_selection:
            cmds.select(current_selection, replace=True)
        else:
            cmds.select(clear=True)
        
        return result
    
    def set_parent(self, child_name, parent_name):
        """Set a parent-child relationship between sets"""
        if child_name not in self.sets:
            cmds.warning(f"Child set '{child_name}' not found.")
            return False
        
        if parent_name and parent_name not in self.sets:
            cmds.warning(f"Parent set '{parent_name}' not found.")
            return False
        
        # Check for circular references
        if parent_name and self.would_create_circular_reference(child_name, parent_name):
            cmds.warning(f"Cannot set '{parent_name}' as parent of '{child_name}' - would create circular reference.")
            return False
        
        # Set the parent
        self.set_parents[child_name] = parent_name
        return True
    
    def would_create_circular_reference(self, child_name, new_parent_name):
        """Check if setting a parent would create a circular reference"""
        # If the child would become its own ancestor, that's a circular reference
        ancestor = new_parent_name
        while ancestor:
            if ancestor == child_name:
                return True
            ancestor = self.set_parents.get(ancestor)
        return False
    
    def update_set_position(self, name, x, y):
        """Update the position of a set"""
        if name in self.sets:
            self.set_positions[name] = [x, y]
            return True
        return False
    
    def update_set_size(self, name, width, height):
        """Update the size of a set"""
        if name in self.sets:
            self.set_sizes[name] = [width, height]
            return True
        return False
    
    def update_set_color(self, name, r, g, b):
        """Update the color of a set"""
        if name in self.sets:
            self.set_colors[name] = [r, g, b]
            return True
        return False
    
    def update_set_transparency(self, name, transparency):
        """Update the transparency of a set"""
        if name in self.sets:
            self.set_transparency[name] = transparency
            return True
        return False
    
    def update_channel_state(self, channel, state):
        """Update the state of a channel filter"""
        if channel in self.active_channels:
            self.active_channels[channel] = state
            return True
        return False
    
    def set_background_image(self, image_path):
        """Set the background image"""
        self.background_image = image_path
        return True
    
    def export_sets(self, file_path):
        """Export selection sets to a JSON file including all customization"""
        try:
            export_data = {
                "sets": self.sets,
                "positions": self.set_positions,
                "colors": self.set_colors,
                "sizes": self.set_sizes,
                "transparency": self.set_transparency,
                "parents": self.set_parents,
                "channels": self.active_channels,
                "background_image": None,
                # Add parent group data
                "parent_groups": self.parent_groups,
                "group_positions": self.group_positions,
                "group_colors": self.group_colors,
                "group_sizes": self.group_sizes,
                "group_transparency": self.group_transparency
            }
            
            # Handle background image if it exists
            if self.background_image and os.path.exists(self.background_image):
                with open(self.background_image, 'rb') as img_file:
                    img_data = img_file.read()
                    img_b64 = base64.b64encode(img_data).decode('utf-8')
                    # Store image data and format
                    export_data["background_image"] = {
                        "data": img_b64,
                        "format": os.path.splitext(self.background_image)[1][1:].lower(),
                        "path": self.background_image
                    }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            return True
        except Exception as e:
            cmds.warning(f"Failed to export sets: {str(e)}")
            return False
    
    def import_sets(self, file_path):
        """Import selection sets from a JSON file including all customization"""
        try:
            with open(file_path, 'r') as f:
                imported_data = json.load(f)
            
            # Check data format
            if not isinstance(imported_data, dict) or "sets" not in imported_data:
                cmds.warning("Invalid JSON format for sets.")
                return False
            
            # Import sets
            imported_sets = imported_data.get("sets", {})
            imported_positions = imported_data.get("positions", {})
            imported_colors = imported_data.get("colors", {})
            imported_sizes = imported_data.get("sizes", {})
            imported_transparency = imported_data.get("transparency", {})
            imported_parents = imported_data.get("parents", {})
            imported_channels = imported_data.get("channels", {})
            
            # Import parent group data
            imported_parent_groups = imported_data.get("parent_groups", {})
            imported_group_positions = imported_data.get("group_positions", {})
            imported_group_colors = imported_data.get("group_colors", {})
            imported_group_sizes = imported_data.get("group_sizes", {})
            imported_group_transparency = imported_data.get("group_transparency", {})
            
            # Update channel states if available
            if imported_channels:
                for channel, state in imported_channels.items():
                    if channel in self.active_channels:
                        self.active_channels[channel] = state
            
            # Clear existing sets and groups
            self.sets.clear()
            self.set_positions.clear()
            self.set_colors.clear()
            self.set_sizes.clear()
            self.set_transparency.clear()
            self.set_parents.clear()
            self.parent_groups.clear()
            self.group_positions.clear()
            self.group_colors.clear()
            self.group_sizes.clear()
            self.group_transparency.clear()
            
            # Import all sets
            for name, objects in imported_sets.items():
                # Filter out objects that don't exist in the scene
                valid_objects = [obj for obj in objects if cmds.objExists(obj)]
                if valid_objects:
                    self.sets[name] = valid_objects
                    
                    # Import position if available
                    if name in imported_positions:
                        self.set_positions[name] = imported_positions[name]
                    else:
                        # Default position
                        self.set_positions[name] = [20, 20 + (len(self.sets) * 30)]
                    
                    # Import color if available
                    if name in imported_colors:
                        self.set_colors[name] = imported_colors[name]
                    else:
                        self.set_colors[name] = [70, 70, 70]  # Default
                    
                    # Import size if available
                    if name in imported_sizes:
                        self.set_sizes[name] = imported_sizes[name]
                    else:
                        self.set_sizes[name] = [200, 150]  # Default
                    
                    # Import transparency if available
                    if name in imported_transparency:
                        self.set_transparency[name] = imported_transparency[name]
                    else:
                        self.set_transparency[name] = 180  # Default
            
            # Import parent relationships after all sets are created
            for name, parent in imported_parents.items():
                if name in self.sets and (parent is None or parent in self.sets):
                    self.set_parents[name] = parent
            
            # Import parent groups
            for name, sets in imported_parent_groups.items():
                # Filter out sets that don't exist
                valid_sets = [set_name for set_name in sets if set_name in self.sets]
                self.parent_groups[name] = valid_sets
                
                # Import position if available
                if name in imported_group_positions:
                    self.group_positions[name] = imported_group_positions[name]
                else:
                    # Default position
                    self.group_positions[name] = [20, 20 + (len(self.parent_groups) * 30)]
                
                # Import color if available
                if name in imported_group_colors:
                    self.group_colors[name] = imported_group_colors[name]
                else:
                    self.group_colors[name] = [100, 100, 60]  # Default
                
                # Import size if available
                if name in imported_group_sizes:
                    self.group_sizes[name] = imported_group_sizes[name]
                else:
                    self.group_sizes[name] = [300, 200]  # Default
                
                # Import transparency if available
                if name in imported_group_transparency:
                    self.group_transparency[name] = imported_group_transparency[name]
                else:
                    self.group_transparency[name] = 180  # Default
            
            # Handle background image if it exists
            bg_image_data = imported_data.get("background_image", None)
            if bg_image_data and isinstance(bg_image_data, dict):
                try:
                    # Save the image to a temp file
                    img_data = base64.b64decode(bg_image_data["data"])
                    img_format = bg_image_data.get("format", "png")
                    
                    # Try to use the original path first
                    original_path = bg_image_data.get("path")
                    if original_path and os.path.dirname(original_path) and os.access(os.path.dirname(original_path), os.W_OK):
                        img_path = original_path
                    else:
                        # Use a temp file in the same directory as the JSON
                        json_dir = os.path.dirname(file_path)
                        img_path = os.path.join(json_dir, f"selset_bg.{img_format}")
                    
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_data)
                    
                    self.background_image = img_path
                except Exception as e:
                    cmds.warning(f"Failed to restore background image: {str(e)}")
            
            return True
        except Exception as e:
            cmds.warning(f"Failed to import sets: {str(e)}")
            return False