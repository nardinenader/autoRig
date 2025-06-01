import maya.cmds as cmds
from functools import partial

from RigBuilder import RigBuilder
from ObjRenamer import ObjectRenamer
from AssetMGMT import AssetManager
from skinWeightMGMT import SkinWeightManager
from attributeLocker import AttributeLocker
from JointDisplayMGMT import JointDisplayManager




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