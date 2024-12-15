import pandas as pd

class StatusEffects:
    def __init__(self, name, duration, apply_chance, effect_value = None, effect_type = None):
        self.name = name
        self.duration = duration
        self.effect_value = effect_value
        self.effect_type = effect_type
        self.apply_chance = apply_chance
    
    def AddEffect(self, target):
        if(self.name == "Stun"):
            target.is_stunned = True
            print(f"{target.__class__.__name__} is stunned for {self.duration} turn(s)!")
        elif(self.name == "Bleed"):
            target.is_bleeding = True
            print(f"{target.__class__.__name__} is bleeding with damage of {self.effect_value} for {self.duration} turn(s)!")
        elif(self.name == "Blight"):
            target.is_blighted = True
            print(f"{target.__class__.__name__} is blighted with damage of {self.effect_value} for {self.duration} turn(s)!")
    
    def RemoveEffect(self, target):

        # Python read excel: https://www.geeksforgeeks.org/reading-excel-file-using-python/
        # Try putting this into an Excel Spreadsheet to be more efficient.
        # x could be self.name variable
        # y = target's variable to be changed
        # z = text from the spreadsheet
        # a = type of variable change (+=, -=, or reset)
        
        effects_df = pd.read_excel("./effects_data.xlsx")
        
        effect_data = effects_df[effects_df["EffectName"] == self.name].iloc[0]
    
        # Get attribute name, reset/modifier, and operation type
        attribute_name = effect_data["Attribute"]
        operation = effect_data["Operation"]
        reset_value = effect_data["ResetValue"]
        message = effect_data["Message"]
        
        if operation  == "reset":
            setattr(target, attribute_name, getattr(target, reset_value) if reset_value else False)
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
