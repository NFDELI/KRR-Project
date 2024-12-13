from Entities import Character
from Attacks import Attacks
from StatusEffects import StatusEffects

class BoneDefender(Character):
    def __init__(self, position):
        super().__init__(False, +0, 0.05, (2, 4), 0, 0.25, 0, 15, position, {}, 0.25, 2.00, 0.10, 0.15, 0.50, -1)
    
        axe_blade = Attacks((1, 2), (1, 2), [], 72.5, (3, 5), 0.06, True, False)
        
        dead_weight_effect = StatusEffects("Self_Knockback", 0, 999, 1, "knockback")
        dead_weight = Attacks((1, 2), (1, 2), [dead_weight_effect], 82.5, (2, 4), 0.06) 
        
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 0, (0, 0), 0)
        
        self.actions_dict['axe_blade'] = axe_blade
        self.actions_dict['dead_weight'] = dead_weight
        self.actions_dict['nothing'] = nothing
        
    def GetAction(self):
        parent_action = super().GetAction()
        return parent_action
    
    def FocusFirstRankPolicy(self):
        if self.position == 1:
            action_name = 'rushed_shot'
            action_target = 1
        else:
            action_name = 'blanket_fire'
            action_target = 1

        result = [action_name, action_target, self.enemy_grid]
        return result