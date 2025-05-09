# trainer.py
import os
import csv
import random
import torch
import torch.nn as nn
import torch.optim as optim
from solitaire_env import SolitaireEnv
from ai import SolitaireAI
from collections import deque


MODEL_PATH = "model.pth"

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.stack(states),
            torch.tensor(actions),
            torch.tensor(rewards),
            torch.stack(next_states),
            torch.tensor(dones)
        )

    def __len__(self):
        return len(self.buffer)


class Trainer:
    def __init__(self, num_games):
        self.num_games = num_games
        self.env = SolitaireEnv()
        self.model = SolitaireAI()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.replay_buffer = ReplayBuffer(10000)  # taille max du buffer
        self.batch_size = 64
        self.gamma = 0.95  # facteur de discount


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
            state = self.env.get_state()

            while not done:
                epsilon = 0.1
                if random.random() < epsilon:
                    action = random.randint(0, 3)
                else:
                    with torch.no_grad():
                        action_scores = self.model(state)
                    action = torch.argmax(action_scores).item()

                reward = self.env.apply_action(action)
                next_state = self.env.get_state()
                done = moves > 1000

                self.replay_buffer.add(state, action, reward, next_state, done)
                state = next_state
                moves += 1

            # Entraînement par batch
                if len(self.replay_buffer) >= self.batch_size:
                    self.train_from_replay()

            score = sum(len(f) for f in self.env.foundations.values())
            self.stats["games_played"] += 1
            self.stats["total_score"] += score
            self.stats["total_moves"] += moves
            if score > self.stats["best_score"]:
                self.stats["best_score"] = score
            if score == 52:
                self.stats["victories"] += 1
                reward += 50

            self.log_game_to_csv(game, score, moves, score == 52)

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

    def log_game_to_csv(self, game_index, score, moves, victory):
        file_exists = os.path.isfile("stats.csv")
        with open("stats.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Partie", "Score", "Victoires", "Coups"])
            writer.writerow([game_index + 1, score, int(victory), moves])
