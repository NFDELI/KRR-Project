from my_utils import all_values_of_class
from entities.Crusader import Crusader
from entities.HighwayMan import HighwayMan
from entities.PlagueDoctor import PlagueDoctor
from entities.Vestal import Vestal
from entities.Cutthroat import Cutthroat
from entities.Fusilier import Fusilier
from entities.Corpse import Corpse
from visuals.PyGameVisuals import SimulationVisuals
import random
from collections import deque
import pandas as pd
from pandasgui import show
import globals

class Grid():
    def __init__(self, herogrid, enemygrid):
        """
        STATE VARIABLES:
        1. Herogrid_dict
        2. Enemygrid_dict
        3. Round_Counter
        
        These dictionaries contain the data of each character in each team. (Data such as Health, Character_Actions, Status_Effects, etc..)
        The Key of the dictionary represents the chartacter rank/position of each character in each team.
        When one dictionary is empty, one side has won. (Either heroes or enemies.)
        Round_Counter is the number of rounds elapsed per simulation. (A round ends after every character has does an action.)
        """
        
        self.herogrid_dict = herogrid
        self.enemygrid_dict = enemygrid
        self.round_counter = 0
        
        total_max_health = 0
        for hero in herogrid.values():
            total_max_health += hero.max_health
        self.total_hero_max_health = total_max_health

class PolicyEvaluator:
    """
    OBJECTIVE FUNCTIONS:
    1. EvaluateHealthScore
    2. EvaluateRound
    
    OBJECTIVE HELPER FUNCTIONS:
    1. UpdateHeroDamage
    2. UpdateEnemyDamage
    3. UpdateHeroDied
    4. UpdateEnemyDied
    5. UpdateHeroHeal
    6. UpdateHeroEnteredDeathDoor
    """
    def __init__(self):
        self.total_hero_damage = 0
        self.total_hero_heal = 0
        self.total_enemy_damage = 0
        self.total_hero_entered_death_door = 0
        self.total_hero_died = 0
        self.total_enemy_died = 0
        self.fight_end_score = 0
        self.actions_log = []
    
    def UpdateCharacterActionLog(self, character, target, action_name, value):
        # Format of Log array:
        target_data = []
        value_data = []
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
    
    def UpdateEnemyDied(self):
        self.total_enemy_died += 20
    
    def EvaluateRound(self):
        round_score = self.total_hero_damage + self.total_hero_heal - self.total_enemy_damage + self.total_enemy_died - self.total_hero_entered_death_door - self.total_hero_died
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
        return round(percentage_score, 2)
         
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
    """
    EXOGENOUS INFORMATION:
    1. Turn Order is determined randomly.
    2. Initiative (in code: value.initiative = speed_rng + values.speed) is calculated by doing speed_rng (random integer value between 1 to 8) + character speed.
    3. Higher Initiative value determines who move first.
    """
    
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
    if globals.show_text_data_frame:
        print(df)
    return df

