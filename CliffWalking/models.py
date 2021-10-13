"""
Models -- Neural Networks
Policy and value function with fully-connected ANNs

"""
# numpy
import numpy as np
# pytorch
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
# misc
import pdb # use with set_trace() for the debugger

# build a fully-connected neural net for the policy
class PolicyApprox(nn.Module):
    # constructor
    def __init__(self, input_size, env, hidden_size, learn_rate=0.01):
        super(PolicyApprox, self).__init__()
        # input arguments
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = 1
        self.learn_rate = learn_rate
        self.env = env
        
        # build all layers
        self.layer1 = nn.Linear(self.input_size, self.hidden_size)
        self.layer2 = nn.Linear(self.hidden_size, self.hidden_size)
        self.layer3 = nn.Linear(self.hidden_size, self.hidden_size)
        self.layer4 = nn.Linear(self.hidden_size, self.hidden_size)
        self.layer5 = nn.Linear(self.hidden_size, self.output_size)

        # initializers for weights and biases
        nn.init.normal_(self.layer1.weight, mean=0, std=1/np.sqrt(input_size)/2)
        nn.init.normal_(self.layer2.weight, mean=0, std=1/np.sqrt(input_size)/2)
        nn.init.normal_(self.layer3.weight, mean=0, std=1/np.sqrt(input_size)/2)
        nn.init.normal_(self.layer4.weight, mean=0, std=1/np.sqrt(input_size)/2)
        nn.init.normal_(self.layer5.weight, mean=0, std=1/np.sqrt(input_size)/2)
        nn.init.constant_(self.layer1.bias, 0)
        nn.init.constant_(self.layer2.bias, 0)
        nn.init.constant_(self.layer3.bias, 0)
        nn.init.constant_(self.layer4.bias, 0)
        nn.init.constant_(self.layer5.bias, 0)

        # optimizer
        self.optimizer = optim.Adam(self.parameters(), lr=self.learn_rate) # SGD or Adam
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)
    
    # forward propagation
    def forward(self, x):
        # normalize features with environment parameters
        x[...,0] /= self.env.params["T"]*(self.env.params["max_u"]/2)
        
        # mean of the Gaussian policy
        loc = F.silu(self.layer1(x))
        loc = F.silu(self.layer2(loc))
        loc = F.silu(self.layer3(loc))
        loc = F.silu(self.layer4(loc))

        # output layer attempts
        loc = T.clamp(self.layer5(loc), min=-self.env.params["max_u"], max=self.env.params["max_u"])

        # standard deviation of the Gaussian policy
        scale = self.env.params["sigma"]
        return loc, scale

# build a fully-connected neural net for the value function
class ValueApprox(nn.Module):
    # constructor
    def __init__(self, input_size, env, hidden_size, learn_rate=0.01):
        super(ValueApprox, self).__init__()
        # input arguments
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.learn_rate = learn_rate
        self.output_size = 1
        self.env = env
        
        # build all layers
        self.layer1 = nn.Linear(self.input_size, self.hidden_size)
        self.layer2 = nn.Linear(self.hidden_size, self.hidden_size)
        self.layer3 = nn.Linear(self.hidden_size, self.hidden_size)
        self.layer4 = nn.Linear(self.hidden_size, self.output_size)
        
        # optimizer
        self.optimizer = optim.Adam(self.parameters(), lr=self.learn_rate)
        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)
    
    # forward propagation
    def forward(self, x):
        # normalize features with environment parameters
        x[...,0] /= self.env.params["T"]*(self.env.params["max_u"]/2)

        # value of the value function
        x = F.silu(self.layer1(x))
        x = F.silu(self.layer2(x))
        x = F.silu(self.layer3(x))
        x = self.layer4(x)

        return x