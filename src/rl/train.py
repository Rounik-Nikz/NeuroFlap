import os
import neat
import pickle
import pygame
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple
import numpy as np
from src.entities.bird import Bird
from src.entities.pipe import Pipe
from src.utils.constants import STATE_GAME_OVER, PIPE_GAP, WINDOW_WIDTH, WINDOW_HEIGHT, FPS, MODELS_DIR
import time

class TrainingControlPanel:
    def __init__(self, trainer):
        self.trainer = trainer
        self.should_stop = False
        
        # Create control window
        self.root = tk.Tk()
        self.root.title("Training Control Panel")
        self.root.geometry("300x200")
        
        # Add controls
        self.generation_label = tk.Label(self.root, text="Generation: 0")
        self.generation_label.pack(pady=10)
        
        self.fitness_label = tk.Label(self.root, text="Best Fitness: 0")
        self.fitness_label.pack(pady=10)
        
        self.stop_button = tk.Button(self.root, text="Stop Training", command=self.stop_training)
        self.stop_button.pack(pady=20)
        
        # Update the window
        self.root.update()
    
    def stop_training(self):
        self.should_stop = True
        # Save the current state when stopping
        save_path = os.path.join(MODELS_DIR, f'stopped_at_gen_{self.trainer.population.generation}.pkl')
        with open(save_path, 'wb') as f:
            pickle.dump({
                'generation': self.trainer.population.generation,
                'population': self.trainer.population,
                'species': self.trainer.population.species,
                'best_genome': self.trainer.best_genome,
                'best_fitness': self.trainer.best_fitness,
                'timestamp': time.time()
            }, f)
        messagebox.showinfo("Training", f"Training will stop after current generation completes.\nModel saved as: {save_path}")
    
    def update(self, generation, fitness):
        self.generation_label.config(text=f"Generation: {generation}")
        self.fitness_label.config(text=f"Best Fitness: {fitness:.2f}")
        self.root.update()

