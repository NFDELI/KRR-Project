from Actions import Actions
import random
class Buffs(Actions):
        def __init__(self, position_req, target_position, apply_status_effects, limited_use, is_unlimited = True, is_multi_target = False, name = " ", is_heal =  False):
            super().__init__(is_player_action = True, is_attack=False, position_req=position_req, 
                        target_position=target_position, limited_use=limited_use if is_unlimited else float('inf'), 
                        apply_status_effects=apply_status_effects, crit=0)
            self.position_req = position_req
            self.target_position = target_position
            self.apply_status_effects = apply_status_effects
            self.is_unlimited = is_unlimited
            self.is_multi_target = is_multi_target
            self.limited_use = limited_use
            self.is_buff = True
            self.is_heal = is_heal
            self.name = name
        
        def DoAction(self, caster, chosen_target, policy_evaluator):
            if self.is_unlimited or self.limited_use > 0:
                # Applying Buffs/Debuffs on Target
                result = self.ApplyStatusEffects(chosen_target, policy_evaluator)
                
                if not self.is_unlimited:
                    self.limited_use -= 1
                return result
            
            else:
                print("Buff cannot be used again!")

        def ApplyStatusEffects(self, chosen_target, policy_evaluator):
            actual_heal_value = 0
            actual_cure_value = 0
            for effect in self.apply_status_effects:
                # Buff RNG    
                buff_chance = effect.apply_chance - chosen_target.debuff_res
                isBuffSuccess = random.random() < buff_chance
                if(isBuffSuccess):
                    chosen_target.status_effects.append(effect)
                    if(effect.name == "Increase_Prot"):
                        chosen_target.protection += effect.effect_value
                        print(f"{chosen_target.__class__.__name__} got INCREASED protection by {effect.effect_value} !")
                    
                    if(effect.name == "Mark"):
                        chosen_target.is_marked = True
                        print(f"{chosen_target.__class__.__name__} is Marked!")
                    
                    # This cure effect is used by Plague Doctor's Battlefield Medicine
                    if(effect.name == "Cure"):
                        for effect in chosen_target.status_effects[:]:
                            if effect.name in ["Bleed", "Blight"]:
                                policy_evaluator.UpdateHeroHeal(effect.effect_value * effect.duration)
                                chosen_target.ReduceStatusEffectsDuration(effect)
                                actual_cure_value += effect.effect_value * effect.duration
                                effect.duration = 0
                    
                    if(effect.name == "Heal"):
                        old_health = chosen_target.health
                        # Healing has a range value!
                        heal_rng = random.randint(effect.effect_value[0], effect.effect_value[1])
                        chosen_target.HealDamage(heal_rng, policy_evaluator)
                        print(f"{chosen_target.__class__.__name__} healed for {heal_rng} hp! -  {chosen_target.__class__.__name__}'s health: {old_health} -> {chosen_target.health}")
                        actual_heal_value = chosen_target.max_health - chosen_target.health if chosen_target.health + heal_rng >= chosen_target.max_health else heal_rng                      
                        
                    if(effect.name == "Stress_Heal"):
                        # Stress Heal has a range value too!
                        stress_heal_rng = random.randint(effect.effect_value[0], effect.effect_value[1])
                        chosen_target.HealDamage(stress_heal_rng)
                        print(f"{chosen_target.__class__.__name__} STRESS healed for {stress_heal_rng} stress value! -  {chosen_target.__class__.__name__}'s stress: {chosen_target.stress}")
                else:
                    # Do nothing
                    pass
            
            # This return value is used for the Character Action Log.
            print(f"Actual Heal Value is: {actual_heal_value}\n")
            print(f"Actual Cure Value is: {actual_cure_value}")
            return (actual_heal_value, True, actual_cure_value, chosen_target.is_at_death_door)