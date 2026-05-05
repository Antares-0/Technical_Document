import torch
import torch.nn.functional as F


class PolicyNet(torch.nn.Module):
    '''策略网络'''

    def __init__(self, state_dim, hidden_dim, action_dim):
        super(PolicyNet, self).__init__()
        # 对于倒立摆：state_dim = 4, hidden_dim = 128
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        # 对于倒立摆：action_dim = 2
        self.fc2 = torch.nn.Linear(hidden_dim, action_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.softmax(self.fc2(x), dim=1)


class ValueNet(torch.nn.Module):
    '''价值网络'''

    def __init__(self, state_dim, hidden_dim):
        super(ValueNet, self).__init__()
        # state_dim = 4
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        # 输出是一个价值，是标量
        self.fc2 = torch.nn.Linear(hidden_dim, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)
