# trainer.py
import os
import torch
import torch.nn as nn
import torch.optim as optim
from solitaire_env import SolitaireEnv
from ai import SolitaireAI

MODEL_PATH = "model.pth"

class Trainer:
    def __init__(self, num_games):
        self.num_games = num_games
        self.env = SolitaireEnv()
        self.model = SolitaireAI()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        self.stats = {
            "games_played": 0,
            "total_score": 0,
            "best_score": 0,
            "victories": 0,
            "total_moves": 0
        }

        self.load_model()

    def train(self):
        for game in range(self.num_games):
            self.env.reset()
            done = False
            moves = 0

            while not done:
                state = self.env.get_state()

                with torch.no_grad():
                    action_scores = self.model(state)
                action = torch.argmax(action_scores).item()

                reward = self.env.apply_action(action)

                # Apprentissage immédiat
                prediction = self.model(state)
                target = prediction.clone()
                target[action] = reward

                loss = self.criterion(prediction, target)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                moves += 1
                if moves > 1000:  # sécurité anti-boucle
                    done = True

            score = sum(len(f) for f in self.env.foundations.values())
            self.stats["games_played"] += 1
            self.stats["total_score"] += score
            self.stats["total_moves"] += moves
            if score > self.stats["best_score"]:
                self.stats["best_score"] = score
            if score == 52:
                self.stats["victories"] += 1
                reward += 50  # bonus victoire


        self.save_model()
        return self.stats

    def save_model(self):
        torch.save(self.model.state_dict(), MODEL_PATH)
        print(f"✅ Modèle sauvegardé dans {MODEL_PATH}")

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model.load_state_dict(torch.load(MODEL_PATH))
            self.model.eval()
            print(f"📥 Modèle chargé depuis {MODEL_PATH}")
        else:
            print("❌ Aucun modèle sauvegardé trouvé.")

