import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import copy
import os

SUITS = ['S', 'H', 'D', 'C']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COLORS = {'S': 'black', 'C': 'black', 'H': 'red', 'D': 'red'}

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

    def image_name(self):
        return f"{self.rank}{self.suit}.png" if self.face_up else "back.png"

class Solitaire:
    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire Deluxe")
        self.start_time = time.time()
        self.history = []

        self.load_images()

        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        self.columns = [[] for _ in range(7)]
        self.stock = []
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.drag_cards = []
        self.drag_offset = (0, 0)
        self.drag_col = -1
        self.score = 0

        # Interface
        self.canvas = tk.Canvas(self.root, width=1000, height=700, bg="darkgreen")
        self.canvas.pack()
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()
        self.score_label = tk.Label(self.info_frame, text="Score : 0", font=('Arial', 14))
        self.score_label.grid(row=0, column=0, padx=10)
        self.time_label = tk.Label(self.info_frame, text="Temps : 0s", font=('Arial', 14))
        self.time_label.grid(row=0, column=1, padx=10)
        self.undo_button = tk.Button(self.info_frame, text="Annuler", command=self.undo)
        self.undo_button.grid(row=0, column=2, padx=10)
        self.new_game_button = tk.Button(self.info_frame, text="Nouvelle Partie", command=self.new_game)
        self.new_game_button.grid(row=0, column=3, padx=10)

        self.new_game()
        self.update_timer()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

    def load_images(self):
        self.images = {}
        for suit in SUITS:
            for rank in RANKS:
                path = f"images/{rank}{suit}.png"
                self.images[f"{rank}{suit}"] = ImageTk.PhotoImage(Image.open(path).resize((71, 96)))
        self.images['back'] = ImageTk.PhotoImage(Image.open("images/back.png").resize((71, 96)))
        self.images['empty'] = ImageTk.PhotoImage(Image.open("images/empty.png").resize((71, 96)))

    def save_state(self):
        state = (copy.deepcopy(self.columns), copy.deepcopy(self.stock), copy.deepcopy(self.waste), copy.deepcopy(self.foundations), self.score)
        self.history.append(state)
        if len(self.history) > 20:
            self.history.pop(0)

    def undo(self):
        if self.history:
            state = self.history.pop()
            self.columns, self.stock, self.waste, self.foundations, self.score = copy.deepcopy(state)
            self.draw()

    def new_game(self):
        random.shuffle(self.deck)
        self.columns = [[] for _ in range(7)]
        self.stock = []
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.score = 0
        self.start_time = time.time()
        self.history.clear()
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                card.face_up = (j == i)
                self.columns[i].append(card)
        self.stock = self.deck
        self.deck = []
        self.save_state()
        self.draw()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.time_label.config(text=f"Temps : {elapsed}s")
        self.root.after(1000, self.update_timer)

    def draw(self):
        self.canvas.delete("all")
        for i, col in enumerate(self.columns):
            x = 50 + i * 120
            y = 150
            for card in col:
                self.canvas.create_image(x, y, image=self.images[card.image_name().replace('.png','')], anchor="nw")
                y += 30

        if self.stock:
            self.canvas.create_image(50, 50, image=self.images['back'], anchor="nw")
        else:
            self.canvas.create_image(50, 50, image=self.images['empty'], anchor="nw")

        if self.waste:
            self.canvas.create_image(120, 50, image=self.images[self.waste[-1].image_name().replace('.png','')], anchor="nw")

        for i, suit in enumerate(SUITS):
            x = 400 + i * 120
            y = 50
            if self.foundations[suit]:
                self.canvas.create_image(x, y, image=self.images[self.foundations[suit][-1].image_name().replace('.png','')], anchor="nw")
            else:
                self.canvas.create_image(x, y, image=self.images['empty'], anchor="nw")

        if self.drag_cards:
            x, y = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx() - self.drag_offset[0], \
                   self.canvas.winfo_pointery() - self.canvas.winfo_rooty() - self.drag_offset[1]
            for i, card in enumerate(self.drag_cards):
                self.canvas.create_image(x, y + i * 30, image=self.images[card.image_name().replace('.png','')], anchor="nw")

        self.score_label.config(text=f"Score : {self.score}")
        self.check_victory()

    def on_click(self, event):
        if 50 < event.x < 100 and 50 < event.y < 100:
            self.save_state()
            if self.stock:
                card = self.stock.pop()
                card.face_up = True
                self.waste.append(card)
            else:
                self.stock = self.waste[::-1]
                for card in self.stock:
                    card.face_up = False
                self.waste.clear()
            self.draw()
            return

        if 120 < event.x < 170 and 50 < event.y < 100 and self.waste:
            self.save_state()
            card = self.waste[-1]
            self.drag_cards = [card]
            self.waste.pop()
            self.drag_offset = (event.x - 120, event.y - 50)
            self.drag_col = -2
            return

        for i, col in enumerate(self.columns):
            x = 50 + i * 120
            y = 150
            for j in range(len(col)):
                card = col[j]
                card_x, card_y = x, y + j * 30
                if card.face_up and card_x < event.x < card_x + 71 and card_y < event.y < card_y + 96:
                    self.save_state()
                    self.drag_cards = col[j:]
                    self.columns[i] = col[:j]
                    self.drag_col = i
                    self.drag_offset = (event.x - card_x, event.y - card_y)
                    return

    def on_drag(self, event):
        if self.drag_cards:
            self.draw()

    def on_drop(self, event):
        if not self.drag_cards:
            return

        col_index = (event.x - 50) // 120
        if 0 <= col_index < 7:
            dest = self.columns[col_index]
            if not dest and self.drag_cards[0].rank == 'K':
                dest.extend(self.drag_cards)
                self.drag_cards = []
            elif dest and dest[-1].face_up and COLORS[self.drag_cards[0].suit] != COLORS[dest[-1].suit] and \
                    RANKS.index(self.drag_cards[0].rank) + 1 == RANKS.index(dest[-1].rank):
                dest.extend(self.drag_cards)
                if self.drag_col == -2:
                    self.score += 5
                self.drag_cards = []

        for i, suit in enumerate(SUITS):
            x = 400 + i * 120
            if x < event.x < x + 71 and 50 < event.y < 146:
                top = self.foundations[suit][-1] if self.foundations[suit] else None
                card = self.drag_cards[0]
                if ((not top and card.rank == 'A') or (top and card.suit == suit and RANKS.index(card.rank) == RANKS.index(top.rank) + 1)):
                    self.foundations[suit].append(card)
                    if self.drag_col == -2:
                        self.score += 10
                    self.drag_cards = []

        if self.drag_cards:
            if self.drag_col == -2:
                self.waste.append(self.drag_cards[0])
            else:
                self.columns[self.drag_col].extend(self.drag_cards)
            self.drag_cards = []

        for col in self.columns:
            if col and not col[-1].face_up:
                col[-1].face_up = True

        self.draw()

    def check_victory(self):
        if all(len(self.foundations[suit]) == 13 for suit in SUITS):
            self.canvas.create_text(500, 350, text="🎉 Vous avez gagné ! 🎉", font=('Arial', 24, 'bold'), fill="gold")

if __name__ == "__main__":
    root = tk.Tk()
    Solitaire(root)
    root.mainloop()
