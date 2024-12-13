from Entities import Character
from Attacks import Attacks
from StatusEffects import StatusEffects
import random

class BoneCourtier(Character):
    def __init__(self, position):
        super().__init__(False, +0, 0.05, (2, 4), 12.5, 0, 8, 10, position, {}, 0.1, 2.00, 0.10, 0.15, 0.10, -1)
    
        tempting_goblet = Attacks((2, 3, 4), (1, 2, 3, 4), [], 92.5, (2, 4), 0.0, stress_damage = 15)
        knife_in_dark = Attacks((1, 2), (1, 2), [], 62.5, (2, 4), 0.06) 
        
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 0, (0, 0), 0)
        
        self.actions_dict['tempting_goblet'] = tempting_goblet
        self.actions_dict['knife_in_dark'] = knife_in_dark
        self.actions_dict['nothing'] = nothing
        
    def GetAction(self, every_grid):
        # parent_action = super().GetAction(every_grid)
        # return parent_action
        return self.FocusFirstRankPolicy(every_grid)
    
    def FocusFirstRankPolicy(self, every_grid):
        available_targets = list(every_grid.enemygrid_dict.keys())
        
        # WORK IN PROGRESS!
        if self.position == 1 or self.position == 2:
            action_name = 'knife_in_dark'
            action_target = 1
        else:
            action_name = 'tempting_goblet'

        # Target enemies if its an attack action
        common_targets = list(set(available_targets) & set(self.actions_dict[action_name].target_position))
        if (common_targets):
            # Add current action to 'new' available actions to choose with targets!
            action_target = random.choice(common_targets)
            result = [action_name, action_target, self.enemy_grid]
            return result
        return ['nothing', [1], self.enemy_grid]