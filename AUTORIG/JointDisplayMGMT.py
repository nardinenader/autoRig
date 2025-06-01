import maya.cmds as cmds

class JointDisplayManager:
    """Manages joint display visibility"""
    
    def toggle_joint_display(self, show=True, selected_only=False):
        """Show or hide joints"""
        draw_style = 0 if show else 2
        
        if selected_only:
            joints = cmds.ls(sl=True, type="joint")
            if not joints:
                cmds.warning("No joints selected.")
                return False
        else:
            joints = cmds.ls(type="joint")
        
        for joint in joints:
            try:
                cmds.setAttr(f"{joint}.drawStyle", draw_style)
            except Exception as e:
                cmds.warning(f"Failed to set display for {joint}: {str(e)}")
        
        action = "shown" if show else "hidden"
        scope = "selected" if selected_only else "all"
        print(f"{action.title()} {len(joints)} {scope} joints")
        return True