from Entities import Character
from Attacks import Attacks
from StatusEffects import StatusEffects
from Buffs import Buffs
import random
import heapq

class Vestal(Character):
    
    def __init__(self, position):
        
        actions_dict  = {}
        
        super().__init__(True, +0, 0.01, (4, 8), 0, 0.00, 4, 24, position, actions_dict, 0.30, 0.40, 0.30, 0.30, 0.30, 0.67)
        
        dazling_light_stun = StatusEffects("Stun", 1, 1.0, 1, "stun")
        dazling_light = Attacks((1, 2 ,3), (1, 2, 3), [lambda: StatusEffects("Stun", 1, 1.0, 1, "stun")], 90, (self.damage_base[0] * 0.25, self.damage_base[1] * 0.25), +0.05, is_unlimited = True, is_multi_target = False, is_stun = True, name = "Dazling_Light")
        
        judgement_heal = StatusEffects("Self_Heal", 0, 3.0, 3, "self_heal")
        judgement = Attacks((3, 4), (1, 2, 3, 4), [judgement_heal], 85, (int(self.damage_base[0] * 0.75), int(self.damage_base[1] * 0.75)), +0.05, is_unlimited = True, name = "Judgement")
        
        divine_grace_heal = StatusEffects("Heal", 999, 300, (4, 5), "heal")
        divine_grace = Buffs((3, 4), (1, 2, 3, 4), [divine_grace_heal], False, True, False, name = "Divine_Grace", is_heal = True)
        
        divine_comfort_heal = StatusEffects("Heal", 999, 300, (1, 3), "heal")
        divine_comfort = Buffs((2, 3, 4), (1, 2, 3, 4), [divine_comfort_heal], False, True, True, name = "Divine_Comfort", is_heal = True)
        
        mace_bash = Attacks((1, 2), (1, 2), [], 85, self.damage_base, 0, True, False, name = "Mace_Bash")
        
        self.actions_dict['judgement'] = judgement
        self.actions_dict['dazling_light'] = dazling_light
        self.actions_dict['divine_grace'] = divine_grace
        self.actions_dict['divine_comfort'] = divine_comfort
        #self.actions_dict['mace_bash'] = mace_bash
        
        # This action is only used for DEBUGGING!
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 0, (0, 0), 0, is_unlimited = True)
        #self.actions_dict['nothing'] = nothing
        
    def GetAction(self, every_grid):
        parent_action = self.policies.BestActionPolicy(every_grid.herogrid_dict, every_grid.enemygrid_dict)
        return parent_action
        
    def FocusFirstRankPolicy(self):
        if self.position not in [3, 4]:
            action_name = 'mace_bash'
            action_target = 1
        else:
            action_name = 'judgement'
            action_target = 1
        
        result = [action_name, action_target]
        return result