#!/usr/bin/env python
import os.path
import codecs

from langcodes import LANGUAGES_LIST




def codeToLocal(code):
    code = str(code)
    if code in LANGUAGES_LIST:
        return LANGUAGES_LIST[code]
    else:
        return code