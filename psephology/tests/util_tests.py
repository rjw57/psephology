from __future__ import division

import unittest

from psephology._util import token_urlsafe

# URL safe characters used in Base64
URL_SAFE='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

def token_urlsafe_test():
    """
    token_urlsafe() returns a non-zero length string of URL safe characters

    Calling with no arguments should generate some non-zero length string
    which is URL safe. The exact length is decided by _util but should
    certainly be longer than 10 characters (60 bits of entropy).

    """
    token = token_urlsafe()
    assert len(token) >= 10
    _assert_url_safe(token)

def token_with_entropy_test():
    """
    token_urlsafe() should return an appropriate length for a given entropy

    Calling with specified number of bits of entropy should return appropriate
    length output *without* padding bits.

    """
    for nbytes in range(5, 20):
        token = token_urlsafe(nbytes=nbytes)
        # this is equivalent to ceil(nbytes * 8/6)
        expected_length = (5 + (nbytes * 8)) // 6
        assert len(token) == expected_length

def _assert_url_safe(s):
    """Asserts that the passed string contains only URL-safe characters."""
    for c in s:
        assert c in URL_SAFE

if __name__ == '__main__':
    unittest.main()
