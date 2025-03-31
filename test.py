import tkinter as tk
import random

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
        self.root.title("Solitaire - Version Drag & Drop OK")

        # Paquet
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)

        # Colonnes
        self.columns = [[] for _ in range(7)]

        # Stock (pioche)
        self.stock = []

        # Interface
        self.canvas = tk.Canvas(self.root, width=900, height=600, bg="green")
        self.canvas.pack()

        self.drag_cards = []
        self.drag_offset = (0, 0)
        self.drag_col = -1

        self.deal_cards()
        self.draw()

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
            x = 50 + i * 120
            y = 50
            for card in col:
                self.draw_card(card, x, y)
                y += 30 if card.face_up else 15

        # Stock (pioche)
        if self.stock:
            self.draw_card(Card('', '', True), 50, 450, back=True)
        else:
            self.canvas.create_rectangle(50, 450, 100, 500, outline="white")

        # Si en train de drag
        if self.drag_cards:
            x, y = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx() - self.drag_offset[0], \
                   self.canvas.winfo_pointery() - self.canvas.winfo_rooty() - self.drag_offset[1]
            for i, card in enumerate(self.drag_cards):
                self.draw_card(card, x, y + i * 30)

    def draw_card(self, card, x, y, back=False):
        if not card.face_up or back:
            self.canvas.create_rectangle(x, y, x+50, y+70, fill="blue")
        else:
            self.canvas.create_rectangle(x, y, x+50, y+70, fill="white")
            self.canvas.create_text(x+25, y+35, text=str(card), fill=COLORS[card.suit], font=('Arial', 12, 'bold'))

    def on_click(self, event):
        # Clique sur les colonnes
        for i, col in enumerate(self.columns):
            x = 50 + i * 120
            y = 50
            for j in range(len(col)):
                card = col[j]
                card_x, card_y = x, y + j * (30 if card.face_up else 15)
                if card.face_up and card_x < event.x < card_x + 50 and card_y < event.y < card_y + 70:
                    self.drag_cards = col[j:]  # prend toutes les cartes à partir de celle-ci
                    self.columns[i] = col[:j]  # enlève de la colonne
                    self.drag_col = i
                    self.drag_offset = (event.x - card_x, event.y - card_y)
                    return

        # Clique sur la pioche
        if 50 < event.x < 100 and 450 < event.y < 500 and self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.columns[0].append(card)
            self.draw()

    def on_drag(self, event):
        if self.drag_cards:
            self.draw()

    def on_drop(self, event):
        if not self.drag_cards:
            return
        col_index = (event.x - 50) // 120
        if 0 <= col_index < 7:
            dest = self.columns[col_index]
            if not dest:
                if self.drag_cards[0].rank == 'K':
                    dest.extend(self.drag_cards)
                    self.drag_cards = []
            elif dest[-1].face_up and COLORS[self.drag_cards[0].suit] != COLORS[dest[-1].suit] and \
                RANKS.index(self.drag_cards[0].rank) +1 == RANKS.index(dest[-1].rank):
                dest.extend(self.drag_cards)
                self.drag_cards = []
        # Si mal déposé, retourne à sa place
        if self.drag_cards:
            self.columns[self.drag_col].extend(self.drag_cards)
            self.drag_cards = []

        # Retourner la carte du dessus si besoin
        for col in self.columns:
            if col and not col[-1].face_up:
                col[-1].face_up = True

        self.draw()

if __name__ == "__main__":
    root = tk.Tk()
    Solitaire(root)
    root.mainloop()

# Fin du code