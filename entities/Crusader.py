from entities.Character import Character
from actions.Attacks import Attacks
from StatusEffects import StatusEffects
from actions.Buffs import Buffs

class Crusader(Character):
    """
    DECISION VARIABLES:
    1. actions_dict: A Dictionary of actions that each character can use.
    """
    # Attacks class format: position_req, target_position, apply_status_effects, accuracy, damage_range, crit, is_unlimited, 
    #                                 is_multi_target, is_traget_friendly, is_stun , name
    def __init__(self, position):
        
        actions_dict  = {}
        
        super().__init__(True, +0, 0.05, (6, 12), 5, 0.00, 0, 33, position, actions_dict, 0.40, 0.30, 0.30, 0.30, 0.40, 0.67)
        
        stunning_blow_stun = StatusEffects("Stun", 1, 1.0, 1, "stun")
        stunning_blow = Attacks((1, 2), (1, 2), [stunning_blow_stun], 90, (int(self.damage_base[0] * 0.5), int(self.damage_base[0] * 0.5)), +0, is_unlimited = True, is_multi_target = False, is_stun = True, name = "Stunning_Blow")
        smite = Attacks((1, 2), (1, 2), [], 85, self.damage_base * 1, +0, is_unlimited = True, name = "Smite")
        
        # Make sure to Round the Damage ranges into Integers or else it will cause errors!
        zealous_accusation = Attacks((1, 2), (1, 2), [], 85, (int(self.damage_base[0] * 0.6), int(self.damage_base[1] * 0.6)), -0.04, is_unlimited = True, is_multi_target = True, name = "Zealous_Accusation")

        faith_mark = StatusEffects("Mark", 999, 300, -1, "mark")
        faith_prot = StatusEffects("Increase_Prot", 999, 300, 0.2, "increase_prot")
        bulwark_of_faith = Buffs((1, 2), [self.position], [lambda: StatusEffects("Mark", 999, 300, -1, "mark"), lambda:StatusEffects("Increase_Prot", 999, 300, 0.2, "increase_prot")], 1, False, name = "Bulwark_of_Faith")

        inspiring_cry = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 10.00, (0, 0), 0, True, stress_damage = -5, is_traget_friendly = True, name = "Inspiring_Cry")
        
        self.actions_dict['smite'] = smite
        self.actions_dict['stunning_blow'] = stunning_blow
        self.actions_dict['zealous_accusation'] = zealous_accusation
        # self.actions_dict['bulwark_of_faith'] = bulwark_of_faith
        # self.actions_dict['inspiring_cry'] = inspiring_cry
        # This action is only used when the character cannot do any other action. (Usually due to mispositioning)
        nothing = Attacks((1, 2, 3, 4), (1,), [], 0, (0, 0), 0, is_unlimited = True, name = "Nothing")
        self.actions_dict['nothing'] = nothing
        
        # Visual Images:
        self.idle_img = "visuals/crusader_anim/Crusader_sprite_combat.png"
        self.defend_img = "visuals/crusader_anim/Crusader_sprite_defend.png"
        self.stun_img = "visuals/crusader_anim/Crusader_sprite_stun.png"
        self.swing_img = "visuals/crusader_anim/Crusader_sprite_swing.png"
        self.paper_img = "visuals/crusader_anim/Crusader_sprite_paper.png"
        self.offset = (0, 0)
        self.scale = (150, 400)
        self.text_offset = (0, 0)

        self.name = "Crusader"

    def GetAction(self, every_grid):
        parent_action = self.policies.BestActionPolicy(every_grid.herogrid_dict, every_grid.enemygrid_dict)
        return parent_action
    
    def FocusFirstRankPolicy(self):
        action_name = 'smite'
        action_target = 1
        result = [action_name, action_target]
        return result