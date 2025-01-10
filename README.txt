1. Code Entry Point is main.py
2. Scroll down to the bottom of globals.py to change simulation settings.
    -> Change number of simulations.
    -> Change which strategy should the Hero AI use.
    -> Change whether to show visuals of simulation or not.
    -> Change whether to show dataframe in terminal-print-texts.
3. Make sure to load in requirements.txt for dependencies.
4. PyGame Controls:
    -> Press 'Enter' to step through the simulation.
    -> Quiting the PyGame window early will cause the simulation to end early with no data generated.

5. There are summary comments made in scripts such as STATE VARIABLES, EXOGENOUS INFORMATION, TRANSITION FUNCTION, etc.. 
    -> These summary comments are located at the top or near-top of some scripts.
    -> Search for """ in each script for to find them.
    -> An example of what action_dict (a dictionary containing decision variables), can be found in entities/Crusader.py. (Each Character have similar format)

6. PyGame Visual Indicators:
    -> Red Water Droplet = Charcter is bleeding
    -> Green Water Droplet = Character is blighted
    -> Yellow diamonds/sparkles = Character is stunned
    -> Yellow Bar/tick = Character has NOT taken their turn