import tkinter as tk

def create_board():
    root = tk.Tk()
    root.title("Solitaire")
    
    board = [
        [" ", " ", "X", "X", "X", " ", " "],
        [" ", " ", "X", "X", "X", " ", " "],
        ["X", "X", "X", "X", "X", "X", "X"],
        ["X", "X", "X", "O", "X", "X", "X"],
        ["X", "X", "X", "X", "X", "X", "X"],
        [" ", " ", "X", "X", "X", " ", " "],
        [" ", " ", "X", "X", "X", " ", " "],
    ]
    
    frame = tk.Frame(root)
    frame.pack()
    
    buttons = []
    for r, row in enumerate(board):
        button_row = []
        for c, cell in enumerate(row):
            if cell == "X":
                btn = tk.Button(frame, text="X", width=4, height=2)
            elif cell == "O":
                btn = tk.Button(frame, text="O", width=4, height=2)
            else:
                btn = tk.Button(frame, text="", state=tk.DISABLED, width=4, height=2)
            btn.grid(row=r, column=c)
            button_row.append(btn)
        buttons.append(button_row)
    
    root.mainloop()

if __name__ == "__main__":
    create_board()