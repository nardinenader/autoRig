import maya.cmds as cmds


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