import torch
import random
import os
from ai.model import SolitaireAI
from game.solitaire_env import SolitaireEnv
from ai.trainer import ReplayBuffer
import pickle

SAVE_DIR = "saved"
MODEL_PATH = os.path.join(SAVE_DIR, "model.pth")
BUFFER_PATH = os.path.join(SAVE_DIR, "replay_buffer.pkl")

os.makedirs(SAVE_DIR, exist_ok=True)

def create_near_win_env():
    env = SolitaireEnv()
    env.reset()

    # Triche : placer les fondations quasi complètes
    for suit in env.foundations:
        env.foundations[suit] = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q']

    # Placer les dernières cartes sur les colonnes ou waste
    env.columns = [[] for _ in range(7)]
    env.waste = [((suit, 'K'), True) for suit in ['♠', '♥', '♦', '♣'][:random.randint(1, 3)]]
    env.stock = []
    return env

def train_on_final_moves(num_episodes=200):
    model = SolitaireAI()
    buffer = ReplayBuffer(1000)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()
    gamma = 0.95
    batch_size = 32

    # Charger modèle/buffer si dispo
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()
        print("✅ Modèle chargé")
    if os.path.exists(BUFFER_PATH):
        with open(BUFFER_PATH, "rb") as f:
            buffer.buffer = pickle.load(f)
        print("✅ Buffer chargé")

    for episode in range(num_episodes):
        env = create_near_win_env()
        state = env.get_state()
        done = False
        moves = 0

        while not done and moves < 5:
            epsilon = max(0.05, 0.9 ** episode)
            if random.random() < epsilon:
                action = random.randint(0, 3)
            else:
                with torch.no_grad():
                    action_scores = model(state)
                action = torch.argmax(action_scores).item()

            reward = env.apply_action(action)
            next_state = env.get_state()
            done = sum(len(f) for f in env.foundations.values()) == 52 or moves >= 5
            buffer.add(state, action, reward, next_state, done)
            state = next_state
            moves += 1

            if len(buffer) >= batch_size:
                states, actions, rewards, next_states, dones = buffer.sample(batch_size)
                q_values = model(states)
                next_q_values = model(next_states).detach()
                max_next_q = torch.max(next_q_values, dim=1)[0]
                targets = q_values.clone()

                for i in range(batch_size):
                    targets[i, actions[i]] = rewards[i] + gamma * max_next_q[i] * (1 - dones[i])

                loss = criterion(q_values, targets)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        print(f"🎯 Épisode {episode+1}/{num_episodes} — Moves: {moves}")

    # Sauvegardes
    torch.save(model.state_dict(), MODEL_PATH)
    with open(BUFFER_PATH, "wb") as f:
        pickle.dump(buffer.buffer, f)
    print("💾 Modèle et buffer sauvegardés.")


if __name__ == "__main__":
    train_on_final_moves(200)