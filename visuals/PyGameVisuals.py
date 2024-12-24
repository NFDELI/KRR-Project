import pygame
import sys

from utils.PositionUtils import all_values_of_class
from entities.Corpse import Corpse

class SimulationVisuals():
    def __init__(self, grid, policy_evaluator, width = 1280, height=720):
        # Initialize Pygame
        pygame.init()

        # Set up the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pygame Basics")

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
        
        # Frame Rate
        self.clock = pygame.time.Clock()
        self.fps = 10
        
        # Text Fonts
        self.font = pygame.font.Font(None, 24)

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
        self.DrawAllCharacters()
        self.DisplayHealthValues()

        pygame.display.flip()
        
    def DrawAllCharacters(self):
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
            text_pos = ((600 + ((position - 1) * self.position_offset_x)) + enemy.offset[0], 600 + enemy.text_offset[1])
            self.screen.blit(health_text, text_pos)
    
    def ApplyImageModify(self, hero, position_id, image):
        image = pygame.transform.scale(image, (hero.scale))
        self.screen.blit(image, ((400 - ((position_id - 1) * self.position_offset_x)) + hero.offset[0], 150 + hero.offset[1]))
        
    def ApplyRightImageModify(self, enemy, position_id, image):
        image = pygame.transform.scale(image, (enemy.scale))
        flipped_image = pygame.transform.flip(image, True, False)
        self.screen.blit(flipped_image, ((600 + ((position_id - 1) * self.position_offset_x)) + enemy.offset[0], 150 + enemy.offset[1]))
    
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
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            # self.update()
            # self.draw()
            self.clock.tick(self.fps)

        # Quit Pygame
        pygame.quit()
        sys.exit()

