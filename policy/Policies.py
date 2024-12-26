import heapq
import random

class Policies:
    """
    STATE VARIABLES: (Attributes of characters and their current state are State Variables)
    1. self.character: The current character choosing their action.
    2. enemies: The current available enemies for each action in the grid. (for attacking)
    3. teamates: The current available teamates for each action in the grid. (for buffs or healing)
    4. enemy.health: Current enemy health.
    5. enemy.is_stunned: Characters won't stun targets who are already stunned. (Stun effects do not stack)
    6. enemy.is_corpse: Enemies who die leave corpses that take up position space and does not attack. (Less priority targets than living targets)
    """
    """
    DECISION VARIABLES:
    1. chosen_action_with_target
    2. best_action
    3. best_target
    4. target_grid: Determines which grid to apply action on, friendly or enemy grid/team.
    """
    """
    DECISION FUNCTIONS:
    1. EvaluateDamageAction(): Calculates the priority of which targets to choose based on weights set.
    2. BestHealPolicy(): Calculates the priority of healing actions based on the weights set.
    3. CalculatePriority(): Calculates the priority of the action. Higher priority based on:
                            -> can_kill
                            -> can_stun
                            -> enemy attributes (health, has_taken_action, rank/position, etc...)
                            -> average_value of heal/attack action
    4. CalculateMultiTargetPriority(): similar to CalculatePriority but for action that apply to multiple targets at the same time.
    """
    def __init__(self, character, kill_weight = 0, stun_weight = 0, turn_weight = 0, rank_weight = 0, health_weight = 0, death_door_weight = 0, heal_weight = 0, damage_weight = 0, cure_weight = 0):
        self.character = character
        self.kill_weight = kill_weight
        self.stun_weight = stun_weight
        self.turn_weight = turn_weight
        self.rank_weight = rank_weight
        self.health_weight = health_weight
        self.damage_weight = damage_weight
        
        self.death_door_weight = death_door_weight
        self.heal_weight = heal_weight
        self.cure_weight = cure_weight
    
    def SetPolicyWeights(self, kill = 0, stun = 0, turn = 0, rank = 0, health = 0, death = 0, heal = 0, damage = 0, cure = 0):
        self.kill_weight = kill 
        self.stun_weight = stun 
        self.turn_weight = turn 
        self.rank_weight = rank 
        self.health_weight = health 
        self.damage_weight = damage
        self.death_door_weight = death 
        self.heal_weight = heal
        self.cure_weight = cure 
    
    def BestActionPolicy(self, teamates, enemies):
        # Priority queue for actions.
        # Format = (Priority, target, Action)
        action_plan_priority = []
        for action_key, action_value in self.character.actions_dict.items():
            # print(f"Checking Action {action_value.name}")
            if not self.IsActionUsable(action_value):
                continue
            if action_value.is_heal:
                # Heal Action Found
                # Priority Format: heal_priority = (-death_door_priority, -effective_heal, ally.health)
                heal_evaluation = self.BestHealPolicy(action_value, teamates)
                # print(f"Priority for {action_value.name} is {heal_evaluation}")
                if heal_evaluation:
                    heapq.heappush(action_plan_priority, heal_evaluation)
            elif action_value.is_buff:
                continue
            else:
                # Damage Action Found
                # Priority Format: kill/stun_priority = (kill_priority, stun_priority, turn_priority, rank_priority, health_priority)
                damage_evaluation = self.EvaluateDamageAction(action_value, enemies)
                print(f"Priority for {action_value.name} is {damage_evaluation}")
                if damage_evaluation:
                    #print(type(damage_evaluation))
                    heapq.heappush(action_plan_priority, damage_evaluation)
        
        if action_plan_priority:
            best_priority, best_target, best_action = heapq.heappop(action_plan_priority)
            #print(f"Best Priority is {action_value.name} with {best_priority}")
            if best_action.is_buff or best_action.is_heal:
                target_grid = teamates
            else:
                target_grid = enemies
            return best_action, best_target, target_grid

        # Fallback Policy if no actions were found!
        return self.HighestDamageOutputPolicy(enemies)


    def EvaluateDamageAction(self, action_value, enemies):
        attack_plan_priority = []
        valid_targets = [
            enemy for enemy in enemies.values()
            if not enemy.is_corpse and enemy.position in action_value.target_position
        ]
        
        # No valid targets found for this action
        if not valid_targets:
            print(f"No valid targets found for action: {action_value.name}")
            return
        
        if action_value.is_multi_target:
            # Multi-target Action
            priority = self.CalculateMultiTargetPriority(action_value, valid_targets)
            if priority:
                # The action_value.target_position[0] is not an error, the game will check all elements in the target_position anyway.
                heapq.heappush(attack_plan_priority, (priority, valid_targets[0], action_value))
        else:
            for enemy in valid_targets:
                # Single-Target Action
                can_kill, can_stun, average_damage, total_damage = self.EvaluateTarget(action_value, enemy)
                priority = self.CalculatePriority(can_kill, can_stun, enemy, total_damage)
                heapq.heappush(attack_plan_priority, (priority, enemy, action_value))
        
        if attack_plan_priority:
            return heapq.heappop(attack_plan_priority)
        else:
            return None
    
    def HighestDamageOutputPolicy(self, enemies):
        # Priority queue for actions.
        # Format = (Priority, target, Action)
        print("Highest Damage Output Policy Called!")
        attack_plan_priority = []
        
        for action_key, action_value in self.character.actions_dict.items():
            if not self.IsActionUsable(action_value) or (action_value.is_heal or action_value.is_buff):
                continue
            
            # Separate living targets and corpses.
            living_targets = [enemy for enemy in enemies.values() if not enemy.is_corpse]
            corpse_targets = [enemy for enemy in enemies.values() if enemy.is_corpse]
            
            valid_targets = [
                enemy for enemy in living_targets
                if enemy.position in action_value.target_position
            ]
            
            if not valid_targets:
                valid_targets = [
                corpse for corpse in corpse_targets
                if corpse.position in action_value.target_position
                ]
            
            if not valid_targets:
                print(f"No valid targets found for action: {action_value.name}")
                continue
            
            # Calculating priority
            if action_value.is_multi_target:
                # Multi-target Action
                priority = self.CalculateMultiTargetPriority(action_value, valid_targets)
                if priority:
                    # The action_value.target_position[0] is not an error, the game will check all elements in the target_position anyway.
                    # heapq.heappush(attack_plan_priority, (priority, valid_targets[0], action_value))
                    heapq.heappush(attack_plan_priority, (priority, valid_targets[0], action_value))
            else:
                for enemy in valid_targets:
                    # Single-Target Action
                    can_kill, can_stun, average_damage, total_damage = self.EvaluateTarget(action_value, enemy)
                
                    if can_kill or can_stun:
                        priority = self.CalculatePriority(can_kill, can_stun, enemy, total_damage)
                        heapq.heappush(attack_plan_priority, (priority, enemy, action_value))
        
        if attack_plan_priority:
            best_priority, best_target, best_action = heapq.heappop(attack_plan_priority)
            return best_action, best_target, self.character.enemy_grid
        
        # Character Found no action to use, usually due to mispositioning.
        return "Nothing", 1, self.character.enemy_grid

    # Healing Policy is placed here because Vestal is the main healer. (The Plague Docter Mainly Cures DOTs)
    # This Policy is going to
    def BestHealPolicy(self, action_value, allies):        
        if not self.IsActionUsable(action_value) or not action_value.is_heal:
            return
        
        # Separate living targets and corpses.
        living_targets = [ally for ally in allies.values() if not ally.is_corpse]
        
        valid_targets = [
            ally for ally in living_targets
            if ally.position in action_value.target_position
        ]
        
        if not valid_targets:
            print(f"No valid targets found for action: {action_value.name}")
            return
        
        heal_range = action_value.apply_status_effects[0].effect_value
        heal_plan_priority = []
        
        if action_value.is_multi_target:
            # Multi-target healing
            total_death_door_priority = 0
            total_effective_heal = 0
            total_cure = 0
            total_health_priority = 0
            
            for ally in valid_targets:
                average_heal = (heal_range[0] + heal_range[1]) / 2
                effective_heal = min(average_heal, ally.max_health - ally.health)
                death_door_priority = 1 if ally.is_at_death_door else 0
                
                total_death_door_priority += death_door_priority
                total_effective_heal += effective_heal
                # Prioritize allies with lower health
                total_health_priority += -ally.health
                
            total_priorities = [
                (self.death_door_weight, -total_death_door_priority),
                (self.heal_weight, -total_effective_heal),
                (self.health_weight, total_health_priority),
                (self.cure_weight, -total_cure),
                (self.kill_weight, 0),
                (self.stun_weight, 0),
                (self.turn_weight, 0),
                (self.rank_weight, 0),
                (self.damage_weight, 0)
            ]
            
            sorted_total_priorities = sorted(total_priorities, key = lambda x: x[0], reverse = True)
            tuple_sorted_total_priorities = tuple(x[1] for x in sorted_total_priorities)
            
            heapq.heappush(heal_plan_priority, (tuple_sorted_total_priorities, valid_targets[0], action_value))

        else:
            # Single-target healing (For now, only battlefield Medicine, 'single-target' can cure)
            for ally in valid_targets:
                cure_value = 0        
                if "Cure" in action_value.apply_status_effects: #action_value.apply_status_effects[1].name == "Cure"
                    cure_value = self.CalculateCureValue(ally.status_effects)
                average_heal = (heal_range[0] + heal_range[1]) / 2
                effective_heal = min(average_heal, ally.max_health - ally.health)
                death_door_priority = 1 if ally.is_at_death_door else 0
                
                priorities = [
                    (self.death_door_weight, -death_door_priority),
                    (self.heal_weight, -effective_heal),
                    (self.health_weight, -ally.health),
                    (self.cure_weight, -cure_value),
                    (self.kill_weight, 0),
                    (self.stun_weight, 0),
                    (self.turn_weight, 0),
                    (self.rank_weight, 0),
                    (self.damage_weight, 0)
                ]
                
                sorted_priorites = sorted(priorities, key = lambda x: x[0], reverse = True)
                tuple_sorted_priorities = tuple(x[1] for x in sorted_priorites)
                
                heapq.heappush(heal_plan_priority, (tuple_sorted_priorities, ally, action_value))
                
        if heal_plan_priority:
            return heapq.heappop(heal_plan_priority)
        else:
            return None
    
    def CalculateCureValue(self, ally_status_effects):
        cure_value = 0
        for effect in ally_status_effects:
            if effect.name in ["Bleed", "Blight"]:
                cure_value += (effect.duration * effect.effect_value)
        return cure_value
    
    # Checks if character is in proper position and action is available.
    def IsActionUsable(self, action):
        if not action or (action.limited_use <= 0 and not action.is_unlimited):
            return False
        
        if(self.character.position not in action.position_req):
            return False
        
        return True

    def CalculateFirstTickDoT(self, action_value, enemy):
        # Add DoT damage if any.
        dot_damage = 0
        first_tick_damage = 0
        if action_value.apply_status_effects:
            for effect_make in action_value.apply_status_effects:
                effect = effect_make() if callable(effect_make) else effect_make
                if effect.name == "Bleed":
                    # Max ensures that enemies with 0 resistances will not result in a negative value.
                    first_tick_damage = effect.effect_value * max(0, (effect.apply_chance - enemy.bleed_res))
                elif effect.name == "Blight":
                    first_tick_damage = effect.effect_value * max(0, (effect.apply_chance - enemy.blight_res))
                dot_damage += first_tick_damage
        return dot_damage

    def CalculateMultiTargetPriority(self, action_value, valid_targets):
        total_priorities = (0, 0, 0, 0, 0, 0, 0, 0, 0) 
    
        for enemy in valid_targets:
            can_kill, can_stun, average_damage, total_damage = self.EvaluateTarget(action_value, enemy)
            priority = self.CalculatePriority(can_kill, can_stun, enemy, total_damage)
            total_priorities = tuple(a + b for a, b in zip(total_priorities, priority))
            #print(f"{total_priorities}\n")
        
        return total_priorities

    def CalculatePriority(self, can_kill, can_stun, enemy, average_value):
        priorities = [
            (self.kill_weight, -1 if can_kill else 0),
            # Using a stun action while killing the enemy at the same time makes the stun have no value!   
            (self.stun_weight, -1 if can_stun and not enemy.is_stunned else 0),
            (self.turn_weight, -1 if not enemy.has_taken_action else 0),
            # Inversion is used to ensure Lower position values will have lesser priority.
            (self.rank_weight, -enemy.position),
            # Prioritise lower health enemies.
            (self.health_weight, -enemy.health),
            (self.damage_weight, -average_value),
            (self.heal_weight, 0),
            (self.cure_weight, 0),
            (self.death_door_weight, 0)
        ]
        
        # print(f"Evaluated {enemy.__class__.__name__} at position {enemy.position}: Priority = {priorities}")
        # Sort the priorities based on the weight. First Element is the highest priority
        sorted_priorites = sorted(priorities, key = lambda x: x[0], reverse = True)
        # Making sure to return the sorted prioties as tuples.
        result = tuple(x[1] for x in sorted_priorites)
        return result

    def EvaluateTarget(self, action_value, enemy):
        dot_damage = 0
        average_damage = ((action_value.damage_range[0] + action_value.damage_range[1]) / 2) * (1 - enemy.protection)
        dot_damage = self.CalculateFirstTickDoT(action_value, enemy)
        total_damage = average_damage + dot_damage
        
        # Calculating priority
        can_kill_direct = average_damage >= enemy.health
        can_kill_with_dot = total_damage >= enemy.health and not enemy.has_taken_action
        can_kill = can_kill_direct or can_kill_with_dot
        can_stun = action_value.is_stun and not enemy.is_stunned
        return (can_kill, can_stun, average_damage, total_damage)
    
    def RandomTargetPolicy(self, every_grid):
        # Random Target Policy will choose a random attack to use on enemy.
        available_targets = list(every_grid.enemygrid_dict.keys())
        available_team_targets = list(every_grid.herogrid_dict.keys())

        available_actions = {}
        # Checking if attack is available to use.
        for action_key, action_value in self.character.actions_dict.items():
            # Check if action is still available to be used.
            if(action_value.limited_use <= 0 and action_value.is_unlimited == False):
                continue
            # Check if caster is in the correct position.
            if(self.character.position in action_value.position_req):
                # Check if there are any available enemies to be targetted using that action.
                if(action_value.is_buff or action_value.is_target_friendly):
                    # Target teamates if its a buff action (or stress heal)
                    common_targets = list(set(available_team_targets) & set(action_value.target_position))
                else:
                    # Target enemies if its an attack action
                    common_targets = list(set(available_targets) & set(action_value.target_position))
                if (common_targets):
                    # Add current action to 'new' available actions to choose with targets!
                    available_actions[action_key] = random.choice(common_targets)
        
        if(available_actions):
            chosen_action_with_target = random.choice(list(available_actions.keys()))
            if(self.character.actions_dict[chosen_action_with_target].is_buff or self.character.actions_dict[chosen_action_with_target].is_target_friendly):
                target_grid = every_grid.herogrid_dict
            else:
                target_grid = every_grid.enemygrid_dict
            result = [chosen_action_with_target, available_actions[chosen_action_with_target], target_grid]
            return result
        else:
            result = ['nothing', random.choice(list(available_targets))]