from entities.Character import Character
from actions.Attacks import Attacks
from StatusEffects import StatusEffects
from actions.Buffs import Buffs

class PlagueDoctor(Character):
    
    def __init__(self, position):
        
        actions_dict  = {}
        
        super().__init__(True, +0, 0.02, (4, 7), 0, 0.00, 7, 22, position, actions_dict, 0.20, 0.20, 0.60, 0.50, 0.20, 0.67) # Set HP Back to 22
        
        noxious_blast_blight = StatusEffects("Blight", 3, 1.0, 5, "dot")
        noxious_blast = Attacks((2, 3, 4), (1, 2), [lambda: StatusEffects("Blight", 3, 1.0, 5, "dot")], 95 , (int(self.damage_base[0] * 0.20), int(self.damage_base[1] * 0.20)), 0.05, name = "Noxious_Blast") # Change Accuracy back to 95
        
        plague_grenade_blight = StatusEffects("Blight", 3, 1.0, 4, "dot")
        plague_grenade = Attacks((3, 4), (3, 4), [lambda: StatusEffects("Blight", 3, 1.0, 4, "dot")], 95, (int(self.damage_base[0] * 0.10), int(self.damage_base[1] * 0.10)), 0.00, is_multi_target = True, name = "Plague_Grenade")
        
        # Blinding Gas does no damage!
        blinding_gas_stun = StatusEffects("Stun", 1, 1.0, 1, "stun")
        blinding_gas = Attacks((3, 4), (3, 4), [lambda: StatusEffects("Stun", 1, 1.0, 1, "stun")], 95, (0, 0), 0, is_multi_target = True, is_stun = True, name = "Blinding_Grenade")
        
        battlefield_medicine_cure = StatusEffects("Cure", 0, 999, 999, "cure")
        battlefield_medicine_heal = StatusEffects("Heal", 0, 999, (1, 1), "heal")
        battlefield_medicine = Buffs((3, 4), (1, 2, 3, 4), [battlefield_medicine_heal, battlefield_medicine_cure], False, True, False, name = "Battlefield_Medicine", is_heal = True)
        
        self.actions_dict["noxious_blast"] = noxious_blast
        self.actions_dict["plague_grenade"] = plague_grenade
        self.actions_dict["blinding_gas"] = blinding_gas
        self.actions_dict["battlefield_medicine"] = battlefield_medicine

        # This action is only used when the character cannot do any other action. (Usually due to mispositioning)
        nothing = Attacks((1, 2, 3, 4), (self.position,), [], 0, (0, 0), 0, is_unlimited = True, name = "Nothing")
        self.actions_dict['nothing'] = nothing
        
        self.idle_img = "visuals/doctor_anim/Plague_doctor_sprite_combat.png"
        self.defend_img = "visuals/doctor_anim/Plague_doctor_sprite_defend.png"
        self.grenade_img = "visuals/doctor_anim/Plague_doctor_sprite_grenade.png"
        self.heal_img = "visuals/doctor_anim/Plague_doctor_sprite_heal.png"
        
        self.offset = (0, 100)
        self.scale = (150, 300)
        self.text_offset = (0, 0)
        self.name = "Plague Doctor"
        
    def GetAction(self, every_grid):
        parent_action = self.policies.BestActionPolicy(every_grid.herogrid_dict, every_grid.enemygrid_dict)
        return parent_action
    
    def FocusFirstRankPolicy(self):
        action_name = 'noxious_blast'
        action_target = 1
        result = [action_name, action_target]
        return result