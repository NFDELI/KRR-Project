import heapq
import random

class Policies:
    def __init__(self, character, kill_weight = 1.0, stun_weight = 0.5, turn_weight = 1.0, rank_weight = 0.2, health_weight = 0.1, death_door_weight = 1.0, heal_weight = 0.5, damage_weight = 0.4):
        self.character = character
        self.kill_weight = kill_weight
        self.stun_weight = stun_weight
        self.turn_weight = turn_weight
        self.rank_weight = rank_weight
        self.health_weight = health_weight
        self.damage_weight = damage_weight
        
        self.death_door_weight = death_door_weight
        self.heal_weight = heal_weight
        
    def BestActionPolicy(self, teamates, enemies):
        # Priority queue for actions.
        # Format = (Priority, target, Action)
        action_plan_priority = []
        for action_key, action_value in self.character.actions_dict.items():
            if not self.IsActionUsable(action_value):
                continue
            if action_value.is_heal:
                # Heal Action Found
                # Priority Format: heal_priority = (-death_door_priority, -effective_heal, ally.health)
                heal_evaluation = self.BestHealPolicy(action_value, teamates)
                if heal_evaluation:
                    heapq.heappush(action_plan_priority, heal_evaluation)
            elif action_value.is_buff:
                continue
            else:
                # Damage Action Found
                # Priority Format: kill/stun_priority = (kill_priority, stun_priority, turn_priority, rank_priority, health_priority)
                damage_evaluation = self.EvaluateDamageAction(action_value, enemies)
                if damage_evaluation:
                    heapq.heappush(action_plan_priority, damage_evaluation)
        
        if action_plan_priority:
            best_priority, best_target, best_action = heapq.heappop(action_plan_priority)
            if best_action.is_buff or best_action.is_heal:
                target_grid = teamates
            else:
                target_grid = enemies
            return best_action, best_target, target_grid

        # Fallback Policy if no actions were found!
        return self.HighestDamageOutputPolicy(enemies)


    def EvaluateDamageAction(self, action_value, enemies):
        # attack_plan_priority = []
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
                # heapq.heappush(attack_plan_priority, (priority, valid_targets[0], action_value))
                return (priority, valid_targets[0], action_value)
        else:
            for enemy in valid_targets:
                # Single-Target Action
                can_kill, can_stun, average_damage, total_damage = self.EvaluateTarget(action_value, enemy)
                priority = self.CalculatePriority(can_kill, can_stun, total_damage, enemy)
                # heapq.heappush(attack_plan_priority, (priority, enemy, action_value))
                return (priority, enemy, action_value)
    
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
                        priority = self.CalculatePriority(can_kill, can_stun, enemy)
                        heapq.heappush(attack_plan_priority, (priority, enemy, action_value))
        
        if attack_plan_priority:
            best_priority, best_target, best_action = heapq.heappop(attack_plan_priority)
            return best_action, best_target, self.character.enemy_grid
            
        return None, None

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
            
            if action_value.is_multi_target:
                # Multi-target healing
                total_death_door_priority = 0
                total_effective_heal = 0
                total_health_priority = 0
                
                for ally in valid_targets:
                    average_heal = ((heal_range[0] + heal_range[1]) / 2)
                    effective_heal = self.heal_weight * (min(average_heal, ally.max_health - ally.health))
                    death_door_priority = self.death_door_weight * (2 if ally.is_at_death_door else 0)
                    
                    total_death_door_priority += death_door_priority
                    total_effective_heal += effective_heal
                    total_health_priority += self.health_weight * ally.health

                total_priority = total_death_door_priority + total_effective_heal + total_health_priority
                return (-total_priority, valid_targets[0], action_value)

            else:
                # Single-target healing (For now, only battlefield Medicine, 'single-target' can cure)
                best_plan = None
                cure_value = 0
                if action_value.apply_status_effects[0].name == "Cure":
                    for ally in valid_targets:
                        for effect in ally.status_effects:
                            if effect in ["Bleed", "Blight"]:
                                cure_value += effect.duration * effect.value
                                
                    average_heal = ((heal_range[0] + heal_range[1]) / 2)
                    effective_heal = self.heal_weight * (min(average_heal, ally.max_health - ally.health) + cure_value)
                    death_door_priority = self.death_door_weight * (2 if ally.is_at_death_door else 0)
                    
                    priority =  -death_door_priority - effective_heal + (ally.health * self.health_weight)
                    plan = (priority, ally, action_value)
                    # Min-Heap Comparison
                    if not best_plan or plan[0] < best_plan[0]:
                        best_plan = plan
                return best_plan
        

    # Checks if character is in proper position and action is available.
    def IsActionUsable(self, action):
        if not action or (action.limited_use <= 0 and not action.is_unlimited):
            return False
        
        if(self.character.position not in action.position_req):
            return False
        
        return True

    def CalculateFirstTickDoT(self, action_value, enemy):
        #print(type(action_value.apply_status_effects))
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
        total_kill_priority = 0
        total_stun_priority = 0
        total_turn_priority = 0
        total_rank_priority = 0
        total_health_priority = 0
        
        for enemy in valid_targets:
            can_kill, can_stun, average_damage, total_damage = self.EvaluateTarget(action_value, enemy)
            
            total_kill_priority += self.kill_weight * (1 if can_kill else 0)
            total_stun_priority += self.stun_weight * (1 if can_stun and not can_kill else 0)
            total_turn_priority += self.turn_weight * (1 if not enemy.has_taken_action else 0)
            total_rank_priority += self.rank_weight * (enemy.position)
            total_health_priority += self.health_weight * (enemy.health)
        
        total_priority = total_kill_priority + total_stun_priority + total_turn_priority + total_rank_priority + total_health_priority
        return -total_priority

    def CalculatePriority(self, can_kill, can_stun, total_damage, enemy):
        kill_priority = self.kill_weight * (1 if can_kill else 0)
        # Using a stun action while killing the enemy at the same time makes the stun have no value!\
        stun_priority = 0
        if can_stun:
            if enemy.is_stunned:
                stun_priority = -1000
            elif can_kill:
                stun_priority = 0
            else:
                stun_priority = 1
        
        # stun_priority = self.stun_weight * (1 if can_stun and not enemy.is_stunned else 0)
        turn_priority = self.turn_weight * (1 if not enemy.has_taken_action else 0)
        rank_priority = self.rank_weight * (enemy.position)
        health_priority = self.health_weight * (enemy.health)
        
        
        total_priority = kill_priority + stun_priority + turn_priority + rank_priority + health_priority
        return -total_priority
        #return (-kill_priority, -stun_priority, -turn_priority, rank_priority, health_priority)

    def EvaluateTarget(self, action_value, enemy):
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