import os
import neat
import pygame
from src.rl.visualizer import NEATVisualizer
from src.core.game import FlappyGame
from src.rl.train import NEATTrainer
from src.utils.constants import STATE_GAME_OVER, MODELS_DIR, FPS
import sys

def play_best_network():
    # Initialize game
    game = FlappyGame()
    
    # Setup paths
    local_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(local_dir, 'neat_config.txt')
    
    # Get model filename from command line or use default
    model_file = sys.argv[1] if len(sys.argv) > 1 else 'best_genome_current.pkl'
    genome_path = os.path.join(MODELS_DIR, model_file)
    
    # Load and create network
    visualizer = NEATVisualizer(config_path)
    trainer = NEATTrainer(config_path)
    
    try:
        # Load the checkpoint
        checkpoint = visualizer.load_genome(genome_path)
        
        # Extract the genome based on file type and format
        if isinstance(checkpoint, dict):
            # For score_50 saves
            if 'genome' in checkpoint and isinstance(checkpoint['genome'], neat.genome.DefaultGenome):
                genome = checkpoint['genome']
            # For regular checkpoints
            elif 'best_genome' in checkpoint:
                genome = checkpoint['best_genome']
            # Try to find any genome in the dictionary
            else:
                for key, value in checkpoint.items():
                    if isinstance(value, neat.genome.DefaultGenome):
                        genome = value
                        break
                else:
                    print("Could not find valid genome in checkpoint")
                    return
        else:
            genome = checkpoint
            
        network = visualizer.create_network(genome)
        print("Visualizing network structure...")
        

        clock = pygame.time.Clock()
        
        # Print initial info
        print(f"\nLoaded model: {model_file}")
        if isinstance(checkpoint, dict):
            print(f"Generation: {checkpoint.get('generation', 'unknown')}")
            print(f"Original Score: {checkpoint.get('score', 'unknown')}")
            print(f"Fitness: {checkpoint.get('fitness', genome.fitness)}")
            print("\nStarting game...\n")
        
        # Play the game
        game.reset_game()
        
        while game.game_state != STATE_GAME_OVER and len(game.birds) > 0:
            # Get current game state
            state = trainer.get_game_state(game.birds[0], game.pipes)
            
            # Get network output
            output = network.activate(state)
            
            # Decide action based on network output
            if output[0] > 0.5:
                game.birds[0].flap()
            
            # Update and draw game
            game.update()
            game.draw()
            
            # Handle window close
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Cap framerate
            clock.tick(FPS)
            
            # Print current score
            if game.score > 0:
                print(f"Current Score: {game.score}", end='\r')
        
        print(f"\nFinal Score: {game.score}")
        visualizer.visualize_network(genome)
        print("Network visualization saved as 'genome_net.dot'")
        
    except FileNotFoundError:
        print(f"Model file not found: {genome_path}")
        print("Please check if the file exists in the models directory")
    except IndexError:
        print("Game over! No birds remaining.")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    play_best_network() 