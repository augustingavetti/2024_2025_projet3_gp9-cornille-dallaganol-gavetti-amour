
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import csv
import os


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
        # Graphique 1 — mode normal
        if os.path.exists("stats/stats.csv"):
            parties, scores, victoires, coups = charger_donnees_csv("stats/stats.csv")

            plt.figure(figsize=(10, 6))
            plt.subplot(2, 1, 1)
            plt.plot(parties, scores, label="Score")
            plt.plot(parties, victoires, label="Victoire")
            plt.title("Évolution des scores (mode normal)")
            plt.xlabel("Partie")
            plt.ylabel("Valeur")
            plt.legend()

            plt.subplot(2, 1, 2)
            plt.plot(parties, coups, color='orange', label="Coups joués")
            plt.xlabel("Partie")
            plt.ylabel("Nombre de coups")
            plt.title("Coups joués (mode normal)")
            plt.tight_layout()
            plt.legend()
            plt.show()

        else:
            print("⚠️ Le fichier stats/stats.csv est introuvable.")

        # Graphique 2 — mode fin de partie
        fin_stats_path = "saved/finisher/fin_stats.csv"
        if os.path.exists(fin_stats_path):
            with open(fin_stats_path, newline='') as f:
                reader = csv.DictReader(f)
                episodes, scores, coups, victoires = [], [], [], []
                for row in reader:
                    episodes.append(int(row['Episode']))
                    scores.append(int(row['Score']))
                    coups.append(int(row['Coups']))
                    victoires.append(int(row['Victoire']))

            plt.figure(figsize=(10, 6))
            plt.subplot(2, 1, 1)
            plt.plot(episodes, scores, label="Score (fin de partie)")
            plt.plot(episodes, victoires, label="Victoire")
            plt.title("Évolution des scores (fin de partie)")
            plt.xlabel("Épisode")
            plt.ylabel("Valeur")
            plt.legend()

            plt.subplot(2, 1, 2)
            plt.plot(episodes, coups, color='green', label="Coups joués (fin)")
            plt.xlabel("Épisode")
            plt.ylabel("Nombre de coups")
            plt.title("Coups joués (fin de partie)")
            plt.tight_layout()
            plt.legend()
            plt.show()

        else:
            print("ℹ️ Le fichier saved/finisher/fin_stats.csv n'existe pas encore. Lance d'abord le mode 'fin de partie'.")

    except Exception as e:
        print("❌ Erreur :", e)


# Interface simple
root = tk.Tk()
root.title("Visualiseur des entraînements IA")
root.geometry("300x150")

label = tk.Label(root, text="Visualiser les statistiques d'entraînement")
label.pack(pady=10)

btn = tk.Button(root, text="Afficher les graphiques", command=afficher_graphiques)
btn.pack(pady=20)

root.mainloop()
