import pygame
import sys

from utils.PositionUtils import all_values_of_class
from entities.Corpse import Corpse
from actions.Attacks import Attacks

class SimulationVisuals():
    def __init__(self, grid, policy_evaluator, width = 1280, height=720):
        # Initialize Pygame
        pygame.init()

        self.screen_width = width
        self.screen_height = height
        
        # Set up the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Darkest Dungeon Fight Simulator")

        # Define colors
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        
        # Running state
        self.running = True
        
        # Grid info
        self.grid = grid
        
        # Policy Evaluator
        self.policy_evaluator = policy_evaluator
        
        self.position_offset_x = 125
        self.effect_icon_offset_x = 125
        
        # Frame Rate
        self.clock = pygame.time.Clock()
        self.fps = 10
        
        # Text Fonts
        self.font = pygame.font.Font(None, 24)
        self.intention_font = pygame.font.Font(None, 24)
        
        # Status Effect Icons:
        self.stun_icon = "visuals/status_effect_icons/Stun.png"
        self.bleed_icon = "visuals/status_effect_icons/Bleed.png"
        self.blight_icon = "visuals/status_effect_icons/Blight.png"

    def handle_events(self):
        """Handle user input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle the close button
                self.running = False
            
            # Check if the right arrow key was pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    print("Right arrow key pressed!")
                    self.screen.fill(self.BLACK)
                    pygame.display.flip()
                    # SHOW NEXT STEP
    
    def DisplayCurrentFrame(self):
        self.DisplayAllCharacters()
        self.DisplayHealthValues()
        self.DisplayCharacterStatusEffects()

        pygame.display.flip()
    
    def DisplayCharacterStatusEffects(self):
        grid = self.grid
        
        for position, hero in grid.herogrid_dict.items():
            if hero.is_bleeding:
                bleed_img = pygame.image.load(self.bleed_icon)
                self.ApplyIconImageModify(hero, hero.position, bleed_img, 445)
            if hero.is_blighted:
                blight_img = pygame.image.load(self.blight_icon)
                self.ApplyIconImageModify(hero, hero.position, blight_img, 470)
            if hero.is_stunned:
                stun_img = pygame.image.load(self.stun_icon)
                self.ApplyIconImageModify(hero, hero.position, stun_img, 495)
        
        for position, enemy in grid.enemygrid_dict.items():
            if enemy.is_bleeding:
                bleed_img = pygame.image.load(self.bleed_icon)
                self.ApplyRightIconImageModify(enemy, enemy.position, bleed_img, 645)
            if enemy.is_blighted:
                blight_img = pygame.image.load(self.blight_icon)
                self.ApplyRightIconImageModify(enemy, enemy.position, blight_img, 670)
            if enemy.is_stunned:
                stun_img = pygame.image.load(self.stun_icon)
                self.ApplyRightIconImageModify(enemy, enemy.position, stun_img, 695)
    
    def DisplayCharacterIntention(self, character, action_name, targets, is_stunned = False):
        self.screen.fill(self.BLACK)
        self.DisplayCurrentFrame()
        
        if isinstance(action_name, str):
            action_name_str = action_name
        else:
            action_name_str = action_name.name
            
        if isinstance(action_name, Attacks):
            targets = action_name.target_position if action_name.is_multi_target else targets
        
        if not character.is_player:
            text_pos = ((self.screen_width * (1/2)), (self.screen_height * (1/6)))
            text_colour = (0, 0, 255)
        else:
            text_pos = ((self.screen_width * (1/11)), (self.screen_height * (1/6)))
            text_colour = (255, 255, 0)
        
        if not is_stunned:
            intention_text = self.intention_font.render(f"{character.name}[{character.position}] used {action_name_str} on positions: {targets}", True, text_colour)
        else:
            intention_text = self.intention_font.render(f"{character.name}[{character.position}]'s turn is Skipped due to Stun or Death!", True, (255, 165, 0))
        
        self.screen.blit(intention_text, text_pos)
        pygame.display.flip()
        
    def DisplayAllCharacters(self):
        self.screen.fill(self.BLACK)
        
        # This function will draw all characters in the grid in idle state.
        grid = self.grid
        for position, hero in grid.herogrid_dict.items():
            idle_img = pygame.image.load(hero.idle_img)
            self.ApplyImageModify(hero, position, idle_img)
        
        for position, enemy in grid.enemygrid_dict.items():
            idle_img = pygame.image.load(enemy.idle_img)
            self.ApplyRightImageModify(enemy, position, idle_img)
            
        pygame.display.flip()
    
    def DisplayHealthValues(self):
        grid = self.grid
        for position, hero in grid.herogrid_dict.items():
            health_text = self.font.render(f"HP: {hero.health}/{hero.max_health}", True, (255, 255, 255))
            text_pos = ((450 - ((position - 1) * self.position_offset_x)) + hero.offset[0], 600 + hero.text_offset[1])
            self.screen.blit(health_text, text_pos)
        
        for position, enemy in grid.enemygrid_dict.items():
            health_text = self.font.render(f"HP: {enemy.health}/{enemy.max_health}", True, (255, 255, 255))
            text_pos = ((650 + ((position - 1) * self.position_offset_x)) + enemy.offset[0], 600 + enemy.text_offset[1])
            self.screen.blit(health_text, text_pos)
    
    def ApplyImageModify(self, hero, position_id, image):
        image = pygame.transform.scale(image, (hero.scale))
        self.screen.blit(image, ((400 - ((position_id - 1) * self.position_offset_x)) + hero.offset[0], 150 + hero.offset[1]))
        
    def ApplyRightImageModify(self, enemy, position_id, image):
        image = pygame.transform.scale(image, (enemy.scale))
        flipped_image = pygame.transform.flip(image, True, False)
        self.screen.blit(flipped_image, ((600 + ((position_id - 1) * self.position_offset_x)) + enemy.offset[0], 150 + enemy.offset[1]))
    
    def ApplyIconImageModify(self, hero, position_id, icon, initial_x):
        upscale_icon = pygame.transform.scale(icon, (30, 30))
        self.screen.blit(upscale_icon, ((initial_x - ((position_id - 1) * self.effect_icon_offset_x)) + hero.offset[0], hero.offset[1] + 450)) 
    
    def ApplyRightIconImageModify(self, enemy, position_id, icon, initial_x):
        upscale_icon = pygame.transform.scale(icon, (30, 30))
        self.screen.blit(upscale_icon, ((initial_x + ((position_id - 1) * self.effect_icon_offset_x)) + enemy.offset[0], enemy.offset[1] + 450))
    
    def VisualPause(self):
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Press Enter to continue
                    if event.key == pygame.K_RETURN:  
                        paused = False
                if event.type == pygame.QUIT:
                    paused = False
                    # This will end the while loop of the simulation.
                    self.grid.round_counter = 999
                    pygame.quit()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.clock.tick(self.fps)

        # Quit Pygame
        pygame.quit()
        sys.exit()

