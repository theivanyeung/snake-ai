import numpy as np
import torch
import pickle
import base64
import random

import torch
import torch.nn as nn
import torch.nn.functional as F
import random

from game import SnakeGame

class GeneticNN:
    def __init__(self, input_size, hidden_size1, hidden_size2, output_size):
        super(GeneticNN, self).__init__()
        self.input_size = input_size
        self.hidden_size1 = hidden_size1
        self.hidden_size2 = hidden_size2
        self.output_size = output_size
        self.fc1 = nn.Linear(self.input_size, self.hidden_size1)
        self.fc2 = nn.Linear(self.hidden_size1, self.hidden_size2)
        self.fc3 = nn.Linear(self.hidden_size2, self.output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x

class Agent:
    def __init__(self):

        # board dimensions
        self.board_width = None
        self.board_height = None

        # Seconds of pausing between each run
        self.pause = 1
        self.fps = 30
        
    # Model handling
        
    def set_weights(self, model, weights):
        model.fc1.weight.data = weights['fc1.weight'].clone().detach()
        model.fc1.bias.data = weights['fc1.bias'].clone().detach()
        model.fc2.weight.data = weights['fc2.weight'].clone().detach()
        model.fc2.bias.data = weights['fc2.bias'].clone().detach()
        model.fc3.weight.data = weights['fc3.weight'].clone().detach()
        model.fc3.bias.data = weights['fc3.bias'].clone().detach()
        
    # SIMULATION
    
    # Converting input data to tensor

    def tuple_to_tensor(self, tuple):
        direction, snake_direction, tail_direction = tuple
        bools = direction + snake_direction + tail_direction
        return torch.tensor(bools, dtype=torch.float32)
    
    def standardize(self, tensor):
        # Split the tensor into two parts
        first_8 = tensor[:8]
        rest_24 = tensor[8:]

        # Define the max values for each neuron
        max_values = torch.tensor([self.board_height, self.board_height, self.board_width, self.board_width] + [min(self.board_height, self.board_width)] * 4)

        # Normalize the first 8 neurons by dividing by max values
        normalized_8 = first_8 / max_values

        # Combine the normalized 8 neurons with the rest of the 24 neurons using torch.cat
        output = torch.cat((normalized_8, rest_24))

        return output
    
    def choose_direction(self, output):
        max_val, max_idx = torch.max(output, dim=0)
        return {
            0: "up",
            1: "down",
            2: "right",
            3: "left",
        }.get(max_idx.item(), 'Invalid case')
    
    def handle_direction(self, game, model):
        direction = game.get_state()
        direction = self.tuple_to_tensor(direction)
        direction = model.forward(direction)
        direction = self.choose_direction(direction)
        game.handle_input(direction)
    
    def run_simulation(self):

        model = GeneticNN(32, 24, 12, 4)
        
        parameters = input("Enter encoded paramater string (pickle serialized -> base64 encoded): ")
        
        parameters = base64.b64decode(parameters)
        parameters = pickle.loads(parameters)
        self.set_weights(model, parameters)
        
        game = SnakeGame()

        while True:
            # Run the game loop
            board_width, board_height, game_over, has_pressed, score, steps = game.get_values()
            self.board_width = board_width
            self.board_height = board_height
            if not game_over:
                game.clear_direction_inputs()

                # Move the snake
                game.move_snake()
                game.set_tail_direction()

                # Check for collisions
                game.check_collisions()
                game.check_apple_collision()

                # Clear the screen
                game.clear_screen()

                # Draw the snake, directions, and the apple
                game.draw_snake()
                game.draw_distances()
                game.draw_apple()

                # Display the score
                game.display_score()

                # Update the screen
                game.update_screen()

                # Set the game clock
                game.set_clock()
                
                direction = game.get_state()
                direction = self.tuple_to_tensor(direction)
                direction = model.forward(direction)
                direction = self.choose_direction(direction)
                game.handle_input(direction)
            else:
                game.reset()
                
if __name__ == '__main__':
    agent = Agent()
    agent.run_simulation()