def RunSimulation(simulation_id):
    # Heroes
    Reynald = Crusader(position = 1)
    Dismas = HighwayMan(position = 2)
    Paracelsus = PlagueDoctor(position = 3)
    Junia = Vestal(position = 4)
    
    # Enemies
    Mald = Cutthroat(position = 1)
    Carlos = Cutthroat(position = 2)
    Axel = Fusilier(position = 3)
    Miguel = Fusilier(position = 4)
    
    # Load Hero Strategy here:
    globals.hero_strategy(Reynald, Dismas, Paracelsus, Junia)
    
    herogrid_dict = {
        Reynald.position : Reynald,
        Dismas.position : Dismas,
        Paracelsus.position : Paracelsus,
        Junia.position : Junia
    }
    
    # Make sure that cutthroat does Shank
    enemygrid_dict = {
        Mald.position : Mald,
        Axel.position : Axel,
        Carlos.position : Carlos,
        Miguel.position : Miguel,
    }
    
    grid = Grid(herogrid_dict, enemygrid_dict)
    policy_evaluator = PolicyEvaluator()
    if globals.show_visuals:
        simulation_visuals = SimulationVisuals(grid, policy_evaluator)
    
    # Assign team and enemy grids for heroes
    heroes = [Reynald, Dismas, Paracelsus, Junia]
    for hero in heroes:
        hero.team_grid = grid.herogrid_dict
        hero.enemy_grid = grid.enemygrid_dict

    # Assign team and enemy grids for enemies
    enemies = [Mald, Axel, Carlos, Miguel]
    
    for enemy in enemies:
        enemy.team_grid = grid.enemygrid_dict
        enemy.enemy_grid = grid.herogrid_dict
    
    # Simulation Starts here!
    while(grid.herogrid_dict and (not all_values_of_class(grid.enemygrid_dict, Corpse) and grid.round_counter < 50)):
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
            
            stunned_result = character_to_act.is_stunned
            
            # Display Character Action and Target Intention
            if globals.show_visuals:
                simulation_visuals.DisplayCharacterIntention(character_to_act, character_decision, character_target.position, stunned_result)
                simulation_visuals.VisualPause()
            
            if not (grid.herogrid_dict and not all_values_of_class(grid.enemygrid_dict, Corpse)):
                break
            
            character_to_act.DoAction(character_decision, target_grid[character_target.position], target_grid, policy_evaluator)
            if globals.show_visuals:
                simulation_visuals.DisplayCurrentFrame()
                
            character_to_act.has_taken_action = True
            print("\n")
        # Evaluate Each Round's Score
        policy_evaluator.EvaluateRound()
        
    total_rounds = grid.round_counter
    fight_score = policy_evaluator.EvaluateRound() 
    health_score = policy_evaluator.EvaluateHealthScore(grid)
    
    # Create the action log DataFrame
    action_log_df = CreateDataFrame(policy_evaluator.actions_log)  # Ensure this returns a DataFrame
    action_log_df["Simulation ID"] = simulation_id  # Tag action logs with the simulation ID

    # Return simulation results and action logs
    return {
        "Rounds": total_rounds,
        "Fight Score": fight_score,
        "Health Score": health_score,
        "Action Log": action_log_df,
    }
    
def BatchSimulations(num_simulations = 1):
    results = []
    all_action_logs = []

    for i in range(num_simulations):
        print(f"Running simulation {i + 1}/{num_simulations}...")
        simulation_result = RunSimulation(simulation_id=i + 1)
        
        # Append summary results
        results.append({
            "Simulation ID": i + 1,
            "Rounds": simulation_result["Rounds"],
            "Fight Score": simulation_result["Fight Score"],
            "Health Score": simulation_result["Health Score"],
        })
        
        # Append detailed action logs
        all_action_logs.append(simulation_result["Action Log"])

    # Convert results to a summary DataFrame
    results_df = pd.DataFrame(results)

    # Combine all action logs into a single DataFrame
    action_logs_df = pd.concat(all_action_logs, ignore_index = True)

    # Save results and logs to CSV (Files are overwritten at each run)
    results_df.to_csv("simulation_summary_results.csv", index = False, mode = 'w')
    action_logs_df.to_csv("simulation_action_logs.csv", index = False, mode = 'w')
    
    return results_df, action_logs_df

if __name__ == "__main__":
    # Define the number of simulations
    num_simulations = globals.number_of_simulations
    summary_df, action_logs_df = BatchSimulations(num_simulations)
    
    # Print or save results
    print("Summary Results:")
    print(summary_df.head())
    print("\nDetailed Action Logs:")
    print(action_logs_df.head())
    
    action_logs_df = pd.read_csv("simulation_action_logs.csv")
    summary_df = pd.read_csv("simulation_summary_results.csv")
    
    # Calculate average health score of all simulation
    average_health_score = summary_df["Health Score"].mean()
    average_fight_score = summary_df["Fight Score"].mean()
    average_rounds = summary_df["Rounds"].mean()
    
    summary_row = {
        "Simulation ID": "Average",
        "Rounds": average_rounds,
        "Fight Score": average_fight_score,
        "Health Score": average_health_score,
    }
    summary_df = pd.concat([summary_df, pd.DataFrame([summary_row])], ignore_index=True)
    
    show(action_logs = action_logs_df, summary = summary_df)
