#!/usr/local/bin python3

import re

def consonants(roman):
    # ローマ字からその子音を抽出
    matches = re.findall(r'(?P<consonants>[^aiueo]*)|(?P<vowels>[aiueo]*)', roman)
    if matches:
        return list(''.join([c for c, v in matches]))
    else:
        return []

def vowels(roman):
    # ローマ字からその母音を抽出
    matches = re.findall(r'(?P<consonants>[^aiueo]*)|(?P<vowels>[aiueo]*)', roman)
    if matches:
        return list(''.join([v for c, v in matches]))
    else:
        return []
