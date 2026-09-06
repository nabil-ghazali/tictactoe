"""Tests de la logique pure du jeu (aucun appel LLM)."""

from Back.game_logic import check_win, is_grid_full, is_move_valid

GRID_SIZE = 10


def empty_grid():
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


# --------------------------------------------------------------------------- #
# is_move_valid
# --------------------------------------------------------------------------- #
def test_is_move_valid_on_empty_cell():
    assert is_move_valid(empty_grid(), 4, 5) is True


def test_is_move_valid_on_occupied_cell():
    grid = empty_grid()
    grid[4][5] = 1
    assert is_move_valid(grid, 4, 5) is False
    grid[4][5] = 2
    assert is_move_valid(grid, 4, 5) is False


def test_is_move_valid_out_of_bounds():
    grid = empty_grid()
    for row, col in [(-1, 0), (0, -1), (GRID_SIZE, 0), (0, GRID_SIZE), (99, 99)]:
        assert is_move_valid(grid, row, col) is False


def test_is_move_valid_rejects_non_int_coordinates():
    grid = empty_grid()
    for row, col in [(1.5, 2), (2, "3"), (None, 0)]:
        assert is_move_valid(grid, row, col) is False


# --------------------------------------------------------------------------- #
# check_win  (alignement de 5)
# --------------------------------------------------------------------------- #
def test_check_win_horizontal():
    grid = empty_grid()
    for c in range(2, 7):  # colonnes 2..6, ligne 3
        grid[3][c] = 1
    assert check_win(grid, 1, 3, 6) is True
    assert check_win(grid, 2, 3, 6) is False  # pas le bon joueur


def test_check_win_vertical():
    grid = empty_grid()
    for r in range(0, 5):
        grid[r][7] = 2
    assert check_win(grid, 2, 4, 7) is True


def test_check_win_diagonal_down_right():
    grid = empty_grid()
    for i in range(5):
        grid[i][i] = 1
    assert check_win(grid, 1, 4, 4) is True


def test_check_win_diagonal_down_left():
    grid = empty_grid()
    for i in range(5):
        grid[i][8 - i] = 2
    assert check_win(grid, 2, 2, 6) is True


def test_check_win_counts_both_directions_from_last_move():
    # Dernier coup au MILIEU de la ligne de 5.
    grid = empty_grid()
    for c in range(4, 9):
        grid[5][c] = 1
    assert check_win(grid, 1, 5, 6) is True


def test_check_win_needs_exactly_five():
    grid = empty_grid()
    for c in range(2, 6):  # seulement 4 alignés
        grid[3][c] = 1
    assert check_win(grid, 1, 3, 5) is False


def test_check_win_does_not_wrap_or_overflow_grid():
    grid = empty_grid()
    for c in range(6, 10):  # 4 alignés collés au bord droit
        grid[0][c] = 1
    assert check_win(grid, 1, 0, 9) is False


# --------------------------------------------------------------------------- #
# is_grid_full
# --------------------------------------------------------------------------- #
def test_is_grid_full_true():
    grid = [[1] * GRID_SIZE for _ in range(GRID_SIZE)]
    assert is_grid_full(grid) is True


def test_is_grid_full_false_with_one_empty():
    grid = [[1] * GRID_SIZE for _ in range(GRID_SIZE)]
    grid[9][9] = 0
    assert is_grid_full(grid) is False


def test_is_grid_full_false_on_empty_grid():
    assert is_grid_full(empty_grid()) is False
