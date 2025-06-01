import maya.cmds as cmds
import os

class AssetManager:
    """Handles asset saving and management"""
    
    def __init__(self):
        self.filepath = os.path.expanduser("~/onedrive/Documents/maya/scripts/Asset/")
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
    
    def get_file_list(self):
        """Get list of files in asset directory"""
        try:
            return cmds.getFileList(folder=self.filepath) or []
        except:
            return []
    
    def save_asset(self, asset_name, file_type="MA"):
        """Save current scene as asset"""
        if not asset_name.strip():
            cmds.warning("No asset name provided.")
            return False
        
        name = asset_name.strip()
        full_path = os.path.join(self.filepath, name)
        
        try:
            cmds.file(rename=full_path)
            
            if file_type == "MA":
                cmds.file(save=True, type='mayaAscii')
                full_path += ".ma"
            else:
                cmds.file(save=True, type='mayaBinary')
                full_path += ".mb"
            
            cmds.confirmDialog(title="Asset Saved", 
                             message=f"Asset saved successfully:\n{full_path}")
            return True
        except Exception as e:
            cmds.warning(f"Failed to save asset: {str(e)}")
            return False