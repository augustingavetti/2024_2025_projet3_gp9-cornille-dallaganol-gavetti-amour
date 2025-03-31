import tkinter as tk
import random

# Constantes
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COLORS = {'♠': 'black', '♣': 'black', '♥': 'red', '♦': 'red'}

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

    def __str__(self):
        return f'{self.rank}{self.suit}' if self.face_up else '??'

class Solitaire:
    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire Optimisé")

        # Paquet
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)

        # Colonnes
        self.columns = [[] for _ in range(7)]

        # Fondations
        self.foundations = {suit: [] for suit in SUITS}

        # Stock
        self.stock = []

        # Interface
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="green")
        self.canvas.pack()

        self.deal_cards()
        self.draw()

        # Drag & drop
        self.drag_data = {"item": None, "col": None, "index": None}

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

    def deal_cards(self):
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                card.face_up = (j == i)
                self.columns[i].append(card)
        self.stock = self.deck
        self.deck = []

    def draw(self):
        self.canvas.delete("all")
        # Colonnes
        for i, col in enumerate(self.columns):
            x = 50 + i * 100
            y = 50
            for card in col:
                self.draw_card(card, x, y)
                y += 25 if card.face_up else 10

        # Stock
        if self.stock:
            self.draw_card(Card('','',True), 50, 400, back=True)
        else:
            self.canvas.create_rectangle(50, 400, 100, 450, outline="white")

        # Fondations
        for i, suit in enumerate(SUITS):
            x = 400 + i * 100
            y = 50
            if self.foundations[suit]:
                self.draw_card(self.foundations[suit][-1], x, y)
            else:
                self.canvas.create_rectangle(x, y, x+50, y+70, outline="white")

    def draw_card(self, card, x, y, back=False):
        if not card.face_up or back:
            self.canvas.create_rectangle(x, y, x+50, y+70, fill="blue")
        else:
            self.canvas.create_rectangle(x, y, x+50, y+70, fill="white")
            self.canvas.create_text(x+25, y+35, text=str(card), fill=COLORS[card.suit], font=('Arial', 12, 'bold'))

    def on_click(self, event):
        # Cherche la carte cliquée
        for i, col in enumerate(self.columns):
            x = 50 + i * 100
            y = 50
            for j, card in enumerate(col):
                if x < event.x < x+50 and y < event.y < y+70 and card.face_up:
                    self.drag_data = {"item": card, "col": i, "index": j}
                    return

        # Stock (pioche)
        if 50 < event.x < 100 and 400 < event.y < 450 and self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.columns[0].append(card)
            self.draw()

    def on_drag(self, event):
        pass  # Optionnel : tu peux dessiner le mouvement de la carte

    def on_drop(self, event):
        if not self.drag_data["item"]:
            return
        card = self.drag_data["item"]
        col_index = (event.x - 50) // 100
        if 0 <= col_index < 7:
            # Vérifie si on peut déposer
            dest = self.columns[col_index]
            if not dest and card.rank == 'K':
                # Roi en colonne vide
                self.columns[self.drag_data["col"]] = self.columns[self.drag_data["col"]][:self.drag_data["index"]]
                dest.append(card)
            elif dest:
                top = dest[-1]
                if COLORS[card.suit] != COLORS[top.suit] and RANKS.index(card.rank) + 1 == RANKS.index(top.rank):
                    self.columns[self.drag_data["col"]] = self.columns[self.drag_data["col"]][:self.drag_data["index"]]
                    dest.append(card)
        self.drag_data = {"item": None, "col": None, "index": None}
        self.draw()

if __name__ == "__main__":
    root = tk.Tk()
    game = Solitaire(root)
    root.mainloop()
