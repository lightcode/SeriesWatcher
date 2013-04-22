#!/usr/bin/env python

__all__ = ['decompose', 'search', 'search2']

import re


PATTERN = re.compile(r"(\w{2,})", flags=re.I|re.U)
def decompose(string):
    return re.findall(PATTERN, words)

def search(user, entry):
    user = decompose(user)
    for u in user:
        for e in entry:
            if e[0:len(u)] == u:
                break
        else:
            return False
    return True

def search2(user, entry):
    user = decompose(user)
    return len(set(user) & set(entry))