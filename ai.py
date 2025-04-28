# ai.py
import torch
import torch.nn as nn

class SolitaireAI(nn.Module):
    def __init__(self):
        super(SolitaireAI, self).__init__()
        self.fc1 = nn.Linear(11, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 4)  # 4 actions : tirer, mettre fondation, déplacer colonne, envoyer fondation

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
