from entities.Character import Character
from actions.Attacks import Attacks
from StatusEffects import StatusEffects
from actions.Buffs import Buffs

class HighwayMan(Character):
    
    def __init__(self, position):
        
        actions_dict  = {}
        
        super().__init__(True, +0, 0.05, (5, 10), 10, 0.00, 5, 23, position, actions_dict, 0.30, 0.30, 0.30, 0.30, 0.30, 0.67)
        
        grape_shot_blast_debuff = StatusEffects("Increase_Crit_Taken", 3, 1.0, 0.04, "increase_crit_taken")
        open_vein_bleed = StatusEffects("Bleed", 3, 1.0, 2, "dot")
        open_vein_reduce_bleed_res = StatusEffects("Reduce_Bleed_Res", 3, 1.0, 0.2, "reduce_bleed_res")
        open_vein_reduce_speed = StatusEffects("Reduce_Speed", 3, 1.0, 1, "reduce_speed")
        
        wicked_slice = Attacks((1, 2, 3), (1, 2), [], 85, (int(self.damage_base[0] * 1.15), int(self.damage_base[1] * 1.15)), 0.05, is_unlimited = True, name = "Wicked_Slice")
        pistol_shot = Attacks((2, 3, 4), (2, 3, 4), [], 85, (int(self.damage_base[0] * 0.85), int(self.damage_base[1] * 0.85)), 0.075, is_unlimited = True, name = "Pistol_Shot")
        grape_shot_blast = Attacks((2, 3), (1, 2, 3), [lambda: StatusEffects("Increase_Crit_Taken", 3, 1.0, 0.04, "increase_crit_taken")], 75, (int(self.damage_base[0] * 0.5), int(self.damage_base[1] * 0.5)), -0.09, is_multi_target = True, name = "Grape_Shot_Blast")
        open_vein = Attacks((1, 2, 3), (1, 2), [lambda:StatusEffects("Bleed", 3, 1.0, 2, "dot"), lambda: StatusEffects("Reduce_Bleed_Res", 3, 1.0, 0.2, "reduce_bleed_res"), lambda: StatusEffects("Reduce_Speed", 3, 1.0, 1, "reduce_speed")], 95, ((int(self.damage_base[0] * 0.85), int(self.damage_base[1] * 0.85))), 0.0, is_unlimited = True, name = "Open_Vein")
        
        self.actions_dict['wicked_slice'] = wicked_slice
        self.actions_dict['pistol_shot'] = pistol_shot
        self.actions_dict['grape_shot_blast'] = grape_shot_blast
        self.actions_dict['open_vein'] = open_vein
        
        # This action is only used for DEBUGGING!
        nothing = Attacks((1, 2, 3, 4), (1,), [], 0, (0, 0), 0, is_unlimited = True, name = "Nothing", is_multi_target = False)
        self.actions_dict['nothing'] = nothing
        
    def GetAction(self, every_grid):    
        parent_action = self.policies.BestActionPolicy(every_grid.herogrid_dict, every_grid.enemygrid_dict)
        return parent_action
    
    def FocusFirstRankPolicy(self):
        action_name = 'open_vein'
        action_target = 1
        result = [action_name, action_target]
        return result