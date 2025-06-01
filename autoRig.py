import maya.cmds as cmds
import os
from functools import partial

class RigBuilder:
    """Handles joint creation and rig setup"""
    
    def __init__(self):
        self.fk_ctrls = {}
    
    def joint_creation(self, name, pos=(0, 0, 0), parent_name=None):
        """Create a joint with proper naming convention"""
        cmds.select(clear=True)
        j = cmds.joint(name=name + "_drv_jnt", position=pos)
        if parent_name:
            cmds.parent(j, parent_name)
        return j
    
    def setup_control(self, jnt):
        """Create control setup for a joint"""
        ctrl = cmds.circle(n=jnt.replace('_jnt', '_CTRL'), nr=(0, 1, 0), ch=0)[0]
        offset = cmds.group(ctrl, n=jnt.replace('_jnt', '_offset'))
        grp = cmds.group(offset, n=jnt.replace('_jnt', '_GRP'))
        cmds.matchTransform(grp, jnt)
        cmds.parentConstraint(ctrl, jnt, mo=True)
        return grp
    
    def create_basic_skeleton(self):
        """Create a basic humanoid skeleton"""
        # Spine and torso
        spine = self.joint_creation("spine", (0, 8, -0.5))
        hip = self.joint_creation("hip", (0, 6.5, -0.5), parent_name=spine)
        chest = self.joint_creation("chest", (0, 10, -0.5), parent_name=spine)
        head = self.joint_creation("head", (0, 12, -0.5), parent_name=chest)
        
        # Right leg
        rt_thigh = self.joint_creation("rt_thigh", (1, 5, -0.5), parent_name=hip)
        rt_knee = self.joint_creation("rt_knee", (1, 2, 0), parent_name=rt_thigh)
        rt_ankle = self.joint_creation("rt_ankle", (1, 0, -0.5), parent_name=rt_knee)
        rt_foot = self.joint_creation("rt_foot", (1, 0, 1), parent_name=rt_ankle)
        
        # Left leg
        lt_thigh = self.joint_creation("lt_thigh", (-1, 5, -0.5), parent_name=hip)
        lt_knee = self.joint_creation("lt_knee", (-1, 2, 0), parent_name=lt_thigh)
        lt_ankle = self.joint_creation("lt_ankle", (-1, 0, -0.5), parent_name=lt_knee)
        lt_foot = self.joint_creation("lt_foot", (-1, 0, 1), parent_name=lt_ankle)
        
        # Right arm
        rt_shoulder = self.joint_creation("rt_shoulder", (-1, 11, -0.5), parent_name=chest)
        rt_elbow = self.joint_creation("rt_elbow", (-3, 8.5, -1), parent_name=rt_shoulder)
        rt_wrist = self.joint_creation("rt_wrist", (-4, 6, -0.5), parent_name=rt_elbow)
        
        # Left arm
        lt_shoulder = self.joint_creation("lt_shoulder", (1, 11, -0.5), parent_name=chest)
        lt_elbow = self.joint_creation("lt_elbow", (3, 8.5, -1), parent_name=lt_shoulder)
        lt_wrist = self.joint_creation("lt_wrist", (4, 6, -0.5), parent_name=lt_elbow)
    
    def create_fk_chain(self):
        """Create FK control chain"""
        if not cmds.objExists('spine_drv_jnt'):
            cmds.warning("No base skeleton found. Create skeleton first.")
            return
        
        # Duplicate and rename for FK
        fk_root = cmds.duplicate('spine_drv_jnt', renameChildren=True)[0]
        fk_root = cmds.rename(fk_root, 'spine_FK_jnt')
        
        for joint in cmds.listRelatives(fk_root, ad=True, type='joint'):
            cmds.rename(joint, joint.replace('_drv_jnt', '_FK_jnt'))
        
        # Create FK controls
        fk_joints = cmds.listRelatives('spine_FK_jnt', ad=True, type='joint') or []
        fk_joints.append('spine_FK_jnt')
        fk_joints = fk_joints[::-1]
        
        for jnt in fk_joints:
            base_name = jnt.replace('_FK_jnt', '')
            ctrl = cmds.circle(n=base_name + '_CTRL', nr=(0, 1, 0), ch=0)[0]
            offset = cmds.group(ctrl, n=base_name + '_offset')
            grp = cmds.group(offset, n=base_name + '_GRP')
            cmds.matchTransform(grp, jnt)
            cmds.parentConstraint(ctrl, jnt, mo=True)
            
            parent_jnt = cmds.listRelatives(jnt, parent=True, type='joint')
            if parent_jnt:
                parent_base = parent_jnt[0].replace('_FK_jnt', '')
                parent_ctrl = self.fk_ctrls.get(parent_base)
                if parent_ctrl:
                    cmds.parent(grp, parent_ctrl)
            
            self.fk_ctrls[base_name] = ctrl
    
    def create_ik_setup(self):
        """Create IK handles and controls"""
        if not cmds.objExists('spine_drv_jnt'):
            cmds.warning("No base skeleton found. Create skeleton first.")
            return
        
        # Duplicate for IK
        ik_root = cmds.duplicate('spine_drv_jnt', renameChildren=True)[0]
        ik_root = cmds.rename(ik_root, 'spine_IK_jnt')
        
        ik_joints = cmds.listRelatives(ik_root, ad=True, type='joint') or []
        ik_joints.append(ik_root)
        
        for joint in ik_joints:
            new_name = joint.replace('_drv_jnt', '_IK_jnt')
            cmds.rename(joint, new_name)
        
        # Create IK handles for limbs
        limbs = [
            ('rt_thigh_IK_jnt1', 'rt_ankle_IK_jnt1', 'rt_leg_IKHandle'),
            ('lt_thigh_IK_jnt1', 'lt_ankle_IK_jnt1', 'lt_leg_IKHandle'),
            ('rt_shoulder_IK_jnt1', 'rt_wrist_IK_jnt1', 'rt_arm_IKHandle'),
            ('lt_shoulder_IK_jnt1', 'lt_wrist_IK_jnt1', 'lt_arm_IKHandle')
        ]
        
        for start_jnt, end_jnt, handle_name in limbs:
            if cmds.objExists(start_jnt) and cmds.objExists(end_jnt):
                ik_handle, effector = cmds.ikHandle(sj=start_jnt, ee=end_jnt, sol='ikRPsolver')
                ik_handle = cmds.rename(ik_handle, handle_name)
                ctrl_grp = self.setup_control(end_jnt)
                ctrl_name = end_jnt.replace('_jnt1', '_CTRL1')
                if cmds.objExists(ctrl_name):
                    cmds.parent(ik_handle, ctrl_name)
    
    def show_display_mode(self, mode):
        """Show specific display mode (base, FK, or IK)"""
        all_nodes = (cmds.ls('*_drv_jnt') + cmds.ls('*_FK_jnt') + cmds.ls('*_IK_jnt') + 
                    cmds.ls('*_CTRL') + cmds.ls('*_GRP') + cmds.ls('*_offset') + cmds.ls('*_IKHandle'))
        
        # Hide all first
        for node in all_nodes:
            if cmds.objExists(node):
                cmds.hide(node)
        
        # Show based on mode
        if mode == "base":
            nodes_to_show = cmds.ls('*_drv_jnt')
        elif mode == "fk":
            nodes_to_show = (cmds.ls('*_FK_jnt') + cmds.ls('*_CTRL') + 
                           cmds.ls('*_GRP') + cmds.ls('*_offset'))
        elif mode == "ik":
            nodes_to_show = (cmds.ls('*_IK_jnt') + cmds.ls('*_CTRL') + 
                           cmds.ls('*_GRP') + cmds.ls('*_offset') + cmds.ls('*_IKHandle'))
        
        for node in nodes_to_show:
            if cmds.objExists(node):
                cmds.showHidden(node)


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


