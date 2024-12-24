import pygame
import sys

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

    def handle_events(self):
        """Handle user input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle the close button
                self.running = False

    def update(self):
        """Update game state (logic)."""
        pass  # Add game logic here in the future

    def draw(self):
        """Draw everything on the screen."""
        # Clear the screen
        self.screen.fill(self.BLACK)

        self.DrawHeroNeutralState()
        self.DrawEnemyNeutralState()
        
        # Draw a red rectangle
        # pygame.draw.rect(self.screen, self.RED, (0, 0, 200, 100))  # x, y, width, height

        # # Update the display
        pygame.display.flip()

    def DrawHeroNeutralState(self):
        hero_dict = self.grid.herogrid_dict
        Crusader_idle = pygame.image.load(hero_dict[1].idle_img)
        self.ApplyImageModify(1, Crusader_idle)
        
        Highwayman_idle = pygame.image.load(hero_dict[2].idle_img)
        self.ApplyImageModify(2, Highwayman_idle)
        
        Plague_Doctor_idle = pygame.image.load(hero_dict[3].idle_img)
        self.ApplyImageModify(3, Plague_Doctor_idle)
        
        Vestal_idle = pygame.image.load(hero_dict[4].idle_img)
        self.ApplyImageModify(4, Vestal_idle)
    
    def DrawEnemyNeutralState(self):
        enemy_dict = self.grid.enemygrid_dict
        Cutthroat_idle = pygame.image.load(enemy_dict[1].idle_img)
        self.ApplyRightImageModify(1, Cutthroat_idle)
        
        Fusilier_idle = pygame.image.load(enemy_dict[2].idle_img)
        self.ApplyRightImageModify(2, Fusilier_idle)
        
    def ApplyImageModify(self, position_id, image):
        hero_dict = self.grid.herogrid_dict
        image = pygame.transform.scale(image, (hero_dict[position_id].scale))
        self.screen.blit(image, ((400 - ((position_id - 1) * self.position_offset_x)) + hero_dict[position_id].offset[0], 150 + hero_dict[position_id].offset[1]))
        
    def ApplyRightImageModify(self, position_id, image):
        enemy_dict = self.grid.enemygrid_dict
        image = pygame.transform.scale(image, (enemy_dict[position_id].scale))
        flipped_image = pygame.transform.flip(image, True, False)
        self.screen.blit(flipped_image, ((600 + ((position_id - 1) * self.position_offset_x)) + enemy_dict[position_id].offset[0], 150 + enemy_dict[position_id].offset[1]))
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

        # Quit Pygame
        pygame.quit()
        sys.exit()

