import random
from typing import Iterable


def generate_sudoku(difficulty: str = "medium", seed: int | None = None) -> tuple[list[list[int]], list[list[int]]]:
    """
    Erzeugt ein Sudoku-Rätsel samt eindeutiger Lösung.

    Rückgabe: (puzzle, solution)
      - puzzle: 9x9-Liste mit Zahlen 0..9, wobei 0 ein leeres Feld bedeutet.
      - solution: vollständige 9x9-Lösung zum puzzle.

    Parameter:
      - difficulty: "easy" | "medium" | "hard" | "expert" (auch deutsch: "leicht" | "mittel" | "schwer" | "experte")
      - seed: Optionaler Seed für reproduzierbare Ergebnisse.

    Hinweise:
      - Das erzeugte Rätsel ist lösbar und besitzt (per Prüfroutine) genau eine Lösung.
      - Je nach Difficulty werden mehr oder weniger Felder entfernt.
    """
    rng = random.Random(seed)

    # Map Schwierigkeitsgrad -> Anzahl Hinweise (Clues)
    difficulty_map = {
        "easy": 40, "leicht": 40,
        "medium": 34, "mittel": 34,
        "hard": 28, "schwer": 28,
        "expert": 24, "experte": 24,
    }
    target_clues = difficulty_map.get(difficulty.lower(), 34)
    target_clues = max(17, min(81, target_clues))  # 17 ist das theoretische Minimum für eindeutige Rätsel

    # 1) Vollständiges, zufälliges Lösungsbrett erzeugen
    full = _generate_full_board(rng)

    # 2) Felder entfernen, dabei Eindeutigkeit wahren
    puzzle = _deepcopy_board(full)
    puzzle = _carve_uniquely(puzzle, target_clues, rng)

    return puzzle, full


# ------------------------- Hilfsfunktionen ------------------------- #

def _generate_full_board(rng: random.Random) -> list[list[int]]:
    board = [[0 for _ in range(9)] for _ in range(9)]
    if not _fill_board(board, rng):
        # Sollte praktisch nie passieren, aber zur Sicherheit: neuer Versuch
        return _generate_full_board(rng)
    return board


def _fill_board(board: list[list[int]], rng: random.Random) -> bool:
    empty = _find_empty(board)
    if not empty:
        return True
    r, c = empty
    for n in _shuffled_numbers(rng):
        if _is_valid(board, r, c, n):
            board[r][c] = n
            if _fill_board(board, rng):
                return True
            board[r][c] = 0
    return False


def _shuffled_numbers(rng: random.Random) -> Iterable[int]:
    nums = list(range(1, 10))
    rng.shuffle(nums)
    return nums


def _find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def _is_valid(board: list[list[int]], r: int, c: int, n: int) -> bool:
    # Zeile
    row = board[r]
    if any(val == n for val in row):
        return False

    # Spalte
    for rr in range(9):
        if board[rr][c] == n:
            return False

    # 3x3-Block
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if board[rr][cc] == n:
                return False

    return True


def _deepcopy_board(board: list[list[int]]) -> list[list[int]]:
    return [row.copy() for row in board]


def _count_solutions(board: list[list[int]], limit: int = 2) -> int:
    # Zählt Lösungen bis zu "limit" (Abbruch sobald erreicht).
    count = 0

    def backtrack() -> bool:
        nonlocal count
        if count >= limit:
            return True  # Früher Abbruch

        empty = _find_empty(board)
        if not empty:
            count += 1
            return count >= limit
        r, c = empty

        # Feste Reihenfolge (1..9) für deterministische Zählung
        for n in range(1, 10):
            if _is_valid(board, r, c, n):
                board[r][c] = n
                if backtrack():
                    board[r][c] = 0
                    return True  # Limit erreicht
                board[r][c] = 0
        return False
import random
from typing import Iterable


