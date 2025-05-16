
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import csv


def charger_donnees_csv(fichier):
    parties, scores, victoires, coups = [], [], [], []
    with open(fichier, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            parties.append(int(row['Partie']))
            scores.append(int(row['Score']))
            victoires.append(int(row['Victoires']))
            coups.append(int(row['Coups']))
    return parties, scores, victoires, coups

def afficher_graphiques():
    try:
        parties, scores, victoires, coups = charger_donnees_csv("stats.csv")

        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(parties, scores, label="Score")
        plt.plot(parties, victoires, label="Victoire")
        plt.title("Évolution des scores et victoires")
        plt.xlabel("Partie")
        plt.ylabel("Valeur")
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(parties, coups, color='orange', label="Coups joués")
        plt.xlabel("Partie")
        plt.ylabel("Nombre de coups")
        plt.title("Nombre de coups par partie")
        plt.tight_layout()
        plt.legend()

        plt.show()
    except Exception as e:
        print("Erreur :", e)

# Interface simple
root = tk.Tk()
root.title("Visualiseur des entraînements IA")
root.geometry("300x150")

label = tk.Label(root, text="Visualiser les statistiques d'entraînement")
label.pack(pady=10)

btn = tk.Button(root, text="Afficher les graphiques", command=afficher_graphiques)
btn.pack(pady=20)

root.mainloop()
