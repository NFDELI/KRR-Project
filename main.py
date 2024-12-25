import numpy as np
from my_utils import update_positions
from my_utils import all_values_of_class
from entities.Crusader import Crusader
from entities.HighwayMan import HighwayMan
from entities.PlagueDoctor import PlagueDoctor
from entities.Vestal import Vestal
from entities.Cutthroat import Cutthroat
from entities.Fusilier import Fusilier
from entities.BoneCourtier import BoneCourtier
from entities.Corpse import Corpse
from visuals.PyGameVisuals import SimulationVisuals
import random
from collections import deque
from StatusEffects import StatusEffects
import pandas as pd
import globals

class Grid():
    def __init__(self, herogrid, enemygrid):
        self.herogrid_dict = herogrid
        self.enemygrid_dict = enemygrid
        self.round_counter = 0
        
        total_max_health = 0
        for hero in herogrid.values():
            total_max_health += hero.max_health
        self.total_hero_max_health = total_max_health

class PolicyEvaluator:
    def __init__(self):
        self.total_hero_damage = 0
        self.total_hero_heal = 0
        self.total_enemy_damage = 0
        self.total_hero_entered_death_door = 0
        self.total_hero_died = 0
        self.fight_end_score = 0
        self.actions_log = []
    
    def UpdateCharacterActionLog(self, character, target, action_name, value):
        # Format of Log array:
        target_data = []
        value_data = []
        print(f"HEREEEE ACTION NAME IS::: {action_name}")
        for _ in target:
            target_data.append((_.__class__.__name__, _.position))
        
        for _ in value:
            value_data.append(_)
        
        caster_name = character.__class__.__name__
        caster_position = character.position
        
        self.actions_log.append([caster_name, caster_position, target_data, action_name, value_data])
    
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
    
    def EvaluateRound(self):
        round_score = self.total_hero_damage + self.total_hero_heal - self.total_enemy_damage - self.total_hero_entered_death_door - self.total_hero_died
        self.fight_end_score += round_score
        self.ResetCounters()
        print(f"Round Score: {round_score}")
        return self.fight_end_score
    
    def EvaluateHealthScore(self, grid):
        total_health = 0
        if grid.herogrid_dict:
            for hero in grid.herogrid_dict.values():
                total_health += hero.health
            
        percentage_score = (total_health / grid.total_hero_max_health) * 100
        print(f"Health Score is {total_health}/{grid.total_hero_max_health}: {round(percentage_score, 2)}%")
         
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

def LoadBestStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    # Crusader has high single target damage and has a stun. (Mainly targets Front Ranks and Crusader is a Tank)
    # HighwayMan has good damage and can target multiple enemies. (Can Target Back Ranks)
    # PlagueDoctor can Deal a lot of Damage Over Time, stun, cure (heal DOTs) and attack the back ranks of enemies.
    # Vestal can Heal, Stun, and Damage single targets at the back ranks
    
    # Function format: SetPolicyWeights(self, kill = 0, stun = 0, turn = 0, rank = 0, health = 0, death = 0, heal = 0):
    
    Crusader.policies.SetPolicyWeights(kill = 10, turn = 9, stun = 8, health = 7)
    HighwayMan.policies.SetPolicyWeights(kill = 10, turn = 9, rank = 8, health = 7)
    PlagueDoctor.policies.SetPolicyWeights(death = 11, kill = 10, turn = 9, rank = 8, heal = 6, health = 5)
    Vestal.policies.SetPolicyWeights(death = 11, stun = 10, turn = 9, rank = 8, heal = 7, health = 6, kill = 5)
    
def LoadHealthFocusStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    Crusader.policies.SetPolicyWeights(stun = 10, turn = 9, health = 8, kill = 6)
    HighwayMan.policies.SetPolicyWeights(kill = 10, turn = 9, rank = 8, health = 7)
    PlagueDoctor.policies.SetPolicyWeights(death = 11, cure = 10, turn = 9, stun = 8, rank = 7, kill = 6)
    Vestal.policies.SetPolicyWeights(death = 11, heal = 10, turn = 9, kill = 7, stun = 6)

def LoadDamageFocusStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    Crusader.policies.SetPolicyWeights(kill = 10, health = 9)
    HighwayMan.policies.SetPolicyWeights(kill = 10, health = 9)
    PlagueDoctor.policies.SetPolicyWeights(kill = 10, health = 9)
    Vestal.policies.SetPolicyWeights(kill = 10, health = 9)

def CreateDataFrame(data):
    # Prepare a list of rows.
    rows = []
    for entry in data:
        caster_name = entry[0]
        caster_position = entry[1]
        targets = entry[2]
        action = entry[3]
        results = entry[4]

        # Consolidate data for multiple targets
        target_names = [target[0] for target in targets]
        target_ranks = [target[1] for target in targets]
        damages = [result[0] for result in results]
        hit_successes = [result[1] for result in results]
        total_dot_values = [result[2] for result in results]
        total_damage = sum(damage + dot for damage, dot in zip(damages, total_dot_values))
        death_blow_or_avoid = [result[3] for result in results]
        
        # Expand the data for each target
        # Note: This dataframe is used for both damaging actions and healing actions, this makes less raw data generated.
        rows.append({
            'Caster': caster_name,
            'Caster Rank': caster_position,
            'Targets': target_names,
            'Target Ranks': target_ranks,
            'Action': action,
            'Damage/Heal': damages,
            'Hit Success': hit_successes,
            'Total DOT/Cure Value': total_dot_values,
            'Total Damage/Heal': total_damage,
            'Death Blow/Prevent': death_blow_or_avoid  
        })

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Display the DataFrame
    print(df)