def generate_sudoku(difficulty: str = "medium", seed: int | None = None) -> tuple[list[list[int]], list[list[int]]]:
    """
    Erzeugt ein Sudoku-Rätsel samt eindeutiger Lösung.

    Rückgabe: (puzzle, solution)
      - puzzle: 9x9-Liste mit Zahlen 0..9, wobei 0 ein leeres Feld bedeutet.
      - solution: vollständige 9x9-Lösung zum puzzle.

    Parameter:
      - difficulty: "easy" | "medium" | "hard" | "expert" (auch deutsch: "leicht" | "mittel" | "schwer" | "experte")
      - seed: Optionaler Seed für reproduzierbare Ergebnisse.

    Hinweise:
      - Das erzeugte Rätsel ist lösbar und besitzt (per Prüfroutine) genau eine Lösung.
      - Je nach Difficulty werden mehr oder weniger Felder entfernt.
    """
    rng = random.Random(seed)

    # Map Schwierigkeitsgrad -> Anzahl Hinweise (Clues)
    difficulty_map = {
        "easy": 40, "leicht": 40,
        "medium": 34, "mittel": 34,
        "hard": 28, "schwer": 28,
        "expert": 24, "experte": 24,
    }
    target_clues = difficulty_map.get(difficulty.lower(), 34)
    target_clues = max(17, min(81, target_clues))  # 17 ist das theoretische Minimum für eindeutige Rätsel

    # 1) Vollständiges, zufälliges Lösungsbrett erzeugen
    full = _generate_full_board(rng)

    # 2) Felder entfernen, dabei Eindeutigkeit wahren
    puzzle = _deepcopy_board(full)
    puzzle = _carve_uniquely(puzzle, target_clues, rng)

    return puzzle, full


# ------------------------- Hilfsfunktionen ------------------------- #

def _generate_full_board(rng: random.Random) -> list[list[int]]:
    board = [[0 for _ in range(9)] for _ in range(9)]
    if not _fill_board(board, rng):
        # Sollte praktisch nie passieren, aber zur Sicherheit: neuer Versuch
        return _generate_full_board(rng)
    return board


def _fill_board(board: list[list[int]], rng: random.Random) -> bool:
    empty = _find_empty(board)
    if not empty:
        return True
    r, c = empty
    for n in _shuffled_numbers(rng):
        if _is_valid(board, r, c, n):
            board[r][c] = n
            if _fill_board(board, rng):
                return True
            board[r][c] = 0
    return False


def _shuffled_numbers(rng: random.Random) -> Iterable[int]:
    nums = list(range(1, 10))
    rng.shuffle(nums)
    return nums


def _find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def _is_valid(board: list[list[int]], r: int, c: int, n: int) -> bool:
    # Zeile
    row = board[r]
    if any(val == n for val in row):
        return False

    # Spalte
    for rr in range(9):
        if board[rr][c] == n:
            return False

    # 3x3-Block
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if board[rr][cc] == n:
                return False

    return True


def _deepcopy_board(board: list[list[int]]) -> list[list[int]]:
    return [row.copy() for row in board]


def _count_solutions(board: list[list[int]], limit: int = 2) -> int:
    # Zählt Lösungen bis zu "limit" (Abbruch sobald erreicht).
    count = 0

    def backtrack() -> bool:
        nonlocal count
        if count >= limit:
            return True  # Früher Abbruch

        empty = _find_empty(board)
        if not empty:
            count += 1
            return count >= limit
        r, c = empty

        # Feste Reihenfolge (1..9) für deterministische Zählung
        for n in range(1, 10):
            if _is_valid(board, r, c, n):
                board[r][c] = n
                if backtrack():
                    board[r][c] = 0
                    return True  # Limit erreicht
                board[r][c] = 0
        return False

    backtrack()
    return count


def _carve_uniquely(puzzle: list[list[int]], target_clues: int, rng: random.Random) -> list[list[int]]:
    # Entfernt Felder, behält Eindeutigkeit (genau eine Lösung)
    positions = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(positions)

    def clues_count(b: list[list[int]]) -> int:
        return sum(1 for r in range(9) for c in range(9) if b[r][c] != 0)

    # Versuche gleichmäßig zu reduzieren
    for r, c in positions:
        if clues_count(puzzle) <= target_clues:
            break
        if puzzle[r][c] == 0:
            continue

        backup = puzzle[r][c]
        puzzle[r][c] = 0

        # Prüfe Eindeutigkeit durch Lösungssuche mit Zählung
        board_copy = _deepcopy_board(puzzle)
        sol_count = _count_solutions(board_copy, limit=2)
        if sol_count != 1:
            puzzle[r][c] = backup  # Rückgängig machen, sonst Mehrdeutigkeit

    return puzzle
    backtrack()
    return count


