from src.core.game import FlappyGame
from src.rl.train import NEATTrainer
import os

def train():
    game = FlappyGame()
    
    # Setup NEAT training
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    trainer = NEATTrainer(config_path)
    
    # Train the AI
    winner = trainer.train(game, generations=100)
    
    print("Training completed!")
    print(f"Best fitness: {winner.fitness}")

if __name__ == "__main__":
    train() 