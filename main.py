import numpy as np
from my_utils import update_positions
from my_utils import all_values_of_class
from Crusader import Crusader
from HighwayMan import HighwayMan
from PlagueDoctor import PlagueDoctor
from Vestal import Vestal
from Cutthroat import Cutthroat
from Fusilier import Fusilier
from BoneCourtier import BoneCourtier
import random
from collections import deque
from Entities import Corpse

class Grid():
    def __init__(self, herogrid, enemygrid):
        self.herogrid_dict = herogrid
        self.enemygrid_dict = enemygrid
        self.round_counter = 0

class PolicyEvaluator:
    def __init__(self):
        self.total_hero_damage = 0
        self.total_hero_heal = 0
        self.total_enemy_damage = 0
        self.total_hero_entered_death_door = 0
        self.total_hero_died = 0
        self.fight_end_score = 0
    
    def UpdateHeroDamage(self, damage):
        self.total_hero_damage += damage
    
    def UpdateHeroHeal(self, heal):
        self.total_hero_heal += heal
        
    def UpdateEnemyDamage(self, damage):
        self.total_enemy_damage += damage
    
    # This function should only called if it is the first time that the hero has entered death's door, not calculating death's door recovery.
    def UpdateHeroEnteredDeathDoor(self, hero):
        if not hero.is_death_door_recovering:
            self.total_hero_entered_death_door += 15
    
    def UpdateHeroDied(self):
        self.total_hero_died += 40
    
    def EvaluateRound(self, hero_grid):
        round_score = self.total_hero_damage + self.total_hero_heal - self.total_enemy_damage - self.total_hero_entered_death_door - self.total_hero_died
        self.fight_end_score += round_score
        self.ResetCounters()
        print(f"Round Score: {round_score}")
        return self.fight_end_score

    # This function is called when evaluating the total health that each hero has at the end of the simulation.
    def GetTotalHeroTeamHealth(self, hero_grid):
        total_health = 0
        for hero in hero_grid.values():
            total_health += hero.health
    
        return total_health

    def ResetCounters(self):
        self.total_hero_damage = 0
        self.total_hero_heal = 0
        self.total_enemy_damage = 0
        self.total_hero_entered_death_door = 0
        self.total_hero_died = 0
    
def GenerateNextRound(herogrid_dict, enemygrid_dict, grid):
    grid.round_counter += 1
    print(f"Round {grid.round_counter} Started!")
    
    initiative_queue = deque()
    
    # Get Every Character's Speed and Do Rng of Speed of each character
    for values in herogrid_dict.values():
        speed_rng = random.randint(1, 8)
        values.has_taken_action = False
        values.initiative = speed_rng + values.speed
        initiative_queue.append(values)
        
    for values in enemygrid_dict.values():
        # Make sure that Corpses dont take any action
        if values.is_corpse:
            values.Decompose()
            continue
        speed_rng = random.randint(1, 8)
        values.has_taken_action = False
        values.initiative = speed_rng + values.speed
        initiative_queue.append(values)
    
    initiative_queue = deque(sorted(initiative_queue, key=lambda Character: Character.initiative, reverse=True))
    return initiative_queue

