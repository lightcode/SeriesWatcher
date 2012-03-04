import unicodedata

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def decompose(string, banWords=[]):
    o = []
    words = string.lower()
    words = remove_accents(words).split()
    
    for word in words:
        if len(word) > 1 and word not in banWords:
            o.append(word)
    
    return o


def search(user, entry):
    user = decompose(user)
    isUFind = True
    for u in user:
        uSize = len(u)
        isEFind = False
        for e in entry:
            tst = e[0:uSize] == u
            isEFind |= tst
        isUFind &= isEFind
    return isUFind