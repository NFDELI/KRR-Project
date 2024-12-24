from entities.Character import Character
from actions.Attacks import Attacks
class Corpse(Character):
    # Corpse will have a portion of the owner's max hp.
    def __init__(self, position, owner_max_health, owner_team_grid):
        super().__init__(False, +0, 0.00, (0, 0), 0, 0, -999, int(owner_max_health * 0.5), position, {}, 0, 0.0, 0.0, 2.0, 2.0, -1)
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 100, (0, 0), 0)
        self.actions_dict['nothing'] = nothing
        self.decay_counter = 1
        self.is_corpse = True
        self.team_grid = owner_team_grid
        
        self.idle_img = "visuals/corpse_anim/cutthroat_sprite_dead.png"
        self.offset = (0, 300)
        self.scale = (150, 100)
        self.text_offset = (0, 0)
        self.name = "Corpse"

    def Decompose(self):
        if(self.decay_counter > 4):
            self.CharacterDisappear()
        
        should_end_fight = True
        for values in self.team_grid.values():
            if(values.__class__.__name__ == "Corpse"):
                return
            else:
                should_end_fight = False

        if(should_end_fight):
            self.CharacterDisappear()
    
    def GetAction(self):
        result = ['nothing', 1]
        return result