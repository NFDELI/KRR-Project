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