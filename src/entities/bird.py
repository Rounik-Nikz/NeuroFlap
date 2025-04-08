import pygame
from src.utils.constants import (
    BIRD_WIDTH, BIRD_HEIGHT, GRAVITY, FLAP_STRENGTH, 
    BIRD_MAX_VEL, BIRD_UPFLAP, BIRD_MIDFLAP, BIRD_DOWNFLAP
)

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load bird images
        try:
            self.images = [
                pygame.image.load(BIRD_UPFLAP).convert_alpha(),
                pygame.image.load(BIRD_MIDFLAP).convert_alpha(),
                pygame.image.load(BIRD_DOWNFLAP).convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (BIRD_WIDTH, BIRD_HEIGHT)) for img in self.images]
        except (pygame.error, FileNotFoundError):
            # Fallback to a simple rectangle if images can't be loaded
            self.images = [pygame.Surface((BIRD_WIDTH, BIRD_HEIGHT))]
            self.images[0].fill((255, 255, 0))  # Yellow color
        
        # Animation setup
        self.current_image = 0
        self.animation_timer = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect()
        
        # Position and movement
        self.rect.x = x
        self.rect.y = y
        self.velocity = 0
        
        # Game state
        self.dead = False  # Add dead attribute
        
    def flap(self):
        """Make the bird jump"""
        self.velocity = FLAP_STRENGTH
        
    def update(self):
        """Update bird's position and animation"""
        # Apply gravity
        self.velocity = min(self.velocity + GRAVITY, BIRD_MAX_VEL)
        self.rect.y += self.velocity
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 5:  # Change image every 5 frames
            self.animation_timer = 0
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            
        # Rotate bird based on velocity
        self.image = pygame.transform.rotate(
            self.images[self.current_image],
            -self.velocity * 2  # Adjust rotation based on velocity
        )