import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import re

# Constants
BG_COLOR = "#f0f0f0"
TILE_COLORS = {
    'correct': '#6aaa64',    # green
    'present': '#c9b458',    # yellow
    'absent': '#787c7e',     # grey
    'empty': '#ffffff',      # white
    'text': '#ffffff',       # white
    'text_dark': '#000000',  # black
    'key_default': '#d3d6da',
}

# Game state
current_row = 0
guesses = [""] * 6
answer = ""
game_active = False
show_menu = True

# Widgets
tiles = []
key_buttons = {}
status_label = None
menu_frame = None
game_frame = None
root = None

def setup_window():
    global root
    root = tk.Tk()
    root.title("Wordle Game")
    root.geometry("450x700")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)

def compile_cpp_code():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cpp_path = os.path.join(script_dir, 'FileName.cpp')
    exe_path = os.path.join(script_dir, 'wordle_game')
    
    if not os.path.exists(exe_path):
        if not os.path.exists(cpp_path):
            messagebox.showerror("File Missing", "FileName.cpp not found!")
            root.quit()
            return False
        
        try:
            subprocess.run(["g++", cpp_path, "-o", exe_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Compilation Error", f"Failed to compile C++ code: {e}")
            root.quit()
            return False
        except FileNotFoundError:
            messagebox.showerror("Compiler Not Found", "g++ compiler not found. Please install it.")
            root.quit()
            return False
    return True

def create_menu():
    global menu_frame
    menu_frame = tk.Frame(root, bg=BG_COLOR)
    menu_frame.pack(fill='both', expand=True)
    
    # Title
    tk.Label(menu_frame, text="WORDLE GAME", 
            font=("Arial", 24, "bold"), bg=BG_COLOR).pack(pady=20)
    
    # Rules
    rules_frame = tk.Frame(menu_frame, bg=BG_COLOR)
    rules_frame.pack(pady=10)
    
    tk.Label(rules_frame, text="Rules:", 
            font=("Arial", 14, "bold"), bg=BG_COLOR).pack(anchor='w')
    
    rules = [
        "- Guess the 5-letter word in 6 tries",
        "- Green: correct letter in correct spot",
        "- Yellow: letter is in word but wrong spot",
        "- Grey: letter is not in the word"
    ]
    
    for rule in rules:
        tk.Label(rules_frame, text=rule, font=("Arial", 12), 
                bg=BG_COLOR, anchor='w').pack(fill='x', padx=20)
    
    # Buttons
    btn_frame = tk.Frame(menu_frame, bg=BG_COLOR)
    btn_frame.pack(pady=30)
    
    tk.Button(btn_frame, text="Play", font=("Arial", 14), 
             command=start_game, width=10).pack(side='left', padx=10)
    
    tk.Button(btn_frame, text="Quit", font=("Arial", 14), 
             command=quit_game, width=10).pack(side='left', padx=10)

def quit_game():
    root.quit()
    root.destroy()

def create_game_frame():
    global game_frame, tiles, status_label, key_buttons
    game_frame = tk.Frame(root, bg=BG_COLOR)
    
    # Game grid
    grid_frame = tk.Frame(game_frame, bg=BG_COLOR)
    grid_frame.pack(pady=20)
    
    tiles = []
    for row in range(6):
        row_tiles = []
        for col in range(5):
            tile = tk.Label(grid_frame, text="", font=("Arial", 24, "bold"),
                          width=2, height=1, relief="solid", borderwidth=2,
                          bg=TILE_COLORS['empty'], fg=TILE_COLORS['text_dark'])
            tile.grid(row=row, column=col, padx=3, pady=3)
            row_tiles.append(tile)
        tiles.append(row_tiles)
    
    # Status label
    status_label = tk.Label(game_frame, 
                          text="", font=("Arial", 12), bg=BG_COLOR)
    status_label.pack(pady=5)
    
    # Keyboard
    create_keyboard()
    
    # Control buttons
    control_frame = tk.Frame(game_frame, bg=BG_COLOR)
    control_frame.pack(pady=10)
    
    tk.Button(control_frame, text="Enter", width=8, height=1,
             font=("Arial", 12), command=submit_guess).pack(side="left", padx=5)
    
    tk.Button(control_frame, text="Delete", width=8, height=1,
             font=("Arial", 12), command=delete_letter).pack(side="left", padx=5)

def create_keyboard():
    global key_buttons
    keyboard_frame = tk.Frame(game_frame, bg=BG_COLOR)
    keyboard_frame.pack(pady=10)
    
    keyboard_rows = [
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM"
    ]
    
    key_buttons = {}
    for i, row in enumerate(keyboard_rows):
        frame = tk.Frame(keyboard_frame, bg=BG_COLOR)
        frame.pack()
        for char in row:
            btn = tk.Button(frame, text=char, width=3, height=1,
                          font=("Arial", 12, "bold"),
                          command=lambda c=char: add_letter(c),
                          bg=TILE_COLORS['key_default'], fg=TILE_COLORS['text_dark'],
                          relief="raised", borderwidth=1)
            btn.pack(side="left", padx=2, pady=2)
            key_buttons[char] = btn

def start_game():
    global current_row, guesses, answer, game_active, show_menu
    
    # Hide menu and show game
    if menu_frame:
        menu_frame.pack_forget()
    
    if not game_frame:
        create_game_frame()
    game_frame.pack(fill='both', expand=True)
    
    # Reset game state
    game_active = True
    current_row = 0
    guesses = [""] * 6
    answer = get_random_word()
    
    if answer == "ERROR":
        quit_game()
        return
    
    # Clear the board
    for row in range(6):
        for col in range(5):
            tiles[row][col].config(
                text="", 
                bg=TILE_COLORS['empty'], 
                fg=TILE_COLORS['text_dark']
            )
    
    # Reset keyboard colors
    for btn in key_buttons.values():
        btn.config(
            bg=TILE_COLORS['key_default'], 
            fg=TILE_COLORS['text_dark'], 
            state="normal"
        )
    
    status_label.config(text="")
    show_menu = False

def get_random_word():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, 'wordle_game')
    try:
        result = subprocess.run([exe_path, "--get-word"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().upper()
        else:
            messagebox.showerror("Error", "Failed to get random word from game logic")
            return "ERROR"
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute game: {e}")
        return "ERROR"

def add_letter(letter):
    global current_row, guesses
    
    if (game_active and 
        len(guesses[current_row]) < 5):
        guesses[current_row] += letter.upper()
        update_grid()

def delete_letter():
    global current_row, guesses
    
    if (game_active and 
        len(guesses[current_row]) > 0):
        guesses[current_row] = guesses[current_row][:-1]
        update_grid()

def update_grid():
    # Update all rows up to the current one
    for row in range(current_row + 1):
        guess = guesses[row]
        for col in range(5):
            if col < len(guess):
                tiles[row][col].config(
                    text=guess[col]
                )
            else:
                tiles[row][col].config(text="")
    
    # Clear rows after current row
    for row in range(current_row + 1, 6):
        for col in range(5):
            tiles[row][col].config(text="")

def check_guess(guess):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(script_dir, 'wordle_game')
    try:
        result = subprocess.run(
            [exe_path, "--check-guess", answer, guess], 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            status_label.config(
                text="Invalid guess - word not in dictionary"
            )
            return None
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check guess: {e}")
        return None

def submit_guess():
    global current_row, game_active
    
    if not game_active:
        return
    
    guess = guesses[current_row]
    if len(guess) != 5:
        status_label.config(text="Word must be 5 letters!")
        return
    
    feedback = check_guess(guess)
    if not feedback:
        return
    
    update_tile_colors(feedback, guess)
    
    if guess == answer:
        status_label.config(
            text=f"Congratulations! You won in {current_row + 1} attempts!"
        )
        game_active = False
        show_end_game_options()
        return
    elif current_row == 5:
        status_label.config(
            text=f"Game over! The word was {answer}"
        )
        game_active = False
        show_end_game_options()
        return
    
    current_row += 1
    status_label.config(text="")

def update_tile_colors(feedback, guess):
    # Parse the ANSI color codes from the C++ output
    parts = re.split('(\033\[[\d;]+m)', feedback)
    parts = [p for p in parts if p]  # Remove empty strings
    
    color_map = {
        '32': 'correct',  # Green
        '33': 'present',  # Yellow
        '90': 'absent'    # Grey
    }
    
    current_color = None
    char_index = 0
    
    for part in parts:
        if part.startswith('\033['):
            # This is a color code
            code = part[2:-1]  # Remove \033[ and m
            if code in color_map:
                current_color = color_map[code]
            else:
                current_color = None
        else:
            # This is a character (or part of one)
            if current_color and char_index < 5:
                char = guess[char_index]
                # Update tile color
                tiles[current_row][char_index].config(
                    bg=TILE_COLORS[current_color],
                    fg=TILE_COLORS['text']
                )
                # Update keyboard color (only if better state)
                btn = key_buttons[char]
                current_btn_color = btn.cget('bg')
                
                if (current_color == 'correct' or 
                    (current_color == 'present' and current_btn_color != TILE_COLORS['correct']) or
                    (current_color == 'absent' and current_btn_color not in (TILE_COLORS['correct'], TILE_COLORS['present']))):
                    btn.config(
                        bg=TILE_COLORS[current_color],
                        fg=TILE_COLORS['text']
                    )
                char_index += 1

def show_end_game_options():
    end_frame = tk.Frame(game_frame, bg=BG_COLOR)
    end_frame.pack(pady=20)
    
    tk.Button(end_frame, text="Play Again", font=("Arial", 12),
             command=lambda: [end_frame.destroy(), start_game()]).pack(side="left", padx=10)
    
    tk.Button(end_frame, text="Quit", font=("Arial", 12),
             command=quit_game).pack(side="left", padx=10)

def handle_key_press(event):
    if not game_active:
        return
    
    key = event.char.upper()
    if key.isalpha() and len(key) == 1:
        add_letter(key)
    elif event.keysym == "BackSpace":
        delete_letter()
    elif event.keysym == "Return":
        submit_guess()

# Main program
if __name__ == "__main__":
    setup_window()
    
    if compile_cpp_code():
        # Check if words5.txt exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        words5_path = os.path.join(script_dir, 'words5.txt')
        if not os.path.exists(words5_path):
            messagebox.showerror("File Missing", "words5.txt not found!")
            root.quit()
        else:
            create_menu()
            root.bind("<Key>", handle_key_press)
            root.mainloop()