def main():
    
    # Heroes
    Reynald = Crusader(position = 1)
    Dismas = HighwayMan(position = 2)
    Paracelsus = PlagueDoctor(position = 3)
    Junia = Vestal(position = 4)
    
    # Enemies
    Mald = Cutthroat(position = 1)
    Axel = Fusilier(position = 2)
    Carlos = Cutthroat(position = 3)
    Miguel = Fusilier(position = 4)
    
    #TEST STRESS SKELETONS
    Quary = BoneCourtier(position = 3)
    
    herogrid_dict = {
        Reynald.position : Reynald,
        Dismas.position : Dismas,
        Paracelsus.position : Paracelsus,
        Junia.position : Junia
    }
    
    enemygrid_dict = {
        Mald.position : Mald,
        Axel.position : Axel,
        Carlos.position : Carlos,
        Miguel.position : Miguel,
        #Quary.position: Quary
    }
    
    grid = Grid(herogrid_dict, enemygrid_dict)
    policy_evaluator = PolicyEvaluator()
    
    # Assign team and enemy grids for heroes
    heroes = [Reynald, Dismas, Paracelsus, Junia]
    for hero in heroes:
        hero.team_grid = grid.herogrid_dict
        hero.enemy_grid = grid.enemygrid_dict

    # Assign team and enemy grids for enemies
    enemies = [Mald, Axel, Carlos, Miguel, Quary]
    for enemy in enemies:
        enemy.team_grid = grid.enemygrid_dict
        enemy.enemy_grid = grid.herogrid_dict
    
    # grid.herogrid_dict[1].DoAction("inspiring_cry", grid.herogrid_dict[2], grid.herogrid_dict)
    # grid.herogrid_dict[1].DoAction("inspiring_cry", grid.herogrid_dict[1], grid.herogrid_dict)
        
    while(grid.herogrid_dict and (not all_values_of_class(grid.enemygrid_dict, Corpse) and grid.round_counter < 20)):
        
        print(f"==========Hero Team=============")
        for key, value in grid.herogrid_dict.items():
            print(f"Position Key: {key}, Value: {value.__class__.__name__}, Health: {value.health}, Stunned: {value.is_stunned}")
        print("\n\n")
        print(f"==========Enemy Team=============")
        for key, value in grid.enemygrid_dict.items():
            print(f"Position Key: {key}, Value: {value.__class__.__name__}, Health: {value.health}, Stunned: {value.is_stunned}")
        print("\n\n")    
        turn_order = GenerateNextRound(grid.herogrid_dict, grid.enemygrid_dict, grid)
        
        # Display Turn Order
        # for i, character in enumerate(turn_order, start = 1):
        #     print(f"{i}: {character.__class__.__name__} with initiative {character.initiative}")
        
        while turn_order:
            if (not grid.herogrid_dict or (all_values_of_class(grid.enemygrid_dict, Corpse) or not grid.enemygrid_dict)):
                break
            character_to_act = turn_order.popleft()
            character_decision, character_target, target_grid = character_to_act.GetAction(grid)
            
            character_to_act.DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
            character_to_act.has_taken_action = True
            #print(f"{character_to_act.__class__.__name__}'s is_dead Boolean is: {character_to_act.is_dead}")
            print("\n")
        
        print("TURN ORDER FINISHED")
        # Evaluate Each Round's Score
        policy_evaluator.EvaluateRound(grid.herogrid_dict)
    
    print("====================================================")
    print(f"Simulation Ended with {grid.round_counter} rounds!")
    print(f"Total Fight Score {policy_evaluator.EvaluateRound(grid.herogrid_dict)}!")
    print("====================================================")
        # Display Turn Order
    for value in grid.herogrid_dict.values():
        print(f"{value.__class__.__name__} has {value.health} hp left!")    

