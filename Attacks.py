from Actions import Actions
from StatusEffects import StatusEffects
import random 
class Attacks(Actions):
    def __init__(self, position_req, target_position, apply_status_effects, accuracy, damage_range, crit, is_unlimited = True, is_multi_target = False, stress_damage = 0, is_traget_friendly = False, is_stun = False, name = ""):
        super().__init__(is_player_action = True, is_attack=True, position_req=position_req, 
                    target_position=target_position, limited_use=0 if is_unlimited else float('inf'), 
                    apply_status_effects=apply_status_effects, crit=crit)
        self.position_req = position_req
        self.target_position = target_position
        self.apply_status_effects = apply_status_effects
        self.accuracy = accuracy
        self.damage_range = damage_range
        self.stress_damage = stress_damage
        self.crit = crit
        self.is_unlimited = is_unlimited
        self.is_multi_target = is_multi_target
        self.is_buff = False
        self.is_target_friendly = is_traget_friendly
        self.is_stun = False
        self.is_heal = False
        self.name = name
        
    def __lt__(self, other):
        # Define how to compare two Attacks objects (e.g., based on their damage range)
        return self.damage_range < other.damage_range

    def __eq__(self, other):
        return self.damage_range == other.damage_range
    
    def DoAction(self, caster, target, policy_evaluator):
        if self.is_unlimited or self.limited_use > 0:      
            # Rolling RNG to see if attack hits
            hit_rng_result = self.RngHit(target)
            if(hit_rng_result):
                # Hit is successful.
                damage_done = self.RngDamage(target)
                
                # Applying Damage to Character.
                actual_damage = int(damage_done[0] * (1 - target.protection))
                target.TakeDamage(actual_damage, policy_evaluator)
                target.TakeStressDamage(self.stress_damage) 
                print(f"{caster.__class__.__name__} [{caster.position}] Damage Rolled: {damage_done[0]} {'(Critical Hit)' if damage_done[1] else ''} - and {target.__class__.__name__} [{target.position}] has {target.health} health remaining.")
                print(f"{caster.__class__.__name__}'s actual Damage is: {actual_damage}")
                #print(f"{target.__class__.__name__} has {target.stress} Stress!")
                
                # Applying Status Efects to Character.
                self.ApplyStatusEffects(caster, target, hit_rng_result, policy_evaluator)
                
                if not self.is_unlimited:
                    self.limited_use -= 1
                
                # Log format: hit_result (bool), actualdamage, isCrit?, target being attacked.
                
            else:
                print("ATTACK MISSED!")
                
            return [hit_rng_result, actual_damage, damage_done[1], target]
            

    def RngDamage(self, target):
        
        # Check if attack will crit
        isCrit = random.random() < self.crit + target.extra_crit_taken
        if(isCrit):
            # Fixed Crit damage of 150%
            damage_roll =  int(self.damage_range[1] * 1.5)
        else:
            # Not Crit, do normal damage range check.
            damage_roll = random.randint(self.damage_range[0], self.damage_range[1])
            
        return (damage_roll, isCrit)
    
    def RngHit(self, chosen_target):
        total_hit_chance = self.accuracy - chosen_target.dodge
        isHitSuccess = random.random() < total_hit_chance
        return isHitSuccess
    
    # effect format: [name, amount, duration]
    def ApplyStatusEffects(self, caster, chosen_target, hit_result, policy_evaluator):
        #for effect in self.apply_status_effects:
        for effect_creator in self.apply_status_effects:
            effect = effect_creator() if callable(effect_creator) else effect_creator
            # Stun RNG
            if(effect.name == "Stun"):
                stun_chance = effect.apply_chance - chosen_target.stun_res
                isStunSuccess = random.random() < stun_chance
                if(isStunSuccess):
                    chosen_target.status_effects.append(effect)
                    chosen_target.is_stunned = True
                    print(f"Stun SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Stun FAILED on {chosen_target.__class__.__name__}")
            
            # Knockback Apply RNG
            if(effect.name == "Knockback"):
                knockback_chance = effect.apply_chance - chosen_target.move_res
                isMoveSuccess = random.random() < knockback_chance
                if(isMoveSuccess):
                    is_positive = effect.effect_value > 0
                    if(is_positive):
                        for i in range(0, effect.effect_value):
                            caster.Move(1)
                    else:
                        for i in range(0, effect.effect_value):
                            caster.Move(-1)                        
                    print(f"{chosen_target.__class__.__name__} knockbacked to position {chosen_target.position}!")
            
            # Bleed Apply RNG
            if(effect.name == "Bleed"):
                bleed_chance = effect.apply_chance - chosen_target.bleed_res
                isBleedSuccess = random.random() < bleed_chance
                if(isBleedSuccess):
                    chosen_target.status_effects.append(StatusEffects(effect.name, effect.duration, effect.apply_chance, effect.effect_value, effect.effect_type))
                    print(f"Bleed SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Bleed FAILED on {chosen_target.__class__.__name__}")
            
            # Blight Apply RNG
            if(effect.name == "Blight"):
                blight_chance = effect.apply_chance - chosen_target.blight_res
                isBlightSuccess = random.random() < blight_chance
                if(isBlightSuccess):
                    #chosen_target.status_effects.append(effect)
                    chosen_target.status_effects.append(StatusEffects(effect.name, effect.duration, effect.apply_chance, effect.effect_value, effect.effect_type))
                    print(f"Blight SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Blight FAILED on {chosen_target.__class__.__name__}")
            
            # Apply Slow Speed
            if(effect.name == "Reduce_Speed"):
                debuff_chance = effect.apply_chance - chosen_target.debuff_res
                isDebuffSuccess = random.random() < debuff_chance
                if(isDebuffSuccess):
                    chosen_target.status_effects.append(StatusEffects(effect.name, effect.duration, effect.apply_chance, effect.effect_value, effect.effect_type))
                    chosen_target.speed -= effect.effect_value
                    print(f"Speed Slow SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Speed Slow FAILED on {chosen_target.__class__.__name__}")
                    
            # Apply Reduce Bleed Res
            if(effect.name == "Reduce_Bleed_Res"):
                debuff_chance = effect.apply_chance - chosen_target.debuff_res
                isDebuffSuccess = random.random() < debuff_chance
                if(isDebuffSuccess):
                    chosen_target.status_effects.append(StatusEffects(effect.name, effect.duration, effect.apply_chance, effect.effect_value, effect.effect_type))
                    chosen_target.bleed_res -= effect.effect_value
                    print(f"Reduce Bleed Res SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Reduce Bleed Res FAILED on {chosen_target.__class__.__name__}")
                    
            # Apply Reduce Dodge
            if(effect.name == "Reduce_Dodge"):
                debuff_chance = effect.apply_chance - chosen_target.debuff_res
                isDebuffSuccess = random.random() < debuff_chance
                if(isDebuffSuccess):
                    chosen_target.status_effects.append(StatusEffects(effect.name, effect.duration, effect.apply_chance, effect.effect_value, effect.effect_type))
                    chosen_target.dodge -= effect.effect_value
                    print(f"Reduce Dodge SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Reduce Dodge FAILED on {chosen_target.__class__.__name__}")
            
            # Apply Take Extra Crit Chance Debuff
            if(effect.name == "Increase_Crit_Taken"):
                debuff_chance = effect.apply_chance - chosen_target.debuff_res
                isDebuffSuccess = random.random() < debuff_chance
                if(isDebuffSuccess):
                    chosen_target.status_effects.append(StatusEffects(effect.name, effect.duration, effect.apply_chance, effect.effect_value, effect.effect_type))
                    chosen_target.extra_crit_taken += effect.effect_value
                    print(f"Increase Crit Taken SUCCESS on {chosen_target.__class__.__name__}")
                else:
                    print(f"Increase Crit Taken FAILED on {chosen_target.__class__.__name__}")
            
            # Apply Self Heal
            if(effect.name == "Self_Heal"):
                if(hit_result):
                    # Vestal only heals if the Judgement attack lands!
                    caster.HealDamage(effect.effect_value, policy_evaluator)
                    print(f"{caster.__class__.__name__} healed for {effect.effect_value} hp!")
            
            # Apply Self Knockback
            if(effect.name == "Self_Knockback"):
                is_positive = effect.effect_value > 0
                
                if(is_positive):
                    for i in range(0, effect.effect_value):
                        caster.Move(1)
                else:
                    for i in range(0, effect.effect_value):
                        caster.Move(-1)                        
                print(f"{caster.__class__.__name__} knockbacked to position {caster.position}!")

            
        

