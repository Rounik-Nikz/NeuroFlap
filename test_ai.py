import os
import sys
import time
from src.core.game import FlappyGame
from src.rl.play import play_best_network
from src.utils.constants import MODELS_DIR

def list_saved_models():
    """List all available saved models"""
    if not os.path.exists(MODELS_DIR):
        print("No models directory found.")
        return []
        
    models = [f for f in os.listdir(MODELS_DIR) if f.endswith('.pkl')]
    return sorted(models)

def print_models_menu(models):
    """Print available models menu"""
    print("\nAvailable Models:")
    print("0. Test all models")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    print(f"{len(models) + 1}. Exit")

def test_single_model(model_name):
    """Test a single model and return its score"""
    print(f"\nTesting model: {model_name}")
    sys.argv = [sys.argv[0], model_name]  # Set up argv for play_best_network
    play_best_network()
    time.sleep(1)  # Brief pause between models

def test_all_models(models):
    """Test all models in sequence"""
    results = []
    for model in models:
        print(f"\nTesting model: {model}")
        sys.argv = [sys.argv[0], model]
        play_best_network()
        time.sleep(1)  # Brief pause between models
        
        # Get the score from the last run (you might need to modify play_best_network to return the score)
        try:
            with open(os.path.join(MODELS_DIR, 'last_test_score.txt'), 'r') as f:
                score = int(f.read().strip())
                results.append((model, score))
        except:
            results.append((model, "N/A"))
    
    # Print summary
    print("\nTest Results Summary:")
    print("Model Name | Score")
    print("-" * 30)
    for model, score in results:
        print(f"{model} | {score}")

def main():
    while True:
        # Get list of saved models
        models = list_saved_models()
        
        if not models:
            print("No saved models found in models directory.")
            return
            
        # Print menu
        print_models_menu(models)
        
        # Get user choice
        try:
            choice = int(input("\nEnter your choice (0-{}): ".format(len(models) + 1)))
            
            if choice == 0:
                test_all_models(models)
            elif choice == len(models) + 1:
                print("Exiting...")
                break
            elif 1 <= choice <= len(models):
                test_single_model(models[choice - 1])
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        
        # Ask if user wants to test another model
        if input("\nTest another model? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main() 