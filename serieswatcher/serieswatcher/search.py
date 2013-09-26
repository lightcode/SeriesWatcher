#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Matthieu GAIGNIÈRE
#
# This file is part of SeriesWatcher.
#
# SeriesWatcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# SeriesWatcher is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# SeriesWatcher. If not, see <http://www.gnu.org/licenses/>.


__all__ = ('split', 'search', 'search2')


import re
import unicodedata


PATTERN = re.compile(r"(\w{2,})")


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


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