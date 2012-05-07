#!/usr/bin/env python

import unicodedata
import re

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


PATTERN = re.compile(r"(\w{2,})")
def decompose(string):
    words = remove_accents(string).lower()
    return re.findall(PATTERN, words)


def search(user, entry):
    user = decompose(user)
    isUFind = True
    for u in user:
        isEFind = False
        for e in entry:
            isEFind |= (e[0:len(u)] == u)
        isUFind &= isEFind
    return isUFind