def main():
    
    # Heroes
    Reynald = Crusader(position = 1)
    Dismas = HighwayMan(position = 2)
    Paracelsus = PlagueDoctor(position = 3)
    Junia = Vestal(position = 4)
    
    # Reynald.health = 1
    # Dismas.health = 1
    # Paracelsus.health = 1
    # Junia.health = 1
    
    # Enemies
    Mald = Cutthroat(position = 1)
    Carlos = Cutthroat(position = 2)
    Axel = Fusilier(position = 3)
    Miguel = Fusilier(position = 4)
    
    # Mald.status_effects.append(StatusEffects("Stun", 1, 1.0, 1, "stun"))
    # Axel.status_effects.append(StatusEffects("Stun", 1, 1.0, 1, "stun"))
    # Carlos.status_effects.append(StatusEffects("Stun", 1, 1.0, 1, "stun"))
    
    #LoadBestStrategy(Reynald, Dismas, Paracelsus, Junia)
    #LoadHealthFocusStrategy(Reynald, Dismas, Paracelsus, Junia)
    LoadDamageFocusStrategy(Reynald, Dismas, Paracelsus, Junia)
    
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
    }
    
    grid = Grid(herogrid_dict, enemygrid_dict)
    policy_evaluator = PolicyEvaluator()
    simulation_visuals = SimulationVisuals(grid, policy_evaluator)
    
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
    
    # simulation_visuals.run()
    # Simulation Starts here!
    while(grid.herogrid_dict and (not all_values_of_class(grid.enemygrid_dict, Corpse) and grid.round_counter < 50)):
        
        print(f"==========Hero Team=============")
        for key, value in grid.herogrid_dict.items():
            print(f"Position Key: {key}, Value: {value.__class__.__name__}, Health: {value.health}, Stunned: {value.is_stunned}")
        print("\n\n")
        print(f"==========Enemy Team=============")
        
        for key, value in grid.enemygrid_dict.items():
            
            print(f"Position Key: {key}, Value: {value.__class__.__name__}, Health: {value.health}, Stunned: {value.is_stunned}")
        print("\n\n")
        
        if globals.show_visuals:
            simulation_visuals.DisplayCurrentFrame()
            simulation_visuals.VisualPause()
        
        turn_order = GenerateNextRound(grid.herogrid_dict, grid.enemygrid_dict, grid)
        
        # Display Turn Order
        # for i, character in enumerate(turn_order, start = 1):
        #     print(f"{i}: {character.__class__.__name__} with initiative {character.initiative}")
        
        while turn_order:
            if (not grid.herogrid_dict or (all_values_of_class(grid.enemygrid_dict, Corpse) or not grid.enemygrid_dict)):
                break
            character_to_act = turn_order.popleft()
            character_decision, character_target, target_grid = character_to_act.GetAction(grid)
            
            # Display Character Action and Target Intention
            if globals.show_visuals:
                simulation_visuals.DisplayCharacterIntention(character_to_act, character_decision, character_target.position)
                simulation_visuals.VisualPause()
            
            character_to_act.DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
            character_to_act.has_taken_action = True
            print("\n")
        
        print("TURN ORDER FINISHED")
        # Evaluate Each Round's Score
        policy_evaluator.EvaluateRound()
        
    print("====================================================")
    print(f"Simulation Ended with {grid.round_counter} rounds!")
    print(f"Total Fight Score {policy_evaluator.EvaluateRound()}!")
    print("====================================================")
    
    # Show Remaining Hp Left.
    for value in grid.herogrid_dict.values():
        print(f"{value.__class__.__name__} has {value.health} hp left!")
    
    policy_evaluator.EvaluateHealthScore(grid)
    
    # Display Action Log
    CreateDataFrame(policy_evaluator.actions_log)  

def MyTest():
    # Heroes
    Reynald = Crusader(position = 1)
    Dismas = HighwayMan(position = 2) # Change this back to 2 later!
    Paracelsus = PlagueDoctor(position = 3) # Change this back to 3 later!
    Junia = Vestal(position = 4)
    
    Junia.policies.SetPolicyWeights(death = 11, stun = 10, turn = 9, rank = 8, heal = 7, kill = 6, health = 5)
    Paracelsus.policies.SetPolicyWeights(death = 11, cure = 10, stun = 9, turn = 8, rank = 7, kill = 6, health = 5, heal = 4)
    Reynald.policies.SetPolicyWeights(stun = 10, turn = 9, health = 8, kill = 6)
    
    #Reynald.health = 3
    
    # Reynald.status_effects.append(StatusEffects("Bleed", 3, 100.0, 1, "dot"))
    Dismas.status_effects.append(StatusEffects("Bleed", 3, 100.0, 8, "dot"))
    Dismas.status_effects.append(StatusEffects("Bleed", 3, 100.0, 1, "dot"))
    Dismas.status_effects.append(StatusEffects("Bleed", 3, 100.0, 1, "dot"))
    
    Dismas.health = 3
    Paracelsus.health = 3
    Junia.health = 1

    
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
    character_decision, character_target, target_grid = grid.herogrid_dict[3].GetAction(grid)
    grid.herogrid_dict[3].DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
    print(policy_evaluator.actions_log)
    
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
    CreateDataFrame(policy_evaluator.actions_log)

main()


# TODO:
# Add Policy/Strategies for each hero (Make unique tunable parameters for each hero)
# Add Policy Evaluation (Need to Add Evaluation for Entering Death's Door and Killing Heroes or Enemies)
# Need to Add different alternative policies to test performance of policy.

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
