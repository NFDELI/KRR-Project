# Scroll to the bottom to see simulation settings.
# All strategies are here, simply pick which one to use/load at the bottom. (variable hero_strategy)

def LoadBestStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    # Crusader has high single target damage and has a stun. (Mainly targets Front Ranks and Crusader is a Tank)
    # HighwayMan has good damage and can target multiple enemies. (Can Target Back Ranks)
    # PlagueDoctor can Deal a lot of Damage Over Time, stun, cure (heal DOTs) and attack the back ranks of enemies.
    # Vestal can Heal, Stun, and Damage single targets at the back ranks
    
    # Weights format: SetPolicyWeights(self, kill = 0, stun = 0, turn = 0, rank = 0, health = 0, death = 0, heal = 0):
    
    Crusader.policies.SetPolicyWeights(kill = 10, turn = 9, stun = 8, health = 7, damage = 6)
    HighwayMan.policies.SetPolicyWeights(kill = 10, turn = 9, rank = 8, health = 7, damage = 6)
    PlagueDoctor.policies.SetPolicyWeights(death = 11, kill = 10, cure = 9, rank = 8, damage = 7, stun = 6, health = 5)
    Vestal.policies.SetPolicyWeights(death = 11, stun = 10, turn = 9, rank = 8, heal = 7, health = 6, kill = 5)
    
def LoadHealthFocusStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    # This Strategy focuses on team survivability.
    # Characters that can stun will stun enemies to prevent upcoming damage.
    # Characters that can heal or cure, will heal often to prevent death blows and prevent DOT damage (bleed and blight)
    # Attacks that stun will still do damage, so it can kill enemies as well.
    
    Crusader.policies.SetPolicyWeights(stun = 10, turn = 9, health = 8, kill = 6)
    HighwayMan.policies.SetPolicyWeights(kill = 10, turn = 9, rank = 8, health = 7)
    PlagueDoctor.policies.SetPolicyWeights(death = 11, cure = 10, turn = 9, stun = 8, rank = 7, kill = 6)
    Vestal.policies.SetPolicyWeights(death = 11, heal = 10, turn = 9, kill = 7, stun = 6)

def LoadDamageFocusStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    # This strategy will focus on ONLY doing the highest damaging attacks to kill the enemies as fast as possible to prevent long fights.
    # Since target ranks are not considered, heroes will focus enemies on the front ranks (Due to Crusader being able to only target ranks 1 and 2)
    Crusader.policies.SetPolicyWeights(kill = 10, damage = 9, health = 8)
    HighwayMan.policies.SetPolicyWeights(kill = 10, damage = 9, health = 8)
    PlagueDoctor.policies.SetPolicyWeights(kill = 10, damage = 9, health = 8)
    Vestal.policies.SetPolicyWeights(kill = 10, damage = 9, health = 8)
    
def LoadBackRankFocusStrategy(Crusader, HighwayMan, PlagueDoctor, Vestal):
    # This strategy is similar to DamageFocusStrategy but focuses on enemies on the back ranks (such as ranks 3 and 4)
    # The rational is that enemies in the back rank usually have less health points but have higher damage output.
    Crusader.policies.SetPolicyWeights(kill = 10, rank = 9, stun = 8, damage = 7, health = 6)
    HighwayMan.policies.SetPolicyWeights(kill = 10, rank = 9, turn = 8, health = 7, damage = 6)
    PlagueDoctor.policies.SetPolicyWeights(death = 11, kill = 10, rank = 9, damage = 8, health = 7, cure = 6)
    Vestal.policies.SetPolicyWeights(death = 11, kill = 10, rank = 9, stun = 8, turn = 7, heal = 6)

# These variables are settings for the simulation.
show_visuals = True
show_text_data_frame = False
number_of_simulations = 5
hero_strategy = LoadHealthFocusStrategy

# Loading Other Strategy Example:
# hero_strategy = LoadDamageFocusStrategy

# Need to show State Variables, Exogenous, Objective, Transition, Decision Variables.