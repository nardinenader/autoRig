import maya.cmds as cmds

class ObjectRenamer:
    """Handles object renaming operations"""
    
    def rename_objects(self, name_input, is_prefix=True):
        """Rename selected objects with prefix or suffix"""
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("No objects selected.")
            return False
        
        if not name_input.strip():
            cmds.warning("No name input provided.")
            return False
        
        name = name_input.strip()
        renamed_count = 0
        
        for obj in sel:
            try:
                if is_prefix:
                    new_name = name + "_" + obj
                else:
                    new_name = obj + "_" + name
                cmds.rename(obj, new_name)
                renamed_count += 1
            except Exception as e:
                cmds.warning(f"Failed to rename {obj}: {str(e)}")
        
        if renamed_count > 0:
            cmds.confirmDialog(title="Rename Objects", 
                             message=f"Successfully renamed {renamed_count} objects!")
        return renamed_count > 0