class RiggingToolkitUI:
    """Main UI class that combines all tools"""
    
    def __init__(self):
        self.window_name = "riggingToolkitUI"
        self.rig_builder = RigBuilder()
        self.skin_manager = SkinWeightManager()
        self.renamer = ObjectRenamer()
        self.joint_display = JointDisplayManager()
        self.attr_locker = AttributeLocker()
        self.asset_manager = AssetManager()
        
        # UI element references
        self.ui_elements = {}
    
    def create_ui(self):
        """Create the main UI"""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        
        window = cmds.window(self.window_name, title="Rigging Toolkit", 
                           widthHeight=(400, 600), sizeable=True)
        
        # Main scroll layout
        scroll = cmds.scrollLayout(verticalScrollBarThickness=16)
        
        # Main column layout
        main_column = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        
        # Header
        cmds.text(label="RIGGING TOOLKIT", font="boldLabelFont", height=30)
        cmds.separator(height=10, style='in')
        
        # Rig Builder Section
        self.create_rig_builder_section()
        cmds.separator(height=10, style='in')
        
        # Skin Weight Manager Section
        self.create_skin_weight_section()
        cmds.separator(height=10, style='in')
        
        # Object Renamer Section
        self.create_renamer_section()
        cmds.separator(height=10, style='in')
        
        # Joint Display Section
        self.create_joint_display_section()
        cmds.separator(height=10, style='in')
        
        # Attribute Locker Section
        self.create_attribute_section()
        cmds.separator(height=10, style='in')
        
        # Asset Manager Section
        self.create_asset_section()
        
        cmds.showWindow(window)
    
    def create_rig_builder_section(self):
        """Create rig builder UI section"""
        cmds.frameLayout(label="Rig Builder", collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        cmds.button(label="Create Basic Skeleton", height=30,
                   command=lambda x: self.rig_builder.create_basic_skeleton())
        
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=True)
        cmds.button(label="Create FK Chain", 
                   command=lambda x: self.rig_builder.create_fk_chain())
        cmds.button(label="Create IK Setup", 
                   command=lambda x: self.rig_builder.create_ik_setup())
        cmds.setParent('..')
        
        cmds.text(label="Display Mode:")
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=True)
        cmds.button(label="Base Setup", 
                   command=lambda x: self.rig_builder.show_display_mode("base"))
        cmds.button(label="FK Mode", 
                   command=lambda x: self.rig_builder.show_display_mode("fk"))
        cmds.button(label="IK Mode", 
                   command=lambda x: self.rig_builder.show_display_mode("ik"))
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    def create_skin_weight_section(self):
        """Create skin weight manager UI section"""
        cmds.frameLayout(label="Skin Weight Manager", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        cmds.text(label='Source Object:')
        self.ui_elements['skin_source'] = cmds.textField()
        
        cmds.button(label='Copy Weights to Default Targets', height=25,
                   command=self.copy_skin_weights_callback)
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    def create_renamer_section(self):
        """Create object renamer UI section"""
        cmds.frameLayout(label="Object Renamer", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        self.ui_elements['rename_mode'] = cmds.radioButtonGrp(
            label='Mode:', labelArray2=['Prefix', 'Suffix'], 
            numberOfRadioButtons=2, sl=1)
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=True)
        cmds.button(label='LT', command=partial(self.rename_callback, "LT"))
        cmds.button(label='RT', command=partial(self.rename_callback, "RT"))
        cmds.setParent('..')
        
        cmds.text(label="Custom Text:")
        self.ui_elements['custom_name'] = cmds.textField()
        cmds.button(label='Rename Selected', height=25, command=self.custom_rename_callback)
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    def create_joint_display_section(self):
        """Create joint display manager UI section"""
        cmds.frameLayout(label="Joint Display Manager", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        self.ui_elements['joint_mode'] = cmds.radioButtonGrp(
            label='Scope:', labelArray2=['All Joints', 'Selected Only'], 
            numberOfRadioButtons=2, sl=1)
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=True)
        cmds.button(label='Hide Joints', command=self.hide_joints_callback)
        cmds.button(label='Show Joints', command=self.show_joints_callback)
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    def create_attribute_section(self):
        """Create attribute locker UI section"""
        cmds.frameLayout(label="Attribute Locker", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        cmds.text(label='Attributes:')
        self.ui_elements['attr_translate'] = cmds.checkBox(label='Translate', value=True)
        self.ui_elements['attr_rotate'] = cmds.checkBox(label='Rotate', value=True)
        self.ui_elements['attr_scale'] = cmds.checkBox(label='Scale', value=True)
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=True)
        cmds.button(label='LOCK', command=self.lock_attributes_callback)
        cmds.button(label='UNLOCK', command=self.unlock_attributes_callback)
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    def create_asset_section(self):
        """Create asset manager UI section"""
        cmds.frameLayout(label="Asset Manager", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)
        
        cmds.text(label='Existing Assets:')
        self.ui_elements['asset_list'] = cmds.textScrollList(height=80)
        self.refresh_asset_list()
        
        cmds.text(label='Asset Name:')
        self.ui_elements['asset_name'] = cmds.textField()
        
        self.ui_elements['save_format'] = cmds.optionMenu(label='Save Format:')
        cmds.menuItem(label='MA')
        cmds.menuItem(label='MB')
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=True)
        cmds.button(label='Save Asset', command=self.save_asset_callback)
        cmds.button(label='Refresh List', command=lambda x: self.refresh_asset_list())
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    def refresh_asset_list(self):
        """Refresh the asset list"""
        if 'asset_list' in self.ui_elements:
            cmds.textScrollList(self.ui_elements['asset_list'], edit=True, removeAll=True)
            files = self.asset_manager.get_file_list()
            for file in files:
                cmds.textScrollList(self.ui_elements['asset_list'], edit=True, append=file)
    
    # Callback methods
    def copy_skin_weights_callback(self, *args):
        source = cmds.textField(self.ui_elements['skin_source'], q=True, text=True)
        self.skin_manager.copy_weights(source)
    
    def rename_callback(self, name, *args):
        mode = cmds.radioButtonGrp(self.ui_elements['rename_mode'], q=True, sl=True)
        is_prefix = (mode == 1)
        self.renamer.rename_objects(name, is_prefix)
    
    def custom_rename_callback(self, *args):
        name = cmds.textField(self.ui_elements['custom_name'], q=True, text=True)
        mode = cmds.radioButtonGrp(self.ui_elements['rename_mode'], q=True, sl=True)
        is_prefix = (mode == 1)
        self.renamer.rename_objects(name, is_prefix)
    
    def hide_joints_callback(self, *args):
        mode = cmds.radioButtonGrp(self.ui_elements['joint_mode'], q=True, sl=True)
        selected_only = (mode == 2)
        self.joint_display.toggle_joint_display(show=False, selected_only=selected_only)
    
    def show_joints_callback(self, *args):
        mode = cmds.radioButtonGrp(self.ui_elements['joint_mode'], q=True, sl=True)
        selected_only = (mode == 2)
        self.joint_display.toggle_joint_display(show=True, selected_only=selected_only)
    
    def lock_attributes_callback(self, *args):
        t = cmds.checkBox(self.ui_elements['attr_translate'], q=True, value=True)
        r = cmds.checkBox(self.ui_elements['attr_rotate'], q=True, value=True)
        s = cmds.checkBox(self.ui_elements['attr_scale'], q=True, value=True)
        self.attr_locker.lock_unlock_attributes(lock=True, translate=t, rotate=r, scale=s)
    
    def unlock_attributes_callback(self, *args):
        t = cmds.checkBox(self.ui_elements['attr_translate'], q=True, value=True)
        r = cmds.checkBox(self.ui_elements['attr_rotate'], q=True, value=True)
        s = cmds.checkBox(self.ui_elements['attr_scale'], q=True, value=True)
        self.attr_locker.lock_unlock_attributes(lock=False, translate=t, rotate=r, scale=s)
    
    def save_asset_callback(self, *args):
        name = cmds.textField(self.ui_elements['asset_name'], q=True, text=True)
        format_type = cmds.optionMenu(self.ui_elements['save_format'], q=True, value=True)
        if self.asset_manager.save_asset(name, format_type):
            self.refresh_asset_list()


# Create and show the UI
def show_rigging_toolkit():
    """Main function to show the rigging toolkit"""
    toolkit = RiggingToolkitUI()
    toolkit.create_ui()

# Run the UI
if __name__ == "__main__":
    show_rigging_toolkit()