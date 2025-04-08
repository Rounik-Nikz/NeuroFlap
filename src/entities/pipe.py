import pygame
import random
from src.utils.constants import (
    WINDOW_HEIGHT, PIPE_GAP, PIPE_WIDTH,
    PIPE_SPRITE, PIPE_SPEED, GREEN
)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, is_top, height=None):
        super().__init__()
        
        try:
            # Load and scale pipe image
            self.image = pygame.image.load(PIPE_SPRITE).convert_alpha()
            # Scale image to proper width while maintaining aspect ratio
            aspect_ratio = self.image.get_height() / self.image.get_width()
            pipe_height = int(PIPE_WIDTH * aspect_ratio)
            self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, pipe_height))
            
            if is_top:
                self.image = pygame.transform.flip(self.image, False, True)
        except (pygame.error, FileNotFoundError):
            # Fallback: create a rectangle if image loading fails
            self.image = pygame.Surface((PIPE_WIDTH, WINDOW_HEIGHT))
            self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        
        if height is None:
            # Default positioning if no height specified
            if is_top:
                self.rect.bottom = WINDOW_HEIGHT // 2 - PIPE_GAP // 2
            else:
                self.rect.top = WINDOW_HEIGHT // 2 + PIPE_GAP // 2
        else:
            # Use specified height and ensure pipes don't clip
            if is_top:
                # For top pipe, extend it upward from the specified height
                self.rect.bottom = height
                # Create a new surface if pipe needs to be taller
                if self.rect.height < self.rect.bottom:
                    new_height = self.rect.bottom
                    new_surface = pygame.Surface((PIPE_WIDTH, new_height), pygame.SRCALPHA)
                    # Tile the pipe texture to fill the height
                    original_height = self.image.get_height()
                    for y in range(0, new_height, original_height):
                        new_surface.blit(self.image, (0, y))
                    self.image = new_surface
            else:
                # For bottom pipe, extend it downward from the specified height
                self.rect.top = height
                # Create a new surface if pipe needs to be taller
                if self.rect.height < WINDOW_HEIGHT - self.rect.top:
                    new_height = WINDOW_HEIGHT - self.rect.top
                    new_surface = pygame.Surface((PIPE_WIDTH, new_height), pygame.SRCALPHA)
                    # Tile the pipe texture to fill the height
                    original_height = self.image.get_height()
                    for y in range(0, new_height, original_height):
                        new_surface.blit(self.image, (0, y))
                    self.image = new_surface
        
        # Update rect to match new image size
        self.rect = self.image.get_rect(x=x)
        if is_top:
            self.rect.bottom = height if height is not None else (WINDOW_HEIGHT // 2 - PIPE_GAP // 2)
        else:
            self.rect.top = height if height is not None else (WINDOW_HEIGHT // 2 + PIPE_GAP // 2)
    
    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill() 