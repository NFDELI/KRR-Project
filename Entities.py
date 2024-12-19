from Attacks import Attacks
from StatusEffects import StatusEffects
from Policies import Policies
from my_utils import update_positions
import random
import heapq
        
class Character:
    is_player : bool
    accuracy_base : int
    crit : float
    damage_base: tuple
    dodge: int
    protection: float
    speed: int
    health: int
    max_health: int
    stress: int
    position: float
    status_effects: list
    actions_dict: dict
    initiative: int

    def __init__(self, is_player, accuracy_base, crit, damage_base, dodge, protection, speed, max_health, position, actions_dict, stun_res, bleed_res, blight_res, debuff_res, move_res, death_blow_res):
        self.is_player = is_player
        self.accuracy_base = accuracy_base
        self.crit = crit
        self.damage_base = damage_base
        self.dodge = dodge
        self.protection = protection
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.stress = 0
        self.position = position
        self.actions_dict = actions_dict
        self.initiative = 1
        self.is_at_death_door = False
        self.is_death_door_recovering = False
        self.status_effects = []
        self.is_stunned = False
        self.is_bleeding = False
        self.is_blighted = False
        self.is_marked = False
        self.has_taken_action = False
        
        self.base_is_bleeding = False
        self.base_is_blighted = False
        self.base_is_stunned = False
        self.base_is_marked = False
        
        self.base_stun_res = stun_res
        self.base_bleed_res = bleed_res
        self.base_speed = speed

        self.stun_res = stun_res
        self.bleed_res = bleed_res
        self.blight_res = blight_res
        self.debuff_res = debuff_res
        self.move_res = move_res
        self.death_blow_res = death_blow_res
        
        self.extra_crit_taken = 0
        
        self.team_grid = {}
        self.enemy_grid = {}
        self.is_corpse = False
        self.initiative = 0
        self.is_dead = False
        
        self.policies = Policies(self)
    
    def __lt__(self, other):
        return self.health < other.health
    
    def StartTurn(self, policy_evaluator):
        
        if(self.is_dead):
            print(f"{self.__class__.__name__}'s [{self.position}] turn is skipped because they died!")
            del self.status_effects
            return False
        
        # Process effects safely
        for effect in self.status_effects[:]:
            if effect.name in ["Bleed", "Blight"]:
                effect.ApplyEffect(self, policy_evaluator)
                self.ReduceStatusEffectsDuration(effect)
            
            if(effect.name == "Stun"):
                self.is_stunned = True
            
            if(effect.name == "Knockback"):
                effect.ApplyEffect(self, policy_evaluator)
                self.ReduceStatusEffectsDuration(effect)
            
            if(effect.name == "Increase_Stun_Res"):
                effect.ApplyEffect(self, policy_evaluator)
                self.ReduceStatusEffectsDuration(effect)
            
            if(effect.name == "Increase_Prot"):
                # Protection buff is applied Immediately After the move is used!
                self.ReduceStatusEffectsDuration(effect)
                
            if(effect.name == "Reduce_Bleed_Res"):
                # Protection buff is applied Immediately After the move is used!
                self.ReduceStatusEffectsDuration(effect)
                
            if(effect.name == "Reduce_Speed"):
                # Applied immediately!
                self.ReduceStatusEffectsDuration(effect)
                
            if(effect.name == "Mark"):
                effect.ApplyEffect(self, policy_evaluator)
                self.ReduceStatusEffectsDuration(effect)
            
            if(effect.name == "Increase_Crit_Taken"):
                self.ReduceStatusEffectsDuration(effect)
                    
        # Check if character stunned.
        if(self.is_stunned):
            print(f"{self.__class__.__name__}'s turn is skipped from being stunned!")
            #self.is_stunned = False
            self.ReduceStatusEffectsDuration(effect)
            
            # Used to trigger the remove +stun res
            self.status_effects.append(StatusEffects("Increase_Stun_Res", 1, 3.0, 0, "increase_stun_res"))
            self.stun_res += 0.5
            print(f"{__class__.__name__} got Increased Stun res into {self.stun_res} from recovering from stun!")
            
            # Skips Turn
            return False
        
        if(self.is_dead):
            print(f"{self.__class__.__name__}'s [{self.position}] turn is skipped because DIED FROM DOTs !")
            return False
        
        # Character can take their Turn.
        return True
    
    def ReduceStatusEffectsDuration(self, effect):
        # print(f"Processing effect: {effect.name}, Duration: {effect.duration}")
        # print(f"Effect ID: {id(effect)}, Name: {effect.name}, Duration: {effect.duration}")
        # print("\n")
        effect.duration -= 1
        if effect.duration <= 0:
            # Properly remove only the expired effect
            effect.RemoveEffect(self)
            if effect in self.status_effects:
                self.status_effects.remove(effect)

    def TakeDamage(self, damage, policy_evaluator):
        if self.is_player:
            policy_evaluator.UpdateEnemyDamage(self.health if self.health - damage <= 0 else damage)
        else:
            policy_evaluator.UpdateHeroDamage(self.health if self.health - damage <= 0 else damage)
        
        self.health = self.health - damage
        if(self.health < 0):
            self.health = 0
        self.CheckCharacterHealth(policy_evaluator)
        
    def TakeStressDamage(self, stress_damage):
        self.stress = self.stress + stress_damage
    
    def CheckCharacterHealth(self, policy_evaluator):
        if(self.health <= 0):
            if(self.is_player):
                if self.is_at_death_door == False:
                    policy_evaluator.UpdateHeroEnteredDeathDoor(self)
                    # Player Character Enters Death's Door.
                    self.is_at_death_door = True
                    self.is_death_door_recovering = False
                    print(f"{self.__class__.__name__} Entered Death's Door!")
                    return
                else:
                    # Player Character is already at Death's Door, roll rng to see if Player Character will die.
                    isDeathSuccess = random.random() < self.death_blow_res
                    if isDeathSuccess:
                        policy_evaluator.UpdateHeroDied()
                        self.CharacterDies()
                    else:
                        print(f"{self.__class__.__name__} SURVIVED DEATH BLOW")
            else:
                self.CharacterDies()
        else:
            if(self.is_player):
                self.is_at_death_door = False
                self.is_death_door_recovering = True
    
    def Move(self, move_amount):
        # Referencing Second Rank guy and switching place with them.
        # If you want to move more than 1 rank, call this move function multiple times!
        if(self.team_grid.get(self.position + move_amount)):
            self.team_grid[self.position + move_amount].position = self.position
            self.position += move_amount
            
        #else:
            # Person not found at that empty spot.
            #self.position += move_amount

        # Prevent Characters moving over the limit.
        if self.position > 4:
            self.position = 4
        elif self.position < 1:
            self.position = 1
        
        # Move Function called!
        # Update the main team grids
        print("Move Function called!")
        update_positions(self.team_grid)

    def HealDamage(self, heal_amount, policy_evaluator):
        # Enemy does not have healing actions for now.
        if self.is_player:
            policy_evaluator.UpdateHeroHeal(self.max_health - self.health if self.health + heal_amount >= self.max_health else heal_amount)
            
        self.health = self.health + heal_amount
        
        if(self.health > self.max_health):
            self.health = self.max_health
    
    def DoAction(self, action_name, chosen_target, grid_target, policy_evaluator):
        
        if not self.StartTurn(policy_evaluator):
            return False

        if isinstance(action_name, str):
            chosen_action = self.actions_dict[action_name]
            action_name_str = action_name
        else:
            chosen_action = action_name
            action_name_str = action_name.name
    
        # Check if requirements for actions are met.
        if(self.position not in chosen_action.position_req or chosen_target.position not in chosen_action.target_position):
            print(f"Invalid Position Input! from using {action_name_str} \nwith caster position: {self.position} \nand target position: {chosen_target.position}")
            return False    
        
        # Check if action is Multi Target.
        print(f"{self.__class__.__name__} used action: {action_name_str}! \n")
        if(chosen_action.is_multi_target):
            targets_data = []
            results_data = []
            for targets in chosen_action.target_position:
                # Check if Key is valid
                if targets in grid_target:
                    result = chosen_action.DoAction(self, grid_target[targets], policy_evaluator)
                    targets_data.append(grid_target[targets])
                    results_data.append(result)
                    #print(f"{self.__class__.__name__} used action: {action_name_str}! \n")
                    
            policy_evaluator.UpdateCharacterActionLog(self, targets_data, action_name_str, results_data)
        else:
            result = chosen_action.DoAction(self, chosen_target, policy_evaluator)
            policy_evaluator.UpdateCharacterActionLog(self, [chosen_target], action_name_str, [result])
            #print(f"{self.__class__.__name__} used action: {action_name_str}! \n")    
    
    def CharacterDies(self):
        # Make sure that corpse Disappears when hp of Corpse go to 0.
        self.is_dead = True
        if(self.is_corpse):
            print(f"CORPSE DETECTED! [{self.position}]")
            self.CharacterDisappear()
        else:
            # Player Characters do not spawn Corpses on Death.
            if(self.is_player):
                print(f"Player {self.__class__.__name__} [{self.position}] DIED!")
                self.CharacterDisappear()
            else:
                # Create Corpse and Replace Dead Character with corpse.
                print(f"{self.__class__.__name__} [{self.position}] DIED!!")
                corpse = Corpse(self.position, self.max_health, self.team_grid)
                self.team_grid[self.position] = corpse
                update_positions(self.team_grid)

    def CharacterDisappear(self):        
        del self.team_grid[self.position]
        
        # When looping through dictionaries, do not edit the keys when looping through it!
        for values in self.team_grid.values():
            if values.position > self.position:
                values.position -= 1
                # Prevent Characters moving over the limit.
                if values.position > 4:
                    values.position = 4
                elif values.position < 1:
                    values.position = 1
        
        update_positions(self.team_grid)

    # The goal of this function is to make a generalized Get Action for everyone.
    def GetAction(self, every_grid):
        return self.RandomTargetPolicy(every_grid)
    
class Corpse(Character):
    # Corpse will have a portion of the owner's max hp.
    def __init__(self, position, owner_max_health, owner_team_grid):
        super().__init__(False, +0, 0.00, (0, 0), 0, 0, -999, int(owner_max_health * 0.5), position, {}, 0, 0.0, 0.0, 2.0, 2.0, -1)
        nothing = Attacks((1, 2, 3, 4), (1, 2, 3, 4), [], 100, (0, 0), 0)
        self.actions_dict['nothing'] = nothing
        self.decay_counter = 1
        self.is_corpse = True
        self.team_grid = owner_team_grid
    
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

    
  