class NEATTrainer:
    def __init__(self, config_path: str):
        """Initialize the NEAT trainer"""
        try:
            self.config = neat.Config(
                neat.DefaultGenome,
                neat.DefaultReproduction,
                neat.DefaultSpeciesSet,
                neat.DefaultStagnation,
                config_path
            )
        except Exception as e:
            print("Error loading NEAT config:")
            print(e)
            print("\nTrying to fix common config issues...")
            self._fix_config(config_path)
            self.config = neat.Config(
                neat.DefaultGenome,
                neat.DefaultReproduction,
                neat.DefaultSpeciesSet,
                neat.DefaultStagnation,
                config_path
            )
        
        # Add reporters for statistics
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)
        
        # Track best genome across all generations
        self.best_genome = None
        self.best_fitness = float('-inf')
        
        # Add control panel
        self.control_panel = TrainingControlPanel(self)
        
        # Create models directory if it doesn't exist
        os.makedirs(MODELS_DIR, exist_ok=True)
        self._running = True
        pygame.init()
        self.last_save_time = time.time()
        self.AUTOSAVE_INTERVAL = 60

    def _fix_config(self, config_path):
        """Fix common config file issues"""
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Fix any values with inline comments
        for section in config.sections():
            for key, value in config.items(section):
                if '#' in value:
                    clean_value = value.split('#')[0].strip()
                    config.set(section, key, clean_value)
        
        # Write fixed config back to file
        with open(config_path, 'w') as f:
            config.write(f)

    def get_game_state(self, bird: Bird, pipes: List[Pipe]) -> Tuple[float, float, float, float, float, float]:
        """Extract relevant game state features"""
        if not pipes:
            # Default state when no pipes are present
            return (
                1.0,  # Max distance when no pipe
                0.0,  # Neutral height diff
                0.0,  # Neutral height diff
                bird.velocity / 10.0,  # Normalized velocity
                bird.rect.y / WINDOW_HEIGHT,  # Normalized bird height
                0.5  # Center gap position when no pipe
            )
            
        # Find the nearest pipe
        pipes_ahead = [p for p in pipes if p.rect.right > bird.rect.x]
        if not pipes_ahead:
            return (
                1.0,
                0.0,
                0.0,
                bird.velocity / 10.0,
                bird.rect.y / WINDOW_HEIGHT,
                0.5
            )
            
        # Get the first pipe pair (top and bottom)
        pipe_pairs = [(pipes_ahead[i], pipes_ahead[i+1]) 
                     for i in range(0, len(pipes_ahead)-1, 2)]
        if not pipe_pairs:
            return (
                1.0,
                0.0,
                0.0,
                bird.velocity / 10.0,
                bird.rect.y / WINDOW_HEIGHT,
                0.5
            )
            
        # Get nearest pipe pair
        top_pipe, bottom_pipe = pipe_pairs[0]
        
        # Ensure correct order (top pipe should have smaller height)
        if top_pipe.rect.bottom > bottom_pipe.rect.top:
            top_pipe, bottom_pipe = bottom_pipe, top_pipe
        
        # Calculate normalized inputs
        horizontal_distance = (top_pipe.rect.x - bird.rect.x) / WINDOW_WIDTH
        height_diff_top = (bird.rect.y - top_pipe.rect.bottom) / WINDOW_HEIGHT
        height_diff_bottom = (bottom_pipe.rect.top - bird.rect.y) / WINDOW_HEIGHT
        bird_velocity = bird.velocity / 10.0
        bird_height = bird.rect.y / WINDOW_HEIGHT
        gap_center = (top_pipe.rect.bottom + (bottom_pipe.rect.top - top_pipe.rect.bottom)/2) / WINDOW_HEIGHT
        
        # Clip values to ensure they're in valid ranges
        horizontal_distance = max(0.0, min(1.0, horizontal_distance))
        height_diff_top = max(-1.0, min(1.0, height_diff_top))
        height_diff_bottom = max(-1.0, min(1.0, height_diff_bottom))
        bird_velocity = max(-1.0, min(1.0, bird_velocity))
        bird_height = max(0.0, min(1.0, bird_height))
        gap_center = max(0.0, min(1.0, gap_center))
        
        return (horizontal_distance, height_diff_top, height_diff_bottom, 
                bird_velocity, bird_height, gap_center)

    def eval_genomes(self, genomes, config, game_instance):
        """Evaluate all genomes simultaneously"""
        networks = []
        birds = []
        ge = []
        
        # Create a neural network and bird for each genome
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            networks.append(net)
            game_instance.add_bird()
            birds.append(game_instance.birds[-1])
            ge.append(genome)
            genome.fitness = 0
        
        clock = pygame.time.Clock()
        active_birds = birds.copy()
        
        while active_birds and self._running:
            # Handle window close event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    return
            
            # Process birds
            for i, bird in enumerate(birds):
                if bird.dead:
                    continue
                    
                state = self.get_game_state(bird, game_instance.pipes)
                output = networks[i].activate(state)
                
                if output[0] > 0.5:
                    bird.flap()
                
                ge[i].fitness += 0.1
                
                if game_instance.pipes:
                    nearest_pipe = min((p for p in game_instance.pipes if p.rect.right > bird.rect.x), 
                                     key=lambda p: p.rect.x - bird.rect.x, 
                                     default=None)
                    if nearest_pipe:
                        pipe_center = nearest_pipe.rect.bottom + PIPE_GAP/2
                        distance_to_center = abs(bird.rect.y - pipe_center)
                        ge[i].fitness += (1 - distance_to_center/WINDOW_HEIGHT) * 0.05
                
                if game_instance.score > 0:
                    ge[i].fitness += game_instance.score * 10
                    
                    # Check if score reached 50
                    if game_instance.score >= 50:
                        # Save this exceptional genome but continue training
                        save_path = os.path.join(MODELS_DIR, f'score_50_gen_{self.population.generation}.pkl')
                        with open(save_path, 'wb') as f:
                            pickle.dump({
                                'generation': self.population.generation,
                                'genome': ge[i],
                                'fitness': ge[i].fitness,
                                'score': game_instance.score,
                                'timestamp': time.time()
                            }, f)
                        print(f"\nScore 50 achieved! Model saved: {save_path}")
                        print("Continuing training...")
            
            game_instance.update()
            game_instance.draw()
            
            active_birds = [bird for bird in birds if not bird.dead]
            clock.tick(FPS)
            pygame.display.flip()

    def train(self, game_instance, generations=100):
        """Train the NEAT population"""
        try:
            def eval_genomes_wrapper(genomes, config):
                if not self._running:
                    raise KeyboardInterrupt
                    
                try:
                    game_instance.reset_game()
                    self.eval_genomes(genomes, config, game_instance)
                    
                    best_genome = max(genomes, key=lambda x: x[1].fitness)[1]
                    
                    if best_genome.fitness > self.best_fitness:
                        self.best_fitness = best_genome.fitness
                        self.best_genome = best_genome
                        print(f"\nNew best fitness: {self.best_fitness}")
                        print(f"Current Score: {game_instance.score}")
                        
                        save_path = os.path.join(MODELS_DIR, 'best_genome_current.pkl')
                        with open(save_path, 'wb') as f:
                            pickle.dump(self.best_genome, f)
                    
                    self.control_panel.update(self.population.generation, self.best_fitness)
                    
                    # Check if it's time for an autosave
                    current_time = time.time()
                    if current_time - self.last_save_time >= self.AUTOSAVE_INTERVAL:
                        save_path = os.path.join(MODELS_DIR, f'autosave_gen_{self.population.generation}.pkl')
                        with open(save_path, 'wb') as f:
                            pickle.dump({
                                'generation': self.population.generation,
                                'population': self.population,
                                'species': self.population.species,
                                'best_genome': self.best_genome,
                                'best_fitness': self.best_fitness,
                                'timestamp': current_time
                            }, f)
                        print(f"\nAutosave created: {save_path}")
                        self.last_save_time = current_time
                    
                    # Regular checkpoint saving
                    if self.population.generation % 1 == 0:
                        save_path = os.path.join(MODELS_DIR, f'checkpoint_gen_{self.population.generation}.pkl')
                        with open(save_path, 'wb') as f:
                            pickle.dump({
                                'generation': self.population.generation,
                                'population': self.population,
                                'species': self.population.species,
                                'best_genome': self.best_genome,
                                'best_fitness': self.best_fitness
                            }, f)
                        print(f"\nCheckpoint saved: {save_path}")
                    
                    if self.control_panel.should_stop:
                        self._running = False
                        raise KeyboardInterrupt
                        
                except Exception as e:
                    print(f"Error in evaluation: {e}")
                    save_path = os.path.join(MODELS_DIR, f'error_checkpoint_gen_{self.population.generation}.pkl')
                    with open(save_path, 'wb') as f:
                        pickle.dump({
                            'generation': self.population.generation,
                            'population': self.population,
                            'species': self.population.species,
                            'best_genome': self.best_genome,
                            'best_fitness': self.best_fitness,
                            'error_time': time.time()
                        }, f)
                    print(f"\nError checkpoint saved: {save_path}")
                    raise
            
            winner = self.population.run(eval_genomes_wrapper, generations)
            
            with open(os.path.join(MODELS_DIR, 'best_genome_final.pkl'), 'wb') as f:
                pickle.dump(winner, f)
                
            print("\nTraining completed!")
            print(f"Final best fitness: {winner.fitness}")
            return winner
            
        except KeyboardInterrupt:
            print("\nTraining interrupted by user")
            print(f"Saving best genome with fitness: {self.best_fitness}")
            
            save_path = os.path.join(MODELS_DIR, f'interrupted_gen_{self.population.generation}.pkl')
            with open(save_path, 'wb') as f:
                pickle.dump({
                    'generation': self.population.generation,
                    'population': self.population,
                    'species': self.population.species,
                    'best_genome': self.best_genome,
                    'best_fitness': self.best_fitness
                }, f)
            print(f"Training state saved to: {save_path}")
            
            return self.best_genome
        
        finally:
            self._running = False
            pygame.quit()
            try:
                self.control_panel.root.destroy()
            except:
                pass