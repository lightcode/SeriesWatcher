# -*-coding: utf8-*-
import re
import unicodedata

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def getCamelCase(string):
    string = remove_accents(string)
    pattern = re.compile('\W+')
    words = pattern.split(string)
    return "".join([w.lower().capitalize() for w in words])