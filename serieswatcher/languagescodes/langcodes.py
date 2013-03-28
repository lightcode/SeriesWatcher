#!/usr/bin/env python
# -*- encoding: utf8 -*-

LANGUAGES = u'''ISO;Local;English
"ar";"العربية";"Arabic"
"az";"Azərbaycan";"Azerbaijani"
"bg";"Български";"Bulgarian"
"bs";"Bosanski";"Bosnian"
"ca";"Català";"Catalan"
"cs";"Česky";"Czech"
"da";"Dansk";"Danish"
"de";"Deutsch";"German"
"el";"Ελληνικά";"Greek"
"en";"English";"English"
"es";"Español";"Spanish"
"et";"Eesti";"Estonian"
"fi";"Suomi";"Finnish"
"fr";"Français";"French"
"he";"עברית";"Hebrew"
"hr";"Hrvatski";"Croatian"
"hu";"Magyar";"Hungarian"
"hy";"Հայերեն";"Armenian"
"is";"Íslenska";"Icelandic"
"it";"Italiano";"Italian"
"ja";"日本語";"Japanese"
"ko";"한국어";"Korean"
"lt";"Lietuvių";"Lithuanian"
"lv";"Latviešu";"Latvian"
"mk";"Makedonski";"Macedonian"
"mn";"Монгол";"Mongolian"
"mt";"Malti";"Maltese"
"nl";"Nederlands";"Dutch"
"no";"Norsk";"Norwegian"
"pl";"Polski";"Polish"
"pt";"Português";"Portuguese"
"ro";"Română";"Romanian"
"ru";"Русский";"Russian"
"sk";"Slovenčina";"Slovak"
"sl";"Slovenščina";"Slovenian"
"sq";"Shqip";"Albanian"
"sr";"Српски / Srpski";"Serbian"
"sv";"Svenska";"Swedish"
"sz";"Crnogorski";"Montenegrin"
"th";"ไทย";"Thai"
"tr";"Türkçe";"Turkish"
"uk";"Українська";"Ukrainian"
"uz";"O‘zbek";"Uzbek"
"vi";"Tiếng Việt";"Vietnamese"
"zh";"中文";"Chinese"'''

LANGUAGES_LIST = {}

for i, l in enumerate(LANGUAGES.split('\n')):
    if i == 1:
        continue
    code, local, english = l.strip().split(';')
    code = code.strip('"')
    local = local.strip('"')
    LANGUAGES_LIST[str(code)] = local