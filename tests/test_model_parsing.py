"""Tests du formatage de grille et du parsing de la reponse LLM (aucun appel reseau)."""

import pytest
from fastapi import HTTPException

from Model.model import LLMClient, format_grid_for_llm

GRID_SIZE = 10


def empty_grid():
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


# --------------------------------------------------------------------------- #
# format_grid_for_llm
# --------------------------------------------------------------------------- #
def test_format_grid_has_header_and_ten_rows():
    out = format_grid_for_llm(empty_grid())
    lines = out.rstrip("\n").split("\n")
    # 1 ligne d'en-tete + 1 ligne de separation + 10 lignes de donnees
    assert len(lines) == 12
    assert lines[0].strip().startswith("|")
    for i in range(GRID_SIZE):
        assert str(i) in lines[0]


def test_format_grid_maps_symbols():
    grid = empty_grid()
    grid[0][0] = 1  # X
    grid[1][1] = 2  # O
    out = format_grid_for_llm(grid)
    assert "X" in out and "O" in out
    # exactement une occurrence de chaque marque (une seule case posee)
    assert out.count("X") == 1
    assert out.count("O") == 1


def _parse(api_response):
    """Appelle la methode sans instancier LLMClient (elle n'utilise pas self)."""
    return LLMClient._parse_llm_response(None, api_response)


# --------------------------------------------------------------------------- #
# _parse_llm_response
# --------------------------------------------------------------------------- #
def test_parse_valid_moves():
    resp = {
        "choices": [
            {"message": {"content": '{"moves": [{"row": 1, "col": 2}, {"row": 3, "col": 4}]}'}}
        ]
    }
    assert _parse(resp) == [{"row": 1, "col": 2}, {"row": 3, "col": 4}]


def test_parse_content_not_json():
    resp = {"choices": [{"message": {"content": "je joue en 4,4"}}]}
    with pytest.raises(HTTPException) as exc:
        _parse(resp)
    assert exc.value.status_code == 500


def test_parse_json_without_moves_key():
    resp = {"choices": [{"message": {"content": '{"coup": [1, 2]}'}}]}
    with pytest.raises(HTTPException) as exc:
        _parse(resp)
    assert exc.value.status_code == 500


def test_parse_moves_not_a_list():
    resp = {"choices": [{"message": {"content": '{"moves": "1,2"}'}}]}
    with pytest.raises(HTTPException) as exc:
        _parse(resp)
    assert exc.value.status_code == 500


def test_parse_content_is_none():
    resp = {"choices": [{"message": {"content": None}}]}
    with pytest.raises(HTTPException) as exc:
        _parse(resp)
    assert exc.value.status_code == 500


def test_parse_missing_choices_raises_keyerror():
    # Comportement actuel : une reponse sans 'choices' n'est pas geree proprement.
    with pytest.raises(KeyError):
        _parse({"foo": "bar"})
