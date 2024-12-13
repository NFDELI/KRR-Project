def update_positions(grid_dict):
    new_grid = {}
    for pos, character in grid_dict.items():
        new_grid[character.position] = character
        
    grid_dict.clear()
    # This if statement ensures to end the simulation if one side of the team grid are just corpses.
    grid_dict.update(new_grid)
    
def all_values_of_class(dictionary, cls):
    return all(isinstance(value, cls) for value in dictionary.values())