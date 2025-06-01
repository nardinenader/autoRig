import maya.cmds as cmds

class AttributeLocker:
    """Handles attribute locking and unlocking"""
    
    def __init__(self):
        self.attributes = {
            "Translate": [".translateX", ".translateY", ".translateZ"],
            "Rotate": [".rotateX", ".rotateY", ".rotateZ"],
            "Scale": [".scaleX", ".scaleY", ".scaleZ"]
        }
    
    def lock_unlock_attributes(self, lock=True, translate=True, rotate=True, scale=True):
        """Lock or unlock specified attributes on selected objects"""
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("No objects selected.")
            return False
        
        attr_groups = []
        if translate:
            attr_groups.extend(self.attributes["Translate"])
        if rotate:
            attr_groups.extend(self.attributes["Rotate"])
        if scale:
            attr_groups.extend(self.attributes["Scale"])
        
        if not attr_groups:
            cmds.warning("No attributes specified.")
            return False
        
        success_count = 0
        for obj in sel:
            try:
                for attr in attr_groups:
                    cmds.setAttr(obj + attr, lock=lock, keyable=not lock, channelBox=not lock)
                success_count += 1
            except Exception as e:
                cmds.warning(f"Failed to modify attributes on {obj}: {str(e)}")
        
        action = "locked" if lock else "unlocked"
        if success_count > 0:
            print(f"Successfully {action} attributes on {success_count} objects")
        return success_count > 0