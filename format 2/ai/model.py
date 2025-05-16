# ai.py
import torch
import torch.nn as nn

class SolitaireAI(nn.Module):
    def __init__(self):
        super(SolitaireAI, self).__init__()
        self.fc1 = nn.Linear(21, 64)  # ⬅️ important : 21 car 21 valeurs dans l’état
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 4)  # 4 actions (0 à 3)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
