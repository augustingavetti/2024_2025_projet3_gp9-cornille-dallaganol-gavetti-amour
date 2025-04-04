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
        self.root.title("Solitaire avec IA")
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
        self.score = 0

        self.canvas = tk.Canvas(self.root, width=1000, height=700, bg="darkgreen")
        self.canvas.pack()
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()

        self.score_label = tk.Label(self.info_frame, text="Score : 0", font=('Arial', 14))
        self.score_label.grid(row=0, column=0, padx=10)
        self.time_label = tk.Label(self.info_frame, text="Temps : 0s", font=('Arial', 14))
        self.time_label.grid(row=0, column=1, padx=10)
        self.suggestion_label = tk.Label(self.info_frame, text="Suggestion :", font=('Arial', 14), fg="green")
        self.suggestion_label.grid(row=0, column=2, padx=10)
        self.undo_button = tk.Button(self.info_frame, text="Annuler", command=self.undo)
        self.undo_button.grid(row=0, column=3, padx=10)
        self.new_game_button = tk.Button(self.info_frame, text="Nouvelle Partie", command=self.new_game)
        self.new_game_button.grid(row=0, column=4, padx=10)
        self.ia_button = tk.Button(self.info_frame, text="IA auto", command=self.start_ia)
        self.ia_button.grid(row=0, column=5, padx=10)

        self.ia_running = False

        self.new_game()
        self.update_timer()
        self.update_suggestion()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

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
        self.ia_running = False
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

    def update_suggestion(self):
        move = self.find_best_move()
        if move:
            self.suggestion_label.config(text=f"Suggestion : {move}")
        else:
            self.suggestion_label.config(text="Suggestion : aucun coup utile")
        self.root.after(1000, self.update_suggestion)

    def find_best_move(self):
        for i, col in enumerate(self.columns):
            if col and col[-1].face_up:
                card = col[-1]
                foundation = self.foundations[card.suit]
                if (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1):
                    return f"envoyer {card} à la fondation"

        for i, col in enumerate(self.columns):
            for j in range(len(col)):
                card = col[j]
                if card.face_up:
                    for k, dest in enumerate(self.columns):
                        if i != k and dest:
                            top = dest[-1]
                            if top.face_up and COLORS[top.suit] != COLORS[card.suit] and RANKS.index(card.rank) + 1 == RANKS.index(top.rank):
                                return f"déplacer {card} sur {top}"

        if self.waste:
            card = self.waste[-1]
            for k, dest in enumerate(self.columns):
                if dest:
                    top = dest[-1]
                    if top.face_up and COLORS[top.suit] != COLORS[card.suit] and RANKS.index(card.rank) + 1 == RANKS.index(top.rank):
                        return f"jouer {card} sur {top}"
        return None

    def start_ia(self):
        if not self.ia_running:
            self.ia_running = True
            self.ia_auto_play()

    def ia_auto_play(self):
        if not self.ia_running:
            return
        move = self.find_best_move()
        if not move:
            self.ia_running = False
            return
        self.perform_best_move()
        self.root.after(500, self.ia_auto_play)

    def perform_best_move(self):
        for i, col in enumerate(self.columns):
            if col and col[-1].face_up:
                card = col[-1]
                foundation = self.foundations[card.suit]
                if (not foundation and card.rank == 'A') or (foundation and RANKS.index(card.rank) == RANKS.index(foundation[-1].rank) + 1):
                    self.try_send_to_foundation(card, i, len(col)-1)
                    return

        for i, col in enumerate(self.columns):
            for j in range(len(col)):
                card = col[j]
                if card.face_up:
                    for k, dest in enumerate(self.columns):
                        if i != k and dest:
                            top = dest[-1]
                            if top.face_up and COLORS[top.suit] != COLORS[card.suit] and RANKS.index(card.rank) + 1 == RANKS.index(top.rank):
                                self.save_state()
                                self.columns[k].extend(col[j:])
                                self.columns[i] = col[:j]
                                self.draw()
                                return

        if self.waste:
            card = self.waste[-1]
            for k, dest in enumerate(self.columns):
                if dest:
                    top = dest[-1]
                    if top.face_up and COLORS[top.suit] != COLORS[card.suit] and RANKS.index(card.rank) + 1 == RANKS.index(top.rank):
                        self.save_state()
                        self.columns[k].append(card)
                        self.waste.pop()
                        self.draw()
                        return

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

    def draw(self):
        self.canvas.delete("all")
        for i, col in enumerate(self.columns):
            x = 50 + i * 120
            y = 150
            for card in col:
                self.draw_card(card, x, y)
                y += 40

        if self.stock:
            self.draw_card(Card('', '', False), 50, 50, back=True)
        else:
            self.canvas.create_rectangle(50, 50, 100, 100, outline="white")

        if self.waste:
            self.draw_card(self.waste[-1], 120, 50)

        for i, suit in enumerate(SUITS):
            x = 400 + i * 120
            y = 50
            if self.foundations[suit]:
                self.draw_card(self.foundations[suit][-1], x, y)
            else:
                self.canvas.create_rectangle(x, y, x + 50, y + 70, outline="white")

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
                card_x, card_y = x, y + j * 40
                if card.face_up and card_x < event.x < card_x + 50 and card_y < event.y < card_y + 70:
                    self.save_state()
                    self.drag_cards = col[j:]
                    self.columns[i] = col[:j]
                    self.drag_col = i
                    self.drag_offset = (event.x - card_x, event.y - card_y)
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
            if x < event.x < x + 50 and 50 < event.y < 120:
                top = self.foundations[suit][-1] if self.foundations[suit] else None
                card = self.drag_cards[0]
                if len(self.drag_cards) == 1 and card.suit == suit:
                    if (not top and card.rank == 'A') or (top and RANKS.index(card.rank) == RANKS.index(top.rank) + 1):
                        self.foundations[suit].append(card)
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

    def on_double_click(self, event):
        for i, col in enumerate(self.columns):
            x = 50 + i * 120
            y = 150
            for j, card in enumerate(col):
                cx, cy = x, y + j * 40
                if card.face_up and cx < event.x < cx + 50 and cy < event.y < cy + 70:
                    self.try_send_to_foundation(card, i, j)
                    return

        if self.waste:
            card = self.waste[-1]
            if 120 < event.x < 170 and 50 < event.y < 100:
                self.try_send_to_foundation(card, -1, -1)

if __name__ == "__main__":
    root = tk.Tk()
    Solitaire(root)
    root.mainloop()
