import os
import pandas as pd

class StatusEffects:
    """
    STATE VARIABLES:
    1. duration: (self.duration) This variable determines how long will the status effect last. (For example, duration of 3 will last for 3 rounds)
    2. effect_Value: (self.effect_value) This variable determines the effect_value of the status effect per round. (For example, effect_value of 5 with type Bleed or Blight, means that the character
        will take 5 damage from the effect when they take their turn.)
    3. effect_name: (self.name) This variable determines which effect is being applied. (Such as Blight, Bleed, Stun, etc...)
    # Note: Same status effects will stack upon one another, except for stun.
    """
    def __init__(self, name, duration, apply_chance, effect_value = None, effect_type = None):
        self.name = name
        self.duration = duration
        self.effect_value = effect_value
        self.effect_type = effect_type
        self.apply_chance = apply_chance
    
    def RemoveEffect(self, target):

        # x could be self.name variable
        # y = target's variable to be changed
        # z = text from the spreadsheet
        # a = type of variable change (+=, -=, or reset)
        
        # Get the absolute path to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "effects_data.xlsx")

        # Read the Excel file
        effects_df = pd.read_excel(file_path, engine="openpyxl")
        effect_data = effects_df[effects_df["EffectName"] == self.name].iloc[0]
    
        # Get attribute name, reset/modifier, and operation type
        attribute_name = effect_data["Attribute"]
        operation = effect_data["Operation"]
        reset_value = effect_data["ResetValue"]
        message = effect_data["Message"]
        
        if operation  == "reset":
            setattr(target, attribute_name, getattr(target, reset_value) if reset_value else False)
            print(f"{attribute_name} has been reset into {reset_value}!")
        elif operation == "+=":
            setattr(target, attribute_name, getattr(target, attribute_name) + self.effect_value)
        elif operation == "-=":
            setattr(target, attribute_name, getattr(target, attribute_name) - self.effect_value)

        print(f"{target.__class__.__name__} {message}")
        
    # Don't be confuse with ApplyStatusEffects() in Attacks.py... This function applies the DOTs/Debuffs/Heals AFTER the character is afflicted by it.
    def ApplyEffect(self, target, policy_evaluator):
        if((self.effect_type == "dot" and self.effect_value) and not target.is_dead):
            print(f"{target.__class__.__name__} takes {self.effect_value} damage from {self.name}!")
            if self.duration > 0:
                target.TakeDamage(self.effect_value, policy_evaluator)
                print(f"\n {target.__class__.__name__} has {target.health} hp left! {self.name} has {self.duration - 1} duration left!")
            
        if(self.effect_type == "increase_stun_res"):
            target.stun_res += self.effect_value
            print(f"{target.__class__.__name__} got INCREASED stun res by {self.effect_value} !")
        
        if(self.effect_type == "mark"):
            target.is_marked = True
            print(f"{target.__class__.__name__} got MARKED for {self.duration} turns!")
