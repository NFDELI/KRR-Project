from entities.Character import Character
from actions.Attacks import Attacks
from StatusEffects import StatusEffects

class Cutthroat(Character):
    def __init__(self, position):
        super().__init__(False, +0, 0.05, (4, 8), 2.5, 0.15, 3, 12, position, {}, 0.25, 0.20, 0.20, 0.15, 0.25, -1)
        
        # Slice and Dice with decrease Bleed Res
        slice_and_dice_reduce_bleed_res = StatusEffects("Reduce_Bleed_Res", 3, 1.00, 0.15, "reduce_bleed_res")
        slice_and_dice = Attacks((1, 2, 3), (1, 2), [lambda: StatusEffects("Reduce_Bleed_Res", 3, 1.00, 0.15, "reduce_bleed_res")], 72.5, (3, 5), 0.12, is_multi_target = True, name = "Slice and Dice")
        
        # Shank with Bleed, default apply chance is 1.00
        shank_bleed = StatusEffects("Bleed", 3, 100.0, 1, "dot")
        shank = Attacks((1, 2, 3), (1, 2, 3, 4), [lambda: StatusEffects("Bleed", 3, 100.0, 1, "dot")], 72.5, (4, 8), 0.06, name = "Shank")
        
        # Uppercut Slice with Knockback
        uppercut_slice_knockback = StatusEffects("Knockback", 1, 1.00, 1, "knockback")
        uppercut_slice = Attacks((1, 2), (1, 2, 3), [uppercut_slice_knockback], 72.5, (2, 4), 0.06)
        
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 100, (0, 0), 0)
        
        self.actions_dict['slice_and_dice'] = slice_and_dice
        self.actions_dict['uppercut_slice'] = uppercut_slice
        self.actions_dict['shank'] = shank
        self.actions_dict['nothing'] = nothing
    
        self.idle_img = "visuals/cutthroat_anim/cutthroat_sprite_combat.png"
        self.defend_img = "visuals/cutthroat_anim/cutthroat_sprite_defend.png"
        self.shank_img = "visuals/cutthroat_anim/cutthroat_sprite_shank.png"
        self.slice_img = "visuals/cutthroat_anim/cutthroat_sprite_slice.png"
        
        self.offset = (0, 100)
        self.scale = (150, 300)
        self.text_offset = (150, 0)
        self.name = "Cutthroat"
        
    def GetAction(self, every_grid):
        return self.CutthroatPolicy(every_grid)

    def FocusFirstRankPolicy(self):
        action_name = 'shank'
        action_target = self.enemy_grid[1]
        result = [action_name, action_target, self.enemy_grid]
        return result
    
    def CutthroatPolicy(self, every_grid):
        # The cutthroat will keep using Slice and Dice 
        # UNLESS there is a low health hero (less than 50% hp) (Use Cut) 
        # or there is only rank 1 as a valid target (Use Cut or Point-Blank Shot)
        action_to_use = None
        action_target = None
        
        shank = self.actions_dict['shank']
        slice_and_dice = self.actions_dict['slice_and_dice']
        for hero in every_grid.herogrid_dict.values():
            if (hero.health < (hero.max_health * 0.5) or len(every_grid.herogrid_dict) == 1) and (self.policies.IsActionUsable(shank) and hero.position in shank.target_position):
                action_to_use = shank
                action_target = hero
                break
            elif(self.policies.IsActionUsable(slice_and_dice) and hero.position in shank.target_position):
                action_to_use = slice_and_dice
                action_target = every_grid.herogrid_dict[1]
        
        if not action_to_use or action_target:
            action_to_use = slice_and_dice
            action_target = every_grid.herogrid_dict[1]
        
        return action_to_use, action_target, every_grid.herogrid_dict
    
    def IsActionValid(self, action_value, every_grid):
        valid_targets = [
            hero for hero in every_grid.herogrid_dict.values()
            if hero.position in action_value.target_position
        ]
        return valid_targets