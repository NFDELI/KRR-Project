class Actions:
    is_player_action: bool
    is_attack: bool
    position_req: tuple
    target_position: tuple
    limited_use: int
    crit = float

    def __init__(self, is_player_action, is_attack, position_req, target_position, limited_use, apply_status_effects, crit = 0, is_buff = False, is_heal = False):
        self.is_player_action = is_player_action
        self.is_attack = is_attack
        self.position_req = position_req
        self.target_position = target_position
        self.limited_use = limited_use
        self.apply_status_effects = apply_status_effects
        self.crit = crit
        self.is_buff = is_buff
        self.is_heal = is_heal
    
    