import tkinter as tk
import random
import time
import copy

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
        self.root.title("Solitaire")
        self.canvas_width = 1000
        self.canvas_height = 700

        self.start_time = time.time()
        self.history = []

        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        self.columns = [[] for _ in range(7)]
        self.stock = []
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.drag_cards = []
        self.drag_offset = (0, 0)
        self.drag_col = -1
        self.drag_foundation = None
        self.score = 0

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="darkgreen")
        self.canvas.pack(fill=tk.BOTH, expand=True)

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
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.root.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.draw()

    def save_state(self):
        state = (copy.deepcopy(self.columns), copy.deepcopy(self.stock),
                 copy.deepcopy(self.waste), copy.deepcopy(self.foundations), self.score)
        self.history.append(state)
        if len(self.history) > 30:
            self.history.pop(0)

    def undo(self):
        if self.history:
            state = self.history.pop()
            self.columns, self.stock, self.waste, self.foundations, self.score = copy.deepcopy(state)
            self.draw()

    def new_game(self):
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
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

        self.score_label.config(text=f"Score : {self.score}")

    def draw_card(self, card, x, y, back=False):
        if back or not card.face_up:
            self.canvas.create_rectangle(x, y, x + 50, y + 70, fill="blue")
            self.canvas.create_text(x + 25, y + 35, text="◆", fill="white", font=('Arial', 16, 'bold'))
        else:
            self.canvas.create_rectangle(x, y, x + 50, y + 70, fill="white")
            color = COLORS[card.suit]
            self.canvas.create_text(x + 25, y + 35, text=f"{card.rank}{card.suit}", fill=color, font=('Arial', 14, 'bold'))

    def on_click(self, event):
        total_width = 7 * 120
        start_x = (self.canvas_width - total_width) // 2

        if start_x < event.x < start_x + 50 and 50 < event.y < 120:
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

        if start_x + 70 < event.x < start_x + 120 and 50 < event.y < 120 and self.waste:
            self.save_state()
            card = self.waste[-1]
            self.drag_cards = [card]
            self.waste.pop()
            self.drag_offset = (event.x - (start_x + 70), event.y - 50)
            self.drag_col = -2
            return

        for i, col in enumerate(self.columns):
            x = start_x + i * 120
            y = 150
            for j, card in enumerate(col):
                card_x, card_y = x, y + j * 40
                if card.face_up and card_x < event.x < card_x + 50 and card_y < event.y < card_y + 70:
                    self.save_state()
                    self.drag_cards = col[j:]
                    self.columns[i] = col[:j]
                    self.drag_col = i
                    self.drag_offset = (event.x - card_x, event.y - card_y)
                    return

        for i, suit in enumerate(SUITS):
            x = start_x + 400 + i * 120
            if x < event.x < x + 50 and 50 < event.y < 120 and self.foundations[suit]:
                self.save_state()
                card = self.foundations[suit].pop()
                self.drag_cards = [card]
                self.drag_col = -3
                self.drag_foundation = suit
                self.drag_offset = (event.x - x, event.y - 50)
                self.draw()
                return

    def on_drag(self, event):
        if self.drag_cards:
            self.draw()
            x, y = event.x - self.drag_offset[0], event.y - self.drag_offset[1]
            for i, card in enumerate(self.drag_cards):
                self.draw_card(card, x, y + i * 40)

    def on_drop(self, event):
        if not self.drag_cards:
            return

        total_width = 7 * 120
        start_x = (self.canvas_width - total_width) // 2

        col_index = (event.x - start_x) // 120
        if 0 <= col_index < 7:
            dest = self.columns[col_index]
            if not dest and self.drag_cards[0].rank == 'K':
                dest.extend(self.drag_cards)
                self.drag_cards = []
            elif dest and dest[-1].face_up and COLORS[self.drag_cards[0].suit] != COLORS[dest[-1].suit] and \
                    RANKS.index(self.drag_cards[0].rank) + 1 == RANKS.index(dest[-1].rank):
                dest.extend(self.drag_cards)
                self.drag_cards = []

        if self.drag_cards:
            if self.drag_col == -2:
                self.waste.append(self.drag_cards[0])
            elif self.drag_col == -3:
                self.foundations[self.drag_foundation].append(self.drag_cards[0])
            else:
                self.columns[self.drag_col].extend(self.drag_cards)
            self.drag_cards = []

        for col in self.columns:
            if col and not col[-1].face_up:
                col[-1].face_up = True

        self.draw()

    def try_send_to_foundation(self, card, col_index, card_index):
        suit = card.suit
        foundation = self.foundations[suit]
        if (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1):
            self.foundations[suit].append(card)
            if col_index == -1:
                self.waste.pop()
            else:
                self.columns[col_index].pop()
                if self.columns[col_index] and not self.columns[col_index][-1].face_up:
                    self.columns[col_index][-1].face_up = True
            self.score += 10
            self.draw()

    def on_double_click(self, event):
        total_width = 7 * 120
        start_x = (self.canvas_width - total_width) // 2

        for i, col in enumerate(self.columns):
            x = start_x + i * 120
            y = 150
            for j, card in enumerate(col):
                cx, cy = x, y + j * 40
                if card.face_up and cx < event.x < cx + 50 and cy < event.y < cy + 70:
                    self.try_send_to_foundation(card, i, j)
                    return

        if self.waste:
            card = self.waste[-1]
            if start_x + 70 < event.x < start_x + 120 and 50 < event.y < 120:
                self.try_send_to_foundation(card, -1, -1)

if __name__ == "__main__":
    root = tk.Tk()
    Solitaire(root)
    root.mainloop()
