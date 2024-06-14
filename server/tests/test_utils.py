import pytest
from utils import validate_message

def test_validate_message():
    assert validate_message('Valid message') is True
    assert validate_message('') is False
