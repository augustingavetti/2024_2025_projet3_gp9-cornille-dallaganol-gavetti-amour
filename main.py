
import tkinter as tk
import random
import time
from trainer import Trainer
import threading
import subprocess

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COLORS = {'♠': 'black', '♣': 'black', '♥': 'red', '♦': 'red'}

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
        random.shuffle(self.deck)
        self.columns = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                card.face_up = (j == i)
                self.columns[i].append(card)
        self.stock = self.deck
        self.deck = []
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
        validate = tk.Button(self.input_window, text="Valider", command=self.start_auto_play)
        validate.pack()

    def start_auto_play(self):
        try:
            self.num_games = int(self.input_entry.get())
        except ValueError:
            self.num_games = 100

        self.input_window.destroy()
        self.open_stats_window()
        threading.Thread(target=self.run_training, daemon=True).start()

    def run_training(self):
        trainer = Trainer(self.num_games)
        stats = trainer.train()
        self.update_stats(stats)

    def open_stats_window(self):
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.title("Stats IA")
        self.stats_text = tk.Label(self.stats_window, text="Stats en cours...", font=('Arial', 12))
        self.stats_text.pack()

    def update_stats(self, stats):
        text = (
            f"Parties jouées : {stats['games_played']}\n"
            f"Score moyen : {stats['total_score'] / max(1, stats['games_played']):.2f}\n"
            f"Meilleur score : {stats['best_score']}\n"
            f"Victoires : {stats['victories']}\n"
            f"Total coups joués : {stats['total_moves']}\n"
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

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireGUI(root)
    root.mainloop()
