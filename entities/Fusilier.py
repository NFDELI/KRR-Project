from entities.Character import Character
from actions.Attacks import Attacks
from StatusEffects import StatusEffects

class Fusilier(Character):
    def __init__(self, position):
        super().__init__(False, +0, 0.05, (2, 4), 7.5, 0, 6, 12, position, {}, 0.25, 0.20, 0.20, 0.15, 0.25, -1)
    
        blanket_fire_debuff = StatusEffects("Reduce_Dodge", 3, 1.0, 0.2, "reduce_dodge")
        blanket_fire = Attacks((2, 3, 4), (1, 2, 3, 4), [lambda: StatusEffects("Reduce_Dodge", 3, 1.0, 0.2, "reduce_dodge")], 72.5, (1, 3), 0.0, is_multi_target = True, name = "Blanket_Fire")
        
        # Rushed Shot Knocksback the Fusilier.
        rushed_shot_buff = StatusEffects("Self_Knockback", 0, 999, 1, "knockback")
        rushed_shot = Attacks((0, 1, 2, 3, 4), (1, 2, 3), [rushed_shot_buff], 62.5, (2, 4), 0.06) 
        
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 0, (0, 0), 0)
        
        self.actions_dict['blanket_fire'] = blanket_fire
        self.actions_dict['rushed_shot'] = rushed_shot
        self.actions_dict['nothing'] = nothing
        
        self.idle_img = "visuals/fusilier_anim/fusilier_sprite_combat.png"
        self.attack_img = "visuals/fusilier_anim/fusilier_sprite_attack.png"
        self.defend_img = "visuals/fusilier_anim/fusilier_sprite_defend.png"
        
        self.offset = (0, 100)
        self.scale = (150, 300)
        self.text_offset = (0, 0)
        self.name = "Fusilier"
        
    def GetAction(self, every_grid):
        return self.FocusFirstRankPolicy(every_grid)
    
    def FocusFirstRankPolicy(self, every_grid):
        if self.position == 1:
            action_name = 'rushed_shot'
            action_target = every_grid.herogrid_dict[1]
        else:
            action_name = 'blanket_fire'
            action_target = every_grid.herogrid_dict[1]

        result = [action_name, action_target, self.enemy_grid]
        return result