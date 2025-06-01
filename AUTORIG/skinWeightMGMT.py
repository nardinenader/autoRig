import maya.cmds as cmds


class SkinWeightManager:
    """Handles skin weight copying operations"""
    
    def __init__(self):
        self.target_objects = ["two", "three", "four"]  # Default targets
    
    def get_skin_cluster(self, obj):
        """Get skin cluster from object"""
        history = cmds.listHistory(obj)
        skin_clusters = cmds.ls(history, type='skinCluster')
        return skin_clusters[0] if skin_clusters else None
    
    def copy_weights(self, source_obj, target_list=None):
        """Copy skin weights from source to targets"""
        if not source_obj:
            cmds.warning("No source object specified")
            return False
        
        if not cmds.objExists(source_obj):
            cmds.warning(f"Source object '{source_obj}' does not exist")
            return False
        
        source_skin = self.get_skin_cluster(source_obj)
        if not source_skin:
            cmds.warning(f"No skinCluster found on {source_obj}")
            return False
        
        targets = target_list or self.target_objects
        success_count = 0
        
        for target in targets:
            if not cmds.objExists(target):
                cmds.warning(f"Target object '{target}' does not exist. Skipping.")
                continue
                
            dest_skin = self.get_skin_cluster(target)
            if not dest_skin:
                cmds.warning(f"No skinCluster found on {target}. Skipping.")
                continue
            
            try:
                cmds.copySkinWeights(ss=source_skin, ds=dest_skin, noMirror=True)
                success_count += 1
            except Exception as e:
                cmds.warning(f"Failed to copy weights to {target}: {str(e)}")
        
        if success_count > 0:
            cmds.confirmDialog(title="Copy Skin Weights", 
                             message=f"Skin weights copied successfully to {success_count} objects!")
        return success_count > 0
