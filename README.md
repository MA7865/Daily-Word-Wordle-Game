# DailyWord 🟩🟨⬜

DailyWord is a Wordle-style word-guessing game. Players have **6 tries** to guess a secret **5-letter word**, getting color-coded hints after every guess:

- 🟩 **Green** — right letter, right spot
- 🟨 **Yellow** — right letter, wrong spot
- ⬜ **Grey** — letter isn't in the word at all

The project has two parts that work together:

1. A **C++ program** that holds all the actual game logic (picking the secret word, checking guesses, giving feedback).
2. A **Python GUI** (built with Tkinter) that gives the player a clickable on-screen board and keyboard, and talks to the C++ program behind the scenes to actually run the game.

---

## How it all works together

The GUI doesn't do any of the "thinking" itself — it just displays things and asks the C++ program for answers. Here's the flow:

1. You run `DailyWord 2.py`.
2. The very first time, the script automatically **compiles** `FileName.cpp` into a runnable program (called `wordle_game`, or `wordle_game.exe` on Windows) using the `g++` compiler. If that program already exists, it skips this step. (A pre-built `wordle_game.exe` is already included in this repo for Windows users.)
3. The Python window opens on a **menu screen** with the rules and a "Play" button.
4. When you click **Play**, Python runs the C++ program with the hidden option `--get-word`, which returns one random 5-letter word chosen from `words5.txt`. This becomes the secret answer for that round. Python never shows this word to you — it just stores it in memory.
5. You type a guess (on-screen keyboard buttons or your physical keyboard both work).
6. When you press **Enter**, Python sends that guess to the C++ program using the `--check-guess` option, along with the secret answer.
7. The C++ program checks the guess and sends back a result string where each letter is wrapped in a color code (green/yellow/grey), the same style used in a colored terminal.
8. Python reads that color-coded string, and instead of printing it to a terminal, it uses it to color the tiles and keyboard keys on screen.
9. This repeats until you either guess the word (win) or run out of 6 tries (lose), after which you get "Play Again" and "Quit" buttons.

So essentially: **Python = the face of the game (what you see and click), C++ = the brain of the game (the actual rules and logic).** They "talk" to each other through the command line, not by sharing code directly.

---

## Files in this project

| File | What it is |
|---|---|
| `FileName.cpp` | The C++ backend — all the real game logic lives here (choosing the word, checking guesses, scoring). Can also be run completely on its own as a text-based terminal game. |
| `DailyWord 2.py` | The Python GUI — the visual Wordle board, on-screen keyboard, buttons, and menus. Calls the compiled C++ program to actually play. Written/run using Thonny. |
| `words5.txt` | The dictionary — a plain text file with one 5-letter word per line (505 words total). This is the pool the C++ program picks the secret word from, and also what it checks your guesses against to make sure you typed a real word. |
| `wordle_game.exe` | The already-compiled version of `FileName.cpp` for Windows, so players don't strictly need a C++ compiler installed to play the GUI version. |
| `DailyWord Code.docx` | A Word document backup containing copies of the C++ and Python source code, kept for reference/documentation purposes. |

---

## C++ functions (`FileName.cpp`) and what they do

| Function | Purpose |
|---|---|
| `main()` | The entry point. If it's launched with special arguments (`--get-word` or `--check-guess`), it runs in "helper mode" for the Python GUI and just prints one result then exits. If launched with no arguments, it runs the full classic terminal game (menu + full play loop). |
| `get5LetterWords()` | A one-time utility function used while building the word list — it reads a big word file and copies out only the words that are exactly 5 letters long into `words5.txt`. (Not used during normal play — it was for preparing the dictionary.) |
| `loadWords()` | Reads `words5.txt` into memory as a list (vector) of words, so the game has something to pick from and check against. |
| `get_random_word()` | Picks and returns one random word from the loaded word list — this becomes the secret answer for a round. |
| `check_if_5_letters()` | Checks that a guess is exactly 5 characters long and that every character is a letter (not a number or symbol). Basic input validation. |
| `check_if_in_dictionary()` | Checks whether a guess actually exists in the word list, so players can't guess made-up words. |
| `menu()` | Prints the welcome screen and rules — used only in terminal mode. |
| `performWordle()` | The heart of the game. Compares a guess letter-by-letter against the secret answer and works out which letters are green (correct spot), yellow (wrong spot but in the word), or grey (not in the word at all) — handling repeated letters correctly. Returns the guess as a string with ANSI color codes attached, ready to display. |
| `playWordle()` | Runs the full game loop for terminal mode: picks a word, repeatedly asks for guesses, checks them, shows results, and asks "play again?" at the end. |

