# solitaire_env.py
from copy import deepcopy
from ai import SolitaireAI
import torch
import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COLORS = {'♠': 'black', '♣': 'black', '♥': 'red', '♦': 'red'}

class SolitaireEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        full_deck = [(s, r) for s in SUITS for r in RANKS]
        random.shuffle(full_deck)

        self.columns = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i + 1):
                card = full_deck.pop()
                self.columns[i].append((card, j == i))  # (card, face_up)

        self.stock = full_deck.copy()  # ✅ on garde les cartes restantes
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.score = 0
        self.done = False
        self.total_moves = 0

    
    def get_state(self):
        state = []

    # 7 colonnes : on encode (cartes visibles, cartes totales)
        for col in self.columns:
            visibles = sum(1 for c, up in col if up)
            total = len(col)
            state.append(visibles)
            state.append(total)

    # stock : nb de cartes restantes
        state.append(len(self.stock))

    # waste : encode rang + couleur (si visible)
        if self.waste:
            suit, rank = self.waste[-1][0]
            state.append(RANKS.index(rank) / 12)  # entre 0 et 1
            state.append(['♠', '♥', '♦', '♣'].index(suit) / 3)
        else:
            state += [0, 0]

    # fondations : normalisées
        for suit in SUITS:
            state.append(len(self.foundations[suit]) / 13)

        return torch.FloatTensor(state)

    
    def apply_action(self, action):
        reward = -0.05  # pénalité par défaut pour encourager l'efficacité

        if action == 0:  # tirer carte
            if self.stock:
                card = self.stock.pop()
                self.waste.append((card, True))
                reward = 0.1
            elif self.waste:
                self.stock = [c for c, _ in self.waste[::-1]]
                self.waste = []
                reward = -0.2  # pénalité : rebrassage inutile

        elif action == 1:  # mettre waste → fondation
            if self.waste:
                suit, rank = self.waste[-1][0]
                foundation = self.foundations[suit]
                if (not foundation and rank == 'A') or (foundation and RANKS.index(rank) == RANKS.index(foundation[-1]) + 1):
                    self.foundations[suit].append(rank)
                    self.waste.pop()
                    reward = 5

        elif action == 2:  # déplacer entre colonnes
            for i, col in enumerate(self.columns):
                if col and col[-1][1]:
                    suit, rank = col[-1][0]
                    for j, dest in enumerate(self.columns):
                        if i != j:
                            if not dest and rank == 'K':
                                self.columns[j].append((col.pop()[0], True))
                                reward = 1
                                return reward
                            elif dest and dest[-1][1]:
                                dsuit, drank = dest[-1][0]
                                if COLORS[suit] != COLORS[dsuit] and RANKS.index(rank) + 1 == RANKS.index(drank):
                                    self.columns[j].append((col.pop()[0], True))
                                    reward = 1
                                    return reward

        elif action == 3:  # colonne → fondation
            for i, col in enumerate(self.columns):
                if col and col[-1][1]:
                    suit, rank = col[-1][0]
                    foundation = self.foundations[suit]
                    if (not foundation and rank == 'A') or (foundation and RANKS.index(rank) == RANKS.index(foundation[-1]) + 1):
                        self.foundations[suit].append(rank)
                        col.pop()
                        reward = 5
                        return reward

        self.total_moves += 1
        return reward

