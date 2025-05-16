import tkinter as tk
import random
import time
import torch
import threading
import subprocess
from ai.trainer import Trainer
from ai.model import SolitaireAI
from game.solitaire_env import RANKS, SUITS, COLORS
from game.card import Card


class SolitaireGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire avec IA Auto")
        self.canvas_width = 1000
        self.canvas_height = 700

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="darkgreen")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()

        self.start_button = tk.Button(self.info_frame, text="Lancer Auto-IA", command=self.ask_num_games)
        self.start_button.grid(row=0, column=0, padx=10)

        self.load_button = tk.Button(self.info_frame, text="Charger IA", command=self.load_model_manually)
        self.load_button.grid(row=0, column=1, padx=10)

        self.stats_button = tk.Button(self.info_frame, text="Voir les stats", command=self.launch_stats_viewer)
        self.stats_button.grid(row=0, column=2, padx=10)

        self.game_progress_label = tk.Label(self.info_frame, text="Aucune partie en cours")
        self.game_progress_label.grid(row=1, column=0, columnspan=4, pady=5)
        
        self.games_played = 0
        self.stats_window = None
        self.num_games = 100
        self.trainer = Trainer(0)

        self.root.bind('<Configure>', self.on_resize)
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        self.columns = [[] for _ in range(7)]
        self.stock = []
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.start_new_game()

    def start_new_game(self):
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)
        self.columns = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                card.face_up = (j == i)
                self.columns[i].append(card)
        self.stock = self.deck
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.draw()

    def ask_num_games(self):
        self.input_window = tk.Toplevel(self.root)
        self.input_window.title("Nombre de parties")

        label = tk.Label(self.input_window, text="Nombre de parties :")
        label.pack()

        self.input_entry = tk.Entry(self.input_window)
        self.input_entry.pack()

        mode_label = tk.Label(self.input_window, text="Mode d'entraînement :")
        mode_label.pack()

        self.mode_var = tk.StringVar(value="visuel")
        tk.Radiobutton(self.input_window, text="Visuel (lent)", variable=self.mode_var, value="visuel").pack()
        tk.Radiobutton(self.input_window, text="Rapide (sans visuel)", variable=self.mode_var, value="rapide").pack()

        validate = tk.Button(self.input_window, text="Valider", command=self.start_auto_play)
        validate.pack()

    def start_auto_play(self):
        try:
            self.num_games = int(self.input_entry.get())
        except ValueError:
            self.num_games = 100

        self.input_window.destroy()
        self.open_stats_window()

        if self.mode_var.get() == "visuel":
            threading.Thread(target=self.run_non_visual_training, daemon=True).start()
        else:
            self.run_fast_training()

    
    def run_training_thread(self):
        stats = self.trainer.train()
        self.update_stats(stats)

    def run_non_visual_training(self):
        VISUAL_SPEED = 0.00  # ➤ Vitesse d'affichage (0.00 = instantané, 0.05 = lent)
        MAX_MOVES = 300      # ➤ Nombre de coups max autorisés par partie

        total_score = 0
        total_moves = 0
        best_score = 0
        victories = 0

        self.trainer.model.eval()

        for i in range(self.num_games):
            self.game_progress_label.config(text=f"Partie {i+1} / {self.num_games}")
            self.root.update_idletasks()

            self.start_new_game()
            state = self.get_current_state()
            moves = 0

            while moves < MAX_MOVES:
                with torch.no_grad():
                    action_scores = self.trainer.model(state)
                    action = torch.argmax(action_scores).item()

                reward = self.apply_action_graphically(action)
                self.draw()
                self.root.update()
                time.sleep(VISUAL_SPEED)

                next_state = self.get_current_state()
                done = moves > MAX_MOVES

                self.trainer.replay_buffer.add(state, action, reward, next_state, done)
                state = next_state
                moves += 1

            score = sum(len(pile) for pile in self.foundations.values())
            total_score += score
            total_moves += moves
            if score > best_score:
                best_score = score
            if score == 52:
                victories += 1

            self.trainer.log_game_to_csv(i, score, moves, score == 52)


            if len(self.trainer.replay_buffer) >= self.trainer.batch_size:
                self.trainer.train_from_replay()
        
        # Sauvegardes finales
        self.trainer.save_model()
        self.trainer.save_buffer()

        # Message de fin
        from tkinter import messagebox
        messagebox.showinfo("Entraînement terminé", "✅ Modèle, replay buffer et stats sauvegardés !")



    def play_one_game_visually(self):
        self.start_new_game()
        model = SolitaireAI()
        model.load_state_dict(torch.load("model.pth"))
        model.eval()

        state = self.get_current_state()
        moves = 0
        max_moves = 200

        while moves < max_moves:
            with torch.no_grad():
                action_scores = model(state)
                action = torch.argmax(action_scores).item()

            reward = self.apply_action_graphically(action)
            self.draw()
            self.root.update()
            time.sleep(0.25)
            state = self.get_current_state()
            moves += 1

        score = sum(len(pile) for pile in self.foundations.values())
        victory = score == 52
        return score, moves, victory

    def open_stats_window(self):
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.title("Stats IA")
        self.stats_text = tk.Label(self.stats_window, text="Stats en cours...", font=('Arial', 12))
        self.stats_text.pack()

    def update_stats(self, stats):
        text = (
            f"Parties jouées : {stats['games_played']}"
            f"Score moyen : {stats['total_score'] / max(1, stats['games_played']):.2f}"
            f"Meilleur score : {stats['best_score']}"
            f"Victoires : {stats['victories']}"
            f"Total coups joués : {stats['total_moves']}"
        )
        if self.stats_window:
            self.stats_text.config(text=text)

    def on_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        total_width = 7 * 120
        start_x = (self.canvas_width - total_width) // 2

        for i, col in enumerate(self.columns):
            x = start_x + i * 120
            y = 150
            for card in col:
                self.draw_card(card, x, y)
                y += 40

        if self.stock:
            self.draw_card(Card('', '', False), start_x, 50, back=True)
        else:
            self.canvas.create_rectangle(start_x, 50, start_x + 50, 120, outline="white")

        if self.waste:
            self.draw_card(self.waste[-1], start_x + 70, 50)

        for i, suit in enumerate(SUITS):
            x = start_x + 400 + i * 120
            if self.foundations[suit]:
                self.draw_card(self.foundations[suit][-1], x, 50)
            else:
                self.canvas.create_rectangle(x, 50, x + 50, 120, outline="white")

    def draw_card(self, card, x, y, back=False):
        if back or not card.face_up:
            self.canvas.create_rectangle(x, y, x + 50, y + 70, fill="blue")
            self.canvas.create_text(x + 25, y + 35, text="◆", fill="white", font=('Arial', 16, 'bold'))
        else:
            self.canvas.create_rectangle(x, y, x + 50, y + 70, fill="white")
            color = COLORS[card.suit]
            self.canvas.create_text(x + 25, y + 35, text=f"{card.rank}{card.suit}", fill=color, font=('Arial', 14, 'bold'))

    def load_model_manually(self):
        self.trainer.load_model()
        popup = tk.Toplevel(self.root)
        popup.title("Modèle IA")
        message = tk.Label(popup, text="Modèle IA chargé avec succès !" if self.trainer.model else "Échec du chargement.")
        message.pack(pady=10)
        close_btn = tk.Button(popup, text="Fermer", command=popup.destroy)
        close_btn.pack(pady=5)

    def launch_stats_viewer(self):
        subprocess.Popen(["python", "visualiseur_stats.py"])

    def get_current_state(self):
        state = []

        for col in self.columns:
            visibles = sum(1 for c in col if c.face_up)
            total = len(col)
            state.append(visibles)
            state.append(total)

        state.append(len(self.stock))

        if self.waste:
            card = self.waste[-1]
            state.append(RANKS.index(card.rank) / 12)
            state.append(SUITS.index(card.suit) / 3)
        else:
            state += [0, 0]

        for suit in SUITS:
            state.append(len(self.foundations[suit]) / 13)

        return torch.FloatTensor(state)

    def apply_action_graphically(self, action):
        reward = -0.1

        if action == 0:
            if self.stock:
                self.waste.append(self.stock.pop())
                reward = 0.1
            elif self.waste:
                self.stock = list(reversed(self.waste))
                self.waste = []
                reward = -0.5
            else:
                reward = -1.0

        elif action == 1:
            if self.waste:
                card = self.waste[-1]
                pile = self.foundations[card.suit]
                if (not pile and card.rank == 'A') or (pile and RANKS.index(card.rank) == RANKS.index(pile[-1].rank) + 1):
                    self.foundations[card.suit].append(card)
                    self.waste.pop()
                    reward = 5
                else:
                    reward = -0.5
            else:
                reward = -1.0

        elif action == 2:
            for i, col in enumerate(self.columns):
                if col and col[-1].face_up:
                    card = col[-1]
                    for j, dest in enumerate(self.columns):
                        if i != j:
                            if not dest and card.rank == 'K':
                                self.columns[j].append(col.pop())
                                reward = 1
                                return reward
                            elif dest and dest[-1].face_up:
                                top = dest[-1]
                                if COLORS[card.suit] != COLORS[top.suit] and RANKS.index(card.rank) + 1 == RANKS.index(top.rank):
                                    self.columns[j].append(col.pop())
                                    reward = 1
                                    return reward
            reward = -0.5

        elif action == 3:
            for col in self.columns:
                if col and col[-1].face_up:
                    card = col[-1]
                    pile = self.foundations[card.suit]
                    if (not pile and card.rank == 'A') or (pile and RANKS.index(card.rank) == RANKS.index(pile[-1].rank) + 1):
                        self.foundations[card.suit].append(col.pop())
                        reward = 5
                        return reward
            reward = -0.5

        return reward
    
    def run_fast_training(self):
        self.trainer.num_games = self.num_games
        threading.Thread(target=self._fast_training_loop_with_stats, daemon=True).start()

    def _fast_training_loop_with_stats(self):
        total_score = 0
        total_moves = 0
        best_score = 0
        victories = 0

        for i in range(self.num_games):
            self.trainer.env.reset()
            done = False
            moves = 0
            state = self.trainer.env.get_state()

            while not done:
                epsilon = max(0.01, 1.0 - i / 10000)
                if random.random() < epsilon:
                    action = random.randint(0, 3)
                else:
                    with torch.no_grad():
                        action_scores = self.trainer.model(state)
                    action = torch.argmax(action_scores).item()

                reward = self.trainer.env.apply_action(action)
                next_state = self.trainer.env.get_state()
                done = moves > 500

                self.trainer.replay_buffer.add(state, action, reward, next_state, done)
                state = next_state
                moves += 1

                current_score = sum(len(f) for f in self.trainer.env.foundations.values())
                self.update_stats({
                    "games_played": i + 1,
                    "total_score": total_score + current_score,
                    "total_moves": total_moves + moves,
                    "best_score": max(best_score, current_score),
                    "victories": victories + (1 if current_score == 52 else 0)
                })

            # apprentissage
            if len(self.trainer.replay_buffer) >= self.trainer.batch_size:
                self.trainer.train_from_replay()

            score = sum(len(f) for f in self.trainer.env.foundations.values())
            total_score += score
            total_moves += moves
            if score > best_score:
                best_score = score
            if score == 52:
                victories += 1

            self.trainer.log_game_to_csv(i, score, moves, score == 52)

        self.trainer.save_model()
        self.trainer.save_buffer()

    from tkinter import messagebox
    messagebox.showinfo("Entraînement rapide terminé", "✅ Modèle, buffer et stats sauvegardés.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireGUI(root)
    root.mainloop()