def MyTest():
    # Heroes
    Reynald = Crusader(position = 1)
    Dismas = HighwayMan(position = 2) # Change this back to 2 later!
    Paracelsus = PlagueDoctor(position = 3) # Change this back to 3 later!
    Junia = Vestal(position = 4)
    
    Reynald.policies.turn_weight = 0
    Reynald.policies.stun_weight = 8
    Reynald.policies.kill_weight = 10
    Reynald.policies.rank_weight = 7
    Reynald.policies.health_weight = 6
    
    # Enemies
    Mald = Cutthroat(position = 1)
    Mald.health = 11
    Axel = Fusilier(position = 2)
    Axel.health = 11
    Axel.has_taken_action = True
    Carlos = Cutthroat(position = 3)
    Miguel = Fusilier(position = 4)
    
    #TEST STRESS SKELETONS
    Quary = BoneCourtier(position = 3)
    
    herogrid_dict = {
        Reynald.position : Reynald,
        # Dismas.position : Dismas,
        # Paracelsus.position : Paracelsus,
        # Junia.position : Junia
    }
    
    enemygrid_dict = {
        Mald.position : Mald,
        Axel.position : Axel,
        Carlos.position : Carlos,
        Miguel.position : Miguel,
        # Quary.position: Quary
    }
    
    grid = Grid(herogrid_dict, enemygrid_dict)
    policy_evaluator = PolicyEvaluator()
    
    # Assign team and enemy grids for heroes
    heroes = [Reynald, Dismas, Paracelsus, Junia]
    for hero in heroes:
        hero.team_grid = grid.herogrid_dict
        hero.enemy_grid = grid.enemygrid_dict

    # Assign team and enemy grids for enemies
    enemies = [Mald, Axel, Carlos, Miguel, Quary]
    for enemy in enemies:
        enemy.team_grid = grid.enemygrid_dict
        enemy.enemy_grid = grid.herogrid_dict
    
    print("ROUND 1")
    print("=================================================================================")
    character_decision, character_target, target_grid = grid.herogrid_dict[1].GetAction(grid)
    grid.herogrid_dict[1].DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
    
    # character_decision, character_target, target_grid = grid.herogrid_dict[1].GetAction(grid)
    # grid.herogrid_dict[1].DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
    
    # character_decision, character_target, target_grid = grid.herogrid_dict[1].GetAction(grid)
    # grid.herogrid_dict[1].DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
    
    # character_decision, character_target, target_grid = grid.herogrid_dict[1].GetAction(grid)
    # grid.herogrid_dict[1].DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
    print("=================================================================================")
    # print("=================================================================================")
    # print("ROUND 2\n")
    # grid.enemygrid_dict[1].DoAction("shank", grid.herogrid_dict[1], grid.enemygrid_dict)
    # grid.herogrid_dict[1].DoAction("nothing", grid.enemygrid_dict[1], grid.enemygrid_dict)
    # print("=================================================================================")
    # print("=================================================================================")
    # print("ROUND 3\n")
    # grid.enemygrid_dict[1].DoAction("shank", grid.herogrid_dict[1], grid.enemygrid_dict)
    # grid.herogrid_dict[1].DoAction("nothing", grid.enemygrid_dict[1], grid.enemygrid_dict)
    # print("=================================================================================")
    # print("=================================================================================")
    # print("ROUND 4\n")
    # grid.herogrid_dict[3].DoAction("battlefield_medicine", grid.herogrid_dict[1], grid.herogrid_dict)
    # grid.enemygrid_dict[1].DoAction("nothing", grid.herogrid_dict[1], grid.enemygrid_dict)
    # print("=================================================================================")
    # print("=================================================================================")
    # print("ROUND 5\n")
    # grid.herogrid_dict[1].DoAction("nothing", grid.herogrid_dict[1], grid.herogrid_dict)
    # #grid.enemygrid_dict[1].DoAction("nothing", grid.herogrid_dict[1], grid.enemygrid_dict)
    # print("=================================================================================")


    # Effect = lambda : Crusader(position = 1)
    # Other = Effect()
    # print(Other.health)
     
main()


# TODO:
# Add Policy/Strategies for each hero
# Add Policy Evaluation (Need to Add Evaluation for Entering Death's Door and Killing Heroes or Enemies)
# Need to Test BestHealPolicy. (Ok, need to check specifics next, like which heal is being used? Bulk heal or spread heal?)
# Need to Add different alternative policies to test performance of policy.
# Need to add value to cure DOTs. (Need Testing!)
# BestActionPolicy can be further improved where for example, Enemy Cutthroat has 3 hp, and 6 damage blight DOT, not yet taken turn, Highwayman still finished him off even though cutthroat will die anyway.

#TODO:
"""
1. Consider Actions that can kill multiple targets at once. (Need to be Tested) (IDK)
2. Consider Blight or Bleed that can kill targets that havent taken their turn. (Ok)
3. Consider Hitting Corpses if their is not targets available. (Next Priority) 
4. Consider healing teamates if they have blight or bleed or low hp instead of attacking.

BUG:
1. Crusader Never stuns an enemy, he always use Zealous accusation, maybe I need to value stun even more!.
"""

"""
BUGFIX:
1. Fixed bug about how status effects are not processed properly, blight and bleed, etc... (NEED TO REFACTOR POLICY CODE)
2. Applied the same technique of iterating through a copy of the list for curing (battlefield medicine) to remove bleed and blight!
"""
