#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Matthieu <http://lightcode.fr>'


__all__ = ['split', 'search', 'search2']

import re
import unicodedata

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

PATTERN = re.compile(r"(\w{2,})")
def split(string):
    """Split and remove accent in a string."""
    words = remove_accents(string).lower()
    return re.findall(PATTERN, words)

def search(user, entry):
    """Return True if the string user match entry.
    
    To match, words in the `user` string must start like the words
    in the `entry` string.
    """
    user_words = split(user)
    for uword in user_words:
        for e in entry:
            if e.startswith(uword):
                break
        else:
            return False
    return True

def search2(user, entry):
    user = split(user)
    return len(set(user) & set(entry))