def _carve_uniquely(puzzle: list[list[int]], target_clues: int, rng: random.Random) -> list[list[int]]:
    # Entfernt Felder, behält Eindeutigkeit (genau eine Lösung)
    positions = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(positions)

    def clues_count(b: list[list[int]]) -> int:
        return sum(1 for r in range(9) for c in range(9) if b[r][c] != 0)

    # Versuche gleichmäßig zu reduzieren
    for r, c in positions:
        if clues_count(puzzle) <= target_clues:
            break
        if puzzle[r][c] == 0:
            continue

        backup = puzzle[r][c]
        puzzle[r][c] = 0

        # Prüfe Eindeutigkeit durch Lösungssuche mit Zählung
        board_copy = _deepcopy_board(puzzle)
        sol_count = _count_solutions(board_copy, limit=2)
        if sol_count != 1:
            puzzle[r][c] = backup  # Rückgängig machen, sonst Mehrdeutigkeit

    return puzzle


# ------------------------- LaTeX-Ausgabe ------------------------- #

def _latex_escape(text: str) -> str:
    # Minimaler Escaper für häufige LaTeX-Sonderzeichen
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = []
    for ch in text:
        out.append(repl.get(ch, ch))
    return "".join(out)


def sudoku_to_tex(puzzle: list[list[int]], title: str | None = None, solution: list[list[int]] | None = None,
                  show_solution: bool = False) -> str:
    """
    Erzeugt LaTeX-Tabellen-Code für ein Sudoku (optional inkl. Lösung).
    Der Code ist als Snippet zum Einfügen per \\input{...} gedacht.
    """
    def row_to_cells(row: list[int]) -> str:
        cells = []
        for v in row:
            cells.append(str(v) if v != 0 else r"\phantom{0}")
        return " & ".join(cells) + r" \\"

    def grid_to_tabular(grid: list[list[int]]) -> list[str]:
        lines = [r"\begin{tabular}{|c|c|c||c|c|c||c|c|c|}", r"\hline"]
        for r in range(9):
            lines.append(row_to_cells(grid[r]))
            if r in (2, 5):
                lines.append(r"\hline\hline")
            else:
                lines.append(r"\hline")
        lines.append(r"\end{tabular}")
        return lines

    out: list[str] = [r"% Sudoku (inkludierbar)"]
    if title:
        out.append(r"\textbf{" + _latex_escape(title) + r"}\\[0.3em]")
    out.extend(grid_to_tabular(puzzle))

    if show_solution and solution is not None:
        out.append(r"\medskip")
        out.append(r"\textit{Lösung}\\[0.2em]")
        out.extend(grid_to_tabular(solution))

    return "\n".join(out) + "\n"


def save_sudoku_tex(filepath: str, puzzle: list[list[int]], solution: list[list[int]] | None = None,
                    show_solution: bool = False, title: str | None = None) -> None:
    """
    Speichert ein Sudoku (und optional die Lösung) als .tex-Snippet, das via \\input eingebunden werden kann.
    """
    content = sudoku_to_tex(puzzle, title=title, solution=solution, show_solution=show_solution)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def generate_and_save_sudoku_tex(filepath: str, difficulty: str = "medium", seed: int | None = None,
                                 show_solution: bool = False, title: str | None = None) -> tuple[list[list[int]], list[list[int]]]:
    """
    Erzeugt ein Sudoku gemäß Schwierigkeitsgrad und speichert es als .tex-Datei.
    Rückgabe: (puzzle, solution)
    """
    puzzle, solution = generate_sudoku(difficulty=difficulty, seed=seed)
    save_sudoku_tex(filepath, puzzle, solution=solution, show_solution=show_solution, title=title)
    return puzzle, solution
