import pygame
import random
import os
from src.entities.bird import Bird
from src.entities.pipe import Pipe
from src.utils.constants import *

class FlappyGame:
    def __init__(self, sound_enabled=True):
        pygame.init()
        if sound_enabled:
            pygame.mixer.init()
        self.sound_enabled = sound_enabled
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize sprite groups first
        self.all_sprites = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        
        # Load background
        try:
            self.background = pygame.image.load(BACKGROUND_SPRITE).convert()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self.gameover_image = pygame.image.load(GAMEOVER_SPRITE).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load sprite: {e}")
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.background.fill(SKY_BLUE)
            self.gameover_image = None
            
        # Load sounds
        try:
            self.sound_die = pygame.mixer.Sound(SOUND_DIE)
            self.sound_hit = pygame.mixer.Sound(SOUND_HIT)
            self.sound_point = pygame.mixer.Sound(SOUND_POINT)
            self.sound_wing = pygame.mixer.Sound(SOUND_WING)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load sound: {e}")
            self.sound_die = self.sound_hit = self.sound_point = self.sound_wing = None
            
        self.font = pygame.font.Font(None, 74)
        self.birds = []  # List to hold multiple birds
        
        # Initialize game state
        self.score = 0
        self.last_pipe = 0
        self.game_state = STATE_PLAYING
        
        # Add initial bird
        self.add_bird()
        
    def reset_game(self):
        """Reset the game state"""
        self.all_sprites.empty()
        self.pipes.empty()
        self.birds = []
        self.add_bird()
        self.score = 0
        self.last_pipe = 0
        self.game_state = STATE_PLAYING
        
    def add_bird(self):
        """Add a new bird to the game"""
        bird = Bird(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2)
        self.birds.append(bird)
        self.all_sprites.add(bird)
        return bird
        
    def spawn_pipes(self):
        if self.game_state != STATE_PLAYING:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe > PIPE_SPAWN_TIME:
            # Check if we need to spawn new pipes
            spawn_new = True
            for pipe in self.pipes:
                if pipe.rect.right > WINDOW_WIDTH:  # If there's already a pipe coming
                    spawn_new = False
                    break
                    
            if spawn_new:
                pipe_x = WINDOW_WIDTH + 10
                reduced_gap = PIPE_GAP - 30  # Reduce gap by 30 pixels
                
                # Define safe ranges for gap position
                top_range = (reduced_gap + 50, WINDOW_HEIGHT // 3)  # Upper third
                bottom_range = (2 * WINDOW_HEIGHT // 3, WINDOW_HEIGHT - reduced_gap - 50)  # Lower third
                
                # Choose which range to use
                if random.random() < 0.5:
                    min_height, max_height = top_range
                else:
                    min_height, max_height = bottom_range
                
                # Ensure min_height is always less than max_height
                min_height = min(min_height, max_height - reduced_gap)
                
                # Get random position within the chosen range
                gap_center = random.randint(min_height, max_height)
                
                # Create pipes with randomized gap position
                top_pipe = Pipe(pipe_x, True, gap_center - reduced_gap // 2)
                bottom_pipe = Pipe(pipe_x, False, gap_center + reduced_gap // 2)
                
                self.pipes.add(top_pipe, bottom_pipe)
                self.all_sprites.add(top_pipe, bottom_pipe)
                self.last_pipe = current_time
            
    def check_collisions(self, bird):
        """Check collisions for a specific bird"""
        if bird.rect.top <= 0 or bird.rect.bottom >= WINDOW_HEIGHT:
            return True
        return pygame.sprite.spritecollide(bird, self.pipes, False)
        
    def game_over(self):
        if self.sound_hit:
            self.sound_hit.play()
        if self.sound_die:
            self.sound_die.play()
        self.game_state = STATE_GAME_OVER
        
    def update(self):
        if self.game_state == STATE_PLAYING:
            self.all_sprites.update()
            self.spawn_pipes()
            
            # Track scored pipes to avoid double counting
            scored_pipes = set()
            
            # Update all birds
            for bird in self.birds:
                if self.check_collisions(bird):
                    bird.dead = True
                    self.all_sprites.remove(bird)  # Remove dead bird from sprites
                else:
                    # Get pipe pairs (every two pipes make a pair)
                    pipe_pairs = [(self.pipes.sprites()[i], self.pipes.sprites()[i+1]) 
                                for i in range(0, len(self.pipes.sprites()), 2) 
                                if i+1 < len(self.pipes.sprites())]
                    
                    # Check each pipe pair for scoring
                    for top_pipe, bottom_pipe in pipe_pairs:
                        # If this pair hasn't been scored and bird has passed it
                        if (bottom_pipe not in scored_pipes and 
                            bottom_pipe.rect.right < bird.rect.left and 
                            bottom_pipe.rect.right > bird.rect.left - PIPE_SPEED):
                            self.score += 1
                            scored_pipes.add(bottom_pipe)  # Mark pair as scored
                            if self.sound_point:
                                self.sound_point.play()
            
            # Remove dead birds from list
            self.birds = [bird for bird in self.birds if not bird.dead]
            
            # Game over only if all birds are dead
            if not self.birds:
                self.game_state = STATE_GAME_OVER
                
    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw sprites
        self.all_sprites.draw(self.screen)
        
        # Draw score
        score_str = str(int(self.score))
        x_offset = WINDOW_WIDTH // 2 - (len(score_str) * 30) // 2
        
        for digit in score_str:
            try:
                number_image = pygame.image.load(NUMBER_SPRITES[int(digit)]).convert_alpha()
                number_image = pygame.transform.scale(number_image, (30, 45))
                self.screen.blit(number_image, (x_offset, 50))
                x_offset += 30
            except (pygame.error, FileNotFoundError):
                score_text = self.font.render(score_str, True, WHITE)
                self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 50))
                break
        
        # Draw game over screen
        if self.game_state == STATE_GAME_OVER and self.gameover_image:
            gameover_rect = self.gameover_image.get_rect()
            gameover_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            self.screen.blit(self.gameover_image, gameover_rect)
        
        pygame.display.flip()
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == STATE_PLAYING:
                        for bird in self.birds:
                            bird.flap()
                            if self.sound_wing:
                                self.sound_wing.play()
                    elif self.game_state == STATE_GAME_OVER:
                        self.reset_game()
                    
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit() 

    def play_sound(self, sound):
        if self.sound_enabled and sound is not None:
            sound.play()
        
    def run_human_mode(self):
        """Run the game in human-playable mode"""
        self.running = True
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_state == STATE_PLAYING:
                            self.birds[0].flap()
                            if self.sound_wing:
                                self.sound_wing.play()
                        elif self.game_state == STATE_GAME_OVER:
                            self.reset_game()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the framerate
            self.clock.tick(FPS)
            
            # Check for game over
            if self.game_state == STATE_GAME_OVER:
                print(f"Game Over! Score: {self.score}")
                # Wait for space to restart or quit
                waiting = True
                while waiting and self.running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            waiting = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                self.reset_game()
                                waiting = False
                            elif event.key == pygame.K_ESCAPE:
                                self.running = False
                                waiting = False
        
        pygame.quit()
        