# visualizer.py
import neat
import pickle
from . import visualize


class NEATVisualizer:
    def __init__(self, config_path: str):
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

    def load_genome(self, genome_path: str):
        with open(genome_path, 'rb') as f:
            genome = pickle.load(f)
        return genome

    def create_network(self, genome):
        return neat.nn.FeedForwardNetwork.create(genome, self.config)

    def visualize_network(self, genome):
        visualize.draw_net(self.config, genome, filename='genome_net')
    
