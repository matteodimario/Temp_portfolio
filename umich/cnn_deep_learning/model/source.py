"""
EECS 445 - Introduction to Machine Learning
Fall 2024 - Project 2
Source CNN
    Constructs a pytorch model for a convolutional neural network
    Usage: from model.source import Source
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from math import sqrt
from utils import config


class Source(nn.Module):
    def __init__(self):
        super().__init__()

        ## TODO: define each layer
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2, padding=2)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 64, kernel_size=5, stride=2, padding=2)
        self.conv3 = nn.Conv2d(64, 8, kernel_size=5, stride=2, padding=2)
        self.fc1 = nn.Linear(32 , 8)

        self.init_weights()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def init_weights(self):
        torch.manual_seed(42)

        for conv in [self.conv1, self.conv2, self.conv3]:
            nn.init.normal_(conv.weight, mean=0.0, std=(1 / (5 * 5 * conv.in_channels))**0.5)
            nn.init.constant_(conv.bias, 0.0)  # Bias initialization

        nn.init.normal_(self.fc1.weight, 0, (1 / self.fc1.in_features)**0.5)
        nn.init.constant_(self.fc1.bias, 0.0)
        

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
        x = self.fc1(x)
        return x


