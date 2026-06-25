"""
EECS 445 - Introduction to Machine Learning
Fall 2024 - Project 2
Target CNN
    Constructs a pytorch model for a convolutional neural network
    Usage: from model.target import target
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from math import sqrt
from utils import config


class Target(nn.Module):
    def __init__(self):
        super().__init__()

        ## TODO: define each layer
        # TODO: change the padding to 'same'
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2, padding=2)  # padding=2 for SAME
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 64, kernel_size=5, stride=2, padding=2)  # padding=2 for SAME
        self.conv3 = nn.Conv2d(64, 8, kernel_size=5, stride=2, padding=2)   # padding=2 for SAME

        # Calculate the output size after the last convolution layer
        self.fc_input_size = 8 * 2 * 2  # Output from conv3 after pooling
        self.fc_1 = nn.Linear(self.fc_input_size, 2)  # Fully connected layer

        self.init_weights()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def init_weights(self):
        torch.manual_seed(42)

        for conv in [self.conv1, self.conv2, self.conv3]:
            nn.init.normal_(conv.weight, mean=0.0, std=(1 / (5 * 5 * conv.in_channels))**0.5)
            nn.init.constant_(conv.bias, 0.0)  # Bias initialization

        nn.init.normal_(self.fc_1.weight, 0, (1 / self.fc_1.in_features)**0.5)
        nn.init.constant_(self.fc_1.bias, 0.0)


    def forward(self, x):
        N, C, H, W = x.shape

        x = self.conv1(x)
        x = F.relu(x)
        x = self.pool(x)

        x = self.conv2(x)
        x = F.relu(x)
        x = self.pool(x)

        x = self.conv3(x)
        x = F.relu(x)  # Apply activation after conv3

        x = x.view(N, -1)  # Flatten the tensor for the fully connected layer
        x = self.fc_1(x)  # Fully connected layer

        return x
        
