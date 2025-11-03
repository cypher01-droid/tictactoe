import tkinter as tk
from tkinter import ttk
from functools import partial
import time
import threading
from typing import List, Tuple, Optional



PLAYER_X: str = "Fire"          # Player
PLAYER_O: str = "Water"         # AI
current_player: str = PLAYER_X
game_active: bool = True
ai_thread: Optional[threading.Thread] = None

scores: dict[str, int] = {"X": 0, "O": 0, "Draw": 0}
theme: str = "dark"


window = tk.Tk()
window.title("Tic Tac Toe Deluxe | Mebucorp Softwares")
window.resizable(False, False)

# All buttons are created → no Optional needed
buttons: List[List[tk.Button]] = [[None for _ in range(3)] for _ in range(3)]



themes = {
    "dark": {"bg": "#1e1e1e", "fg": "white", "btn": "#3c3c3c", "accent": "#ffd700"},
    "light": {"bg": "white", "fg": "black", "btn": "#e0e0e0", "accent": "#b8860b"},
}

style = ttk.Style()
style.theme_use("clam")

def apply_theme() -> None:
    t = themes[theme]
    window.config(bg=t["bg"])
    score_label.config(bg=t["bg"], fg=t["fg"])
    mode_button.config(bg=t["btn"], fg=t["fg"])
    reset_button.config(bg=t["btn"], fg=t["fg"])
    style.configure("TProgressbar", background=t["accent"], troughcolor=t["btn"])

    for row in buttons:
        for btn in row:
            if btn["text"] == "":
                btn.config(bg=t["btn"], fg=t["fg"])



score_label = tk.Label(window, text="", font=("Arial", 16, "bold"))
score_label.grid(row=3, column=0, columnspan=3, pady=10)

def update_scoreboard() -> None:
    score_label.config(
        text=f"{PLAYER_X}: {scores['X']} | {PLAYER_O}: {scores['O']} | Draw: {scores['Draw']}"
    )



def toggle_theme() -> None:
    global theme
    theme = "light" if theme == "dark" else "dark"
    apply_theme()

mode_button = tk.Button(window, text="Toggle Theme", command=toggle_theme, font=("Arial", 10))
mode_button.grid(row=4, column=0, columnspan=3, pady=5)



def check_winner() -> Optional[str]:
    wins = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
    ]

    for line in wins:
        symbols = [buttons[r][c]["text"] for r, c in line]
        if symbols[0] != "" and all(s == symbols[0] for s in symbols):
            animate_win(line)
            return "X" if symbols[0] == PLAYER_X else "O"

    if all(buttons[r][c]["text"] != "" for r in range(3) for c in range(3)):
        return "draw"

    return None

def animate_win(winning_cells: List[Tuple[int, int]]) -> None:
    def flash(count: int = 6) -> None:
        if count == 0:
            return
        color = "gold" if count % 2 == 0 else themes[theme]["btn"]
        for r, c in winning_cells:
            buttons[r][c].config(bg=color)
        window.after(150, flash, count - 1)
    flash()


def evaluate_board() -> Optional[int]:
    result = check_winner()
    if result == "X":
        return -10
    if result == "O":
        return 10
    if result == "draw":
        return 0
    return None

def minimax(is_maximizing: bool, alpha: Optional[int] = None, beta: Optional[int] = None) -> int:
    if alpha is None:
        alpha = -1000
    if beta is None:
        beta = 1000

    score = evaluate_board()
    if score is not None:
        return score

    empty_cells = [(r, c) for r in range(3) for c in range(3) if buttons[r][c]["text"] == ""]

    if is_maximizing:
        max_eval = -1000
        for r, c in empty_cells:
            buttons[r][c].config(text=PLAYER_O)
            eval_score = minimax(False, alpha, beta)
            buttons[r][c].config(text="")
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 1000
        for r, c in empty_cells:
            buttons[r][c].config(text=PLAYER_X)
            eval_score = minimax(True, alpha, beta)
            buttons[r][c].config(text="")
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def best_move() -> Optional[Tuple[int, int]]:
    empty = [(r, c) for r in range(3) for c in range(3) if buttons[r][c]["text"] == ""]
    if not empty:
        return None

    best_score = -1000
    move: Optional[Tuple[int, int]] = None
    for r, c in empty:
        buttons[r][c].config(text=PLAYER_O)
        score = minimax(False)
        buttons[r][c].config(text="")
        if score > best_score:
            best_score = score
            move = (r, c)
    return move



thinking_var = tk.DoubleVar()
thinking_bar = ttk.Progressbar(window, variable=thinking_var, maximum=100, length=280)
thinking_bar.grid(row=6, column=0, columnspan=3, pady=8)

def ai_move() -> None:
    global current_player, game_active, ai_thread

    if not game_active or current_player != PLAYER_O:
        thinking_var.set(0)
        return

    # Simulate thinking
    for i in range(101):
        if not game_active or current_player != PLAYER_O:
            thinking_var.set(0)
            return
        thinking_var.set(i)
        window.update_idletasks()
        time.sleep(0.008)
    thinking_var.set(0)
    time.sleep(0.1)

    if not game_active or current_player != PLAYER_O:
        return

    move = best_move()
    if move is None:
        return

    r, c = move
    window.after(0, lambda: buttons[r][c].config(text=PLAYER_O))
    window.after(50, complete_ai_turn)

def complete_ai_turn() -> None:
    global current_player, game_active
    if not game_active:
        return

    result = check_winner()
    if result:
        handle_result(result)
    else:
        current_player = PLAYER_X



def handle_result(result: str) -> None:
    global game_active
    game_active = False
    if result == "X":
        scores["X"] += 1
    elif result == "O":
        scores["O"] += 1
    elif result == "draw":
        scores["Draw"] += 1
    update_scoreboard()



def reset_game() -> None:
    global current_player, game_active, ai_thread
    current_player = PLAYER_X
    game_active = True
    ai_thread = None
    thinking_var.set(0)

    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="", bg=themes[theme]["btn"])
    update_scoreboard()

reset_button = tk.Button(window, text="Reset Game", command=reset_game, font=("Arial", 10))
reset_button.grid(row=5, column=0, columnspan=3, pady=5)



def on_button_click(r: int, c: int) -> None:
    global ai_thread, current_player
    btn = buttons[r][c]
    if btn["text"] != "" or not game_active or current_player != PLAYER_X:
        return

    btn.config(text=PLAYER_X)
    result = check_winner()
    if result:
        handle_result(result)
        return

    current_player = PLAYER_O
    if ai_thread is None or not ai_thread.is_alive():
        ai_thread = threading.Thread(target=ai_move, daemon=True)
        ai_thread.start()


for r in range(3):
    for c in range(3):
        btn = tk.Button(
            window,
            text="",
            font=("Arial", 36, "bold"),
            width=4,
            height=2,
            relief="flat",
            highlightthickness=0,
        )
        btn.config(command=partial(on_button_click, r, c))
        btn.grid(row=r, column=c, padx=6, pady=6)
        buttons[r][c] = btn



update_scoreboard()
apply_theme()


window.update_idletasks()
w = window.winfo_width()
h = window.winfo_height()
x = (window.winfo_screenwidth() // 2) - (w // 2)
y = (window.winfo_screenheight() // 2) - (h // 2)
window.geometry(f"{w}x{h}+{x}+{y}")

window.mainloop()