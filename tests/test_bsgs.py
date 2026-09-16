# tests/test_bsgs.py

from algo.bsgs import bsgs


def test_bsgs():
    assert bsgs(2, 8, 11) == 3
