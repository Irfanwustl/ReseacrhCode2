"""
-*- coding: utf-8 -*-
DATE  : 2021/12/15
FUNC  : construct CNN model
AUTH  : Rong QIAO

"""

from torch import nn
import torch
import sys

class CNN(nn.Module):

    def __init__(self, conv1_out_channels, conv1_kernel_size, conv2_out_channels, conv2_kernel_size, linear1_in, linear2_in):
        super(CNN, self).__init__()

        self.conv1 = nn.Sequential(
            nn.Conv1d(in_channels=8, out_channels=conv1_out_channels, kernel_size=conv1_kernel_size, stride=1),
            nn.BatchNorm1d(conv1_out_channels),
            nn.ReLU()
        )
        self.conv2 = nn.Sequential(
            nn.Conv1d(in_channels=conv1_out_channels, out_channels=conv2_out_channels, kernel_size=conv2_kernel_size, stride=1),
            nn.BatchNorm1d(conv2_out_channels),
            nn.ReLU()
        )
        self.linear1 = nn.Sequential(
            nn.Linear(linear1_in, linear2_in),
            nn.Dropout(0.5),
            nn.ReLU()
        )
        self.linear2 = nn.Sequential(
            nn.Linear(linear2_in, 1),
            nn.Sigmoid()
        )

        
    def forward(self, x):
        
        x = self.conv1(x)
        x = self.conv2(x)
        x = x.view(-1, self.num_flat_features(x))
        x = self.linear1(x)
        output = self.linear2(x)
        
        return output

    def num_flat_features(self, x):
        
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
            
        return num_features
