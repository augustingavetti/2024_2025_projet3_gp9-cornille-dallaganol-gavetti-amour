import curses

def draw_board(stdscr, board):
    stdscr.clear()
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            stdscr.addch(y, x * 2, cell)
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    board = [
        [" ", " ", "X", "X", "X", " ", " "],
        [" ", " ", "X", "X", "X", " ", " "],
        ["X", "X", "X", "X", "X", "X", "X"],
        ["X", "X", "X", "O", "X", "X", "X"],
        ["X", "X", "X", "X", "X", "X", "X"],
        [" ", " ", "X", "X", "X", " ", " "],
        [" ", " ", "X", "X", "X", " ", " "],
    ]
    draw_board(stdscr, board)
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
