
from tools import is_key_correct


def test_key_correct():
    assert(is_key_correct('123') == False)
    assert(is_key_correct('1234') == True)
    assert(is_key_correct('123456789012') == True)
    assert(is_key_correct('1234567890123') == False)