### About the `--get-word` / `--check-guess` options
These aren't part of the "real" game rules — they were added specifically so the Python GUI can use the C++ program like a mini calculator:
- `wordle_game --get-word` → just prints one random word and exits.
- `wordle_game --check-guess <answer> <guess>` → checks one guess against one answer and prints the colored result, then exits.

This lets the GUI reuse all the original game logic without rewriting it in Python.

---

## Python functions (`DailyWord 2.py`) and what they do

| Function | Purpose |
|---|---|
| `setup_window()` | Creates and configures the main game window (size, title, background color). |
| `compile_cpp_code()` | Checks if the compiled C++ program already exists; if not, compiles `FileName.cpp` using `g++`. Shows an error popup if the compiler or source file is missing. |
| `create_menu()` | Builds the start-screen menu: title, rules text, and Play/Quit buttons. |
| `quit_game()` | Closes the game window. |
| `create_game_frame()` | Builds the main game screen: the 6×5 grid of letter tiles, the status message label, the on-screen keyboard, and the Enter/Delete buttons. |
| `create_keyboard()` | Builds the on-screen QWERTY keyboard as clickable buttons. |
| `start_game()` | Resets the board for a new round, hides the menu, shows the game screen, and asks the C++ program for a new secret word. |
| `get_random_word()` | Calls the compiled C++ program with `--get-word` and returns the word it gives back (this is the hidden answer for the round). |
| `add_letter()` | Adds a typed/clicked letter to the current guess (if the row isn't already full). |
| `delete_letter()` | Removes the last letter from the current guess (backspace). |
| `update_grid()` | Redraws the letters currently typed onto the tile grid. |
| `check_guess()` | Calls the compiled C++ program with `--check-guess` to validate and score the current guess. |
| `submit_guess()` | Called when Enter is pressed. Makes sure the guess is 5 letters, gets the color feedback from C++, updates the tiles/keyboard colors, and checks if the player has won or lost. |
| `update_tile_colors()` | Reads the color codes sent back by the C++ program and applies matching colors to the tiles and the on-screen keyboard keys. |
| `show_end_game_options()` | Shows "Play Again" and "Quit" buttons once a round ends. |
| `handle_key_press()` | Lets the player use their physical keyboard (letters, Backspace, Enter) instead of only clicking on-screen buttons. |

---

## How to run it

**You need:**
- Python 3 (Tkinter comes built in with most Python installs, so no extra install needed for the GUI itself)
- A C++ compiler (`g++`) available in your system's PATH — only needed if you're not on Windows or don't want to use the included `wordle_game.exe`
  - Windows: install [MinGW](https://www.mingw-w64.org/) or MSYS2, which provides `g++`
  - Mac: install Xcode Command Line Tools (`xcode-select --install`)
  - Linux: install `build-essential` (`sudo apt install build-essential`)

**Steps:**
1. Download/clone this repository — keep all files in the **same folder** (the Python script looks for `FileName.cpp`, `words5.txt`, and the compiled program right next to itself).
2. Run the GUI:
   ```
   python "DailyWord 2.py"
   ```
3. On first launch, it will automatically compile `FileName.cpp` (unless `wordle_game`/`wordle_game.exe` already exists). This may take a second.
4. Click **Play** and start guessing!

**Playing in the terminal instead (no GUI):**
You can also play the original text-based version directly:
```
g++ FileName.cpp -o wordle_game
./wordle_game
```
This runs the classic menu + full game loop version, with colored text straight in your terminal.

---

## Notes

- The word list (`words5.txt`) currently has 505 words. You can add more by putting additional 5-letter words in the file, one per line, in capital letters.
- In terminal mode, `playWordle()` currently prints a "(Debug) Randomly selected word" line that reveals the answer — this was left in for testing and can be removed for a "real" play experience. It has no effect on the GUI version, since the GUI never calls this function.
- Tools used while building this: **VS Code** for the C++ backend, and **Thonny** for the Python GUI.

---

## Credits

Built by [Your Name] and [Friend's Name].
